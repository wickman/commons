.. _buildingpex:

*******************
Building .pex files
*******************

The easiest way to build .pex files is with the ``pex`` utility.  This comes as part of twitter.common.python
and may be installed using ``pip install pex`` or, more verbosely, ``pip install twitter.common.python``.


Invoking the ``pex`` utility
----------------------------

The ``pex`` utility has no required arguments and by default will construct an empty environment
and invoke it.  When no entry point is specified, "invocation" means starting an interpreter:

    mba=twitter-commons=; pex
    Python 2.6.9 (unknown, Jan  2 2014, 14:52:48) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2336.11.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>>

You can tailor which interpreter is used by specifying ``--python=PATH``.  PATH can be either the
absolute path of a Python binary or the name of a Python interpreter within the environment, e.g.::

    mba=twitter-commons=; pex --python=python3.3
    Python 3.3.3 (default, Jan  2 2014, 14:57:01) 
    [GCC 4.2.1 Compatible Apple Clang 4.0 ((tags/Apple/clang-421.0.60))] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> 


Specifying requirements
-----------------------

Requirements are specified using the same form as expected by ``setuptools``.


Specifying entry points
-----------------------

Entry points can be specified in one of two ways: using the standard ``pkg_resources.EntryPoint``
form of ``package:target`` or directly as ``module``.  If the former, ``target`` will be imported
from ``package`` and invoked with no arguments.  If the latter, ``module`` will be imported and
executed as if ``__name__`` were ``__main__`` similar in fashion to ``python -m module``.

For example, the Python ``pydoc`` module has a command-line interface 



There are two other supported ways to build pex files:
  * Using pants.  See `Pants Python documentation <http://pantsbuild.github.io/python-readme.html>`_.
  * Programmatically via twitter.common.python.  See :ref:`usingtcp`.
