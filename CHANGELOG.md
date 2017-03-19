
# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [unreleased] -

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

[unreleased]: https://github.com/osmcode/pyosmium/compare/v2.12.0...HEAD
[2.12.0]: https://github.com/osmcode/pyosmium/compare/v2.11.0...v2.12.0
[2.11.0]: https://github.com/osmcode/pyosmium/compare/v2.10.2...v2.11.0
[2.10.2]: https://github.com/osmcode/pyosmium/compare/v2.9.0...v2.10.2
[2.9.0]: https://github.com/osmcode/pyosmium/compare/v2.8.0...v2.9.0
[2.8.0]: https://github.com/osmcode/pyosmium/compare/v2.7.1...v2.8.0
[2.7.1]: https://github.com/osmcode/pyosmium/compare/v2.6.0...v2.7.1
[2.6.0]: https://github.com/osmcode/pyosmium/compare/v2.5.4...v2.6.0
[2.5.4]: https://github.com/osmcode/pyosmium/compare/v2.5.3...v2.5.4
[2.5.3]: https://github.com/osmcode/pyosmium/compare/v2.4.1...v2.5.3
[2.4.1]: https://github.com/osmcode/pyosmium/compare/v2.3.0...v2.4.1
[2.3.0]: https://github.com/osmcode/pyosmium/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/osmcode/pyosmium/compare/v2.1.0...v2.2.0

