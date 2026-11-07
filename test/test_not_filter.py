# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import gc
import weakref

import pytest

import osmium
from helpers import IDCollector


@pytest.mark.parametrize('kind,attribute', [('n', 'nodes'), ('w', 'ways'),
                                            ('r', 'relations'), ('c', 'changesets')])
def test_inverse_tag_filter(opl_reader, kind, attribute):
    ids = IDCollector()
    osmium.apply(opl_reader([f'{kind}1 Ta=1', f'{kind}2 Ta=2', f'{kind}3']),
                 osmium.filter.NotFilter(osmium.filter.TagFilter(('a', '1'))), ids)
    assert getattr(ids, attribute) == [2, 3]


def test_inverse_whole_chain_and_nested_inverse(opl_buffer):
    data = opl_buffer('n1 Ta=1,b=2\nn2 Ta=1\nn3 Tb=2\nn4')
    inverse = osmium.filter.NotFilter(osmium.filter.KeyFilter('a'),
                                      osmium.filter.TagFilter(('b', '2')))
    assert [n.id for n in osmium.FileProcessor(data).with_filter(inverse)] == [2, 3, 4]
    double_inverse = osmium.filter.NotFilter(inverse)
    assert [n.id for n in osmium.FileProcessor(data).with_filter(double_inverse)] == [1]


@pytest.mark.parametrize('make_filter', [
    lambda: osmium.filter.IdFilter([1]),
    lambda: osmium.filter.EmptyTagFilter(),
    lambda: osmium.filter.EntityFilter(osmium.osm.NODE),
])
def test_other_native_filters(opl_buffer, make_filter):
    data = opl_buffer('n1 Ta=1\nn2\nw3 Ta=1\nr4\nc5')
    original = [o.id for o in osmium.FileProcessor(data).with_filter(make_filter())]
    inverse = [o.id for o in osmium.FileProcessor(data).with_filter(
        osmium.filter.NotFilter(make_filter()))]
    assert sorted(original + inverse) == [1, 2, 3, 4, 5]
    assert set(original).isdisjoint(inverse)


def test_callback_order_and_short_circuit(opl_reader):
    calls = []

    class First:
        def node(self, node):
            calls.append(('first', node.id))
            return node.id == 1

    class Second:
        def node(self, node):
            calls.append(('second', node.id))
            return node.id == 2

    ids = IDCollector()
    osmium.apply(opl_reader('n1\nn2\nn3'), osmium.filter.NotFilter(First(), Second()), ids)
    assert ids.nodes == [1, 2]
    assert calls == [('first', 1), ('first', 2), ('second', 2),
                     ('first', 3), ('second', 3)]


@pytest.mark.parametrize('value,expected', [(None, []), (False, []), (1, []), (True, [1])])
def test_python_callback_return_protocol(opl_reader, value, expected):
    class Predicate:
        def node(self, _):
            return value

    ids = IDCollector()
    osmium.apply(opl_reader('n1'), osmium.filter.NotFilter(Predicate()), ids)
    assert ids.nodes == expected


def test_outer_type_restriction(opl_reader):
    inverse = osmium.filter.NotFilter(osmium.filter.KeyFilter('a'))
    inverse.enable_for(osmium.osm.NODE)
    ids = IDCollector()
    osmium.apply(opl_reader('n1 Ta=1\nn2\nw3 Ta=1\nw4'), inverse, ids)
    assert ids.nodes == [2]
    assert ids.ways == [3, 4]


def test_inner_type_restriction(opl_reader):
    inner = osmium.filter.KeyFilter('a')
    inner.enable_for(osmium.osm.NODE)
    ids = IDCollector()
    osmium.apply(opl_reader('n1 Ta=1\nn2\nw3 Ta=1\nw4'),
                 osmium.filter.NotFilter(inner), ids)
    assert ids.nodes == [2]
    assert ids.ways == []


def test_retains_and_releases_python_handler(opl_reader):
    class Predicate:
        def node(self, _):
            return True

    handler = Predicate()
    reference = weakref.ref(handler)
    inverse = osmium.filter.NotFilter(handler)
    del handler
    gc.collect()
    assert reference() is not None
    ids = IDCollector()
    osmium.apply(opl_reader('n1'), inverse, ids)
    assert ids.nodes == [1]
    del inverse
    gc.collect()
    assert reference() is None


