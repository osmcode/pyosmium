"""
Compute the total length of highways in an osm file.

Shows how to extract the geometry of a way.
"""
import osmium
import sys


def main(osmfile):
    total = 0.0
    # As we need the way geometry, the node locations need to be cached.
    # This is enabled with the with_locations() function.
    for obj in osmium.FileProcessor(osmfile, osmium.osm.NODE | osmium.osm.WAY)\
                     .with_locations()\
                     .with_filter(osmium.filter.KeyFilter('highway')):
        if obj.is_way():
            try:
                total += osmium.geom.haversine_distance(obj.nodes)
            except osmium.InvalidLocationError:
                # A location error might occur if the osm file is an extract
                # where nodes of ways near the boundary are missing.
                print("WARNING: way %d incomplete. Ignoring." % obj.id)

    print('Total way length: %.2f km' % (total/1000))

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
