# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest
import uuid

import osmium
from helpers import CountingHandler


@pytest.mark.parametrize('as_string', [True, False])
def test_file_simple(tmp_path, as_string):
    fn = tmp_path / f"{uuid.uuid4()}.opl"
    fn.write_text('n1')

    if as_string:
        fn = str(fn)

    for n in osmium.FileProcessor(osmium.io.File(fn)):
        assert n.is_node()
        assert n.id == 1


@pytest.mark.parametrize('as_string', [True, False])
def test_file_with_format(tmp_path, as_string):
    fn = tmp_path / f"{uuid.uuid4()}.txt"
    fn.write_text('n1')

    if as_string:
        fn = str(fn)

    for n in osmium.FileProcessor(osmium.io.File(fn, 'opl')):
        assert n.is_node()
        assert n.id == 1


def test_broken_timestamp(test_data):
    fn = test_data('n1 tx')

    with osmium.io.Reader(fn) as rd:
        with pytest.raises(RuntimeError):
            osmium.apply(rd, CountingHandler())


@pytest.mark.parametrize('as_string', [True, False])
def test_file_header(tmp_path, as_string):
    fn = tmp_path / f"{uuid.uuid4()}.xml"
    fn.write_text("""<?xml version='1.0' encoding='UTF-8'?>
    <osm version="0.6" generator="test-pyosmium" timestamp="2014-08-26T20:22:02Z">
         <bounds minlat="-90" minlon="-180" maxlat="90" maxlon="180"/>
    </osm>
    """)

    if as_string:
        fn = str(fn)

    with osmium.io.Reader(fn) as rd:
        h = rd.header()
        assert not h.has_multiple_object_versions
        assert h.box().valid()
        assert h.box().size() == 64800.0


def test_reader_with_filebuffer():
    rd = osmium.io.Reader(osmium.io.FileBuffer('n1 x4 y1'.encode('utf-8'), 'opl'))
    try:
        handler = CountingHandler()

        osmium.apply(rd, handler)

        assert handler.counts == [1, 0, 0, 0]
        assert rd.eof()
    finally:
        rd.close()


def test_reader_with_separate_thread_pool(test_data):
    with osmium.io.Reader(test_data('n1 x1 y1'), thread_pool=osmium.io.ThreadPool()) as rd:
        for obj in osmium.OsmFileIterator(rd):
            assert obj.id == 1


@pytest.mark.parametrize("entities,expected", [(osmium.osm.NODE, [2, 0, 0, 0]),
                                               (osmium.osm.ALL, [2, 1, 1, 0])])
def test_reader_with_entity_filter(test_data, entities, expected):
    fn = test_data("""\
        n1 x1 y2
        n2 x1 y3
        w34 Nn1,n2
        r67 Mw34@
        """)

    h = CountingHandler()
    with osmium.io.Reader(fn, entities) as rd:
        osmium.apply(rd, h)

    assert h.counts == expected


def test_thread_pool():
    pool = osmium.io.ThreadPool(2, 15)

    assert pool.num_threads == 2
    assert pool.queue_size() == 0
    assert pool.queue_empty()
