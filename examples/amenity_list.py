"""
Extract all objects with an amenity tag from an osm file and list them
with their name and position.

This example shows how geometries from osmium objects can be imported
into shapely using the WKBFactory.
"""
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python amenity_list.py <osmfile>")
        sys.exit(-1)

    handler = AmenityListHandler()

    handler.apply_file(sys.argv[1])
