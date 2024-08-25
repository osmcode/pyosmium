# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Optional, Callable, TypeVar, TYPE_CHECKING

from .simple_handler import SimpleHandler
from .osm import Node, Way, Relation, Area, Changeset
from .index import create_map
from ._osmium import SimpleWriter, NodeLocationsForWays

from ._osmium import MergeInputReader as MergeInputReader

if TYPE_CHECKING:
    from ._osmium import HandlerLike

T = TypeVar('T')
HandlerFunc = Optional[Callable[[T], None]]


def make_simple_handler(node: HandlerFunc[Node] = None,
                        way: HandlerFunc[Way] = None,
                        relation: HandlerFunc[Relation] = None,
                        area: HandlerFunc[Area] = None,
                        changeset: HandlerFunc[Changeset] = None) -> SimpleHandler:
    """ _(deprecated)_ Convenience function that creates a
        [SimpleHandler](Handler-Processing.md#osmium.SimpleHandler) from a set of
        callback functions. Each of the parameters takes an optional callable
        that must expect a single positional parameter with the object being
        processed.
    """
    class __HandlerWithCallbacks(SimpleHandler):
        pass

    if node is not None:
        setattr(__HandlerWithCallbacks, "node", staticmethod(node))
    if way is not None:
        setattr(__HandlerWithCallbacks, "way", staticmethod(way))
    if relation is not None:
        setattr(__HandlerWithCallbacks, "relation", staticmethod(relation))
    if area is not None:
        setattr(__HandlerWithCallbacks, "area", staticmethod(area))
    if changeset is not None:
        setattr(__HandlerWithCallbacks, "changeset", staticmethod(changeset))

    return __HandlerWithCallbacks()


# WriteHandler no longer exists. SimpleWriter can now function as a handler.
class WriteHandler(SimpleWriter):
    """ (Deprecated) Handler function that writes all data directly to a file.

        This is now simply an alias for SimpleWriter. Please refer to its
        documentation.
    """

    def __init__(self, filename: str, bufsz: int=4096*1024, filetype: str="") -> None:
        super().__init__(filename, bufsz=bufsz, filetype=filetype)


def _merge_apply(self: MergeInputReader, *handlers: 'HandlerLike', idx: str = '', simplify: bool = True) -> None:
    if idx:
        lh = NodeLocationsForWays(create_map(idx))
        lh.ignore_errors()
        self._apply_internal(lh, *handlers, simplify=simplify)

    self._apply_internal(*handlers, simplify=simplify)

MergeInputReader.apply = _merge_apply # type: ignore[method-assign]
