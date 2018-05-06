#!/bin/bash
set -e -x

for PYBIN in /opt/python/*/bin ; do
    "${PYBIN}/pip" install nose mock
    "${PYBIN}/pip" install osmium --no-index -f /io/dist
    "${PYBIN}/python" -c "import osmium"
    "${PYBIN}/python" /io/test/run_tests.py || "${PYBIN}/python2" /io/test/run_tests.py || "${PYBIN}/python3" /io/test/run_tests.py
done
