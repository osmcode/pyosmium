# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2024 Sarah Hoffmann.
import osmium as o

import pytest

class IDCollector:

    def __init__(self):
        self.nodes = []
        self.ways = []
        self.relations = []

    def node(self, n):
        self.nodes.append(n.id)

    def way(self, w):
        self.ways.append(w.id)

    def relation(self, r):
        self.relations.append(r.id)


@pytest.fixture
def reader(opl_reader):
    return opl_reader("""\
               n1 x1 y1
               n2 x1 y1 Tfoo=bar
               w1 Nn1,n2 Thighway=road
               w34 Nn2,n1
               r90
               r91 Tsome=thing
               """)

def test_filter_default_config(reader):
    pre = IDCollector()
    post = IDCollector()
    o.apply(reader, pre, o.filter.EmptyTagFilter(), post)

    assert pre.nodes == [1, 2]
    assert post.nodes == [2]
    assert pre.ways == [1, 34]
    assert post.ways == [1]
    assert pre.relations == [90, 91]
    assert post.relations == [91]


def test_filter_inverted(reader):
    pre = IDCollector()
    post = IDCollector()
    o.apply(reader, pre, o.filter.EmptyTagFilter().invert(), post)

    assert pre.nodes == [1, 2]
    assert post.nodes == [1]
    assert pre.ways == [1, 34]
    assert post.ways == [34]
    assert pre.relations == [90, 91]
    assert post.relations == [90]


def test_filter_restrict_entity(reader):
    pre = IDCollector()
    post = IDCollector()
    o.apply(reader, pre, o.filter.EmptyTagFilter().enable_for(o.osm.WAY | o.osm.RELATION), post)

    assert pre.nodes == [1, 2]
    assert post.nodes == [1, 2]
    assert pre.ways == [1, 34]
    assert post.ways == [1]
    assert pre.relations == [90, 91]
    assert post.relations == [91]


def test_filter_restrict_entity_invert(reader):
    pre = IDCollector()
    post = IDCollector()
    o.apply(reader, pre, o.filter.EmptyTagFilter().enable_for(o.osm.NODE).invert(), post)

    assert pre.nodes == [1, 2]
    assert post.nodes == [1]
    assert pre.ways == [1, 34]
    assert post.ways == [1, 34]
    assert pre.relations == [90, 91]
    assert post.relations == [90, 91]


def test_filter_chained(reader):
    pre = IDCollector()
    post = IDCollector()
    o.apply(reader, pre,
            o.filter.EmptyTagFilter().enable_for(o.osm.NODE).invert(False),
            o.filter.EmptyTagFilter().enable_for(o.osm.WAY).invert(True),
            post)

    assert pre.nodes == [1, 2]
    assert post.nodes == [2]
    assert pre.ways == [1, 34]
    assert post.ways == [34]
    assert pre.relations == [90, 91]
    assert post.relations == [90, 91]
