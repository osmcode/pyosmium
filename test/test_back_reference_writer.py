# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

from helpers import IDCollector

def test_simple_way(test_data, tmp_path):
    ref_file = test_data('\n'.join((f"n{i} x2 y3" for i in range(10))))

    class TestWay:
        id = 34
        nodes = [3, 6, 5]

    outfile = str(tmp_path / 'test.osm')

    with o.BackReferenceWriter(outfile, ref_file) as writer:
        writer.add_way(TestWay())

    ids = IDCollector()
    o.apply(outfile, ids)

    assert ids.nodes == [3, 5, 6]
    assert ids.ways == [34]
    assert not ids.relations


def test_do_not_write_on_exception(test_data, tmp_path):
    ref_file = test_data('\n'.join((f"n{i} x2 y3" for i in range(10))))
    outfile = tmp_path / 'test.osm'

    with pytest.raises(RuntimeError, match="inner error"):
        with o.BackReferenceWriter(str(outfile), ref_file) as writer:
            raise RuntimeError("inner error")

    assert not outfile.exists()
