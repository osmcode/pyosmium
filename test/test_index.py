from nose.tools import *
import unittest

import osmium as o

class TestIndexMapTypes(unittest.TestCase):

    def runTest(self):
        ml = o.index.map_types()
        assert_true(isinstance(ml, list))
        assert_greater(len(ml), 0)
