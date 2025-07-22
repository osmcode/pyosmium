# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import osmium

import pytest
from helpers import IDCollector


def test_filter_no_keys():
    with pytest.raises(TypeError, match="keys to filter"):
        osmium.filter.KeyFilter()


@pytest.mark.parametrize('key', [None, 1, IDCollector(), 'a'.encode('utf-8')])
def test_filter_bad_argument_types(key):
    with pytest.raises(TypeError, match="must be strings"):
        osmium.filter.KeyFilter("foo", key)


@pytest.mark.parametrize('key,nodes,changesets', [('foo', [1], [10]),
                                                  ('name', [1, 2], [20]),
                                                  ('kö*', [4], [])])
def test_filter_simple(opl_reader, key, nodes, changesets):
    data = """\
           n1 Tfoo=bar,name=loo
           n2 Tname=else
           n3 x9 y0
           n4 Tkö*=fr
           c10 Tfoo=baz
           c20 Tname=none
           """

    post = IDCollector()

    osmium.apply(opl_reader(data), osmium.filter.KeyFilter(key), post)

    assert post.nodes == nodes
    assert post.changesets == changesets
