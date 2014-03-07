from __future__ import absolute_import

from abc import abstractmethod
import os
import warnings
from zipimport import zipimporter

from .common import chmod_plus_w, safe_rmtree, safe_mkdir, safe_mkdtemp
from .compatibility import AbstractClass
from .http.link import EggLink, SourceLink, WheelLink
from .installer import Installer, EggInstaller
from .interpreter import PythonInterpreter
from .platforms import Platform
from .tracer import TRACER
from .util import DistributionHelper

from pkg_resources import Distribution, EggMetadata, PathMetadata


class TranslatorBase(AbstractClass):
  """
    Translate a link into a distribution.
  """
  @abstractmethod
  def translate(self, link):
    pass


class ChainedTranslator(TranslatorBase):
  """
    Glue a sequence of Translators together in priority order.  The first Translator to resolve a
    requirement wins.
  """
  def __init__(self, *translators):
    self._translators = list(filter(None, translators))
    for tx in self._translators:
      if not isinstance(tx, TranslatorBase):
        raise ValueError('Expected a sequence of translators, got %s instead.' % type(tx))

  def translate(self, link):
    for tx in self._translators:
      dist = tx.translate(link)
      if dist:
        return dist


class SourceTranslator(TranslatorBase):
  @classmethod
  def run_2to3(cls, path):
    from lib2to3.refactor import get_fixers_from_package, RefactoringTool
    rt = RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
    with TRACER.timed('Translating %s' % path):
      for root, dirs, files in os.walk(path):
        for fn in files:
          full_fn = os.path.join(root, fn)
          if full_fn.endswith('.py'):
            with TRACER.timed('%s' % fn, V=3):
              try:
                chmod_plus_w(full_fn)
                rt.refactor_file(full_fn, write=True)
              except IOError as e:
                TRACER.log('Failed to translate %s: %s' % (fn, e))

  def __init__(self,
               install_cache=None,
               interpreter=PythonInterpreter.get(),
               platform=Platform.current(),
               use_2to3=False,
               conn_timeout=None):
    self._interpreter = interpreter
    self._use_2to3 = use_2to3
    self._install_cache = install_cache or safe_mkdtemp()
    safe_mkdir(self._install_cache)
    self._conn_timeout = conn_timeout
    self._platform = platform

  def translate(self, link):
    """From a link, translate a distribution."""
    if not isinstance(link, SourceLink):
      return None

    unpack_path, installer = None, None
    version = self._interpreter.version

    try:
      unpack_path = link.fetch(conn_timeout=self._conn_timeout)
    except link.UnreadableLink as e:
      TRACER.log('Failed to fetch %s: %s' % (link, e))
      return None

    try:
      if self._use_2to3 and version >= (3,):
        with TRACER.timed('Translating 2->3 %s' % link.name):
          self.run_2to3(unpack_path)
      # TODO(wickman) Allow for pluggable installers (e.g. WheelInstaller) once
      # Platform.distribution_compatible understands PEP425 tags.
      installer = EggInstaller(
          unpack_path,
          interpreter=self._interpreter,
          strict=(link.name != 'distribute'))
      with TRACER.timed('Packaging %s' % link.name):
        try:
          dist_path = installer.bdist()
        except Installer.InstallFailure:
          return None
        target_path = os.path.join(self._install_cache, os.path.basename(dist_path))
        os.rename(dist_path, target_path)
        dist = DistributionHelper.distribution_from_path(target_path)
        if not dist:
          return None
        if Platform.distribution_compatible(
            dist, python=self._interpreter.python, platform=self._platform):
          return dist
    finally:
      if installer:
        installer.cleanup()
      if unpack_path:
        safe_rmtree(unpack_path)


class BinaryTranslator(TranslatorBase):
  def __init__(self,
               link_type,
               install_cache=None,
               interpreter=PythonInterpreter.get(),
               platform=Platform.current(),
               python=None,
               conn_timeout=None):
    if python:
      warnings.warn('python= keyword argument to Translator is deprecated.')
      if python != interpreter.python:
        raise ValueError('Two different python interpreters supplied!')
    self._link_type = link_type
    self._install_cache = install_cache or safe_mkdtemp()
    self._platform = platform
    self._identity = interpreter.identity
    self._conn_timeout = conn_timeout

  def translate(self, link):
    """From a link, translate a distribution."""
    if not isinstance(link, self._link_type):
      return None
    if not link.compatible(identity=self._identity, platform=self._platform):
      return None
    try:
      bdist = link.fetch(location=self._install_cache, conn_timeout=self._conn_timeout)
    except link.UnreadableLink as e:
      TRACER.log('Failed to fetch %s: %s' % (link, e))
      return None
    return DistributionHelper.distribution_from_path(bdist)


class EggTranslator(BinaryTranslator):
  def __init__(self, **kw):
    super(EggTranslator, self).__init__(EggLink, **kw)


class WheelTranslator(BinaryTranslator):
  def __init__(self, **kw):
    super(WheelTranslator, self).__init__(WheelLink, **kw)


class Translator(object):
  @staticmethod
  def default(install_cache=None,
              platform=Platform.current(),
              interpreter=PythonInterpreter.get(),
              conn_timeout=None):

    shared_options = dict(
        install_cache=install_cache,
        interpreter=interpreter,
        conn_timeout=conn_timeout)

    whl_translator = WheelTranslator(platform=platform, **shared_options)
    egg_translator = EggTranslator(platform=platform, **shared_options)
    source_translator = SourceTranslator(**shared_options)
    return ChainedTranslator(whl_translator, egg_translator, source_translator)
