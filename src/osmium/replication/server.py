""" Helper functions to communicate with replication servers.
"""

import sys
try:
    import urllib.request as urlrequest
except ImportError:
    import urllib2 as urlrequest
try:
    import urllib.error as urlerror
except ImportError:
    import urllib2 as urlerror
import datetime as dt
from collections import namedtuple
from math import ceil
from osmium import MergeInputReader
from osmium import io as oio

import logging

log = logging.getLogger('pyosmium')
log.addHandler(logging.NullHandler())

OsmosisState = namedtuple('OsmosisState', ['sequence', 'timestamp'])
DownloadResult = namedtuple('DownloadResult', ['id', 'reader', 'newest'])

class ReplicationServer(object):
    """ Represents a server that publishes replication data. Replication
        change files allow to keep local OSM data up-to-date without downloading
        the full dataset again.
    """

    def __init__(self, url, diff_type='osc.gz'):
        self.baseurl = url
        self.diff_type = diff_type

    def collect_diffs(self, start_id, max_size=1024):
        """ Create a MergeInputReader and download diffs starting with sequence
            id `start_id` into it. `max_size`
            restricts the number of diffs that are downloaded. The download
            stops as soon as either a diff cannot be downloaded or the
            unpacked data in memory exceeds `max_size` kB.

            If some data was downloaded, returns a namedtuple with three fields:
            `id` contains the sequence id of the last downloaded diff, `reader`
            contains the MergeInputReader with the data and `newest` is a
            sequence id of the most recent diff available.

            Returns None if there was an error during download or no new
            data was available.
        """
        left_size = max_size * 1024
        current_id = start_id

        # must not read data newer than the published sequence id
        # or we might end up reading partial data
        newest = self.get_state_info()

        if newest is None or current_id > newest.sequence:
            return None

        rd = MergeInputReader()

        while left_size > 0 and current_id <= newest.sequence:
            try:
                diffdata = self.get_diff_block(current_id)
            except:
                diffdata = ''
            if len(diffdata) == 0:
                if start_id == current_id:
                    return None
                break

            left_size -= rd.add_buffer(diffdata, self.diff_type)
            log.debug("Downloaded change %d. (%d kB available in download buffer)"
                      % (current_id, left_size / 1024))
            current_id += 1

        return DownloadResult(current_id - 1, rd, newest.sequence)

    def apply_diffs(self, handler, start_id, max_size=1024, simplify=True):
        """ Download diffs starting with sequence id `start_id`, merge them
            together and then apply them to handler `handler`. `max_size`
            restricts the number of diffs that are downloaded. The download
            stops as soon as either a diff cannot be downloaded or the
            unpacked data in memory exceeds `max_size` kB.

            The function returns the sequence id of the last diff that was
            downloaded or None if the download failed completely.
        """
        diffs = self.collect_diffs(start_id, max_size)

        if diffs is None:
            return None

        diffs.reader.apply(handler, simplify)

        return diffs.id

    def apply_diffs_to_file(self, infile, outfile, start_id, max_size=1024,
                            set_replication_header=True):
        """ Download diffs starting with sequence id `start_id`, merge them
            with the data from the OSM file named `infile` and write the result
            into a file with the name `outfile`. The output file must not yet
            exist.

            `max_size` restricts the number of diffs that are downloaded. The
            download stops as soon as either a diff cannot be downloaded or the
            unpacked data in memory exceeds `max_size` kB.

            If `set_replication_header` is true then the URL of the replication
            server and the sequence id and timestamp of the last diff applied
            will be written into the `writer`. Note that this currently works
            only for the PBF format.

            The function returns a tuple of last downloaded sequence id and
            newest available sequence id if new data has been written or None
            if no data was available or the download failed completely.
        """
        diffs = self.collect_diffs(start_id, max_size)

        if diffs is None:
            return None

        reader = oio.Reader(infile)
        has_history = reader.header().has_multiple_object_versions

        h = oio.Header()
        h.has_multiple_object_versions = has_history
        if set_replication_header:
            h.set("osmosis_replication_base_url", self.baseurl)
            h.set("osmosis_replication_sequence_number", str(diffs.id))
            info = self.get_state_info(diffs.id)
            h.set("osmosis_replication_timestamp", info.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))

        writer = oio.Writer(outfile, h)

        log.debug("Merging changes into OSM file.")

        diffs.reader.apply_to_reader(reader, writer, has_history)

        reader.close()
        writer.close()

        return (diffs.id, diffs.newest)


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
            log.debug("Trying with Id %s" % lowerid)
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
                ts_int = (upper.timestamp - lower.timestamp).total_seconds()
                seq_int = upper.sequence - lower.sequence
                goal = (timestamp - lower.timestamp).total_seconds()
                base_splitid = lower.sequence + ceil(goal * seq_int / ts_int)
                if base_splitid >= upper.sequence:
                    base_splitid = upper.sequence - 1
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
        """ Downloads and returns the state information for the given
            sequence. If the download is successful, a namedtuple with
            `sequence` and `timestamp` is returned, otherwise the function
            returns `None`.
        """
        try:
            response = urlrequest.urlopen(self.get_state_url(seq))
        except:
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
                kv = line.split('=', 2)
                if len(kv) != 2:
                    return None
                if kv[0] == 'sequenceNumber':
                    seq = int(kv[1])
                elif kv[0] == 'timestamp':
                    ts = dt.datetime.strptime(kv[1], "%Y-%m-%dT%H\\:%M\\:%SZ")
                    if sys.version_info >= (3,0):
                        ts = ts.replace(tzinfo=dt.timezone.utc)
            line = response.readline()

        return OsmosisState(sequence=seq, timestamp=ts)

    def get_diff_block(self, seq):
        """ Downloads the diff with the given sequence number and returns
            it as a byte sequence. Throws a `urllib.error.HTTPError`
            (or `urllib2.HTTPError` in python2)
            if the file cannot be downloaded.
        """
        return urlrequest.urlopen(self.get_diff_url(seq)).read()


    def get_state_url(self, seq):
        """ Returns the URL of the state.txt files for a given sequence id.

            If seq is `None` the URL for the latest state info is returned,
            i.e. the state file in the root directory of the replication
            service.
        """
        if seq is None:
            return self.baseurl + '/state.txt'

        return '%s/%03i/%03i/%03i.state.txt' % (self.baseurl,
                     seq / 1000000, (seq % 1000000) / 1000, seq % 1000)


    def get_diff_url(self, seq):
        """ Returns the URL to the diff file for the given sequence id.
        """
        return '%s/%03i/%03i/%03i.%s' % (self.baseurl,
                     seq / 1000000, (seq % 1000000) / 1000, seq % 1000,
                     self.diff_type)
