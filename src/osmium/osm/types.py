# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Sequence, Any, NamedTuple, Callable, Optional, Iterator, \
                   Iterable, TYPE_CHECKING, TypeVar, Generic, Tuple, Union
import datetime as dt

import osmium.osm.mutable


if TYPE_CHECKING:
    import osmium.osm._osm as cosm

T_obj = TypeVar('T_obj', 'cosm.COSMNode', 'cosm.COSMWay', 'cosm.COSMRelation', 'cosm.COSMArea')

def _make_repr(name: str, *attrs: str) -> Callable[[Any], str]:
    fmt_string = f'osmium.osm.{name}('\
                 + ', '.join([f'{x}={{0.{x}!r}}' for x in attrs])\
                 + ')'

    def _repr(self: Any) -> str:
        if self._pyosmium_data.is_valid():
            return fmt_string.format(self)

        return f'osmium.osm.{name}(<invalid>)'

    return _repr


def _list_elipse(obj: Iterable[Any]) -> str:
    objects = ','.join(map(str, obj))
    if len(objects) > 50:
        objects = objects[:47] + '...'
    return objects


class Tag(NamedTuple):
    """ A single OSM tag.
    """

    k: str
    "Tag key"

    v: str
    "Tag value"

    def __str__(self) -> str:
        return f"{self.k}={self.v}"


class TagIterator:

    def __init__(self, parent: 'cosm.TagContainerProtocol') -> None:
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.tags_begin()

    def __iter__(self) -> 'TagIterator':
        return self

    def __next__(self) -> Tag:
        return self._pyosmium_data.tags_next(self.iterator)


class TagList(Iterable[Tag]):
    """ A fixed list of tags. The list is exported as an unmutable,
        dictionary-like object where the keys are tag strings and the
        items are [Tags][osmium.osm.Tag].
    """

    def __init__(self, parent: 'cosm.TagContainerProtocol') -> None:
        self._pyosmium_data = parent

    def __len__(self) -> int:
        return self._pyosmium_data.tags_size()

    def __getitem__(self, key: str) -> str:
        if key is None:
            raise KeyError("Key 'None' not allowed.")

        val = self._pyosmium_data.tags_get_value_by_key(key, None)
        if val is None:
            raise KeyError("No tag with that key.")

        return val

    def __contains__(self, key: str) -> bool:
        return key is not None and self._pyosmium_data.tags_has_key(key)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """ Return the value for the given key. or 'value' if the key
            does not exist in the list.
        """
        if key is None:
            return default

        return self._pyosmium_data.tags_get_value_by_key(key, default)

    def __iter__(self) -> TagIterator:
        return TagIterator(self._pyosmium_data)

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f"{{{_list_elipse(self)}}}"

        return '<taglist invalid>'

    def __repr__(self) -> str:
        if self._pyosmium_data.is_valid():
            tagstr = ', '.join([f"{i.k!r}: {i.v!r}" for i in self])
        else:
            tagstr = '<invalid>'

        return f"osmium.osm.TagList({{{tagstr}}})"


class NodeRef:
    """ A reference to a OSM node that also caches the nodes location.
    """

    def __init__(self, location: 'osmium.osm.Location', ref: int) -> None:
        self.location = location
        self.ref = ref

    @property
    def x(self) -> int:
        """ (read-only) X coordinate (longitude) as a fixed-point integer.
        """
        return self.location.x

    @property
    def y(self) -> int:
        """ (read-only) Y coordinate (latitude) as a fixed-point integer.
        """
        return self.location.y

    @property
    def lat(self) -> float:
        """ (read-only) Latitude (y coordinate) as floating point number.
        """
        return self.location.lat

    @property
    def lon(self) -> float:
        """ (read-only) Longitude (x coordinate) as floating point number.
        """
        return self.location.lon

    def __str__(self) -> str:
        if self.location.valid():
            return f"{self.ref:d}@{self.location!s}"

        return str(self.ref)

    def __repr__(self) -> str:
        return f"osmium.osm.NodeRef(ref={self.ref!r}, location={self.location!r})"


