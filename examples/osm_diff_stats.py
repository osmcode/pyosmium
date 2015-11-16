"""
Simple example that counts the number of changes in an osm diff file.

Shows how to detect the different kind of modifications.
"""
import osmium as o
import sys

class Stats(object):

    def __init__(self):
        self.added = 0
        self.modified = 0
        self.deleted = 0

    def add(self, o):
        if o.deleted:
            self.deleted += 1
        elif o.version == 1:
            self.added += 1
        else:
            self.modified += 1


    def outstats(self, prefix):
        print("%s added: %d" % (prefix, self.added))
        print("%s modified: %d" % (prefix, self.modified))
        print("%s deleted: %d" % (prefix, self.deleted))

class FileStatsHandler(o.SimpleHandler):
    def __init__(self):
        o.SimpleHandler.__init__(self)
        self.nodes = Stats()
        self.ways = Stats()
        self.rels = Stats()

    def node(self, n):
        self.nodes.add(n)

    def way(self, w):
        self.ways.add(w)

    def relation(self, r):
        self.rels.add(r)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python osm_file_stats.py <osmfile>")
        sys.exit(-1)

    h = FileStatsHandler()

    h.apply_file(sys.argv[1])

    h.nodes.outstats("Nodes")
    h.ways.outstats("Ways")
    h.rels.outstats("Relations")
