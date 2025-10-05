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

import pytest

import osmium
from osmium.tools.pyosmium_get_changes import pyosmium_get_changes

from helpers import IDCollector

try:
    import http.cookiejar as cookiejarlib
except ImportError:
    import cookielib as cookiejarlib


class TestPyosmiumGetChanges:

    def main(self, httpserver, *args):
        return pyosmium_get_changes(['--server', httpserver.url_for('')] + list(args))

    def test_init_id(self, capsys, httpserver):
        assert 0 == self.main(httpserver, '-I', '453')

        output = capsys.readouterr().out.strip()

        assert output == '453'

    def test_init_date(self, capsys, httpserver):
        httpserver.expect_request('/state.txt').respond_with_data(dedent("""\
                    sequenceNumber=100
                    timestamp=2017-08-26T11\\:04\\:02Z
                 """))
        httpserver.expect_request('/000/000/000.state.txt').respond_with_data(dedent("""\
                    sequenceNumber=0
                    timestamp=2016-08-26T11\\:04\\:02Z
                 """))
        assert 0 == self.main(httpserver, '-D', '2015-12-24T08:08:08Z')

        output = capsys.readouterr().out.strip()

        assert output == '-1'

    def test_init_to_file(self, tmp_path, httpserver):
        fname = tmp_path / f"{uuid.uuid4()}.seq"

        assert 0 == self.main(httpserver, '-I', '453', '-f', str(fname))
        assert fname.read_text() == '453'

    def test_init_from_seq_file(self, tmp_path, httpserver):
        fname = tmp_path / f"{uuid.uuid4()}.seq"
        fname.write_text('453')

        assert 0 == self.main(httpserver, '-f', str(fname))
        assert fname.read_text() == '453'

    def test_init_date_with_cookie(self, capsys, tmp_path, httpserver):
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

        assert 0 == self.main(httpserver, '--cookie', str(fname),
                              '-D', '2015-12-24T08:08:08Z')

        output = capsys.readouterr().out.strip()

        assert output == '-1'

    def test_get_simple_update(self, tmp_path, httpserver):
        outfile = tmp_path / f"{uuid.uuid4()}.opl"

        httpserver.expect_request('/state.txt').respond_with_data(dedent("""\
                    sequenceNumber=454
                    timestamp=2017-08-26T11\\:04\\:02Z
                 """))
        httpserver.expect_request('/000/000/454.state.txt').respond_with_data(dedent("""\
                    sequenceNumber=454
                    timestamp=2016-08-26T11\\:04\\:02Z
                 """))
        httpserver.expect_request('/000/000/454.opl').respond_with_data(
                 "n12 v1 x4 y6\nn13 v1 x9 y-6\nw2 v2 Nn1,n2")

        assert 0 == self.main(httpserver, '--diff-type', 'opl',
                              '-I', '453', '-o', str(outfile))

        ids = IDCollector()
        osmium.apply(str(outfile), ids)

        assert ids.nodes == [12, 13]
        assert ids.ways == [2]
        assert ids.relations == []

    @pytest.mark.parametrize('end_id,max_size,actual_end', [(107, None, 107),
                                                            (None, 1, 108),
                                                            (105, 1, 105),
                                                            (110, 1, 108)])
    def test_apply_diffs_endid(self, tmp_path, httpserver, end_id, max_size, actual_end):
        outfile = tmp_path / f"{uuid.uuid4()}.opl"

        httpserver.expect_request('/state.txt').respond_with_data("""\
            sequenceNumber=140
            timestamp=2017-08-26T11\\:04\\:02Z
        """)
        for i in range(100, 141):
            httpserver.expect_request(f'/000/000/{i}.opl')\
                      .respond_with_data(f"r{i} M" + ",".join(f"n{i}@" for i in range(1, 6000)))

        params = [httpserver, '--diff-type', 'opl', '-I', '100', '-o', str(outfile)]
        if end_id is not None:
            params.extend(('--end-id', str(end_id)))
        if max_size is not None:
            params.extend(('-s', str(max_size)))

        assert 0 == self.main(*params)

        ids = IDCollector()
        osmium.apply(str(outfile), ids)

        assert ids.relations == list(range(101, actual_end + 1))
