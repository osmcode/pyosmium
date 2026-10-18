# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import logging

import pytest

import osmium
import osmium.replication.utils as rutil

from helpers import mkdate


def test_get_replication_header_empty(tmp_path):
    fn = tmp_path / 'test.opl'
    fn.write_text('n6365 v1 c63965061 t2018-10-29T03:56:07Z i8369524 ux x1 y7')

    val = rutil.get_replication_header(str(fn))
    assert val.url is None
    assert val.sequence is None
    assert val.timestamp is None


def test_get_replication_header_full(test_data_dir):
    val = rutil.get_replication_header(test_data_dir / 'example-test.pbf')

    assert val.url == 'http://download.geofabrik.de/europe/andorra-updates'
    assert val.sequence == 2167
    assert val.timestamp == mkdate(2019, 2, 23, 21, 15, 2)


@pytest.mark.parametrize("inseq, error", [("not-a-number", "OSM file header is not a number"),
                                          ("-5", "OSM file header is negative")])
def test_get_replication_header_invalid_sequence(test_data_dir, caplog, monkeypatch,
                                                 inseq, error):
    h = osmium.io.Header()
    h.set("osmosis_replication_base_url", "https://example.com/replication")
    h.set("osmosis_replication_sequence_number", inseq)
    h.set("osmosis_replication_timestamp", "2024-01-01T00:00:00Z")

    monkeypatch.setattr(osmium.io.Reader, "header", lambda _: h)

    with caplog.at_level(logging.WARNING, logger='pyosmium'):
        val = rutil.get_replication_header(test_data_dir / 'example-test.pbf')

    assert val.url == 'https://example.com/replication'
    assert val.sequence is None
    assert val.timestamp == mkdate(2024, 1, 1, 0, 0, 0)
    assert error in caplog.text
