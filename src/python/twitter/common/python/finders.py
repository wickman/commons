import os
import pkgutil
import zipimport

import pkg_resources
from pkg_resources import (
    DistInfoDistribution,
    find_distributions,
    PathMetadata,
)


class ChainedFinder(object):
  """A utility to chain together multiple pkg_resources finders."""

  def __init__(self, finders):
    self.finders = finders

  def __call__(self, importer, path_item, only=False):
    for finder in self.finders:
      for dist in finder(importer, path_item, only=only):
        yield dist


def register_chained_finder(importer, finder):
  """Register a new pkg_resources path finder that does not replace the existing finder."""

  # TODO(wickman) This is somewhat dangerous as it is not an exposed API,
  # but pkg_resources doesn't let us chain multiple distribution finders
  # together.  This is likely possible using importlib but that does us no
  # good as the importlib machinery supporting this is 3.x-only.
  existing_finder = pkg_resources._distribution_finders.get(importer)
  if existing_finder:
    chained_finder = ChainedFinder([existing_finder, finder])
  else:
    chained_finder = finder
  pkg_resources.register_finder(importer, chained_finder)



class WheelMetadata(pkg_resources.EggMetadata):
  @classmethod
  def _split_wheelname(cls, wheelname):
    split_wheelname = wheelname.split('-')
    return '-'.join(split_wheelname[:-3])

  def _setup_prefix(self):
    path = self.module_path
    old = None
    while path != old:
      if path.lower().endswith('.whl'):
        self.egg_name = os.path.basename(path)
        # TODO(wickman) Test the regression where we have both upper and lower cased package
        # names.
        self.egg_info = os.path.join(path, '%s.dist-info' % self._split_wheelname(self.egg_name))
        self.egg_root = path
        break
      old = path
      path, base = os.path.split(path)


# See https://bitbucket.org/tarek/distribute/issue/274
class FixedEggMetadata(pkg_resources.EggMetadata):
  @classmethod
  def normalized_elements(cls, path):
    path_split = path.split('/')
    while path_split[-1] in ('', '.'):
      path_split.pop(-1)
    return path_split

  def _fn(self, base, resource_name):
    #original_fn = super(FixedEggMetadata, self)._fn(base, resource_name)
    original_fn = pkg_resources.EggMetadata._fn(self, base, resource_name)
    return '/'.join(self.normalized_elements(original_fn))

  def _zipinfo_name(self, fspath):
    fspath = self.normalized_elements(fspath)
    zip_pre = self.normalized_elements(self.zip_pre)
    if fspath[:len(zip_pre)] == zip_pre:
      return '/'.join(fspath[len(zip_pre):])
    assert "%s is not a subpath of %s" % (fspath, self.zip_pre)


def wheel_from_metadata(location, metadata):
  if not metadata.has_metadata(DistInfoDistribution.PKG_INFO):
    return None

  from email.parser import Parser
  pkg_info = Parser().parsestr(metadata.get_metadata(DistInfoDistribution.PKG_INFO))
  return DistInfoDistribution(
      location=location,
      metadata=metadata,
      project_name=pkg_info.get('Name'),
      version=pkg_info.get('Version'),
      # TODO(wickman) We currently don't use this though for completeness it may make
      # sense to implement.
      platform=None)


def find_wheels_on_path(importer, path_item, only=False):
  if not os.path.isdir(path_item) or not os.access(path_item, os.R_OK):
    return
  if not only:
    for entry in os.listdir(path_item):
      if entry.lower().endswith('.whl'):
        for dist in find_distributions(os.path.join(path_item, entry)):
          yield dist


def find_eggs_in_zip(importer, path_item, only=False):
  if importer.archive.endswith('.whl'):
    return
  metadata = FixedEggMetadata(importer)
  if metadata.has_metadata('PKG-INFO'):
    yield pkg_resources.Distribution.from_filename(path_item, metadata=metadata)
  if only:
    return  # don't yield nested distros
  for subitem in metadata.resource_listdir('/'):
    if subitem.endswith('.egg'):
      subpath = os.path.join(path_item, subitem)
      for dist in find_eggs_in_zip(zipimport.zipimporter(subpath), subpath):
        yield dist


def find_wheels_in_zip(importer, path_item, only=False):
  metadata = WheelMetadata(importer)
  dist = wheel_from_metadata(path_item, metadata)
  if dist:
    yield dist


def register_finders():
  """Register a pkg_resources finder for wheels contained in zips."""

  # replace the zip finder
  pkg_resources.register_finder(
      zipimport.zipimporter, ChainedFinder([find_eggs_in_zip, find_wheels_in_zip]))

  # append the wheel finder
  register_chained_finder(pkgutil.ImpImporter, find_wheels_on_path)
