
# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [4.0.0] - 2024-09-20

### Added

- support for Python 3.13
- iterative processing of OSM files (see FileProcessor)
- new `flush()` callback for handlers
- FileBuffer for reading from a Python buffer instead of a file
- bit operators for entity bit enum
- filter mode for handlers (return False to stop processing)
- various C++-implementations of filters (for tags, keys, ids, etc.)
- convenience functions to determine object types
- binary wheels for MAcOS and Intel ARM architecture
- haversine functions for two point
- direct access to lat/lon for nodes
- expose osmium's IdSet
- new IdTracker for efficient tracking of dependent objects
- new writers for adding forward and backward references to output
- new parameter for server file type for pyosmium_get_updates
- new filter to add `__geo_interface__` attribute

### Fixed

- consistently use namespaces everywhere
- deprecation warnings around utc_now (thanks @mtmail)

### Changed

- SimpleHandler is now a Python class
- make NodeLocationForWays a generic BaseHandler
- `apply()` and MergeInputReader can take an arbitrary number of handlers
- accept Python class as handler, no inheritance from SimpleHandler necessary
- new minimum requirements: pybind 2.7, Python 3.7, C++17 compatible compiler, cmake 3.8
- AreaManager is now part of the Python interface
- consistently allow str, Path, File and FileBuffer, where OSM files are expected
- objects stay alive through handler chain allowing to carry over extra attributes
- switch SimpleWriter to use keyword arguments
- make Reader and SimpleWriter context managers
- new overwrite parameter for writers
- remove GIL release, only slows down processing
- move documentation of C++ interface into pyi files
- complete rewrite of documentation using mkdocs
- update pybind to 2.13.6
- use maximum parallelization when building (thanks @Mathiasdm)
- move build configuration to pyproject.toml as far as possible

## [3.7.0] - 2023-11-19

### Added

- transparently retry download on transient HTTP errors

### Fixed

- catch non-200 status for HTTP responses

### Changed

- update to pybind 2.11.1
- update to libosmium 2.20.0


## [3.6.0] - 2023-01-20

### Changed

- update to pybind 2.10.3
- update to libosmium 2.19.0
- change minimum required version of Cmake to 3.0


## [3.6.0rc1] - 2022-12-13

### Changed

- complete internal rewrite of the bindings for OSM data types
- invalid buffers are now checked on access time, no more reference count
  checks on leaving the handler callback


## [3.5.0] - 2022-11-09

### Added

- type annotations for the public interface
- new `ReplicationServer.set_request_parameter()` function to specify additional
  parameters to give to `requests.get()`

### Fixed

