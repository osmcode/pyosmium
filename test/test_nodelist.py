# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
import pytest

import osmium as o

def test_waynode_length(simple_handler):
    data = """\
           w593
           w4 Nn1,n2,n-34
           w8 Nn12,n12,n12,n0
           """

    lens = {}
    def way(w):
        lens[w.id] = len(w.nodes)

    simple_handler(data, way=way)

    assert lens == { 593 : 0, 4 : 3, 8 : 4 }


def test_node_ids(simple_handler):
    refs = []
    def way(w):
        refs.extend(n.ref for n in w.nodes)
        assert w.nodes[-2].ref == -34
        with pytest.raises(IndexError):
            w.nodes[5]
        with pytest.raises(IndexError):
            w.nodes[-6]

    simple_handler("w4 Nn1,n1,n34359737784,n-34,n0", way=way)

    assert refs == [1, 1, 34359737784, -34, 0]


def test_missing_location_without_location_handler(simple_handler):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """

    refs = []
    def way(w):
        refs.extend(n.ref for n in w.nodes)
        assert not w.nodes[0].location.valid()
        with pytest.raises(o.InvalidLocationError):
            w.nodes[0].location.lat
        with pytest.raises(o.InvalidLocationError):
            w.nodes[0].location.lon

    simple_handler(data, way=way)

    assert refs == [1]


def test_valid_locations(simple_handler):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """

    locations = []
    def way(w):
        assert all(n.location.valid() for n in w.nodes)
        locations.extend((int(10 * n.location.lon), int(10 * n.location.lat))
                         for n in w.nodes)

    simple_handler(data, way=way, locations=True)

    assert locations == [(5, 100)]
