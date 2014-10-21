from nose.tools import *
import unittest
import os

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
            assert_equals(str(n.timestamp), '2014-01-31T06:23:35Z')
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), True)

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
            assert_equals(str(n.timestamp), '2014-01-31T06:23:35Z')
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), True)

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
            assert_equals(str(n.timestamp), '2014-01-31T06:23:35Z')
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), True)


