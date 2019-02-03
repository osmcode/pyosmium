import datetime

import typing

from osmium.osm import mutable
from osmium.replication.utils import Timestamp

OSMObjectIdType = typing.NewType('OSMObjectId', int)
UnsginedOSMObjectIdType = typing.NewType('UnsginedOSMObjectIdType', OSMObjectIdType)
UidType = typing.NewType('UserId', int)
VersionType = typing.NewType('VersionType', int)


class OSMObject:
    id: OSMObjectIdType
    deleted: bool
    visible: bool
    version: VersionType
    changeset: ChangesetId
    uid: UidType
    timestamp: Timestamp
    user: str
    tags: TagList

    def positive_id(self) -> UnsginedOSMObjectIdType: ...

    def user_is_anonymous(self) -> bool: ...


class NodeRefList:
    def __len__(self) -> int: ...

    def __getitem__(self, arg2: int) -> NodeRef: ...

    def __iter__(self) -> typing.Iterable[NodeRef]: ...

    def ends_have_same_id(self) -> bool: ...

    def ends_have_same_location(self) -> bool: ...

    def is_closed(self) -> bool: ...


class InnerRing(NodeRefList): ...


InnerRingIterator = typing.Iterable[InnerRing]


class OuterRing(NodeRefList): ...


OuterRingIterator = typing.Iterable[OuterRing]


class Area(OSMObject):
    def from_way(self) -> bool: ...

    def orig_id(self) -> OSMObjectIdType: ...

    def is_multipolygon(self) -> bool: ...

    def num_rings(self) -> typing.Tuple[int, int]: ...

    def outer_rings(self) -> OuterRingIterator: ...

    def inner_rings(self) -> InnerRingIterator: ...


class Box:
    bottom_left: Location
    top_right: Location

    @typing.overload
    def __init__(self): ...

    @typing.overload
    def __init__(self, arg2: float, arg3: float, arg4: float, arg5: float): ...

    @typing.overload
    def __init__(self, arg2: Location, arg3: Location): ...

    def contains(self, location: Location) -> bool: ...

    @typing.overload
    def extend(self, arg2: Location) -> Box: ...

    @typing.overload
    def extend(self, arg2: Box) -> Box: ...

    def size(self) -> float: ...

    def valid(self) -> bool: ...


ChangesetId = typing.NewType('ChangesetId', int)


class Changeset:
    id: ChangesetId
    uid: UidType
    created_at: datetime.datetime  # ???
    closed_at: datetime.datetime  # ???
    open: bool
    num_changes: int
    bounds: Box
    user: str
    tags: TagList

    def user_is_anonymous(self) -> bool: ...


class Location:
    lat: float
    lon: float
    x: float
    y: float

    def __init__(self, arg2: float, arg3: float): ...  # x, y ?

    def lat_without_check(self) -> float: ...

    def lon_without_check(self) -> float: ...

    def valid(self) -> bool: ...


class Node(OSMObject):
    location: Location

    def replace(self) -> mutable.Node: ...


class NodeRef:
    ref: OSMObjectIdType
    location: Location
    lat: float
    lon: float
    x: float
    y: float


class Relation(OSMObject):
    members: RelationMemberList

    def replace(self) -> mutable.Relation: ...


class RelationMember:
    ref: OSMObjectIdType
    type: str
    role: str


class RelationMemberList:
    def __len__(self) -> int: ...

    def __iter__(self) -> typing.Iterable[RelationMember]: ...


class Tag:
    k: str
    v: str


class TagList:
    def __len__(self) -> int: ...

    def __getitem__(self, arg2: str) -> str: ...

    def __contains__(self, arg2: str) -> bool: ...

    def __iter__(self) -> typing.Iterable[Tag]: ...  # ???

    @typing.overload
    def get(self, arg2) -> str: ...

    @typing.overload
    def get(self, key: str, default: str) -> str: ...


class Way(OSMObject):
    nodes: WayNodeList

    def ends_have_same_id(self) -> bool: ...

    def ends_have_same_location(self) -> bool: ...

    def is_closed(self) -> bool: ...

    def replace(self) -> mutable.Way: ...


class WayNodeList(NodeRefList): ...


class osm_entity_bits:
    ALL: osm_entity_bits = ...
    AREA: osm_entity_bits = ...
    CHANGESET: osm_entity_bits = ...
    NODE: osm_entity_bits = ...
    NOTHING: osm_entity_bits = ...
    OBJECT: osm_entity_bits = ...
    RELATION: osm_entity_bits = ...
    WAY: osm_entity_bits = ...
    names: typing.Dict[str, osm_entity_bits] = ...
    values: typing.Dict[int, osm_entity_bits] = ...
