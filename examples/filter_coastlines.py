"""
Filter all objects with a coastline tag.

This example shows how to write objects to a file.

We need to go twice over the file. First read the ways, filter the ones
we are interested in and remember the nodes required. Then, in a second
run all the relevant nodes and ways are written out.
"""
import osmium as o
import sys


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python filter_coastlines.py <infile> <outfile>")
        sys.exit(-1)


    # go through the ways to find all relevant nodes
    nodes = set()
    # Pre-filter the ways by tags. The less object we need to look at, the better.
    way_filter = o.filter.KeyFilter('natural')
    # only scan the ways of the file
    for obj in o.FileProcessor(sys.argv[1], o.osm.WAY).with_filter(way_filter):
        if obj.tags['natural'] == 'coastline':
            nodes.update(n.ref for n in obj.nodes)


    # go through the file again and write out the data
    writer = o.SimpleWriter(sys.argv[2])

    # This time the pre-filtering should only apply to ways.
    way_filter = o.filter.KeyFilter('natural').enable_for(o.osm.WAY)

    # We need nodes and ways in the second pass.
    for obj in o.FileProcessor(sys.argv[1], o.osm.WAY | o.osm.NODE).with_filter(way_filter):
        if obj.is_node() and obj.id in nodes:
            # Strip the object of tags along the way
            writer.add_node(obj.replace(tags={}))
        elif obj.is_way() and obj.tags['natural'] == 'coastline':
            writer.add_way(obj)

    writer.close()
