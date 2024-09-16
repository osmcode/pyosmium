# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
from contextlib import contextmanager
from collections import OrderedDict
import uuid

import pytest

import osmium as o

from helpers import mkdate


@pytest.fixture
def test_writer(tmp_path):
    @contextmanager
    def _WriteExpect(filename, expected):
        with o.SimpleWriter(str(filename), 1024*1024) as writer:
            yield writer

        assert filename.read_text().strip() == expected


    def _create(expected):
        filename = tmp_path / (str(uuid.uuid4()) + '.opl')
        return _WriteExpect(filename, expected)

    return _create


class O:
    def __init__(self, **params):
        for k,v in params.items():
            setattr(self, k, v)


@pytest.mark.parametrize('osmobj, out_attr', [
      (O(id=None), '0 v0 dV c0 t i0 u T'),
      (O(visible=None), '0 v0 dV c0 t i0 u T'),
      (O(version=None), '0 v0 dV c0 t i0 u T'),
      (O(uid=None), '0 v0 dV c0 t i0 u T'),
      (O(user=None), '0 v0 dV c0 t i0 u T'),
      (O(timestamp=None), '0 v0 dV c0 t i0 u T'),
      (O(id=1), '1 v0 dV c0 t i0 u T'),
      (O(id=-99), '-99 v0 dV c0 t i0 u T'),
      (O(visible=True), '0 v0 dV c0 t i0 u T'),
      (O(visible=False), '0 v0 dD c0 t i0 u T'),
      (O(version=23), '0 v23 dV c0 t i0 u T'),
      (O(user="Schmidt"), '0 v0 dV c0 t i0 uSchmidt T'),
      (O(user=""), '0 v0 dV c0 t i0 u T'),
      (O(uid=987), '0 v0 dV c0 t i987 u T'),
      (O(timestamp='2012-04-14T20:58:35Z'), '0 v0 dV c0 t2012-04-14T20:58:35Z i0 u T'),
      (O(timestamp=mkdate(2009, 4, 14, 20, 58, 35)), '0 v0 dV c0 t2009-04-14T20:58:35Z i0 u T'),
      (O(timestamp='1970-01-01T00:00:01Z'), '0 v0 dV c0 t1970-01-01T00:00:01Z i0 u T')
    ])
class TestWriteAttributes:
    def test_node_simple_attr(self, test_writer, osmobj, out_attr):
        with test_writer('n' + out_attr + ' x y') as w:
            w.add_node(osmobj)

    def test_way_simple_attr(self, test_writer, osmobj, out_attr):
        with test_writer('w' + out_attr + ' N') as w:
            w.add_way(osmobj)

    def test_relation_simple_attr(self, test_writer, osmobj, out_attr):
        with test_writer('r' + out_attr + ' M') as w:
            w.add_relation(osmobj)


@pytest.mark.parametrize('tags,out', [
     (None, 'T'),
     ([], 'T'),
     ({}, 'T'),
     ((("foo", "bar"), ), 'Tfoo=bar'),
     ((("foo", "bar"), ("2", "1")), 'Tfoo=bar,2=1'),
     ({'test' : 'drive'}, 'Ttest=drive'),
     (OrderedDict((('a', 'b'), ('c', '3'))), 'Ta=b,c=3'),
    ])
class TestWriteTags:
    def test_node_tags(self, test_writer, tags, out):
        with test_writer('n0 v0 dV c0 t i0 u ' + out + ' x y') as w:
            w.add_node(O(tags=tags))

    def test_way_tags(self, test_writer, tags, out):
        with test_writer('w0 v0 dV c0 t i0 u ' + out + ' N') as w:
            w.add_way(O(tags=tags))

    def test_relation_tags(self, test_writer, tags, out):
        with test_writer('r0 v0 dV c0 t i0 u ' + out + ' M') as w:
            w.add_relation(O(tags=tags))


@pytest.mark.parametrize("location,out", [((1.1234561, 0.1234561), 'x1.1234561 y0.1234561'),
                                          ((30.46, 50.37), 'x30.46 y50.37'),
                                          (None, 'x y')])
def test_location(test_writer, location, out):
    with test_writer('n0 v0 dV c0 t i0 u T ' + out) as w:
        w.add_node(O(location=location))


def test_location_generic(test_writer):
    with test_writer('n0 v0 dV c0 t i0 u T x30.46 y50.37') as w:
        w.add_node(O(location=(30.46, 50.37)))


def test_node_list(test_writer):
    with test_writer('w0 v0 dV c0 t i0 u T Nn1,n2,n3,n-4') as w:
        w.add_way(O(nodes=(1, 2, 3, -4)))


def test_node_list_generic(test_writer):
    with test_writer('w0 v0 dV c0 t i0 u T Nn1,n2,n3,n-4') as w:
        w.add(O(nodes=(1, 2, 3, -4)))


def test_node_list_none(test_writer):
    with test_writer('w0 v0 dV c0 t i0 u T N') as w:
        w.add_way(O(nodes=None))


