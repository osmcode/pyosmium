import osmium
import sys

class NamesHandler(osmium.SimpleHandler):

    def output_pubs(self, tags):
        if 'amenity' in tags and tags['amenity'] == 'pub':
            if 'name' in tags:
                print tags['name']

    def node(self, n):
        self.output_pubs(n.tags)

    def way(self, w):
        self.output_pubs(w.tags)


osmium.apply(osmium.io.Reader(sys.argv[1]), NamesHandler())

