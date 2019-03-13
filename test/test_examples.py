"""
Tests for all examples.
"""
from nose.tools import *
import unittest
import sys
from helpers import load_script
from os import path as osp

TEST_FILE='example-test.pbf'
TEST_DIFF='example-test.osc'

try:
    from StringIO import StringIO
except:
    from io import StringIO

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

def load_example(name):
    return load_script(osp.join(osp.realpath(__file__),
                                "..", "..", "examples", name + ".py"))

def test_amenity_list():
    script = load_example("amenity_list")

    with Capturing() as output:
        eq_(0, script['main'](TEST_FILE))

    eq_(835, len(output))
    eq_('1.535245 42.556681 parking', output[0].strip())
    eq_('1.570729 42.529562 parking         Aparcament Comunal', output[-1].strip())

def test_road_length():
    script = load_example("road_length")

    with Capturing() as output:
        eq_(0, script['main'](TEST_FILE))

    eq_(output, ["Total way length: 1590.82 km"])


def test_pub_names():
    script = load_example("pub_names")

    with Capturing() as output:
        eq_(0, script['main'](TEST_FILE))

    eq_(output, ['Kyu', 'Havana Club', "Mulligan's", 'Bar Broques',
                 'The Camden - English Pub', 'Aspen', 'el Raval'])

def test_osm_diff_stats():
    script = load_example("osm_diff_stats")

    with Capturing() as output:
        eq_(0, script['main'](TEST_DIFF))

    eq_(9, len(output))
    eq_('Nodes added: 305', output[0])
    eq_('Nodes modified: 192', output[1])
    eq_('Nodes deleted: 20', output[2])
    eq_('Ways added: 31', output[3])
    eq_('Ways modified: 93', output[4])
    eq_('Ways deleted: 0', output[5])
    eq_('Relations added: 0', output[6])
    eq_('Relations modified: 0', output[7])
    eq_('Relations deleted: 0', output[8])

def test_osm_file_stats():
    script = load_example("osm_file_stats")

    with Capturing() as output:
        eq_(0, script['main'](TEST_FILE))

    eq_(3, len(output))
    eq_('Nodes: 211100', output[0])
    eq_('Ways: 10315', output[1])
    eq_('Relations: 244', output[2])
