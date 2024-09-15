# OSM Objects

This chapter explains more about the different object types that are
returned in pyosmium and how to access its data.

## Determining the Type of Object

pyosmium may return five different types of objects. First there are the
three base types from the OSM data model already
[introduced in the last chapter][osm-data-model]:
nodes, ways and relations. Next there is an _area type_. It is explained
in more detail in the [Geometry chapter](03-Working-with-Geometries.md#areas).
Finally, there is a type for changesets, which contains information about
edits in the OSM database. It can only appear in special changeset files
and explained in more detail [below](#changeset).

The FileProcessor may return any of these objects, when iterating over a file.
Therefore, a script will usually first need to determine the type of object
received. There are a couple of ways to do this.

#### Using `is_*()` convenience functions

All object types, except changesets, implement a set of
`is_node`/`is_way`/`is_relation`/`is_area` functions, which give a nicely
readable way of testing for a specific object type.

!!! example
    === "Code"
    ```python
    for o in osmium.FileProcessor('buildings.opl'):
        if o.is_relation():
            print('Found a relation.')
    ```
    === "Output"
    ```
    Found a relation.
    ```

#### Using the type identifier

The `type_str()` function returns the type of the object as a single
lower case character. The supported types are:

| Character | Type      |
|-----------|-----------|
| __n__     | node      |
| __w__     | way       |
| __r__     | relation  |
| __a__     | area      |
| __c__     | changeset |

This type string can be useful for printing or when saving data by
type. It can also be used to test for a specific type. It is particularly
useful when testing for multiple types:

!!! example
    === "Code"
    ```python
    for o in osmium.FileProcessor('../data/buildings.opl'):
        if o.type_str() in 'wr':
            print('Found a way or relation.')
    ```
    === "Output"
    ```
    Found a way or relation.
    Found a way or relation.
    Found a way or relation.
    ```

#### Testing for object type

Each OSM object type has a [corresponding Python class](../reference/Dataclasses.md).
You can simply test for this object type:

!!! example
    ```python
    for o in osmium.FileProcessor('buildings.opl'):
        if isinstance(o, osmium.osm.Relation):
            print('Found a relation.')
    ```


## Reading object tags

Every object has a list of properties, the tags. They can be accessed through
the `tags` property, which provides a simple dictionary-like view of the tags.
You can use the bracket notation to access a specific tag or use the more
explicit `get()` function. Just like for Python dictionaries, an access by
bracket raises a `ValueError` when the key you are looking for does not exist,
while the `get()` function returns the selected default value.

The `in` operation can be used to check for existence of a key:

!!! example
    ```python
    for o in osmium.FileProcessor('buildings.opl'):
        # When using the bracket notation, make sure the tag exists.
        if 'entrance' in o.tags:
            print('entrace =', o.tags['entrance'])

        # The get() function never throws.
        print('building =', o.tags.get('building', '<unset>')
    ```

Tags can also be iterated over. The iterator returns [Tag][osmium.osm.Tag]
objects. These each hold a key (`k`) and a value (`v`) string. A tag is
itself a Python iterable, so that you can easily iterate through keys and
values like this:

!!! example
    ```python
    from collections import Counter

    stats = Counter()

    for o in osmium.FileProcessor('buildings.opl'):
        for k, v in o.tags:
            stats.update([(k, v)])

    print("Most common tags:", stats.most_common(3))
    ```

As with all data in OSM objects, the tags property is only a view on tags
of the object. If you want to save the tag list for later use, you must make
a copy of the list. The most simple way to do this, is to convert the tag
list into a Python dictionary:

!!! example
    ```python
    saved_tags = []

    for o in osmium.FileProcessor('../data/buildings.opl'):
        if o.tags:
            saved_tags.append(dict(o.tags))

    print("Saved tags:", saved_tags)
    ```


## Other common meta information

Next to the tags, every OSM object also carries some meta information
describing its ID, version and information regarding the editor.

## Properties of OSM object types

### Nodes

The main property of a [Node][osmium.osm.Node] is the _location_,
a coordinate in WGS84 projection.
Latitude and longitude of the node can be accessed either through the
`location` property or through the `lat` and `lon` shortcuts:

!!! example
    ```python
    for o in osmium.FileProcessor('../data/buildings.opl', osmium.osm.NODE):
        assert (o.location.lon, o.location.lat) == (o.lon, o.lat)
    ```

OpenStreetMap, and by extension pyosmium, saves latitude and longitude
internally as a 7-digit fixed-point number. You can access the coordinates
as fixed-point integers through the `x` and `y` properties. There may be rare
use cases, where using this fixed-point notation is faster and more precise.

The coordinates returned by the `lat`/`lon` accessors are guaranteed to be
valid. That means that a value is set and is between -180 and 180 degrees
for longitude and -90 and 90 degrees for latitude. If the file contains
an invalid coordinate, then pyosmium will throw a `ValueError`. To access
the raw unchecked coordinates, use the
functions `location.lat_without_check()` and `location.lon_without_check()`.

### Ways

A [Way][osmium.osm.Way] is essentially an ordered sequence of nodes. This
sequence can be accessed through the `nodes` property. An OSM way only
stores the ID of each node. This can be rather inconvenient when you want
to work with the geometry of the way, because the coordinates of each
node need to be looked up. pyosmium therefore exposes a list of
[NodeRefs][osmium.osm.NodeRef] with the nodes property. Each element in this
list contains the node ID and optionally the location of the node. The
next chapter [Working with Geometries](03-Working-with-Geometries.md)
explains in detail, how pyosmium can help to fill the location of the node.

### Relations

A [Relation][osmium.osm.Relation] is also an ordered sequence. Each sequence
element can reference an arbitrary OSM object. In addition, each of the
members can be assigned a _role_, an arbitrary string that describes the
function of the member. The OSM data model does not specify what the function
of a member is and which roles are defined. You need to know what kind
of relation you are dealing with in order to understand what the members
are suppose to represent. Over the years, the OSM community has established
a convention that every relation comes with a `type` tag, which defines
the basic kind of the relation. For each type you can refer to the
Wiki documentation to learn about the meaning of members and roles.
The most important types currently in use are:

* [multipolygon](https://wiki.openstreetmap.org/wiki/Relation:multipolygon)
  describes an area geometry. Pyosmium natively supports creating geometries
  from this type of relation. See
  [Working with Geometries](03-Working-with-Geometries.md) for more information.
* [boundary](https://wiki.openstreetmap.org/wiki/Relation:boundary) 
  is a special form of the multipolygon type. It is used specifically for
  the various forms of boundaries and define some special roles
  for associated node objects.
* [route](https://wiki.openstreetmap.org/wiki/Relation:route) is for
  collections of ways that make up marked routes for hiking, cycling
  and other forms of transport.
* [public_transport](https://wiki.openstreetmap.org/wiki/Relation:public_transport)
  are a special form of the route relation made for routes of public transport
  vehicles (trains, buses, trams etc). They add some special member roles
  for the stops of the vehicles.
* [restriction](https://wiki.openstreetmap.org/wiki/Relation%3Arestriction)
  is for street-level routing and describes turn restrictions for vehicles.
* [associatedStreet](https://wiki.openstreetmap.org/wiki/Relation:associatedStreet)
  relation types are used in some parts of the world to create a connection
  between address points and the street they belong to.

The members of a relation can be accessed through the `members` property.
This is a simple list of [RelationMember][osmium.osm.RelationMember] objects.
They expose the OSM type of the member, its ID and a role string. When no
role has been set, the `role` property returns an empty string. Here is an
example of a simple iteration over all members:

!!! example
    ```python
    for o in osmium.FileProcessor('buildings.opl', osmium.osm.RELATION):
        for member in o.members:
            print(f"Type: {member.type}  ID: {member.ref}  Role: {member.role}")
    ```


The member property provides only a temporary read-only view of the members.
If you want to save the list for later processing, you need to make an explicit
copy like this:

!!! example
    ```python
    memberlist = {}

    for o in osmium.FileProcessor('buildings.opl', osmium.osm.RELATION):
        memberlist[o.id] = [(m.type, m.ref, m.role) for m in o.members]

    print(memberlist)
    ```


Always keep in mind that relations can become very large. Some have thousands
of members. Therefore consider very carefully which members you are actually
interested when saving members and only keep those that are actually needed later.

### Changeset

The [Changeset][osmium.osm.Changeset] type is the odd one out among the
OSM data types. It does not contain actual map data. Instead it is use
to save meta information about the edits made to the OSM database. You
normally don't find Changeset objects in a datafile. Changeset information
is published in separate files.
