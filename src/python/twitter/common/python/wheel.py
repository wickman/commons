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


def find_wheels_in_zip(importer, path_item, only=False):
  metadata = WheelMetadata(importer)
  dist = wheel_from_metadata(path_item, metadata)
  if dist:
    yield dist


def register_finders():
  """Register a pkg_resources finder for wheels contained in zips."""
  register_chained_finder(zipimport.zipimporter, find_wheels_in_zip)
  register_chained_finder(pkgutil.ImpImporter, find_wheels_on_path)
