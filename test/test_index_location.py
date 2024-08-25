# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
import pytest
import osmium as o

def test_list_types():
    ml = o.index.map_types()
    assert isinstance(ml, list)
    assert ml


@pytest.fixture
def table():
    return o.index.create_map("flex_mem")

@pytest.mark.parametrize('use_get', [True, False])
@pytest.mark.parametrize('use_set', [True, False])
def test_set_get(table, use_set, use_get):
    if use_set:
        table.set(4, o.osm.Location(3.4, -5.6))
    else:
        table[4] = o.osm.Location(3.4, -5.6)
    if use_get:
        l = table.get(4)
    else:
        l = table[4]
    assert l.lon == pytest.approx(3.4)
    assert l.lat == pytest.approx(-5.6)

def test_get_unset(table):
    with pytest.raises(KeyError):
        table.get(56)

def test_array_get_unset(table):
    with pytest.raises(KeyError):
        table[56]

def test_set_negative(table):
    with pytest.raises(TypeError):
        table.set(-4, o.osm.Location(3.4, -5.6))

def test_array_set_negative(table):
    with pytest.raises(TypeError):
        table[-4] = o.osm.Location(3.4, -5.6)

def test_used_memory(table):
    table.set(4, o.osm.Location(3.4, -5.6))

    assert table.used_memory() > 0

def test_clear(table):
    table.set(593, o.osm.Location(0.35, 45.3))
    table.get(593)
    table.clear()
    with pytest.raises(KeyError):
        table.get(593)
