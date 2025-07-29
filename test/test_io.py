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


class NullHandler:

    def node(self, n):
        pass


def _run_file(fn):
    with osmium.io.Reader(fn) as rd:
        osmium.apply(rd, NullHandler())


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


def test_node_only(test_data):
    _run_file(test_data('n1'))


def test_way_only(test_data):
    _run_file(test_data('w1 Nn1,n2,n3'))


def test_relation_only(test_data):
    _run_file(test_data('r573 Mw1@'))


def test_node_with_tags(test_data):
    _run_file(test_data('n32 Tbar=xx'))


def test_way_with_tags(test_data):
    _run_file(test_data('w5666 Nn1,n2,n3 Tbar=xx'))


def test_relation_with_tags(test_data):
    _run_file(test_data('r573 Mw1@ Tbar=xx'))


def test_broken_timestamp(test_data):
    fn = test_data('n1 tx')

    with osmium.io.Reader(fn) as rd:
        with pytest.raises(RuntimeError):
            osmium.apply(rd, NullHandler())


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
    handler = CountingHandler()

    osmium.apply(rd, handler)

    assert handler.counts == [1, 0, 0, 0]
