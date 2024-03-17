"""
Simple example that counts the number of changes in an osm diff file.

Shows how to detect the different kind of modifications and how to
use the handler generator function instead of a handler class.
"""
import osmium as o
import sys

class Stats:

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
        print(f"{prefix} added: {self.added}")
        print(f"{prefix} modified: {self.modified}")
        print(f"{prefix} deleted: {self.deleted}")


def main(osmfile):
    stats = {t: Stats() for t in 'nwr'}

    for obj in o.FileProcessor(osmfile):
        stats[obj.type_str()].add(obj)

    stats['n'].outstats("Nodes")
    stats['w'].outstats("Ways")
    stats['r'].outstats("Relations")

    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
