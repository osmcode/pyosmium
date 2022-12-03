import osmium.osm._osm as cosm

UNDEFINED_COORDINATE = cosm.get_undefined_coordinate()

class _OSMObject:

    @property
    def id(self):
        return self._data.id()


    @property
    def deleted(self):
        return self._data.deleted()


    @property
    def visible(self):
        return self._data.visible()


    @property
    def version(self):
        return self._data.version()


    @property
    def changeset(self):
        return self._data.changeset()


    @property
    def uid(self):
        return self._data.uid()


    @property
    def timestamp(self):
        return self._data.timestamp()


    @property
    def user(self):
        return self._data.user()


    def positive_id(self):
        return self._data.positive_id()


    def user_is_anonymous(self):
        return self._data.user_is_anonymous()


class Node(_OSMObject):

    def __init__(self, cnode: cosm.COSMNode):
        self._data = cnode
        self._location = None

    @property
    def location(self):
        if self._location is None:
            self._location = self._data.location()

        return self._location


class Way(_OSMObject):

    def __init__(self, cway: cosm.COSMWay):
        self._data = cway


    def is_closed(self):
        return self._data.is_closed()


    def ends_have_same_id(self):
        return self._data.ends_have_same_id()


    def ends_have_same_location(self):
        return self._data.ends_have_same_location()


class Relation(_OSMObject):

    def __init__(self, crelation: cosm.COSMRelation):
        self._data = crelation


class Area(_OSMObject):

    def __init__(self, carea: cosm.COSMArea):
        self._data = carea


    def from_way(self):
        return self._data.from_way()


    def orig_id(self):
        return self._data.orig_id()


    def is_multipolygon(self):
        return self._data.is_multipolygon()


    def num_rings(self):
        return self._data.num_rings()


class Changeset(_OSMObject):

    def __init__(self, carea: cosm.COSMChangeset):
        self._data = carea


    @property
    def id(self):
        return self._data.id()


    @property
    def uid(self):
        return self._data.uid()


    @property
    def created_at(self):
        return self._data.created_at()


    @property
    def closed_at(self):
        return self._data.closed_at()


    @property
    def open(self):
        return self._data.open()


    @property
    def num_changes(self):
        return self._data.num_changes()


    @property
    def user(self):
        return self._data.user()


    def user_is_anonymous(self):
        return self._data.user_is_anonymous()