class NodeRefList:
    """ A list of node references, implemented as
        an immutable sequence of [osmium.osm.NodeRef][]. This class
        is normally not used directly, use one of its subclasses instead.
    """

    def __init__(self, parent: 'cosm.BufferProxyProtocol', ref_list: 'cosm.NodeRefList') -> None:
        self._pyosmium_data = parent
        self._list = ref_list

    def is_closed(self) -> bool:
        """ True if the start and end node are the same (synonym for
            ``ends_have_same_id``).
        """
        return self._list.is_closed(self._pyosmium_data)

    def ends_have_same_id(self) -> bool:
        """ True if the start and end node are exactly the same.
        """
        return self._list.is_closed(self._pyosmium_data)

    def ends_have_same_location(self) -> bool:
        """ True if the start and end node of the way are at the same location. "
            Expects that the coordinates of the way nodes have been loaded
            ([SimpleHandler apply functions][osmium.SimpleHandler] and
            [`FileProcessor.with_locations()`][osmium.FileProcessor.with_locations]).
            If the locations are not present then the function returns always true.
        """
        return self._list.ends_have_same_location(self._pyosmium_data)

    def __len__(self) -> int:
        return self._list.size(self._pyosmium_data)

    def __getitem__(self, idx: int) -> NodeRef:
        return self._list.get(self._pyosmium_data, idx)

    def __iter__(self) -> Iterator[NodeRef]:
        return (self[i] for i in range(len(self)))

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f'[{_list_elipse(self)}]'

        return '<node list invalid>'

    def __repr__(self) -> str:
        if self._pyosmium_data.is_valid():
            nodes = ', '.join(map(repr, self))
        else:
            nodes = '<invalid>'

        return 'osmium.osm.{}([{}])'.format(self.__class__.__name__, nodes)


class WayNodeList(NodeRefList):
    """ List of nodes in a way.
        For its members see [`osmium.osm.NodeRefList`][].
    """


class OuterRing(NodeRefList):
    """List of nodes in an outer ring.
       For its members see [`osmium.osm.NodeRefList`][].
    """

class InnerRing(NodeRefList):
    """ List of nodes in an inner ring. "
        For its members see [`osmium.osm.NodeRefList`][].
    """

class RelationMember:
    """ Single member of a relation.
    """
    ref : int
    "OSM ID of the object. Only unique within the type."
    type: str
    "Type of object referenced, a node, way or relation."
    role: str
    """ The role of the member within the relation, a free-text string.
        If no role is set then the string is empty.
    """

    def __init__(self, ref: int, mtype: str, role: str):
        self.ref = ref
        self.type = mtype
        self.role = role

    def __str__(self) -> str:
        if self.role:
            return f"{self.type}{self.ref:d}@{self.role}"

        return f"{self.type}{self.ref:d}"

    def __repr__(self) -> str:
        return f"osmium.osm.RelationMember(ref={self.ref!r}, type={self.type!r}, role={self.role!r})"


class MemberIterator:
    """ Iterator over a sequence of RelationMembers.
    """

    def __init__(self, parent: 'cosm.COSMRelation') -> None:
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.members_begin()

    def __iter__(self) -> 'MemberIterator':
        return self

    def __next__(self) -> RelationMember:
        return self._pyosmium_data.members_next(self.iterator)


class RelationMemberList:
    """ An immutable  sequence of relation members
        [`osmium.osm.RelationMember`][].
    """

    def __init__(self, parent: 'cosm.COSMRelation') -> None:
        self._pyosmium_data = parent

    def __len__(self) -> int:
        return self._pyosmium_data.members_size()

    def __iter__(self) -> MemberIterator:
        return MemberIterator(self._pyosmium_data)

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f'[{_list_elipse(self)}]'

        return '<member list invalid>'

    def __repr__(self) -> str:
        if self._pyosmium_data.is_valid():
            members = ', '.join(map(repr, self))
        else:
            members = '<invalid>'

        return f'osmium.osm.RelationMemberList([{members}])'


