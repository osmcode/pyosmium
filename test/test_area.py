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
