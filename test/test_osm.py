# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import re
from itertools import count
import pytest

from helpers import mkdate

import osmium


def apply_simple(handler, data, locations, tmp_path):
    handler.apply_buffer(data.encode('utf-8'), 'opl', locations=locations)


def apply_with_merge(handler, data, locations, tmp_path):
    mir = osmium.MergeInputReader()

    mir.add_buffer(data.encode('utf-8'), format='opl')

    fn = tmp_path / 'temp.opl'
    fn.write_text(data)
    mir.add_file(str(fn))

    mir.apply(handler, idx='flex_mem' if locations else '')


def _make_importer_factory(apply_func, tmp_path, to_opl):

    def _run(data, node=None, way=None, relation=None, area=None, changeset=None, locations=False):
        cnt = count()

        def _m(func):
            if func is None:
                return None

            def _inner(obj):
                next(cnt)
                func(obj)
            return _inner

        handler = osmium.make_simple_handler(node=_m(node), way=_m(way),
                                             relation=_m(relation), area=_m(area),
                                             changeset=_m(changeset))
        apply_func(handler, to_opl(data), locations, tmp_path)

        return next(cnt)

    return _run


@pytest.fixture(params=[apply_simple, apply_with_merge])
def test_importer(request, tmp_path, to_opl):
    return _make_importer_factory(request.param, tmp_path, to_opl)


@pytest.fixture(params=[apply_simple])
def area_importer(request, tmp_path, to_opl):
    return _make_importer_factory(request.param, tmp_path, to_opl)


def test_invalid_location():
    loc = osmium.osm.Location()
    assert not loc.valid()
    assert str(loc) == 'invalid'
    assert repr(loc) == 'osmium.osm.Location()'

    with pytest.raises(osmium.InvalidLocationError):
        loc.lat
    with pytest.raises(osmium.InvalidLocationError):
        loc.lon
    # these two don't raise an exception
    assert loc.lat_without_check() is not None
    assert loc.lon_without_check() is not None


def test_valid_location():
    loc = osmium.osm.Location(-1, 10)
    assert loc.lon == pytest.approx(-1)
    assert loc.lat == pytest.approx(10)
    assert loc.x == -10000000
    assert loc.y == 100000000
    assert re.fullmatch('-1.0*/10.0*', str(loc))
    assert repr(loc) == 'osmium.osm.Location(x=-10000000, y=100000000)'


@pytest.mark.parametrize('attrname', ['id', 'deleted', 'visible',
                                      'changeset', 'uid', 'timestamp', 'user',
                                      'tags'])
@pytest.mark.parametrize('osmdata', ['n1 v5 c58674 uänonymous',
                                     'w34 Nn34',
                                     'r45 Tfoo=rte'])
def test_object_attribute_do_not_overwrite(opl_buffer, attrname, osmdata):
    for n in osmium.FileProcessor(opl_buffer(osmdata)):
        with pytest.raises(AttributeError):
            setattr(n, attrname, 3)


def test_node_attributes(opl_buffer):
    node_data = 'n1 v5 c58674 t2014-01-31T06:23:35Z i42 uänonymous'

    for n in osmium.FileProcessor(opl_buffer(node_data)):
        assert n.deleted is False
        assert n.visible is True
        assert n.version == 5
        assert n.changeset == 58674
        assert n.uid == 42
        assert n.user_is_anonymous() is False
        assert n.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
        assert n.user == u'änonymous'
        assert n.positive_id() == 1
        assert n.is_node()
        assert n.is_way() is False
        assert n.type_str() == 'n'
        assert str(n) == 'n1: location=invalid tags={}'
        assert repr(n) == 'osmium.osm.Node(id=1, deleted=False, visible=True, ' \
                          'version=5, changeset=58674, uid=42, ' \
                          'timestamp=datetime.datetime(2014, 1, 31, 6, 23, 35,' \
                          ' tzinfo=datetime.timezone.utc), ' \
                          "user='änonymous', tags=osmium.osm.TagList({}), " \
                          'location=osmium.osm.Location())'
        break
    else:
        assert False


def test_node_location(opl_buffer):
    for n in osmium.FileProcessor(opl_buffer("n1 x4 y5")):
        assert n.lat == 5.0
        assert n.lon == 4.0


@pytest.mark.parametrize('nid', (23, 0, -68373, 17179869418, -17179869417))
def test_node_positive_id(opl_buffer, nid):
    for n in osmium.FileProcessor(opl_buffer(f"n{nid} v5 c58674")):
        assert n.id == nid
        assert n.positive_id() == abs(nid)
        break
    else:
        assert False


