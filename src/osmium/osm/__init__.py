from typing import Any, Callable, Sequence

from osmium.osm.mutable import create_mutable_node, create_mutable_way, create_mutable_relation
from ._osm import *

setattr(Node, 'replace', create_mutable_node)
setattr(Way, 'replace', create_mutable_way)
setattr(Relation, 'replace', create_mutable_relation)

def _make_repr(*attrs: str) -> Callable[[object], str]:
    fmt_string = 'osmium.osm.{0}('\
                 + ', '.join([f'{x}={{1.{x}!r}}' for x in attrs])\
                 + ')'

    return lambda o: fmt_string.format(o.__class__.__name__, o)

def _list_repr(obj: Sequence[Any]) -> str:
    return 'osmium.osm.{}([{}])'.format(obj.__class__.__name__,
                                        ', '.join(map(repr, obj)))

def _list_elipse(obj: Sequence[Any]) -> str:
    objects = ','.join(map(str, obj))
    if len(objects) > 50:
        objects = objects[:47] + '...'
    return objects

setattr(Location, '__repr__',
        lambda l: f'osmium.osm.Location(x={l.x!r}, y={l.y!r})'
                      if l.valid() else 'osmium.osm.Location()')
setattr(Location, '__str__',
        lambda l: f'{l.lon_without_check():.7f}/{l.lat_without_check():.7f}'
                      if l.valid() else 'invalid')

setattr(Box, '__repr__', _make_repr('bottom_left', 'top_right'))
setattr(Box, '__str__', lambda b: f'({b.bottom_left!s} {b.top_right!s})')

setattr(Tag, '__repr__', _make_repr('k', 'v'))
setattr(Tag, '__str__', lambda t: f'{t.k}={t.v}')

setattr(TagList, '__repr__', lambda t: "osmium.osm.TagList({%s})"
                                       % ', '.join([f"{i.k!r}: {i.v!r}" for i in t]))
setattr(TagList, '__str__', lambda t: f'{{{_list_elipse(t)}}}')

setattr(NodeRef, '__repr__', _make_repr('ref', 'location'))
setattr(NodeRef, '__str__', lambda n: f'{n.ref:d}@{n.location!s}'
                                     if n.location.valid() else str(n.ref))

setattr(NodeRefList, '__repr__', _list_repr)
setattr(NodeRefList, '__str__', lambda o: f'[{_list_elipse(o)}]')

setattr(RelationMember, '__repr__', _make_repr('ref', 'type', 'role'))
setattr(RelationMember, '__str__', lambda r: f'{r.type}{r.ref:d}@{r.role}' \
                                             if r.role else f'{r.type}{r.ref:d}')

setattr(RelationMemberList, '__repr__', _list_repr)
setattr(RelationMemberList, '__str__', lambda o: f'[{_list_elipse(o)}]')

setattr(OSMObject, '__repr__', _make_repr('id', 'deleted', 'visible', 'version',
                                          'changeset', 'uid', 'timestamp', 'user',
                                          'tags'))

setattr(Node, '__repr__', _make_repr('id', 'deleted', 'visible', 'version',
                                     'changeset', 'uid', 'timestamp', 'user',
                                     'tags', 'location'))
setattr(Node, '__str__', lambda n: f'n{n.id:d}: location={n.location!s} tags={n.tags!s}')

setattr(Way, '__repr__', _make_repr('id', 'deleted', 'visible', 'version', 'changeset',
                                   'uid', 'timestamp', 'user', 'tags', 'nodes'))
setattr(Way, '__str__', lambda o: f'w{o.id:d}: nodes={o.nodes!s} tags={o.tags!s}')

setattr(Relation, '__repr__', _make_repr('id', 'deleted', 'visible', 'version',
                                         'changeset', 'uid', 'timestamp', 'user',
                                         'tags', 'members'))
setattr(Relation, '__str__', lambda o: f'r{o.id:d}: members={o.members!s}, tags={o.tags!s}')

setattr(Changeset, '__repr__', _make_repr('id', 'uid', 'created_at', 'closed_at',
                                          'open', 'num_changes', 'bounds', 'user',
                                          'tags'))
setattr(Changeset, '__str__', lambda o: f'c{o.id:d}: closed_at={o.closed_at!s}, bounds={o.bounds!s}, tags={o.tags!s}')
