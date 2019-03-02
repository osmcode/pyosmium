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
        super(FileStatsHandler, self).__init__()
        self.nodes = Stats()
        self.ways = Stats()
        self.rels = Stats()

    def node(self, n):
        self.nodes.add(n)

    def way(self, w):
        self.ways.add(w)

    def relation(self, r):
        self.rels.add(r)


def main(osmfile):
    h = FileStatsHandler()

    h.apply_file(osmfile)

    h.nodes.outstats("Nodes")
    h.ways.outstats("Ways")
    h.rels.outstats("Relations")

    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