class OSMObject(Generic[T_obj]):
    """ This is the base class for all OSM entity classes below and contains
        all common attributes.
    """
    _pyosmium_data: T_obj
    _tags: TagList

    @property
    def id(self) -> int:
        """ (read-only) OSM id of the object.
        """
        return self._pyosmium_data.id()

    @property
    def deleted(self) -> bool:
        """ (read-only) True if the object is no longer visible.
        """
        return self._pyosmium_data.deleted()

    @property
    def visible(self) -> bool:
        """ (read-only) True if the object is visible.
        """
        return self._pyosmium_data.visible()

    @property
    def version(self) -> int:
        """ (read-only) Version number of the object.
        """
        return self._pyosmium_data.version()

    @property
    def changeset(self) -> int:
        """ (read-only) Id of changeset where this version of the object was created.
        """
        return self._pyosmium_data.changeset()

    @property
    def uid(self) -> int:
        """ (read-only) Id of the user that created this version
            of the object. Only this ID uniquely identifies users.
        """
        return self._pyosmium_data.uid()

    @property
    def timestamp(self) -> dt.datetime:
        """ (read-only) Date when this version has been created,
            returned as a ``datetime.datetime``.
        """
        return self._pyosmium_data.timestamp()

    @property
    def user(self) -> str:
        """ (read-only) Name of the user that created this version.
            Be aware that user names can change, so that the same
            user ID may appear with different names and vice versa.
        """
        return self._pyosmium_data.user()

    @property
    def tags(self) -> TagList:
        """ (read-only) List of tags describing the object.
            See [`osmium.osm.TagList`][].
        """
        return self._tags

    def positive_id(self) -> int:
        """ Get the absolute value of the id of this object.
        """
        return self._pyosmium_data.positive_id()

    def user_is_anonymous(self) -> bool:
        """ Check if the user is anonymous. If true, the uid does not uniquely
            identify a single user but only the group of all anonymous users
            in general.
        """
        return self._pyosmium_data.user_is_anonymous()

    def type_str(self) -> str:
        """ Return a single character identifying the type of the object.
            The character is the same as used in OPL.
        """
        return 'o'

    def is_node(self) -> bool:
        """ Return true if the object is a Node object.
        """
        return isinstance(self, Node)

    def is_way(self) -> bool:
        """ Return true if the object is a Way object.
        """
        return isinstance(self, Way)

    def is_relation(self) -> bool:
        """ Return true if the object is a Relation object.
        """
        return isinstance(self, Relation)

    def is_area(self) -> bool:
        """ Return true if the object is a Way object.
        """
        return isinstance(self, Area)


class Node(OSMObject['cosm.COSMNode']):
    """ Represents a single OSM node. It inherits all properties from OSMObjects
        and adds a single extra attribute: the location.
    """

    def __init__(self, cnode: 'cosm.COSMNode'):
        self._pyosmium_data = cnode
        self._location: Optional['osmium.osm.Location'] = None
        self._tags = TagList(self._pyosmium_data)

    def replace(self, **kwargs: Any) -> 'osmium.osm.mutable.Node':
        """ Create a mutable node replacing the properties given in the
            named parameters. The properties may be any of the properties
            of OSMObject or Node.

            Note that this function only creates a shallow copy per default.
            It is still bound to the scope of the original object.
            To create a full copy use:
            ``node.replace(tags=dict(node.tags))``
        """
        return osmium.osm.mutable.Node(self, **kwargs)

    @property
    def location(self) -> 'osmium.osm.Location':
        """ The geographic coordinates of the node.
            See [`osmium.osm.Location`][].
        """
        if self._location is None:
            self._location = self._pyosmium_data.location()

        return self._location

    @property
    def lat(self) -> float:
        """ Return latitude of the node.
        """
        return self.location.lat


    @property
    def lon(self) -> float:
        """ Return longitude of the node.
        """
        return self.location.lon

    def type_str(self) -> str:
        return 'n'

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f'n{self.id:d}: location={self.location!s} tags={self.tags!s}'

        return '<node invalid>'


    __repr__ = _make_repr('Node', 'id', 'deleted', 'visible', 'version',
                          'changeset', 'uid', 'timestamp', 'user',
                          'tags', 'location')


