``osm`` - Basic Datatypes
-------------------------

The ``osm`` submodule contains definition of the basic data types used
throughout the library.

OSM Objects
^^^^^^^^^^^

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


