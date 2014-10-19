import osmium as o
import sys
import shapely.wkb as wkblib

wkbfab = o.geom.WKBFactory()

class AmenityListHandler(o.SimpleHandler):

    def print_amenity(amenity, tags, lon, lat):
        name = tags['name'] if 'name' in tags else ''
        print("%f %f %-15s %s" % (lon, lat, tags['amenity'], name))

    def node(self, n):
        if 'amenity' in n.tags:
            self.print_amenity(n.tags, n.location.lon, n.location.lat)

    def area(self, a):
        if 'amenity' in a.tags:
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)
            centroid = poly.representative_point()
            self.print_amenity(a.tags, centroid.x, centroid.y)


handler = AmenityListHandler()

handler.apply_file(sys.argv[1], o.pre_handlers.AREA)
