# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest
import osmium as o

from helpers import IDCollector

@pytest.mark.parametrize('init', [None, 1])
def test_file_processor_bad_init(init):
    with pytest.raises(TypeError):
        for obj in o.FileProcessor(init):
            pass

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


def test_generator_with_areas_with_filter(opl_buffer):
    data = opl_buffer("""\
            n10 x3 y3
            n11 x3 y3.01
            n12 x3.01 y3.01
            n13 x3.01 y3
            w11 Nn10,n11,n12,n13
            w12 Nn13,n10
            r1 Tbuilding=yes,type=multipolygon Mw11@,w12@
            """)

    count = 0
    for obj in o.FileProcessor(data)\
                .with_areas()\
                .with_filter(o.filter.EntityFilter(o.osm.AREA)):
        assert obj.is_area()
        count += 1

    assert count == 1

def test_generator_with_areas_with_area_filter(opl_buffer):
    data = opl_buffer("""\
            n10 x3 y3
            n11 x3 y3.01
            n12 x3.01 y3.01
            n13 x3.01 y3
            w11 Nn10,n11,n12,n13
            w12 Nn13,n10
            r1 Tbuilding=yes,type=multipolygon Mw11@,w12@
            r2 Tlanduse=grass,type=multipolygon Mw11@,w12@
            """)

    count = 0
    for obj in o.FileProcessor(data)\
                .with_areas(o.filter.KeyFilter('building'))\
                .with_filter(o.filter.EntityFilter(o.osm.AREA)):
        assert obj.is_area()
        assert obj.id == 3
        count += 1

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


def test_propagate_data_from_filters(opl_buffer):
    class MyFilter:
        def node(self, n):
            n.saved = 'test'
            return False

    fp = o.FileProcessor(opl_buffer('n56 x3 y-3')).with_filter(MyFilter())

    for obj in fp:
        assert obj.saved == 'test'


def test_simple_zip(opl_buffer):
    fp1 = o.FileProcessor(opl_buffer("""\
            n1
            n3
            n5
            w10 Nn1,n2
            r1 Mw1@
          """))

    fp2 = o.FileProcessor(opl_buffer("""\
            n2
            n3
            n456
            w12 Nn45,n85
            r1 Mw2@
          """))

    results = []
    for o1, o2 in o.zip_processors(fp1, fp2):
        results.append(((None if o1 is None else o1.type_str() + str(o1.id)),
                       (None if o2 is None else o2.type_str() + str(o2.id))))

    assert results == [('n1', None),
                      (None, 'n2'),
                      ('n3', 'n3'),
                      ('n5', None),
                      (None, 'n456'),
                      ('w10', None),
                      (None, 'w12'),
                      ('r1', 'r1')]


def test_filtered_handler_python(opl_buffer):
    data = opl_buffer("""\
            n1 Tamenity=foo
            n3
            w1 Thighway=residential
            w2
            r4
            """)

    ids = IDCollector()

    processed = []

    fp = o.FileProcessor(data)\
            .handler_for_filtered(ids)\
            .with_filter(o.filter.EmptyTagFilter())

    for obj in fp:
        processed.append(f"{obj.type_str()}{obj.id}")

    assert processed == ['n1', 'w1']
    assert ids.nodes == [3]
    assert ids.ways == [2]
    assert ids.relations == [4]


def test_filtered_handler_basehandler(opl_buffer, tmp_path):
    data = opl_buffer("""\
            n1 Tamenity=foo
            n3
            w1 Thighway=residential
            w2
            r4
            """)

    testf = tmp_path / 'test.opl'

    with o.SimpleWriter(str(testf)) as writer:
        fp = o.FileProcessor(data)\
                .handler_for_filtered(writer)\
                .with_filter(o.filter.EmptyTagFilter())

        processed = []
        for obj in fp:
            processed.append(f"{obj.type_str()}{obj.id}")

    assert processed == ['n1', 'w1']

    ids = IDCollector()

    o.apply(testf, ids)

    assert ids.nodes == [3]
    assert ids.ways == [2]
    assert ids.relations == [4]

