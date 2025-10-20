# Working With Change Files

OpenStreetMap is a database that is constantly changing. Data is added,
improved and refined by the thousands of contributors around the world.
A standard OpenStreetMap data file, like the "planet file" only represents
a _snapshot_ of the OpenStreetMap database: the state of the world at a given
point in time. For many applications it is completely sufficient to work
with such a snapshot. To get the latest version of the data, they can
simply download another snapshot and process the data from scratch.
For some applications, however, it is necessary to keep their view of
OpenStreetMap always up-to-date with the latest version of the data.
This is where _OSM change files_ (also known as _OSM diff files_)
come into play.

## OSM change files

OpenStreetMap is a database with immutable data: objects are never directly edited.
Whenever you change an object, a new version of the object is created. In a similar
vain, it is not really possible to delete an object. You can only create
a new version of the object that is marked as being invisible.

So, technically speaking an OSM database knows only one operation: adding a
new version of an object. Change files are a collection of these additions to
the main database over a given time period.

When it comes to the file format and content an OSM change file does not
differ greatly from a normal OSM file: a change file is a collection of nodes,
ways and relations. There are just some meta attributes of the objects that
are more relevant than before: the **version** number and the **deleted** flag. 

A single modification may describe one of three operations:

* **Creation.** A new node, way or relation is added. It has always the
  version number 1.
* **Modification.** An existing object was directly modified: tags of the object,
  the location of a node, the node list of a way or the member list of a
  relation have been changed. A modified object has a version number larger
  than 1 and the deleted flag is not set.
* **Deletion.** The object has been marked as deleted. The deleted flag is
  set to true. Delete objects are usually not included in normal snapshot files.
  This is an important difference when working with change files.

There is no explicit _undelete_ operation. To undo a deletion, one can simply
_modify_ the object again and create a new version of the object with the
delete flag set to false.

!!! danger
    Undoing a deletion is an action that regularly happens in the
    OpenStreetMap database. It can, for example, happen when the edit of a
    user gets reverted because it was bogus.
    Always be prepared for an object to reappear.

## About replication services

There are various ways to produce an OSM change file but the by far most
important source of change files are _replication services_. These services
publish in regular intervals all changes to the data that have happened in
the area of interest.

Change files from replication services are
consecutively numbered. Each change is guaranteed to start exactly where
the previous change ended, so that by applying one change after another to
an existing planet (or extract), you can get a new complete snapshot
that corresponds to a newer version of the OSM database.

Each change file is accompanied by a state file which has information about
the time of the change file. This can be used to find the right synchronisation
point when working with OSM files from different sources.

## Full vs. simplified change files

A change file that comes from a replication service usually contains the
full set of changes for a given time span. This means in particular that
there may be multiple versions of the same object when it was changed
multiple times in a very short time. In OSM, these kind of change files
are referred to as being _full_.

There are many use cases, where these intermediate versions
are not really of interest. When updating a planet file, only the latest
version of an object will remain. For these use cases, change files may be
_simplified_. A simplified change file only keeps the latest version of
each object. Programs like `pyosmium-get-changes` can produce either version
of a change file. Usually, you want to work with simplified change files
unless you are interested in the exact history of changes to OSM.


## Referential integrity of change files

We have previously discussed that the OSM data format is a topological format:
ways contain references to nodes and relations can contain references to any
kind of OSM object. This has two important implications for change files:

* __Referential incompleteness__ 
  When a way or relation is changed, then only the way or relation
  itself will be included in a normal change file. This means, for example, that
  you will usually not be able to reconstruct the geometry of a changed way
  by looking at a change file alone. The necessary information about the
  location of the way is saved in its nodes and these nodes will not be
  present in the change file if they haven't been changed. You cannot
  even rely on anything when a way or relation has been newly created: the
  nodes or members the new object references may have been created
  many months ago.

