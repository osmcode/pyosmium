"""
Compute the total length of highways in an osm file.

Shows how to extract the geometry of a way.
"""
import osmium as o
import sys

class RoadLengthHandler(o.SimpleHandler):
    def __init__(self):
        super(RoadLengthHandler, self).__init__()
        self.length = 0.0

    def way(self, w):
        if 'highway' in w.tags:
            try:
                self.length += o.geom.haversine_distance(w.nodes)
            except o.InvalidLocationError:
                # A location error might occur if the osm file is an extract
                # where nodes of ways near the boundary are missing.
                print("WARNING: way %d incomplete. Ignoring." % w.id)

def main(osmfile):
    h = RoadLengthHandler()
    # As we need the geometry, the node locations need to be cached. Therefore
    # set 'locations' to true.
    h.apply_file(osmfile, locations=True)

    print('Total way length: %.2f km' % (h.length/1000))

    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
