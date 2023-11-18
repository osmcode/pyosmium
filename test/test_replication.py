# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2023 Sarah Hoffmann.
import logging
import time
from textwrap import dedent

import pytest

from werkzeug.wrappers import Response

from helpers import mkdate, CountingHandler

import osmium as o
import osmium.replication.server as rserv
import osmium.replication


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


def test_get_newest_change_from_file(tmp_path):
    fn = tmp_path / 'change.opl'
    fn.write_text('n6365 v1 c63965061 t2018-10-29T03:56:07Z i8369524 ux x1 y7')

    val = osmium.replication.newest_change_from_file(str(fn))
    assert val == mkdate(2018, 10, 29, 3, 56, 7)


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
            assert None == svr.apply_diffs(h, 100, 10000)
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


def test_apply_diffs_transient_error(httpserver, caplog):
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
