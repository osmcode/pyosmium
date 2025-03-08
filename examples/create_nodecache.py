import osmium
import sys

if len(sys.argv) != 3:
    print("Usage: python create_nodecache.py <osm file> <node cache>")
    exit(-1)

reader = osmium.io.Reader(sys.argv[1], osmium.osm.osm_entity_bits.NODE)

idx = osmium.index.create_map("sparse_file_array," + sys.argv[2])
lh = osmium.NodeLocationsForWays(idx)

osmium.apply(reader, lh)

reader.close()
