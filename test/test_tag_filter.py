# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium
from helpers import IDCollector


def test_tag_filter_no_keys():
    with pytest.raises(TypeError, match="tags to filter"):
        osmium.filter.TagFilter()


@pytest.mark.parametrize('kv', ['something', 'so', ('a', 'b', 'c'),
                                (None, 'a'), ('a', None),
                                (34, 'a'), ('a', 0)])
def test_tag_filter_bad_arguments(kv):
    with pytest.raises(TypeError, match="Each tag must be a tuple"):
        osmium.filter.TagFilter(kv)


@pytest.mark.parametrize('tags,filt', [('foo=bar', [('foo', 'bar')]),
                                       ('a=1,b=2', [('x', 'x'), ('a', '1')]),
                                       ('a=1,b=2', [('x', 'x'), ('b', '2')])
                                       ])
def test_tag_filter_pass(opl_reader, tags, filt):
    data = f"""\
            n1 T{tags}
            w2 T{tags}
            r3 T{tags}
            c4 T{tags}
            """

    ids = IDCollector()

    osmium.apply(opl_reader(data), osmium.filter.TagFilter(*filt), ids)

    assert ids.nodes == [1]
    assert ids.ways == [2]
    assert ids.relations == [3]
    assert ids.changesets == [4]


@pytest.mark.parametrize('tags,filt', [('foo=bar', [('foo', 'bars')]),
                                       ('a=1,b=2', [('x', 'x'), ('a', '2')])
                                       ])
def test_tag_filter_fail(opl_reader, tags, filt):
    data = f"""\
            n1 T{tags}
            w2 T{tags}
            r3 T{tags}
            c4 T{tags}
            """

    ids = IDCollector()

    osmium.apply(opl_reader(data), osmium.filter.TagFilter(*filt), ids)

    assert ids.nodes == []
    assert ids.ways == []
    assert ids.relations == []
    assert ids.changesets == []


@pytest.fixture
def tag_filter_stream():
    tags = [(('foo', 'bar'),), (('foo', 'baz'),), (),
            (('name', 'test'), ('foo', 'bar')),
            (('name', 'test'),), (('empty', ''),)]
    objects = [(kind, i, values) for kind in 'nwrc'
               for i, values in enumerate(tags, 1)]
    data = '\n'.join(f'{kind}{i}' +
                     (' T' + ','.join(f'{k}={v}' for k, v in values)
                      if values else '')
                     for kind, i, values in objects)
    return data, objects


class OrderedCollector:
    def __init__(self):
        self.objects = []

    def node(self, obj):
        self.objects.append(('n', obj.id))

    def way(self, obj):
        self.objects.append(('w', obj.id))

    def relation(self, obj):
        self.objects.append(('r', obj.id))

    def changeset(self, obj):
        self.objects.append(('c', obj.id))


@pytest.mark.parametrize('pairs', [(('foo', 'bar'),),
                                   (('foo', 'bar'), ('name', 'test')),
                                   (('empty', ''),)])
@pytest.mark.parametrize('invert', [False, True])
def test_tag_filter_inverse_complement(opl_reader, tag_filter_stream, pairs, invert):
    data, objects = tag_filter_stream
    collector = OrderedCollector()
    osmium.apply(opl_reader(data), osmium.filter.TagFilter(*pairs, invert=invert),
                 collector)

    # Independent classification of source tuples, including untagged objects.
    expected = [(kind, i) for kind, i, tags in objects
                if any(pair in tags for pair in pairs) != invert]
    assert collector.objects == expected


@pytest.mark.parametrize('invert', [False, True])
@pytest.mark.parametrize('entities', [osmium.osm.NOTHING,
                                      osmium.osm.NODE | osmium.osm.RELATION,
                                      osmium.osm.ALL])
def test_tag_filter_inverse_entity_restriction(opl_reader, tag_filter_stream,
                                               invert, entities):
    data, objects = tag_filter_stream
    filt = osmium.filter.TagFilter(('foo', 'bar'), invert=invert)
    assert filt.enable_for(entities) is filt
    collector = OrderedCollector()
    osmium.apply(opl_reader(data), filt, collector)

    bits = dict(n=osmium.osm.NODE, w=osmium.osm.WAY,
                r=osmium.osm.RELATION, c=osmium.osm.CHANGESET)
    expected = [(kind, i) for kind, i, tags in objects
                if not (entities & bits[kind]) or
                ((('foo', 'bar') in tags) != invert)]
    assert collector.objects == expected


def test_tag_filter_inverse_chaining(opl_reader, tag_filter_stream):
    data, objects = tag_filter_stream
    seen = OrderedCollector()
    remaining = OrderedCollector()
    osmium.apply(opl_reader(data),
                 osmium.filter.TagFilter(('foo', 'bar'), invert=True), seen,
                 osmium.filter.TagFilter(('name', 'test')), remaining)
    assert seen.objects == [(kind, i) for kind, i, tags in objects
                            if ('foo', 'bar') not in tags]
    assert remaining.objects == [(kind, i) for kind, i, tags in objects
                                 if ('foo', 'bar') not in tags and
                                 ('name', 'test') in tags]


def test_tag_filter_inverse_file_processor(opl_buffer):
    fp = osmium.FileProcessor(opl_buffer('n1 Tfoo=bar\nn2\nw3 Tfoo=baz\nr4 Tfoo=bar'))\
               .with_filter(osmium.filter.TagFilter(('foo', 'bar'), invert=True))
    assert [(obj.type_str(), obj.id) for obj in fp] == [('n', 2), ('w', 3)]


@pytest.mark.parametrize('bad', ['tag', ('one',), (None, 'value'), ['foo', 'bar']])
def test_tag_filter_inverse_preserves_validation(bad):
    with pytest.raises(TypeError, match='Each tag must be a tuple'):
        osmium.filter.TagFilter(bad, invert=True)


def test_tag_filter_inverse_requires_tags():
    with pytest.raises(TypeError, match='tags to filter'):
        osmium.filter.TagFilter(invert=True)


def test_tag_filter_inverse_is_keyword_only():
    with pytest.raises(TypeError, match='Each tag must be a tuple'):
        osmium.filter.TagFilter(('foo', 'bar'), True)


def test_tag_filter_inverse_bad_keyword():
    with pytest.raises(TypeError):
        osmium.filter.TagFilter(('foo', 'bar'), invert='yes')
