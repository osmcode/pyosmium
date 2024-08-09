# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2024 Sarah Hoffmann.
import json

import pytest

import osmium as o
import osmium.geom

wkbfab = o.geom.WKBFactory()

@pytest.fixture
def node_geom(test_data):

    def _run(factory, data='n1 x-23.3 y28.0'):
        geoms = []
        def _mk_point(node):
            geoms.append(factory.create_point(node))
        handler = o.make_simple_handler(node=_mk_point)
        handler.apply_file(test_data(data))

        assert len(geoms) == 1
        return geoms[0]

    return _run


def test_wkb_create_node(node_geom):
    wkb = node_geom(o.geom.WKBFactory())
    if wkb.startswith('01'):
        assert wkb.startswith('0101000000')
    else:
        assert wkb.startswith('00')


def test_wkt_create_node(node_geom):
    wkt = node_geom(o.geom.WKTFactory())
    assert wkt.startswith('POINT(')


def test_geojson_create_node(node_geom):
    geom = node_geom(o.geom.GeoJSONFactory())
    geom = json.loads(geom)
    assert geom['type'], 'Point'


@pytest.fixture
def way_geom(test_data):

    def _run(factory):
        opl = test_data(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3'])
        geoms = []
        def _mk_way(w):
            geoms.append(factory.create_linestring(w))
            geoms.append(factory.create_linestring(w,
                                          direction=o.geom.direction.BACKWARD))
            geoms.append(factory.create_linestring(w,
                                          use_nodes=o.geom.use_nodes.ALL))

        handler = o.make_simple_handler(way=_mk_way)
        handler.apply_file(opl, locations=True)

        assert len(geoms) == 3
        return geoms

    return _run


def test_wkb_create_way(way_geom):
    wkbs = way_geom(o.geom.WKBFactory())

    for wkb in wkbs:
        if wkb.startswith('01'):
            assert wkb.startswith('0102000000030'), "wkb: " + wkb
        else:
            assert wkb.startswith('00')

def test_wkt_create_way(way_geom):
    wkts = way_geom(o.geom.WKTFactory())

    assert all(wkt.startswith('LINESTRING(') for wkt in wkts)

def test_geojson_create_way(way_geom):
    geoms = way_geom(o.geom.GeoJSONFactory())

    assert all(json.loads(geom)['type'] == 'LineString' for geom in geoms)


@pytest.fixture
def area_geom(test_data):

    def _run(factory):
        opl = test_data(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w23 Nn1,n2,n3,n1 Tarea=yes'])
        geoms = []
        def _mk_area(a):
            geoms.append(factory.create_multipolygon(a))

        handler = o.make_simple_handler(area=_mk_area)
        handler.apply_file(opl, locations=True)

        assert len(geoms) == 1
        return geoms[0]

    return _run


def test_wkb_create_poly(area_geom):
    wkb = area_geom(o.geom.WKBFactory())
    if wkb.startswith('01'):
        assert wkb.startswith('010600000001'), "wkb: " + wkb
    else:
        assert wkb.startswith('00')


def test_wkt_create_poly(area_geom):
    wkt = area_geom(o.geom.WKTFactory())
    assert wkt.startswith('MULTIPOLYGON(')


def test_geojson_create_poly(area_geom):
    geom = area_geom(o.geom.GeoJSONFactory())
    geom = json.loads(geom)
    assert geom['type'] == 'MultiPolygon'


def test_lonlat_to_mercator():
    c = o.geom.lonlat_to_mercator(o.geom.Coordinates(3.4,-7.3))
    assert c.x == pytest.approx(378486.2686971)
    assert c.y == pytest.approx(-814839.8325696)


def test_mercator_lonlat():
    c = o.geom.mercator_to_lonlat(o.geom.Coordinates(0.03,10.2))
    assert c.x == pytest.approx(0.00000026, rel=1e-1)
    assert c.y == pytest.approx(0.00009162, rel=1e-1)


def test_coordinate_from_location():
    c = o.geom.Coordinates(o.osm.Location(10.0, -3.0))
    assert c.x == pytest.approx(10.0)
    assert c.y == pytest.approx(-3.0)


def test_haversine():
    data = ['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3']

    results = []
    def call_haversine(w):
        results.append(o.geom.haversine_distance(w.nodes))

    handler = o.make_simple_handler(way=call_haversine)
    handler.apply_buffer('\n'.join(data).encode('utf-8'), 'opl', locations=True)

    assert 1 == len(results)
    assert 268520 == pytest.approx(results[0])


def test_haversine_invalid_object():
    data = ['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3']

    results = []
    def call_haversine(w):
        results.append(w.nodes)
    handler = o.make_simple_handler(way=call_haversine)
    handler.apply_buffer('\n'.join(data).encode('utf-8'), 'opl', locations=True)

    assert results

    with pytest.raises(RuntimeError, match="removed OSM object"):
        o.geom.haversine_distance(results[0])


def test_haversine_coordinates():
    dist = o.geom.haversine_distance(o.geom.Coordinates(0,0), o.geom.Coordinates(1,1))
    assert dist == pytest.approx(157293.74877)


def test_haversine_location():
    dist = o.geom.haversine_distance(o.osm.Location(0,0), o.osm.Location(1,1))
    assert dist == pytest.approx(157293.74877)
