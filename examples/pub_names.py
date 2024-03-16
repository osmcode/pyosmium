"""
Search for pubs in an osm file and list their names.
"""
import osmium
import sys

def main(osmfile):
    for obj in osmium.FileProcessor(osmfile)\
                     .with_filter(osmium.filter.KeyFilter('amenity'))\
                     .with_filter(osmium.filter.KeyFilter('name')):
        if obj.tags['amenity'] == 'pub':
            print(obj.tags['name'])

    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    exit(main(sys.argv[1]))
