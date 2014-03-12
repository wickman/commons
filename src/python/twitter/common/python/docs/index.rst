.. twitter.common.python documentation master file, created by
   sphinx-quickstart on Tue Mar 11 10:18:49 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

******
tl;dr
******

To quickly get started building .pex (PEX) files, go straight to :ref:`buildingpex`

twitter.common.python
=====================

twitter.common.python contains the Python packaging and distribution
libraries in use by Twitter and available from the `twitter commons
<https://github.com/twitter/commons>`_.  The most notable components of
twitter.common.python are the
.pex (Python EXecutable) format and the associated ``pex`` tool which provide a general purpose Python environment virtualization
solution similar in spirit to `virtualenv <http://virtualenv.org>`_   PEX files have been used by Twitter
to deploy Python applications to production since 2011.

To learn more about what the .pex format is and why it could be useful for
you, see :ref:`whatispex`  For the impatient, there is also a lightning
talk published by Twitter University: `WTF is PEX?
<http://www.youtube.com/watch?v=NmpnGhRwsu0>`_.


Guide:

.. toctree::
   :maxdepth: 1

   whatispex
   buildingpex
   usingtcp
   python
