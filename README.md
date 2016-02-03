# pyosmium

Provides Python bindings for the [Libosmium](https://github.com/osmcode/libosmium) C++
library, a library for working with OpenStreetMap data in a fast and flexible
manner.

[![Build Status](https://secure.travis-ci.org/osmcode/pyosmium.png)](http://travis-ci.org/osmcode/pyosmium)


## Dependencies

Python >= 2.7 is supported but a version >= 3.3 is strongly recommended.

pyosmium uses [Boost.Python](http://www.boost.org/doc/libs/1_56_0/libs/python/doc/index.html)
to create the bindings. On Debian/Ubuntu install `libboost-python-dev`. OS X run `brew install boost-python` or `brew install boost-python --with-python3` depending on which python version you want to use – You can also (re)install both.

You have to compile with the same compiler version python is compiled with on
your system, otherwise it might not work.

Libosmium is expected to reside in the same directory as pyosmium or to be
installed globally.

## Installation

To compile the bindings, run

    python setup.py build

To compile and install the bindings, run

    python setup.py install

## Examples

The `example` directory contains small examples on how to use the library.
They are mostly ports of the examples in Libosmium and osmium-contrib.


## Testing

There is a small test suite in the test directory. This provides regression
test for the python bindings, it is not meant to be a test suite for Libosmium.

You'll need the Python `nose` module. On Debian/Ubuntu install the package
`python-nose`.

The suite can be run with:

    cd test
    python run_tests.py


## Documentation

To build the documentation you need [Sphinx](http://sphinx-doc.org/).
On Debian/Ubuntu install `python-sphinx` or `python3-sphinx`.

First compile the bindings as described above and then run:

    cd doc
    make html


## License

Pyosmium is available under the BSD 2-Clause License. See LICENSE.TXT.


## Authors

Sarah Hoffmann (lonvia@denofr.de)

