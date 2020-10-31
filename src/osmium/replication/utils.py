""" Helper functions for change file handling. """

import logging
import datetime as dt
from collections import namedtuple
from osmium.io import Reader as oreader
from osmium.osm import NOTHING

LOG = logging.getLogger('pyosmium')

ReplicationHeader = namedtuple('ReplicationHeader',
                               ['url', 'sequence', 'timestamp'])

def get_replication_header(fname):
    """ Scans the given file for an Osmosis replication header. It returns
        a namedtuple with `url`, `sequence` and `timestamp`. Each or all fields
        may be None, if the piece of information is not avilable. If any of
        the fields has an invalid format, it is simply ignored.

        The given file must exist and be readable for osmium, otherwise
        a `RuntimeError` is raised.
    """

    r = oreader(fname, NOTHING)
    h = r.header()

    ts = h.get("osmosis_replication_timestamp")
    url = h.get("osmosis_replication_base_url")

    if url or ts:
        LOG.debug("Replication information found in OSM file header.")

    if url:
        LOG.debug("Replication URL: %s", url)
        # the sequence ID is only considered valid, if an URL is given
        seq = h.get("osmosis_replication_sequence_number")
        if seq:
            LOG.debug("Replication sequence: %s", seq)
            try:
                seq = int(seq)
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

    if ts:
        LOG.debug("Replication timestamp: %s", ts)
        try:
            ts = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            ts = ts.replace(tzinfo=dt.timezone.utc)

        except ValueError:
            LOG.warning("Date in OSM file header is not in ISO8601 format (e.g. 2015-12-24T08:08Z). Ignored.")
            ts = None
    else:
        ts = None

    return ReplicationHeader(url, seq, ts)
