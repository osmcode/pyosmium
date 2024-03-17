"""
Converts a file from one format to another.

This example shows how to write objects to a file.
"""

import osmium as o

import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert.py <infile> <outfile>")
        sys.exit(-1)

    writer = o.SimpleWriter(sys.argv[2])

    for obj in o.FileProcessor(sys.argv[1]):
        if obj.is_node():
            writer.add_node(obj)
        elif obj.is_way():
            writer.add_way(obj)
        elif obj.is_relation():
            writer.add_relation(obj)

    writer.close()

