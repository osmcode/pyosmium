# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Any, Union
from pathlib import Path
from tempfile import TemporaryDirectory
import os

from osmium._osmium import SimpleWriter
from osmium.io import File, FileBuffer
from osmium.file_processor import FileProcessor, zip_processors
from osmium import IdTracker

class BackReferenceWriter:
    """ Writer that adds referenced objects, so that all written
        objects are reference-complete.

        The collected data is first written into a temporary file and
        the necessary references are tracked internally. When the writer
        is closed, it writes the final file, mixing together the referenced
        objects from the original file and the written data.

        The writer should usually be used as a context manager.
    """

    def __init__(self, outfile: Union[str, 'os.PathLike[str]', File],
                 ref_src: Union[str, 'os.PathLike[str]', File, FileBuffer],
                 overwrite: bool=False, remove_tags: bool=True,
                 relation_depth: int = 0):
        """ Create a new writer.

            `outfile` is the name of the output file to write. The file must
            not yet exist unless `overwrite` is set to True.

            `ref_src` is the OSM input file, where to take the reference objects
            from. This is usually the same file the data to be written is taken
            from.

            The writer will by default remove all tags from referenced objects,
            so that they do not appear as stray objects in the file. Set
            `remove_tags` to False to keep the tags.

            The writer will not complete nested relations by default. If you
            need nested relations, set `relation_depth` to the minimum depth
            to which relations shall be completed.
        """
        self.outfile = outfile
        self.tmpdir = TemporaryDirectory()
        self.writer = SimpleWriter(str(Path(self.tmpdir.name, 'back_writer.osm.pbf')))
        self.overwrite = overwrite
        self.remove_tags = remove_tags
        self.id_tracker = IdTracker()
        self.ref_src = ref_src
        self.relation_depth = relation_depth

    def __enter__(self) -> 'BackReferenceWriter':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if exc_type is None:
            self.close()
        else:
            # Exception occured. Do not write out the final file.
            self.writer.close()

    def add(self, obj: Any) -> None:
        """ Write an arbitrary OSM object. This can be either an
            osmium object or a Python object that has the appropriate
            attributes.
        """
        self.id_tracker.add_references(obj)
        self.writer.add(obj)

    def add_node(self, n: Any) -> None:
        """ Write out an OSM node.
        """
        self.writer.add_node(n)

    def add_way(self, w: Any) -> None:
        """ Write out an OSM way.
        """
        self.id_tracker.add_references(w)
        self.writer.add_way(w)

    def add_relation(self, r: Any) -> None:
        """ Write out an OSM relation.
        """
        self.id_tracker.add_references(r)
        self.writer.add_relation(r)

    def close(self) -> None:
        """ Close the writer and write out the final file.

            The function will be automatically called when the writer
            is used as a context manager.
        """
        self.writer.close()
        self.id_tracker.complete_backward_references(self.ref_src,
                                                     relation_depth=self.relation_depth)

        fp1 = FileProcessor(str(Path(self.tmpdir.name, 'back_writer.osm.pbf')))
        fp2 = FileProcessor(self.ref_src).with_filter(self.id_tracker.id_filter())

        with SimpleWriter(self.outfile, overwrite=self.overwrite) as writer:
            for o1, o2 in zip_processors(fp1, fp2):
                if o1:
                    writer.add(o1)
                elif o2:
                    if self.remove_tags and hasattr(o2, 'replace'):
                        writer.add(o2.replace(tags={}))
                    else:
                        writer.add(o2)

        self.tmpdir.cleanup()
