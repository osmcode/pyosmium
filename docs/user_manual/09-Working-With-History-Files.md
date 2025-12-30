# Working With History Files

An OSM data file usually contains the data of a snapshot of the OpenStreetMap
database at a certain point in time. The main OpenStreetMap database contains
not only the latest view of the data but every single change ever made.
This full version of OpenStreetMap editing history is published in so called
_history files_. pyosmium can process these files but they do
require some special attention.

## Make-up of history files

We have already discussed in the
[chapter on change files](08-Working-With-Change-Files.md) what
a single change to an OSM object looks like. It has the same format as an
ordinary OSM object in a snapshot, except that meta data properties like
`version` and `visibility` are important to take into account to understand
what part of the history the object belongs to. That means that history
files can be processed often with the same tools. Extra care just needs
to be taken because each OSM object appears in the file multiple times in
different versions.

History files are conventionally sorted by OSM type, OSM ID and version. That
means that, when reading a history file sequentially like pyosmium does, then
all the versions of an object follow each other in order. However, it also
means that history files are not sorted by time. And this has important
implications when resolving references.

## Resolving references in history files

OSM objects only change when its own properties change. There is no new version
when the data changes that it refers to. For example, an OSM way will get
a new version, when a tag is modified or a node added to the list of nodes
that make up the way. When a node that is referenced by the way changes its
position, then the way remains the same. As a result, when working with way
geometries or objects created from relation members, it is not unusual that
between two versions of a way or relations, there are many hidden subversions
due to modifications to the nodes or members. In order to resolve these
subversions, you need to keep a cache of all the versions of the nodes, ways
and relations that are relevant and then use the timestamps of the object
to infer, which versions of the members are relevant between two versions
of the parent object.

Note that you cannot use the standard caching mechanisms like the
[location storage](03-Working-with-Geometries.md#line-geometries)
or the standard area processor. These will only keep the latest version of
each object. There are currently no data structures supporting history files
in particular.

!!! Danger
    Timestamps are the only way to resolve the right version of dependent
    objects. Still you need to take them with a grain of salt. In the early
    days of OpenStreetMap, the servers creating the timestamps for new object
    versions weren't always correctly in sync. And so it is possible to find
    referential errors where a way refers to a node that according to the
    timestamps hasn't existed, when the way was created. The synchronisation
    issues have long since been resolved but you will encounter them when
    working with historic data.
