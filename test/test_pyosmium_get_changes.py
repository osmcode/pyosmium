""" Tests for the pyosmium-get-changes script.
"""

from helpers import load_script
from nose.tools import *
import unittest
from io import BytesIO
from os import path as osp
from textwrap import dedent
import sys
import tempfile
from os import unlink

try:
    from cStringIO import StringIO
except:
    from io import StringIO

from requests import Session

try:
    import http.cookiejar as cookiejarlib
except ImportError:
    import cookielib as cookiejarlib

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

try:
    from unittest.mock import MagicMock, DEFAULT
except ImportError:
    from mock import MagicMock, DEFAULT

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class RequestsResponses(BytesIO):

    def __init__(self, bytes):
       super(RequestsResponses, self).__init__(bytes)
       self.content = bytes

    def iter_lines(self):
       return self.readlines()

class TestPyosmiumGetChanges(unittest.TestCase):

    def setUp(self):
        self.script = load_script(osp.join(osp.realpath(__file__),
                                           "../../tools/pyosmium-get-changes"))
        self.url_mock = MagicMock()
        self.urls = dict()
        self.url_mock.side_effect = lambda url,data=None,timeout=None : self.urls[url.get_full_url()]
        self.script['rserv'].urlrequest.OpenerDirector.open = self.url_mock

        self.urlreq_mock = MagicMock()
        self.urlreq_mock.side_effect = lambda url,**kw : self.urls[url]
        self.script['rserv'].requests.Session.get = self.urlreq_mock

    def url(self, url, result):
        self.urls[url] = RequestsResponses(dedent(result).encode())

    def main(self, *args):
        with Capturing() as output:
            ret = self.script['main'](args)
            self.stdout = output
        return ret

    def test_init_id(self):
        assert_equals(0, self.main('-I', '453'))
        assert_equals(1, len(self.stdout))
        assert_equals('454', self.stdout[0])

    def test_init_date(self):
        self.url('https://planet.osm.org/replication/minute//state.txt',
                 """\
                    sequenceNumber=100
                    timestamp=2017-08-26T11\:04\:02Z
                 """)
        self.url('https://planet.osm.org/replication/minute//000/000/000.state.txt',
                 """\
                    sequenceNumber=0
                    timestamp=2016-08-26T11\:04\:02Z
                 """)
        assert_equals(0, self.main('-D', '2015-12-24T08:08:08Z'))
        assert_equals(1, len(self.stdout))
        assert_equals('1', self.stdout[0])

    def test_init_to_file(self):
        fd = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), suffix='.seq', delete=False)
        fname = fd.name
        fd.close()

        assert_equals(0, self.main('-I', '453', '-f', fd.name))
        fd = open(fname, 'r')
        content = fd.read()
        try:
            assert_equals('454', content)
        finally:
            fd.close()
            unlink(fname)

    def test_init_from_seq_file(self):
        with tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), suffix='.seq', delete=False) as fd:
            fd.write('453'.encode('utf-8'))
            fname = fd.name

        assert_equals(0, self.main('-f', fname))
        fd = open(fname, 'r')
        content = fd.read()
        try:
            assert_equals('454', content)
        finally:
            fd.close()
            unlink(fname)

    def test_init_date_with_cookie(self):
        self.url('https://planet.osm.org/replication/minute//state.txt',
                 """\
                    sequenceNumber=100
                    timestamp=2017-08-26T11\:04\:02Z
                 """)
        self.url('https://planet.osm.org/replication/minute//000/000/000.state.txt',
                 """\
                    sequenceNumber=0
                    timestamp=2016-08-26T11\:04\:02Z
                 """)

        with tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), suffix='.cookie', delete=False) as fd:
            fname = fd.name
        cookie_jar = cookiejarlib.MozillaCookieJar(fname)
        cookie_jar.save()

        try:
            assert_equals(0, self.main('--cookie', fname, '-D', '2015-12-24T08:08:08Z'))
            assert_equals(1, len(self.stdout))
            assert_equals('1', self.stdout[0])
        finally:
            unlink(fname)
