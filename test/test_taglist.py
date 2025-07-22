# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest


@pytest.fixture
def tag_handler(simple_handler):

    def _handle(data, tests):
        tags = {None: None}  # marker that handler hasn't run yet

        def node(n):
            if None in tags:
                del tags[None]
            tags.update(n.tags)
            tests(n)

        simple_handler(data, node=node)

        return tags

    return _handle


def test_empty_taglist_length(tag_handler):
    def tests(n):
        assert 0 == len(n.tags)
        assert not n.tags
        assert str(n.tags) == '{}'
        assert repr(n.tags) == 'osmium.osm.TagList({})'

    tags = tag_handler("n234 x1 y2", tests)
    assert tags == {}


def test_empty_taglist_contains(tag_handler):
    def tests(n):
        assert "a" not in n.tags

    tags = tag_handler("n234 x1 y2", tests)
    assert tags == {}


def test_empty_taglist_get(tag_handler):
    def tests(n):
        assert n.tags.get("foo") is None
        assert n.tags.get("foo", None) is None
        assert "fs" == n.tags.get("foo", "fs")

    tags = tag_handler("n234 x1 y2", tests)
    assert tags == {}


def test_empty_taglist_indexop(tag_handler):
    def tests(n):
        with pytest.raises(KeyError):
            n.tags["foo"]
        with pytest.raises(KeyError):
            n.tags[None]

    tags = tag_handler("n234 x1 y2", tests)
    assert tags == {}


def test_taglist_length(simple_handler):
    data = u"""\
           n1 x0 y0 Ta=a
           n2 Tkeyñ=value
           n3 Tfoo=1ß,bar=2,foobar=33
           """

    lens = {}

    def node(n):
        lens[n.id] = len(n.tags)
        assert n.tags

    simple_handler(data, node=node)

    assert lens == {1: 1, 2: 1, 3: 3}


def test_taglist_contains(tag_handler):
    def tests(n):
        assert "abba" in n.tags
        assert "2" in n.tags
        assert "xx" in n.tags
        assert "x" not in n.tags
        assert None not in n.tags
        assert "" not in n.tags
        assert str(n.tags) == '{abba=x,2=vvv,xx=abba}'
        assert repr(n.tags) == "osmium.osm.TagList({'abba': 'x', '2': 'vvv', 'xx': 'abba'})"

    tags = tag_handler("n234 Tabba=x,2=vvv,xx=abba", tests)

    assert tags == {'abba': 'x', '2': 'vvv', 'xx': 'abba'}


def test_taglist_indexop(tag_handler):
    def tests(n):
        assert "x" == n.tags["abba"]
        assert "vvv" == n.tags["2"]
        assert "abba" == n.tags["xx"]
        for k in ("x", "addad", "..", None):
            with pytest.raises(KeyError):
                n.tags[k]

    tags = tag_handler("n234 Tabba=x,2=vvv,xx=abba", tests)

    assert tags == {'abba': 'x', '2': 'vvv', 'xx': 'abba'}


def test_taglist_indexop_get(tag_handler):
    def tests(n):
        assert "x" == n.tags.get("abba")
        assert "vvv" == n.tags.get("2", None)
        assert "abba" == n.tags.get("xx", "ff")
        assert "43 fg" == n.tags.get("_", "43 fg")
        assert n.tags.get("gerger4") is None
        assert n.tags.get("ffleo", None) is None

    tags = tag_handler("n234 Tabba=x,2=vvv,xx=abba", tests)

    assert tags == {'abba': 'x', '2': 'vvv', 'xx': 'abba'}
