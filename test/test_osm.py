from nose.tools import *
import unittest
import os
import sys
from datetime import datetime

if sys.version_info[0] == 3:
    from datetime import timezone

    def mkdate(*args):
        return datetime(*args, tzinfo=timezone.utc)
else:
    def mkdate(*args):
        return datetime(*args)


from helpers import create_osm_file, osmobj, HandlerTestBase

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
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 1)


class TestNodePositiveId(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=-34, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous')]

    class Handler(o.SimpleHandler):
        def node(self, n):
            assert_equals(n.positive_id(), 34)


class TestWayAttributes(HandlerTestBase, unittest.TestCase):

    apply_locations = True

    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=3, lat=1, lon=1),
            osmobj('W', id=1, version=5, changeset=58674, uid=42,
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
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'anonymous')
            assert_equals(n.positive_id(), 1)
            assert_false(n.is_closed())
            assert_false(n.ends_have_same_id())
            assert_false(n.ends_have_same_location())

class TestRelationAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('R', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   members=[('way',1,'')])]

    class Handler(o.SimpleHandler):
        def relation(self, n):
            assert_equals(n.id, 1)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 5)
            assert_equals(n.changeset, 58674)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
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
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
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
            assert_true(oring.is_closed())
            assert_true(oring.ends_have_same_id())
            assert_true(oring.ends_have_same_location())
            assert_equals(len(list(n.inner_rings())), 0)

class TestChangesetAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('C', id=34, created_at="2005-04-09T19:54:13Z",
                num_changes=2, closed_at="2005-04-09T20:54:39Z",
                open="false", min_lon=-0.1465242,
                min_lat=51.5288506, max_lon=-0.1464925,
                max_lat=51.5288620, user="Steve", uid="1")
           ]

    class Handler(o.SimpleHandler):
        def changeset(self,c):
            assert_equals(34, c.id)
            assert_equals(1, c.uid)
            assert_false(c.user_is_anonymous())
            assert_equals("Steve", c.user)
            assert_equals(mkdate(2005, 4, 9, 19, 54, 13), c.created_at)
            assert_equals(mkdate(2005, 4, 9, 20, 54, 39), c.closed_at)
            assert_false(c.open)
            assert_equals(2, c.num_changes)
            assert_equals(0, len(c.tags))
            assert_equals(-1464925, c.bounds.top_right.x)
            assert_equals(515288620, c.bounds.top_right.y)
            assert_equals(-1465242, c.bounds.bottom_left.x)
            assert_equals(515288506, c.bounds.bottom_left.y)
