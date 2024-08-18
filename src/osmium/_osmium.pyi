# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import ByteString, Union, Optional, Any
import os

from .osm import osm_entity_bits
from .osm.types import OSMEntity
from .index import LocationTable, IdSet
from .io import Reader, Writer, Header

StrPath = Union[str, 'os.PathLike[str]']

# Placeholder for more narrow type defintion to come
HandlerLike = object

class InvalidLocationError(Exception):
    """ Raised when the location of a node is requested that has
        no valid location. To be valid, a location must be
        inside the -180 to 180 and -90 to 90 degree range.
    """


class BaseHandler:
    """ Base class for all native handler functions in pyosmium.
        Any class that derives from this class can be used for
        parameters that need a handler-like object.
    """


class BaseFilter(BaseHandler):
    """ Base class for all native filter functions in pyosmium.
        A filter is a handler that returns a boolean in the handler
        functions indicating if the object should pass the filter (False)
        or be dropped (True).
    """
    def enable_for(self, entities: osm_entity_bits) -> None:
        """ Set the OSM types this filter should be applied to. If
            an object has a type for wich the filter is not enabled,
            the filter will be skipped completely. Or to put it in
            different words: every object for which the filter is not
            enabled, passes the filter automatically.
        """


class BufferIterator:
    """ (internal) Iterator interface for reading from a queue of buffers.

        This class is needed for pyosmium's internal implementation. There is
        currently no way to create buffers or add them to the iterator
        from Python.
    """
    def __init__(self, *handlers: HandlerLike) -> None:
        """ Create a new iterator. The iterator will pass each
            object through the filter chain _handlers_ before returning
            it.
        """
    def __bool__(self) -> bool:
        """ True if there are any objects left to return.
        """
    def __iter__(self) -> 'BufferIterator':
        """ Returns itself.
        """
    def __next__(self) -> OSMEntity:
        """ Get the next OSM object from the buffer or raise an StopIteration.
        """


class MergeInputReader:
    """ Buffer which collects data from multiple input files, sorts it
        and optionally deduplicates the data before applying to a handler.
    """
    def __init__(self) -> None:
        """ Initialize a new reader.
        """
    def _apply_internal(self, *handlers: HandlerLike, simplify: bool = ...) -> None:
        """ Internal application function. Do not use.
        """
    def add_buffer(self, buffer: Union[ByteString, str], format: str) -> int:
        """ Add input data from a buffer to the reader. The buffer may
            be any data which follows the Python buffer protocol. The
            manadatory _format_ parameter describes the format of the data.

            The data will be copied into internal buffers, so that the input
            buffer can be safely discarded after the function has been called.
        """
    def add_file(self, file: str) -> int:
        """ Add data from the given input file _file_ to the reader.
        """
    def apply_to_reader(self, reader: Reader, writer: Writer, with_history: bool = ...) -> None:
        """ Apply the collected data to data from the given _reader_ and write
            the result to _writer_. This function can be used to merge the diff "
            data together with other OSM data (for example when updating a
            planet file. If _with_history_ is true, then the collected data will
            be applied verbatim without removing duplicates. This is important
            when using OSM history files as input.
        """
    def apply(self, *handlers: HandlerLike, idx: str = '', simplify: bool = True) -> None:
        """ Apply collected data to a handler. The data will be sorted first.
            If _simplify_ is true (default) then duplicates will be eliminated
            and only the newest version of each object kept. If _idx_ is given
            a node location cache with the given type will be created and
            applied when creating the ways. Note that a diff file normally does
            not contain all node locations to reconstruct changed ways. If the
            full way geometries are needed, create a persistent node location
            cache during initial import of the area and reuse it when processing
            diffs. After the data
            has been applied the buffer of the MergeInputReader is empty and
            new data can be added for the next round of application.
        """