class Way(OSMObject['cosm.COSMWay']):
    """ Represents an OSM way. It inherits the attributes from OSMObject and
        adds an ordered list of nodes that describes the way.
    """

    def __init__(self, cway: 'cosm.COSMWay'):
        self._pyosmium_data = cway
        self._tags = TagList(self._pyosmium_data)
        self._nodes: Optional[WayNodeList] = None

    def replace(self, **kwargs: Any) -> 'osmium.osm.mutable.Way':
        """ Create a mutable way replacing the properties given in the
            named parameters. The properties may be any of the properties
            of OSMObject or Way.

            Note that this function only creates a shallow copy per default.
            It is still bound to the scope of the original object.
            To create a full copy use:
            ``way.replace(tags=dict(way.tags), nodes=list(way.nodes))``
        """
        return osmium.osm.mutable.Way(self, **kwargs)

    @property
    def nodes(self) -> WayNodeList:
        """ (read-only) Ordered list of nodes.
            See [`osmium.osm.WayNodeList`][].
        """
        if self._nodes is None:
            self._nodes = WayNodeList(self._pyosmium_data, self._pyosmium_data.nodes())

        return self._nodes

    def is_closed(self) -> bool:
        """ True if the start and end node are the same (synonym for
            ``ends_have_same_id``).
        """
        return self._pyosmium_data.is_closed()

    def ends_have_same_id(self) -> bool:
        """ True if the start and end node are exactly the same.
        """
        return self._pyosmium_data.is_closed()

    def ends_have_same_location(self) -> bool:
        """ True if the start and end node of the way are at the same location.
            Expects that the coordinates of the way nodes have been loaded
            (see [SimpleHandler apply functions][osmium.SimpleHandler] and
            [`FileProcessor.with_locations()`][osmium.FileProcessor.with_locations])
            If the locations are not present then the function returns always true.
        """
        return self._pyosmium_data.ends_have_same_location()

    def type_str(self) -> str:
        return 'w'

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f'w{self.id:d}: nodes={self.nodes!s} tags={self.tags!s}'

        return '<way invalid>'

    __repr__ = _make_repr('Way', 'id', 'deleted', 'visible', 'version', 'changeset',
                          'uid', 'timestamp', 'user', 'tags', 'nodes')


class Relation(OSMObject['cosm.COSMRelation']):
    """ Represents a OSM relation. It inherits the attributes from OSMObject
        and adds an ordered list of members.
    """
    _members: RelationMemberList

    def __init__(self, crelation: 'cosm.COSMRelation'):
        self._pyosmium_data = crelation
        self._tags = TagList(self._pyosmium_data)
        self._members = RelationMemberList(self._pyosmium_data)

    def replace(self, **kwargs: Any) -> 'osmium.osm.mutable.Relation':
        """ Create a mutable relation replacing the properties given in the
            named parameters. The properties may be any of the properties
            of OSMObject or Relation.

            Note that this function only creates a shallow copy per default.
            It is still bound to the scope of the original object.
            To create a full copy use:
            ``rel.replace(tags=dict(rel.tags), members=list(rel.members))``
        """
        return osmium.osm.mutable.Relation(self, **kwargs)

    @property
    def members(self) -> RelationMemberList:
        """(read-only) Ordered list of relation members.
           See [`osmium.osm.RelationMemberList`][].
        """
        return self._members

    def type_str(self) -> str:
        return 'r'

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f"r{self.id:d}: members={self.members!s}, tags={self.tags!s}"

        return f"<relation invalid>"

    __repr__ = _make_repr('Relation', 'id', 'deleted', 'visible', 'version',
                                      'changeset', 'uid', 'timestamp', 'user',
                                      'tags', 'members')


class OuterRingIterator:
    """ Iterator over outer rings of an area.
    """

    def __init__(self, parent: Any) -> None:
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.outer_begin()

    def __iter__(self) -> 'OuterRingIterator':
        return self

    def __next__(self) -> OuterRing:
        return OuterRing(self._pyosmium_data, self._pyosmium_data.outer_next(self.iterator))


class InnerRingIterator:
    """ Iterator over the inner rings of an outer ring.
    """

    def __init__(self, parent: Any, oring: OuterRing) -> None:
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.inner_begin(oring._list)

    def __iter__(self) -> 'InnerRingIterator':
        return self

    def __next__(self) -> InnerRing:
        return InnerRing(self._pyosmium_data, self._pyosmium_data.inner_next(self.iterator))


