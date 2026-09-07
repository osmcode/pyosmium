"""
Download example object from Overpass and turn it to shapely geometry and analyze shapely geometries
"""
import requests
import shapely.ops
import shapely.wkb

import osmium as o

wkb_factory = o.geom.WKBFactory()


class GeometryHandler(o.SimpleHandler):
    def __init__(self):
        super(GeometryHandler, self).__init__()
        self.__geometries = []

    def way(self, w):
        if 'amenity' in w.tags:
            wkb = wkb_factory.create_linestring(w)
            shape = shapely.wkb.loads(wkb, hex=True)
            self.__geometries.append(shape)

    @property
    def geometries(self):
        return self.__geometries


def get_geometries(data):
    # use MergeInputReader to sort input, so nodes will come first. Otherwise invalid locations could be passed
    # in ways/relations GeometryHandler
    mir = o.MergeInputReader()
    mir.add_buffer(data, "osm")  # Overpass returns data in osm format
    gh = GeometryHandler()
    # use memory index (flex_mem) for node locations cache. Use "sparse_file_array,<filename>" for file backed indices
    mir.apply(gh, idx='flex_mem')
    return gh.geometries


def analyze(geoms):
    """Union all geometries and get its centroid"""
    print(shapely.ops.cascaded_union(geoms).centroid)


def overpass_query():
    resp = requests.post(url="https://overpass-api.de/api/interpreter",
                         data="[timeout:30];"
                              "way[amenity]"
                              "(41.886272470886496,12.476906776428223,41.89371621291292,12.507097721099854);"
                              "out body;"
                              ">;"
                              "out body;"
                         )
    if resp.ok:
        return resp.content
    raise RuntimeError("Invalid response from Overpass: " + resp.text)


if __name__ == '__main__':
    analyze(get_geometries(overpass_query()))
