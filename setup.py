from distutils.core import setup, Extension
from os import environ
from sys import version_info as pyversion, platform as osplatform
from ctypes.util import find_library

includes = []
libs = []
libdirs = []

## boost dependencies
includes.append('/usr/include')
if osplatform in ["linux", "linux2"]:
    libdirs.append('/usr/lib/x86_64-linux-gnu/')

# try to find the boost library matching the python version
suffixes = [ # Debian naming convention for version installed in parallel
             "-py%d%d" % (pyversion.major, pyversion.minor),
             # standard suffix for Python3
             "%d" % (pyversion.major),
             # standard naming
             "",
             # former naming schema?
             "-mt"
           ]
for suf in suffixes:
    lib = find_library("boost_python%s" % suf)
    if lib is not None:
        libs.append("boost_python%s" % suf)
        break
else:
    raise Exception("Cannot find boost_python library")

### osmium dependencies
includes.append('../libosmium/include')
osmium_libs = ('expat', 'pthread', 'z', 'protobuf-lite', 'osmpbf', 'bz2')
libs.extend(osmium_libs)

extensions = []
extra_compile_args = [ '-std=c++11', '-D_LARGEFILE_SOURCE', '-D_FILE_OFFSET_BITS=64' ]

for ext in ('osmium', 'io', 'osm', 'index', 'geom'):
    extensions.append(Extension('osmium._%s' % ext,
           sources = ['lib/%s.cc' % ext],
           include_dirs = includes,
           libraries = libs,
           library_dirs = libdirs,
           language = 'c++',
           extra_compile_args = extra_compile_args
         ))

setup (name = 'pyosmium',
       version = '0.1',
       description = 'Provides python bindings for libosmium.',
       packages = [ 'osmium' ],
       ext_modules = extensions)


