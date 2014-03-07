import contextlib
import os
import tarfile
import zipfile

from .base import maybe_requirement
from .common import safe_mkdtemp
from .http.link import Link
from .platforms import Platform
from .pep425 import PEP425

from pkg_resources import (
    EGG_NAME,
    parse_version,
    safe_name,
)


class Package(Link):
  _REGISTRY = set()
  
  @classmethod
  def register(cls, package_type):
    cls._REGISTRY.add(package_type)
  
  @classmethod
  def from_href(cls, href, **kw):
    for package_type in cls._REGISTRY:
      try:
        return package_type(href, **kw)
      except package_type.InvalidLink:
        continue

  @property
  def name(self):
    return NotImplementedError

  @property
  def raw_version(self):
    return NotImplementedError

  @property
  def version(self):
    return parse_version(self.raw_version)

  def satisfies(self, requirement):
    """Does the signature of this filename match the requirement (pkg_resources.Requirement)?"""
    requirement = maybe_requirement(requirement)
    link_name = safe_name(self.name).lower()
    if link_name != requirement.key:
      return False
    return self.raw_version in requirement

  def compatible(self, identity, platform=Platform.current()):
    """Is this link compatible with the given :class:`PythonIdentity` identity and platform?"""
    raise NotImplementedError


class SourcePackage(Package):
  """A Target providing source that can be built into a Distribution via Installer."""

  EXTENSIONS = {
    '.tar': (tarfile.TarFile.open, tarfile.ReadError),
    '.tar.gz': (tarfile.TarFile.open, tarfile.ReadError),
    '.tar.bz2': (tarfile.TarFile.open, tarfile.ReadError),
    '.tgz': (tarfile.TarFile.open, tarfile.ReadError),
    '.zip': (zipfile.ZipFile, zipfile.BadZipfile)
  }

  @classmethod
  def split_fragment(cls, fragment):
    """heuristic to split by version name/fragment:

       >>> split_fragment('pysolr-2.1.0-beta')
       ('pysolr', '2.1.0-beta')
       >>> split_fragment('cElementTree-1.0.5-20051216')
       ('cElementTree', '1.0.5-20051216')
       >>> split_fragment('pil-1.1.7b1-20090412')
       ('pil', '1.1.7b1-20090412')
       >>> split_fragment('django-plugin-2-2.3')
       ('django-plugin-2', '2.3')
    """
    def likely_version_component(enumerated_fragment):
      return sum(bool(v and v[0].isdigit()) for v in enumerated_fragment[1].split('.'))
    fragments = fragment.split('-')
    if len(fragments) == 1:
      return fragment, ''
    max_index, _ = max(enumerate(fragments), key=likely_version_component)
    return '-'.join(fragments[0:max_index]), '-'.join(fragments[max_index:])

  def __init__(self, url, **kw):
    super(SourcePackage, self).__init__(url, **kw)

    for ext, class_info in self.EXTENSIONS.items():
      if self.filename.endswith(ext):
        self._archive_class = class_info
        fragment = self.filename[:-len(ext)]
        break
    else:
      raise self.InvalidLink('%s does not end with any of: %s' % (
          self.filename, ' '.join(self.EXTENSIONS)))
    self._name, self._raw_version = self.split_fragment(fragment)

  @property
  def name(self):
    return safe_name(self._name)

  @property
  def raw_version(self):
    return safe_name(self._raw_version)

  @classmethod
  def first_nontrivial_dir(cls, path):
    files = os.listdir(path)
    if len(files) == 1 and os.path.isdir(os.path.join(path, files[0])):
      return cls.first_nontrivial_dir(os.path.join(path, files[0]))
    else:
      return path

  def _unpack(self, filename, location=None):
    """Unpack this source target into the path if supplied.  If the path is not supplied, a
       temporary directory will be created."""
    path = location or safe_mkdtemp()
    archive_class, error_class = self._archive_class
    try:
      with contextlib.closing(archive_class(filename)) as package:
        package.extractall(path=path)
    except error_class:
      raise self.UnreadableLink('Could not read %s' % self.url)
    return self.first_nontrivial_dir(path)

  def fetch(self, location=None, conn_timeout=None):
    target = super(SourcePackage, self).fetch(conn_timeout=conn_timeout)
    return self._unpack(target, location)

  # SourcePackages are always compatible as they can be translated to a distribution.
  def compatible(self, identity, platform=Platform.current()):
    return True


class EggPackage(Package):
  """A Target providing an egg."""

  def __init__(self, url, **kw):
    super(EggPackage, self).__init__(url, **kw)
    filename, ext = os.path.splitext(self.filename)
    if ext.lower() != '.egg':
      raise self.InvalidLink('Not an egg: %s' % filename)
    matcher = EGG_NAME(filename)
    if not matcher:
      raise self.InvalidLink('Could not match egg: %s' % filename)

    self._name, self._raw_version, self._py_version, self._platform = matcher.group(
        'name', 'ver', 'pyver', 'plat')

    if self._raw_version is None or self._py_version is None:
      raise self.InvalidLink('url with .egg extension but bad name: %s' % url)

  def __hash__(self):
    return hash((self.name, self.version, self.py_version, self.platform))

  @property
  def name(self):
    return safe_name(self._name)

  @property
  def raw_version(self):
    return safe_name(self._raw_version)

  @property
  def py_version(self):
    return self._py_version

  @property
  def platform(self):
    return self._platform

  def compatible(self, identity, platform=Platform.current()):
    if not Platform.version_compatible(self.py_version, identity.python):
      return False
    if not Platform.compatible(self.platform, platform):
      return False
    return True


class WheelPackage(Package):
  """A Target providing a wheel."""

  def __init__(self, url, **kw):
    super(WheelPackage, self).__init__(url, **kw)
    filename, ext = os.path.splitext(self.filename)
    if ext.lower() != '.whl':
      raise self.InvalidLink('Not a wheel: %s' % filename)
    try:
      self._name, self._raw_version, self._py_tag, self._abi_tag, self._arch_tag = (
          filename.split('-'))
    except ValueError:
      raise self.InvalidLink('Wheel filename malformed.')
    # See https://github.com/pypa/pip/issues/1150 for why this is unavoidable.
    self._name.replace('_', '-')
    self._raw_version.replace('_', '-')
    self._supported_tags = frozenset(self._iter_tags())

  @property
  def name(self):
    return self._name

  @property
  def raw_version(self):
    return self._raw_version

  def _iter_tags(self):
    for py in self._py_tag.split('.'):
      for abi in self._abi_tag.split('.'):
        for arch in self._arch_tag.split('.'):
          yield (py, abi, arch)

  def compatible(self, identity, platform=Platform.current()):
    for tag in PEP425.iter_supported_tags(identity, platform):
      if tag in self._supported_tags:
        return True
    return False


Package.register(SourcePackage)
Package.register(EggPackage)
Package.register(WheelPackage)
