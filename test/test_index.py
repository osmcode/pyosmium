from nose.tools import *
import unittest

import osmium as o

class TestIndexMapTypes(unittest.TestCase):

    def test_list_types(self):
        ml = o.index.map_types()
        assert_true(isinstance(ml, list))
        assert_greater(len(ml), 0)


class TestLocationTable(unittest.TestCase):

    def setUp(self):
        self.table = o.index.create_map("flex_mem")

    def test_set_get(self):
        self.table.set(4, o.osm.Location(3.4, -5.6))
        l = self.table.get(4)
        assert_almost_equal(3.4, l.lon, 5)
        assert_almost_equal(-5.6, l.lat, 5)

    def test_get_unset(self):
        with assert_raises(KeyError):
            self.table.get(56)

    def test_set_negative(self):
        with assert_raises(TypeError):
            self.table.set(-4, o.osm.Location(3.4, -5.6))

    def test_used_memory(self):
        self.table.set(4, o.osm.Location(3.4, -5.6))
        assert_greater(self.table.used_memory(), 0)

    def test_clear(self):
        self.table.set(593, o.osm.Location(0.35, 45.3))
        self.table.get(593)
        self.table.clear()
        with assert_raises(KeyError):
            self.table.get(593)

