# vim: set fileencoding=utf-8 :
from nose.tools import *
import unittest
import os
from helpers import create_osm_file, create_opl_file, osmobj, check_repr,  mkdate

import osmium as o


class HandlerTestBase:

    apply_locations = False
    apply_idx = 'flex_mem'

    def test_func(self):
        if isinstance(self.data, (list, tuple)):
            fn = create_osm_file(self.data)
        else:
            fn = create_opl_file(self.data)

        try:
            self.handler = self.Handler()
            mir = o.MergeInputReader()
            with open(fn, "rb") as f:
                data = f.read()
                mir.add_buffer(data, format='osm')
            mir.add_file(fn)
            mir.apply(self.handler, idx=self.apply_idx)
        finally:
            os.remove(fn)

        if hasattr(self, "check_result"):
            self.check_result()


class TestAreaFromWayAttributes(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[1, 2, 3, 1], tags={"area": "yes"}),
           ]
    has_ran = False

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
            assert_equals(len(list(n.inner_rings(oring))), 0)
            TestAreaFromWayAttributes.has_ran = True

    def check_result(self):
        assert_equals(self.has_ran, True)


class TestAreaFromMultipolygonRelation(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[1, 2, 3], tags = {}),
            osmobj('W', id=24, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[3, 1], tags={}),
            osmobj('R', id=1, version=3, changeset=7654, uid=42, timestamp='2014-01-31T06:23:35Z', user='Anon',
                   members=[('way', 23, 'outer'), ('way', 24, 'outer')], tags={'type': 'multipolygon'}),
            ]
    has_ran = False

    class Handler(o.SimpleHandler):
        def area(self, n):
            assert_equals(n.id, 3)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 3)
            assert_equals(n.changeset, 7654)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'Anon')
            assert_equals(n.positive_id(), 3)
            assert_equals(n.orig_id(), 1)
            assert_equals(n.from_way(), False)
            assert_equals(n.is_multipolygon(), False)
            assert_equals(n.num_rings(), (1, 0))
            assert_equals(len(list(n.outer_rings())), 1)
            oring = list(n.outer_rings())[0]
            assert_equals(len(list(oring)), 4)
            assert_equals(set((1,2,3)), set([x.ref for x in oring]))
            assert_true(oring.is_closed())
            assert_true(oring.ends_have_same_id())
            assert_true(oring.ends_have_same_location())
            assert_equals(len(list(n.inner_rings(oring))), 0)
            TestAreaFromMultipolygonRelation.has_ran = True

    def check_result(self):
        assert_equals(self.has_ran, True)


class TestAreaFromBoundaryRelation(HandlerTestBase, unittest.TestCase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[1, 2, 3], tags = {}),
            osmobj('W', id=24, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[3, 1], tags={}),
            osmobj('R', id=1, version=3, changeset=7654, uid=42, timestamp='2014-01-31T06:23:35Z', user='Anon',
                   members=[('way', 23, 'outer'), ('way', 24, 'outer')], tags={'type': 'boundary'}),
            ]
    has_ran = False

    class Handler(o.SimpleHandler):
        def area(self, n):
            assert_equals(n.id, 3)
            assert_equals(n.deleted, False)
            assert_equals(n.visible, True)
            assert_equals(n.version, 3)
            assert_equals(n.changeset, 7654)
            assert_equals(n.uid, 42)
            assert_equals(n.user_is_anonymous(), False)
            assert_equals(n.timestamp, mkdate(2014, 1, 31, 6, 23, 35))
            assert_equals(n.user, 'Anon')
            assert_equals(n.positive_id(), 3)
            assert_equals(n.orig_id(), 1)
            assert_equals(n.from_way(), False)
            assert_equals(n.is_multipolygon(), False)
            assert_equals(n.num_rings(), (1, 0))
            assert_equals(len(list(n.outer_rings())), 1)
            oring = list(n.outer_rings())[0]
            assert_equals(len(list(oring)), 4)
            assert_equals(set((1,2,3)), set([x.ref for x in oring]))
            assert_true(oring.is_closed())
            assert_true(oring.ends_have_same_id())
            assert_true(oring.ends_have_same_location())
            assert_equals(len(list(n.inner_rings(oring))), 0)
            TestAreaFromBoundaryRelation.has_ran = True

    def check_result(self):
        assert_equals(self.has_ran, True)
