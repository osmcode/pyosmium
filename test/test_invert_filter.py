# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import osmium

from helpers import IDCollector


def test_filter_no_handlers(opl_reader):
    data = """\
        n11 Tfoo=bar
        w34 Twhat=ever
        r99 Tsomething=else
        """

    post = IDCollector()

    osmium.apply(opl_reader(data), osmium.filter.InvertFilter().enable_for(osmium.osm.WAY), post)

    assert post.nodes == [11]
    assert post.ways == []
    assert post.relations == [99]


def test_filter_simple_handler(opl_reader):
    data = """\
        n11 Tfoo=bar
        w34 Twhat=ever
        r99 Tsomething=else
        """

    post = IDCollector()

    filters = osmium.filter.InvertFilter(osmium.filter.KeyFilter('what', 'foo'))

    osmium.apply(opl_reader(data), filters, post)

    assert post.nodes == []
    assert post.ways == []
    assert post.relations == [99]


def test_filter_chained_handler(opl_reader):
    data = """\
        n11 Tfoo=bar
        w34 Twhat=ever
        r99 Twhat=ever,something=else
        """

    post = IDCollector()

    filters = osmium.filter.InvertFilter(
        osmium.filter.KeyFilter('what'),
        osmium.filter.TagFilter(('something', 'else')))

    osmium.apply(opl_reader(data), filters, post)

    assert post.nodes == [11]
    assert post.ways == [34]
    assert post.relations == []


def test_double_invert(opl_reader):
    data = """\
        n11 Tfoo=bar
        w34 Twhat=ever
        r99 Tsomething=else
        """

    post = IDCollector()

    filters = osmium.filter.InvertFilter(
                osmium.filter.InvertFilter(
                    osmium.filter.KeyFilter('what', 'foo')))

    osmium.apply(opl_reader(data), filters, post)

    assert post.nodes == [11]
    assert post.ways == [34]
    assert post.relations == []
