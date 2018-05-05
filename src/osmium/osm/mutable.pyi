import typing
from typing import Any, Optional

from . import OSMObjectIdType, VersionType, ChangesetId, UidType, TagList
from ..replication.utils import Timestamp
from .. import osm

LocationType = typing.Union[osm.Location, typing.Tuple[float, float]]
NodeListType = typing.Union[osm.WayNodeList, typing.List[osm.NodeRef], typing.List[int]]
RelationMembersType = typing.Union[
    osm.RelationMemberList,
    typing.List[osm.RelationMember],
    typing.List[typing.Tuple[str, int, str]]
]


class OSMObject:
    id: OSMObjectIdType
    version: VersionType
    visible: bool
    changeset: ChangesetId
    timestamp: Timestamp
    uid: UidType
    tags: typing.Union[TagList, typing.Dict]

    def __init__(self,
                 base: Optional[Any] = ...,
                 id: Optional[OSMObjectIdType] = ...,
                 version: Optional[VersionType] = ...,
                 visible: Optional[bool] = ...,
                 changeset: Optional[ChangesetId] = ...,
                 timestamp: Optional[Timestamp] = ...,
                 uid: Optional[UidType] = ...,
                 tags: Optional[typing.Union[TagList, typing.Dict]] = ...) -> None: ...


class Node(OSMObject):
    location: LocationType

    def __init__(self, base: Optional[osm.Node], location: Optional[LocationType], **attrs: Any) -> None: ...


class Way(OSMObject):
    nodes: NodeListType = ...

    def __init__(self, base: Optional[osm.Way] = ..., nodes: Optional[NodeListType] = ..., **attrs: Any) -> None: ...


class Relation(OSMObject):
    members: RelationMembersType = ...

    def __init__(self, base: Optional[osm.Relation] = ..., members: Optional[RelationMembersType] = ...,
                 **attrs: Any) -> None: ...
