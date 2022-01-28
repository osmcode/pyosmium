import pytest

from helpers import create_osm_file, osmobj, HandlerTestBase

import osmium as o

class TestLength(HandlerTestBase):
    data = """\
           w593
           w4 Nn1,n2,n-34
           w8 Nn12,n12,n12,n0
           """

    class Handler(o.SimpleHandler):
        expected_length = { 593 : 0, 4 : 3, 8 : 4 }

        def way(self, w):
            assert self.expected_length[w.id] == len(w.nodes)

class TestNodeIds(HandlerTestBase):
    data = """w4 Nn1,n1,n34359737784,n-34,n0"""

    class Handler(o.SimpleHandler):

        def way(self, w):
            assert 1 == w.nodes[0].ref
            assert 1 == w.nodes[1].ref
            assert 34359737784 == w.nodes[2].ref
            assert -34 == w.nodes[3].ref
            assert 0 == w.nodes[4].ref
            assert 0 == w.nodes[-1].ref

class TestMissingRef(HandlerTestBase):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """

    class Handler(o.SimpleHandler):

        def way(self, w):
            assert 1 == w.nodes[0].ref
            assert not w.nodes[0].location.valid()
            with pytest.raises(o.InvalidLocationError):
                w.nodes[0].location.lat
            with pytest.raises(o.InvalidLocationError):
                w.nodes[0].location.lon

class TestValidRefs(HandlerTestBase):
    data = """\
           n1 x0.5 y10.0
           w4 Nn1
           """
    apply_locations = True

    class Handler(o.SimpleHandler):

        def way(self, w):
            assert 1 == w.nodes[0].ref
            assert w.nodes[0].location.valid()
            assert w.nodes[0].location.lat == pytest.approx(10.0)
            assert w.nodes[0].location.lon == pytest.approx(0.5)
