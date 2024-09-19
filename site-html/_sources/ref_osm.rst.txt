``osm`` - Basic Datatypes
-------------------------

The ``osm`` submodule contains definitions of the basic data types used
throughout the library.

Native OSM Objects
^^^^^^^^^^^^^^^^^^

Native OSM object classes are lightwight wrappers around the osmium OSM
data classes. They are immutable and generally bound to the lifetime of
the buffer they are saved in.

There are five classes representing the basic OSM entities.

.. autoclass:: osmium.osm.OSMObject
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Node
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Way
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Relation
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Area
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Changeset
    :members:
    :undoc-members:

.. _mutable-objects:

Mutable OSM Objects
^^^^^^^^^^^^^^^^^^^

The objects in ``osmium.osm.mutable`` are Python versions of the native OSM
objects that can be modified. You can use these classes as a base class for
your own objects or to modify objects read from a file.

.. autoclass:: osmium.osm.mutable.OSMObject
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.mutable.Node
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.mutable.Way
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.mutable.Relation
    :members:
    :undoc-members:


Node Reference Lists
^^^^^^^^^^^^^^^^^^^^

Line geometries in OSM are simply a sequence of nodes. To simplify processing
osmium returns such node sequences using a special datatype that contains a
reference to the node id and also the location geometry. The latter is only
valid if the node locations have been cached by a location handler.

.. autoclass:: osmium.osm.NodeRef
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.NodeRefList
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.WayNodeList
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.OuterRing
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.InnerRing
    :members:
    :undoc-members:

Other OSM Entity Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some of the attributes of the OSM entities are represented with more
complex classes.

.. autoclass:: osmium.osm.Box
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Location
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.RelationMember
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.RelationMemberList
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Tag
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.TagList
    :members:
    :undoc-members:


