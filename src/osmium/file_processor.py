# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Iterable, Iterator, Tuple, Any, Union, Optional, List
import os

import osmium
from osmium.index import LocationTable
from osmium.io import File, FileBuffer
from osmium.osm.types import OSMEntity

class FileProcessor:
    """ A processor that reads an OSM file in a streaming fashion,
        optionally pre-filters the data, enhances it with geometry information,
        returning the data via an iterator.
    """

    def __init__(self, indata: Union[File, FileBuffer, str, 'os.PathLike[str]'],
                 entities: osmium.osm.osm_entity_bits=osmium.osm.ALL) -> None:
        """ Initialise a new file processor for the given input source _indata_.
            This may either be a filename, an instance of [File](IO.md#osmium.io.File)
            or buffered data in form of a [FileBuffer](IO.md#osmium.io.FileBuffer).

            The types of objects which will be read from the file can be
            restricted with the _entities_ parameter. The data will be skipped
            directly at the source file and will never be passed to any filters
            including the location and area processors. You usually should not
            be restricting objects, when using those.
            """
        self._file = indata
        self._entities = entities
        self._node_store: Optional[LocationTable] = None
        self._area_handler: Optional[osmium.area.AreaManager] = None
        self._filters: List['osmium._osmium.HandlerLike'] = []
        self._area_filters: List['osmium._osmium.HandlerLike'] = []
        self._filtered_handler: Optional['osmium._osmium.HandlerLike'] = None

    @property
    def header(self) -> osmium.io.Header:
        """ (read-only) [Header](IO.md#osmium.io.Header) information
            for the file to be read.
        """
        return osmium.io.Reader(self._file, osmium.osm.NOTHING).header()

    @property
    def node_location_storage(self) -> Optional[LocationTable]:
        """ Node location cache currently in use, if enabled.
            This can be used to manually look up locations of nodes.
            Be aware that the nodes must have been read before you
            can do a lookup via the location storage.
        """
        return self._node_store

    def with_locations(self, storage: str='flex_mem') -> 'FileProcessor':
        """ Enable caching of node locations. The file processor will keep
            the coordinates of all nodes that are read from the file in
            memory and automatically enhance the node list of ways with
            the coordinates from the cache. This information can then be
            used to create geometries for ways. The node location cache can
            also be directly queried through the [node_location_storage]() property.

            The _storage_ parameter can be used to change the type of cache
            used to store the coordinates. The default 'flex_mem' is good for
            small to medium-sized files. For large files you may need to
            switch to a disk-storage based implementation because the cache
            can become quite large. See the section on
            [location storage in the user manual][location-storage]
            for more information.
        """
        if not (self._entities & osmium.osm.NODE):
            raise RuntimeError('Nodes not read from file. Cannot enable location cache.')
        if isinstance(storage, str):
            self._node_store = osmium.index.create_map(storage)
        elif storage is None or isinstance(storage, osmium.index.LocationTable):
            self._node_store = storage
        else:
            raise TypeError("'storage' argument must be a LocationTable or a string describing the index")

        return self

    def with_areas(self, *filters: 'osmium._osmium.HandlerLike') -> 'FileProcessor':
        """ Enable area processing. When enabled, then closed ways and
            relations of type multipolygon will also be returned as an
            Area type.

            Optionally one or more filters can be passed. These filters
            will be applied in the first pass, when relation candidates
            for areas are selected.
            Calling this function multiple times causes more filters to
            be added to the filter chain.

            Calling this function automatically enables location caching
            if it was not enabled yet using the default storage type.
            To use a different storage type, call `with_locations()` explicity
            with the approriate _storage_ parameter before calling this
            function.
        """
        if self._area_handler is None:
            self._area_handler = osmium.area.AreaManager()
            if self._node_store is None:
                self.with_locations()
        self._area_filters.extend(filters)
        return self

    def with_filter(self, filt: 'osmium._osmium.HandlerLike') -> 'FileProcessor':
        """ Add a filter function to the processors filter chain.
            Filters are called for each prcoessed object in the order they
            have been installed. Only when the object passes all the
            filter functions will it be handed to the iterator.

            Note that any handler-like object can be installed as a filter.
            A non-filtering handler simply works like an all-pass filter.
        """
        self._filters.append(filt)
        return self


    def handler_for_filtered(self, handler: 'osmium._osmium.HandlerLike') -> 'FileProcessor':
        """ Set a fallback handler for object that have been filtered out.

            Any object that does not pass the filter chain installed with
            `with_filter()` will be passed to this handler. This can be useful
            when the entire contents of a file should be passed to a writer
            and only some of the objects need to be processed specially
            in the iterator body.
        """
        self._filtered_handler = handler
        return self

    def __iter__(self) -> Iterator[OSMEntity]:
        """ Create a new iterator for the file processor. It is possible to
            create mulitple iterators from the same processor and even run
            them in parallel. However, you must not change the properties
            of the file processor while a iterator is in progress of reading
            a file.

            When area processing is enabled, then the input data needs to
            be read twice. The first pass reads the relations, while the
            second pass reads the whole file. The iterator will do this
            transparantly for the user. However, be aware that the first
            pass of reading may take a while for large files, so that the
            iterator might block before the first object is returned.
        """
        handlers: List['osmium._osmium.HandlerLike'] = []

        if self._node_store is not None:
            lh = osmium.NodeLocationsForWays(self._node_store)
            lh.ignore_errors()
            handlers.append(lh)

        if self._area_handler is None:
            reader = osmium.io.Reader(self._file, self._entities)
            it = osmium.OsmFileIterator(reader, *handlers, *self._filters)
            if self._filtered_handler:
                it.set_filtered_handler(self._filtered_handler)
            yield from it
            return

        # need areas, do two pass handling
        rd = osmium.io.Reader(self._file, osmium.osm.RELATION)
        try:
            osmium.apply(rd, *self._area_filters, self._area_handler.first_pass_handler())
        finally:
            rd.close()

        buffer_it = osmium.BufferIterator(*self._filters)
        handlers.append(self._area_handler.second_pass_to_buffer(buffer_it))

        reader = osmium.io.Reader(self._file, self._entities)
        it = osmium.OsmFileIterator(reader, *handlers, *self._filters)
        if self._filtered_handler:
            it.set_filtered_handler(self._filtered_handler)
        for obj in it:
            yield obj
            if buffer_it:
                yield from buffer_it

        # catch anything after the final flush
        if buffer_it:
            yield from buffer_it


