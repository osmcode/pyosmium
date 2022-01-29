# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
""" Tests for the pyosmium-get-changes script.
"""
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from urllib.error import URLError
from unittest.mock import MagicMock, DEFAULT

import pytest
from requests import Session


try:
    import http.cookiejar as cookiejarlib
except ImportError:
    import cookielib as cookiejarlib


class RequestsResponses(BytesIO):

    def __init__(self, bytes):
       super(RequestsResponses, self).__init__(bytes)
       self.content = bytes

    def iter_lines(self):
       return self.readlines()


class TestPyosmiumGetChanges:

    @pytest.fixture(autouse=True)
    def setUp(self, monkeypatch):
        self.script = dict()

        filename = (Path(__file__) / ".." / ".." / "tools"/ "pyosmium-get-changes").resolve()
        with filename.open("rb") as f:
            exec(compile(f.read(), str(filename), 'exec'), self.script)

        self.urls = dict()

        self.url_mock = MagicMock()
        self.url_mock.side_effect = lambda url,data=None,timeout=None : self.urls[url.get_full_url()]
        self.script['rserv'].urlrequest.OpenerDirector.open = self.url_mock

        self.urlreq_mock = MagicMock()
        self.urlreq_mock.side_effect = lambda url,**kw : self.urls[url]
        self.script['rserv'].requests.Session.get = self.urlreq_mock


    def url(self, url, result):
        self.urls[url] = RequestsResponses(dedent(result).encode())

    def main(self, *args):
        return self.script['main'](args)

    def test_init_id(self, capsys):
        assert 0 == self.main('-I', '453')

        output = capsys.readouterr().out.strip()

        assert output == '454'


    def test_init_date(self, capsys):
        self.url('https://planet.osm.org/replication/minute//state.txt',
                 """\
                    sequenceNumber=100
                    timestamp=2017-08-26T11\\:04\\:02Z
                 """)
        self.url('https://planet.osm.org/replication/minute//000/000/000.state.txt',
                 """\
                    sequenceNumber=0
                    timestamp=2016-08-26T11\\:04\\:02Z
                 """)
        assert 0 == self.main('-D', '2015-12-24T08:08:08Z')

        output = capsys.readouterr().out.strip()

        assert output == '1'


    def test_init_to_file(self, tmp_path):
        fname = tmp_path / 'db.seq'

        assert 0 == self.main('-I', '453', '-f', str(fname))
        assert fname.read_text() == '454'


    def test_init_from_seq_file(self, tmp_path):
        fname = tmp_path / 'db.seq'
        fname.write_text('453')

        assert 0 == self.main('-f', str(fname))
        assert fname.read_text() == '454'


    def test_init_date_with_cookie(self, capsys, tmp_path):
        self.url('https://planet.osm.org/replication/minute//state.txt',
                 """\
                    sequenceNumber=100
                    timestamp=2017-08-26T11\\:04\\:02Z
                 """)
        self.url('https://planet.osm.org/replication/minute//000/000/000.state.txt',
                 """\
                    sequenceNumber=0
                    timestamp=2016-08-26T11\\:04\\:02Z
                 """)

        fname = tmp_path / 'my.cookie'
        cookie_jar = cookiejarlib.MozillaCookieJar(str(fname))
        cookie_jar.save()

        assert 0 == self.main('--cookie', str(fname), '-D', '2015-12-24T08:08:08Z')

        output = capsys.readouterr().out.strip()

        assert output == '1'
