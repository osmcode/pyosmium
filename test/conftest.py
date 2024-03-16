# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
from io import StringIO
from pathlib import Path
import sys
import sysconfig
import uuid
from textwrap import dedent

SRC_DIR = (Path(__file__) / '..' / '..').resolve()

BUILD_DIR = "build/lib.{}-{}.{}".format(sysconfig.get_platform(),
                                        sys.version_info[0], sys.version_info[1])
if not (SRC_DIR / BUILD_DIR).exists():
    BUILD_DIR = "build/lib.{}-{}".format(sysconfig.get_platform(),
                                            sys.implementation.cache_tag)

if (SRC_DIR / BUILD_DIR).exists():
    sys.path.insert(0, str(SRC_DIR))
    sys.path.insert(0, str(SRC_DIR / BUILD_DIR))

import pytest

import osmium as o

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
        return o.io.FileBuffer(to_opl(data).encode('utf-8'), 'opl')

    return _mkbuffer

@pytest.fixture
def opl_reader(opl_buffer):

    def _mkbuffer(data):
        return o.io.Reader(opl_buffer(data))

    return _mkbuffer

@pytest.fixture
def simple_handler(to_opl):

    def _run(data, node=None, way=None, relation=None, area=None, locations=False):
        handler = o.make_simple_handler(node=node, way=way, relation=relation, area=area)
        handler.apply_buffer(to_opl(data).encode('utf-8'), 'opl', locations=locations)

    return _run
