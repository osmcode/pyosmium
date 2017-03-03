""" Helper functions for change file handling. """

import logging
from datetime import datetime
from collections import namedtuple
from osmium.io import Reader as oreader

log = logging.getLogger('pyosmium')

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

    r = oreader(fname)
    h = r.header()

    ts = h.get("osmosis_replication_timestamp")
    seq = h.get("osmosis_replication_sequence_number")
    url = h.get("osmosis_replication_base_url")

    if url or seq or ts:
        log.debug("Replication information found in OSM file header.")

    if url:
        log.debug("Replication URL: %s" % url)
    else:
        url = None

    if seq:
        log.debug("Replication sequence: %s" % seq)
        try:
            seq = int(seq)
            if seq < 0:
                log.warning("Sequence id '%d' in OSM file header is negative. Ignored." % seq)
        except ValueError:
            log.warning("Sequence id '%s' in OSM file header is not a number.Ignored" % seq)
    else:
        seq = None

    if ts:
        log.debug("Replication timestamp: %s" % ts)
        try:
            ts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            log.warning("Date in OSM file header is not in ISO8601 format (e.g. 2015-12-24T08:08Z). Ignored")
    else:
        ts = None

    return ReplicationHeader(url, seq, ts)
