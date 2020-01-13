# vim: set fileencoding=utf-8 :
from nose.tools import *
import unittest
from sys import version_info as python_version

from helpers import create_osm_file

import osmium as o

class DanglingReferenceBase(object):
    """ Base class for tests that try to keep a reference to the object
        that was handed into the callback. We expect that the handler
        bails out with a runtime error in such a case.
    """


    node = None
    way = None
    relation = None
    area = None
    refkeeper = []

    def keep(self, obj):
        self.refkeeper.append(obj)

    def test_keep_reference(self):
        h = o.make_simple_handler(node=self.node, way=self.way,
                                  relation=self.relation, area=self.area)
        if python_version < (3,0):
            with self.assertRaisesRegexp(RuntimeError, "callback keeps reference"):
                h.apply_file('example-test.pbf')
        else:
            with self.assertRaisesRegex(RuntimeError, "callback keeps reference"):
                h.apply_file('example-test.pbf')
        assert_greater(len(self.refkeeper), 0)
        while len(self.refkeeper) > 0:
            self.refkeeper.pop()
#        self.refkeeper.clear()


class TestKeepNodeRef(DanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n)

class TestKeepWayRef(DanglingReferenceBase, unittest.TestCase):

    def way(self, w):
        self.keep(w)

class TestKeepRelationRef(DanglingReferenceBase, unittest.TestCase):

    def relation(self, r):
        self.keep(r)

class TestKeepAreaRef(DanglingReferenceBase, unittest.TestCase):

    def area(self, a):
        self.keep(a)

class TestKeepNodeTagsRef(DanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.tags)

class TestKeepWayTagsRef(DanglingReferenceBase, unittest.TestCase):

    def way(self, w):
        self.keep(w.tags)

class TestKeepRelationTagsRef(DanglingReferenceBase, unittest.TestCase):

    def relation(self, r):
        self.keep(r.tags)

class TestKeepAreaTagsRef(DanglingReferenceBase, unittest.TestCase):

    def area(self, a):
        self.keep(a.tags)

class TestKeepTagListIterator(DanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.tags.__iter__())

class TestKeepSingleTag(DanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        for t in n.tags:
            self.keep(t)

class TestKeepOuterRingIterator(DanglingReferenceBase, unittest.TestCase):

    def area(self, r):
        self.keep(r.outer_rings())

class TestKeepOuterRing(DanglingReferenceBase, unittest.TestCase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(ring)

class TestKeepInnerRingIterator(DanglingReferenceBase, unittest.TestCase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(r.inner_rings(ring))

class TestKeepInnerRing(DanglingReferenceBase, unittest.TestCase):

    def area(self, r):
        for outer in r.outer_rings():
            for inner in r.inner_rings(outer):
                self.keep(inner)

class TestKeepRelationMemberIterator(DanglingReferenceBase, unittest.TestCase):

    def relation(self, r):
        self.keep(r.members)

class TestKeepRelationMember(DanglingReferenceBase, unittest.TestCase):

    def relation(self, r):
        for m in r.members:
            self.keep(m)


class NotADanglingReferenceBase(object):
    """ Base class for tests that ensure that the callback does not
        bail out because of dangling references when POD types are
        kept.
    """

    node = None
    way = None
    relation = None
    area = None
    refkeeper = []

    def keep(self, obj):
        self.refkeeper.append(obj)

    def test_keep_reference(self):
        h = o.make_simple_handler(node=self.node, way=self.way,
                                  relation=self.relation, area=self.area)
        # Does not rise a dangling reference excpetion
        h.apply_file('example-test.pbf')
        assert_greater(len(self.refkeeper), 0)
        #self.refkeeper.clear()
        while len(self.refkeeper) > 0:
            self.refkeeper.pop()

class TestKeepId(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.id)

class TestKeepChangeset(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.changeset)

class TestKeepUid(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.uid)

class TestKeepUser(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.user)

class TestKeepLocation(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        self.keep(n.location)

class TestKeepKey(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        for t in n.tags:
            self.keep(t.k)

class TestKeepValue(NotADanglingReferenceBase, unittest.TestCase):

    def node(self, n):
        for t in n.tags:
            self.keep(t.v)
