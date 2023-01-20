# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Optional, Callable, TypeVar

from osmium._osmium import SimpleHandler
from osmium.osm import Node, Way, Relation, Area, Changeset

T = TypeVar('T')
HandlerFunc = Optional[Callable[[T], None]]


def make_simple_handler(node: HandlerFunc[Node] = None,
                        way: HandlerFunc[Way] = None,
                        relation: HandlerFunc[Relation] = None,
                        area: HandlerFunc[Area] = None,
                        changeset: HandlerFunc[Changeset] = None) -> SimpleHandler:
    """ Convenience function that creates a `SimpleHandler` from a set of
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