def test_relation_members(test_writer):
    with test_writer('r0 v0 dV c0 t i0 u T Mn34@foo,r200@,w1111@x') as w:
        w.add_relation(O(members=(('n', 34, 'foo'),
                                  ('r', 200, ''),
                                  ('w', 1111, 'x')
                                 )))


def test_relation_members_generic(test_writer):
    with test_writer('r0 v0 dV c0 t i0 u T Mn34@foo,r200@,w1111@x') as w:
        w.add(O(members=(('n', 34, 'foo'),
                         ('r', 200, ''),
                         ('w', 1111, 'x')
                        )))


def test_relation_members_None(test_writer):
    with test_writer('r0 v0 dV c0 t i0 u T M') as w:
        w.add_relation(O(members=None))


def test_node_object(test_writer, simple_handler):
    node_opl = 'n235 v1 dV c0 t i0 u Telephant=yes x98.7 y-3.45'

    with test_writer(node_opl) as w:
        simple_handler(node_opl, node=lambda o: w.add_node(o))


def test_node_object_generic(test_writer, simple_handler):
    node_opl = 'n235 v1 dV c0 t i0 u Telephant=yes x98.7 y-3.45'

    with test_writer(node_opl) as w:
        simple_handler(node_opl, node=lambda o: w.add(o))


def test_location_object(test_writer, simple_handler):
    node_opl = 'n235 v1 dV c0 t i0 u Telephant=yes x98.7 y-3.45'

    with test_writer('n0 v0 dV c0 t i0 u T x98.7 y-3.45') as w:
        simple_handler(node_opl, node=lambda o: w.add_node(O(location=o.location)))


def test_tag_object(test_writer, simple_handler):
    node_opl = 'n235 v1 dV c0 t i0 u Telephant=yes x98.7 y-3.45'

    with test_writer('n0 v0 dV c0 t i0 u Telephant=yes x y') as w:
        simple_handler(node_opl, node=lambda o: w.add_node(O(tags=o.tags)))


def test_way_object(test_writer, simple_handler):
    way_opl = 'w45 v14 dV c0 t i0 u Thighway=top Nn23,n56,n34,n23'

    with test_writer(way_opl) as w:
        simple_handler(way_opl, way=lambda o: w.add_way(o))


def test_way_object_generic(test_writer, simple_handler):
    way_opl = 'w45 v14 dV c0 t i0 u Thighway=top Nn23,n56,n34,n23'

    with test_writer(way_opl) as w:
        simple_handler(way_opl, way=lambda o: w.add(o))


def test_nodelist_object(test_writer, simple_handler):
    way_opl = 'w45 v14 dV c0 t i0 u Thighway=top Nn23,n56,n34,n23'

    with test_writer('w0 v0 dV c0 t i0 u T Nn23,n56,n34,n23') as w:
        simple_handler(way_opl, way=lambda o: w.add_way(O(nodes=o.nodes)))


def test_noderef_object(test_writer, simple_handler):
    way_opl = 'w45 v14 dV c0 t i0 u Thighway=top Nn23,n56,n34,n23'

    with test_writer('w0 v0 dV c0 t i0 u T Nn56,n34') as w:
        simple_handler(way_opl,
                       way=lambda o: w.add_way(O(nodes=[n for n in o.nodes if n.ref != 23])))


def test_relation_object(test_writer, simple_handler):
    rel_opl = 'r2 v0 dV c0 t i0 u Ttype=multipolygon Mw1@,w2@,w3@inner'

    with test_writer(rel_opl) as w:
        simple_handler(rel_opl, relation=lambda o: w.add_relation(o))


def test_relation_object_generic(test_writer, simple_handler):
    rel_opl = 'r2 v0 dV c0 t i0 u Ttype=multipolygon Mw1@,w2@,w3@inner'

    with test_writer(rel_opl) as w:
        simple_handler(rel_opl, relation=lambda o: w.add(o))


def test_memberlist_object(test_writer, simple_handler):
    rel_opl = 'r2 v0 dV c0 t i0 u Ttype=multipolygon Mw1@,w2@,w3@inner'

    with test_writer('r0 v0 dV c0 t i0 u T Mw1@,w2@,w3@inner') as w:
        simple_handler(rel_opl,
                       relation=lambda o: w.add_relation(O(members=o.members)))


def test_member_object(test_writer, simple_handler):
    rel_opl = 'r2 v0 dV c0 t i0 u Ttype=multipolygon Mw1@,w2@,w3@inner'

    with test_writer('r0 v0 dV c0 t i0 u T Mw1@,w2@') as w:
        simple_handler(rel_opl,
                       relation=lambda o: w.add_relation(O(members=[m for m in o.members
                                                                    if m.role != 'inner'])))


