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
    def __init__(self) -> None: ...


class KeyFilter(BaseFilter):
    def __init__(self, *keys: str) -> None: ...


class TagFilter(BaseFilter):
    def __init__(self, *tags: Tuple[str, str]) -> None: ...


class EntityFilter(BaseFilter):
    def __init__(self, entities: osm_entity_bits) -> None: ...


class IdFilter(BaseFilter):
    def __init__(self, ids: Iterable[int]) -> None: ...


class GeoInterfaceFilter(BaseFilter):
    def __init__(self, drop_invalid_geometries: bool= ..., tags: Iterable[str] = ...) -> None: ...
