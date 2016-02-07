""" Helper functions to communicate with replication servers.
"""

import urllib.request
import urllib.error
from datetime import datetime
from collections import namedtuple
from math import ceil

OsmosisState = namedtuple('OsmosisState', ['sequence', 'timestamp'])

class ReplicationServer(object):
    """ Represents a server that publishes replication data. Replication
        change files allow to keep local OSM data up-to-date without downloading
        the full dataset again.
    """

    def __init__(self, url):
        self.baseurl = url


    def timestamp_to_sequence(self, timestamp, balanced_search=False):
        """ Get the sequence number of the replication file that contains the
            given timestamp. The search algorithm is optimised for replication
            servers that publish updates in regular intervals. For servers
            with irregular change file publication dates 'balanced_search`
            should be set to true so that a standard binary search for the
            sequence will be used. The default is good for all known
            OSM replication services.
        """

        # get the current timestamp from the server
        upper = self.get_state_info()

        if upper is None:
            return None
        if timestamp >= upper.timestamp or upper.sequence <= 0:
            return upper.sequence

        # find a state file that is before the required timestamp
        lower = None
        lowerid = 0
        while lower is None:
            lower = self.get_state_info(lowerid)

            if lower is not None and lower.timestamp >= timestamp:
                if lower.sequence == 0 or lower.sequence + 1 >= upper.sequence:
                    return lower.sequence
                upper = lower
                lower = None
                lowerid = 0

            if lower is None:
                # no lower yet, so try a higher id (binary search wise)
                newid = int((lowerid + upper.sequence) / 2)
                if newid <= lowerid:
                    # nothing suitable found, so upper is probably the best we can do
                    return upper.sequence
                lowerid = newid

        # Now do a binary search between upper and lower.
        # We could be clever here and compute the most likely state file
        # by interpolating over the timestamps but that creates a whole ton of
        # special cases that need to be handled correctly.
        while True:
            if balanced_search:
                base_splitid = int((lower.sequence + upper.sequence) / 2)
            else:
                ts_int = upper.timestamp - lower.timestamp
                seq_int = upper.sequence - lower.sequence
                goal = timestamp - lower.timestamp
                base_splitid = lower.sequence + ceil(goal * seq_int / ts_int)
                if base_splitid == upper.sequence:
                    base_splitid -= 1
            split = self.get_state_info(base_splitid)

            if split is None:
                # file missing, search the next towards lower
                splitid = base_splitid - 1
                while split is None and splitid > lower.sequence:
                    split = self.get_state_info(splitid)
                    splitid -= 1
            if split is None:
                # still nothing? search towards upper
                splitid = base_splitid + 1
                while split is None and splitid < upper.sequence:
                    split = self.get_state_info(splitid)
                    splitid += 1
            if split is None:
                # still nothing? Then lower has to do
                return lower.sequence

            # set new boundary
            if split.timestamp < timestamp:
                lower = split
            else:
                upper = split

            if lower.sequence + 1 >= upper.sequence:
                return lower.sequence


    def get_state_info(self, seq=None):
        try:
            response = urllib.request.urlopen(self.sequence_to_state_url(seq))
        except urllib.error.HTTPError:
            return None

        ts = None
        seq = None
        line = response.readline()
        while line:
            line = line.decode('utf-8')
            if '#' in line:
                line = line[0:line.index('#')]
            else:
                line = line.strip()
            if line:
                key, val = line.split('=', 2)
                if key == 'sequenceNumber':
                    seq = int(val)
                elif key == 'timestamp':
                    ts = datetime.strptime(val, "%Y-%m-%dT%H\\:%M\\:%SZ")
            line = response.readline()

        return OsmosisState(sequence=seq, timestamp=ts)

    def sequence_to_state_url(self, seq):
        """ Returns the URL of the state.txt files for a given sequence id.
        """
        if seq is None:
            return self.baseurl + '/state.txt'

        return '%s/%03i/%03i/%03i.state.txt' % (self.baseurl,
                     seq / 1000000, (seq % 100000) / 1000, seq % 1000)


