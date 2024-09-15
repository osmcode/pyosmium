# Overview

This user manual gives you an introduction on how to process OpenStreetMap
data

- [**First Steps**](user_manual/01-First-Steps.md)
  gives an overview of the OSM data model and how pyosmium processes the data
- [**Extracting Object Data**](user_manual/02-Extracting-Object-Data.md)
  looks into what data is contained inside an OSM object
- [**Working with Geometries**](user_manual/03-Working-with-Geometries.md)
  explains how to create points, line strings and polygons for OSM objects
- [**Working with Filters**](user_manual/04-Working-with-Filters.md)
  introduces how to select the right data to process
- [**Working with Handlers**](user_manual/05-Working-with-Handlers.md)
  shows how to work with a callback-based approach for processing data
- [**Writing data**](user_manual/06-Writing-Data.md)
  explains how to create a new OSM file
- [**Input Formats and Other Sources**](user_manual/07-Input-Formats-And-Other-Sources.md)
  looks into other sources for OSM data than files
- [**Working With Change Files**](user_manual/08-Working-With-Change-Files.md)
  explores how to handle OSM diff files with updates
- [**Working with History Files**](user_manual/09-Working-With-History-Files.md)
  looks into the specifics of OSM files containing multiple versions of an object
- [**Replication Tools**](user_manual/10-Replication-Tools.md)
  lists the means how to obtain OSM update data with pyosmium

pyosmium builds on the fast and efficient [libosmium](https://osmcode.org/libosmium/)
library. It borrows many of its concepts from libosmium. For more in-depth
information, you might also want to consult the
[**libosmium manual**](https://osmcode.org/libosmium/manual.html).
