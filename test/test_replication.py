# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import logging
import time
from textwrap import dedent
import uuid

import pytest
import requests

from werkzeug.wrappers import Response

from helpers import mkdate, CountingHandler, IDCollector

import osmium.replication.server as rserv
import osmium.replication

pytestmark = [pytest.mark.thread_unsafe, pytest.mark.iterations(1)]


@pytest.mark.parametrize("inp,outp", [
        (None,      'https://text.org/state.txt'),
        (1,         'https://text.org/000/000/001.state.txt'),
        (999,       'https://text.org/000/000/999.state.txt'),
        (1000,      'https://text.org/000/001/000.state.txt'),
        (573923,    'https://text.org/000/573/923.state.txt'),
        (3290012,   'https://text.org/003/290/012.state.txt'),
    ])
def test_get_state_url(inp, outp):
    svr = rserv.ReplicationServer("https://text.org")

    assert outp == svr.get_state_url(inp)


@pytest.mark.parametrize("inp,outp", [
        (1,         'https://who.is/me//000/000/001.osc.gz'),
        (500,       'https://who.is/me//000/000/500.osc.gz'),
        (83750,     'https://who.is/me//000/083/750.osc.gz'),
        (999999999, 'https://who.is/me//999/999/999.osc.gz'),
    ])
def test_get_diff_url(inp, outp):
    svr = rserv.ReplicationServer("https://who.is/me/")

    assert outp, svr.get_diff_url(inp)


@pytest.mark.parametrize("as_string", [True, False])
def test_get_newest_change_from_file(tmp_path, as_string):
    fn = tmp_path / f"{uuid.uuid4()}.opl"
    fn.write_text('n6365 v1 c63965061 t2018-10-29T03:56:07Z i8369524 ux x1 y7')

    if as_string:
        fn = str(fn)

    val = osmium.replication.newest_change_from_file(fn)
    assert val == mkdate(2018, 10, 29, 3, 56, 7)


def test_get_newest_change_from_reader():
    fb = osmium.io.FileBuffer(
        'n6365 v1 t2018-10-29T03:56:07Z x1 y7\n'
        'n6366 v1 t2018-10-29T04:56:07Z x1 y7\n'.encode('utf-8'), 'opl')

    with osmium.io.Reader(fb, thread_pool=osmium.io.ThreadPool()) as rd:
        val = osmium.replication.newest_change_from_file(rd)
        assert val == mkdate(2018, 10, 29, 4, 56, 7)


def test_get_state_valid(httpserver):
    httpserver.expect_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z
        txnReadyList=
        txnMax=1219304113
        txnActiveList=1219303583,1219304054,1219304104""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669


def test_get_state_sequence_cut(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=259""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669


def test_get_state_date_cut(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-2""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669


def test_get_state_timestamp_cut(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669


def test_get_state_permanent_error(httpserver, caplog):
    httpserver.expect_request('/state.txt').respond_with_data('stuff', status=404)

    with caplog.at_level(logging.DEBUG):
        res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is None
    assert "Loading state info failed" in caplog.text


def test_get_state_transient_error(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data('stuff', status=500)
    httpserver.expect_ordered_request('/state.txt').respond_with_data('stuff', status=500)
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z
        txnReadyList=
        txnMax=1219304113
        txnActiveList=1219303583,1219304054,1219304104""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669


def test_get_state_too_many_retries(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=""")
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z""")

    res = rserv.ReplicationServer(httpserver.url_for('')).get_state_info()

    assert res is None


def test_get_state_server_timeout(httpserver):
    def sleeping(request):
        time.sleep(2)
        return Response("""\
    #Sat Aug 26 11:04:04 UTC 2017
    txnMaxQueried=1219304113
    sequenceNumber=2594669
    timestamp=2017-08-26T11\\:04\\:02Z
    txnReadyList=
    txnMax=1219304113
    txnActiveList=1219303583,1219304054,1219304104""")

    httpserver.expect_request("/state.txt").respond_with_handler(sleeping)

    with rserv.ReplicationServer(httpserver.url_for('')) as svr:
        svr.set_request_parameter('timeout', 1)

        res = svr.get_state_info()

    assert res is None


def test_apply_diffs_count(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1
        w1
        r1
    """))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000)
        assert h.counts == [1, 1, 1, 0]


@pytest.mark.parametrize('end_id,max_size, actual_end', [(107, None, 107),
                                                         (None, 512, 108),
                                                         (105, 512, 105),
                                                         (110, 512, 108),
                                                         (None, None, 115)])
def test_apply_diffs_endid(httpserver, end_id, max_size, actual_end):
    httpserver.expect_request('/state.txt').respond_with_data("""\
        sequenceNumber=140
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    for i in range(100, 141):
        httpserver.expect_request(f'/000/000/{i}.opl')\
                  .respond_with_data(f"r{i} M" + ",".join(f"n{i}@" for i in range(1, 3000)))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        res = svr.collect_diffs(101, end_id=end_id, max_size=max_size)

        assert res is not None
        assert res.id == actual_end
        assert res.newest == 140

        ids = IDCollector()
        res.reader.apply(ids)

        assert ids.relations == list(range(101, actual_end + 1))


def test_apply_diffs_without_simplify(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 v23
        n1 v24
        w1
        r1
    """))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000, simplify=False)
        assert [2, 1, 1, 0] == h.counts


def test_apply_diffs_with_simplify(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 v23
        n1 v24
        w1
        r1
    """))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000, simplify=True)
        assert [1, 1, 1, 0] == h.counts


def test_apply_with_location(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))

    class Handler(CountingHandler):
        def way(self, w):
            self.counts[1] += 1
            assert 2 == len(w.nodes)
            assert 1 == w.nodes[0].ref
            assert 10 == w.nodes[0].location.lon
            assert 23 == w.nodes[0].location.lat
            assert 2 == w.nodes[1].ref
            assert not w.nodes[1].location.valid()

    h = Handler()
    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        assert 100 == svr.apply_diffs(h, 100, 10000, idx="flex_mem")
        assert h.counts == [1, 1, 0, 0]


def test_apply_reader_without_simplify(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 v23
        n1 v24
        w1
        r1
    """))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = CountingHandler()
        diffs = svr.collect_diffs(100, 100000)

    assert diffs is not None
    diffs.reader.apply(h, simplify=False)
    assert [2, 1, 1, 0] == h.counts


def test_apply_reader_with_simplify(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 v23
        n1 v24
        w1
        r1
    """))

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = CountingHandler()
        diffs = svr.collect_diffs(100, 100000)

    assert diffs is not None
    diffs.reader.apply(h, simplify=True)
    assert [1, 1, 1, 0] == h.counts


def test_apply_reader_with_location(httpserver):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))

    class Handler(CountingHandler):
        def way(self, w):
            self.counts[1] += 1
            assert 2 == len(w.nodes)
            assert 1 == w.nodes[0].ref
            assert 10 == w.nodes[0].location.lon
            assert 23 == w.nodes[0].location.lat
            assert 2 == w.nodes[1].ref
            assert not w.nodes[1].location.valid()

    with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
        h = Handler()
        diffs = svr.collect_diffs(100, 100000)

    assert diffs is not None
    diffs.reader.apply(h, idx="flex_mem")
    assert h.counts == [1, 1, 0, 0]


