# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Iterable, Iterator, Tuple, Any, Union, Optional, List
from pathlib import Path

import osmium
from osmium.index import LocationTable
from osmium.osm.types import OSMEntity

class FileProcessor:
    """ A generator that emits OSM objects read from a file.
    """

    def __init__(self, filename: Union[osmium.io.File, osmium.io.FileBuffer, str, Path],
                 entities: osmium.osm.osm_entity_bits=osmium.osm.ALL) -> None:
        if isinstance(filename, (osmium.io.File, osmium.io.FileBuffer)):
            self._file = filename
        elif isinstance(filename, (str, Path)):
            self._file = osmium.io.File(str(filename))
        else:
            raise TypeError("File must be an osmium.io.File, osmium.io.FileBuffer, str or Path")
        self._entities = entities
        self._node_store: Optional[LocationTable] = None
        self._area_handler: Optional[osmium.area.AreaManager] = None
        self._filters: List['osmium._osmium.HandlerLike'] = []
        self._area_filters: List['osmium._osmium.HandlerLike'] = []
        self._filtered_handler: Optional['osmium._osmium.HandlerLike'] = None

    @property
    def header(self) -> osmium.io.Header:
        """ Return the header information for the file to be read.
        """
        return osmium.io.Reader(self._file, osmium.osm.NOTHING).header()

    @property
    def node_location_storage(self) -> Optional[LocationTable]:
        """ Return the node location cache, if enabled.
            This can be used to manually look up locations of nodes.
        """
        return self._node_store

    def with_locations(self, storage: str='flex_mem') -> 'FileProcessor':
        """ Enable caching of node locations. This is necessary in order
            to get geometries for ways and relations.
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

            Automatically enables location caching, if it was not yet set.
            It uses the default location cache type. To use a different
            cache type, you need to call with_locations() explicity.

            Area processing requires that the file is read twice. This
            happens transparently.
        """
        if self._area_handler is None:
            self._area_handler = osmium.area.AreaManager()
            if self._node_store is None:
                self.with_locations()
        self._area_filters.extend(filters)
        return self

    def with_filter(self, filt: 'osmium._osmium.HandlerLike') -> 'FileProcessor':
        """ Add a filter function that is called before an object is
            returned in the iterator. Filters are applied sequentially
            in the order they were added.
        """
        self._filters.append(filt)
        return self


    def handler_for_filtered(self, handler: 'osmium._osmium.HandlerLike') -> 'FileProcessor':
        """ Set a handler to be called on all objects that have been
            filtered out and are not presented to the iterator loop.
        """
        self._filtered_handler = handler
        return self

    def __iter__(self) -> Iterator[OSMEntity]:
        """ Return the iterator over the file.
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
