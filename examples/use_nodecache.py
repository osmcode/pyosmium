import osmium as o
import sys

class WayHandler(o.SimpleHandler):

    def __init__(self, idx):
        o.SimpleHandler.__init__(self)
        self.idx = idx

    def way(self, w):
        for n in w.nodes:
            n.lat, n.lon # throws an exception if the coordinates are missing
            loc = idx.get(n.ref)
        print w.id, len(w.nodes)

if len(sys.argv) != 3:
    print "Usage: python create_nodecache.py <osm file> <node cache>"
    exit()

reader = o.io.Reader(sys.argv[1], o.osm.osm_entity_bits.WAY)

idxfile = open(sys.argv[2], 'a+b')
print sys.argv[2],idxfile.fileno()

idx = o.index.DenseLocationMapFile(idxfile.fileno())
lh = o.NodeLocationsForWays(idx)

o.apply(reader, lh, WayHandler(idx))

reader.close()
