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

    def keep(self, obj, func):
        self.refkeeper.append((obj, func))

    def test_keep_reference(self):
        h = o.make_simple_handler(node=self.node, way=self.way,
                                  relation=self.relation, area=self.area)
        h.apply_file(TEST_DIR / 'example-test.osc')
        assert self.refkeeper

        for obj, func in self.refkeeper:
            with pytest.raises(RuntimeError, match="removed OSM object"):
                func(obj)
            # str() and repr() must not throw errors
            str(obj)
            repr(obj)

    def test_keep_reference_generator(self):
        for obj in o.FileProcessor(TEST_DIR / 'example-test.osc').with_areas():
            if obj.type_str() == 'n' and self.node is not None:
                self.node(obj)
            elif obj.type_str() == 'w' and self.way is not None:
                self.way(obj)
            elif obj.type_str() == 'r' and self.relation is not None:
                self.relation(obj)
            elif obj.type_str() == 'a' and self.area is not None:
                self.area(obj)

        assert self.refkeeper

        for obj, func in self.refkeeper:
            with pytest.raises(RuntimeError, match="removed OSM object"):
                func(obj)
            # str() and repr() must not throw errors
            str(obj)
            repr(obj)


class TestKeepNodeRef(DanglingReferenceBase):

    def node(self, n):
        self.keep(n, lambda n: n.id)

class TestKeepWayRef(DanglingReferenceBase):

    def way(self, w):
        self.keep(w, lambda n: n.id)

class TestKeepRelationRef(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r, lambda n: n.id)

class TestKeepAreaRef(DanglingReferenceBase):

    def area(self, a):
        self.keep(a, lambda n: n.id)

class TestKeepNodeTagsRef(DanglingReferenceBase):

    def node(self, n):
        self.keep(n.tags, lambda t: 'foo' in t)

class TestKeepWayTagsRef(DanglingReferenceBase):

    def way(self, w):
        self.keep(w.tags, lambda t: 'foo' in t)

class TestKeepRelationTagsRef(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r.tags, lambda t: 'foo' in t)

class TestKeepAreaTagsRef(DanglingReferenceBase):

    def area(self, a):
        self.keep(a.tags, lambda t: 'foo' in t)

class TestKeepTagListIterator(DanglingReferenceBase):

    def node(self, n):
        self.keep(n.tags.__iter__(), lambda t: next(t))

class TestKeepOuterRingIterator(DanglingReferenceBase):

    def area(self, r):
        self.keep(r.outer_rings(), lambda t: next(t))

class TestKeepOuterRing(DanglingReferenceBase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(ring, lambda t: len(t))

class TestKeepInnerRingIterator(DanglingReferenceBase):

    def area(self, r):
        for ring in r.outer_rings():
            self.keep(r.inner_rings(ring), lambda t: next(t))

class TestKeepInnerRing(DanglingReferenceBase):

    def area(self, r):
        for outer in r.outer_rings():
            for inner in r.inner_rings(outer):
                self.keep(inner, lambda t: len(t))

class TestKeepRelationMemberIterator(DanglingReferenceBase):

    def relation(self, r):
        self.keep(r.members, lambda t: next(t))



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

    def keep(self, obj, func):
        self.refkeeper.append((obj, func))

    def test_keep_reference(self):
        h = o.make_simple_handler(node=self.node, way=self.way,
                                  relation=self.relation, area=self.area)
        h.apply_file(TEST_DIR / 'example-test.pbf')
        assert self.refkeeper

        for obj, func in self.refkeeper:
            func(obj)

    def test_keep_reference_generator(self):
        for obj in o.FileProcessor(TEST_DIR / 'example-test.pbf').with_areas():
            if obj.is_node() and self.node is not None:
                self.node(obj)
            elif obj.is_way() and self.way is not None:
                self.way(obj)
            elif obj.is_relation() and self.relation is not None:
                self.relation(obj)
            elif obj.is_area() and self.area is not None:
                self.area(obj)

        assert self.refkeeper

        for obj, func in self.refkeeper:
            func(obj)


class TestKeepLocation(NotADanglingReferenceBase):

    def node(self, n):
        self.keep(n.location, lambda l: l.x)

class TestKeepNode(NotADanglingReferenceBase):

    def node(self, n):
        for t in n.tags:
            self.keep(t, lambda t: t.k)

class TestKeepMember(NotADanglingReferenceBase):

    def relation(self, r):
        for m in r.members:
            self.keep(m, lambda m: m.ref)
