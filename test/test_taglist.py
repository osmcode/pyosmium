# vim: set fileencoding=utf-8 :
import pytest

from helpers import create_osm_file, osmobj, check_repr, HandlerTestBase

import osmium as o

class TestTagEmptyTagListLength(HandlerTestBase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert 0 == len(n.tags)
            assert not n.tags

class TestTagEmptyTagListContains(HandlerTestBase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert "a" not in n.tags

class TestTagEmptyTagListGet(HandlerTestBase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert None == n.tags.get("foo")
            assert None == n.tags.get("foo", None)
            assert "fs" == n.tags.get("foo", "fs")

class TestTagEmptyTagListIndexOp(HandlerTestBase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            with pytest.raises(KeyError):
                n.tags["foo"]
            with pytest.raises(KeyError):
                n.tags[None]

class TestTagListLen(HandlerTestBase):
    data = u"""\
           n1 x0 y0 Ta=a
           n2 Tkeyñ=value
           n3 Tfoo=1ß,bar=2,foobar=33
           """
    class Handler(o.SimpleHandler):

        expected_len = { 1 : 1, 2 : 1, 3 : 3}

        def node(self, n):
            assert n.tags
            assert self.expected_len[n.id], len(n.tags)
            assert check_repr(n.tags)

class TestTagContains(HandlerTestBase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert "abba" in n.tags
            assert "2" in n.tags
            assert "xx" in n.tags
            assert "x" not in n.tags
            assert None not in n.tags
            assert "" not in n.tags
            assert check_repr(n.tags)

class TestTagIndexOp(HandlerTestBase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert "x" == n.tags["abba"]
            assert "vvv" == n.tags["2"]
            assert "abba" == n.tags["xx"]
            for k in ("x", "addad", "..", None):
                with pytest.raises(KeyError):
                    n.tags[k]

class TestTagGet(HandlerTestBase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert "x" == n.tags.get("abba")
            assert "vvv" == n.tags.get("2", None)
            assert "abba" == n.tags.get("xx", "ff")
            assert "43 fg" == n.tags.get("_", "43 fg")
            assert n.tags.get("gerger4") is None
            assert n.tags.get("ffleo", None) is None

class TestTagToDict(HandlerTestBase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            d = dict(n.tags)
            assert len(d) == 3
            assert d['abba'] == 'x'
            assert d['2'] == 'vvv'
            assert d['xx'] == 'abba'
