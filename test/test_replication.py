# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
from io import BytesIO
from textwrap import dedent
from urllib.error import URLError

import pytest
import requests.exceptions

from helpers import mkdate, CountingHandler

import osmium as o
import osmium.replication.server as rserv
import osmium.replication

class RequestsResponses(BytesIO):

    def __init__(self, bytes):
       super(RequestsResponses, self).__init__(bytes)
       self.content = bytes

    def iter_lines(self):
       return self.readlines()


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


class TestReplication:

    @pytest.fixture(params=["requests", "urllib"], autouse=True)
    def setup_mocks(self, request, monkeypatch):
        self.url_requests = []
        self.url_exception = None
        if request.param == "requests":
            # Default use of the requests library. Simply patch the get method.
            def mock_get(*args, **kwargs):
                if self.url_exception is not None:
                    raise self.url_exception
                assert self.url_requests
                return RequestsResponses(self.url_requests.pop(0))
            monkeypatch.setattr(osmium.replication.server.requests.Session, "get", mock_get)

            def mk_server(*args, **kwargs):
                return rserv.ReplicationServer(*args, **kwargs)
            self.mk_replication_server = mk_server

        elif request.param == "urllib":
            def mock_get(*args, **kwargs):
                if self.url_exception is not None:
                    raise self.url_exception
                assert self.url_requests
                return BytesIO(self.url_requests.pop(0))
            def mk_server(*args, **kwargs):
                server = rserv.ReplicationServer(*args, **kwargs)
                server.open_url = mock_get
                return server
            self.mk_replication_server = mk_server


    def set_result(self, content):
        self.url_requests = [dedent(content).encode()]


    def set_script(self, files):
        self.url_requests = [dedent(s).encode() for s in files]


    def test_get_state_valid(self):
        self.set_result("""\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-26T11\\:04\\:02Z
            txnReadyList=
            txnMax=1219304113
            txnActiveList=1219303583,1219304054,1219304104""")

        res = self.mk_replication_server("https://test.io").get_state_info()

        assert res is not None
        assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
        assert res.sequence == 2594669


    def test_get_state_sequence_cut(self):
        self.set_script(("""\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=259""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-26T11\\:04\\:02Z"""))

        res = self.mk_replication_server("https://test.io").get_state_info()

        assert res is not None
        assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
        assert res.sequence == 2594669


    def test_get_state_date_cut(self):
        self.set_script(("""\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-2""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-26T11\\:04\\:02Z"""))

        res = self.mk_replication_server("https://test.io").get_state_info()

        assert res is not None
        assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
        assert res.sequence == 2594669


    def test_get_state_timestamp_cut(self):
        self.set_script(("""\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-26T11\\:04\\:02Z"""))

        res = self.mk_replication_server("https://test.io").get_state_info()

        assert res is not None
        assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
        assert res.sequence == 2594669


    def test_get_state_too_many_retries(self):
        self.set_script(("""\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=""",
            """\
            #Sat Aug 26 11:04:04 UTC 2017
            txnMaxQueried=1219304113
            sequenceNumber=2594669
            timestamp=2017-08-26T11\\:04\\:02Z"""))

        res = self.mk_replication_server("https://test.io").get_state_info()

        assert res is None


    @pytest.mark.parametrize("error", [URLError(reason='Mock'),
                                       requests.exceptions.ConnectTimeout])
    def test_get_state_server_timeout(self, error):
        self.url_exception = error

        svr = self.mk_replication_server("https://test.io")
        assert svr.get_state_info() is None


    def test_apply_diffs_count(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1
            w1
            r1
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000)

        assert h.counts == [1, 1, 1, 0]


    def test_apply_diffs_without_simplify(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 v23
            n1 v24
            w1
            r1
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000, simplify=False)
        assert [2, 1, 1, 0] == h.counts


    def test_apply_diffs_with_simplify(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 v23
            n1 v24
            w1
            r1
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

        h = CountingHandler()
        assert 100 == svr.apply_diffs(h, 100, 10000, simplify=True)
        assert [1, 1, 1, 0] == h.counts


    def test_apply_with_location(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 x10.0 y23.0
            w1 Nn1,n2
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

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
        assert 100 == svr.apply_diffs(h, 100, 10000, idx="flex_mem")

        assert h.counts == [1, 1, 0, 0]


    def test_apply_reader_without_simplify(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 v23
            n1 v24
            w1
            r1
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

        h = CountingHandler()

        diffs = svr.collect_diffs(100, 100000)
        assert diffs is not None

        diffs.reader.apply(h, simplify=False)
        assert [2, 1, 1, 0] == h.counts


    def test_apply_reader_with_simplify(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 v23
            n1 v24
            w1
            r1
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

        h = CountingHandler()
        diffs = svr.collect_diffs(100, 100000)
        assert diffs is not None

        diffs.reader.apply(h, simplify=True)
        assert [1, 1, 1, 0] == h.counts


    def test_apply_reader_with_location(self):
        self.set_script(("""\
            sequenceNumber=100
            timestamp=2017-08-26T11\\:04\\:02Z
        """, """
            n1 x10.0 y23.0
            w1 Nn1,n2
        """))
        svr = self.mk_replication_server("https://test.io", "opl")

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
        diffs = svr.collect_diffs(100, 100000)
        assert diffs is not None

        diffs.reader.apply(h, idx="flex_mem")

        assert h.counts == [1, 1, 0, 0]
