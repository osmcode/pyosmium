import osmium as o
import sys

if len(sys.argv) != 3:
    print("Usage: python create_nodecache.py <osm file> <node cache>")
    exit(-1)

reader = o.io.Reader(sys.argv[1], o.osm.osm_entity_bits.NODE)

# see more info about cache types at https://docs.osmcode.org/pyosmium/latest/intro.html#handling-geometries
idx = o.index.create_map("sparse_file_array," + sys.argv[2])
lh = o.NodeLocationsForWays(idx)

o.apply(reader, lh)

reader.close()
