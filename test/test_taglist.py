# vim: set fileencoding=utf-8 :
from nose.tools import *
import unittest
import os
import sys
from datetime import datetime

from helpers import create_osm_file, osmobj, check_repr, HandlerTestBase

import osmium as o

class TestTagEmptyTagListLength(HandlerTestBase, unittest.TestCase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert_equals(0, len(n.tags))
            assert_false(n.tags)

class TestTagEmptyTagListContains(HandlerTestBase, unittest.TestCase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert_not_in("a", n.tags)

class TestTagEmptyTagListGet(HandlerTestBase, unittest.TestCase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert_equals(None, n.tags.get("foo"))
            assert_equals(None, n.tags.get("foo", None))
            assert_equals("fs", n.tags.get("foo", "fs"))

class TestTagEmptyTagListIndexOp(HandlerTestBase, unittest.TestCase):
    data = "n234 x1 y2"

    class Handler(o.SimpleHandler):

        def node(self, n):
            with assert_raises(KeyError):
                n.tags["foo"]
            with assert_raises(KeyError):
                n.tags[None]

class TestTagListLen(HandlerTestBase, unittest.TestCase):
    data = u"""\
           n1 x0 y0 Ta=a
           n2 Tkeyñ=value
           n3 Tfoo=1ß,bar=2,foobar=33
           """
    class Handler(o.SimpleHandler):

        expected_len = { 1 : 1, 2 : 1, 3 : 3}

        def node(self, n):
            assert_true(n.tags)
            assert_equals(self.expected_len[n.id], len(n.tags))
            assert_true(check_repr(n.tags))

class TestTagContains(HandlerTestBase, unittest.TestCase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            assert_in("abba", n.tags)
            assert_in("2", n.tags)
            assert_in("xx", n.tags)
            assert_not_in("x", n.tags)
            assert_not_in(None, n.tags)
            assert_not_in("", n.tags)
            assert_true(check_repr(n.tags))

class TestTagIndexOp(HandlerTestBase, unittest.TestCase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            eq_("x", n.tags["abba"])
            eq_("vvv", n.tags["2"])
            eq_("abba", n.tags["xx"])
            for k in ("x", "addad", "..", None):
                with assert_raises(KeyError):
                    n.tags[k]

class TestTagGet(HandlerTestBase, unittest.TestCase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            eq_("x", n.tags.get("abba"))
            eq_("vvv", n.tags.get("2", None))
            eq_("abba", n.tags.get("xx", "ff"))
            eq_("43 fg", n.tags.get("_", "43 fg"))
            assert_is_none(n.tags.get("gerger4"))
            assert_is_none(n.tags.get("ffleo", None))

class TestTagToDict(HandlerTestBase, unittest.TestCase):
    data = "n234 Tabba=x,2=vvv,xx=abba"

    class Handler(o.SimpleHandler):

        def node(self, n):
            d = dict(n.tags)
            eq_(len(d), 3)
            eq_(d['abba'], 'x')
            eq_(d['2'], 'vvv')
            eq_(d['xx'], 'abba')
