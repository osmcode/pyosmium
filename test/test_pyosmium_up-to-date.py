# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
""" Tests for the pyosmium-up-to-date script.
"""
import uuid
import datetime as dt

import pytest
import osmium
from osmium.tools.pyosmium_up_to_date import pyosmium_up_to_date
import osmium.replication.utils as rutil

from helpers import IDCollector

# Choosing a future date here, so we don't run into pyosmium's check for old
# data. If you get caught by this: congratulations, you are maintaining a
# 50-year old test.
REPLICATION_BASE_TIME = dt.datetime(year=2070, month=5, day=6, hour=20, tzinfo=dt.timezone.utc)
REPLICATION_BASE_SEQ = 100
REPLICATION_CURRENT = 140


@pytest.fixture
def replication_server(httpserver):
    def _state(seq):
        seqtime = REPLICATION_BASE_TIME + dt.timedelta(hours=seq - REPLICATION_CURRENT)
        timestamp = seqtime.strftime('%Y-%m-%dT%H\\:%M\\:%SZ')
        return f"sequenceNumber={seq}\ntimestamp={timestamp}\n"

    httpserver.no_handler_status_code = 404
    httpserver.expect_request('/state.txt').respond_with_data(_state(REPLICATION_CURRENT))
    for i in range(REPLICATION_BASE_SEQ, REPLICATION_CURRENT + 1):
        httpserver.expect_request(f'/000/000/{i}.opl')\
                  .respond_with_data(f"r{i} M" + ",".join(f"n{i}@" for i in range(1, 6000)))
        httpserver.expect_request(f'/000/000/{i}.state.txt').respond_with_data(_state(i))

    return httpserver.url_for('')


@pytest.fixture
def runner(replication_server):
    def _run(*args):
        return pyosmium_up_to_date(
            ['--server', replication_server, '--diff-type', 'opl'] + list(map(str, args)))

    return _run


def test_no_output_file(runner):
    with pytest.raises(SystemExit):
        runner()


def test_simple_update_no_windback(runner, test_data):
    outfile = test_data("n1 v1 t2070-05-06T19:30:00Z")

    assert 0 == runner('--wind-back', 0, outfile)

    ids = IDCollector()
    osmium.apply(outfile, ids)

    assert ids.nodes == [1]
    assert ids.relations == list(range(139, REPLICATION_CURRENT + 1))


def test_simple_update_override(runner, test_data):
    outfile = test_data("n1 v1 t2070-05-06T19:30:00Z")

    assert 0 == runner(outfile)

    ids = IDCollector()
    osmium.apply(outfile, ids)

    assert ids.nodes == [1]
    assert ids.relations == list(range(138, REPLICATION_CURRENT + 1))


def test_simple_update_new_file(runner, replication_server, test_data, tmp_path):
    outfile = test_data("n1 v1 t2070-05-06T19:30:00Z")
    newfile = tmp_path / f"{uuid.uuid4()}.pbf"

    assert 0 == runner('-o', str(newfile), outfile)

    ids = IDCollector()
    osmium.apply(outfile, ids)

    assert ids.nodes == [1]
    assert ids.relations == []

    ids = IDCollector()
    osmium.apply(newfile, ids)
    assert ids.nodes == [1]
    assert ids.relations == list(range(138, REPLICATION_CURRENT + 1))

    header = rutil.get_replication_header(newfile)

    assert header.url == replication_server
    assert header.sequence == REPLICATION_CURRENT
    assert header.timestamp == REPLICATION_BASE_TIME


def test_update_sequences(runner, test_data, tmp_path):
    outfile = test_data("n1 v1 t2070-05-05T10:30:00Z")
    newfile = tmp_path / f"{uuid.uuid4()}.pbf"

    assert 0 == runner('--end-id', '110', '-o', str(newfile), outfile)

    ids = IDCollector()
    osmium.apply(newfile, ids)
    assert ids.nodes == [1]
    assert ids.relations == list(range(105, 111))

    header = rutil.get_replication_header(newfile)

    assert header.sequence == 110

    # Note: this test only catches holes, no duplicate application.
    assert 0 == runner(newfile)

    ids = IDCollector()
    osmium.apply(newfile, ids)
    assert ids.nodes == [1]
    assert ids.relations == list(range(105, REPLICATION_CURRENT + 1))

    header = rutil.get_replication_header(newfile)

    assert header.sequence == REPLICATION_CURRENT


@pytest.mark.parametrize('end_id,max_size,actual_end', [(107, None, 107),
                                                        (None, 1, 108),
                                                        (105, 1, 105),
                                                        (110, 1, 108)])
def test_update_with_endid(test_data, runner, end_id, max_size, actual_end):
    outfile = test_data("n1 v1 t2070-05-05T06:30:00Z")

    params = [outfile]
    if end_id is not None:
        params.extend(('--end-id', end_id))
    if max_size is not None:
        params.extend(('-s', max_size))

    assert (0 if end_id == actual_end else 1) == runner(*params)

    ids = IDCollector()
    osmium.apply(outfile, ids)

    assert ids.relations == list(range(101, actual_end + 1))


def test_update_with_enddate(test_data, runner, tmp_path):
    outfile = test_data("n1 v1 t2070-05-05T06:30:00Z")
    newfile = tmp_path / f"{uuid.uuid4()}.pbf"

    assert 0 == runner('-E', '2070-05-05T09:30:00Z', '-o', newfile, outfile)

    header = rutil.get_replication_header(newfile)

    assert header.sequence == 105
    assert header.timestamp == dt.datetime(year=2070, month=5, day=5, hour=9,
                                           tzinfo=dt.timezone.utc)

    ids = IDCollector()
    osmium.apply(newfile, ids)

    assert ids.relations == list(range(101, 106))


def test_change_date_too_old_for_replication_source(test_data, runner, caplog):
    outfile = test_data("n1 v1 t2070-04-05T06:30:00Z")

    assert 3 == runner(outfile)
    assert 'No starting point found' in caplog.text


def test_change_id_too_old_for_replication_source(caplog, tmp_path, runner, replication_server):
    outfile = tmp_path / f"{uuid.uuid4()}.pbf"
    h = osmium.io.Header()
    h.set('osmosis_replication_base_url', replication_server)
    h.set('osmosis_replication_sequence_number', '98')

    with osmium.SimpleWriter(outfile, 4000, h) as w:
        w.add_node({'id': 1})

    assert 3 == runner(outfile)
    assert 'Cannot download state information for ID 98' in caplog.text
