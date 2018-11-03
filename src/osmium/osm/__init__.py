from ._osm import *
import osmium.osm.mutable

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

Location.__repr__ = lambda l : 'osmium.osm.Location(x=%r, y=%r)' \
                               % (l.x, l.y) \
                               if l.valid() else 'osmium.osm.Location()'
Location.__str__ = lambda l : '%f/%f' % (l.lon_without_check(), l.lat_without_check()) \
                              if l.valid() else 'invalid'

Box.__repr__ = lambda b : 'osmium.osm.Box(bottom_left=%r, top_right=%r)' \
                          % (b.bottom_left, b.top_right)
Box.__str__ = lambda b : '(%s %s)' % (b.bottom_left, b.top_right)

Tag.__repr__ = lambda t : 'osmium.osm.Tag(k=%s, v=%s)' % (t.k, t.v)
Tag.__str__ = lambda t : '%s=%s' % (t.k, t.v)

TagList.__repr__ = lambda t : "osmium.osm.TagList({%s})" \
                              % ",".join(["%r=%r" % (i.k, i.v) for i in t])
TagList.__str__ = lambda t : "{%s}" % ",".join([str(i) for i in t])

NodeRef.__repr__ = lambda n : 'osmium.osm.NodeRef(ref=%r, location=%r)' % (n.ref, n.location)
NodeRef.__str__ = lambda n : '%s@%s' % (n.ref, n.location) if n.location.valid() \
                             else str(n.ref)

NodeRefList.__repr__ = lambda t : "%s([%s])" % (t.__class__.__name__,
                                                ",".join([repr(i) for i in t]))
NodeRefList.__str__ = lambda t : "[%s]" % ",".join([str(i) for i in t])

RelationMember.__repr__ = lambda r : 'osmium.osm.RelationMember(ref=%r, type=%r, role=%r)' \
                                     % (r.ref, r.type, r.role)
RelationMember.__str__ = lambda r : '%s%d@%s' % (r.type, r.ref, r.role) \
                                    if r.role else '%s%d' % (r.type, r.ref)

RelationMemberList.__repr__ = lambda t : "osmium.osm.RelationMemberList([%s])" \
                                  % ",".join([repr(i) for i in t])
RelationMemberList.__str__ = lambda t : "[%s]" % ",".join([str(i) for i in t])

OSMObject.__repr__ = lambda o : '%s(id=%r, deleted=%r, visible=%r, version=%r, changeset=%r, uid=%r, timestamp=%r, user=%r, tags=%r)'% (o.__class__.__name__, o.id, o.deleted, o.visible, o.version, o.changeset, o.uid, o.timestamp, o.user, o.tags)

def _str_ellipse(s, length=50):
    s = str(s)
    return s if len(s) <= length else (s[:length - 4] + '...' + s[-1])

Node.__repr__ = lambda o : '%s(id=%r, deleted=%r, visible=%r, version=%r, changeset=%r, uid=%r, timestamp=%r, user=%r, tags=%r, location=%r)'% (o.__class__.__name__, o.id, o.deleted, o.visible, o.version, o.changeset, o.uid, o.timestamp, o.user, o.tags, o.location)
Node.__str__ = lambda n : 'n%d: location=%s tags=%s' \
                          % (n.id, n.location, _str_ellipse(n.tags))

Way.__repr__ = lambda o : '%s(id=%r, deleted=%r, visible=%r, version=%r, changeset=%r, uid=%r, timestamp=%r, user=%r, tags=%r, nodes=%r)'% (o.__class__.__name__, o.id, o.deleted, o.visible, o.version, o.changeset, o.uid, o.timestamp, o.user, o.tags, o.nodes)
Way.__str__ = lambda o : 'w%d: nodes=%s tags=%s' \
                         % (o.id, _str_ellipse(o.nodes), _str_ellipse(o.tags))

Relation.__repr__ = lambda o : '%s(id=%r, deleted=%r, visible=%r, version=%r, changeset=%r, uid=%r, timestamp=%r, user=%r, tags=%r, members=%r)'% (o.__class__.__name__, o.id, o.deleted, o.visible, o.version, o.changeset, o.uid, o.timestamp, o.user, o.tags, o.members)
Relation.__str__ = lambda o : 'r%d: members=%s, tags=%s' \
                              % (o.id, _str_ellipse(o.members), _str_ellipse(o.tags))

Changeset.__repr__ = lambda o : '%s(id=%r, uid=%r, created_at=%r, closed_at=%r, open=%r, num_changes=%r, bounds=%r, user=%r, tags=%s)' %(o.__class__.__name__, o.id, o.uid, o.created_at, o.closed_at, o.open, o.num_changes, o.bounds, o.user, o.tags)
Changeset.__str__ = lambda o : 'c%d: closed_at=%s, bounds=%s, tags=%s' \
                               % (o.id, o.closed_at, o.bounds, _str_ellipse(o.tags))
