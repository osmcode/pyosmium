# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
from contextlib import contextmanager
from collections import OrderedDict
import uuid

import pytest

import osmium as o

from helpers import mkdate


@pytest.fixture
def test_writer(tmp_path):
    @contextmanager
    def _WriteExpect(filename, expected):
        writer = o.SimpleWriter(str(filename), 1024*1024)
        try:
            yield writer
        finally:
            writer.close()

        assert filename.read_text().strip() == expected


    def _create(expected):
        filename = tmp_path / (str(uuid.uuid4()) + '.opl')
        return _WriteExpect(filename, expected)

    return _create


class O:
    def __init__(self, **params):
        for k,v in params.items():
            setattr(self, k, v)


@pytest.fixture(params=[
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
      (O(timestamp='1970-01-01T00:00:01Z'), '0 v0 dV c0 t1970-01-01T00:00:01Z i0 u T')
    ])
def attr_sample(request):
    return request.param

def test_node_simple_attr(test_writer, attr_sample):
    with test_writer('n' + attr_sample[1] + ' x y') as w:
        w.add_node(attr_sample[0])

def test_way_simple_attr(test_writer, attr_sample):
    with test_writer('w' + attr_sample[1] + ' N') as w:
        w.add_way(attr_sample[0])

def test_relation_simple_attr(test_writer, attr_sample):
    with test_writer('r' + attr_sample[1] + ' M') as w:
        w.add_relation(attr_sample[0])


@pytest.fixture(params = [
     (None, 'T'),
     ([], 'T'),
     ({}, 'T'),
     ((("foo", "bar"), ), 'Tfoo=bar'),
     ((("foo", "bar"), ("2", "1")), 'Tfoo=bar,2=1'),
     ({'test' : 'drive'}, 'Ttest=drive'),
     (OrderedDict((('a', 'b'), ('c', '3'))), 'Ta=b,c=3'),
    ])
def tags_sample(request):
    return request.param

def test_node_tags(test_writer, tags_sample):
    with test_writer('n0 v0 dV c0 t i0 u ' + tags_sample[1] + ' x y') as w:
        w.add_node(O(tags=tags_sample[0]))

def test_way_tags(test_writer, tags_sample):
    with test_writer('w0 v0 dV c0 t i0 u ' + tags_sample[1] + ' N') as w:
        w.add_way(O(tags=tags_sample[0]))

def test_relation_tags(test_writer, tags_sample):
    with test_writer('r0 v0 dV c0 t i0 u ' + tags_sample[1] + ' M') as w:
        w.add_relation(O(tags=tags_sample[0]))


def test_location_tuple(test_writer):
    with test_writer('n0 v0 dV c0 t i0 u T x1.1234561 y0.1234561') as w:
        w.add_node(O(location=(1.1234561, 0.1234561)))

def test_location_rounding(test_writer):
    with test_writer('n0 v0 dV c0 t i0 u T x30.46 y50.37') as w:
        w.add_node(O(location=(30.46, 50.37)))

def test_location_none(test_writer):
    with test_writer('n0 v0 dV c0 t i0 u T x y') as w:
        w.add_node(O(location=None))


def test_node_list(test_writer):
    with test_writer('w0 v0 dV c0 t i0 u T Nn1,n2,n3,n-4') as w:
        w.add_way(O(nodes=(1, 2, 3, -4)))

def test_node_list_none(test_writer):
    with test_writer('w0 v0 dV c0 t i0 u T N') as w:
        w.add_way(O(nodes=None))


def test_relation_members(test_writer):
    with test_writer('r0 v0 dV c0 t i0 u T Mn34@foo,r200@,w1111@x') as w:
        w.add_relation(O(members=(('n', 34, 'foo'),
                                  ('r', 200, ''),
                                  ('w', 1111, 'x')
                                 )))

def test_relation_members_None(test_writer):
    with test_writer('r0 v0 dV c0 t i0 u T M') as w:
        w.add_relation(O(members=None))
