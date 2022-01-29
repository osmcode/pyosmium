""" Provides some helper functions for test.
"""
from datetime import datetime, timezone

import osmium

def mkdate(*args):
    return datetime(*args, tzinfo=timezone.utc)

def check_repr(o):
    return not str(o).startswith('<') and not repr(o).startswith('<')

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
