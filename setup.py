from setuptools import setup, Extension
from setuptools.command.sdist import sdist as orig_sdist
from distutils.command import build_ext as setuptools_build_ext
from subprocess import call
from sys import version_info as pyversion, platform as osplatform
from ctypes.util import find_library
import os
import os.path as osp

includes = []
libs = []
libdirs = []

class My_sdist(orig_sdist):

    def make_release_tree(self, base_dir, files):
        orig_sdist.make_release_tree(self, base_dir, files)
        # checkout libosmium in the required version
        tarball = 'https://github.com/osmcode/libosmium/archive/v%s.tar.gz' % libosmium_version
        print("Downloading and adding libosmium sources from", tarball)
        call('cd %s && wget -O - -q %s | tar xz' % (base_dir, tarball), shell=True)
        # checkout protozero in the required version
        tarball = 'https://github.com/mapbox/protozero/archive/v%s.tar.gz' % protozero_version
        print("Downloading and adding protozero sources from", tarball)
        call('cd %s && wget -O - -q %s | tar xz' % (base_dir, tarball), shell=True)

def get_versions():
    """ Read the version file.

        The file cannot be directly imported because it is not installed
        yet.
    """
    version_py = os.path.join(os.path.split(__file__)[0], "src/osmium/version.py")
    v = {}
    with open(version_py) as version_file:
        # Execute the code in version.py.
        exec(compile(version_file.read(), version_py, 'exec'), v)

    return v['pyosmium_release'], v['libosmium_version'], v['protozero_version']


def find_includes(libname, chk_file=None, prefix=None, version_postfix=None):
    if chk_file is None:
        chk_file = osp.join('include', libname, 'version.hpp')

    if prefix is not None:
        if not os.path.isfile(osp.join(prefix, chk_file)):
            raise RuntimeError("Prefix for %s set but library not found in '%s'."
                               % (libname, prefix))
        return osp.join(prefix, 'include')

    search_paths = []
    if version_postfix:
        search_paths.append('%s-%s' % (libname, version_postfix))
    search_paths.append(osp.join('..', libname))

    for p in search_paths:
        if os.path.isfile(osp.join(p, chk_file)):
            print("%s found in '%s'." % (libname, p))
            return osp.join(p, 'include')

    print("Using global %s" % libname)


pyosmium_release, libosmium_version, protozero_version = get_versions()

## boost dependencies
boost_prefix = os.environ.get('BOOST_PREFIX',
                              'c:/libs' if osplatform == "win32" else '/usr')

includes.append(os.path.join(boost_prefix, 'include'))
if 'BOOST_VERSION' in os.environ:
    for boost_dir in ('boost-%s', 'boost%s'):
        if os.path.isdir(os.path.join(boost_prefix, 'include', boost_dir % os.environ['BOOST_VERSION'])):
            includes.append(os.path.join(boost_prefix, 'include', boost_dir %os.environ['BOOST_VERSION']))
            break
    else:
        raise Exception("Cannot find boost headers")
elif 'BOOST_PREFIX' in os.environ:
    if os.path.isdir(os.path.join(boost_prefix, 'include', 'boost')):
        includes.append(os.path.join(boost_prefix, 'include', 'boost'))
    else:
        raise Exception("Cannot find boost headers")

if 'BOOST_PREFIX' in os.environ:
    libdirs.append(os.path.join(boost_prefix, 'lib'))
elif osplatform in ["linux", "linux2"] and os.path.isdir('/usr/lib/x86_64-linux-gnu/'):
    libdirs.append('/usr/lib/x86_64-linux-gnu/')
else:
    libdirs.append(os.path.join(boost_prefix, 'lib'))

