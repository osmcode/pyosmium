# pyosmium

Provides Python bindings for the [Libosmium](https://github.com/osmcode/libosmium) C++
library, a library for working with OpenStreetMap data in a fast and flexible
manner.

[![Github Actions Build Status](https://github.com/osmcode/pyosmium/workflows/CI/badge.svg)](https://github.com/osmcode/pyosmium/actions?query=workflow%3ACI)

## Installation

Pyosmium works with Python >= 3.8. Pypy is known to not work.

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
 * [Pybind11](https://github.com/pybind/pybind11) >= 2.7
 * [expat](https://libexpat.github.io/)
 * [libz](https://www.zlib.net/)
 * [libbz2](https://www.sourceware.org/bzip2/)
 * [Boost](https://www.boost.org/) variant and iterator >= 1.70
 * [Python Requests](https://docs.python-requests.org/)
 * [scikit-build-core](https://scikit-build-core.readthedocs.io)
 * a C++17-compatible compiler (Clang 13+, GCC 10+ are supported)

### Compiling from Source

Make sure to install the development packages for expat, libz, libbz2
and boost.

The appropriate versions for Libosmium and Protozero will be downloaded into
the `contrib` directory when building the source package:

    python3 -m build -s

Alternatively, provide custom locations for these libraries by setting
`Libosmium_ROOT` and `Protozero_ROOT`.

To compile and install the bindings, run

    pip install .

### Compiling for Development

To compile during development, you can use the experimental
[Editable install mode](https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html#editable-installs)
of scikit-build-core:

Create a virtualenv with scikit-build-core and pybind11 preinstalled:

    virtualenv /tmp/dev-venv
    /tmp/dev-venv/bin/pip install scikit-build-core pybind11

Now compile pyosmium with:

    /tmp/dev-venv/bin/pip --no-build-isolation --config-settings=editable.rebuild=true -Cbuild-dir=/tmp/build -ve.


## Examples

The `example` directory contains small examples on how to use the library.
They are mostly ports of the examples in Libosmium and osmium-contrib.


## Testing

There is a small test suite in the test directory. This provides unit
test for the python bindings, it is not meant to be a test suite for Libosmium.

Testing requires `pytest` and `pytest-httpserver` and optionally
pytest-run-parallel and shapely. Install those into your dev environment:

    /tmp/dev-venv/bin/pip install --no-build-isolation --config-settings=editable.rebuild=true -Cbuild-dir=build -ve.[tests]

The test suite can be run with:

    /tmp/dev-venv/bin/pytest test

To test parallel execution on free-threaded Python, run:

    /tmp/dev-venv/bin/pytest test --parallel-threads 10 --iterations 100


## Documentation

To build the documentation you need [mkdocs](https://www.mkdocs.org/)
with the [mkdocstrings](https://mkdocstrings.github.io/)
and [jupyter](https://github.com/danielfrg/mkdocs-jupyter) extensions
and the [material theme](https://squidfunk.github.io/mkdocs-material/).

All necessary packages can be installed via pip:

    pip install osmium[docs]

To build the documentation run:

    mkdocs build

or to few it locally, you can use:

    mkdocs serve

For building the man pages for the tools run:

    cd docs
    make man

The man pages can be found in docs/man.

## Bugs and Questions

If you find bugs or have feature requests, please report those in the
[github issue tracker](https://github.com/osmcode/pyosmium/issues/).

For general questions about using pyosmium you can use the
[OSM development mailing list](https://lists.openstreetmap.org/listinfo/dev)
or ask on [OSM help](https://help.openstreetmap.org/).

## License

Pyosmium is available under the BSD 2-Clause License. See LICENSE.TXT.

## Authors

Sarah Hoffmann (lonvia@denofr.de) and otheres. See commit logs for a full
list.
