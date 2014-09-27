import osmium as o
import sys

class RoadLengthHandler(o.SimpleHandler):
    def __init__(self):
        o.SimpleHandler.__init__(self)
        self.length = 0.0

    def way(self, w):
        if 'highway' in w.tags:
            self.length += o.geom.haversine_distance(w.nodes)


fd = o.io.Reader(sys.argv[1])
h = RoadLengthHandler()

i = o.index.SparseLocationTable()
l = o.SparseNodeLocationsForWays(i)

o.apply(fd, l, h)

print 'Total way length:', h.length/1000, 'km'
