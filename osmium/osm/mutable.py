class OSMObject(object):

    def __init__(self, base=None, id=None, version=None, visible=None, changeset=None,
            timestamp=None, uid=None, tags=None):
        if base is None:
            self.id = id
            self.version = version
            self.visible = visible
            self.changeset = changeset
            self.timestamp = timestamp
            self.uid = uid
            self.tags = tags
        else:
            self.id = base.id if id is None else id
            self.version = base.version if version is None else version
            self.visible = base.visible if visible is None else visible
            self.changeset = base.changeset if changeset is None else changeset
            self.timestamp = base.timestamp if timestamp is None else timestamp
            self.uid = base.uid if uid is None else uid
            self.tags = base.tags if tags is None else tags


class Node(OSMObject):
    """An OSM node that can be modified. The class has the same attributes as
       an osmium.osm.Node. The `location` attribute may either be an
       osmium.osm.Location or a tuple of floats representing (x,y) coordinates.
       The `tags` attribute can be an osmium.osm.TagList, a dict-like object
       or a list of tuples, where each tuple contains a (key value) string pair.
    """

    def __init__(self, base=None, location=None, **attrs):
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.location = location
        else:
            self.location = loctation if location is not None else base.location


class Way(OSMObject):
    """An OSM way that can be modified.
    """

    def __init__(self, base=None, nodes=None, **attrs):
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.nodes = nodes
        else:
            self.nodes = nodes if nodes is not None else base.nodes

class Relation(OSMObject):
    """An OSM relation that can be modified.
    """

    def __init__(self, base=None, members=None, **attrs):
        OSMObject.__init__(self, base=base, **attrs)
        if base is None:
            self.members = members
        else:
            self.members = members if members is not None else base.members


