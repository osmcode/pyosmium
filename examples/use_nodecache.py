"""
Iterate over all ways (and ways only) using node cache to obtain geometries
"""
import osmium
import sys


class WayHandler:

    def __init__(self, idx):
        self.idx = idx

    def way(self, w):
        locations = []
        for n in w.nodes:
            locations.append(idx.get(n.ref))  # note that cache is used here
        print(w.id, len(w.nodes), locations)


if len(sys.argv) != 3:
    print("Usage: python use_nodecache.py <osm file> <node cache>")
    exit()

reader = osmium.io.Reader(sys.argv[1], osmium.osm.osm_entity_bits.WAY)

idx = osmium.index.create_map("sparse_file_array," + sys.argv[2])
lh = osmium.NodeLocationsForWays(idx)
lh.ignore_errors()

osmium.apply(reader, lh, WayHandler(idx))

reader.close()
