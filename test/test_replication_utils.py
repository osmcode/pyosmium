# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import logging

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
    val = rutil.get_replication_header(str(test_data_dir / 'example-test.pbf'))

    assert val.url == 'http://download.geofabrik.de/europe/andorra-updates'
    assert val.sequence == 2167
    assert val.timestamp == mkdate(2019, 2, 23, 21, 15, 2)


def test_get_replication_header_invalid_sequence(caplog):
    from unittest.mock import MagicMock, patch

    mock_header = MagicMock()
    mock_header.get.side_effect = lambda k: {
        "osmosis_replication_base_url": "https://example.com/replication",
        "osmosis_replication_sequence_number": "not-a-number",
        "osmosis_replication_timestamp": "2024-01-01T00:00:00Z",
    }.get(k)

    mock_reader = MagicMock()
    mock_reader.header.return_value = mock_header

    with patch('osmium.replication.utils.oreader', return_value=mock_reader):
        with caplog.at_level(logging.WARNING, logger='pyosmium'):
            val = rutil.get_replication_header('dummy.pbf')

    assert val.url == 'https://example.com/replication'
    assert val.sequence is None
    assert val.timestamp is not None
    assert 'not-a-number' in caplog.text


def test_get_replication_header_negative_sequence(caplog):
    from unittest.mock import MagicMock, patch

    mock_header = MagicMock()
    mock_header.get.side_effect = lambda k: {
        "osmosis_replication_base_url": "https://example.com/replication",
        "osmosis_replication_sequence_number": "-5",
        "osmosis_replication_timestamp": "2024-01-01T00:00:00Z",
    }.get(k)

    mock_reader = MagicMock()
    mock_reader.header.return_value = mock_header

    with patch('osmium.replication.utils.oreader', return_value=mock_reader):
        with caplog.at_level(logging.WARNING, logger='pyosmium'):
            val = rutil.get_replication_header('dummy.pbf')

    assert val.url == 'https://example.com/replication'
    assert val.sequence is None
    assert val.timestamp is not None
    assert '-5' in caplog.text
