from nose.tools import *
import unittest
import os
import json

from helpers import create_osm_file, osmobj, HandlerTestBase, HandlerFunction
import osmium as o
import osmium.geom

wkbfab = o.geom.WKBFactory()

class NodeGeomCollector(object):

    def __init__(self, fab):
        self.fab = fab
        self.geoms = []

    def __call__(self, n):
        self.geoms.append(self.fab.create_point(n))

    def run(self):
        data = [osmobj('N', id=1, lat=28.0, lon=-23.3)]
        HandlerFunction(node=self).run(data)

        assert_equals(1, len(self.geoms))
        return self.geoms[0]

def test_wkb_create_node():
    c = NodeGeomCollector(o.geom.WKBFactory())
    wkb = c.run()
    if wkb.startswith('01'):
        assert_true(wkb.startswith('0101000000'))
    else:
        assert_true(wkb.startswith('00'))

def test_wkt_create_node():
    c = NodeGeomCollector(o.geom.WKTFactory())
    wkt = c.run()
    assert_true(wkt.startswith('POINT('))

def test_geojson_create_node():
    c = NodeGeomCollector(o.geom.GeoJSONFactory())
    geom = c.run()
    geom = json.loads(geom)
    assert_equal(geom['type'], 'Point')


class WayGeomCollector(object):

    def __init__(self, fab):
        self.fab = fab
        self.geoms = []

    def __call__(self, w):
        self.geoms.append(self.fab.create_linestring(w))
        self.geoms.append(self.fab.create_linestring(w,
                                           direction=o.geom.direction.BACKWARD))
        self.geoms.append(self.fab.create_linestring(w,
                                           use_nodes=o.geom.use_nodes.ALL))

    def run(self):
        data = [osmobj('N', id=1, lat=0, lon=0),
                osmobj('N', id=2, lat=0, lon=1),
                osmobj('N', id=3, lat=1, lon=0),
                osmobj('W', id=1, nodes = [1,2,3])]
        HandlerFunction(way=self).run(data, apply_locations=True)

        assert_equals(3, len(self.geoms))
        return self.geoms

def test_wkb_create_way():
    c = WayGeomCollector(o.geom.WKBFactory())
    for wkb in c.run():
        if wkb.startswith('01'):
            assert_true(wkb.startswith('0102000000030'), "wkb: " + wkb)
        else:
            assert_true(wkb.startswith('00'))

def test_wkt_create_way():
    c = WayGeomCollector(o.geom.WKTFactory())
    for wkt in c.run():
        assert_true(wkt.startswith('LINESTRING('))

def test_geojson_create_way():
    c = WayGeomCollector(o.geom.GeoJSONFactory())
    for geom in c.run():
        geom = json.loads(geom)
        assert_equal(geom['type'], 'LineString')


class PolyGeomCollector(object):

    def __init__(self, fab):
        self.fab = fab
        self.geoms = []

    def __call__(self, n):
        self.geoms.append(self.fab.create_multipolygon(n))

    def run(self):
        data = [osmobj('N', id=1, lat=0, lon=0),
                osmobj('N', id=2, lat=0, lon=1),
                osmobj('N', id=3, lat=1, lon=0),
                osmobj('W', id=23,
                       nodes = [1,2,3,1], tags = { "area" : "yes" })]
        HandlerFunction(area=self).run(data, apply_locations=True)

        assert_equals(1, len(self.geoms))
        return self.geoms[0]

def test_wkb_create_poly():
    c = PolyGeomCollector(o.geom.WKBFactory())
    wkb = c.run()
    if wkb.startswith('01'):
        assert_true(wkb.startswith('010600000001'), "wkb: " + wkb)
    else:
        assert_true(wkb.startswith('00'))

def test_wkt_create_poly():
    c = PolyGeomCollector(o.geom.WKTFactory())
    wkt = c.run()
    assert_true(wkt.startswith('MULTIPOLYGON('))

def test_geojson_create_poly():
    c = PolyGeomCollector(o.geom.GeoJSONFactory())
    geom = c.run()
    geom = json.loads(geom)
    assert_equal(geom['type'], 'MultiPolygon')


def test_lonlat_to_mercator():
    c = o.geom.lonlat_to_mercator(o.geom.Coordinates(3.4,-7.3))
    assert_almost_equals(c.x, 378486.2686971, 5)
    assert_almost_equals(c.y, -814839.8325696, 5)

def test_mercator_lonlat():
    c = o.geom.mercator_to_lonlat(o.geom.Coordinates(0.03,10.2))
    assert_almost_equals(c.x, 0.00000026, 5)
    assert_almost_equals(c.y, 0.00009162, 5)

def test_coordinate_from_location():
    c = o.geom.Coordinates(o.osm.Location(10.0, -3.0))
    assert_almost_equals(c.x, 10.0)
    assert_almost_equals(c.y, -3.0)

def test_haversine():
    data = [osmobj('N', id=1, lat=0, lon=0),
                osmobj('N', id=2, lat=0, lon=1),
                osmobj('N', id=3, lat=1, lon=0),
                osmobj('W', id=1, nodes = [1,2,3])]

    results = []
    def call_haversine(w):
        results.append(o.geom.haversine_distance(w.nodes))
    HandlerFunction(way=call_haversine).run(data, apply_locations=True)

    assert_equal(1, len(results))
    assert_almost_equals(268520, results[0], 0)
