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


def test_value_propagation(opl_reader):
    logged = []

    class FirstHandler:
        def node(self, n):
            n.saved = 45674

    class SecondHandler:
        def node(self, n):
            logged.append(n.saved)

    o.apply(opl_reader("n1 x0 y0"), FirstHandler(), SecondHandler())

    assert logged == [45674]