class Area(OSMObject['cosm.COSMArea']):
    """ Areas are a special kind of meta-object representing a polygon.
        They can either be derived from closed ways or from relations
        that represent multipolygons. They also inherit the attributes
        of OSMObjects and in addition contain polygon geometries. Areas have
        their own unique id space. This is computed as the OSM id times 2
        and for relations 1 is added.
    """

    def __init__(self, carea: 'cosm.COSMArea') -> None:
        self._pyosmium_data = carea
        self._tags = TagList(self._pyosmium_data)

    def from_way(self) -> bool:
        """ Return true if the area was created from a way, false if it was
            created from a relation of multipolygon type.
        """
        return self._pyosmium_data.from_way()

    def orig_id(self) -> int:
        """ Compute the original OSM id of this object. Note that this is not
            necessarily unique because the object might be a way or relation
            which have an overlapping id space.
        """
        return self._pyosmium_data.orig_id()

    def is_multipolygon(self) -> bool:
        """ Return true if this area is a true multipolygon, i.e. it consists
            of multiple outer rings.
        """
        return self._pyosmium_data.is_multipolygon()

    def num_rings(self) -> Tuple[int,int]:
        """ Return a tuple with the number of outer rings and inner rings.

            This function goes through all rings to count them.
        """
        return self._pyosmium_data.num_rings()

    def outer_rings(self) -> OuterRingIterator:
        """ Return an iterator over all outer rings of the multipolygon.
        """
        return OuterRingIterator(self._pyosmium_data)

    def inner_rings(self, oring: OuterRing) -> InnerRingIterator:
        """ Return an iterator over all inner rings of the multipolygon.
        """
        return InnerRingIterator(self._pyosmium_data, oring)

    def type_str(self) -> str:
        return 'a'

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f"a{self.id:d}: num_rings={self.num_rings()}, tags={self.tags!s}"

        return f"<area invalid>"

    __repr__ = _make_repr('Area', 'id', 'deleted', 'visible', 'version',
                                  'changeset', 'uid', 'timestamp', 'user',
                                  'tags')


class Changeset:
    """ A changeset description.
    """
    _pyosmium_data: 'cosm.COSMChangeset'
    _bounds: Optional['osmium.osm.Box']
    _tags: TagList

    def __init__(self, carea: 'cosm.COSMChangeset') -> None:
        self._pyosmium_data = carea
        self._bounds = None
        self._tags = TagList(self._pyosmium_data)

    @property
    def id(self) -> int:
        """ (read-only) Unique ID of the changeset.
        """
        return self._pyosmium_data.id()

    @property
    def uid(self) -> int:
        """ (read-only) User ID of the changeset creator.
        """
        return self._pyosmium_data.uid()

    @property
    def created_at(self) -> dt.datetime:
        """ (read-only) Timestamp when the changeset was first opened.
        """
        return self._pyosmium_data.created_at()

    @property
    def closed_at(self) -> dt.datetime:
        """ (read-only) Timestamp when the changeset was finalized. May be
            ``None`` when the changeset is still open.
        """
        return self._pyosmium_data.closed_at()

    @property
    def open(self) -> bool:
        """ (read-only) True when the changeset is still open.
        """
        return self._pyosmium_data.open()

    @property
    def num_changes(self) -> int:
        """ (read-only) The total number of objects changed in this Changeset.
        """
        return self._pyosmium_data.num_changes()

    @property
    def user(self) -> str:
        """ (read-only) Name of the user that created the changeset.
            Be aware that user names can change, so that the same
            user ID may appear with different names and vice versa.
        """
        return self._pyosmium_data.user()

    @property
    def bounds(self) -> 'osmium.osm.Box':
        """ (read-only) The bounding box of the area that was edited.
        """
        if self._bounds is None:
            self._bounds = self._pyosmium_data.bounds()

        return self._bounds

    @property
    def tags(self) -> TagList:
        """ (read-only) List of tags describing the object.
            See [`osmium.osm.TagList`][].
        """
        return self._tags

    def user_is_anonymous(self) -> bool:
        """ Check if the user anonymous. If true, the uid does not uniquely
            identify a single user but only the group of all anonymous users
            in general.
        """
        return self._pyosmium_data.user_is_anonymous()

    def type_str(self) -> str:
        return 'c'

    def __str__(self) -> str:
        if self._pyosmium_data.is_valid():
            return f'c{self.id:d}: closed_at={self.closed_at!s}, bounds={self.bounds!s}, tags={self.tags!s}'

        return f"<changeset invalid>"

    __repr__ =  _make_repr('Changeset', 'id', 'uid', 'created_at', 'closed_at',
                                        'open', 'num_changes', 'bounds', 'user',
                                        'tags')


OSMEntity = Union[Node, Way, Relation, Area, Changeset]