* __Indirect modifications__
  When a node that is part of a way is moved to a different location, then the
  geometry of the way is changed. The OSM change file, however, will only contain
  the new version of the node with the new location. The way itself has not
  been changed: it still refers to the same list of nodes. Therefore the way
  does not appear in the change file even though it might need to be updated
  in your data.

The reminder of this section discusses how references can be resolved when
working with change files.

## Strategies for resolving forward and backward references for change files

A change file can only ever fully interpreted in conjunction with a snapshot
of the planet that corresponds to the time of the first change in the
change file. Keeping such a planet snapshot is unfortunately not an easy
task because of the sheer size of the full planet data. However, there are
some shortcuts available depending on what kind of data you are interested in.

### Following changes on nodes

If you are only working with OSM nodes, no special provision are necessary.
Every change in a node will make it appear in the change file.

### Following changes on ways

Ways reference nodes. To derive the node geometry of a changed way, you need
to keep track of the location of each node. This process is very similar to
the process of tracking nodes when
[creating way geometries](03-Working-with-Geometries.md/#line-geometries).
You need to add a location cache when processing the change file. The
main difference is that the location cache needs to made persistent in a file
and that it needs to be pre-filled from the locations in your reference
planet. You can use the location storage type `sparse_file_array` to
create a persistent file which can be updated. Be aware that such a file
is around 100GB in size these days. Populate the file by running with
your planet file (here called `planet.osm.pbf`) as follows:

```python
import osmium

with osmium.io.Reader("planet.osm.pbf, osmium.osm.osm_entity_bits.NODE) as reader:
    idx = osmium.index.create_map("sparse_file_array,nodecache.data")

    osmium.apply(reader, osmium.NodeLocationsForWays(idx))
```

After this has run the file `nodecache.data` will contain location of all nodes
that were found in the input file. Subsequently you can use the node cache
with your change file just as described in the Geometry chapter:

```python
import osmium

for obj in osmium.FileProcessor("mychange.osm.xml")\
                 .with_locations("sparse_file_array,nodecache.data"):
    if obj.is_way():
        coords = ", ".join((f"{n.lon} {n.lat}" for n in o.nodes if n.location.valid()))
        print(f"Way {o.id}: LINESTRING({coords})")
```

Note that this piece of code not only uses the locations from the cache file
but it also __updates__ the cache file with the locations from your change file.
This is usually what you want. You can process subsequent change file and
always have the reference to the corresponding locations.


!!! tip
    In theory there are no restrictions to which nodes may be references by
    a way. Thus, in theory, you always need to keep the
    full set of node location that exist in OSM. In practise, edits mostly
    happen in a confined area. Therefore, when your geographic area of
    interest is limited, it is sufficient to only keep the node locations
    that fall within that area. Just add a large enough buffer zone to
    account for nodes being moved around.

## Keeping a full planet snapshot

After a full planet or an extract has been downloaded, it first needs to be
brought in sync with the replication source of change files you are using.
This is easiest done with the
[pyosmium-up-to-date](10-Replication-Tools.md/#updating-a-planet-or-extract) tool.
It takes an OSM file and a replication source and creates a new OSM file
which is perfectly synchronised with the replication source. It will also
tell you what the sequence number is of the next file to download. Use this
sequence number to get the next change file. You can either download a
single change file or use
[pyosmium-get-changes](10-Replication-Tools.md/#creating-change-files-for-updating-databases) to download multiple change files at once and combine them.

Now that you have the change file, you can use the synchronised planet to
look up any missing OSM objects referenced in the file. Once you are done with
processing, you need to merge the synchronised planet with the change file,
for example using
[osmium apply-changes](https://docs.osmcode.org/osmium/latest/osmium-apply-changes.html).
After that you have a new synchronised planet ready for processing with the
next change file.

If you regularly work with change data, have a look at
[osm2pgsql](https://osm2pgsql.org/). This is an application that stores OSM
data in a PostgreSQL database and also handles updates and change files.
