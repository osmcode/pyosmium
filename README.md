# pyosmium

Provides Python bindings for the [libosmium](https://github.com/osmcode/libosmium) C++
library, a library for fast and flexible working with OpenStreetMap data.

## Depends

pyosmium uses [Boost.Python](http://www.boost.org/doc/libs/1_56_0/libs/python/doc/index.html)
to create the bindings.

## Installation

To compile and install the bindings, simply run

    python setup.py install

## Examples

The example/ directory contains small examples on how to use the library.
They are for most parts ports of the examples in libosmium and osmium/contrib.

## Testing

There is a small test suite in the test directory. This provides regression
test for the python bindings, it is not meant to be a test suite for libosmium.
The suit can be run with:

    cd test
    python run_tests.py

## License

pyosmium is available under a BSD license.

## Authors

Sarah Hoffmann (lonvia@denofr.de)
