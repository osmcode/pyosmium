"""
Iterate over all ways (and ways only) using node cache to obtain geometries
"""
import osmium
import sys

class WayHandler:

    def __init__(self, idx):
        self.idx = idx

    def way(self, w):
        for n in w.nodes:
            loc = idx.get(n.ref) # note that cache is used here
        print("%d %s" % (w.id, len(w.nodes)))

if len(sys.argv) != 3:
    print("Usage: python use_nodecache.py <osm file> <node cache>")
    exit()

reader = osmium.io.Reader(sys.argv[1], osmium.osm.osm_entity_bits.WAY)

idx = osmium.index.create_map("sparse_file_array," + sys.argv[2])
lh = osmium.NodeLocationsForWays(idx)
lh.ignore_errors()

osmium.apply(reader, lh, WayHandler(idx))

reader.close()