def zip_processors(*procs: FileProcessor) -> Iterable[List[Optional[OSMEntity]]]:
    """ Return the data from the FileProcessors in parallel such
        that objects with the same ID are returned at the same time.

        The processors must contain sorted data or the results are
        undefined.
    """
    TID = {'n': 0, 'w': 1, 'r': 2, 'a': 3, 'c': 4}

    class _CompIter:

        def __init__(self, fp: FileProcessor) -> None:
            self.iter = iter(fp)
            self.current: Optional[OSMEntity] = None
            self.comp: Optional[Tuple[int, int]] = None

        def val(self, nextid: Tuple[int, int]) -> Optional[OSMEntity]:
            """ Return current object if it corresponds to the given object ID.
            """
            if self.comp == nextid:
                return self.current
            return None

        def next(self, nextid: Optional[Tuple[int, int]]) -> Tuple[int, int]:
            """ Get the next object ID, if and only if nextid points to the
                previously returned object ID. Otherwise return the previous
                ID again.
            """
            if self.comp == nextid:
                self.current = next(self.iter, None)
                if self.current is None:
                    self.comp = (100, 0) # end of file marker. larger than any ID
                else:
                    self.comp = (TID[self.current.type_str()], self.current.id)
            assert self.comp is not None
            return self.comp


    iters = [_CompIter(p) for p in procs]

    nextid = min(i.next(None) for i in iters)

    while nextid[0] < 100:
        yield [i.val(nextid) for i in iters]
        nextid = min(i.next(nextid) for i in iters)
