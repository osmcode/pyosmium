# Working with Geometries

When working with map data, sooner or later, you will need the geometry
of an object: a point, a line or a polygon. OSM's topologic data model
doesn't make them directly available with each object. In order to build
a geometry for an object, the location information from referenced nodes
need to be collected and then the geometry can be assembled from that.
pyosmium provides a number of data structures and helpers to create
geometries for OSM objects.

## Geometry types

### Point geometries

OSM nodes are the only kind of OSM object that produce a point geometry.
The location of the point is directly stored with the OSM nodes. This
makes it straightforward to extract such a geometry:

!!! example
    === "Code"
    ```python
    for o in osmium.FileProcessor('buildings.opl', osmium.osm.NODE):
        print(f"Node {o.id}: lat = {o.lat} lon = {o.lon}")
    ```
    === "Output"
    ```
    Node 1: lat = 13.0 lon = 45.0
    Node 2: lat = 13.0 lon = 45.0001
    Node 3: lat = 13.0001 lon = 45.0001
    Node 4: lat = 13.0001 lon = 45.0
    Node 11: lat = 13.00001 lon = 45.00001
    Node 12: lat = 13.00001 lon = 45.00005
    Node 13: lat = 13.00005 lon = 45.00005
    Node 14: lat = 13.00005 lon = 45.00001
    ```

### Line geometries

Line geometries are usually created from OSM ways. The OSM way object does
not contain the coordinates of a line geometry directly. It only contains a
list of references to OSM nodes. To create a line geometry from an OSM way,
it is necessary to look up the coordinate of each referenced node.
pyosmium provides an efficient way to do so: the location storage. The storage
automatically records the coordinates of each node that is read from the file
and caches them for future use. When later a way is read from a file, the
list of nodes in the way is augmented with the appropriate coordinates.
Location storage is not enabled by default. To add it to the processing,
use the function [`with_locations()`][osmium.FileProcessor.with_locations]
of the FileProcessor.

!!! example
    === "Code"
    ```python
    for o in osmium.FileProcessor('../data/buildings.opl').with_locations():
        if o.is_way():
            coords = ", ".join((f"{n.lon} {n.lat}" for n in o.nodes if n.location.valid()))
            print(f"Way {o.id}: LINESTRING({coords})")
    ```
    === "Output"
    ```
    Way 1: LINESTRING(45.0 13.0, 45.0001 13.0, 45.0001 13.0001, 45.0 13.0001, 45.0 13.0)
    Way 2: LINESTRING(45.00001 13.00001, 45.00005 13.00001, 45.00005 13.00005, 45.00001 13.00005, 45.00001 13.00001)
    ```


Not all OSM files are _reference-complete_. It can happen that some nodes
which are referenced by a way are missing from a file. Always write your
code so that it can work with incomplete geometries. In particular, you
should be aware that there is no guarantee that an OSM way will translate
into a valid line geometry. An OSM way may consist of only one node.
Or two subsequent coordinates in the line are exactly at the same position.

pyosmium provides different implementations for the location storage. The
default should be suitable for small to medium-sized OSM files. See the
paragraph on [Location storage][location-storage] below for more information
on the different types of storages and how to switch them.

### Areas

OSM has two different ways to model area geometries: they may be derived
from way objects or relation objects.

A way can be interpreted as an area when it is _closed_. That happens when
the first and the last node are exactly the same. You can use the function
[`is_closed()`][osmium.osm.Way.is_closed].

Not every closed way necessarily represents and area. Think of a little
garden with a fence around it. If the OSM way represents the garden, then it
should be interpreted as an area. If it represents the fence, then it is a
line geometry that just happens to go full circle. You need to look at the
tags of a way in order to decide if it should become an area or a line,
or sometimes even both.

There are two types of relations that also represent areas. If the relation
is tagged with `type=multipolygon` or `type=boundary` then it is by
convention an area independently of all the other tags of the relation.

pyosmium implements a special handler for the processing of areas. This
handler creates a new type of object, the [Area][osmium.osm.Area] object,
and makes it available like the other OSM types. It can be enabled
with the [`with_areas()`][osmium.FileProcessor.with_areas] function:

!!! example
    === "Code"
    ```python
    objects = ''
    areas = ''
    for o in osmium.FileProcessor('../data/buildings.opl').with_areas():
        objects += f" {o.type_str()}{o.id}"
        if o.is_area():
            areas += f" {o.type_str()}{o.id}({'w' if o.from_way() else 'r'}{o.orig_id()})"

    print("OSM objects in this file:", objects)
    print("Areas in this file:", areas)
    ```
    === "Output"
    ```
    OSM objects in this file:  n1 n2 n3 n4 n11 n12 n13 n14 w1 w2 r1 a2 a3
    Areas in this file:  a2(w1) a3(r1)
    ```

Note how Area objects are added to the iterator _in addition_ to the original
OSM data. During the processing of the loop, there is first OSM way 1 and
then the Area object 2, which corresponds to the same way.

When the area handler is enabled, the FileProcessor scans the file twice:
during the first run information about all relations that might be areas
is collected. This information is then used in the main run of the file
processor, where the areas are assembled as soon as all the necessary
objects that are part of each relation have been collected.

The area handler automatically enables a location storage because it needs
access to the node geometries. It will set up the default implementation.
To use a different implementation, simply use `with_locations()` with
a custom storage together with `with_areas()`.