- writer now rolls back data buffer after exceptions (fixes #212)
- off-by-one error in computation of change ID from a start date
- socket timeout in pyosmium-get-changes/pyosmium-up-to-date was ignored
  falling back to waiting forever on requests

### Changed

- use format strings instead of `format()` where possible
- pyosmium-get-changes now prints an error message when there is a HTTP error
  during download
- overwriting `ReplicationServer.open_url()` is no longer recommended,
  use new `ReplicationServer.set_request_parameter()` function instead
- cookies for pyosmium-get-changes/pyosmium-up-to-date are now set via
  request parameters, removing the last use-case where urllib was used
- update bundled pybind11 to 2.10.1

## [3.4.1] - 2022-07-28

### Fixed

- allow building docs from built sources in PYTHONPATH again


## [3.4.0] - 2022-07-27

### Fixed

- finding the build directory when newer versions of setuptools are used

### Changed

- improve error message when writing to a writer that is already closed
- update to pybind 2.10.0
- drop support for Python 3.5


## [3.3.0] - 2022-03-22

### Added

- `add_box()` for osmium.osm.Header for setting the bbox in a OSM file
- SimpleWriter now can receive a customized header in its constructor
- SimpleWriter now accepts a list of RelationMember in then member parameter
  of `add_relation()`
- more tests for replication server and osm base types

### Fixed

- AttributeError when using pyosmium-get-changes with cookies (thanks @wiktorn)
- avoid memory leak in `apply_buffer()` functions in
  SimpleHandler and MergeInputReader
- maek sure close() is called for requests.Session and requests.Response
- documentation for `open_url()` now reflects its new behaviour
- build issue with raw ssize_t on Windows since Python 3.10

### Changed

- ReplicationServer is now a context manager
- allow any string-like object for `apply_file()`
- switch tests from nose to pytest
- use Python libraries instead of wget for downloading contrib packages
- update to libosmium 2.18.0 (requires now C++14)
- update to pybind11 2.9.1


## [3.2.0] - 2021-08-09

### Fixed

- merge change files correctly so that latest applied object comes first

### Changed

- switch to requests library for downloading files (thanks @jocelynj)
- update to libosmium 2.17.0
- update to pybind11 2.7.1

## [3.1.3] - 2021-02-05

### Fixed

- up-to-date: check if any updates are available before starting download
- AttributeError when writing replication headers and network is unreachable

### Changed

- update to pybind11 2.6.2

## [3.1.2] - 2021-01-13

### Fixed

- package pypi source wheel with correct libosmium version

## [3.1.1] - 2021-01-12

### Added

- support for lz4 compression (compiled in when library is found)

### Changed

- update to libosmium 2.16.0
- update to pybind11 2.6.1

## [3.1.0] - 2020-11-03

### Added

### Changed

- improved help messages for update tools
- update to pybind11 2.6

### Fixed

- pyosmium-up-to-date: fix missing flag when applying changes to history files
- smaller linting and documentation issues

## [3.0.1] - 2020-07-25

### Added

- allow to set user in mutable object

### Changed

- use current libosmium and protozero

### Fixed

- avoid leaking Python handle in timestamp conversion

## [3.0.0] - 2020-05-03

### Added

- socket timeouts for pyosmium-get-changes and pyosmium-up-to-date
- pyosmium-up-to-date: allow writing the diff to stdout (requires format option)

### Changed

- remove support for Python2 and Python 3.3

## [2.15.4] - 2020-02-29

### Added

- pyosmium-get-changes: allow to pipe updates to stdout
- doc: add more information about file updates

### Changed

- check for dangling references in callbacks
- use a custom HTTP user agent when requesting diffs
- use current libosmium

### Fixed

- replication: retry downloading truncated state files

## [2.15.3] - 2019-08-16

### Added

- `make_simple_handler()` convenience wrapper
- iterator for Tag type (for allowing to convert TagLists into python dicts)
- tests for examples
- tests for MP building and MergeInputReader

### Changed

- use current libosmium and protozero

### Fixed

- remove spurious 404 error message when downloading OSM diffs

## [2.15.2] - 2019-03-09

### Added

- NodeLocationsForWays (accidentally removed in 2.15.0)
- more tests

### Changed

- GIL lock now released while apply() is in C++ code

### Fixed

- unicode output of tag str() representation for python 2
- handling of tempfile in test for pyosmium_get_changes
- documentation for ends_have_same_location()

## [2.15.1] - 2019-01-24

### Added

- tests for pyosmium-get-changes

### Changed

- do not read data when checking for replication headers

### Fixed

- fix typo in sequence file reading of pyosmium-get-changes

## [2.15.0] - 2018-12-09

### Added

- more tests

### Changed

- replace boost-python with header only pybind11 library
- switch to cmake for configuration (called through setup.py)
- default node cache changed to flex_mem

## [2.14.4] - 2018-10-30

### Added

- allow to add arbitrary headers when updating files
- replication: custom URL opener
- cookie support for pyosmium-get-changes and pyosmium-up-to-date

### Changed

- pyosmium-up-to-date declares itself as 'generator'

### Fixed

- bug when reading sequence ID files in pyosmium-get-changes

## [2.14.3] - 2018-08-08

### Added

### Changed

### Fixed

- fix rounding error in tests

## [2.14.2] - 2018-08-07

### Added

- expose Coordinates struct and mercator projection functions

### Changed

- use current libosmium and protozero

### Fixed


## [2.14.1] - 2018-04-24

### Added

### Changed

### Fixed

- fix build script to find libboost-python on Darwin

## [2.14.0] - 2018-03-31

### Added

### Changed

- use current libosmium
- install protozero separately from libosmium
- installation documentation updated

### Fixed

## [2.13.0] - 2017-08-31

### Added

- tests for WKB factories and replication server
- str() and repr() implementations for all classes in osmium.osm
- when applying diffs to a handler, a location cache may be used

### Changed

- use new MultipolygonManager for building areas
- allow to access nodes in a NodeRefList with negative index
- use current libosmium

### Fixed

- pyosmium-get-changes exits with an error when no start sequence can
  be found


## [2.12.4] - 2017-08-19

### Added

### Changed

### Fixed

- make apply_reader_simple a template again
- minor fixes to documentation


## [2.12.3] - 2017-05-25

### Added

- links to appropriate mailing lists and issue trackers

### Changed

### Fixed

- handler functions not called when using replication service (#38)
- pyosmium-get-updates: bad variable name

## [2.12.2] - 2017-05-04

### Added

- build support for Windows
- various tests

### Changed

- python sources moved into src/ directory
- use current libosmium
- area.inner_rings() now takes an outer ring as parameter and returns an iterator

### Fixed

- force use of C++ compiler
- output type of index.map_types() function
- write buffers growing unbound

## [2.12.1] - 2017-04-11

### Added

- geometry factories for WKT and GeoJSON
- man pages for new tools
- get() function for TagList
- tests for TagList

### Changed

- example code simplified
- use current libosmium

### Fixed

- area creator always called (#32)
- various typos
- TagList [] accessor properly throws KeyError on missing element

## [2.12.0] - 2017-03-19

### Added

- WriteHandler for writing data directly to a file
- tools for downloading changes and updating a OSM files from these changes
- get/set functions for io.Header

### Changed

- use current libosmium

### Fixed

- various typos in documentation

## [2.11.0] - 2017-01-15

### Changed

- Use current libosmium


## [2.10.2] - 2016-11-16

### Added

- support for sdist creation (now published via Pypi)
- custom locations for libosmium and boost can be set via the
  environment variables `LIBOSMIUM_PREFIX` and `BOOST_PREFIX`.
- export bounding box from osmium::io::Header

### Changed

- Use libosmium 2.10.2

### Fixed

- various typos in documentation
- crash in replication handler on incomplete state files


## [2.9.0] - 2016-09-15

### Changed

- Use current libosmium


## [2.8.0] - 2016-08-08

### Changed

- Use current libosmium

### Fixed

- Works with different libosmium versions.


## [2.7.1] - 2016-06-01

### Added

- `apply_buffer()` for handling in-memory data
- MergeInputReader for reading and sorting multiple input files
- Functions using replication change files to update an OSM file or database.

### Changed

- Use current libosmium


## [2.6.0] - 2016-02-04

### Added

- Experimental write support, see documentation
- Multiple examples for writing data

### Changed

- Use current libosmium
- Improve timestamp to datetime conversion
- Simplified package structure that uses the compiled libs directly


## [2.5.4] - 2015-12-03

### Changed

- Use current libosmium
- README updates


## [2.5.3] - 2015-11-17

### Changed

- Use current libosmium


## [2.4.1] - 2015-08-31

### Changed

- Use current libosmium


## [2.3.0] - 2015-08-18

### Changed

- Use current libosmium


## [2.2.0] - 2015-07-04

### Changed

- Use current libosmium

### Fixed

- Exception not caught in test.