def test_apply_diffs_permanent_error(httpserver, caplog):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl')\
              .respond_with_data('not a file', status=404)

    with caplog.at_level(logging.ERROR):
        with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
            h = CountingHandler()
            with pytest.raises(requests.HTTPError, match='404'):
                svr.apply_diffs(h, 100, 10000)

    assert 'Permanent server error' in caplog.text


def test_apply_diffs_transient_error_first_diff(httpserver, caplog):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_request('/000/000/100.opl')\
              .respond_with_data('not a file', status=503)

    with caplog.at_level(logging.ERROR):
        with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
            h = CountingHandler()
            assert svr.apply_diffs(h, 100, 10000) is None
            assert h.counts == [0, 0, 0, 0]

    assert 'Error during diff download' in caplog.text


def test_apply_diffs_permanent_error_later_diff(httpserver, caplog):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=101
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))
    httpserver.expect_ordered_request('/000/000/101.opl')\
              .respond_with_data('not a file', status=404)

    with caplog.at_level(logging.ERROR):
        with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
            h = CountingHandler()
            assert 100 == svr.apply_diffs(h, 100, 10000)
            assert h.counts == [1, 1, 0, 0]

    assert 'Error during diff download' in caplog.text


def test_apply_diffs_transient_error_later_diff(httpserver, caplog):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=101
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))
    httpserver.expect_ordered_request('/000/000/101.opl')\
              .respond_with_data('not a file', status=503)
    httpserver.expect_ordered_request('/000/000/101.opl').respond_with_data(dedent("""\
        n2 x10.0 y23.0
    """))

    with caplog.at_level(logging.ERROR):
        with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
            h = CountingHandler()
            assert 101 == svr.apply_diffs(h, 100, 10000)
            assert h.counts == [2, 1, 0, 0]

    assert 'Error during diff download' not in caplog.text


def test_apply_diffs_transient_error_permanent(httpserver, caplog):
    httpserver.expect_ordered_request('/state.txt').respond_with_data("""\
        sequenceNumber=101
        timestamp=2017-08-26T11\\:04\\:02Z
    """)
    httpserver.expect_ordered_request('/000/000/100.opl').respond_with_data(dedent("""\
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))
    for _ in range(4):
        httpserver.expect_ordered_request('/000/000/101.opl')\
                  .respond_with_data('not a file', status=503)
    httpserver.expect_ordered_request('/000/000/101.opl').respond_with_data(dedent("""\
        n2 x10.0 y23.0
    """))

    with caplog.at_level(logging.ERROR):
        with rserv.ReplicationServer(httpserver.url_for(''), "opl") as svr:
            h = CountingHandler()
            assert 100 == svr.apply_diffs(h, 100, 10000)
            assert h.counts == [1, 1, 0, 0]

    assert 'Error during diff download' in caplog.text
