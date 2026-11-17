# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import gc

import pytest
import osmium

from helpers import CountingHandler


@pytest.fixture
def test_reader(test_data_dir):
    def _mk():
        return osmium.io.Reader(test_data_dir / 'example-test.pbf')
    return _mk


@pytest.mark.thread_unsafe
def test_area_handler(test_reader):
    area = osmium.area.AreaManager()

    osmium.apply(test_reader(), area.first_pass_handler())

    ch_area = CountingHandler()
    ch_others = CountingHandler()

    lh = osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem"))
    lh.ignore_errors()

    osmium.apply(test_reader(), lh, ch_others, area.second_pass_handler(ch_area))

    assert ch_area.counts == [0, 0, 0, 5239]
    assert ch_others.counts == [211100, 10315, 244, 0]


def test_area_buffer_handler(test_reader):
    area = osmium.area.AreaManager()

    osmium.apply(test_reader(), area.first_pass_handler())

    lh = osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem"))
    lh.ignore_errors()

    buf = osmium.BufferIterator()

    osmium.apply(test_reader(), lh, area.second_pass_to_buffer(buf))

    counts = 0
    for obj in buf:
        assert obj.is_area()
        counts += 1

    assert counts == 5239


def test_area_second_pass_handler_with_anonymous_python_handler(test_reader):
    area = osmium.area.AreaManager()

    osmium.apply(test_reader(), area.first_pass_handler())

    handler = area.second_pass_handler(CountingHandler())
    gc.collect()

    osmium.apply(test_reader(), handler)


def test_area_second_pass_handler_with_anonymous_native_handler(test_reader):
    area = osmium.area.AreaManager()

    osmium.apply(test_reader(), area.first_pass_handler())

    handler = area.second_pass_handler(osmium.filter.EmptyTagFilter())
    gc.collect()

    osmium.apply(test_reader(), handler)


def test_area_second_pass_handler_with_anonymous_second_handler(test_reader):
    def mk_second_handler():
        area = osmium.area.AreaManager()

        osmium.apply(test_reader(), area.first_pass_handler())

        return area.second_pass_handler(osmium.filter.EmptyTagFilter())

    handler = mk_second_handler()
    gc.collect()

    osmium.apply(test_reader(), handler)
