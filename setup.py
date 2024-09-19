# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
import os
import re
import sys
import platform
import subprocess
import urllib.request
import tarfile
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist as orig_sdist

BASEDIR = os.path.split(os.path.abspath(__file__))[0]

class PyosmiumSDist(orig_sdist):

    contrib = (
        ('libosmium', 'https://github.com/osmcode/libosmium/archive/v{}.tar.gz'),
        ('protozero', 'https://github.com/mapbox/protozero/archive/v{}.tar.gz'),
        ('pybind11', 'https://github.com/pybind/pybind11/archive/v{}.tar.gz'),
    )

    def make_release_tree(self, base_dir, files):
        orig_sdist.make_release_tree(self, base_dir, files)

        # add additional dependecies in the required version
        for name, tar_src in self.contrib:
            tarball = tar_src.format(versions[name + '_version'])
            print("Downloading and adding {} sources from {}".format(name, tarball))
            base = Path("-".join((name, versions[name + '_version'])))
            dest = Path(base_dir) / "contrib" / name
            with urllib.request.urlopen(tarball) as reader:
                with tarfile.open(fileobj=reader, mode='r|gz') as tf:
                    for member in tf:
                        fname = Path(member.name)
                        if not fname.is_absolute():
                            fname = fname.relative_to(base)
                            if member.isdir():
                                (dest / fname).mkdir(parents=True, exist_ok=True)
                            elif member.isfile():
                                with tf.extractfile(member) as memberfile:
                                    with (dest / fname).open('wb') as of:
                                        of.write(memberfile.read())



def get_versions():
    """ Read the version file.

        The file cannot be directly imported because it is not installed
        yet.
    """
    version_py = os.path.join(BASEDIR, "src/osmium/version.py")
    v = {}
    with open(version_py) as version_file:
        # Execute the code in version.py.
        exec(compile(version_file.read(), version_py, 'exec'), v)

    return v

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            nbr_cpus = os.cpu_count() or 2 # fallback if None is returned
            build_args += ['--', f'-j{nbr_cpus}']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())

        if 'LIBOSMIUM_PREFIX' in env:
            cmake_args += ['-DOSMIUM_INCLUDE_DIR={}/include'.format(env['LIBOSMIUM_PREFIX'])]
        elif os.path.exists(os.path.join(BASEDIR, 'contrib', 'libosmium', 'include', 'osmium', 'version.hpp')):
            cmake_args += ['-DOSMIUM_INCLUDE_DIR={}/contrib/libosmium/include'.format(BASEDIR)]

        if 'PROTOZERO_PREFIX' in env:
            cmake_args += ['-DPROTOZERO_INCLUDE_DIR={}/include'.format(env['PROTOZERO_PREFIX'])]
        elif os.path.exists(os.path.join(BASEDIR, 'contrib', 'protozero', 'include', 'protozero', 'version.hpp')):
            cmake_args += ['-DPROTOZERO_INCLUDE_DIR={}/contrib/protozero/include'.format(BASEDIR)]

        if 'PYBIND11_PREFIX' in env:
            cmake_args += ['-DPYBIND11_PREFIX={}'.format(env['PYBIND11_PREFIX'])]
        elif os.path.exists(os.path.join(BASEDIR, 'contrib', 'pybind11')):
            cmake_args += ['-DPYBIND11_PREFIX={}/contrib/pybind11'.format(BASEDIR)]

        if 'BOOST_PREFIX' in env:
            cmake_args += ['-DBOOST_ROOT={}'.format(env['BOOST_PREFIX'])]

        if 'CMAKE_CXX_STANDARD' in env:
            cmake_args += ['-DCMAKE_CXX_STANDARD={}'.format(env['CMAKE_CXX_STANDARD'])]

        cmake_args += [f"-DWITH_LZ4={env.get('CMAKE_WITH_LZ4', 'ON')}"]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

versions = get_versions()

setup(
    scripts=['tools/pyosmium-get-changes', 'tools/pyosmium-up-to-date'],
    ext_modules=[CMakeExtension('cmake_example')],
    cmdclass=dict(build_ext=CMakeBuild, sdist=PyosmiumSDist),
    zip_safe=False,
)
