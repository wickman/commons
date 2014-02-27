python_library(
  name = 'all',
  sources = globs('*.py'),
  dependencies = [
    pants('src/python/twitter/pants/base:address'),
    pants('src/python/twitter/pants/base:build_environment'),
    pants('src/python/twitter/pants/base:build_manual'),
    pants('src/python/twitter/pants/base:parse_context'),
    pants('src/python/twitter/pants/base:target'),
    pants('src/python/twitter/pants/common/collections'),
    pants('src/python/twitter/pants/common/dirutil'),
    pants('src/python/twitter/pants/common/quantity'),
    pants('src/python/twitter/pants/common/lang'),
    pants('src/python/twitter/pants/common/python'),
  ]
)

# XXX oddballs:
#   jvm_binary
#   pants_target
#   python_binary
