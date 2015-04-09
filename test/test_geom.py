from nose.tools import *
import unittest

from helpers import create_osm_file, osmobj, HandlerTestBase
import osmium as o

wkbfab = o.geom.WKBFactory()

class TestWkbCreateNode(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1)]

    class Handler(o.SimpleHandler):
        def node(self, n):
            wkb = wkbfab.create_point(n)

class TestWkbCreateWay(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=1, nodes = [1,2,3])]
    apply_locations = True

    class Handler(o.SimpleHandler):
        def way(self, w):
            wkb = wkbfab.create_linestring(w)
            wkb = wkbfab.create_linestring(w, direction=o.geom.direction.BACKWARD)
            wkb = wkbfab.create_linestring(w, use_nodes=o.geom.use_nodes.ALL)

class TestWkbCreatePoly(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23,
                   nodes = [1,2,3,1], tags = { "area" : "yes" }),
           ]
    apply_locations = True

    class Handler(o.SimpleHandler):
        def area(self, a):
            wkb = wkbfab.create_multipolygon(a)