def test_retains_temporary_nested_native_filters(opl_reader):
    inverse = osmium.filter.NotFilter(osmium.filter.NotFilter(osmium.filter.KeyFilter('a')))
    gc.collect()
    ids = IDCollector()
    osmium.apply(opl_reader('n1 Ta=1\nn2'), inverse, ids)
    assert ids.nodes == [1]


@pytest.mark.parametrize('depth', [1, 3])
def test_collects_owner_cycle(opl_reader, depth):
    class Predicate:
        def node(self, _):
            return True

    handler = Predicate()
    wrapper = osmium.filter.NotFilter(handler)
    wrappers = [weakref.ref(wrapper)]
    for _ in range(depth - 1):
        wrapper = osmium.filter.NotFilter(wrapper)
        wrappers.append(weakref.ref(wrapper))
    handler.owner = wrapper
    reference = weakref.ref(handler)
    gc.collect()
    # An externally live wrapper must retain the entire chain, even when only
    # that wrapper owns the Python callback and the callback points back.
    del handler
    gc.collect()
    assert reference() is not None
    ids = IDCollector()
    osmium.apply(opl_reader('n1'), wrapper, ids)
    assert ids.nodes == [1]
    del wrapper
    gc.collect()
    assert reference() is None
    assert all(ref() is None for ref in wrappers)


def test_collects_subclass_cycle():
    class Wrapper(osmium.filter.NotFilter):
        pass

    class Predicate:
        def node(self, _):
            return True

    handler = Predicate()
    wrapper = Wrapper(handler)
    wrapper.extra = handler
    handler.owner = wrapper
    handler_ref, wrapper_ref = weakref.ref(handler), weakref.ref(wrapper)
    del handler, wrapper
    gc.collect()
    assert handler_ref() is None
    assert wrapper_ref() is None


def test_gc_before_initialization():
    wrapper = osmium.filter.NotFilter.__new__(osmium.filter.NotFilter)
    reference = weakref.ref(wrapper)
    gc.collect()
    del wrapper
    gc.collect()
    assert reference() is None


def test_constructor_validation():
    with pytest.raises(TypeError, match='at least one filter'):
        osmium.filter.NotFilter()
    for invalid in (None, 1, 'a', [osmium.filter.KeyFilter('a')]):
        with pytest.raises(TypeError, match='handler-like'):
            osmium.filter.NotFilter(invalid)


def test_failed_constructor_releases_handler():
    class Predicate:
        def node(self, _):
            return False

    handler = Predicate()
    reference = weakref.ref(handler)
    with pytest.raises(TypeError, match='handler-like'):
        osmium.filter.NotFilter(handler, None)
    del handler
    gc.collect()
    assert reference() is None


def test_callback_exception_propagates(opl_reader):
    class Predicate:
        def node(self, _):
            raise ValueError('predicate failed')

    with pytest.raises(ValueError, match='predicate failed'):
        osmium.apply(opl_reader('n1'), osmium.filter.NotFilter(Predicate()), IDCollector())


def test_area_dispatch(opl_buffer):
    class Predicate:
        def area(self, _):
            return True

    data = opl_buffer('n1 x0 y0\nn2 x1 y0\nn3 x0 y1\nw1 Ta=1 Nn1,n2,n3,n1')
    objects = osmium.FileProcessor(data).with_areas().with_filter(
        osmium.filter.NotFilter(Predicate()))
    assert [o.id for o in objects if o.is_area()] == [2]


def test_geometry_side_effects_are_preserved(opl_buffer):
    inverse = osmium.filter.NotFilter(osmium.filter.GeoInterfaceFilter(),
                                      osmium.filter.KeyFilter('missing'))
    objects = osmium.FileProcessor(opl_buffer('n1 x3 y4')).with_filter(inverse)
    for node in objects:
        assert node.id == 1
        assert node.__geo_interface__['geometry'] == {'type': 'Point', 'coordinates': (3, 4)}
        break
    else:
        pytest.fail('inverted chain should retain the node and its geometry')


def test_invalid_geometry_can_be_inverted(opl_buffer):
    objects = osmium.FileProcessor(opl_buffer('n1\nn2 x3 y4')).with_filter(
        osmium.filter.NotFilter(osmium.filter.GeoInterfaceFilter()))
    assert [node.id for node in objects] == [1]
