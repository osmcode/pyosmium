# pyosmium

Provides Python bindings for the [Libosmium](https://github.com/osmcode/libosmium) C++
library, a library for working with OpenStreetMap data in a fast and flexible
manner.

[![Github Actions Build Status](https://github.com/osmcode/pyosmium/workflows/CI/badge.svg)](https://github.com/osmcode/pyosmium/actions?query=workflow%3ACI)

## Installation

Pyosmium works with Python >= 3.6. Pypy is known to not work.

### Using Pip

The recommended way to install pyosmium is via pip:

    pip install osmium

We provide binary wheels for Linux and Windows 64 for all actively
maintained Python versions.

For other versions, a source wheel is provided. Make sure to install all
external dependencies first. On Debian/Ubuntu-like systems, the following
command installs all required packages:

    sudo apt-get install build-essential cmake libboost-dev \
                         libexpat1-dev zlib1g-dev libbz2-dev


### Installing from source

#### Prerequisites

pyosmium has the following dependencies:

 * [libosmium](https://github.com/osmcode/libosmium) >= 2.16.0
 * [protozero](https://github.com/mapbox/protozero)
 * [cmake](https://cmake.org/)
 * [Pybind11](https://github.com/pybind/pybind11) >= 2.2
 * [expat](https://libexpat.github.io/)
 * [libz](https://www.zlib.net/)
 * [libbz2](https://www.sourceware.org/bzip2/)
 * [Boost](https://www.boost.org/) variant and iterator >= 1.41
 * [Python Requests](https://docs.python-requests.org/en/master/)
 * Python setuptools
 * a recent C++ compiler (Clang 3.4+, GCC 4.8+)

### Compiling from Source

Get the latest versions of libosmium, protozero and pybind11. It is
recommended that you put them in a subdirectory `contrib`. You can also
set custom locations with `LIBOSMIUM_PREFIX`, `PROTOZERO_PREFIX` and
`PYBIND11_PREFIX` respectively.

To use a custom boost installation, set `BOOST_PREFIX`.

To compile the bindings during development, you can use
[build](https://pypa-build.readthedocs.io/en/stable/).
On Debian/Ubuntu-like systems, install `python3-build`, then
run:

    python3 -m build -w

To compile and install the bindings, run

    pip install [--user] .


## Examples

The `example` directory contains small examples on how to use the library.
They are mostly ports of the examples in Libosmium and osmium-contrib.


## Testing

There is a small test suite in the test directory. This provides unit
test for the python bindings, it is not meant to be a test suite for Libosmium.

Testing requires `pytest` and `pytest-httpserver`. On Debian/Ubuntu install
the dependencies with:

    sudo apt-get install python3-pytest python3-pytest-httpserver

The test suite can be run with:

    pytest test


## Documentation

To build the documentation you need [Sphinx](http://sphinx-doc.org/)
and the [autoprogram extension](https://pythonhosted.org/sphinxcontrib-autoprogram/)
On Debian/Ubuntu install `python-sphinx sphinxcontrib-autoprogram`
or `python3-sphinx python3-sphinxcontrib.autoprogram`.

First compile the bindings as described above and then run:

    cd doc
    make html

For building the man pages for the tools run:

    cd doc
    make man

## Bugs and Questions

If you find bugs or have feature requests, please report those in the
[github issue tracker](https://github.com/osmcode/pyosmium/issues/).

For general questions about using pyosmium you can use the
[OSM development mailing list](https://lists.openstreetmap.org/listinfo/dev)
or ask on [OSM help](https://help.openstreetmap.org/).

## License

Pyosmium is available under the BSD 2-Clause License. See LICENSE.TXT.

## Authors

Sarah Hoffmann (lonvia@denofr.de)
