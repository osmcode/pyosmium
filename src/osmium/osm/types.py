from typing import Sequence, Any, NamedTuple, Callable
import collections.abc

import osmium.osm._osm as cosm
import osmium.osm.mutable

def _make_repr(name, *attrs: str) -> Callable[[object], str]:
    fmt_string = f'osmium.osm.{name}('\
                 + ', '.join([f'{x}={{0.{x}!r}}' for x in attrs])\
                 + ')'

    def _repr(self):
        if self._pyosmium_data.is_valid():
            return fmt_string.format(self)

    return _repr


def _list_elipse(obj: Sequence[Any]) -> str:
    objects = ','.join(map(str, obj))
    if len(objects) > 50:
        objects = objects[:47] + '...'
    return objects


class _OSMObject:

    @property
    def id(self):
        return self._pyosmium_data.id()


    @property
    def deleted(self):
        return self._pyosmium_data.deleted()


    @property
    def visible(self):
        return self._pyosmium_data.visible()


    @property
    def version(self):
        return self._pyosmium_data.version()


    @property
    def changeset(self):
        return self._pyosmium_data.changeset()


    @property
    def uid(self):
        return self._pyosmium_data.uid()


    @property
    def timestamp(self):
        return self._pyosmium_data.timestamp()


    @property
    def user(self):
        return self._pyosmium_data.user()


    def positive_id(self):
        return self._pyosmium_data.positive_id()


    def user_is_anonymous(self):
        return self._pyosmium_data.user_is_anonymous()


class Node(_OSMObject):

    def __init__(self, cnode: cosm.COSMNode):
        self._pyosmium_data = cnode
        self._location = None
        self.tags = TagList(self._pyosmium_data)

    def replace(self, **kwargs):
        return osmium.osm.mutable.Node(self, **kwargs)

    @property
    def location(self):
        if self._location is None:
            self._location = self._pyosmium_data.location()

        return self._location


    def __str__(self):
        return f'n{self.id:d}: location={self.location!s} tags={self.tags!s}'


    __repr__ = _make_repr('Node', 'id', 'deleted', 'visible', 'version',
                          'changeset', 'uid', 'timestamp', 'user',
                          'tags', 'location')


class Way(_OSMObject):

    def __init__(self, cway: cosm.COSMWay):
        self._pyosmium_data = cway
        self.tags = TagList(self._pyosmium_data)
        self._nodes = None

    def replace(self, **kwargs):
        return osmium.osm.mutable.Way(self, **kwargs)


    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = WayNodeList(self._pyosmium_data, self._pyosmium_data.nodes())

        return self._nodes


    def is_closed(self):
        return self._pyosmium_data.is_closed()


    def ends_have_same_id(self):
        return self._pyosmium_data.is_closed()


    def ends_have_same_location(self):
        return self._pyosmium_data.ends_have_same_location()


    def __str__(self):
        return f'w{self.id:d}: nodes={self.nodes!s} tags={self.tags!s}'


    __repr__ = _make_repr('Way', 'id', 'deleted', 'visible', 'version', 'changeset',
                          'uid', 'timestamp', 'user', 'tags', 'nodes')


class Relation(_OSMObject):

    def __init__(self, crelation: cosm.COSMRelation):
        self._pyosmium_data = crelation
        self.tags = TagList(self._pyosmium_data)
        self.members = RelationMemberList(self._pyosmium_data)

    def replace(self, **kwargs):
        return osmium.osm.mutable.Relation(self, **kwargs)

    def __str__(self):
        if self._pyosmium_data.is_valid():
            return f"r{self.id:d}: members={self.members!s}, tags={self.tags!s}"

        return f"<invalid>"

    __repr__ = _make_repr('Relation', 'id', 'deleted', 'visible', 'version',
                                      'changeset', 'uid', 'timestamp', 'user',
                                      'tags', 'members')

class OuterRingIterator:

    def __init__(self, parent):
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.outer_begin()

    def __iter__(self):
        return self

    def __next__(self):
        return OuterRing(self._pyosmium_data, self._pyosmium_data.outer_next(self.iterator))


class InnerRingIterator:

    def __init__(self, parent, oring):
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.inner_begin(oring._get_list())

    def __iter__(self):
        return self

    def __next__(self):
        return InnerRing(self._pyosmium_data, self._pyosmium_data.inner_next(self.iterator))




class Area(_OSMObject):

    def __init__(self, carea: cosm.COSMArea):
        self._pyosmium_data = carea
        self.tags = TagList(self._pyosmium_data)


    def from_way(self):
        return self._pyosmium_data.from_way()


    def orig_id(self):
        return self._pyosmium_data.orig_id()


    def is_multipolygon(self):
        return self._pyosmium_data.is_multipolygon()


    def num_rings(self):
        return self._pyosmium_data.num_rings()


    def outer_rings(self):
        return OuterRingIterator(self._pyosmium_data)

    def inner_rings(self, oring):
        return InnerRingIterator(self._pyosmium_data, oring)
        return map(lambda ring: InnerRing(self._pyosmium_data, ring), self._pyosmium_data.inner_rings(oring._get_list()))


