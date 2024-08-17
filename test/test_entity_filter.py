# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import pytest

import osmium as o

from helpers import CountingHandler

@pytest.mark.parametrize('ent,cnt', [(o.osm.NODE, (1, 0, 0)),
                                     (o.osm.NODE | o.osm.WAY, (1, 1, 0)),
                                     (o.osm.ALL, (1, 1, 1))])
def test_entity_filter_simple(opl_reader, ent, cnt):
    data = """\
           n1 Ttype=node
           w1 Ttype=way
           r1 Ttype=rel
           """

    processed = CountingHandler()

    o.apply(opl_reader(data), o.filter.EntityFilter(ent), processed)

    assert list(cnt) == processed.counts[:3]
