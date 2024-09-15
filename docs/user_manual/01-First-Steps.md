# First Steps

pyosmium is a library that processes data as a stream: it reads the data from
a file or other input source and presents the data to the user one object at
the time. This means that it can efficiently process large files with many
objects. The down-side is that it is not possible to directly access specific
objects as you need them. Instead it is necessary to apply some simple
techniques of caching and repeated reading of files to get all the data you
need. This takes some getting used to at the beginning but pyosmium gives
you the necessary tools to make it easy.

## File processing

pyosmium allows to process OSM files just like any other file: Open the
file by instantiating a [FileProcessor][osmium.FileProcessor], then iterate
over each OSM object in the file with a simple 'for' loop.

Lets start with a very simple script that lists the contents of file:


!!! example
    === "Code"
    ```python
    import osmium

    for obj in osmium.FileProcessor('buildings.opl'):
        print(obj)
    ```

    === "Output"
    ```
    n1: location=45.0000000/13.0000000 tags={}
    n2: location=45.0001000/13.0000000 tags={}
    n3: location=45.0001000/13.0001000 tags={}
    n4: location=45.0000000/13.0001000 tags={entrance=yes}
    n11: location=45.0000000/13.0000000 tags={}
    n12: location=45.0000500/13.0000000 tags={}
    n13: location=45.0000500/13.0000500 tags={}
    n14: location=45.0000000/13.0000500 tags={}
    w1: nodes=[1,2,3,4,1] tags={}
    w2: nodes=[11,12,13,14,11] tags={}
    r1: members=[w1,w2], tags={type=multipolygon,building=yes}
    ```

While iterating over the file, pyosmium decodes the data from the file
in the background and puts it into a buffer. It then returns a
_read-only view_ of each OSM object to Python. This is important to always
keep in mind. pyosmium never shows you a full data object, it only ever
presents a view. That means you can read and process the information about
the object but you cannot change it or keep the object around for later. Once
you retrieve the next object, the view will no longer be valid.

To show you what happens, when you try to keep the objects around, let us
slightly modify the example above. Say you want to have a more compact output
and just print for each object type, which IDs appear in the file. You might
be tempted to just save the object and create the formatted output only after
reading the file is done:

!!! bug "Buggy Example"
    === "Code"
    ```python
    # saves object by their type, more about types later
    objects = {'n' : [], 'w': [], 'r': []}

    for obj in osmium.FileProcessor('buildings.opl'):
        objects[obj.type_str()].append(obj)

    for otype, olist in objects.items():
        print(f"{otype}: {','.join(o.id for o in olist)}")
    ```

    === "Output"
    ```
    Traceback (most recent call last):
      File "bad_ref.py", line 10, in <module>
        print(f"{otype}: {','.join(o.id for o in olist)}")
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "bad_ref.py", line 10, in <genexpr>
        print(f"{otype}: {','.join(o.id for o in olist)}")
                                   ^^^^
      File "osmium/osm/types.py", line 313, in id
        return self._pyosmium_data.id()
               ^^^^^^^^^^^^^^^^^^^^^^^^
    RuntimeError: Illegal access to removed OSM object
    ```

As you can see, the code throws a runtime error complaining about an
'illegal access'. The `objects` dictionary doesn't contain any OSM objects.
It just has collected all the views on the objects. By the time the view
is accessed in the print function, the buffer the view points to is long gone.
pyosmium has invalidated the view. In practise this means that you need to
make an explicit copy of all information you need outside the loop iteration.

The code above can be easily "fixed" by saving only the id instead of the full
object. This also happens to be much more memory efficient:

!!! example
    === "Code"
    ```python
    objects = {'n' : [], 'w': [], 'r': []}

    for obj in osmium.FileProcessor('buildings.opl'):
        objects[obj.type_str()].append(obj.id)

    for otype, olist in objects.items():
        print(f"{otype}: {','.join(str(id) for id in olist)}")
    ```
    === "Output"
    ```
    n: 1,2,3,4,11,12,13,14
    w: 1,2
    r: 1
    ```

