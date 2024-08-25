# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.

from . import BaseHandler, BufferIterator
from ._osmium import HandlerLike

class AreaManagerSecondPassHandler(BaseHandler): ...

class AreaManagerBufferHandler(BaseHandler):...


class AreaManager(BaseHandler):
    """ Handler class that manages building area objects from ways
        and relations.

        Building area objects always requires two passes through the file:
        in the first pass, the area manager collects the relation candidates
        for areas and IDs of all ways that are needed to build their areas.
        During the second pass of the file the areas are assembled: areas
        from ways are created immediately when the handler encounters a
        closed way. Areas for relations are built as soon as all the ways
        that the relation needs are available.

        You usually should not be using the AreaManager direcly. The
        interface of the handler is considered an internal implementation
        detail and may change in future versions of pyosmium. Area assembly
        can be enabled through the [SimpleHandler][osmium.SimpleHandler]
        and the [FileProcessor][osmium.FileProcessor].
    """
    def __init__(self) -> None:
        """ Set up a new area manager.
        """
    def first_pass_handler(self) -> 'AreaManager':
        """ Return a handler object to be used for the first pass through
            a file. It collects information about area relations and their
            way members.
        """
    def second_pass_handler(self, *handlers: HandlerLike) -> AreaManagerSecondPassHandler:
        """ Return a handler used for the second pass of the
            file, where areas are assembled. Pass the chain of filters and
            handlers that should be applied the areas.
        """
    def second_pass_to_buffer(self, callback: BufferIterator) -> AreaManagerBufferHandler:
        """ Return a handler for the second pass of the file, which stores
            assembled areas in the given buffer.
        """
