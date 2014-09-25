import osmium as o
import sys

class FileStatsHandler(o.SimpleHandler):
    def __init__(self):
        o.SimpleHandler.__init__(self)
        self.nodes = 0
        self.ways = 0
        self.rels = 0

    def node(self, n):
        self.nodes += 1

    def way(self, w):
        self.ways += 1

    def relation(self, r):
        self.rels += 1


fd = o.Reader(sys.argv[1])
h = FileStatsHandler()

o.apply(fd, h)

print "Nodes:", h.nodes
print "Ways:", h.ways
print "Relations:", h.rels
