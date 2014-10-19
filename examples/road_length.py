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
                print("WARNING: way %d incomplete. Ignoring." % w.id)

h = RoadLengthHandler()
h.apply_file(sys.argv[1], o.pre_handlers.LOCATION)

print('Total way length: %.2f km' % (h.length/1000))
