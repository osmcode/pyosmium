
# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [unreleased] -

### Added

### Changed

### Fixed

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


