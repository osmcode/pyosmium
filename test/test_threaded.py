# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
import os
import threading

from helpers import create_osm_file, osmobj, HandlerTestBase, CountingHandler
import osmium as o

def import_data(function_complete):
    data = [osmobj('N', id=1, lat=28.0, lon=-23.3)]
    fn = create_osm_file(data)

    c = CountingHandler()
    try:
        c.apply_file(fn)
    finally:
        os.remove(fn)

    function_complete.set()


def test_threaded_processing():
    """ Process a file in a different thread and make sure that processing
        completes.
    """

    function_complete = threading.Event()
    t = threading.Thread(target=import_data, args=(function_complete,))
    t.start()
    function_complete.wait(timeout=2)

    assert function_complete.is_set()


