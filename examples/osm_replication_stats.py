"""
Simple example that counts the number of changes on a replication server
starting from a given timestamp for a maximum of n hours.

Shows how to detect the different kind of modifications.
"""
import osmium as o
import sys
import datetime as dt
import osmium.replication.server as rserv

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


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python osm_replication_stats.py <server_url> <start_time> <max kB>")
        sys.exit(-1)

    server_url = sys.argv[1]
    start = dt.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M:%SZ")
    if sys.version_info >= (3,0):
        start = start.replace(tzinfo=dt.timezone.utc)
    maxkb = min(int(sys.argv[3]), 10 * 1024)

    repserv = rserv.ReplicationServer(server_url)

    seqid = repserv.timestamp_to_sequence(start)
    print("Initial sequence id:", seqid)

    h = FileStatsHandler()
    seqid = repserv.apply_diffs(h, seqid, maxkb)
    print("Final sequence id:", seqid)

    h.nodes.outstats("Nodes")
    h.ways.outstats("Ways")
    h.rels.outstats("Relations")
