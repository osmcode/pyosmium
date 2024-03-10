""" Provides some helper functions for test.
"""
from datetime import datetime, timezone

import osmium

def mkdate(*args):
    return datetime(*args, tzinfo=timezone.utc)

class CountingHandler(osmium.SimpleHandler):

    def __init__(self):
        super(CountingHandler, self).__init__()
        self.counts = [0, 0, 0, 0]

    def node(self, _):
        self.counts[0] += 1

    def way(self, _):
        self.counts[1] += 1

    def relation(self, _):
        self.counts[2] += 1

    def area(self, _):
        self.counts[3] += 1


class IDCollector:

    def __init__(self):
        self.nodes = []
        self.ways = []
        self.relations = []
        self.changesets = []

    def node(self, n):
        self.nodes.append(n.id)

    def way(self, w):
        self.ways.append(w.id)

    def relation(self, r):
        self.relations.append(r.id)

    def changeset(self, c):
        self.changesets.append(c.id)
