# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
""" Helper functions for change file handling. """
from typing import NamedTuple, Optional
import logging
import datetime as dt
from collections import namedtuple
from osmium.io import Reader as oreader
from osmium.osm import NOTHING

LOG = logging.getLogger('pyosmium')

class ReplicationHeader(NamedTuple):
    url: Optional[str]
    sequence: Optional[int]
    timestamp: Optional[dt.datetime]


def get_replication_header(fname: str) -> ReplicationHeader:
    """ Scans the given file for an Osmosis replication header. It returns
        a namedtuple with `url`, `sequence` and `timestamp`. Each or all fields
        may be None, if the piece of information is not avilable. If any of
        the fields has an invalid format, it is simply ignored.

        The given file must exist and be readable for osmium, otherwise
        a `RuntimeError` is raised.
    """

    r = oreader(fname, NOTHING)
    h = r.header()

    tsstr = h.get("osmosis_replication_timestamp")
    url: Optional[str] = h.get("osmosis_replication_base_url")

    if url or tsstr:
        LOG.debug("Replication information found in OSM file header.")

    if url:
        LOG.debug("Replication URL: %s", url)
        # the sequence ID is only considered valid, if an URL is given
        seqstr = h.get("osmosis_replication_sequence_number")
        seq: Optional[int]
        if seqstr:
            LOG.debug("Replication sequence: %s", seqstr)
            try:
                seq = int(seqstr)
                if seq < 0:
                    LOG.warning("Sequence id '%d' in OSM file header is negative. Ignored.", seq)
                    seq = None
            except ValueError:
                LOG.warning("Sequence id '%s' in OSM file header is not a number. Ignored.", seq)
                seq = None
        else:
            seq = None
    else:
        url = None
        seq = None

    if tsstr:
        LOG.debug("Replication timestamp: %s", tsstr)
        try:
            ts = dt.datetime.strptime(tsstr, "%Y-%m-%dT%H:%M:%SZ")
            ts = ts.replace(tzinfo=dt.timezone.utc)

        except ValueError:
            LOG.warning("Date in OSM file header is not in ISO8601 format (e.g. 2015-12-24T08:08Z). Ignored.")
            ts = None
    else:
        ts = None

    return ReplicationHeader(url, seq, ts)
