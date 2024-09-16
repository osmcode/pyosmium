# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Any, Optional, Union
from pathlib import Path
from tempfile import TemporaryDirectory
import os

from osmium._osmium import SimpleWriter
from osmium import IdTracker
from osmium.io import File, FileBuffer
from osmium.file_processor import FileProcessor, zip_processors

class ForwardReferenceWriter:
    """ Writer that adds forward-referenced objects optionally also making
        the final file reference complete. An object is a forward reference
        when it directly or indirectly needs one of the objects originally
        written out.

        The collected data is first written into a temporary file, When the
        writer is closed, the references are collected from the reference file
        and written out together with the collected data into the final file.

        The writer should usually be used as a context manager.
    """

    def __init__(self, outfile: Union[str, 'os.PathLike[str]', File],
                 ref_src: Union[str, 'os.PathLike[str]', File, FileBuffer],
                 overwrite: bool=False, back_references: bool=True,
                 remove_tags: bool=True, forward_relation_depth: int=0,
                 backward_relation_depth: int=1) -> None:
        """ Create a new writer.

            `outfile` is the name of the output file to write. The file must
            not yet exist unless `overwrite` is set to True.

            `ref_src` is the OSM input file, where to take the reference objects
            from. This is usually the same file the data to be written is taken
            from.

            The writer will collect back-references by default to make the
            file reference-complete. Set `back_references=False` to disable
            this behaviour.

            The writer will not complete nested relations by default. If you
            need nested relations, set `relation_depth` to the minimum depth
            to which relations shall be completed.
        """
        self.outfile = outfile
        self.tmpdir: Optional['TemporaryDirectory[Any]'] = TemporaryDirectory()
        self.writer = SimpleWriter(str(Path(self.tmpdir.name, 'forward_writer.osm.pbf')))
        self.overwrite = overwrite
        self.back_references = back_references
        self.id_tracker = IdTracker()
        self.ref_src = ref_src
        self.forward_relation_depth = forward_relation_depth
        self.backward_relation_depth = backward_relation_depth


    def __enter__(self) -> 'ForwardReferenceWriter':
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
        if hasattr(obj, 'location'):
            self.id_tracker.add_node(obj.id)
        elif hasattr(obj, 'nodes'):
            self.id_tracker.add_way(obj.id)
        elif hasattr(obj, 'members'):
            self.id_tracker.add_relation(obj.id)
        self.writer.add(obj)


    def add_node(self, n: Any) -> None:
        """ Write out an OSM node.
        """
        self.id_tracker.add_node(n.id)
        self.writer.add_node(n)


    def add_way(self, w: Any) -> None:
        """ Write out an OSM way.
        """
        self.id_tracker.add_way(w.id)
        self.writer.add_way(w)


    def add_relation(self, r: Any) -> None:
        """ Write out an OSM relation.
        """
        self.id_tracker.add_relation(r.id)
        self.writer.add_relation(r)


    def close(self) -> None:
        """ Close the writer and write out the final file.

            The function will be automatically called when the writer
            is used as a context manager.
        """
        if self.tmpdir is not None:
            self.writer.close()

            self.id_tracker.complete_forward_references(self.ref_src,
                                                        relation_depth=self.forward_relation_depth)
            if self.back_references:
                self.id_tracker.complete_backward_references(self.ref_src,
                                                             relation_depth=self.backward_relation_depth)

            fp1 = FileProcessor(Path(self.tmpdir.name, 'forward_writer.osm.pbf'))
            fp2 = FileProcessor(self.ref_src).with_filter(self.id_tracker.id_filter())


            with SimpleWriter(self.outfile, overwrite=self.overwrite) as writer:
                for o1, o2 in zip_processors(fp1, fp2):
                    if o1:
                        writer.add(o1)
                    else:
                        writer.add(o2)

            self.tmpdir.cleanup()
            self.tmpdir = None


