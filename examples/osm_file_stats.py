"""
Simple example that counts the number of objects in an osm file.

Shows how to write a handler for the different types of objects.
"""
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python osm_file_stats.py <osmfile>")
        sys.exit(-1)

    h = FileStatsHandler()

    h.apply_file(sys.argv[1])

    print("Nodes: %d" % h.nodes)
    print("Ways: %d" % h.ways)
    print("Relations: %d" % h.rels)
