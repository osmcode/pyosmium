# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
import pytest

from helpers import create_osm_file, osmobj, check_repr, HandlerTestBase,\
                    HandlerTestWithMergeInput, mkdate, ExecutedHandler

import osmium as o

def test_invalid_location():
    loc = o.osm.Location()
    assert not loc.valid()
    assert check_repr(loc)
    with pytest.raises(o.InvalidLocationError):
        lat = loc.lat
    with pytest.raises(o.InvalidLocationError):
        lon = loc.lon
    # these two don't raise an exception
    lat = loc.lat_without_check()
    lon = loc.lon_without_check()

def test_valid_location():
    loc = o.osm.Location(1,10)
    assert loc.lon == pytest.approx(1)
    assert loc.lat == pytest.approx(10)
    assert loc.x == 10000000
    assert loc.y == 100000000
    assert check_repr(loc)


class TestNodeAttributes(HandlerTestWithMergeInput):
    data = [osmobj('N', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user=u'änonymous')]

    class Handler(ExecutedHandler):
        def node(self, n):
            assert n.id == 1
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 5
            assert n.changeset == 58674
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == u'änonymous'
            assert n.positive_id() == 1
            assert check_repr(n)
            self.has_run = True


class TestNodePositiveId(HandlerTestWithMergeInput):
    data = [osmobj('N', id=-34, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous')]

    class Handler(ExecutedHandler):
        def node(self, n):
            assert n.positive_id() == 34
            self.has_run = True

class TestNodeLargeId(HandlerTestWithMergeInput):
    data = [osmobj('N', id=17179869418, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous')]

    class Handler(ExecutedHandler):
        def node(self, n):
            assert n.id == 17179869418
            self.has_run = True


class TestWayAttributes(HandlerTestWithMergeInput):

    apply_locations = True

    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=3, lat=1, lon=1),
            osmobj('W', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes = [1,2,3])]

    class Handler(ExecutedHandler):
        def way(self, n):
            assert n.id == 1
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 5
            assert n.changeset == 58674
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == 'anonymous'
            assert n.positive_id() == 1
            assert not n.is_closed()
            assert not n.ends_have_same_id()
            assert not n.ends_have_same_location()
            assert check_repr(n)
            assert check_repr(n.nodes)
            self.has_run = True

class TestRelationAttributes(HandlerTestWithMergeInput):
    data = [osmobj('R', id=1, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user=' anonymous',
                   members=[('way',1,'')])]

    class Handler(ExecutedHandler):
        def relation(self, n):
            assert n.id == 1
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 5
            assert n.changeset == 58674
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == ' anonymous'
            assert n.positive_id() == 1
            assert check_repr(n)
            assert check_repr(n.members)
            self.has_run = True

class TestAreaFromWayAttributes(HandlerTestBase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes = [1,2,3,1], tags = { "area" : "yes" }),
           ]

    class Handler(ExecutedHandler):
        def area(self, n):
            assert n.id == 46
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 5
            assert n.changeset == 58674
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == 'anonymous'
            assert n.positive_id() == 46
            assert n.orig_id() == 23
            assert n.from_way() == True
            assert n.is_multipolygon() == False
            assert n.num_rings() == (1, 0)
            assert len(list(n.outer_rings())) == 1
            oring = list(n.outer_rings())[0]
            assert len(list(oring)) == 4
            assert set((1,2,3)) == set([x.ref for x in oring])
            assert oring.is_closed()
            assert oring.ends_have_same_id()
            assert oring.ends_have_same_location()
            assert len(list(n.inner_rings(oring))) == 0
            self.has_run = True

class TestAreaFromMultipolygonRelation(HandlerTestBase):
    data = [osmobj('N', id=1, lat=0, lon=0),
            osmobj('N', id=2, lat=0, lon=1),
            osmobj('N', id=3, lat=1, lon=0),
            osmobj('W', id=23, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes = [1, 2, 3], tags = {}),
            osmobj('W', id=24, version=5, changeset=58674, uid=42,
                   timestamp='2014-01-31T06:23:35Z', user='anonymous',
                   nodes=[3, 1], tags={}),
            osmobj('R', id=1, version=3, changeset=7654, uid=42, timestamp='2014-01-31T06:23:35Z', user='Anon',
                   members=[('way', 23, 'outer'), ('way', 24, 'outer')], tags={'type': 'multipolygon'}),
            ]

    class Handler(ExecutedHandler):
        def area(self, n):
            assert n.id == 3
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 3
            assert n.changeset == 7654
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == 'Anon'
            assert n.positive_id() == 3
            assert n.orig_id() == 1
            assert n.from_way() == False
            assert n.is_multipolygon() == False
            assert n.num_rings() == (1, 0)
            assert len(list(n.outer_rings())) == 1
            oring = list(n.outer_rings())[0]
            assert len(list(oring)) == 4
            assert set((1,2,3)) == set([x.ref for x in oring])
            assert oring.is_closed()
            assert oring.ends_have_same_id()
            assert oring.ends_have_same_location()
            assert len(list(n.inner_rings(oring))) == 0
            self.has_run = True

class TestAreaFromBoundaryRelation(HandlerTestBase):
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

    class Handler(ExecutedHandler):
        def area(self, n):
            assert n.id == 3
            assert n.deleted == False
            assert n.visible == True
            assert n.version == 3
            assert n.changeset == 7654
            assert n.uid == 42
            assert n.user_is_anonymous() == False
            assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
            assert n.user == 'Anon'
            assert n.positive_id() == 3
            assert n.orig_id() == 1
            assert n.from_way() == False
            assert n.is_multipolygon() == False
            assert n.num_rings() == (1, 0)
            assert len(list(n.outer_rings())) == 1
            oring = list(n.outer_rings())[0]
            assert len(list(oring)) == 4
            assert set((1,2,3)) == set([x.ref for x in oring])
            assert oring.is_closed()
            assert oring.ends_have_same_id()
            assert oring.ends_have_same_location()
            assert len(list(n.inner_rings(oring))) == 0
            self.has_run = True


class TestChangesetAttributes(HandlerTestBase):
    data = [osmobj('C', id=34, created_at="2005-04-09T19:54:13Z",
                num_changes=2, closed_at="2005-04-09T20:54:39Z",
                open="false", min_lon=-0.1465242,
                min_lat=51.5288506, max_lon=-0.1464925,
                max_lat=51.5288620, user="Steve", uid="1")
           ]

    class Handler(ExecutedHandler):
        def changeset(self,c):
            assert 34 == c.id
            assert 1 == c.uid
            assert not c.user_is_anonymous()
            assert "Steve" == c.user
            assert mkdate(2005, 4, 9, 19, 54, 13), c.created_at
            assert mkdate(2005, 4, 9, 20, 54, 39), c.closed_at
            assert not c.open
            assert 2 == c.num_changes
            assert 0 == len(c.tags)
            assert -1464925 == c.bounds.top_right.x
            assert 515288620 == c.bounds.top_right.y
            assert -1465242 == c.bounds.bottom_left.x
            assert 515288506 == c.bounds.bottom_left.y
            assert check_repr(c)
            self.has_run = True
