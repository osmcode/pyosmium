"""
Tests for all examples.
"""
import sys
from helpers import load_script
from io import StringIO
from pathlib import Path

TEST_DIR = (Path(__file__) / '..').resolve()
TEST_FILE = TEST_DIR / 'example-test.pbf'
TEST_DIFF = TEST_DIR / 'example-test.osc'


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
    return load_script((TEST_DIR / '..' / "examples" / (name + ".py")).resolve())

def test_amenity_list():
    script = load_example("amenity_list")

    with Capturing() as output:
        assert 0 == script['main'](TEST_FILE)

    assert 835 == len(output)
    assert '1.535245 42.556681 parking' == output[0].strip()
    assert '1.570729 42.529562 parking         Aparcament Comunal' == output[-1].strip()

def test_road_length():
    script = load_example("road_length")

    with Capturing() as output:
        assert 0 == script['main'](TEST_FILE)

    assert output == ["Total way length: 1590.82 km"]


def test_pub_names():
    script = load_example("pub_names")

    with Capturing() as output:
        assert 0 == script['main'](TEST_FILE)

    assert output == ['Kyu', 'Havana Club', "Mulligan's", 'Bar Broques',
                      'The Camden - English Pub', 'Aspen', 'el Raval']

def test_osm_diff_stats():
    script = load_example("osm_diff_stats")

    with Capturing() as output:
        assert 0 == script['main'](TEST_DIFF)

    assert 9 == len(output)
    assert 'Nodes added: 305' == output[0]
    assert 'Nodes modified: 192' == output[1]
    assert 'Nodes deleted: 20' == output[2]
    assert 'Ways added: 31' == output[3]
    assert 'Ways modified: 93' == output[4]
    assert 'Ways deleted: 0' == output[5]
    assert 'Relations added: 0' == output[6]
    assert 'Relations modified: 0' == output[7]
    assert 'Relations deleted: 0'== output[8]

def test_osm_file_stats():
    script = load_example("osm_file_stats")

    with Capturing() as output:
        assert 0 == script['main'](TEST_FILE)

    assert 3 == len(output)
    assert 'Nodes: 211100' == output[0]
    assert 'Ways: 10315' == output[1]
    assert 'Relations: 244' == output[2]
