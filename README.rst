========
pyosmium
========

This library provides Python bindings for the `Libosmium`_ C++
library, a library for working with OpenStreetMap data in a fast and flexible
manner.

.. _Libosmium: https://github.com/osmcode/libosmium

Installation
============

pyosmium can be installed with pip:

    pip install osmium

The Pypi source package already comes bundled with a matching version of
libosmium. The library uses `pybind11`_ to create the C++ bindings.

Python >= 2.7 is supported but a version >= 3.3 is strongly recommended.

Other dependencies are expat, libz, libbz2 and Boost iterator.
See `Libosmium dependencies`_ for required packages for various distributions.

.. _pybind11: https://github.com/pybind/pybind11
.. _Libosmium dependencies: http://osmcode.org/libosmium/manual.html#dependencies

Documentation
=============

The documentation for the latest release is available at
`osmcode.org`_.

If you find bugs or have feature requests, please report those in the
`Github issue tracker`_. For general questions about using pyosmium you
can contanct the `OSM development mailing list`_ or ask on `OSM help`_.

.. _osmcode.org: http://docs.osmcode.org/pyosmium/latest
.. _Github issue tracker: https://github.com/osmcode/pyosmium/issues/
.. _OSM development mailing list: https://lists.openstreetmap.org/listinfo/dev
.. _OSM help: https://help.openstreetmap.org/

Examples
========

The package contains an `example` directory with small examples on how to use
the library. They are mostly ports of the examples in Libosmium and
osmium-contrib.

Fineprint
=========

Pyosmium is available under the BSD 2-Clause License. See LICENSE.TXT.

The source code can be found on `GitHub`_.

.. _GitHub: https://github.com/osmcode/pyosmium