def test_way_attributes(test_importer):
    def way(o):
        assert o.id == 1
        assert o.deleted is False
        assert o.visible is True
        assert o.version == 5
        assert o.changeset == 58674
        assert o.uid == 42
        assert o.user_is_anonymous() is False
        assert o.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
        assert o.user == 'anonymous'
        assert o.positive_id() == 1
        assert o.is_way()
        assert o.type_str() == 'w'
        assert not o.is_closed()
        assert not o.ends_have_same_id()
        assert not o.ends_have_same_location()

        assert str(o) == 'w1: nodes=[1@0.0000000/0.0000000,2,3@1.0000000/1.0000000] tags={}'
        assert repr(o) == 'osmium.osm.Way(id=1, deleted=False, visible=True, ' \
                          'version=5, changeset=58674, uid=42, ' \
                          'timestamp=datetime.datetime(2014, 1, 31, 6, 23, 35,' \
                          ' tzinfo=datetime.timezone.utc), ' \
                          "user='anonymous', tags=osmium.osm.TagList({}), " \
                          'nodes=osmium.osm.WayNodeList([osmium.osm.NodeRef(ref=1,' \
                          ' location=osmium.osm.Location(x=0, y=0)), ' \
                          'osmium.osm.NodeRef(ref=2, location=osmium.osm.Location()), ' \
                          'osmium.osm.NodeRef(ref=3, location=osmium.osm.Location(' \
                          'x=10000000, y=10000000))]))'

        assert str(o.nodes) == '[1@0.0000000/0.0000000,2,3@1.0000000/1.0000000]'
        assert repr(o.nodes) == 'osmium.osm.WayNodeList([osmium.osm.NodeRef(ref=1, ' \
                                'location=osmium.osm.Location(x=0, y=0)), '\
                                'osmium.osm.NodeRef(ref=2, location=osmium.osm.Location()), '\
                                'osmium.osm.NodeRef(ref=3, location=osmium.osm.Location(' \
                                'x=10000000, y=10000000))])'

    assert 1 == test_importer(['n1 x0 y0', 'n3 x1 y1',
                               'w1 v5 c58674 t2014-01-31T06:23:35Z i42 uanonymous Nn1,n2,n3'],
                              way=way, locations=True)


def test_way_attribute_do_not_overwrite(opl_buffer):
    data = """\
           w34 Nn34
           """
    for w in osmium.FileProcessor(opl_buffer(data)):
        with pytest.raises(AttributeError):
            w.nodes = [3, 4, 5]


def test_relation_attributes(test_importer):
    def relation(o):
        assert o.id == 1
        assert o.deleted is False
        assert o.visible is True
        assert o.version == 5
        assert o.changeset == 58674
        assert o.uid == 42
        assert o.user_is_anonymous() is False
        assert o.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
        assert o.user == ' anonymous'
        assert o.positive_id() == 1
        assert o.is_relation()
        assert o.type_str() == 'r'

        assert str(o) == 'r1: members=[w1], tags={}'
        assert repr(o) == 'osmium.osm.Relation(id=1, deleted=False, visible=True, ' \
                          'version=5, changeset=58674, uid=42, ' \
                          'timestamp=datetime.datetime(2014, 1, 31, 6, 23, 35,' \
                          ' tzinfo=datetime.timezone.utc), ' \
                          "user=' anonymous', tags=osmium.osm.TagList({}), " \
                          'members=osmium.osm.RelationMemberList(' \
                          "[osmium.osm.RelationMember(ref=1, type='w', role='')]))"

        assert str(o.members) == '[w1]'
        assert repr(o.members) == 'osmium.osm.RelationMemberList('\
                                  "[osmium.osm.RelationMember(ref=1, type='w', role='')])"

    assert 1 == test_importer('r1 v5 c58674 t2014-01-31T06:23:35Z i42 u%20%anonymous Mw1@',
                              relation=relation)


def test_relation_attribute_do_not_overwrite(opl_buffer):
    data = """\
           r34 Mn23@,w34@
           """
    for r in osmium.FileProcessor(opl_buffer(data)):
        with pytest.raises(AttributeError):
            r.members = [3, 4, 5]


