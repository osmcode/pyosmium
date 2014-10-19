import osmium as o
import sys

if len(sys.argv) != 3:
    print("Usage: python create_nodecache.py <osm file> <node cache>")
    exit()

reader = o.io.Reader(sys.argv[1], o.osm.osm_entity_bits.NODE)

idxfile = open(sys.argv[2], 'a+b')

idx = o.index.DenseLocationMapFile(idxfile.fileno())
lh = o.NodeLocationsForWays(idx)

o.apply(reader, lh)

reader.close()
