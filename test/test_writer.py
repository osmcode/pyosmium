from nose.tools import *
import unittest
import tempfile
import os
from contextlib import contextmanager
from datetime import datetime
from collections import OrderedDict
import logging
import sys

import osmium as o

log = logging.getLogger(__name__)

if sys.version_info[0] == 3:
    from datetime import timezone

    def mkdate(*args):
        return datetime(*args, tzinfo=timezone.utc)
else:
    def mkdate(*args):
        return datetime(*args)

@contextmanager
def WriteExpect(expected):
    fname = tempfile.mktemp(dir=tempfile.gettempdir(), suffix='.opl')
    writer = o.SimpleWriter(fname, 1024*1024)
    try:
        yield writer
    finally:
        writer.close()

    with open(fname, 'r') as fd:
        line = fd.readline().strip()
    assert_equals(line, expected)
    os.remove(fname)

class O(object):
    def __init__(self, **params):
        for k,v in params.items():
            setattr(self, k, v)

class TestWriteSimpleAttributes(unittest.TestCase):

    test_data_simple_attr = (
      (O(id=None), '0 v0 dV c0 t i0 u T'),
      (O(visible=None), '0 v0 dV c0 t i0 u T'),
      (O(version=None), '0 v0 dV c0 t i0 u T'),
      (O(uid=None), '0 v0 dV c0 t i0 u T'),
      (O(user=None), '0 v0 dV c0 t i0 u T'),
      (O(timestamp=None), '0 v0 dV c0 t i0 u T'),
      (O(id=1), '1 v0 dV c0 t i0 u T'),
      (O(id=-99), '-99 v0 dV c0 t i0 u T'),
      (O(visible=True), '0 v0 dV c0 t i0 u T'),
      (O(visible=False), '0 v0 dD c0 t i0 u T'),
      (O(version=23), '0 v23 dV c0 t i0 u T'),
      (O(user="Schmidt"), '0 v0 dV c0 t i0 uSchmidt T'),
      (O(user=""), '0 v0 dV c0 t i0 u T'),
      (O(uid=987), '0 v0 dV c0 t i987 u T'),
      (O(timestamp='2012-04-14T20:58:35Z'), '0 v0 dV c0 t2012-04-14T20:58:35Z i0 u T'),
      (O(timestamp=mkdate(2009, 4, 14, 20, 58, 35)), '0 v0 dV c0 t2009-04-14T20:58:35Z i0 u T'),
      (O(timestamp='1970-01-01T00:00:01Z'), '0 v0 dV c0 t1970-01-01T00:00:01Z i0 u T'),
    )

    def test_node_simple_attr(self):
        for node, out in self.test_data_simple_attr:
            with WriteExpect('n' + out + ' x y') as w:
                w.add_node(node)

    def test_way_simple_attr(self):
        for way, out in self.test_data_simple_attr:
            with WriteExpect('w' + out + ' N') as w:
                w.add_way(way)

    def test_relation_simple_attr(self):
        for rel, out in self.test_data_simple_attr:
            with WriteExpect('r' + out + ' M') as w:
                w.add_relation(rel)

class TestWriteTags(unittest.TestCase):

    test_data_tags = (
     (None, 'T'),
     ([], 'T'),
     ({}, 'T'),
     ((("foo", "bar"), ), 'Tfoo=bar'),
     ((("foo", "bar"), ("2", "1")), 'Tfoo=bar,2=1'),
     ({'test' : 'drive'}, 'Ttest=drive'),
     (OrderedDict((('a', 'b'), ('c', '3'))), 'Ta=b,c=3'),
    )

    def test_node_tags(self):
        for tags, out in self.test_data_tags:
            with WriteExpect('n0 v0 dV c0 t i0 u ' + out + ' x y') as w:
                w.add_node(O(tags=tags))

    def test_way_tags(self):
        for tags, out in self.test_data_tags:
            with WriteExpect('w0 v0 dV c0 t i0 u ' + out + ' N') as w:
                w.add_way(O(tags=tags))

    def test_relation_tags(self):
        for tags, out in self.test_data_tags:
            with WriteExpect('r0 v0 dV c0 t i0 u ' + out + ' M') as w:
                w.add_relation(O(tags=tags))


class TestWriteNode(unittest.TestCase):

    def test_location_tuple(self):
        with WriteExpect('n0 v0 dV c0 t i0 u T x1.1234561 y0.1234561') as w:
            w.add_node(O(location=(1.1234561, 0.1234561)))

    def test_location_rounding(self):
        with WriteExpect('n0 v0 dV c0 t i0 u T x30.46 y50.37') as w:
            w.add_node(O(location=(30.46, 50.37)))

    def test_location_none(self):
        with WriteExpect('n0 v0 dV c0 t i0 u T x y') as w:
            w.add_node(O(location=None))

class TestWriteWay(unittest.TestCase):

    def test_node_list(self):
        with WriteExpect('w0 v0 dV c0 t i0 u T Nn1,n2,n3,n-4') as w:
            w.add_way(O(nodes=(1, 2, 3, -4)))

    def test_node_list_none(self):
        with WriteExpect('w0 v0 dV c0 t i0 u T N') as w:
            w.add_way(O(nodes=None))

class TestWriteRelation(unittest.TestCase):

    def test_relation_members(self):
        with WriteExpect('r0 v0 dV c0 t i0 u T Mn34@foo,r200@,w1111@x') as w:
            w.add_relation(O(members=(('n', 34, 'foo'),
                                      ('r', 200, ''),
                                      ('w', 1111, 'x')
                                     )))

    def test_relation_members_None(self):
        with WriteExpect('r0 v0 dV c0 t i0 u T M') as w:
            w.add_relation(O(members=None))

if __name__ == '__main__':
    unittest.main()
