MYPY = False
if MYPY:
    import typing
    from typing import Optional
    from . import TagList
    from ..replication.utils import Timestamp
    from . import Location
    from .. import osm

    OSMObjectIdType = typing.NewType('OSMObjectId', int)
    VersionType = typing.NewType('VersionType', int)
    UnsginedOSMObjectIdType = typing.NewType('UnsginedOSMObjectIdType', OSMObjectIdType)
    UidType = typing.NewType('UserId', int)
    ChangesetId = typing.NewType('ChangesetId', int)
    LocationType = typing.Union[Location, typing.Tuple[float, float]]

    NodeListType = typing.Union[osm.WayNodeList, typing.List[osm.NodeRef], typing.List[int]]
    RelationMembersType = typing.Union[
        osm.RelationMemberList,
        typing.List[osm.RelationMember],
        typing.List[typing.Tuple[str, int, str]]
    ]


class OSMObject(object):
    """Mutable version of ``osmium.osm.OSMObject``. It exposes the following
       attributes ``id``, ``version``, ``visible``, ``changeset``, ``timestamp``,
       ``uid`` and ``tags``. Timestamps may be strings or datetime objects.
       Tags can be an osmium.osm.TagList, a dict-like object
       or a list of tuples, where each tuple contains a (key value) string pair.

       If the ``base`` parameter is given in the constructor, then the object
       will be initialised first from the attributes of this base object.
    """

    def __init__(self, base=None, id=None, version=None, visible=None, changeset=None,
            timestamp=None, uid=None, tags=None):
        # type: (Optional[typing.Any], Optional[OSMObjectIdType], Optional[VersionType], bool, ChangesetId, Timestamp, UidType, typing.Union[TagList, typing.Dict[str, str]]) -> None
        if base is None:
            self.id = id  # type: OSMObjectIdType
            self.version = version  # type: VersionType
            self.visible = visible  # type: bool
            self.changeset = changeset  # type: ChangesetId
            self.timestamp = timestamp  # type: Timestamp
            self.uid = uid  # type: UidType
            self.tags = tags  # typing.Union[TagList, typing.Dict[str, str]]
        else:
            self.id = base.id if id is None else id
            self.version = base.version if version is None else version
            self.visible = base.visible if visible is None else visible
            self.changeset = base.changeset if changeset is None else changeset
            self.timestamp = base.timestamp if timestamp is None else timestamp
            self.uid = base.uid if uid is None else uid
            self.tags = base.tags if tags is None else tags


class Node(OSMObject):
    """The mutable version of ``osmium.osm.Node``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `location` attribute. This
       may either be an `osmium.osm.Location` or a tuple of lon/lat coordinates.
    """

    def __init__(self, base=None, location=None, **attrs):
        # type: (Optional[osm.Node], Optional[LocationType], typing.Any) -> None
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.location = location  # type: LocationType
        else:
            self.location = location if location is not None else base.location


class Way(OSMObject):
    """The mutable version of ``osmium.osm.Way``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `nodes` attribute. This may
       either be and ``osmium.osm.NodeList`` or a list consisting of
       ``osmium.osm.NodeRef`` or simple node ids.
    """

    def __init__(self, base=None, nodes=None, **attrs):
        # type: (Optional[osm.Way], Optional[NodeListType], typing.Any) -> None
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.nodes = nodes  # type: NodeListType
        else:
            self.nodes = nodes if nodes is not None else base.nodes


class Relation(OSMObject):
    """The mutable version of ``osmium.osm.Relation``. It inherits all attributes
       from osmium.osm.mutable.OSMObject and adds a `members` attribute. This
       may either be an ``osmium.osm.RelationMemberList`` or a list consisting
       of ``osmium.osm.RelationMember`` or tuples of (type, id, role). The
       member type should be a single character 'n', 'w' or 'r'.
    """

    def __init__(self, base=None, members=None, **attrs):
        # type: (Optional[osm.Relation], Optional[RelationMembersType], typing.Any) -> None
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.members = members  # type: RelationMembersType
        else:
            self.members = members if members is not None else base.members


