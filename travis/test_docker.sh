#!/usr/bin/env bash

set -e -v

PACKAGE_INSTALL="apt-get update ; apt-get install -y python python-virtualenv"
DOCKER_IMAGE=debian
SHEEL=/bin/bash

OS=${1}
PYTHON_VERSION=${2}

case ${PYTHON_VERSION} in
"2")
    PYTHON=python
    ;;
"3")
    PYTHON=python3
    ;;
*)
    exit "Uknown python version: ${PYTHON_VERSION}"
    ;;
esac

case ${OS} in
"debian")
    if [ ${PYTHON_VERSION} = "2" ] ; then
        PACKAGE_INSTALL="apt-get update && apt-get install -y python python-virtualenv"
    else
        PACKAGE_INSTALL="apt-get update && apt-get install -y python3 python3-virtualenv"
    fi
    DOCKER_IMAGE=${OS}
    ;;
"ubuntu")
    if [ ${PYTHON_VERSION} = "2" ] ; then
        PACKAGE_INSTALL="apt-get update && apt-get install -y python python-virtualenv"
    else
        PACKAGE_INSTALL="apt-get update && apt-get install -y python3 python3-virtualenv"
    fi
    DOCKER_IMAGE=${OS}
    ;;
"centos")
    if [ ${PYTHON_VERSION} = "2" ] ; then
        PACKAGE_INSTALL="yum install -y epel-release && yum install -y python2 python2-virtualenv"
    else
        PACKAGE_INSTALL="yum install -y epel-release && yum install -y python34 python34-virtualenv"
    fi
    DOCKER_IMAGE=${OS}
    ;;
"archlinux")
    if [ ${PYTHON_VERSION} = "2" ] ; then
        PACKAGE_INSTALL="pacman -Sy --noconfirm python2 python2-virtualenv"
        PYTHON=python2
    else
        PACKAGE_INSTALL="pacman -Sy --noconfirm python3 python-virtualenv"
        PYTHON=python
    fi
    DOCKER_IMAGE="base/archlinux"
    ;;
"alpine")
    if [ ${PYTHON_VERSION} = "2" ] ; then
        PACKAGE_INSTALL="apk update && apk add python2 py2-virtualenv"
    else
        PACKAGE_INSTALL="apk update && apk add python3 py3-virtualenv"
    fi
    DOCKER_IMAGE=${OS}
    PYTHON=python
    SHELL=/bin/ash
    ;;

*)
    exit "Uknown OS: ${OS}"
    ;;
esac

rm -rf build
VENV_PYTHON=/venv/bin/python
VENV_PIP=/venv/bin/pip
cat << EOF | docker run --rm -i -v `pwd`:/io:ro $DOCKER_IMAGE $SHELL
set -e -v
${PACKAGE_INSTALL} &&
${PYTHON} -m virtualenv --python=python${PYTHON_VERSION} /venv &&
${VENV_PIP} install -U setuptools nose mock &&
${VENV_PYTHON} -c "from setuptools.pep425tags import is_manylinux1_compatible, get_supported ; print('Manylinux compatibility: ' + str(is_manylinux1_compatible())+ '\n' + 'Supported latforms: ' + ','.join((str(x) for x in get_supported())))" &&
${VENV_PIP} install osmium --no-index -f /io/dist &&
cd /io/test &&
${VENV_PYTHON} -m nose &&
${VENV_PYTHON} -c "import osmium"
EOF
