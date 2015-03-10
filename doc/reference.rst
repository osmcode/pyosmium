Pyosmium Reference
==================

Pyosmium is a thin wrapper to the osmium library. Where possible it follows
its structure and naming scheme. This reference provides a short description
of the exported classes and interfaces. More details and background
information can be found in the osmium manual.

``osm`` - Basic Datatypes
-----------------------

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

OSM Entity Attributes
^^^^^^^^^^^^^^^^^^^^^

Some of the attributes of the OSM entities are represented with more
complex classes.

.. autoclass:: osmium.osm.Changeset
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.Location
    :members:
    :undoc-members:

.. autoclass:: osmium.osm.NodeRef
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

.. autoclass:: osmium.osm.Timestamp
    :members:
    :undoc-members:

