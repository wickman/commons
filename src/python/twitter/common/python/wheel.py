import os
import zipimport

import pkg_resources
from pkg_resources import DistInfoDistribution


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


"""
TODO(wickman) Implement this if necessary

def find_zipped_wheels_on_path(importer, path_item, only=False):
  pass
"""
def find_wheels_in_zip(importer, path_item, only=False):
  if not importer.archive.endswith('.whl'):
    return
  metadata = WheelMetadata(importer)
  if metadata.has_metadata(DistInfoDistribution.PKG_INFO):
    from email.parser import Parser
    pkg_info = Parser().parsestr(metadata.get_metadata(DistInfoDistribution.PKG_INFO))
    yield pkg_resources.DistInfoDistribution(
        location=path_item,
        metadata=metadata,
        project_name=pkg_info.get('Name'),
        version=pkg_info.get('Version'),
        # TODO(wickman) We currently don't use this though for completeness it may make
        # sense to implement.
        platform=None)


def distribution_from_zipped_wheel(path):
  distributions = list(find_wheels_in_zip(zipimport.zipimporter(path), path))
  if len(distributions) != 1:
    return None
  return distributions[0]


def register_finder():
  """Register a pkg_resources finder for wheels contained in zips."""
  pkg_resources.register_finder(zipimport.zipimporter, find_wheels_in_zip)
