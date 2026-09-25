# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from textwrap import dedent
import uuid

import pytest

import osmium


class ListHandler:
    def __init__(self):
        self.data = []

    def node(self, o):
        self.data.append(f"N{o.id}/{o.version}")

    def way(self, o):
        self.data.append(f"W{o.id}/{o.version}")

    def relation(self, o):
        self.data.append(f"R{o.id}/{o.version}")

    def area(self, _):
        assert not "Area handler should not be called"


def add_as_buffer(mir, opl, tmp_path):
    mir.add_buffer(dedent(opl).encode('utf-8'), format='opl')


def add_as_file(mir, opl, tmp_path):
    fn = tmp_path / (str(uuid.uuid4()) + '.opl')
    fn.write_text(dedent(opl))

    mir.add_file(str(fn))


@pytest.mark.parametrize('adder', [add_as_buffer, add_as_file])
def test_simple_input(adder, tmp_path):
    mir = osmium.MergeInputReader()

    opl = """\
        n1 v1 x1 y1
        w3 v34 Nn1
        """

    adder(mir, opl, tmp_path)

    h = ListHandler()
    mir.apply(h)

    assert h.data == ['N1/1', 'W3/34']


@pytest.mark.parametrize('adder', [add_as_buffer, add_as_file])
def test_multibuffer_no_simplify(adder, tmp_path):
    mir = osmium.MergeInputReader()

    opls = ["""\
            n1 v1 x1 y1
            w3 v2 Nn1
            """,
            """\
            n2 v1 x1 y1
            w3 v1 Nn2
            """]

    for opl in opls:
        adder(mir, opl, tmp_path)

    h = ListHandler()
    mir.apply(h, simplify=False)

    assert h.data == ['N1/1', 'N2/1', 'W3/1', 'W3/2']


@pytest.mark.parametrize('adder', [add_as_buffer, add_as_file])
def test_multibuffer_simplify(adder, tmp_path):
    mir = osmium.MergeInputReader()

    opls = ["""\
            n1 v1 x1 y1
            w3 v2 Nn1
            """,
            """\
            n2 v1 x1 y1
            w3 v1 Nn2
            """]

    for opl in opls:
        adder(mir, opl, tmp_path)

    h = ListHandler()
    mir.apply(h, simplify=True)

    assert h.data == ['N1/1', 'N2/1', 'W3/2']


def test_simplify_same_id_different_object(tmp_path):
    mir = osmium.MergeInputReader()

    opls = ["""\
            n1 v1 x1 y1
            n2 v1 x90 y45
            w1 v1 Nn1,n2
            r1 v1 Mw1@
            """,
            """\
            r1 v2 Mw1@ Thello=world
            """]

    for opl in opls:
        add_as_file(mir, opl, tmp_path)

    h = ListHandler()
    mir.apply(h, simplify=True)

    assert h.data == ['N1/1', 'N2/1', 'W1/1', 'R1/2']


def test_apply_to_reader_nohistory(test_data, tmp_path):
    fn = test_data("""\
            n1 v1 x1 y1
            n2 v1 x90 y45
            w1 v1 Nn1,n2
            r1 v1 Mw1@
            """)

    outfn = tmp_path / 'outfile_apply_to_reader_nohistory.opl'

    reader = osmium.io.Reader(fn)
    writer = osmium.io.Writer(outfn)

    mir = osmium.MergeInputReader()
    add_as_buffer(mir, "r1 v2 Mw1@ Thello=world", tmp_path)

    mir.apply_to_reader(reader, writer, False)

    reader.close()
    writer.close()

    h = ListHandler()
    osmium.apply(outfn, h)

    assert h.data == ['N1/1', 'N2/1', 'W1/1', 'R1/2']


def test_apply_to_reader_with_history(test_data, tmp_path):
    fn = test_data("""\
            n1 v1 x1 y1
            n2 v1 x90 y45
            w1 v1 Nn1,n2
            r1 v1 Mw1@
            """)

    outfn = tmp_path / 'outfile_apply_to_reader_nohistory.opl'

    reader = osmium.io.Reader(fn)
    writer = osmium.io.Writer(outfn)

    mir = osmium.MergeInputReader()
    add_as_buffer(mir, "r1 v2 Mw1@ Thello=world", tmp_path)

    mir.apply_to_reader(reader, writer, True)

    reader.close()
    writer.close()

    h = ListHandler()
    osmium.apply(outfn, h)

    assert h.data == ['N1/1', 'N2/1', 'W1/1', 'R1/1', 'R1/2']
