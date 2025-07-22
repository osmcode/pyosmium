# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import json

import pytest

import osmium
import osmium.geom

wkbfab = osmium.geom.WKBFactory()


@pytest.fixture
def node_geom(test_data):

    def _run(factory, data='n1 x-23.3 y28.0'):
        geoms = []

        def _mk_point(node):
            geoms.append(factory.create_point(node))
        handler = osmium.make_simple_handler(node=_mk_point)
        handler.apply_file(test_data(data))

        assert len(geoms) == 1
        return geoms[0]

    return _run


def test_wkb_create_node(node_geom):
    wkb = node_geom(osmium.geom.WKBFactory())
    if wkb.startswith('01'):
        assert wkb.startswith('0101000000')
    else:
        assert wkb.startswith('00')


def test_wkt_create_node(node_geom):
    wkt = node_geom(osmium.geom.WKTFactory())
    assert wkt.startswith('POINT(')


def test_geojson_create_node(node_geom):
    geom = node_geom(osmium.geom.GeoJSONFactory())
    geom = json.loads(geom)
    assert geom['type'], 'Point'


@pytest.fixture
def way_geom(test_data):

    def _run(factory):
        opl = test_data(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3'])
        geoms = []

        def _mk_way(w):
            geoms.append(factory.create_linestring(w))
            geoms.append(factory.create_linestring(
                w, direction=osmium.geom.direction.BACKWARD))
            geoms.append(factory.create_linestring(
                w, use_nodes=osmium.geom.use_nodes.ALL))

        handler = osmium.make_simple_handler(way=_mk_way)
        handler.apply_file(opl, locations=True)

        assert len(geoms) == 3
        return geoms

    return _run


def test_wkb_create_way(way_geom):
    wkbs = way_geom(osmium.geom.WKBFactory())

    for wkb in wkbs:
        if wkb.startswith('01'):
            assert wkb.startswith('0102000000030'), "wkb: " + wkb
        else:
            assert wkb.startswith('00')


def test_wkt_create_way(way_geom):
    wkts = way_geom(osmium.geom.WKTFactory())

    assert all(wkt.startswith('LINESTRING(') for wkt in wkts)


def test_geojson_create_way(way_geom):
    geoms = way_geom(osmium.geom.GeoJSONFactory())

    assert all(json.loads(geom)['type'] == 'LineString' for geom in geoms)


@pytest.fixture
def area_geom(test_data):

    def _run(factory):
        opl = test_data(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w23 Nn1,n2,n3,n1 Tarea=yes'])
        geoms = []

        def _mk_area(a):
            geoms.append(factory.create_multipolygon(a))

        handler = osmium.make_simple_handler(area=_mk_area)
        handler.apply_file(opl, locations=True)

        assert len(geoms) == 1
        return geoms[0]

    return _run


def test_wkb_create_poly(area_geom):
    wkb = area_geom(osmium.geom.WKBFactory())
    if wkb.startswith('01'):
        assert wkb.startswith('010600000001'), "wkb: " + wkb
    else:
        assert wkb.startswith('00')


def test_wkt_create_poly(area_geom):
    wkt = area_geom(osmium.geom.WKTFactory())
    assert wkt.startswith('MULTIPOLYGON(')


def test_geojson_create_poly(area_geom):
    geom = area_geom(osmium.geom.GeoJSONFactory())
    geom = json.loads(geom)
    assert geom['type'] == 'MultiPolygon'


def test_lonlat_to_mercator():
    c = osmium.geom.lonlat_to_mercator(osmium.geom.Coordinates(3.4, -7.3))
    assert c.x == pytest.approx(378486.2686971)
    assert c.y == pytest.approx(-814839.8325696)


def test_mercator_lonlat():
    c = osmium.geom.mercator_to_lonlat(osmium.geom.Coordinates(0.03, 10.2))
    assert c.x == pytest.approx(0.00000026, rel=1e-1)
    assert c.y == pytest.approx(0.00009162, rel=1e-1)


def test_coordinate_from_location():
    c = osmium.geom.Coordinates(osmium.osm.Location(10.0, -3.0))
    assert c.x == pytest.approx(10.0)
    assert c.y == pytest.approx(-3.0)


def test_haversine():
    data = ['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3']

    results = []

    def call_haversine(w):
        results.append(osmium.geom.haversine_distance(w.nodes))

    handler = osmium.make_simple_handler(way=call_haversine)
    handler.apply_buffer('\n'.join(data).encode('utf-8'), 'opl', locations=True)

    assert 1 == len(results)
    assert 268520 == pytest.approx(results[0])


def test_haversine_invalid_object():
    data = ['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1', 'w1 Nn1,n2,n3']

    results = []

    def call_haversine(w):
        results.append(w.nodes)
    handler = osmium.make_simple_handler(way=call_haversine)
    handler.apply_buffer('\n'.join(data).encode('utf-8'), 'opl', locations=True)

    assert results

    with pytest.raises(RuntimeError, match="removed OSM object"):
        osmium.geom.haversine_distance(results[0])


def test_haversine_coordinates():
    dist = osmium.geom.haversine_distance(osmium.geom.Coordinates(0, 0),
                                          osmium.geom.Coordinates(1, 1))
    assert dist == pytest.approx(157293.74877)


def test_haversine_location():
    dist = osmium.geom.haversine_distance(osmium.osm.Location(0, 0),
                                          osmium.osm.Location(1, 1))
    assert dist == pytest.approx(157293.74877)
