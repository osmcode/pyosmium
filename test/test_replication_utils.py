# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.

import osmium.replication.utils as rutil

from helpers import mkdate

def test_get_replication_header_empty(tmp_path):
    fn = tmp_path / 'test.opl'
    fn.write_text('n6365 v1 c63965061 t2018-10-29T03:56:07Z i8369524 ux x1 y7')

    val = rutil.get_replication_header(str(fn))
    assert val.url is None
    assert val.sequence is None
    assert val.timestamp is None


def test_get_replication_header_full(test_data_dir):
    val = rutil.get_replication_header(str(test_data_dir / 'example-test.pbf'))

    assert val.url == 'http://download.geofabrik.de/europe/andorra-updates'
    assert val.sequence == 2167
    assert val.timestamp == mkdate(2019, 2, 23, 21, 15, 2)
