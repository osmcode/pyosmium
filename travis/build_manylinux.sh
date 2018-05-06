#!/bin/bash
set -e -x

yum install -y sparsehash-devel bzip2-devel zlib-devel

mkdir -p boost
RETURN_PWD="$(pwd)"
cd boost
export BOOST_PREFIX="$(pwd)"
curl -L https://dl.bintray.com/boostorg/release/1.67.0/source/boost_1_67_0.tar.bz2 | tar xfj -
cd boost_1_67_0/
BOOST_ROOT="$(pwd)"
cd tools/build
sh bootstrap.sh
./b2 install --prefix="${BOOST_PREFIX}"

for PYBIN in /opt/python/*/bin ; do
    cd "${BOOST_ROOT}"
    cat << EOF > tools/build/src/site-config.jam
        using gcc ;
        using python : : $(ls ${PYBIN}/python* | head -n 1 ) : $(${PYBIN}/python -c 'from sysconfig import get_paths; print(get_paths()["include"])') ;
EOF
    echo "Using following BOOST configuration:"
    cat tools/build/src/site-config.jam

    echo "Using PYTHON_VERSION: ${PYBIN}"
    rm -rf ${BOOST_PREFIX}/build
    "${BOOST_PREFIX}"/bin/b2 --with-python --toolset=gcc --prefix="${BOOST_PREFIX}" --build-dir="${BOOST_PREFIX}"/build stage

    "${BOOST_PREFIX}"/bin/b2 --with-python --toolset=gcc --prefix="${BOOST_PREFIX}" --build-dir="${BOOST_PREFIX}"/build install > /dev/null
    # Add boost path to loader and linker
    export LD_LIBRARY_PATH="${BOOST_PREFIX}/lib:${LD_LIBRARY_PATH}"
    export LIBRARY_PATH="${BOOST_PREFIX}/lib"

    # update ldconfig cache, so find_library will find it
    ldconfig ${BOOST_PREFIX}/lib
    export LIBOSMIUM_PREFIX=/io/libosmium
    export PROTOZERO_PREFIX=/io/protozero
    cd /io
    rm -rf /io/build
    rm -rf wheelhouse
    "${PYBIN}/python" setup.py build
    "${PYBIN}/pip" wheel  /io/ -w wheelhouse/
    for whl in wheelhouse/*.whl; do
        auditwheel repair "$whl" -w /io/dist/
    done
    rm -rf /io/build
    rm -rf wheelhouse
done

