from io import BytesIO
import os
from textwrap import dedent

import pytest

from helpers import mkdate, osmobj, create_osm_file, CountingHandler

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

import osmium as o
import osmium.replication.server as rserv
import osmium.replication.utils as rutil
import osmium.replication
import tempfile
import datetime

class RequestsResponses(BytesIO):

    def __init__(self, bytes):
       super(RequestsResponses, self).__init__(bytes)
       self.content = bytes

    def iter_lines(self):
       return self.readlines()

class UrllibMock(MagicMock):

    def set_result(self, s):
        self.return_value = RequestsResponses(dedent(s).encode())

    def set_script(self, files):
        self.side_effect = [RequestsResponses(dedent(s).encode()) for s in files]

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

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_valid(mock):
    mock.set_result("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z
        txnReadyList=
        txnMax=1219304113
        txnActiveList=1219303583,1219304054,1219304104""")

    res = rserv.ReplicationServer("https://test.io").get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669

    assert mock.call_count == 1

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_sequence_cut(mock):
    mock.set_script(("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=259""",
        """\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z"""))

    res = rserv.ReplicationServer("https://test.io").get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669

    assert mock.call_count == 2

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_date_cut(mock):
    mock.set_script(("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-2""",
        """\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z"""))

    res = rserv.ReplicationServer("https://test.io").get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669

    assert mock.call_count == 2

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_timestamp_cut(mock):
    mock.set_script(("""\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=""",
        """\
        #Sat Aug 26 11:04:04 UTC 2017
        txnMaxQueried=1219304113
        sequenceNumber=2594669
        timestamp=2017-08-26T11\\:04\\:02Z"""))

    res = rserv.ReplicationServer("https://test.io").get_state_info()

    assert res is not None
    assert res.timestamp == mkdate(2017, 8, 26, 11, 4, 2)
    assert res.sequence == 2594669

    assert mock.call_count == 2

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_too_many_retries(mock):
    mock.set_script(("""\
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

    res = rserv.ReplicationServer("https://test.io").get_state_info()

    assert res is None

    assert mock.call_count == 3



@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_get_state_server_timeout(mock):
    mock.side_effect = URLError(reason='Mock')

    svr = rserv.ReplicationServer("https://test.io")
    assert svr.get_state_info() is None

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_diffs_count(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1
        w1
        r1
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

    h = CountingHandler()
    assert 100 == svr.apply_diffs(h, 100, 10000)

    assert h.counts == [1, 1, 1, 0]

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_diffs_without_simplify(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 v23
        n1 v24
        w1
        r1
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

    h = CountingHandler()
    assert 100 == svr.apply_diffs(h, 100, 10000, simplify=False)
    assert [2, 1, 1, 0] == h.counts

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_diffs_with_simplify(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 v23
        n1 v24
        w1
        r1
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

    h = CountingHandler()
    assert 100 == svr.apply_diffs(h, 100, 10000, simplify=True)
    assert [1, 1, 1, 0] == h.counts

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_with_location(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

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



@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_reader_without_simplify(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 v23
        n1 v24
        w1
        r1
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

    h = CountingHandler()

    diffs = svr.collect_diffs(100, 100000)
    assert diffs is not None

    diffs.reader.apply(h, simplify=False)
    assert [2, 1, 1, 0] == h.counts

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_reader_with_simplify(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 v23
        n1 v24
        w1
        r1
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

    h = CountingHandler()
    diffs = svr.collect_diffs(100, 100000)
    assert diffs is not None

    diffs.reader.apply(h, simplify=True)
    assert [1, 1, 1, 0] == h.counts

@patch('osmium.replication.server.requests.Session.get', new_callable=UrllibMock)
def test_apply_reader_with_location(mock):
    mock.set_script(("""\
        sequenceNumber=100
        timestamp=2017-08-26T11\\:04\\:02Z
    """, """
        n1 x10.0 y23.0
        w1 Nn1,n2
    """))
    svr = rserv.ReplicationServer("https://test.io", "opl")

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

def test_get_newest_change_from_file():
    data = [osmobj('N', id=1, version=1, changeset=63965061, uid=8369524,
                   timestamp='2018-10-29T03:56:07Z', user='x')]
    fn = create_osm_file(data)


    try:
        val = osmium.replication.newest_change_from_file(fn)
        assert val == mkdate(2018, 10, 29, 3, 56, 7)
    finally:
        os.remove(fn)

def test_get_replication_header_empty():
    data = [osmobj('N', id=1, version=1, changeset=63965061, uid=8369524,
                   timestamp='2018-10-29T03:56:07Z', user='x')]
    fn = create_osm_file(data)

    try:
        val = rutil.get_replication_header(fn)
        assert val.url is None
        assert val.sequence is None
        assert val.timestamp is None
    finally:
        os.remove(fn)
