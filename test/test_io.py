# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
import pytest

import osmium as o

def _run_file(fn):
    rd = o.io.Reader(fn)
    try:
        o.apply(rd, o.SimpleHandler())
    finally:
        rd.close()

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
    try:
        rd = o.io.Reader(fn)
        with pytest.raises(RuntimeError):
            o.apply(rd, o.SimpleHandler())
    finally:
        rd.close()


def test_file_header(tmp_path):
    fn = tmp_path / 'empty.xml'
    fn.write_text("""<?xml version='1.0' encoding='UTF-8'?>
    <osm version="0.6" generator="test-pyosmium" timestamp="2014-08-26T20:22:02Z">
         <bounds minlat="-90" minlon="-180" maxlat="90" maxlon="180"/>
    </osm>
    """)

    rd = o.io.Reader(str(fn))
    try:
        h = rd.header()
        assert not h.has_multiple_object_versions
        assert h.box().valid()
        assert h.box().size() == 64800.0
    finally:
        rd.close()
