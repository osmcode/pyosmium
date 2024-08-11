# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

def test_set_unset_empty():
    ids = o.index.IdSet()
    assert ids.empty()
    assert not ids

    ids.set(34)
    assert not ids.empty()
    assert ids

    ids.unset(34)
    assert ids.empty()
    assert not ids


def test_set_get():
    ids = o.index.IdSet()

    for i in (1,100,2):
        ids.set(i)

    assert ids.get(100)
    assert not ids.get(3)
    assert 1 in ids
    assert 45 not in ids


def test_clear_and_size():
    ids = o.index.IdSet()

    assert len(ids) == 0

    for i in (1,100,2):
        ids.set(i)

    assert len(ids) == 3

    ids.clear()

    assert len(ids) == 0
