# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

from helpers import IDCollector

def test_tag_filter_no_keys():
    with pytest.raises(TypeError, match="tags to filter"):
        o.filter.TagFilter()


@pytest.mark.parametrize('kv', ['something', 'so', ('a', 'b', 'c'),
                                (None, 'a'), ('a', None),
                                (34, 'a'), ('a', 0)])
def test_tag_filter_bad_arguments(kv):
    with pytest.raises(TypeError, match="Each tag must be a tuple"):
        o.filter.TagFilter(kv)

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

    o.apply(opl_reader(data), o.filter.TagFilter(*filt), ids)

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

    o.apply(opl_reader(data), o.filter.TagFilter(*filt), ids)

    assert ids.nodes == []
    assert ids.ways == []
    assert ids.relations == []
    assert ids.changesets == []
