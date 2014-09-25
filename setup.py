from distutils.core import setup, Extension

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


osmium = Extension('osmium._osmium',
           sources = ['lib/osmium.cc'],
           include_dirs = includes,
           libraries = libs,
           library_dirs = libdirs,
           extra_compile_args = [ '-std=c++11' ]
         )

setup (name = 'pyosmium',
       version = '0.1',
       description = 'Provides python bindings for libosmium.',
       packages = [ 'osmium' ],
       ext_modules = [osmium])