def test_area_from_way_attributes(area_importer):
    def area(o):
        assert o.id == 46
        assert o.deleted is False
        assert o.visible is True
        assert o.version == 5
        assert o.changeset == 58674
        assert o.uid == 42
        assert o.user_is_anonymous() is False
        assert o.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
        assert o.user == 'anonymous'
        assert o.positive_id() == 46
        assert o.orig_id() == 23
        assert o.from_way() is True
        assert o.is_area()
        assert o.type_str() == 'a'
        assert o.is_multipolygon() is False
        assert o.num_rings() == (1, 0)
        assert len(list(o.outer_rings())) == 1

        oring = next(o.outer_rings())
        assert len(list(oring)) == 4
        assert {1, 2, 3} == {x.ref for x in oring}
        assert oring.is_closed()
        assert oring.ends_have_same_id()
        assert oring.ends_have_same_location()
        assert len(list(o.inner_rings(oring))) == 0

    assert 1 == area_importer(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1',
                               'w23 v5 c58674 t2014-01-31T06:23:35Z i42 '
                               'uanonymous Nn1,n2,n3,n1 Tarea=yes'],
                              area=area)


@pytest.mark.parametrize('mptype', ('multipolygon', 'boundary'))
def test_area_from_multipolygon_relation(area_importer, mptype):
    def area(o):
        assert o.id == 3
        assert o.deleted is False
        assert o.visible is True
        assert o.version == 3
        assert o.changeset == 7654
        assert o.uid == 42
        assert o.user_is_anonymous() is False
        assert o.timestamp == mkdate(2014, 1, 31, 6, 23, 35)
        assert o.user == 'Anon'
        assert o.positive_id() == 3
        assert o.orig_id() == 1
        assert o.from_way() is False
        assert o.is_multipolygon() is False
        assert o.num_rings() == (1, 0)
        assert len(list(o.outer_rings())) == 1

        oring = next(o.outer_rings())
        assert len(list(oring)) == 4
        assert {1, 2, 3} == {x.ref for x in oring}
        assert oring.is_closed()
        assert oring.ends_have_same_id()
        assert oring.ends_have_same_location()
        assert len(list(o.inner_rings(oring))) == 0

    assert 1 == area_importer(['n1 x0 y0', 'n2 x1 y0', 'n3 x0 y1',
                               'w23 Nn1,n2,n3', 'w24 Nn3,n1',
                               'r1 v3 c7654 t2014-01-31T06:23:35Z i42 uAnon '
                               f"Mw23@outer,w24@outer Ttype={mptype}"],
                              area=area)


def test_changeset_attributes(area_importer):
    def changeset(c):
        assert 34 == c.id
        assert 1 == c.uid
        assert not c.user_is_anonymous()
        assert "Steve" == c.user
        assert mkdate(2005, 4, 9, 19, 54, 13) == c.created_at
        assert mkdate(2005, 4, 9, 20, 54, 39) == c.closed_at
        assert not c.open
        assert 2 == c.num_changes
        assert 0 == len(c.tags)
        assert -1464925 == c.bounds.top_right.x
        assert 515288620 == c.bounds.top_right.y
        assert -1465242 == c.bounds.bottom_left.x
        assert 515288506 == c.bounds.bottom_left.y
        assert c.type_str() == 'c'
        assert str(c) == 'c34: closed_at=2005-04-09 20:54:39+00:00, '\
                         'bounds=(-0.1465242/51.5288506 -0.1464925/51.5288620), tags={}'
        assert repr(c) == 'osmium.osm.Changeset(id=34, uid=1, ' \
                          'created_at=datetime.datetime(2005, 4, 9, 19, 54, 13,' \
                          ' tzinfo=datetime.timezone.utc), ' \
                          'closed_at=datetime.datetime(2005, 4, 9, 20, 54, 39,' \
                          ' tzinfo=datetime.timezone.utc), '\
                          'open=False, num_changes=2, '\
                          'bounds=osmium.osm.Box(bottom_left=' \
                          'osmium.osm.Location(x=-1465242, y=515288506), ' \
                          'top_right=osmium.osm.Location(x=-1464925, y=515288620)), '\
                          "user='Steve', tags=osmium.osm.TagList({}))"

    assert 1 == area_importer('c34 k2 s2005-04-09T19:54:13Z e2005-04-09T20:54:39Z '
                              'd34 i1 uSteve x-0.1465242 y51.5288506 X-0.1464925 Y51.5288620',
                              changeset=changeset)


def test_entity_operations():
    assert not osmium.osm.NOTHING
    assert osmium.osm.NODE

    assert osmium.osm.AREA | osmium.osm.NODE | osmium.osm.WAY | osmium.osm.RELATION \
           == osmium.osm.OBJECT
    assert osmium.osm.ALL & osmium.osm.RELATION == osmium.osm.RELATION

    assert ~osmium.osm.CHANGESET == osmium.osm.OBJECT
