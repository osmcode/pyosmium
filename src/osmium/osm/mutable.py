# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Optional, Union, Any, Mapping, Sequence, Tuple, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    import osmium.osm

    OSMObjectLike = Union['OSMObject', osmium.osm.OSMObject[Any]]

    TagSequence = Union[osmium.osm.TagList, Mapping[str, str], Sequence[Tuple[str, str]]]
    LocationLike = Union[osmium.osm.Location, Tuple[float, float]]
    NodeSequence = Union[osmium.osm.NodeRefList, Sequence[Union[osmium.osm.NodeRef, int]]]
    MemberSequence = Union[osmium.osm.RelationMemberList,
                       Sequence[Union[osmium.osm.RelationMember, Tuple[str, int, str]]]]

class OSMObject:
    """Mutable version of ``osmium.osm.OSMObject``. It exposes the following
       attributes ``id``, ``version``, ``visible``, ``changeset``, ``timestamp``,
       ``uid`` and ``tags``. Timestamps may be strings or datetime objects.
       Tags can be an osmium.osm.TagList, a dict-like object
       or a list of tuples, where each tuple contains a (key value) string pair.

       If the ``base`` parameter is given in the constructor, then the object
       will be initialised first from the attributes of this base object.
    """

    def __init__(self, base: Optional['OSMObjectLike'] = None,
                 id: Optional[int] = None, version: Optional[int] = None,
                 visible: Optional[bool] = None, changeset: Optional[int] = None,
                 timestamp: Optional[datetime] = None, uid: Optional[int] = None,
                 tags: Optional['TagSequence'] = None, user: Optional[str] = None) -> None:
        if base is None:
            self.id = id
            self.version = version
            self.visible = visible
            self.changeset = changeset
            self.timestamp = timestamp
            self.uid = uid
            self.tags = tags
            self.user = user
        else:
            self.id = base.id if id is None else id
            self.version = base.version if version is None else version
            self.visible = base.visible if visible is None else visible
            self.changeset = base.changeset if changeset is None else changeset
            self.timestamp = base.timestamp if timestamp is None else timestamp
            self.uid = base.uid if uid is None else uid
            self.tags = base.tags if tags is None else tags
            self.user = base.user if user is None else user


class Node(OSMObject):
    """The mutable version of ``osmium.osm.Node``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `location` attribute. This
       may either be an `osmium.osm.Location` or a tuple of lon/lat coordinates.
    """

    def __init__(self, base: Optional[Union['Node', 'osmium.osm.Node']] = None,
                 location: Optional['LocationLike'] = None,
                 **attrs: Any) -> None:
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.location = location
        else:
            self.location = location if location is not None else base.location


class Way(OSMObject):
    """The mutable version of ``osmium.osm.Way``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `nodes` attribute. This may
       either be and ``osmium.osm.NodeList`` or a list consisting of
       ``osmium.osm.NodeRef`` or simple node ids.
    """

    def __init__(self, base: Optional[Union['Way', 'osmium.osm.Way']] = None,
                 nodes: Optional['NodeSequence'] = None, **attrs: Any) -> None:
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.nodes = nodes
        else:
            self.nodes = nodes if nodes is not None else base.nodes

class Relation(OSMObject):
    """The mutable version of ``osmium.osm.Relation``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `members` attribute. This
       may either be an ``osmium.osm.RelationMemberList`` or a list consisting
       of ``osmium.osm.RelationMember`` or tuples of (type, id, role). The
       member type should be a single character 'n', 'w' or 'r'.
    """

    def __init__(self, base: Optional[Union['Relation', 'osmium.osm.Relation']] = None,
                 members: Optional['MemberSequence'] = None, **attrs: Any) -> None:
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.members = members
        else:
            self.members = members if members is not None else base.members


def create_mutable_node(node: Union[Node, 'osmium.osm.Node'], **args: Any) -> Node:
    """ Create a mutable node replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return Node(base=node, **args)

def create_mutable_way(way: Union[Way, 'osmium.osm.Way'], **args: Any) -> Way:
    """ Create a mutable way replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return Way(base=way, **args)

def create_mutable_relation(rel: Union[Relation, 'osmium.osm.Relation'], **args: Any) -> Relation:
    """ Create a mutable relation replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return Relation(base=rel, **args)

