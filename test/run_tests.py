import sys
import sysconfig
import os

# use some black magic to find the libraries in the build directory
# borrowed from http://stackoverflow.com/questions/14320220/testing-python-c-libraries-get-build-path

build_dir = "../../build/lib.%s-%d.%d" % (
                    sysconfig.get_platform(),
                    sys.version_info[0], sys.version_info[1])

# insert after the current directory
sys.path.insert(1, os.path.normpath(os.path.join(os.path.realpath(__file__), build_dir)))

import nose
nose.main()
