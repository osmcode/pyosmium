# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
import subprocess
import sys

import pytest


@pytest.mark.parametrize('object_type, data', [
    ('Node', 'n1 x5 y5'),
    ('Way', 'w1 Nn1,n2'),
    ('Relation', 'r1 Mn1@'),
])
@pytest.mark.parametrize('exception', ['KeyboardInterrupt', 'MemoryError', 'RuntimeError'])
def test_constructor_exception_does_not_crash_cleanup(object_type, data, exception):
    # Keep native destruction in a child: a regression must not kill pytest.
    # Tracing raises at the constructor entry without replacing wrapper classes.
    code = '''
import builtins
import sys

import osmium

object_type, data, exception_name = sys.argv[1:]
constructor = getattr(osmium.osm, object_type).__init__.__code__
exception_type = getattr(builtins, exception_name)


def fail_constructor(frame, event, arg):
    if event == 'call' and frame.f_code is constructor:
        sys.settrace(None)
        raise exception_type('injected constructor failure')
    return fail_constructor


source = osmium.io.FileBuffer(data.encode(), 'opl')
sys.settrace(fail_constructor)
try:
    list(osmium.FileProcessor(source))
except exception_type:
    sys.settrace(None)
    print('caught ' + exception_name, flush=True)
else:
    raise AssertionError('constructor was not reached')
'''
    result = subprocess.run(
        [sys.executable, '-X', 'faulthandler', '-c', code,
         object_type, data, exception],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'caught ' + exception
