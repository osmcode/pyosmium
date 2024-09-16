# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Any, Union
import os
from typing_extensions import Buffer

from typing import overload

from .osm import Box, osm_entity_bits

class File:
    """ A wrapper for an OSM data file.
    """
    @property
    def has_multiple_object_versions(self) -> bool:
        """ True when the file is in a data format which supports
            having multiple versions of the same object in the file.
            This is usually the case with OSM history and diff files.
        """
    @has_multiple_object_versions.setter
    def has_multiple_object_versions(self, value: bool) -> None: ...
    def __init__(self, filename: Union[str, 'os.PathLike[str]'], format: str='') -> None:
        """ Initialise a new file object. Normally the file format of the
            file is guessed from the suffix of the file name. It may
            also be set explicitly using the _format_ parameter.
        """
    def parse_format(self, format: str) -> None:
        """ Set the format of the file from a format string.
        """

class FileBuffer:
    """ A wrapper around a buffer containing OSM data.
    """
    def __init__(self, buf: Buffer, format: str) -> None:
        """ Initialise a new buffer object. _buf_ can be any buffer
            that adheres to the Python buffer protocol. The format of
            the data must be defined in the _format_ parameter.
        """
    @property
    def has_multiple_object_versions(self) -> bool:
        """ True when the file is in a data format which supports
            having multiple versions of the same object in the file.
            This is usually the case with OSM history and diff files.
        """
    @has_multiple_object_versions.setter
    def has_multiple_object_versions(self, value: bool) -> None: ...

    def parse_format(self, format: str) -> None:
        """ Set the format of the file from a format string.
        """

class Header:
    """ File header data with global information about the file.
    """
    @property
    def has_multiple_object_versions(self) -> bool:
        """ True when the file is in a data format which supports
            having multiple versions of the same object in the file.
            This is usually the case with OSM history and diff files.
        """
    @has_multiple_object_versions.setter
    def has_multiple_object_versions(self, value: bool) -> None: ...

    def __init__(self) -> None:
        """ Initiate an empty header.
        """

    def add_box(self, box: Box) -> Header:
        """ Add the given bounding box to the list of bounding boxes
            saved in the header.
        """

    def box(self) -> Box:
        """ Return the bounding box of the data in the file. If no
            such information is available, an invalid box is returned.
        """

    def get(self, key: str, default: str = ...) -> str:
        """ Get the value of header option _key_ or return _default_ if
            there is no header option with that name.
        """

    def set(self, key: str, value: str) -> None:
        """ Set the value of header option _key_ to _value_.
        """

class Reader:
    """ Low-level object for reading data from an OSM file.

        A Reader does not expose functions to process the data it has read
        from the file. Use [apply][osmium.apply] for that purpose.
    """
    def __init__(self, filename: Union[str, 'os.PathLike[str]', FileBuffer, File],
                 types: osm_entity_bits = ...) -> None:
        """ Create a new reader object. The input may either be
            a filename or a [File][osmium.io.File] or
            [FileBuffer][osmium.io.FileBuffer] object. The _types_ parameter
            defines which kinds of objects will be read from the input. Any
            types not present will be skipped completely when reading the
            file. Depending on the type of input, this can save quite a bit
            of time. However, be careful to not skip over types that may
            be referenced by other objects. For example, ways need
            nodes in order to compute their geometry.

            Readers may be used as a context manager. In that case, the
            `close()` function will be called automatically when the
            reader leaves the scope.
        """

    def close(self) -> None:
        """ Close any open file handles and free all resources. The
            Reader is unusuable afterwards.
        """

    def eof(self) -> bool:
        """ Check if the reader has reached the end of the input data.
        """

    def header(self) -> Header:
        """ Return the Header structure containing global information about
            the input. What information is available depends on the format
            of the input data.
        """

    def __enter__(self) -> 'Reader':...
    def __exit__(self, *args: Any) -> None:...


class Writer:
    """ Low-level object for writing OSM data into a file. This class does not
        expose functions for receiving data to be written. Have a look at
        [SimpleWriter][osmium.SimpleWriter] for a higher-level interface
        for writing data.
    """
    def __init__(self, ffile: Union[str, 'os.PathLike[str]', File],
                 header: Header = ...) -> None:
        """ Create a new Writer. The output may either be a simple filename
            or a [File][osmium.io.File] object. A custom [Header][osmium.io.Header]
            object may be given, to customize the global file information that
            is written out. Be aware that not all file formats support writing
            out all header information.
        """

    def close(self) -> int:
        """ Close any open file handles and free all resources. The Writer
            is unusable afterwards.
        """