#### The pyosmium Area type

The Area type has the same common attributes as the other OSM types.
However, it produces its own special ID space. This is necessary because
an area might be originally derived from a relation or way. When derived
from a way, the ID is computed as `2 * way ID`. When it is derived from
a relation, the ID is `2 * relation ID + 1`. Use the function
[`from_way()`][osmium.osm.Area.from_way] to check what type the original OSM
object is and the function [`orig_id()`][osmium.osm.Area.orig_id]
to get the ID of the underlying object.

The polygon information is organised in lists of rings. Use
[`outer_rings()`][osmium.osm.Area.outer_rings] to iterate over the rings
of the polygon that form outer boundaries of the polygon. The data structures
for these rings are node lists just like the ones used in OSM ways.
They always form a closed line that goes clockwise. Each outer ring can have
one or more holes. These can be iterated through with the
[`inner_rings()`][osmium.osm.Area.inner_rings] function. The inner rings
are also a node list but will go anti-clockwise. To illustrate how to process
the functions, here is the simplified code to create the
[WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)
representation of the polygon:

!!! example
    === "Code"
    ```python
    for o in osmium.FileProcessor('../data/buildings.opl').with_areas():
        if o.is_area():
            polygons = []
            for outer in o.outer_rings():
                rings = "(" + ", ".join((f"{n.lon} {n.lat}" for n in outer if n.location.valid())) + ")"
                for inner in o.inner_rings(outer):
                    rings += ", (" + ", ".join((f"{n.lon} {n.lat}" for n in outer if n.location.valid())) + ")"
                polygons.append(rings)
            if o.is_multipolygon():
                wkt = f"MULTIPOLYGON(({'), ('.join(polygons)}))"
            else:
                wkt = f"POLYGON({polygons[0]})"
            print(f"Area {o.id}: {wkt}")        
    ```
    === "Output"
    ```
    Area 2: POLYGON((45.0 13.0, 45.0001 13.0, 45.0001 13.0001, 45.0 13.0001, 45.0 13.0))
    Area 3: POLYGON((45.0 13.0, 45.0001 13.0, 45.0001 13.0001, 45.0 13.0001, 45.0 13.0), (45.0 13.0, 45.0001 13.0, 45.0001 13.0001, 45.0 13.0001, 45.0 13.0))
    ```


### Geometries from other relation types

OSM has many other relation types apart from the area types. pyosmium has
no special support for other relation types yet. You need to manually
assemble geometries by collecting the geometries of the members.

## Geometry Factories

pyosmium has a number of geometry factories to make it easier to convert
an OSM object to well known geometry formats. To use them, instantiate
the factory once and then hand in the OSM object to one of the create
functions. A code snippet that converts all objects into WKT format looks
approximately like that:

!!! example
    ```python
    fab = osmium.geom.WKTFactory()

    for o in osmium.FileProcessor('../data/buildings.opl').with_areas():
        if o.is_node():
            wkt = fab.create_point(o.location)
        elif o.is_way() and not o.is_closed():
            wkt = fab.create_linestring(o.nodes)
        elif o.is_area():
            wkt = fab.create_multipolygon(o)
        else:
            wkt = None # ignore relations
    ```

There are factories for GeoJSON ([`osmium.geom.GeoJSONFactory`][]),
well-known text ([`osmium.geom.WKTFactory`][])
and well-known binary ([`osmium.geom.WKBFactory`][]) formats.

## Python Geo Interface

If you want to process the geometries with Python libraries like
[shapely](https://shapely.readthedocs.io)[^1] or [GeoPandas](https://geopandas.org),
then the standardized [__geo_interface__](https://gist.github.com/2217756)
format can come in handy.

[^1]: Shapely only received full support for geo_interface geometries with
      features in version 2.1. For older versions create WKT geometries as
      explained above and create Shapely geometries from that.

pyosmium has a special filter [GeoInterfaceFilter][osmium.filter.GeoInterfaceFilter]
which enhances pyosmium objects with a `geo_interface` attribute.
This allows libraries that support this interface to directly consume the
OSM objects. The GeoInterfaceFilter needs location information to create
the geometries. Don't forget to add `with_locations()` and/or
`with_areas()` to the FileProcessor.

Here is an example that computes the total length of highways using
the geometry functions of shapely:

!!! example
    === "Code"
    ```python
    from shapely.geometry import shape

    total = 0.0
    for o in osmium.FileProcessor('liechtenstein.osm.pbf').with_locations().with_filter(osmium.GeoHandler()):
        if o.is_way() and 'highway' in o.tags:
            # Shapely has only support for Features starting from version 2.1,
            # so lets cheat a bit here.
            geom = shape(o.__geo_interface__['geometry'])
            # Length is computed in WGS84 projection, which is practically meaningless.
            # Lets pretend we didn't notice, it is an example after all.
            total += geom.length

    print("Total length:", total)
    ```
    === "Output"
    ```
    Total length: 14.58228287312081
    ```


For an example on how to use the Python Geo Interface together with GeoPandas,
have a look at the [Visualisation Recipe](../cookbooks/Visualizing-Data-With-Geopandas.ipynb).

## Location Storage

See the [Osmium manual](https://osmcode.org/osmium-concepts/#indexes)
for the different types of location storage.