# try to find the boost library matching the python version
suffixes = [ # Debian naming convention for version installed in parallel
             "-py%d%d" % (pyversion.major, pyversion.minor),
             # Gentoo naming convention for version installed in parallel
             "-%d.%d" % (pyversion.major, pyversion.minor),
             # Darwin
             "%d%d" % (pyversion.major, pyversion.minor),
             # standard suffix for Python3
             "%d" % (pyversion.major),
             # standard naming
             "",
             # former naming schema?
             "-mt"
           ]
for suf in suffixes:
    libboost = "boost_python%s" % suf
    found = find_library(libboost)
    if found:
        libs.append(libboost)
        break
else:
    # Visual C++ supports auto-linking, no library needed
    if osplatform != "win32":
        raise Exception("Cannot find boost_python library")

if osplatform != "win32":
    orig_compiler = setuptools_build_ext.customize_compiler

    def cpp_compiler(compiler):
        retval = orig_compiler(compiler)
        # force C++ compiler
        # Note that we only exchange the compiler as we want to keep the
        # original Python cflags.
        if len(compiler.compiler_cxx) > 0:
            compiler.compiler_so[0] = compiler.compiler_cxx[0]
        # remove warning that does not make sense for C++
        try:
            compiler.compiler_so.remove('-Wstrict-prototypes')
        except (ValueError, AttributeError):
            pass
        return retval

    setuptools_build_ext.customize_compiler = cpp_compiler

### osmium dependencies
osmium_inc = find_includes('libosmium',
                           chk_file=osp.join('include', 'osmium', 'version.hpp'),
                           prefix=os.environ.get('LIBOSMIUM_PREFIX'),
                           version_postfix=libosmium_version)
if osmium_inc is not None:
    includes.insert(0, osmium_inc)

### protozero dependencies
protozero_inc = find_includes('protozero',
                              prefix=os.environ.get('PROTOZERO_PREFIX'),
                              version_postfix=protozero_version)
if protozero_inc is not None:
    includes.insert(0, protozero_inc)

if osplatform == "win32" :
    osmium_libs = ('expat', 'zlib', 'bzip2', 'ws2_32')
    extra_compile_args = [ '-DWIN32_LEAN_AND_MEAN', '-D_CRT_SECURE_NO_WARNINGS', '-DNOMINMAX', '/wd4996', '/EHsc' ]
else:
    osmium_libs = ('expat', 'pthread', 'z', 'bz2')
    extra_compile_args = [ '-std=c++11', '-D_LARGEFILE_SOURCE', '-D_FILE_OFFSET_BITS=64', '-D__STDC_FORMAT_MACROS' ]

libs.extend(osmium_libs)

extensions = []

extensions.append(Extension('osmium._osmium',
       sources = ['lib/osmium.cc'],
       include_dirs = includes,
       libraries = libs,
       library_dirs = libdirs,
       language = 'c++',
       extra_compile_args = extra_compile_args
     ))
packages = ['osmium']

for ext in ('io', 'index', 'geom'):
    extensions.append(Extension('osmium.%s' % ext,
           sources = ['lib/%s.cc' % ext],
           include_dirs = includes,
           libraries = libs,
           library_dirs = libdirs,
           language = 'c++',
           extra_compile_args = extra_compile_args
         ))

for ext in ('osm', 'replication'):
    extensions.append(Extension('osmium.%s._%s' % (ext, ext),
           sources = ['lib/%s.cc' % ext],
           include_dirs = includes,
           libraries = libs,
           library_dirs = libdirs,
           language = 'c++',
           extra_compile_args = extra_compile_args
         ))
    packages.append('osmium.%s' % ext)

classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: C++",
        ]

descfile=open('README.rst')
long_description = descfile.read()
descfile.close()

setup (name = 'osmium',
       version = pyosmium_release,
       description = 'Python bindings for libosmium, the data processing library for OSM data',
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
       classifiers=classifiers,
       packages = packages,
       package_dir = {'' : 'src'},
       package_data = { 'osmium' : [ '*.dll' ] },
       cmdclass={'sdist' : My_sdist},
       ext_modules = extensions)

