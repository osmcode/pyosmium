import osmium as o
import sys

class WayHandler(o.SimpleHandler):

    def __init__(self, idx):
        super(WayHandler, self).__init__()
        self.idx = idx

    def way(self, w):
        for n in w.nodes:
            loc = idx.get(n.ref)
        print("%d %s" % (w.id, len(w.nodes)))

if len(sys.argv) != 3:
    print("Usage: python create_nodecache.py <osm file> <node cache>")
    exit()

reader = o.io.Reader(sys.argv[1], o.osm.osm_entity_bits.WAY)

idx = o.index.create_map("sparse_file_array," + sys.argv[2])
lh = o.NodeLocationsForWays(idx)
lh.ignore_errors()

o.apply(reader, lh, WayHandler(idx))

reader.close()
