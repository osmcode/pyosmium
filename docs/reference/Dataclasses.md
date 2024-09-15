# OSM data views

These classes expose the data from an OSM file to the Python scripts.
Objects of these classes are always _views_ unless stated otherwise.
This means that they are only valid as long as the view to an object is
valid.

## OSM types

::: osmium.osm.osm_entity_bits

## OSM primary objects

::: osmium.osm.OSMObject
    options:
        show_bases: False
::: osmium.osm.Node
::: osmium.osm.Way
::: osmium.osm.Relation
::: osmium.osm.Area
::: osmium.osm.Changeset

## Tag lists

::: osmium.osm.Tag
::: osmium.osm.TagList

## Node lists

::: osmium.osm.NodeRef
::: osmium.osm.NodeRefList
::: osmium.osm.WayNodeList
::: osmium.osm.InnerRing
::: osmium.osm.OuterRing

## Relation members

::: osmium.osm.RelationMember
::: osmium.osm.RelationMemberList

## Geometry types

::: osmium.osm.Box
::: osmium.osm.Location
