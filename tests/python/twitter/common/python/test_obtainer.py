# ==================================================================================================
# Copyright 2012 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

from twitter.common.python.fetcher import Fetcher
from twitter.common.python.package import EggPackage, SourcePackage, WheelPackage
from twitter.common.python.obtainer import Obtainer

from pkg_resources import Requirement


def test_package_precedence():
  source = SourcePackage('psutil-0.6.1.tar.gz')
  egg = EggPackage('psutil-0.6.1-py2.6.egg')
  whl = WheelPackage('psutil-0.6.1-cp26-none-macosx_10_4_x86_64.whl')
  
  # default precedence
  assert Obtainer.package_precedence(whl) > Obtainer.package_precedence(egg)
  assert Obtainer.package_precedence(egg) > Obtainer.package_precedence(source)
  assert Obtainer.package_precedence(whl) > Obtainer.package_precedence(source)
  
  # overridden precedence
  PRECEDENCE = (EggPackage, WheelPackage)
  assert Obtainer.package_precedence(source, PRECEDENCE) == (source.version, -1)  # unknown rank
  assert Obtainer.package_precedence(whl, PRECEDENCE) > Obtainer.package_precedence(
      source, PRECEDENCE)
  assert Obtainer.package_precedence(egg, PRECEDENCE) > Obtainer.package_precedence(
      whl, PRECEDENCE)
  

class FakeCrawler(object):
  def __init__(self, hrefs):
    self._hrefs = hrefs
    self.opener = None

  def crawl(self, *args, **kw):
    return self._hrefs


class FakeObtainer(Obtainer):
  def __init__(self, links):
    self.__links = list(links)
    super(FakeObtainer, self).__init__(FakeCrawler([]), [], [])

  def iter_unordered(self, req):
    return iter(self.__links)


def test_iter_ordering():
  tgz = SourcePackage('psutil-0.6.1.tar.gz')
  egg = EggPackage('psutil-0.6.1-py3.3-linux-x86_64.egg')
  whl = WheelPackage('psutil-0.6.1-cp26-none-macosx_10_4_x86_64.whl')
  req = Requirement.parse('psutil')

  assert list(FakeObtainer([tgz, egg, whl]).iter(req)) == [whl, egg, tgz]
  assert list(FakeObtainer([egg, tgz, whl]).iter(req)) == [whl, egg, tgz]


def test_href_translation():
  VERSIONS = ['0.4.0', '0.4.1', '0.5.0', '0.6.0']
 
  def fake_link(version):
    return 'http://www.example.com/foo/bar/psutil-%s.tar.gz' % version
 
  fc = FakeCrawler([fake_link(v) for v in VERSIONS])
  ob = Obtainer(fc, [], [])

  for v in VERSIONS:
    pkgs = list(ob.iter(Requirement.parse('psutil==%s' % v)))
    assert len(pkgs) == 1, 'Version: %s' % v
    assert pkgs[0] == SourcePackage(fake_link(v))

  assert list(ob.iter(Requirement.parse('psutil>=0.5.0'))) == [
    SourcePackage(fake_link('0.6.0')),
    SourcePackage(fake_link('0.5.0'))]

  assert list(ob.iter(Requirement.parse('psutil'))) == [
      SourcePackage(fake_link(v)) for v in reversed(VERSIONS)]
