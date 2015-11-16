"""
Compute the total length of highways in an osm file.

Shows how extract the geometry of a way.
"""
import osmium as o
import sys

class RoadLengthHandler(o.SimpleHandler):
    def __init__(self):
        o.SimpleHandler.__init__(self)
        self.length = 0.0

    def way(self, w):
        if 'highway' in w.tags:
            try:
                self.length += o.geom.haversine_distance(w.nodes)
            except o.InvalidLocationError:
                # A location error might occur if the osm file is an extract
                # where nodes of ways near the boundary are missing.
                print("WARNING: way %d incomplete. Ignoring." % w.id)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python road_length.py <osmfile>")
        sys.exit(-1)

    h = RoadLengthHandler()
    # As we need the geometry, the node locations need to be cached. Therefore
    # set 'locations' to true.
    h.apply_file(sys.argv[1], locations=True)

    print('Total way length: %.2f km' % (h.length/1000))