def test_set_custom_header(tmp_path):
    fn = str(tmp_path / 'test.xml')
    h = o.io.Header()
    h.set('generator', 'foo')
    h.add_box(o.osm.Box(0.1, -4, 10, 45))

    writer = o.SimpleWriter(fn, 4000, h)

    try:
        writer.add_node({})
    finally:
        writer.close()

    with o.io.Reader(fn) as rd:
        h = rd.header()
        assert h.get('generator') == 'foo'
        assert h.box().valid()
        assert h.box().bottom_left == o.osm.Location(0.1, -4)
        assert h.box().top_right == o.osm.Location(10, 45)


def test_add_node_after_close(tmp_path, simple_handler):
    node_opl = "n235 v1 dV c0 t i0 u Telephant=yes x98.7 y-3.45"

    filename = tmp_path / (str(uuid.uuid4()) + '.opl')
    writer = o.SimpleWriter(str(filename), 1024*1024)
    writer.close()

    with pytest.raises(RuntimeError, match='closed'):
        simple_handler(node_opl, node=lambda o: writer.add_node(o))


def test_add_way_after_close(tmp_path, simple_handler):
    node_opl = "w1 Nn1"

    filename = tmp_path / (str(uuid.uuid4()) + '.opl')
    writer = o.SimpleWriter(str(filename), 1024*1024)
    writer.close()

    with pytest.raises(RuntimeError, match='closed'):
        simple_handler(node_opl, way=lambda o: writer.add_way(o))

def test_add_relation_after_close(tmp_path, simple_handler):
    node_opl = "r54 Mn1@,w3@foo"

    filename = tmp_path / (str(uuid.uuid4()) + '.opl')
    writer = o.SimpleWriter(str(filename), 1024*1024)
    writer.close()

    with pytest.raises(RuntimeError, match='closed'):
        simple_handler(node_opl, relation=lambda o: writer.add_relation(o))


@pytest.mark.parametrize("final_item", (True, False))
def test_catch_errors_in_add_node(tmp_path, final_item):
    test_file = tmp_path / 'test.opl'

    with o.SimpleWriter(str(test_file), 4000) as writer:
        writer.add_node(o.osm.mutable.Node(id=123))
        with pytest.raises(TypeError):
            writer.add_node(o.osm.mutable.Node(id=124, tags=34))
        if not final_item:
            writer.add_node(o.osm.mutable.Node(id=125))

    output = test_file.read_text()

    expected = 'n123 v0 dV c0 t i0 u T x y\n'
    if not final_item:
        expected += 'n125 v0 dV c0 t i0 u T x y\n'

    assert output == expected


@pytest.mark.parametrize("final_item", (True, False))
def test_catch_errors_in_add_way(tmp_path, final_item):
    test_file = tmp_path / 'test.opl'

    with o.SimpleWriter(test_file, 4000) as writer:
        writer.add_way(o.osm.mutable.Way(id=123, nodes=[1, 2, 3]))
        with pytest.raises(TypeError):
            writer.add_way(o.osm.mutable.Way(id=124, nodes=34))
        if not final_item:
            writer.add_way(o.osm.mutable.Way(id=125, nodes=[11, 12]))

    output = test_file.read_text()

    expected = 'w123 v0 dV c0 t i0 u T Nn1,n2,n3\n'
    if not final_item:
        expected += 'w125 v0 dV c0 t i0 u T Nn11,n12\n'

    assert output == expected


@pytest.mark.parametrize("final_item", (True, False))
def test_catch_errors_in_add_relation(tmp_path, final_item):
    test_file = tmp_path / 'test.opl'

    with o.SimpleWriter(filename=str(test_file), bufsz=4000) as writer:
        writer.add_relation(o.osm.mutable.Relation(id=123))
        with pytest.raises(TypeError):
            writer.add_relation(o.osm.mutable.Relation(id=124, members=34))
        if not final_item:
            writer.add_relation(o.osm.mutable.Relation(id=125))

    output = test_file.read_text()

    expected = 'r123 v0 dV c0 t i0 u T M\n'
    if not final_item:
        expected += 'r125 v0 dV c0 t i0 u T M\n'

    assert output == expected


def test_do_not_overwrite_by_default(tmp_path):
    test_file = tmp_path / 'test.opl'

    with o.SimpleWriter(filename=str(test_file), bufsz=4000) as writer:
        writer.add_node(o.osm.mutable.Node(id=123))

    # try to open again
    with pytest.raises(RuntimeError, match='Open failed'):
        o.SimpleWriter(filename=str(test_file))


def test_do_overwrite(tmp_path):
    test_file = tmp_path / 'test.opl'

    with o.SimpleWriter(filename=str(test_file), bufsz=4000) as writer:
        writer.add_node(o.osm.mutable.Node(id=123))

    with o.SimpleWriter(filename=str(test_file), overwrite=True) as writer:
        pass



def test_write_to_file(tmp_path):
    test_file = tmp_path / 'test.txt'

    with o.SimpleWriter(o.io.File(test_file, 'opl'), bufsz=4000) as writer:
        writer.add_node(o.osm.mutable.Node(id=123))
