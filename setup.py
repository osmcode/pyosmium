from distutils.core import setup, Extension
from os import environ

includes = []
libs = []
libdirs = []

## boost dependencies
includes.append('/usr/include')
libs.append('boost_python')
libdirs.append('/usr/lib/x86_64-linux-gnu/')

### osmium dependencies
includes.append('../libosmium/include')
libs.extend(('expat', 'pthread', 'z', 'protobuf-lite', 'osmpbf', 'z', 'bz2'))

extensions = []
extra_compile_args = [ '-std=c++11' ]

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


