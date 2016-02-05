"""
This also creates stats over an OSM file, only the file is first read into
a string buffer.

Shows how to use input from strings.
"""
import osmium as o
import sys
import urllib.request

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
        print("Usage: python osm_url_stats.py <osmfile>")
        sys.exit(-1)


    data = urllib.request.urlopen(sys.argv[1]).read()

    h = FileStatsHandler()
    h.apply_buffer(data, sys.argv[1])

    print("Nodes: %d" % h.nodes)
    print("Ways: %d" % h.ways)
    print("Relations: %d" % h.rels)
