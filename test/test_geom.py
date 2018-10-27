from nose.tools import *
import unittest

from helpers import create_osm_file, osmobj, HandlerTestBase
import osmium as o

wkbfab = o.geom.WKBFactory()

class TestWkbCreateNode(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1)]

    class Handler(o.SimpleHandler):
        wkbs = []
        def node(self, n):
            self.wkbs.append(wkbfab.create_point(n))

    def check_result(self):
        assert_equals(1, len(self.handler.wkbs))

class TestWkbCreateWay(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=1, nodes = [1,2,3])]
    apply_locations = True

    class Handler(o.SimpleHandler):
        wkbs = []
        def way(self, w):
            self.wkbs.append(wkbfab.create_linestring(w))
            self.wkbs.append(wkbfab.create_linestring(w, direction=o.geom.direction.BACKWARD))
            self.wkbs.append(wkbfab.create_linestring(w, use_nodes=o.geom.use_nodes.ALL))

    def check_result(self):
        assert_equals(3, len(self.handler.wkbs))

class TestWkbCreatePoly(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23,
                   nodes = [1,2,3,1], tags = { "area" : "yes" }),
           ]
    apply_locations = True

    class Handler(o.SimpleHandler):
        wkbs = []

        def area(self, a):
            self.wkbs.append(wkbfab.create_multipolygon(a))

    def check_result(self):
        assert_equals(1, len(self.handler.wkbs))
