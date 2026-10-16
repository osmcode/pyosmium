# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
# Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import multiprocessing
import sys

import pytest
import osmium


def run_interrupted_read(pipe, object_type, opl, exception_type):
    constructor = object_type.__init__.__code__

    def fail_constructor(frame, event, arg):
        if event == 'call' and frame.f_code is constructor:
            sys.settrace(None)
            raise exception_type('injected constructor failure')
        return fail_constructor

    sys.settrace(fail_constructor)
    try:
        list(osmium.FileProcessor(osmium.io.FileBuffer(opl.encode('utf-8'), 'opl')))
    except exception_type:
        sys.settrace(None)
        pipe.send(str(exception_type))
    else:
        pipe.send('constructor was not reached')


@pytest.mark.thread_unsafe
@pytest.mark.parametrize('object_type', [osmium.osm.Node, osmium.osm.Way, osmium.osm.Relation])
@pytest.mark.parametrize('exception', [KeyboardInterrupt, MemoryError, RuntimeError])
def test_constructor_exception_does_not_crash_cleanup(to_opl, object_type, exception):
    data = to_opl("""\
        n1 x5 y5
        w1 Nn1,n2
        r1 Mn1@
    """)

    parent_conn, child_conn = multiprocessing.Pipe()
    ctx = multiprocessing.get_context('spawn')
    p = ctx.Process(target=run_interrupted_read,
                    args=[child_conn, object_type, data, exception])
    p.start()

    assert parent_conn.poll(2)
    assert parent_conn.recv() == str(exception)

    p.join(2)

    assert p.exitcode == 0, f"Segmentation fault ({-p.exitcode})" if p.exitcode < 0 \
                            else f"Test exited with error {p.exitcode}"
