# SPDX-License-Identifier: BSD
#
# This file is part of Pyosmium.
#
# Copyright (C) 2022 Sarah Hoffmann.
from pathlib import Path
import sys
import sysconfig

SRC_DIR = (Path(__file__) / '..' / '..').resolve()
BUILD_DIR = "build/lib.{}-{}.{}".format(sysconfig.get_platform(),
                                        sys.version_info[0], sys.version_info[1])

# always test against the source
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(SRC_DIR / BUILD_DIR))

import pytest
