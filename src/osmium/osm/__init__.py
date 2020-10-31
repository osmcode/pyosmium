import osmium.osm.mutable
from ._osm import *

def create_mutable_node(node, **args):
    """ Create a mutable node replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Node(base=node, **args)

def create_mutable_way(way, **args):
    """ Create a mutable way replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Way(base=way, **args)

def create_mutable_relation(rel, **args):
    """ Create a mutable relation replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Relation(base=rel, **args)

Node.replace = create_mutable_node
Way.replace = create_mutable_way
Relation.replace = create_mutable_relation

def _make_repr(attr_list):
    fmt_string = 'osmium.osm.{0}('\
                 + ', '.join(['{0}={{1.{0}!r}}'.format(x) for x in attr_list])\
                 + ')'

    return lambda o: fmt_string.format(o.__class__.__name__, o)

def _list_repr(obj):
    return 'osmium.osm.{}([{}])'.format(obj.__class__.__name__,
                                        ', '.join(map(repr, obj)))

def _list_elipse(obj):
    objects = ','.join(map(str, obj))
    if len(objects) > 50:
        objects = objects[:47] + '...'
    return objects

Location.__repr__ = lambda l: 'osmium.osm.Location(x={0.x!r}, y={0.y!r})'.format(l) \
                               if l.valid() else 'osmium.osm.Location()'
Location.__str__ = lambda l: '{:f}/{:f}'.format(l.lon_without_check(),
                                                l.lat_without_check()) \
                             if l.valid() else 'invalid'

Box.__repr__ = _make_repr(['bottom_left', 'top_right'])
Box.__str__ = lambda b: '({0.bottom_left!s} {0.top_right!s})'.format(b)

Tag.__repr__ = _make_repr(['k', 'v'])
Tag.__str__ = lambda t: '{0.k}={0.v}'.format(t)

TagList.__repr__ = lambda t: "osmium.osm.TagList({%s})" \
                              % ', '.join(["%r: %r" % (i.k, i.v) for i in t])
TagList.__str__ = lambda t: '{' + _list_elipse(t) + '}'

NodeRef.__repr__ = _make_repr(['ref', 'location'])
NodeRef.__str__ = lambda n: '{0.ref:d}@{0.location!s}'.format(n) \
                            if n.location.valid() else str(n.ref)

NodeRefList.__repr__ = _list_repr
NodeRefList.__str__ = lambda o: '[' + _list_elipse(o) + ']'

RelationMember.__repr__ = _make_repr(['ref', 'type', 'role'])
RelationMember.__str__ = lambda r: ('{0.type}{0.ref:d}@{0.role}' \
                                   if r.role else '{0.type}{0.ref:d}').format(r)

RelationMemberList.__repr__ = _list_repr
RelationMemberList.__str__ = lambda o: '[' + _list_elipse(o) + ']'

OSMObject.__repr__ = _make_repr(['id', 'deleted', 'visible', 'version', 'changeset',
                                 'uid', 'timestamp', 'user', 'tags'])

Node.__repr__ = _make_repr(['id', 'deleted', 'visible', 'version', 'changeset',
                            'uid', 'timestamp', 'user', 'tags', 'location'])
Node.__str__ = lambda n: 'n{0.id:d}: location={0.location!s} tags={0.tags!s}'\
                         .format(n)

Way.__repr__ = _make_repr(['id', 'deleted', 'visible', 'version', 'changeset',
                           'uid', 'timestamp', 'user', 'tags', 'nodes'])
Way.__str__ = lambda o: 'w{0.id:d}: nodes={0.nodes!s} tags={0.tags!s}' \
                         .format(o)

Relation.__repr__ = _make_repr(['id', 'deleted', 'visible', 'version', 'changeset',
                                'uid', 'timestamp', 'user', 'tags', 'members'])
Relation.__str__ = lambda o: 'r{0.id:d}: members={0.members!s}, tags={0.tags!s}' \
                             .format(o)

Changeset.__repr__ = _make_repr(['id', 'uid', 'created_at', 'closed_at', 'open',
                                 'num_changes', 'bounds', 'user', 'tags'])
Changeset.__str__ = lambda o: 'c{0.id:d}: closed_at={0.closed_at!s}, bounds={0.bounds!s}, tags={0.tags!s}' \
                              .format(o)
