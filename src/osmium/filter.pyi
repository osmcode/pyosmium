# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Tuple, Iterable

from ._osmium import BaseFilter
from .osm import osm_entity_bits

class EmptyTagFilter(BaseFilter):
    """ Filter class which only lets pass objects which have at least one tag.
    """
    def __init__(self) -> None:
        """ Create a new filter object.
        """


class KeyFilter(BaseFilter):
    """ Filter class which lets objects pass which have tags with at
        least one of the listed keys.

        This filter functions like an OR filter. To create an AND filter
        (a filter that lets object pass that have tags with all the listed
        keys) you need to chain multiple KeyFilter objects.
    """
    def __init__(self, *keys: str) -> None:
        """ Create a new filter object. The parameters list the keys
            by which the filter should choose the objects. At least one
            key is required.
        """


class TagFilter(BaseFilter):
    """ Filter class which lets objects pass which have tags with at
        least one of the listed key-value pair.

        This filter functions like an OR filter. To create an AND filter
        (a filter that lets object pass that have tags with all the listed
        key-value pairs) you need to chain multiple TagFilter objects.
    """
    def __init__(self, *tags: Tuple[str, str]) -> None:
        """ Create a new filter object. The parameters list the key-value
            pairs by which the filter should choose objects. Each pair must
            be a tuple with two strings and at least one pair is required.
        """


class EntityFilter(BaseFilter):
    """ Filter class which lets pass objects according to their type.
    """
    def __init__(self, entities: osm_entity_bits) -> None:
        """ Crate a new filter object. Only objects whose type is listed
            in _entities_ can pass the filter.
        """


class IdFilter(BaseFilter):
    """ Filter class which only lets pass objects with given IDs.

        This filter usually only makes sense when used together with
        a type restriction, set using `enable_for()`.
    """
    def __init__(self, ids: Iterable[int]) -> None:
        """ Create a new filter object. _ids_ contains the IDs the filter
            should let pass. It can be any iterable over ints.
        """


class GeoInterfaceFilter(BaseFilter):
    """ Filter class, which adds a [__geo_interface__](https://gist.github.com/sgillies/2217756) attribute to object which have geometry information.

        The filter can process node, way and area types. All other types
        will be dropped. To create geometries for ways, the location cache needs
        to be enabled. Relations and closed ways can only be transformed
        to polygons when the area handler is enabled.
    """
    def __init__(self, drop_invalid_geometries: bool= ..., tags: Iterable[str] = ...) -> None:
        """ Create a new filter object. The filter will usually drop all
            objects that do not have a geometry. Set _drop_invalid_geometries_
            to `False` to just let them pass.

            The filter will normally add all tags it finds as properties to
            the GeoInterface output. To filter the tags to relevant ones, set
            _tags_ to the desired list.
        """
