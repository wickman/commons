python_library(
  name = 'command',
  sources = ['__init__.py'],
  dependencies = [
    pants('src/python/twitter/common/collections'),
    pants('src/python/twitter/pants/base:build_file'),
    pants('src/python/twitter/pants/base:target'),
  ]
)

python_library(
  name = 'pants_old',
  dependencies = [
    pants(':build'),
    pants(':help'),
    pants(':py'),
    pants(':setup_py'),
  ]
)

python_library(
  name = 'pants_new',
  dependencies = [
    pants(':goal'),
  ]
)

python_library(
  name = 'build',
  sources = ['build.py'],
  dependencies = [
    pants(':command'),
    pants('src/python/twitter/common/collections'),
    pants('src/python/twitter/pants/base:address'),
    pants('src/python/twitter/pants/base:config'),
    pants('src/python/twitter/pants/base:target'),
    pants('src/python/twitter/pants/targets:common'),
    pants('src/python/twitter/pants/python:python_builder'),
    pants('src/python/twitter/pants/python:interpreter_cache'),
  ]
)

python_library(
  name = 'help',
  sources = ['help.py'],
  dependencies = [
    pants(':command'),
  ]
)

python_library(
  name = 'py',
  sources = ['py.py'],
  dependencies = [
    pants(':command'),
    pants('src/python/twitter/common/python'),
    pants('src/python/twitter/pants/base:address'),
    pants('src/python/twitter/pants/base:config'),
    pants('src/python/twitter/pants/base:parse_context'),
    pants('src/python/twitter/pants/base:target'),
    pants('src/python/twitter/pants/python:python_chroot'),
    pants('src/python/twitter/pants/python:interpreter_cache'),
    pants('src/python/twitter/pants/targets:python'),
  ]
)

python_library(
  name = 'setup_py',
  sources = ['setup_py.py'],
  dependencies = [
    pants(':command'),
    pants('src/python/twitter/common/collections'),
    pants('src/python/twitter/common/dirutil'),
    pants('src/python/twitter/common/python'),
    pants('src/python/twitter/pants/base:address'),
    pants('src/python/twitter/pants/base:config'),
    pants('src/python/twitter/pants/base:target'),
    pants('src/python/twitter/pants/python:antlr_builder'),
    pants('src/python/twitter/pants/python:thrift_builder'),
    pants('src/python/twitter/pants/targets:python'),
  ]
)

python_library(
  name = 'goal',
  sources = ['goal.py'],
  dependencies = [
    # XXX(finishme)
  ],
)
