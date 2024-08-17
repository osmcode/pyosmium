# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

from helpers import IDCollector

@pytest.fixture
def ref_file(test_data):
    return test_data("""\
                n1 x0 y0
                n2 x0 y0
                n99 x0 y0
                n100 x0 y0
                w12 Nn1,n2
                w90 Nn10,n11
                r2 Mn99@
                r10 Mn100@,w90@,r2@
                """)


class DummyNode:
    def __init__(self, nid):
        self.id = nid
        self.location = (3, 4)


def test_simple_forward_no_back_reference(ref_file, tmp_path):
    outfile = str(tmp_path / 'test.osm')

    with o.ForwardReferenceWriter(outfile, ref_file, back_references=False) as writer:
        writer.add_node(DummyNode(2))
        writer.add_node(DummyNode(99))

    ids = IDCollector()
    o.apply(outfile, ids)

    assert ids.nodes == [2, 99]
    assert ids.ways == [12]
    assert ids.relations == [2]


def test_simple_forward_with_back_reference(ref_file, tmp_path):
    outfile = str(tmp_path / 'test.osm')

    with o.ForwardReferenceWriter(outfile, ref_file) as writer:
        writer.add_node(DummyNode(2))
        writer.add_node(DummyNode(99))

    ids = IDCollector()

    for obj in o.FileProcessor(outfile)\
                .with_filter(ids)\
                .with_filter(o.filter.EntityFilter(o.osm.NODE)):
        if obj.id in (2, 99):
            assert obj.lat == 4
            assert obj.lon == 3
        else:
            assert obj.lat == 0
            assert obj.lon == 0

    assert ids.nodes == [1, 2, 99]
    assert ids.ways == [12]
    assert ids.relations == [2]
