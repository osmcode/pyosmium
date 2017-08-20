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
            eq_(0, w.nodes[-1].ref)

class TestMissingRef(HandlerTestBase, unittest.TestCase):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """

    class Handler(o.SimpleHandler):

        def way(self, w):
            eq_(1, w.nodes[0].ref)
            assert_false(w.nodes[0].location.valid())
            with assert_raises(o.InvalidLocationError):
                w.nodes[0].location.lat
            with assert_raises(o.InvalidLocationError):
                w.nodes[0].location.lon

class TestValidRefs(HandlerTestBase, unittest.TestCase):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """
    apply_locations = True

    class Handler(o.SimpleHandler):

        def way(self, w):
            eq_(1, w.nodes[0].ref)
            assert_true(w.nodes[0].location.valid())
            assert_almost_equal(w.nodes[0].location.lat, 10.0)
            assert_almost_equal(w.nodes[0].location.lon, 0.5)
