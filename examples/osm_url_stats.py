"""
This also creates stats over an OSM file, only the file is first read into
a string buffer.

Shows how to use input from strings.
"""
import osmium
import sys
import urllib.request as urlrequest

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python osm_url_stats.py <osmfile>")
        sys.exit(-1)


    data = urlrequest.urlopen(sys.argv[1]).read()

    counter = {'n': 0, 'w': 0, 'r': 0}

    for o in osmium.FileProcessor(osmium.io.FileBuffer(data, sys.argv[1])):
        counter[o.type_str()] += 1

    print("Nodes: %d" % counter['n'])
    print("Ways: %d" % counter['w'])
    print("Relations: %d" % counter['r'])