class Changeset(_OSMObject):

    def __init__(self, carea: cosm.COSMChangeset):
        self._pyosmium_data = carea
        self._bounds = None
        self.tags = TagList(self._pyosmium_data)


    @property
    def id(self):
        return self._pyosmium_data.id()


    @property
    def uid(self):
        return self._pyosmium_data.uid()


    @property
    def created_at(self):
        return self._pyosmium_data.created_at()


    @property
    def closed_at(self):
        return self._pyosmium_data.closed_at()


    @property
    def open(self):
        return self._pyosmium_data.open()


    @property
    def num_changes(self):
        return self._pyosmium_data.num_changes()


    @property
    def user(self):
        return self._pyosmium_data.user()


    @property
    def bounds(self):
        if self._bounds is None:
            self._bounds = self._pyosmium_data.bounds()

        return self._bounds


    def user_is_anonymous(self):
        return self._pyosmium_data.user_is_anonymous()


    def __str__(self):
        return f'c{self.id:d}: closed_at={self.closed_at!s}, bounds={self.bounds!s}, tags={self.tags!s}'


    __repr__ =  _make_repr('Changeset', 'id', 'uid', 'created_at', 'closed_at',
                                        'open', 'num_changes', 'bounds', 'user',
                                        'tags')


class Tag(NamedTuple):
    k: str
    v: str

    def __str__(self):
        return f"{self.k}={self.v}"


class TagIterator:

    def __init__(self, parent):
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.tags_begin()

    def __iter__(self):
        return self

    def __next__(self):
        return self._pyosmium_data.tags_next(self.iterator)


class MemberIterator:

    def __init__(self, parent):
        self._pyosmium_data = parent
        self.iterator = self._pyosmium_data.members_begin()

    def __iter__(self):
        return self

    def __next__(self):
        return self._pyosmium_data.members_next(self.iterator)


class TagList:

    def __init__(self, parent):
        self._pyosmium_data = parent


    def __len__(self):
        return self._pyosmium_data.tags_size()


    def __getitem__(self, key):
        if key is None:
            raise KeyError("Key 'None' not allowed.")

        val = self._pyosmium_data.tags_get_value_by_key(key, None)
        if val is None:
            raise KeyError("No tag with that key.")

        return val


    def __contains__(self, key):
        return key is not None and self._pyosmium_data.tags_has_key(key)


    def get(self, key, default=None):
        if key is None:
            return default

        return self._pyosmium_data.tags_get_value_by_key(key, default)


    def __iter__(self):
        return TagIterator(self._pyosmium_data)


    def __str__(self):
        return f"{{{_list_elipse(self)}}}"


    def __repr__(self):
        tagstr = ', '.join([f"{i.k!r}: {i.v!r}" for i in self])
        return f"osmium.osm.TagList({{{tagstr}}})"


class RelationMember:

    def __init__(self, ref, mtype, role):
        self.ref = ref
        self.type = mtype
        self.role = role


    def __str__(self):
        if self.role:
            return f"{self.type}{self.ref:d}@{self.role}"

        return f"{self.type}{self.ref:d}"


    def __repr__(self):
        return f"osmium.osm.RelationMember(ref={self.ref!r}, type={self.type!r}, role={self.role!r})"


class RelationMemberList:

    def __init__(self, parent):
        self._pyosmium_data = parent


    def __len__(self):
        return self._pyosmium_data.members_size()


    def __iter__(self):
        return MemberIterator(self._pyosmium_data)


    def __str__(self):
        if not self._pyosmium_data.is_valid():
            return '[<invalid>]'

        return f'[{_list_elipse(self)}]'


    def __repr__(self):
        if not self._pyosmium_data.is_valid():
            return f"osmium.osm.{self.__class__.__name__}(<invalid>)"

        return 'osmium.osm.{}([{}])'.format(self.__class__.__name__,
                                        ', '.join(map(repr, self)))



class NodeRef:

    def __init__(self, location, ref):
        self.location = location
        self.ref = ref


    @property
    def x(self):
        return self.location.x


    @property
    def y(self):
        return self.location.y


    @property
    def lat(self):
        return self.location.lat


    @property
    def lon(self):
        return self.location.lon


    def __str__(self):
        if self.location.valid():
            return f"{self.ref:d}@{self.location!s}"

        return str(self.ref)


    def __repr__(self):
        return f"osmium.osm.NodeRef(ref={self.ref!r}, location={self.location!r})"



class NodeRefList(collections.abc.Sequence):

    def __init__(self, parent, ref_list):
        self._pyosmium_data = parent
        self._list = ref_list


    def _get_list(self):
        if self._pyosmium_data.is_valid():
            return self._list

        raise RuntimeError("Access to removed object")

    def is_closed(self):
        return self._get_list().is_closed()

    def ends_have_same_id(self):
        return self._get_list().is_closed()

    def ends_have_same_location(self):
        return self._get_list().ends_have_same_location()

    def __len__(self):
        return self._get_list().size()


    def __getitem__(self, idx):
        return self._get_list().get(idx)


    def __str__(self):
        if not self._pyosmium_data.is_valid():
            return '[<invalid>]'

        return f'[{_list_elipse(self)}]'


    def __repr__(self):
        if not self._pyosmium_data.is_valid():
            return f"osmium.osm.{self.__class__.__name__}(<invalid>)"

        return 'osmium.osm.{}([{}])'.format(self.__class__.__name__,
                                        ', '.join(map(repr, self)))


class WayNodeList(NodeRefList):
    pass


class OuterRing(NodeRefList):
    pass


class InnerRing(NodeRefList):
    pass
