# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium
from helpers import CountingHandler


@pytest.mark.parametrize('ent,cnt', [(osmium.osm.NODE, (1, 0, 0)),
                                     (osmium.osm.NODE | osmium.osm.WAY, (1, 1, 0)),
                                     (osmium.osm.ALL, (1, 1, 1))])
def test_entity_filter_simple(opl_reader, ent, cnt):
    data = """\
           n1 Ttype=node
           w1 Ttype=way
           r1 Ttype=rel
           """

    processed = CountingHandler()

    osmium.apply(opl_reader(data), osmium.filter.EntityFilter(ent), processed)

    assert list(cnt) == processed.counts[:3]
