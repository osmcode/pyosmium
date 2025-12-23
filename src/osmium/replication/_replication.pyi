# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Union
import datetime
import os

from ..io import Reader, File

def newest_change_from_file(file: Union[str, 'os.PathLike[str]', File, Reader]
                           ) -> datetime.datetime:
    """ Find the date of the most recent change in a file.
    """
