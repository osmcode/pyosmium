# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from pathlib import Path

import pytest
import osmium

from helpers import CountingHandler


TEST_FILE = str((Path(__file__) / '..' / 'example-test.pbf').resolve())


@pytest.mark.thread_unsafe
def test_area_handler():
    area = osmium.area.AreaManager()

    osmium.apply(osmium.io.Reader(TEST_FILE), area.first_pass_handler())

    ch_area = CountingHandler()
    ch_others = CountingHandler()

    lh = osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem"))
    lh.ignore_errors()

    osmium.apply(osmium.io.Reader(TEST_FILE), lh,
                 ch_others, area.second_pass_handler(ch_area))

    assert ch_area.counts == [0, 0, 0, 5239]
    assert ch_others.counts == [211100, 10315, 244, 0]


def test_area_buffer_handler():
    area = osmium.area.AreaManager()

    osmium.apply(osmium.io.Reader(TEST_FILE), area.first_pass_handler())

    lh = osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem"))
    lh.ignore_errors()

    buf = osmium.BufferIterator()

    osmium.apply(osmium.io.Reader(TEST_FILE), lh, area.second_pass_to_buffer(buf))

    counts = 0
    for obj in buf:
        assert obj.is_area()
        counts += 1

    assert counts == 5239
