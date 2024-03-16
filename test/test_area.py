# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2024 Sarah Hoffmann.
from pathlib import Path

import osmium as o

from helpers import CountingHandler

TEST_FILE = str((Path(__file__) / '..' / 'example-test.pbf').resolve())

def test_area_handler():
    area = o.area.AreaManager()

    o.apply(o.io.Reader(TEST_FILE), area.first_pass_handler())

    ch_area = CountingHandler()
    ch_others = CountingHandler()

    lh = o.NodeLocationsForWays(o.index.create_map("flex_mem"))
    lh.ignore_errors()

    o.apply(o.io.Reader(TEST_FILE), lh,
            ch_others, area.second_pass_handler(ch_area))

    assert ch_area.counts == [0, 0, 0, 5239]
    assert ch_others.counts == [211100, 10315, 244, 0]


def test_area_buffer_handler():
    area = o.area.AreaManager()

    o.apply(o.io.Reader(TEST_FILE), area.first_pass_handler())

    lh = o.NodeLocationsForWays(o.index.create_map("flex_mem"))
    lh.ignore_errors()

    buf = o.BufferIterator()

    o.apply(o.io.Reader(TEST_FILE), lh, area.second_pass_to_buffer(buf))

    counts = 0
    for obj in buf:
        assert obj.is_area()
        counts += 1

    assert counts == 5239
