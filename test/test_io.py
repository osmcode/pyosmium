import os

import pytest

from helpers import create_osm_file, osmobj

import osmium as o

class TestReaderFromFile:

    def _run_file(self, fn):
        try:
            rd = o.io.Reader(fn)
            o.apply(rd, o.SimpleHandler())
            rd.close()
        finally:
            os.remove(fn)

    def test_node_only(self):
        self._run_file(create_osm_file([osmobj('N', id=1)]))

    def test_way_only(self):
        self._run_file(create_osm_file([osmobj('W', id=1, nodes=[1,2,3])]))

    def test_relation_only(self):
        self._run_file(create_osm_file([osmobj('R', id=1, members=[('way', 1, '')])]))

    def test_node_with_tags(self):
        self._run_file(create_osm_file([osmobj('N', id=1, 
                                               tags=dict(foo='bar', name='xx'))]))

    def test_way_with_tags(self):
        self._run_file(create_osm_file([osmobj('W', id=1, nodes=[1,2,3],
                                               tags=dict(foo='bar', name='xx'))]))

    def test_relation_with_tags(self):
        self._run_file(create_osm_file([osmobj('R', id=1, members=[('way', 1, '')],
                                               tags=dict(foo='bar', name='xx'))]))

    def test_broken_timestamp(self):
        fn = create_osm_file([osmobj('N', id=1, timestamp='x')])
        try:
            rd = o.io.Reader(fn)
            with pytest.raises(ValueError):
                o.apply(rd, o.SimpleHandler())
                rd.close()
        finally:
            os.remove(fn)


def test_file_header():
    fn = create_osm_file([osmobj('N', id=1)])
    try:
        rd = o.io.Reader(fn)
        h = rd.header()
        assert not h.has_multiple_object_versions
        assert h.box().valid()
        assert h.box().size() == 64800.0
        rd.close()
    finally:
        os.remove(fn)
