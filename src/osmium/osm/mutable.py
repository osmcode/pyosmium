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
                 timestamp=None, uid=None, tags=None, user=None):
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

    def __init__(self, base=None, location=None, **attrs):
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

    def __init__(self, base=None, nodes=None, **attrs):
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

    def __init__(self, base=None, members=None, **attrs):
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.members = members
        else:
            self.members = members if members is not None else base.members
