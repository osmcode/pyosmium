import osmium as o
import sys

class RoadLengthHandler(o.SimpleHandler):
    def __init__(self):
        o.SimpleHandler.__init__(self)
        self.length = 0.0

    def way(self, w):
        if 'highway' in w.tags:
            self.length += o.geom.haversine_distance(w.nodes)

h = RoadLengthHandler()
h.apply_file(sys.argv[1])

print 'Total way length:', h.length/1000, 'km'
