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
    def __init__(self) -> None:...
    def first_pass_handler(self) -> 'AreaManager':...
    def second_pass_handler(self, *handlers: HandlerLike) -> AreaManagerSecondPassHandler:...
    def second_pass_to_buffer(self, callback: BufferIterator) -> AreaManagerBufferHandler:...
