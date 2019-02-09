import os
import re
import sys
import platform
import shutil
import subprocess
import tempfile

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist as orig_sdist
from setuptools.command.build_py import build_py
from distutils.version import LooseVersion
from sys import executable, version_info as python_version


BASEDIR = os.path.split(os.path.abspath(__file__))[0]

class Pyosmium_sdist(orig_sdist):

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
            subprocess.call('wget -O - -q {} | tar xz -C {} --one-top-level=contrib/{} --strip-components=1'.format(
                   tarball, base_dir, name), shell=True)


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

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

        self.generate_pyi()

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
            build_args += ['--', '-j2']

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

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

    def generate_pyi(self):
        # set python executable
        if python_version >= (3, 4, 0):
            python_name = executable
        else:
            if platform == 'win32':
                python_name = 'py -3'
            else:
                python_name = 'python3'

        if python_version[0] < 3:
            return # no mypy for python2

        # set target directory
        dst = self.build_lib
        # test that everything is OK
        env = os.environ.copy()
        env['PYTHONPATH'] = dst

        # test if there is no errors in osmium, stubgen doesn't report error on import error
        import_test = subprocess.Popen([python_name, '-c', 'import osmium'], env=env, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        if import_test.wait():
            error = ""
            if import_test.stdout:
                error += "\n".join(x.decode('utf-8') for x in import_test.stdout.readlines())
            if import_test.stderr:
                error += "\n".join(x.decode('utf-8') for x in import_test.stderr.readlines())
            raise Exception("Failure importing osmium: \n" + error)

        # generate pyi files
        with tempfile.TemporaryDirectory() as tmpdir:
            p = subprocess.Popen([python_name, '-m', 'mypy.stubgen', '-p', 'osmium', '-o', tmpdir], env=env,
                                 stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            retcode = p.wait()
            error = ""
            if p.stdout:
                error += "\n".join(x.decode('utf-8') for x in p.stdout.readlines())
            if p.stderr:
                error += "\n".join(x.decode('utf-8') for x in p.stderr.readlines())
            if retcode:
                raise Exception("Failure calling stubgen: \n" + error)
            for pyi in (os.path.join("osmium", "osm", "_osm.pyi"),
                        os.path.join("osmium", "replication", "_replication.pyi"),
                        os.path.join("osmium", '_osmium.pyi'),
                        os.path.join("osmium", 'geom.pyi'),
                        os.path.join("osmium", 'index.pyi'),
                        os.path.join("osmium", 'io.pyi')):
                shutil.copyfile(os.path.join(tmpdir, pyi), os.path.join(dst, pyi))

versions = get_versions()

with open('README.rst', 'r') as descfile:
    long_description = descfile.read()


setup(
    name='osmium',
    version=versions['pyosmium_release'],
    description='Python bindings for libosmium, the data processing library for OSM data',
    long_description=long_description,
    author='Sarah Hoffmann',
    author_email='lonvia@denofr.de',
    maintainer='Sarah Hoffmann',
    maintainer_email='lonvia@denofr.de',
    download_url='https://github.com/osmcode/pyosmium',
    url='http://osmcode.org/pyosmium',
    keywords=["OSM", "OpenStreetMap", "Osmium"],
    license='BSD',
    scripts=['tools/pyosmium-get-changes', 'tools/pyosmium-up-to-date'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: C++",
        ],

    ext_modules=[CMakeExtension('cmake_example')],
    packages = ['osmium', 'osmium/osm', 'osmium/replication'],
    package_dir = {'' : 'src'},
    package_data={'osmium': ['py.typed']},
    cmdclass=dict(build_ext=CMakeBuild, sdist=Pyosmium_sdist),
    zip_safe=False,
)
