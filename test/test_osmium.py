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

    class WayNodeHandler(o.SimpleHandler):
        def __init__(self):
            super().__init__()
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
