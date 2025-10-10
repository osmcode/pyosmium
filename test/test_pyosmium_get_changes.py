# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
""" Tests for the pyosmium-get-changes script.
"""
from textwrap import dedent
import uuid
import datetime as dt

import pytest

import osmium
from osmium.tools.pyosmium_get_changes import pyosmium_get_changes

from helpers import IDCollector

try:
    import http.cookiejar as cookiejarlib
except ImportError:
    import cookielib as cookiejarlib


REPLICATION_BASE_TIME = dt.datetime(year=2017, month=8, day=26, hour=11, tzinfo=dt.timezone.utc)
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
def runner(httpserver):
    def _run(*args):
        return pyosmium_get_changes(
            ['--server', httpserver.url_for(''), '--diff-type', 'opl'] + list(map(str, args)))

    return _run


def test_init_id(runner, capsys, replication_server):
    assert 0 == runner('-I', '100')

    output = capsys.readouterr().out.strip()

    assert output == '100'


def test_init_date(runner, capsys, httpserver):
    httpserver.expect_request('/state.txt').respond_with_data(dedent("""\
                sequenceNumber=100
                timestamp=2017-08-26T11\\:04\\:02Z
             """))
    httpserver.expect_request('/000/000/000.state.txt').respond_with_data(dedent("""\
                sequenceNumber=0
                timestamp=2016-08-26T11\\:04\\:02Z
             """))
    assert 0 == runner('-D', '2015-12-24T08:08:08Z')

    output = capsys.readouterr().out.strip()

    assert output == '-1'


def test_init_to_file(runner, tmp_path, replication_server):
    fname = tmp_path / f"{uuid.uuid4()}.seq"

    assert 0 == runner('-I', '130', '-f', fname)
    assert fname.read_text() == '130'


def test_init_from_seq_file(runner, tmp_path, replication_server):
    fname = tmp_path / f"{uuid.uuid4()}.seq"
    fname.write_text('140')

    assert 0 == runner('-f', fname)
    assert fname.read_text() == '140'


def test_init_date_with_cookie(runner, capsys, tmp_path, httpserver):
    httpserver.expect_request('/state.txt').respond_with_data(dedent("""\
                sequenceNumber=100
                timestamp=2017-08-26T11\\:04\\:02Z
             """))
    httpserver.expect_request('/000/000/000.state.txt').respond_with_data(dedent("""\
                sequenceNumber=0
                timestamp=2016-08-26T11\\:04\\:02Z
             """))

    fname = tmp_path / 'my.cookie'
    cookie_jar = cookiejarlib.MozillaCookieJar(str(fname))
    cookie_jar.save()

    assert 0 == runner('--cookie', fname, '-D', '2015-12-24T08:08:08Z')

    output = capsys.readouterr().out.strip()

    assert output == '-1'


def test_get_simple_update(runner, tmp_path, replication_server):
    outfile = tmp_path / f"{uuid.uuid4()}.opl"

    assert 0 == runner('-I', '139', '-o', outfile)

    ids = IDCollector()
    osmium.apply(outfile, ids)

    assert ids.nodes == []
    assert ids.ways == []
    assert ids.relations == [140]


@pytest.mark.parametrize('end_id,max_size,actual_end', [(107, None, 107),
                                                        (None, 1, 108),
                                                        (105, 1, 105),
                                                        (110, 1, 108)])
def test_apply_diffs_endid(runner, tmp_path, replication_server, end_id, max_size, actual_end):
    outfile = tmp_path / f"{uuid.uuid4()}.opl"

    params = ['-I', '100', '-o', outfile]
    if end_id is not None:
        params.extend(('--end-id', end_id))
    if max_size is not None:
        params.extend(('-s', max_size))

    assert 0 == runner(*params)

    ids = IDCollector()
    osmium.apply(str(outfile), ids)

    assert ids.relations == list(range(101, actual_end + 1))


def test_change_id_too_old_for_replication_source(runner, tmp_path, replication_server, caplog):
    outfile = tmp_path / f"{uuid.uuid4()}.opl"

    assert 1 == runner('-I', 98, '-o', outfile)
    assert 'Cannot download state information for ID 98.' in caplog.text


def test_change_date_too_old_for_replication_source(runner, tmp_path, replication_server, caplog):
    outfile = tmp_path / f"{uuid.uuid4()}.opl"

    assert 1 == runner('-D', '2015-12-24T08:08:08Z', '-o', outfile)
    assert 'No starting point found' in caplog.text
