
from nose.tools import *
import unittest
import os
import sys
from datetime import datetime

from helpers import create_osm_file, osmobj, HandlerTestBase

import osmium as o

class TestLength(HandlerTestBase, unittest.TestCase):
    data = """\
           w593
           w4 Nn1,n2,n-34
           w8 Nn12,n12,n12,n0
           """

    class Handler(o.SimpleHandler):
        expected_length = { 593 : 0, 4 : 3, 8 : 4 }

        def way(self, w):
            assert_equals(self.expected_length[w.id], len(w.nodes))

class TestNodeIds(HandlerTestBase, unittest.TestCase):
    data = """w4 Nn1,n1,n34359737784,n-34,n0"""

    class Handler(o.SimpleHandler):

        def way(self, w):
            eq_(1, w.nodes[0].ref)
            eq_(1, w.nodes[1].ref)
            eq_(34359737784, w.nodes[2].ref)
            eq_(-34, w.nodes[3].ref)
            eq_(0, w.nodes[4].ref)
