import osmium as o

class MyHandler(o.SimpleHandler):
    def node(self, n):
        print "Node!",n.id, n.location.lon, n.location.lat

    def way(self, w):
        print "Way!", w.id, len(w.tags), w.timestamp
        if len(w.tags) > 0:
            print "yes" if "landuse" in w.tags else "no"
            for t in w.tags:
                print t.k,"=>", t.v
            print w.nodes[100000].ref

    def relation(self, r):
        print "Relation!", r.id, len(r.members)
        for m in r.members:
            print m.type, m.ref, m.role


fd = o.io.Reader("examples/test.osm", o.osm.osm_entity_bits.NODE)
h = MyHandler()

o.apply(fd, h)
