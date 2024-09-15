# Introduction

pyosmium is a library to efficiently read and process OpenStreetMap data files. It is based on the osmium library for reading and writing data and adds convenience functions that allow you to set up fast processing pipelines in Pythons that can handle even planet-sized data.

This manual comes in three parts:

* the [**User Manual**](user_manual.md) introduces the concepts and functionalities of pyosmium
* the [**Cookbook**](cookbooks.md) shows how to solve typical OSM data processing challenges with pyosmium
* the [**Reference**](reference.md) contains a complete list of classes and functions.

## Installation

The recommended way to install pyosmium is via pip:

    pip install osmium

Binary wheels are provided for all actively maintained Python versions on
Linux, MacOS and Windows 64bit.

### Installing from Source

To compile pyosmium from source or when installing it from the source wheel,
the following additional dependencies need to be available:

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

On Debian/Ubuntu-like systems, the following command installs all required
packages:

    sudo apt-get install python3-dev build-essential cmake libboost-dev \
                         libexpat1-dev zlib1g-dev libbz2-dev

libosmium, protozero and pybind11 are shipped with the source wheel. When
building from source, you need to download the source code and put it
in the subdirectory 'contrib'. Alternatively, if you want to put the sources
somewhere else, point pyosmium to the source code location by setting the
CMake variables `LIBOSMIUM_PREFIX`, `PROTOZERO_PREFIX` and
`PYBIND11_PREFIX` respectively.

To compile and install the bindings, run

    pip install [--user] .
