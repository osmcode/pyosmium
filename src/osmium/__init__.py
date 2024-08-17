# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Any

from osmium._osmium import *
from osmium.helper import *
from osmium.simple_handler import SimpleHandler
from osmium.file_processor import FileProcessor, zip_processors
from osmium.back_reference_writer import BackReferenceWriter
from osmium.forward_reference_writer import ForwardReferenceWriter
import osmium.io
import osmium.osm
import osmium.index
import osmium.geom
import osmium.area
import osmium.filter

# WriteHandler no longer exists. SimpleWriter can now function as a handler.
class WriteHandler(SimpleWriter):
    """ (Deprecated) Handler function that writes all data directly to a file.

        This is now simply an alias for SimpleWriter. Please refer to its
        documentation.
    """

    def __init__(self, filename: str, bufsz: int=4096*1024, filetype: str="") -> None:
        super().__init__(filename, bufsz=bufsz, filetype=filetype)


def _merge_apply(self: osmium.MergeInputReader, *handlers: Any, idx: str = '', simplify: bool = True) -> None:
    """ Apply collected data to a handler. The data will be sorted first.
        If `simplify` is true (default) then duplicates will be eliminated
        and only the newest version of each object kept. If `idx` is given
        a node location cache with the given type will be created and
        applied when creating the ways. Note that a diff file normally does
        not contain all node locations to reconstruct changed ways. If the
        full way geometries are needed, create a persistent node location
        cache during initial import of the area and reuse it when processing
        diffs. After the data
        has been applied the buffer of the MergeInputReader is empty and
        new data can be added for the next round of application.
    """
    if idx:
        lh = NodeLocationsForWays(osmium.index.create_map(idx))
        lh.ignore_errors()
        self._apply_internal(lh, *handlers, simplify=simplify)

    self._apply_internal(*handlers, simplify=simplify)

osmium.MergeInputReader.apply = _merge_apply # type: ignore[method-assign]