class SimpleWriter:
    """ Basic writer for OSM data. The SimpleWriter can write out
        object that are explicitly passed or function as a handler and
        write out all objects it receives. It is also possible to
        mix these two modes of operations.

        The writer writes out the objects in the order it receives them.
        It is the responsibility of the caller to ensure to follow the
        [ordering conventions](../user_manual/01-First-Steps.ipynb#the-order-of-osm-files)
        for OSM files.

        The SimpleWriter should normally used as a context manager. If you
        don't use it in a `with` context, don't forget to call `close()`,
        when writing is finished.
    """
    def __init__(self, filename: str, bufsz: int= ...,
                 header: Optional[Header]= ..., overwrite: bool= ...,
                 filetype: str= ...) -> None:
        """ Initiate a new writer for the file _filename_. The writer will
            refuse to overwrite an already existing file unless _overwrite_
            is explicitly set to `True`. The file type is usually determined
            from the file extension. It can also be set explicitly with the
            _filetype_ parameter.

            The optional parameter _bufsz_ sets the size of the buffers used
            for collecting the data before they are written out. The default
            size is 4MB. Larger buffers are normally better but you should
            be aware that there are normally multiple buffers in use during
            the write process.
        """
    def add_node(self, node: object) -> None:
        """ Add a new node to the file. The node may be a
            [Node](Dataclasses.md#osmium.osm.Node] object or its mutable
            variant or any other Python object that implements the same
            attributes.
        """
    def add_relation(self, relation: object) -> None:
        """ Add a new relation to the file. The relation may be a
            [Relation](Dataclasses.md#osmium.osm.Relation] object or its mutable
            variant or any other Python object that implements the same
            attributes.
        """
    def add_way(self, way: object) -> None:
        """ Add a new way to the file. The way may be a
            [Way](Dataclasses.md#osmium.osm.Way] object or its mutable
            variant or any other Python object that implements the same
            attributes.
        """
    def add(self, obj: object) -> None:
        """ Add a new object to the file. The function will try to determine
            the kind of object automatically.
        """
    def close(self) -> None:
        """ Flush the remaining buffers and close the writer. While it is not
            strictly necessary to call this function explicitly, it is still
            strongly recommended to close the writer as soon as possible, so
            that the buffer memory can be freed.
        """
    def __enter__(self) -> 'SimpleWriter':...
    def __exit__(self, *args: Any) -> None:...


class NodeLocationsForWays:
    """ Handler for retriving and caching locations from ways
        and adding them to ways.
    """
    @property
    def apply_nodes_to_ways(self) -> bool:
        """ When set (the default), the collected locations
            are propagated to the node list of ways.
        """
    @apply_nodes_to_ways.setter
    def apply_nodes_to_ways(self, value: bool) -> None:...

    def __init__(self, locations: LocationTable) -> None:
        """ Intiate a new handler using the given location table _locations_
            to cache the node coordinates.
        """
    def ignore_errors(self) -> None:
        """ Disable raising an exception when filling the node list of
            a way and a coordinate is not available.
        """


class OsmFileIterator:
    """ Low-level iterator interface for reading from an OSM source.
    """
    def __init__(self, reader: Reader, *handlers: HandlerLike) -> None:
        """ Initialise a new iterator using the given _reader_ as source.
            Each object is passed through the list of filters given by
            _handlers_. If all the filters are passed, the object is
            returned by `next()`.
        """
    def set_filtered_handler(self, handler: object) -> None:
        """ Set a fallback handler for objects that have been filtered
            out. The objects will be passed to the single handler.
        """
    def __iter__(self) -> 'OsmFileIterator':
        """ Returns itself.
        """
    def __next__(self) -> OSMEntity:
        """ Get the next OSM object from the file or raise a StopIteration.
        """


class IdTrackerIdFilter(BaseFilter): ...


class IdTrackerContainsFilter(BaseFilter): ...


class IdTracker:
    def __init__(self) -> None: ...
    def add_node(self, node: int) -> None: ...
    def add_relation(self, relation: int) -> None: ...
    def add_way(self, way: int) -> None: ...
    def add_references(self, obj: object) -> None: ...
    def contains_any_references(self, obj: object) -> bool: ...
    def complete_backward_references(self, filename: str, relation_depth: int = ...) -> None: ...
    def complete_forward_references(self, filename: str, relation_depth: int = ...) -> None: ...
    def id_filter(self) -> IdTrackerIdFilter: ...
    def contains_filter(self) -> IdTrackerContainsFilter: ...
    def node_ids(self) -> IdSet: ...
    def way_ids(self) -> IdSet: ...
    def relation_ids(self) -> IdSet: ...

def apply(reader: Union[Reader | str], *handlers: HandlerLike) -> None:
    """ Apply a chain of handlers to the given input source. The input
        source may be given either as a [Reader](IO.md#osmium.io.Reader) or
        as a simple file name. If one of the handler is a
        [filter](osmium.BaseFilter), then processing of the object will
        be stopped if it does not pass the filter.
    """