The output shows IDs for three different kind of objects: nodes, ways and
relations. Before we can continue, you need to understand the basics about
these types of objects and of the OpenStreetMap data model. If you are already
familiar with the structure of OSM data, you can go directly to the next
chapter.

## OSM data model

OpenStreetMap data is organised as a topological model. Objects are not
described with geometries like most GIS models do. Instead the objects are
described in how they relate to points in the world. This makes a huge
difference in how the data is processed.

An OSM object does not have a pre-defined function. What an object represents
is described with a set of properties, the _tags_. This is a simple key-value
store of strings. The meaning of the tags is not part of the data model
definition. Except for some minor technical limits, for example a maximum
length, any string can appear in the key and value of the tags. What keys and
values are used is decided through _consensus between users_. This gives OSM
a great flexibility to experiment with new kinds of data and evolve its
dataset. Over time a large set of agreed-upon tags has emerged for most kinds
of objects. These are the tags you will usually work with. You can search the
documentation in the [OSM Wiki](https://wiki.openstreetmap.org/) to find
out about the tags. It is also always useful to consult
[Taginfo](https://taginfo.openstreetmap.org/), which shows statistics over the
different keys and value in actual use.

Tags are common to all OSM objects. After that there are three kinds of
objects in OSM: nodes, ways and relations.

### Nodes

A node is a point on the surface of the earth. Its location is described through
its latitude and longitude using projection WSG84.

### Ways

Ways are lines that are created by connecting a sequence of nodes. The
nodes are described with the ID of a node in the database. That means
that a way object does not directly have coordinates. To find out about
the coordinates where the way is located, it is necessary to look up the
nodes of the way in the database and get their coordinates.

Representing a way through nodes has another interesting side effect:
many of the nodes in OSM are not meaningful in itself. They don't represent
a bus stop or lamp post or entrance or any other point of interest. They
only exist as supporting points for the ways and don't have any tags.

When a way ends at the same node ID where it starts, then the way may be
interpreted as representing an area. If it is really an area or just a linear
feature that happens to circle back on itself (for example, a fence around a
garden) depends on the tags of the way. Areas are handled more
in-depth in the chapter
[Working with Geometries](03-Working-with-Geometries.md#areas).

### Relations

A relation is an ordered collection of objects. Nodes, ways and relations all
can be a member in a relation. In addition, a relation member can be assigned
a _role_, a string that describes the function of a member. The data model
doesn't define what relations should be used for or how the members should
be interpreted.

## Forward and backward references

The topologic nature of the OSM data model means that an OSM object rarely
can be regarded in isolation. OSM ways are not meaningful without the
location information contained in its nodes. And conversely, changing the
location in a way also changes the geometry of the way even though the way
itself is not changed. This is an important concept to keep in mind when
working with OSM data. In this manual, we will use the terms forward and
backward references when talking about the dependencies between objects:

* A __forward reference__ means that an object is referenced to by another.
  Nodes appear in ways. Ways appear in relations. And a node may even have
  an indirect forward reference to a relation through a way it appear in.
  Forward references are important when tracking changes. When the location
  of a node changes, then all its forward references have to be reevaluated.

* A __backward reference__ goes from an object to its referenced children.
  Going from a way to its containing nodes means following a backward
  reference. Backward references are needed to get the complete geometry of
  an object: given that only nodes contain location information, we have
  to follow the backward references for ways and relations until we reach
  the nodes.

## Order in OSM files

OSM files usually follow a sorting convention to make life easier for
processing software: first come nodes, then ways, then relations. Each
group of objects is ordered by ID. One of the advantages of this order
is that you can be sure that you have been already presented with all
backward references to an object, when it appears in the processing loop.
Knowing this fact can help you optimise how often you have to read through
the file and speed up processing.

Sadly, there is an exception to the rule which is nested relations:
relations can of course contain other relations with a higher ID. If you
have to work with nested relations, rescanning the file multiple times
or keeping large parts of the file in memory is pretty much always unavoidable.
