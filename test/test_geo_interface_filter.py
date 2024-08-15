# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

from helpers import IDCollector

def test_node_geometry(opl_buffer):
    fp = o.FileProcessor(opl_buffer("n23 x3 y4"))\
          .with_filter(o.filter.GeoInterfaceFilter())

    for n in fp:
        assert n.__geo_interface__ == \
               dict(type='Feature', properties={},
                    geometry=dict(type='Point',
                                  coordinates=(pytest.approx(3), pytest.approx(4))))
        break
    else:
        assert False


def test_way_geometry(opl_buffer):
    data = """\
            n1 x0.001 y0
            n2 x0.002 y0
            w1 Nn1,n2
           """

    fp = o.FileProcessor(opl_buffer(data))\
          .with_locations()\
          .with_filter(o.filter.EntityFilter(o.osm.WAY))\
          .with_filter(o.filter.GeoInterfaceFilter())

    for w in fp:
        assert w.__geo_interface__ == \
                dict(type='Feature', properties={},
                    geometry=dict(type='LineString',
                                  coordinates=[[pytest.approx(0.001), pytest.approx(0)],
                                               [pytest.approx(0.002), pytest.approx(0)]]))
        break
    else:
        assert False


def test_area_geometry(opl_buffer):
    data = """\
            n1 x0.001 y0
            n2 x0.002 y0
            n3 x0.001 y0.001
            w1 Nn1,n2,n3
            w2 Nn3,n1
            r1 Ttype=multipolygon Mw1@,w2@
           """

    fp = o.FileProcessor(opl_buffer(data))\
          .with_areas()\
          .with_filter(o.filter.GeoInterfaceFilter())

    for r in fp:
        print(r)
        if r.is_area():
            assert r.__geo_interface__ == \
                    dict(type='Feature', properties={},
                        geometry=dict(type='MultiPolygon',
                                      coordinates=[[[[pytest.approx(0.001), pytest.approx(0)],
                                                     [pytest.approx(0.002), pytest.approx(0)],
                                                     [pytest.approx(0.001), pytest.approx(0.001)],
                                                     [pytest.approx(0.001), pytest.approx(0)]]]]))
            break
    else:
        assert False


def test_area_geometry_without_drop(opl_reader):
    data = """\
            n1 x0.001 y0
            n2 x0.002 y0
            n3 
           """

    ids = IDCollector()
    o.apply(opl_reader(data), o.filter.GeoInterfaceFilter(), ids)

    assert ids.nodes == [1, 2]

    ids = IDCollector()
    o.apply(opl_reader(data), o.filter.GeoInterfaceFilter(drop_invalid_geometries=False), ids)

    assert ids.nodes == [1, 2, 3]



def test_property_tag_filter(opl_buffer):
    data = """\
           n1 x0.001 y0 Ta=1,b=1,c=1,d=1
           n2 x0.001 y0 Tx=1
           n3 x0.001 y0 Ta=1,c=3
           """

    fp = o.FileProcessor(opl_buffer(data))\
          .with_filter(o.filter.GeoInterfaceFilter(tags=['a', 'b']))

    count = 0
    for obj in fp:
        count += 1
        for k in obj.__geo_interface__['properties']:
            assert k in ['a', 'b']

    assert count == 3
