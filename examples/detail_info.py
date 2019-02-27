"""
Print most info there is about the first encountered node, way, area and relation

see https://docs.osmcode.org/pyosmium/master/ref_osm.html for the full documentation

Note that some .pbf files may have part of their information stripped, e.g. in some downloads from https://download.geofabrik.de the user names, user IDs and changeset IDs are missing due to data protection regulations in the European Union.

Author: Lukas Toggenburger
"""

import osmium
import sys

class DetailInfoHandler(osmium.SimpleHandler):

    def __init__(self):
        super(DetailInfoHandler, self).__init__()
        self._node_showed = False
        self._way_showed  = False
        self._rel_showed  = False
        self._area_showed = False

    def print_obj_info(self, o):
        print("changeset: Id of changeset where this version of the object was created (read-only): " + str(o.changeset))
        print("deleted: True if the object is no longer visible (read-only): " + str(o.deleted))
        print("id: OSM id of the object (read-only): " + str(o.id))
        print("positive_id(): OSM id of the object: " + str(o.positive_id()))

        #print("tags: List of tags describing the object (read-only): " + str(o.tags)) # TODO: doesn't work with python2 if keys/values contain non-ASCII characters
        print("tags: List of tags describing the object (read-only):")
        for tag in o.tags:
            print("    " + tag.k + " = " + tag.v)

        print("timestamp: Date when this version has been created (returned as a datetime.datetime) (read-only): " + str(o.timestamp))
        print("uid: Id of the user that created this version of the object. Only this ID uniquely identifies users. (read-only): " + str(o.uid))
        print("user: Name of the user that created this version. Be aware that user names can change, so that the same user ID may appear with different names and vice versa. (read-only): " + str(o.user))
        print("user_is_anonymous(): Check if the user is anonymous. If true, the uid does not uniquely identify a single user but only the group of all anonymous users in general.: " + str(o.user_is_anonymous()))
        print("version: Version number of the object (read-only): " + str(o.version))
        print("visible: True if the object is visible (read-only): " + str(o.visible))

    def node(self, n):
        if self._node_showed == False:
            self._node_showed = True
            print("This is a NODE with the following properties:")
            self.print_obj_info(n)
            print("location: The geographic coordinates of the node (data type osmium.osm.Location): " + str(n.location))
            print("location.lat: Latitude  (y coordinate) as floating point number (read-only): " + str(n.location.lat))
            print("location.lon: Longitude (x coordinate) as floating point number (read-only): " + str(n.location.lon))
            print("location.lat_without_check(): Latitude  (y coordinate) without checking if the location is valid (datatype float): " + str(n.location.lat_without_check()))
            print("location.lon_without_check(): Longitude (x coordinate) without checking if the location is valid (datatype float): " + str(n.location.lon_without_check()))
            print("valid(): Check that the location is a valid WGS84 coordinate, i.e. that it is within the usual bounds (datatype bool): " + str(n.location.valid()))
            print("x: X coordinate (longitude) as a fixed-point integer: " + str(n.location.x))
            print("y: Y coordinate (latitude)  as a fixed-point integer: " + str(n.location.y))
            print("------------------------------------------------------")

    def way(self, w):
        if self._way_showed == False:
            self._way_showed = True
            print("This is a WAY with the following properties:")
            self.print_obj_info(w)

            print("nodes: Ordered list of nodes (datatype osmium.osm.WayNodeList) (read-only): " + str(w.nodes))
            for node in w.nodes:
                print("    " + str(node))
                # TODO: how to access lat/lon of nodes?

            print("ends_have_same_id(): True if the start and end node are exactly the same (synonym for is_closed()): " + str(w.ends_have_same_id()) + "=" + str(w.is_closed()))
            print("ends_have_same_location(): True if the start and end node of the way are at the same location: " + str(w.ends_have_same_location())) # Throws an exception if the location of one of the nodes is missing.
            print("------------------------------------------------------")

    def area(self, a):
        if self._area_showed == False:
            self._area_showed = True
            print("This is an AREA with the following properties:")
            self.print_obj_info(a)
            print("from_way(): Return true if the area was created from a way, false if it was created from a relation of multipolygon type: " + str(a.from_way()))
            print("is_multipolygon(): Return true if this area is a true multipolygon, i.e. it consists of multiple outer rings: " + str(a.is_multipolygon()))
            print("num_rings(): Return a tuple with the number of outer rings and inner rings: " + str(a.num_rings()))
            print("orig_id(): Compute the original OSM id of this object. Note that this is not necessarily unique because the object might be a way or relation which have an overlapping id space: " + str(a.orig_id()))

            print("outer_rings() / inner_rings(): Return an iterator over all outer rings / inner rings of the multipolygon: " + str(a.outer_rings()))
            for outer_ring in a.outer_rings():
                print("    " + str(outer_ring))
                for inner_ring in a.inner_rings(outer_ring): # TODO: check if this nested structure makes sense
                    print("        " + str(inner_ring))
            print("------------------------------------------------------")

    def relation(self, r):
        if self._rel_showed == False:
            self._rel_showed = True
            print("This is a RELATION with the following properties:")
            self.print_obj_info(r)

            print("members: " + str(r.members))
            for member in r.members:
                print("    " + str(member))
            print("------------------------------------------------------")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python detail_info.py <osmfile>")
        sys.exit(-1)

    DetailInfoHandler().apply_file(sys.argv[1])

