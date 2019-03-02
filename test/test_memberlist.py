# vim: set fileencoding=utf-8 :
from nose.tools import *
import unittest
import os
import sys
from datetime import datetime

from helpers import create_osm_file, osmobj, HandlerTestBase, check_repr

import osmium as o

class TestLength(HandlerTestBase, unittest.TestCase):
    data = """\
           r2 Mn3@
           r4
           r45 Mw1@fo,r45@4,r45@5
           """

    class Handler(o.SimpleHandler):
        expected_length = { 2 : 1, 4 : 0, 45 : 3 }

        def relation(self, r):
            assert_equals(self.expected_length[r.id], len(r.members))

class TestMembers(HandlerTestBase, unittest.TestCase):
    data = u"""r34 Mn23@,n12@foo,w5@.,r34359737784@(ü)"""

    class Handler(o.SimpleHandler):

        def relation(self, r):
            m = list(r.members)
            eq_(4, len(m))
            eq_(23, m[0].ref)
            eq_('n', m[0].type)
            eq_('', m[0].role)
            eq_(12, m[1].ref)
            eq_('n', m[1].type)
            eq_('foo', m[1].role)
            eq_(5, m[2].ref)
            eq_('w', m[2].type)
            eq_('.', m[2].role)
            eq_(34359737784, m[3].ref)
            eq_('r', m[3].type)
            eq_(u'(ü)', m[3].role)
            assert_true(check_repr(m))
