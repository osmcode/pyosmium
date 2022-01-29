# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
"""
Tests for all examples.
"""
from pathlib import Path

TEST_DIR = (Path(__file__) / '..').resolve()
TEST_FILE = TEST_DIR / 'example-test.pbf'
TEST_DIFF = TEST_DIR / 'example-test.osc'


def run_example(name, *args):
    filename = (TEST_DIR / '..' / "examples" / (name + ".py")).resolve()
    globvars = dict()

    with filename.open("rb") as f:
        exec(compile(f.read(), str(filename), 'exec'), globvars)

    return globvars['main'](*args)


def test_amenity_list(capsys):
    assert 0 == run_example("amenity_list", TEST_FILE)

    output = capsys.readouterr().out.splitlines()

    assert 835 == len(output)
    assert '1.535245 42.556681 parking' == output[0].strip()
    assert '1.570729 42.529562 parking         Aparcament Comunal' == output[-1].strip()


def test_road_length(capsys):
    assert 0 == run_example("road_length", TEST_FILE)

    output = capsys.readouterr().out.strip()

    assert output == "Total way length: 1590.82 km"


def test_pub_names(capsys):
    assert 0 == run_example("pub_names", TEST_FILE)

    output = capsys.readouterr().out.splitlines()

    assert output == ['Kyu', 'Havana Club', "Mulligan's", 'Bar Broques',
                      'The Camden - English Pub', 'Aspen', 'el Raval']


def test_osm_diff_stats(capsys):
    assert 0 == run_example("osm_diff_stats", TEST_DIFF)

    output = capsys.readouterr().out.splitlines()

    assert output == ['Nodes added: 305',
                     'Nodes modified: 192',
                     'Nodes deleted: 20',
                     'Ways added: 31',
                     'Ways modified: 93',
                     'Ways deleted: 0',
                     'Relations added: 0',
                     'Relations modified: 0',
                     'Relations deleted: 0']


def test_osm_file_stats(capsys):
    assert 0 == run_example("osm_file_stats", TEST_FILE)

    output = capsys.readouterr().out.splitlines()

    assert output == ['Nodes: 211100',
                      'Ways: 10315',
                      'Relations: 244']
