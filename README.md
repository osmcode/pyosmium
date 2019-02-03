# pyosmium

Provides Python bindings for the [Libosmium](https://github.com/osmcode/libosmium) C++
library, a library for working with OpenStreetMap data in a fast and flexible
manner.

[![Travis Build Status](https://api.travis-ci.org/osmcode/pyosmium.svg)](http://travis-ci.org/osmcode/pyosmium)
[![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/github/osmcode/pyosmium?svg=true)](https://ci.appveyor.com/project/lonvia/pyosmium)

## Dependencies

Python >= 2.7 is supported but a version >= 3.3 is strongly recommended.

Other requirements are:

 * Python setuptools
 * [cmake](https://cmake.org/)
 * [Pybind11](https://github.com/pybind/pybind11) >= 2.2
 * libosmium, protozero
 * expat, libz, libbz2 and Boost variant and iterator
 * a recent C++ compiler (Clang 3.4+, GCC 4.8+)

## Installation

### Installing prerequisites

On Debian/Ubuntu-like systems the following should install all
dependencies required for installing via pip:

    sudo apt-get install build-essential cmake libboost-dev \
                         libexpat1-dev zlib1g-dev libbz2-dev

### Using Pip

The recommended way to install pyosmium is via pip:

    pip install osmium

You need to install development packages first for the dependencies
mentioned above. For Windows, there are also experimental binary wheels
available with all required dependencies packed already.

### Compiling from Source

Get the latest versions of libosmium, protozero and pybind11. It is
recommended that you put them in a subdirectory `contrib`. You can also
set custom locations with `LIBOSMIUM_PREFIX`, `PROTOZERO_PREFIX` and
`PYBIND11_PREFIX` respectively.

To use a custom boost installation, set `BOOST_PREFIX`.

To compile the bindings, run

    python setup.py build

To compile and install the bindings, run

    python setup.py install [--user]


## Examples

The `example` directory contains small examples on how to use the library.
They are mostly ports of the examples in Libosmium and osmium-contrib.


## Testing

There is a small test suite in the test directory. This provides regression
test for the python bindings, it is not meant to be a test suite for Libosmium.

You'll need the Python `nose` module. On Debian/Ubuntu install the package
`python-nose`. For Python2 `mock` is required as well (package `python-mock`).

The suite can be run with:

    cd test
    python run_tests.py


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

