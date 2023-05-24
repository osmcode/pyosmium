``osm`` - Basic Datatypes
-------------------------

The ``osm`` submodule contains definitions of the basic data types used
throughout the library.

Native OSM Objects
^^^^^^^^^^^^^^^^^^

Native OSM object classes are lightwight wrappers around the npyosmium OSM
data classes. They are immutable and generally bound to the lifetime of
the buffer they are saved in.

There are five classes representing the basic OSM entities.

.. autoclass:: npyosmium.osm.OSMObject
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Node
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Way
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Relation
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Area
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Changeset
    :members:
    :undoc-members:

.. _mutable-objects:

Mutable OSM Objects
^^^^^^^^^^^^^^^^^^^

The objects in ``npyosmium.osm.mutable`` are Python versions of the native OSM
objects that can be modified. You can use these classes as a base class for
your own objects or to modify objects read from a file.

.. autoclass:: npyosmium.osm.mutable.OSMObject
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.mutable.Node
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.mutable.Way
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.mutable.Relation
    :members:
    :undoc-members:


Node Reference Lists
^^^^^^^^^^^^^^^^^^^^

Line geometries in OSM are simply a sequence of nodes. To simplify processing
npyosmium returns such node sequences using a special datatype that contains a
reference to the node id and also the location geometry. The latter is only
valid if the node locations have been cached by a location handler.

.. autoclass:: npyosmium.osm.NodeRef
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.NodeRefList
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.WayNodeList
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.OuterRing
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.InnerRing
    :members:
    :undoc-members:


Relation member lists
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: npyosmium.osm.RelationMember
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.RelationMemberList
    :members:
    :undoc-members:

Tag lists
^^^^^^^^^

.. autoclass:: npyosmium.osm.Tag
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.TagList
    :members:
    :undoc-members:


Geometry Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: npyosmium.osm.Box
    :members:
    :undoc-members:

.. autoclass:: npyosmium.osm.Location
    :members:
    :undoc-members:

