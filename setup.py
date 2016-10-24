from setuptools import setup, Extension
from setuptools.command.sdist import sdist as orig_sdist
from subprocess import call
from sys import version_info as pyversion, platform as osplatform
from ctypes.util import find_library

osmium_version = '2.9.0'
version = '2.9.0'
includes = []
libs = []
libdirs = []

class My_sdist(orig_sdist):

    def make_release_tree(self, base_dir, files):
        orig_sdist.make_release_tree(self, base_dir, files)
        # checkout libosmium in the required version
        print("Downloading and adding libosmium sources")
        call('cd ' + base_dir + ' && wget -O - -q https://github.com/osmcode/libosmium/archive/v2.9.0.tar.gz | tar xz', shell=True)



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
includes.append('libosmium-' + osmium_version + '/include')
includes.append('../libosmium/include')
osmium_libs = ('expat', 'pthread', 'z', 'bz2')
libs.extend(osmium_libs)

extensions = []
extra_compile_args = [ '-std=c++11', '-D_LARGEFILE_SOURCE', '-D_FILE_OFFSET_BITS=64' ]

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
       version = version,
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
       classifiers=classifiers,
       packages = packages,
       cmdclass={'sdist' : My_sdist },
       ext_modules = extensions)


