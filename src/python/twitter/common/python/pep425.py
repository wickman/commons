class PEP425Extras(object):
  """Extensions to platform handling beyond PEP425."""

  MACOSX_VERSION_STRING = re.compile(r"macosx-(\d+)\.(\d+)-(\S+)")
  MACOSX_PLATFORM_COMPATIBILITY = {
    'i386'      : ('i386',),
    'ppc'       : ('ppc',),
    'x86_64'    : ('x86_64',),
    'ppc64'     : ('ppc64',),
    'fat'       : ('i386', 'ppc'),
    'intel'     : ('i386', 'x86_64'),
    'fat3'      : ('i386', 'ppc', 'x86_64'),
    'fat64'     : ('ppc64', 'x86_64'),
    'universal' : ('i386', 'ppc', 'ppc64', 'x86_64')
  }

  @classmethod
  def is_macosx_platform(cls, platform):
    return platform.startswith('macosx')

  @classmethod
  def iter_osx_platform_tags(cls, supported_platform):
    MAJOR, MINOR, PLATFORM = range(1, 4)
    platform_match = cls.MACOSX_VERSION_STRING.match(supported_platform)
    platform_major, platform_minor, platform = (
        platform_match.group(MAJOR), platform_match.group(MINOR), platform_match.group(PLATFORM))
    for minor in range(int(platform_minor), -1, -1):
      for binary_compat in set((platform,) + cls.MACOSX_PLATFORM_COMPATIBILITY.get(platform, ())):
        yield 'macosx-%s.%s-%s' % (platform_major, minor, binary_compat)

  @classmethod
  def platform_iterator(cls, platform):
    if cls.is_macosx_platform(platform):
      for plat in cls.iter_osx_platform_tags(platform):
        yield plat
    else:
      yield platform


class PEP425(object):
  INTERPRETER_TAGS = {
    'CPython': 'cp',
    'Jython': 'jy',
    'PyPy': 'pp',
    'IronPython': 'ip',
  }

  @classmethod
  def get_implementation_tag(cls, interpreter_subversion):
    return cls.INTERPRETER_TAGS.get(interpreter_subversion)
  
  @classmethod
  def get_version_tag(cls, interpreter_version):
    return ''.join(map(str, interpreter_version[:2]))

  @classmethod
  def get_platform_tag(cls):
    return get_supported_platform()
  
  @classmethod
  def translate_platform_to_tag(cls, platform):
    return platform.replace('.', '_').replace('-', '_')
    
  # TODO(wickman) This implementation is technically incorrect but we need to be able to
  # predict the supported tags of an interpreter that may not be on this machine or
  # of a different platform.  Alternatively we could store the manifest of supported tags
  # of a targeted platform in a file to be more correct.
  @classmethod
  def _iter_supported_tags(cls, impl, version, platform):
    """
       :param impl: Python implementation tag e.g. cp, jy, pp.
       :param version: E.g. '26', '33'
       :param platform: Platform as from :function:`pkg_resources.get_supported_platform`,
                        for example 'linux-x86_64' or 'macosx-10.4-x86_64'.
       
       yields (pyver, abi, platform) tuples.
    """
    # Predict soabi for reasonable interpreters.  This is technically wrong but essentially right.
    abis = []
    if impl == 'cp' and version.startswith('3'):
      abis.extend(['cp%sm' % version, 'abi3'])

    major_version = int(version[0])
    minor_versions = []
    for minor in range(int(version[1]), -1, -1):
      minor_versions.append('%d%d' % (major_version, minor))

    platforms = [cls.translate_platform_to_tag(p) for p in PEP425Extras.platform_iterator(platform)]

    # interpreter specific
    for p in platforms:
      for abi in abis:
        yield ('%s%s' % (impl, version), abi, p)

    # everything else
    for p in platforms + ['any']:
      for i in ('py', impl):
        yield ('%s%d' % (i, major_version), 'none', p)
        for minor_version in minor_versions:
          yield ('%s%s' % (i, minor_version), 'none', p)
  
  @classmethod
  def iter_supported_tags(cls, interpreter, platform=get_supported_platform()):
    """Iterate over the supported tag tuples of this interpreter.
    
       :param interpreter: :class:`PythonInterpreter` over which tags should iterate.
    """
    tag_iterator = cls._iter_supported_tags(interpreter.interpreter, interpreter.version, platform)
    for tag in tag_iterator:
      yield tag

  """
  @classmethod
  def iter_provided_tags_from_egg(cls, dist):
    if dist.py_version is None:
      # we do not support unversioned eggs
      return
    version = ''.join(dist.py_version.split('.')[:2])
    if dist.platform:
      platform_iter = PEP425Extras.platform_iterator(dist.platform)
      impl = 'cp'  # all platform-specific eggs must be presumed against cpython
    else:
      platform_iter = ('any',)
      impl = 'py'
    for platform in platform_iter:
      yield ('%s%s' % (impl, version), 'none', platform)
  
  @classmethod
  def iter_provided_tags_from_whl_name(cls, name):
    wheel_base, _ = os.path.splitext(name)
    try:
      pytag, abitag, archtag = wheel_base.split('-')[-3:]
    except ValueError:
      return
    for py in pytag.split('.'):
      for abi in abitag.split('.'):
        for arch in archtag.split('.'):
          yield (py, abi, arch)
  
  @classmethod
  def iter_provided_tags_from_whl(cls, dist):
    wheel_base, _ = os.path.splitext(dist.location)
    for tag in cls.iter_provided_tags_from_whl_name(wheel_base):
      yield tag
  
  @classmethod
  def iter_provided_tags(cls, distribution):
    iterator = []
    if distribution.location.endswith('.egg'):
      iterator = cls.iter_provided_tags_from_egg(distribution)
    elif distribution.location.endswith('.whl'):
      iterator = cls.iter_provided_tags_from_whl(distribution)
    for tags in iterator:
      yield tags
  """  