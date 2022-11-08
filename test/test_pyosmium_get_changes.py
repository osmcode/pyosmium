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

import pytest
import osmium.replication.server

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


    @pytest.fixture
    def mock_requests(self, monkeypatch):
        def mock_get(session, url, **kwargs):
            return RequestsResponses(self.urls[url])
        monkeypatch.setattr(osmium.replication.server.requests.Session, "get", mock_get)


    def url(self, url, result):
        self.urls[url] = dedent(result).encode()

    def main(self, *args):
        return self.script['main'](args)


    def test_init_id(self, capsys):
        assert 0 == self.main('-I', '453')

        output = capsys.readouterr().out.strip()

        assert output == '453'


    def test_init_date(self, capsys, mock_requests):
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

        assert output == '-1'


    def test_init_to_file(self, tmp_path):
        fname = tmp_path / 'db.seq'

        assert 0 == self.main('-I', '453', '-f', str(fname))
        assert fname.read_text() == '453'


    def test_init_from_seq_file(self, tmp_path):
        fname = tmp_path / 'db.seq'
        fname.write_text('453')

        assert 0 == self.main('-f', str(fname))
        assert fname.read_text() == '453'


    def test_init_date_with_cookie(self, capsys, tmp_path, mock_requests):
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

        assert output == '-1'
