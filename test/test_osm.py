from nose.tools import *
import unittest
import os
from datetime import datetime

from test_helper import create_osm_file, osmobj, HandlerTestBase

import osmium as o

class TestLocation(unittest.TestCase):

    def test_invalid_location(self):
        loc = o.osm.Location()
        assert_false(loc.valid())

    def test_valid_location(self):
        loc = o.osm.Location(1,10)
        assert_equals(loc.lon, 1, 0.0001)
        assert_equals(loc.lat, 10, 0.00001)
        assert_equals(loc.x, 10000000)
        assert_equals(loc.y, 100000000)

class TestNodeAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous')]

    class Handler(o.SimpleHandler):
        def node(self, n):
            assert_equals(n.id, 1)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 5)
            assert_equals(n.changeset, 58674)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, datetime(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 1)


class TestNodePositiveId(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=-34, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous')]

    class Handler(o.SimpleHandler):
        def node(self, n):
            assert_equals(n.positive_id(), 34)


class TestWayAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('W', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes = [1,2,3])]

    class Handler(o.SimpleHandler):
        def way(self, n):
            assert_equals(n.id, 1)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 5)
            assert_equals(n.changeset, 58674)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, datetime(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 1)

class TestRelationAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('R', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   members=[('W',1,'')])]

    class Handler(o.SimpleHandler):
        def relation(self, n):
            assert_equals(n.id, 1)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 5)
            assert_equals(n.changeset, 58674)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, datetime(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 1)

class TestAreaFromWayAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes = [1,2,3,1], tags = { "area" : "yes" }),
           ]

    class Handler(o.SimpleHandler):
        def area(self, n):
            assert_equals(n.id, 46)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 5)
            assert_equals(n.changeset, 58674)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, datetime(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 46)
            assert_equals(n.orig_id(), 23)
            assert_equals(n.from_way(), True)
            assert_equals(n.is_multipolygon(), False)
            assert_equals(n.num_rings(), (1, 0))
            assert_equals(len(list(n.outer_rings())), 1)
            oring = list(n.outer_rings())[0]
            assert_equals(len(list(oring)), 4)
            assert_equals(set((1,2,3)), set([x.ref for x in oring]))
            assert_equals(len(list(n.inner_rings())), 0)


