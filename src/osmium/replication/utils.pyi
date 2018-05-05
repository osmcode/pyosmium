import logging
from datetime import datetime

import typing

log: logging.Logger

Sequence = typing.NewType('Sequence', int)
Timestamp = typing.NewType('Timestamp', datetime)

ReplicationHeader = typing.NamedTuple('ReplicationHeader',
                                      [('url', str), ('sequence', Sequence), ('timestamp', Timestamp)])


def get_replication_header(fname: str) -> ReplicationHeader: ...
