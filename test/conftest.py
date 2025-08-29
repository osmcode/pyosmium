# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from pathlib import Path
import uuid
from textwrap import dedent

import pytest
import osmium


@pytest.fixture
def test_data_dir():
    return (Path(__file__) / '..').resolve()


@pytest.fixture
def to_opl():
    def _make(data):
        if isinstance(data, (list, tuple)):
            return '\n'.join(data)

        return dedent(data)

    return _make


@pytest.fixture
def test_data(tmp_path, to_opl):

    def _mkfile(data):
        filename = tmp_path / (str(uuid.uuid4()) + '.opl')
        filename.write_text(to_opl(data))
        return str(filename)

    return _mkfile


@pytest.fixture
def opl_buffer(to_opl):

    def _mkbuffer(data):
        return osmium.io.FileBuffer(to_opl(data).encode('utf-8'), 'opl')

    return _mkbuffer


@pytest.fixture
def opl_reader(opl_buffer):

    def _mkbuffer(data):
        return osmium.io.Reader(opl_buffer(data))

    return _mkbuffer


@pytest.fixture
def simple_handler(to_opl):

    def _run(data, node=None, way=None, relation=None, area=None, locations=False):
        handler = osmium.make_simple_handler(node=node, way=way, relation=relation, area=area)
        handler.apply_buffer(to_opl(data).encode('utf-8'), 'opl', locations=locations)

    return _run
