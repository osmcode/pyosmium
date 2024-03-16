# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2024 Sarah Hoffmann.
import pytest
import osmium as o


def test_read_node_location_with_handler(opl_reader):
    idx = o.index.create_map("flex_mem")
    hdlr = o.NodeLocationsForWays(idx)

    data = """\
           n1 x6 y7
           n45 x-3 y0
           """

    o.apply(opl_reader(data), hdlr)

    assert idx.get(1).lon == pytest.approx(6)
    assert idx.get(1).lat == pytest.approx(7)
    assert idx.get(45).lon == pytest.approx(-3)
    assert idx.get(45).lat == 0.0

    with pytest.raises(KeyError):
        idx.get(2)


@pytest.mark.parametrize('ignore_error', [(True, False)])
def test_apply_node_location_handler(opl_reader, ignore_error):

    hdlr = o.NodeLocationsForWays(o.index.create_map("flex_mem"))
    if ignore_error:
        hdlr.ignore_errors()

    class WayNodeHandler:
        def __init__(self):
            self.collect = []
            self.with_error = []

        def way(self, w):
            try:
                self.collect.append((w.id, [(n.lon, n.lat) for n in w.nodes]))
            except o.InvalidLocationError:
                self.with_error.append(w.id)


    data = """\
           n1 x6 y7
           n2 x6 y7.1
           n45 x-3 y0
           n55 x-2.9 y0
           w3 Nn1,n2
           w4 Nn45,n55,n56
           """

    tester = WayNodeHandler()

    if ignore_error:
        o.apply(opl_reader(data), hdlr, tester)

        assert tester.collect == [(3, [(pytest.approx(6), pytest.approx(7)),
                                      (pytest.approx(6), pytest.approx(7.1))])]
        assert tester.with_error == [4]
    else:
        with pytest.raises(osmium.InvalidLocationError):
            o.apply(opl.reader(data), hdlr, tester)


def test_apply_invalid_handler_object(opl_reader):
    class DummyHandler:
        def some_func():
            print('A')

    with pytest.raises(TypeError):
        o.apply(opl_reader("n1 x2 z4"), DummyHandler())


def test_mixed_handlers(opl_reader):
    logged = []

    class OldStyle(o.SimpleHandler):
        def node(self, n):
            logged.append('old')

    class NewStyle:
        def node(self, n):
            logged.append('new')

    o.apply(opl_reader("n1 x0 y0"), NewStyle(), OldStyle(), NewStyle(), OldStyle())

    assert logged == ['new', 'old', 'new', 'old']

@pytest.mark.parametrize('init', [None, 1])
def test_file_processor_bad_init(init):
    with pytest.raises(TypeError):
        o.FileProcessor(init)

def test_simple_generator(opl_buffer):
    count = 0
    for obj in o.FileProcessor(opl_buffer('n1 x5 y5')):
        assert obj.type_str() == 'n'
        assert obj.id == 1
        count += 1

    assert count == 1

def test_generator_with_location(opl_buffer):
    data = opl_buffer("""\
              n1 x10 y20
              n2 x11 y21
              w45 Nn1,n2
              """)

    count = 0
    for obj in o.FileProcessor(data).with_locations():
        count += 1
        if obj.type_str() == 'w':
            assert len(obj.nodes) == 2
            assert [n.ref for n in obj.nodes] == [1, 2]
            assert [n.location.lon for n in obj.nodes] == [10, 11]
            assert [n.location.lat for n in obj.nodes] == [20, 21]

    assert count == 3

def test_generator_with_areas(opl_buffer):
    data = opl_buffer("""\
            n10 x3 y3
            n11 x3 y3.01
            n12 x3.01 y3.01
            n13 x3.01 y3
            w12 Nn10,n11,n12,n13,n10 Tbuilding=yes
            """)

    count = 0
    for obj in o.FileProcessor(data).with_areas():
        if obj.type_str() == 'a':
            count += 1
            assert obj.from_way()
            assert obj.orig_id() == 12

    assert count == 1

def test_generator_with_filter(opl_buffer):
    data = opl_buffer("""\
            n10 x3 y3
            n11 x3 y3.01 Tfoo=bar
            """)

    count = 0
    for obj in o.FileProcessor(data).with_filter(o.filter.EmptyTagFilter()):
        count += 1
        assert obj.type_str() == 'n'
        assert obj.id == 11

    assert count == 1

def test_file_processor_header(tmp_path):
    fn = tmp_path / 'empty.xml'
    fn.write_text("""<?xml version='1.0' encoding='UTF-8'?>
    <osm version="0.6" generator="test-pyosmium" timestamp="2014-08-26T20:22:02Z">
         <bounds minlat="-90" minlon="-180" maxlat="90" maxlon="180"/>
    </osm>
    """)

    h = o.FileProcessor(fn).header

    assert not h.has_multiple_object_versions
    assert h.box().valid()
    assert h.box().size() == 64800.0

def test_file_processor_access_nodestore(opl_buffer):
    fp = o.FileProcessor(opl_buffer('n56 x3 y-3'))\
          .with_locations(o.index.create_map('sparse_mem_map'))

    for _ in fp:
        pass

    assert fp.node_location_storage.get(56).lat == -3
    assert fp.node_location_storage.get(56).lon == 3

def test_file_processor_bad_location_type(opl_buffer):
    with pytest.raises(TypeError, match='LocationTable'):
        o.FileProcessor(opl_buffer('n56 x3 y-3')).with_locations(67)
