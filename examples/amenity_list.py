import osmium as o
import sys

class AmenityListHandler(o.SimpleHandler):

    def print_amenity(amenity, tags, lon, lat):
        name = tags['name'] if 'name' in tags else ''
        print "%f %f %-15s %s" % (lon, lat,
                    tags['amenity'], name)

    def node(self, n):
        if 'amenity' in n.tags:
            self.print_amenity(n.tags, n.location.lon, n.location.lat)

    def area(self, a):
        if 'amenity' in a.tags:
            self.print_amenity(a.tags, 0, 0)


handler = AmenityListHandler()

handler.apply_file(sys.argv[1], o.pre_handlers.AREA)
