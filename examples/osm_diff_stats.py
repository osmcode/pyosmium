"""
Simple example that counts the number of changes in an osm diff file.

Shows how to detect the different kind of modifications and how to
use the handler generator function instead of a handler class.
"""
import osmium as o
import sys

class Stats(object):

    def __init__(self):
        self.added = 0
        self.modified = 0
        self.deleted = 0

    def __call__(self, o):
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


def main(osmfile):
    nodes = Stats()
    ways = Stats()
    rels = Stats()

    h = o.make_simple_handler(node=nodes, way=ways, relation=rels)

    h.apply_file(osmfile)

    nodes.outstats("Nodes")
    ways.outstats("Ways")
    rels.outstats("Relations")

    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
