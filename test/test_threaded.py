# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import threading

from helpers import CountingHandler


def test_threaded_processing():
    """ Process a file in a different thread and make sure that processing
        completes.
    """
    function_complete = threading.Event()
    c = CountingHandler()

    def import_data():
        c.apply_buffer('n1 x67.8 y-45.6932'.encode('utf-8'), 'opl')
        function_complete.set()

    t = threading.Thread(target=import_data)
    t.start()
    function_complete.wait(timeout=2)

    assert function_complete.is_set()
    assert c.counts == [1, 0, 0, 0]
