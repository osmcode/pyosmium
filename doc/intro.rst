Basic Usage
===========

The following chapter gives a practical introduction on how to use Pyosmium.
It is assumed that you already have a basic knowledge about the
`OSM data model`_.

For a more detailed introduction into the design of the osmium library, the
reader is referred to the `osmium documentation`_.

.. _OSM data model: http://wiki.openstreetmap.org/wiki/Elements
.. _osmium documentation: http://osmcode.org/libosmium/manual/libosmium-manual.html

Reading OSM Data
----------------

Using Handler Classes
^^^^^^^^^^^^^^^^^^^^^

OSM file parsing by osmium is built around the concept of handlers. A handler
is a class with a set of callback functions. Each function processes exactly
one type of object as it is read from the file.

Let's start with a very simple handler that counts the nodes in the
input file::

    import osmium

    class CounterHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.num_nodes = 0

        def node(self, n):
            self.num_nodes += 1

A handler first of all needs to inherit from one of the handler classes.
At the moment this is always :py:class:`osmium.SimpleHandler`. Then it
needs to implement functions for each object type it wants to process. In
our case it is exactly one function `node()`. All other potential callbacks
can be safely ignored.

Now the handler needs to be applied to an OSM file. The easiest way to
accomplish that is to call the :py:meth:`~osmium.SimpleHandler.apply_file`
convenience function, which in its simplest form only requires the file name
as a parameter. The main routine of the node counting application
therefore looks like this::

    if __name__ == '__main__':

        h = CounterHandler()

        h.apply_file("test.osm.pbf")

        print("Number of nodes: %d" % h.num_nodes)

That already finishes our node counting program.

Inspecting the OSM objects
^^^^^^^^^^^^^^^^^^^^^^^^^^

Counting nodes is actually boring because it completely ignores the
content of the nodes. So let's change the handler to only count hotels
(normally tagged with ``tourism=hotel``). They may be tagged as nodes, ways
or relations, so handler functions for all three types need to be implemented::

    import osmium

    class HotelCounterHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.num_nodes = 0

        def count_hotel(self, tags):
            if tags['tourism'] == 'hotel':
                self.num_nodes += 1

        def node(self, n):
            self.count_hotel(n.tags)

        def way(self, w):
            self.count_hotel(w.tags)

        def relation(self, r):
            self.count_hotel(r.tags)

A reference to the object is always given as the only parameter to the
handler functions. The objects have some common methods and attributes,
listed in :py:class:`osmium.osm.OSMObject`, and some that are specific to
each type. As all objects have tags, it is possible to reuse the same
implementation for all types. The main function remains the same.

It is important to remember that the object
references that are handed to the handler are only temporary. They will
become invalid as soon as the function returns. Handler functions *must*
copy any data that should be kept for later use into their own data
structures. This also includes attributes like tag lists.

Handling Geometries
^^^^^^^^^^^^^^^^^^^

Because of the way that OSM data is structured, osmium needs to internally
cache node geometries, when the handler wants to process the geometries of
ways and areas. The :py:meth:`~!osmium.SimpleHandler.apply_file` method cannot
deduce by itself if this cache is needed. Therefore locations need to be
explicitly enabled by setting the locations parameter to True::

    h.apply_file("test.osm.pbf", locations=True, idx='sparse_mem_array')

The third parameter `idx` is optional and states what kind of cache
osmium is supposed to use. The default `sparse_mem_array` is a good
choice for small to medium size extracts of OSM data. If you plan to
process the whole planet file, `dense_mmap_array` is better suited.
If you want the cache to be persistent across invocations, you
can use `dense_file_array` giving an additional file location for the
cache like that::

    h.apply_file("test.osm.pbf", locations=True, idx='sparse_file_array,example.nodecache')

where `example.nodecache` is the name of the cache file.

Interfacing with Shapely
^^^^^^^^^^^^^^^^^^^^^^^^

Pyosmium is a library for processing OSM files and therefore offers almost
no functionality for processing geometries further. There are other libraries
for that purpose. To interface with these libraries you can simply convert the
osmium geometries into WKB or WKT format and import the result. The following
example uses the libgeos wrapper `Shapely`_ to compute the total way length::

    import osmium
    import shapely.wkb as wkblib

    # A global factory that creates WKB from a osmium geometry
    wkbfab = osmium.geom.WKBFactory()

    class WayLenHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.total = 0

        def way(self, w):
            wkb = wkbfab.create_linestring(w)
            line = wkblib.loads(wkb, hex=True)
            # Length is computed in WGS84 projection, which is practically meaningless.
            # Lets pretend we didn't notice, it is an example after all.
            self.total += line.length

    if __name__ == '__main__':
        h = WayLenHandler()
        h.apply_file("test.osm.pbf", locations=True)
        print("Total length: %f" % h.total)

.. _Shapely: http://toblerity.org/shapely/index.html


Writing OSM Data
----------------

:py:class:`osmium.SimpleWriter` is the main class that takes care of
writing out OSM data to a file. The file name must be given when the
writer is constructed. Its suffix determines the format of the data.
For example::

    writer = osmium.SimpleWriter('nodes.osm.bz2')

opens a new writer for a packed OSM XML file. Objects can be written
by using one of the writers ``add_*`` functions.

A simple handler, that only writes out all the nodes from the input
file into our new ``nodes.osm.bz2`` file would look like this::

    import osmium

    class NodeWriter(osmium.SimpleHandler):
        def __init__(self, writer):
            osmium.SimpleHandler.__init__(self)
            self.writer = writer

        def node(self, n):
            self.writer.add_node(n)

This example shows that an unmodified object can be written out directly
to the writer. Normally, however, you want to modify some data. The native
osmium OSM types are immutable and cannot be changed directly. Therefore
you have to create a copy that can be changed. The ``node``, ``way`` and ``relation``
objects offer a convenient ``replace()`` function to achieve exactly that.
The function makes a copy and at the same time replaces all attributes where
new values are given as parameters to the function.

Let's say you want to
remove all the user names from your nodes before saving them to the new
file (maybe to save some space), then the ``node()`` handler callback above
needs to be changed like this::

    class NodeWriter(osmium.SimpleHandler):
        ...

        def node(self, n):
            self.writer.add_node(n.replace(user=""))

``replace()`` creates a new instance of an ``osmium.osm.mutable`` object. These
classes are python implementations of the native object types in ``osmium.osm``.
They have exactly the same attributes but they are mutable.

A writer is able to process the mutable datatypes just like the native osmium
types. In fact, a writer is able to process any python object. It just expects
suitably named attributes and will simply assume sensible default values for
attributes that are missing.

.. note::

    It is important to understand that ``replace()`` only makes a shallow copy
    of the object. Tag, node and member lists are still native osmium objects.
    Normally this is what you want because the writer is much faster writing
    these native objects than pythonized copies. However, it means that you
    cannot use ``replace()`` to create a copy of the object that can be kept
    after the handler callback has finished.
