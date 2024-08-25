# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import List

import osmium.osm

class LocationTable:
    """ A map from a node ID to a location object. Location can be set
        and queried using the standard [] notation for dicts.
        This implementation works only with positive node IDs.
    """
    def clear(self) -> None:
        """ Remove all entries from the location table..
        """
    def get(self, id: int) -> osmium.osm.Location:
        """ Get the location for the given node ID. Raises a `KeyError`
            when there is no location for the given id.
        """
    def set(self, id: int, loc: osmium.osm.Location) -> None:
        """ Set the location for the given node ID.
        """
    def used_memory(self) -> int:
        """ Return the size (in bytes) currently allocated by this location table.
        """
    def __getitem__(self, id: int) -> osmium.osm.Location: ...
    def __setitem__(self, id: int, loc: osmium.osm.Location) -> None: ...



class IdSet:
    """ Compact storage for a set of IDs.
    """
    def __init__(self) -> None:
        """ Initialise an empty set.
        """
    def set(self, id: int) -> None:
        """ Add an ID to the storage.
            Does nothing if the ID is already contained.
        """
    def unset(self, id: int) -> None:
        """ Remove an ID from the storage.
            Does nothing if the ID is not in the storage.
        """
    def get(self, id: int) -> bool:
        """ Check if the given ID is in the storage.
        """
    def empty(self) -> bool:
        """ Check if no IDs are stored yet.
        """
    def clear(self) -> None:
        """ Remove all IDs from the set.
        """
    def __len__(self) -> int: ...
    def __contains__(self, id: int) -> bool: ...


def create_map(map_type: str) -> LocationTable:
    """ Create a new location store. Use the _map_type_ parameter
        to choose a concrete implementation. Some implementations
        take additiona configuration parameters, which can also be
        set through the _map_type_ argument. For example,
        to create an array cache backed by a file 'foo.store',
        the map_type needs to be set to `dense_file_array,foo.store`.
        Read the section on [location storage][location-storage] in the
        user manual for more information about the different implementations.
    """
def map_types() -> List[str]:
    """ Return a list of strings with valid types for the location table.
    """
