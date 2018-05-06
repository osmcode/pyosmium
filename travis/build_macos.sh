#!/usr/bin/env bash
set -e -x

$PYTHON --version
$PYTHON -m pip install virtualenv
$PYTHON -m virtualenv venv_build

export LIBOSMIUM_PREFIX=./libosmium
export PROTOZERO_PREFIX=./protozero

venv_build/bin/python -m pip install -q nose mock wheel setuptools auditwheel
venv_build/bin/pip wheel . -w dist/
rm -rf build
