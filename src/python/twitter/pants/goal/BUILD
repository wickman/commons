python_library(
  name = 'goal',
  sources = globs('*.py'),
  dependencies = [
    pants('src/python/twitter/pants/base:build_manual'),
    pants('src/python/twitter/pants/tasks'),  # XXX(fixme)
    pants('src/python/twitter/common/dirutil'),
    pants(':context_deps'),
    pants(':initialize_reporting_deps'),
    pants(':run_tracking_deps'),
  ],
)

python_library(
  name = 'context_deps',
  dependencies = [
    pants('src/python/twitter/base:parse_context'),
    pants('src/python/twitter/base:target'),
    pants('src/python/twitter/base:workunit'),
    pants('src/python/twitter/common/collections'),
    pants('src/python/twitter/common/dirutil'),
    pants('src/python/twitter/common/process'),
    pants('src/python/twitter/pants/base:build_environment'),
    pants('src/python/twitter/pants/java'),  # XXX(fixme)
    pants('src/python/twitter/reporting'),
    pants('src/python/twitter/targets:all'),  # XXX(fixme)
  ],
)

python_library(
  name = 'initialize_reporting_deps',  # XXX should be in reporting?!
  dependencies = [
    pants('src/python/twitter/common/dirutil'),
    pants('src/python/twitter/common/lang'),
    pants('src/python/twitter/common/reporting'),
  ],
)

python_library(
  name = 'run_tracker_deps',  # XXX
  dependencies = [
    pants('src/python/twitter/pants/base:run_info'),
    pants('src/python/twitter/pants/base:worker_pool'),
    pants('src/python/twitter/pants/base:workunit'),
    pants('src/python/twitter/pants/reporting'),
    pants('src/python/twitter/pants:config'),
  ],
)

