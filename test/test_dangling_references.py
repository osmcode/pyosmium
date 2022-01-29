# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.

from pathlib import Path

import pytest

TEST_DIR = (Path(__file__) / '..').resolve()

import osmium as o

class DanglingReferenceBase:
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
        with pytest.raises(RuntimeError, match="callback keeps reference"):
              h.apply_file(TEST_DIR / 'example-test.pbf')
        assert self.refkeeper
        while len(self.refkeeper) > 0:
            self.refkeeper.pop()


class TestKeepNodeRef(DanglingReferenceBase):

    def node(self, n):
        self.keep(n)

class TestKeepWayRef(DanglingReferenceBase):

    def way(self, w):
        self.keep(w)

class TestKeepRelationRef(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r)

class TestKeepAreaRef(DanglingReferenceBase):

    def area(self, a):
        self.keep(a)

class TestKeepNodeTagsRef(DanglingReferenceBase):

    def node(self, n):
        self.keep(n.tags)

class TestKeepWayTagsRef(DanglingReferenceBase):

    def way(self, w):
        self.keep(w.tags)

class TestKeepRelationTagsRef(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r.tags)

class TestKeepAreaTagsRef(DanglingReferenceBase):

    def area(self, a):
        self.keep(a.tags)

class TestKeepTagListIterator(DanglingReferenceBase):

    def node(self, n):
        self.keep(n.tags.__iter__())

class TestKeepSingleTag(DanglingReferenceBase):

    def node(self, n):
        for t in n.tags:
            self.keep(t)

class TestKeepOuterRingIterator(DanglingReferenceBase):

    def area(self, r):
        self.keep(r.outer_rings())

class TestKeepOuterRing(DanglingReferenceBase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(ring)

class TestKeepInnerRingIterator(DanglingReferenceBase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(r.inner_rings(ring))

class TestKeepInnerRing(DanglingReferenceBase):

    def area(self, r):
        for outer in r.outer_rings():
            for inner in r.inner_rings(outer):
                self.keep(inner)

class TestKeepRelationMemberIterator(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r.members)

class TestKeepRelationMember(DanglingReferenceBase):

    def relation(self, r):
        for m in r.members:
            self.keep(m)


class NotADanglingReferenceBase:
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
        h.apply_file(TEST_DIR / 'example-test.pbf')
        assert self.refkeeper
        while len(self.refkeeper) > 0:
            self.refkeeper.pop()

class TestKeepId(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.id)

class TestKeepChangeset(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.changeset)

class TestKeepUid(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.uid)

class TestKeepUser(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.user)

class TestKeepLocation(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.location)

class TestKeepKey(NotADanglingReferenceBase):

    def node(self, n):
        for t in n.tags:
            self.keep(t.k)

class TestKeepValue(NotADanglingReferenceBase):

    def node(self, n):
        for t in n.tags:
            self.keep(t.v)
