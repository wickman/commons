page(
  name = 'readme',
  source = 'README.md',
  dependencies = [
    pants('src/python/twitter/pants:readme'),
  ]
)

python_library(
  name = 'python',
  sources = globs('*.py'),
  dependencies = [
    
  ]
)

"""
python_library(
  name = 'interpreter_cache',
  sources = ['interpreter_cache.py'],
  dependencies = [
    pants('3rdparty/python:setuptools'),
    pants(':resolver'),
    pants('src/python/twitter/common/dirutil'),
    pants('src/python/twitter/common/python'),
  ]
)

python_library(
  name = 'code_generator',
  sources = ['code_generator.py', 'sdist_builder.py'],
  dependencies = [
    pants('src/python/twitter/common/contextutil'),
    pants('src/python/twitter/common/dirutil'),
    pants('src/python/twitter/common/python'),
  ]
)

python_library(
  name = 'thrift_builder',
  sources = ['thrift_builder.py'],
  dependencies = [
    pants(':code_generator'),
    pants('src/python/twitter/pants/base:build_environment'),
    pants('src/python/twitter/pants/targets:build_environment'),
    pants('src/python/twitter/pants:thrift_util'),
  ]
)
"""