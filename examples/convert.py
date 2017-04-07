"""
Converts a file from one format to another.

This example shows how to write objects to a file.
"""

import osmium as o

import sys

class Convert(o.SimpleHandler):

    def __init__(self, writer):
        super(Convert, self).__init__()
        self.writer = writer

    def node(self, n):
        self.writer.add_node(n)

    def way(self, w):
        self.writer.add_way(w)

    def relation(self, r):
        self.writer.add_relation(r)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert.py <infile> <outfile>")
        sys.exit(-1)

    writer = o.SimpleWriter(sys.argv[2])
    handler = Convert(writer)

    handler.apply_file(sys.argv[1])

    writer.close()

