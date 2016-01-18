"""
Filter all objects with a tag waterway and save them in a new file.
Note that the result is missing the nodes to be able to reconstruct
the geometries of the ways and relations.

This example shows how to write objects to a file.
"""

import osmium as o

import sys

class WaterwayFilter(o.SimpleHandler):

    def __init__(self, writer):
        o.SimpleHandler.__init__(self)
        self.writer = writer

    def node(self, n):
        if 'waterway' in n.tags:
            self.writer.add_node(n)

    def way(self, w):
        if 'waterway' in w.tags:
            self.writer.add_way(w)

    def relation(self, r):
        if 'waterway' in r.tags:
            self.writer.add_relation(r)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python filter_waterway.py <infile> <outfile>")
        sys.exit(-1)

    writer = o.SimpleWriter(sys.argv[2])
    handler = WaterwayFilter(writer)

    handler.apply_file(sys.argv[1])

    writer.close()

