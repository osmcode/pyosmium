# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

def assert_tracker_content(ids, nodes, ways, rels):
    assert len(ids.node_ids()) == len(nodes)
    assert all(n in ids.node_ids() for n in nodes), \
           f"Nodes not found: {[n for n in nodes if n not in ids.node_ids()]}"
    assert len(ids.way_ids()) == len(ways)
    assert all(n in ids.way_ids() for n in ways), \
           f"Ways not found: {[n for n in ways if n not in ids.way_ids()]}"
    assert len(ids.relation_ids()) == len(rels)
    assert all(n in ids.relation_ids() for n in rels), \
           f"Relations not found: {[n for n in rels if n not in ids.relation_ids()]}"


def test_add_node():
    ids = o.IdTracker()

    ids.add_node(45)

    assert ids.node_ids().get(45)
    assert len(ids.node_ids()) == 1

    ids.node_ids().unset(45)
    assert ids.node_ids().empty()


def test_add_way():
    ids = o.IdTracker()

    ids.add_way(45)

    assert ids.way_ids().get(45)
    assert len(ids.way_ids()) == 1

    ids.way_ids().unset(45)
    assert ids.way_ids().empty()


def test_add_relation():
    ids = o.IdTracker()

    ids.add_relation(45)

    assert ids.relation_ids().get(45)
    assert len(ids.relation_ids()) == 1

    ids.relation_ids().unset(45)
    assert ids.relation_ids().empty()


def test_add_references_from_file(opl_buffer):
    data = """\
           w1 Nn1,n2,n3
           w2 Nn100,n2,n101
           r1 Mn1000@,w23@,r1@
           """

    ids = o.IdTracker()

    for obj in o.FileProcessor(opl_buffer(data)):
        ids.add_references(obj)

    assert len(ids.node_ids()) == 6
    assert all(n in ids.node_ids() for n in (1, 2, 3, 100, 101, 1000))

    assert len(ids.way_ids()) == 1
    assert 23 in ids.way_ids()

    assert len(ids.relation_ids()) == 1
    assert 1 in ids.relation_ids()


def test_add_reference_from_python_way():
    ids = o.IdTracker()

    class Way:
        nodes = [5, 7, 23, 1, 5]

    ids.add_references(Way())

    assert len(ids.node_ids()) == 4
    assert all(n in ids.node_ids() for n in (1, 5, 7, 23))


def test_add_reference_from_python_relation():
    ids = o.IdTracker()

    class Member:
        type = 'r'
        ref = 100
        role = ''

    class Rel:
        members = [('n', 23, ''),
                   ('w', 3, ''),
                   Member()]

    ids.add_references(Rel())

    assert len(ids.node_ids()) == 1
    assert 23 in ids.node_ids()

    assert len(ids.way_ids()) == 1
    assert 3 in ids.way_ids()

    assert len(ids.relation_ids()) == 1
    assert 100 in ids.relation_ids()


def test_contains_references_in_node(opl_buffer):
    ids = o.IdTracker()
    ids.add_node(45)

    for obj in o.FileProcessor(opl_buffer('n45')):
        assert not ids.contains_any_references(obj)


def test_contains_references_in_way(opl_buffer):
    ids = o.IdTracker()
    ids.add_node(45)

    for obj in o.FileProcessor(opl_buffer('w3 Nn12,n45')):
        assert ids.contains_any_references(obj)


def test_contains_references_not_in_way(opl_buffer):
    ids = o.IdTracker()
    ids.add_way(3)

    for obj in o.FileProcessor(opl_buffer('w3 Nn12,n45')):
        assert not ids.contains_any_references(obj)


def test_contains_references_in_relation(opl_buffer):
    ids = o.IdTracker()
    ids.add_node(45)

    for obj in o.FileProcessor(opl_buffer('r3 Mn12@,n45@')):
        assert ids.contains_any_references(obj)


def test_contains_references_not_in_relation(opl_buffer):
    ids = o.IdTracker()
    ids.add_way(3)

    for obj in o.FileProcessor(opl_buffer('r3 Mn12@,n45@')):
        assert not ids.contains_any_references(obj)

REF_SRC = """\
w12 Nn1,n2
w90 Nn10,n11
r2 Mn99@
r10 Mn100@,w90@,r2@
"""

@pytest.mark.parametrize('depth', range(3))
def test_complete_backward_references(tmp_path, depth):
    if depth == 0:
        data_file = o.io.FileBuffer(REF_SRC.encode('utf-8'), 'opl')
    else:
        data_file = tmp_path / 'test.opl'
        data_file.write_text(REF_SRC)

    ids = o.IdTracker()
    ids.add_way(12)
    ids.add_relation(10)

    ids.complete_backward_references(data_file, relation_depth=depth)

    if depth == 0:
        assert_tracker_content(ids, nodes=(1, 2), ways=(12,), rels=(10,))
    elif depth == 1:
        assert_tracker_content(ids, nodes=(1, 2, 10, 11, 100), ways=(12, 90), rels=(10, 2))
    elif depth == 2:
        assert_tracker_content(ids, nodes=(1, 2, 10, 11, 99, 100), ways=(12, 90), rels=(10, 2))


@pytest.mark.parametrize('depth', range(-1, 2))
def test_complete_forward_references(tmp_path, depth):
    if depth == 0:
        data_file = o.io.FileBuffer(REF_SRC.encode('utf-8'), 'opl')
    else:
        data_file = tmp_path / 'test.opl'
        data_file.write_text(REF_SRC)

    ids = o.IdTracker()
    ids.add_node(1)
    ids.add_node(99)

    ids.complete_forward_references(data_file, relation_depth=depth)

    if depth == -1:
        assert_tracker_content(ids, nodes=(1, 99), ways=(12,), rels=[])
    elif depth == 0:
        assert_tracker_content(ids, nodes=(1, 99), ways=(12,), rels=[2])
    elif depth == 1:
        assert_tracker_content(ids, nodes=(1, 99), ways=(12,), rels=[2, 10])


def test_clear_node_id_set():
    ids = o.IdTracker()
    for i in range (1000, 1003):
        ids.add_node(i)

    assert len(ids.node_ids()) == 3

    ids.node_ids().clear()

    assert len(ids.node_ids()) == 0
