# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
""" Helper functions to communicate with replication servers.
"""
from typing import NamedTuple, Optional, Any, Iterator, cast, Mapping, Tuple, Dict
import urllib.request as urlrequest
from urllib.error import URLError
import datetime as dt
from contextlib import contextmanager
from math import ceil

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from osmium import MergeInputReader, BaseHandler
from osmium import io as oio
from osmium import version

import logging

LOG = logging.getLogger('pyosmium')
LOG.addHandler(logging.NullHandler())


class OsmosisState(NamedTuple):
    """ Represents a state file of a replication server.
    """
    sequence: int
    "The ID of the replication change on the server."
    timestamp: dt.datetime
    "Date until when changes are contained in the change file."


class DownloadResult(NamedTuple):
    """ Downloaded change.
    """
    id: int
    "The ID of the latest downloaded replication change on the server."
    reader: MergeInputReader
    "[osmium.MergeInputReader][] with all downloaded changes."
    newest: int
    "ID of the newest change available on the server."


class ReplicationServer:
    """ Represents a connection to a  server that publishes replication data.
        Replication change files allow to keep local OSM data up-to-date without
        downloading the full dataset again.

        ReplicationServer may be used as a context manager. In this case, it
        internally keeps a connection to the server making downloads faster.
    """

    def __init__(self, url: str, diff_type: str = 'osc.gz') -> None:
        """ Set up the connection to a replication server.

            `url` contains the base URL of the replication service. This is
            the directory that contains the state file with the current
            state. If the replication service serves something other
            than osc.gz files, set the `diff_type` to the given file suffix.
        """

        self.baseurl = url
        self.diff_type = diff_type
        self.extra_request_params: Dict[str, Any] = dict(timeout=60, stream=True)
        self.session: Optional[requests.Session] = None
        self.retry = Retry(total=3, backoff_factor=0.5, allowed_methods={'GET'},
                           status_forcelist=[408, 429, 500, 502, 503, 504])

    def close(self) -> None:
        """ Close any open connection to the replication server.
        """
        if self.session is not None:
            self.session.close()
            self.session = None

    def __enter__(self) -> 'ReplicationServer':
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=self.retry))
        self.session.mount('https://', HTTPAdapter(max_retries=self.retry))
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def set_request_parameter(self, key: str, value: Any) -> None:
        """ Set a parameter which will be handed to the requests library
            when calling `requests.get()`. This
            may be used to set custom headers, timeouts and similar parameters.
            See the `requests documentation <https://requests.readthedocs.io/en/latest/api/?highlight=get#requests.request>`_
            for possible parameters. Per default, a timeout of 60 sec is set
            and streaming download enabled.
        """  # noqa
        self.extra_request_params[key] = value

    def make_request(self, url: str) -> urlrequest.Request:
        headers = {"User-Agent": f"pyosmium/{version.pyosmium_release}"}
        return urlrequest.Request(url, headers=headers)

    def open_url(self, url: urlrequest.Request) -> Any:
        """ Download a resource from the given URL and return a byte sequence
            of the content.
        """
        if 'headers' in self.extra_request_params:
            get_params = self.extra_request_params
        else:
            get_params = dict(self.extra_request_params)
            get_params['headers'] = {k: v for k, v in url.header_items()}

        if self.session is not None:
            return self.session.get(url.get_full_url(), **get_params)

        @contextmanager
        def _get_url_with_session() -> Iterator[requests.Response]:
            with requests.Session() as session:
                session.mount('http://', HTTPAdapter(max_retries=self.retry))
                session.mount('https://', HTTPAdapter(max_retries=self.retry))
                request = session.get(url.get_full_url(), **get_params)
                yield request

        return _get_url_with_session()

    def collect_diffs(self, start_id: int, max_size: Optional[int] = None,
                      end_id: Optional[int] = None) -> Optional[DownloadResult]:
        """ Create a MergeInputReader and download diffs starting with sequence
            id `start_id` into it. `end_id` optionally gives the highest
            sequence number to download. `max_size` restricts the number of
            diffs that are downloaded by size. If neither `end_id` nor
            `max_size` are given, then download default to stop after 1MB.

            The download stops as soon as
            1. a diff cannot be downloaded or
            2. the end_id (inclusive) is reached or
            3. the unpacked data in memory exceeds `max_size` kB or,
               when no `end_id` and `max_size` are given, 1024kB.

            If some data was downloaded, returns a namedtuple with three fields:
            `id` contains the sequence id of the last downloaded diff, `reader`
            contains the MergeInputReader with the data and `newest` is a
            sequence id of the most recent diff available.

            Returns None if there was no new data was available.

            If there is an error during the download, then the function will
            simply return the already downloaded data. If the reported
            error is a client error (HTTP 4xx) and happens during the download
            of the first diff, then a ::request.HTTPError:: is raised: this
            condition is likely to be permanent and the caller should not
            simply retry without investigating the cause.
        """
        # must not read data newer than the published sequence id
        # or we might end up reading partial data
        newest = self.get_state_info()

        if newest is None or start_id > newest.sequence:
            return None

        current_id = start_id
        left_size: Optional[int] = None
        if max_size is not None:
            left_size = max_size * 1024
        elif end_id is None:
            left_size = 1024 * 1024

        rd = MergeInputReader()

        while (left_size is None or left_size > 0) \
                and (end_id is None or current_id <= end_id) \
                and current_id <= newest.sequence:
            try:
                diffdata = self.get_diff_block(current_id)
            except requests.RequestException as ex:
                if start_id == current_id \
                        and ex.response is not None \
                        and (ex.response.status_code % 100 == 4):
                    # If server directly responds with a client error,
                    # reraise the exception to signal a potentially permanent
                    # error.
                    LOG.error("Permanent server error: %s", ex.response)
                    raise ex
                # In all other cases, process whatever diffs we have and
                # encourage a retry.
                LOG.error("Error during diff download: %s", ex)
                LOG.error("Bailing out.")
                diffdata = ''
            if len(diffdata) == 0:
                if start_id == current_id:
                    return None
                break

            diff_size = rd.add_buffer(diffdata, self.diff_type)
            if left_size is None:
                LOG.debug("Downloaded change %d.", current_id)
            else:
                left_size -= diff_size
                LOG.debug("Downloaded change %d. (%d kB available in download buffer)",
                          current_id, left_size / 1024)
            current_id += 1

        return DownloadResult(current_id - 1, rd, newest.sequence)

    def apply_diffs(self, handler: BaseHandler, start_id: int,
                    max_size: Optional[int] = None,
                    idx: str = "", simplify: bool = True,
                    end_id: Optional[int] = None) -> Optional[int]:
        """ Download diffs starting with sequence id `start_id`, merge them
            together and then apply them to handler `handler`. `end_id`
            optionally gives the highest sequence id to download. `max_size`
            allows to restrict the amount of diffs that are downloaded.
            Downloaded diffs are temporarily saved in memory and this parameter
            ensures that pyosmium doesn't run out of memory. `max_size`
            is the maximum size in kB this internal buffer may have.

            If neither `end_id` nor `max_size` are given, the download is
            restricted to a maximum size of 1MB. The download also
            stops when the most recent diff has been processed.

            If `idx` is set, a location cache will be created and applied to
            the way nodes. You should be aware that diff files usually do not
            contain the complete set of nodes when a way is modified. That means
            that you cannot just create a new location cache, apply it to a diff
            and expect to get complete way geometries back. Instead you need to
            do an initial data import using a persistent location cache to
            obtain a full set of node locations and then reuse this location
            cache here when applying diffs.

            Diffs may contain multiple versions of the same object when it was
            changed multiple times during the period covered by the diff. If
            `simplify` is set to False then all versions are returned. If it
            is True (the default) then only the most recent version will be
            sent to the handler.

            The function returns the sequence id of the last diff that was
            downloaded or None if the download failed completely.
        """
        diffs = self.collect_diffs(start_id, end_id=end_id, max_size=max_size)

        if diffs is None:
            return None

        diffs.reader.apply(handler, idx=idx, simplify=simplify)

        return diffs.id

    def apply_diffs_to_file(self, infile: str, outfile: str, start_id: int,
                            max_size: Optional[int] = None,
                            set_replication_header: bool = True,
                            extra_headers: Optional[Mapping[str, str]] = None,
                            outformat: Optional[str] = None,
                            end_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """ Download diffs starting with sequence id `start_id`, merge them
            with the data from the OSM file named `infile` and write the result
            into a file with the name `outfile`. The output file must not yet
            exist.

            `end_id` optionally gives the highest sequence id to download.
            `max_size` allows to restrict the amount of diffs that are
            downloaded. Downloaded diffs are saved in memory and this parameter
            ensures that pyosmium doesn't run out of memory. `max_size`
            is the maximum size in kB this internal buffer may have.

            If neither `end_id` nor `max_size` are given, the
            download is restricted to a maximum size of 1MB. The download also
            stops when the most recent diff has been processed.

            If `set_replication_header` is true then the URL of the replication
            server and the sequence id and timestamp of the last diff applied
            will be written into the `writer`. Note that this currently works
            only for the PBF format.

            `extra_headers` is a dict with additional header fields to be set.
            Most notably, the 'generator' can be set this way.

            `outformat` sets the format of the output file. If None, the format
            is determined from the file name.

            The function returns a tuple of last downloaded sequence id and
            newest available sequence id if new data has been written or None
            if no data was available or the download failed completely.
        """
        diffs = self.collect_diffs(start_id, end_id=end_id, max_size=max_size)

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
            if info is not None:
                h.set("osmosis_replication_timestamp",
                      info.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if extra_headers is not None:
            for k, v in extra_headers.items():
                h.set(k, v)

        if outformat is None:
            of = oio.File(outfile)
        else:
            of = oio.File(outfile, outformat)

        of.has_multiple_object_versions = has_history
        writer = oio.Writer(of, h)

        LOG.debug("Merging changes into OSM file.")

        diffs.reader.apply_to_reader(reader, writer, has_history)

        reader.close()
        writer.close()

        return (diffs.id, diffs.newest)

    def timestamp_to_sequence(self, timestamp: dt.datetime,
                              balanced_search: bool = False,
                              limit_by_oldest_available: bool = False) -> Optional[int]:
        """ Get the sequence number of the replication file that contains the
            given timestamp. The search algorithm is optimised for replication
            servers that publish updates in regular intervals. For servers
            with irregular change file publication dates 'balanced_search`
            should be set to true so that a standard binary search for the
            sequence will be used. The default is good for all known
            OSM replication services.

            When `limit_by_oldest_available` is set, then the function will
            return None when the server replication does not start at 0 and
            the given timestamp is older than the oldest available timestamp
            on the server. Some replication servers do not keep the full
            history and this flag avoids accidentally trying to download older
            data. The downside is that the function will never return the
            oldest available sequence ID when the flag is set.
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
            LOG.debug("Trying with Id %s", lowerid)
            lower = self.get_state_info(lowerid)

            if lower is not None and lower.timestamp >= timestamp:
                if lower.sequence == 0:
                    return 0
                if lower.sequence + 1 >= upper.sequence:
                    return None if limit_by_oldest_available else lower.sequence
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

    def get_state_info(self, seq: Optional[int] = None, retries: int = 2) -> Optional[OsmosisState]:
        """ Downloads and returns the state information for the given
            sequence. If the download is successful, a namedtuple with
            `sequence` and `timestamp` is returned, otherwise the function
            returns `None`. `retries` sets the number of times the download
            is retried when pyosmium detects a truncated state file.
        """
        for _ in range(retries + 1):
            ts = None
            next_seq = None

            try:
                with self.open_url(self.make_request(self.get_state_url(seq))) as response:
                    if hasattr(response, 'iter_lines'):
                        # generated by requests
                        response.raise_for_status()
                        lines = response.iter_lines()
                    else:
                        lines = response

                    for line in lines:
                        line = line.decode('utf-8').strip()
                        if '#' in line:
                            line = line[0:line.index('#')]
                        else:
                            line = line.strip()
                        if line:
                            kv = line.split('=', 2)
                            if len(kv) != 2:
                                return None
                            if kv[0] == 'sequenceNumber':
                                next_seq = int(kv[1])
                            elif kv[0] == 'timestamp':
                                try:
                                    ts = dt.datetime.strptime(kv[1], "%Y-%m-%dT%H\\:%M\\:%SZ")
                                except ValueError:
                                    break
                                ts = ts.replace(tzinfo=dt.timezone.utc)

            except (URLError, IOError) as err:
                LOG.debug("Loading state info failed with: %s", str(err))
                return None

            if ts is not None and next_seq is not None:
                return OsmosisState(sequence=next_seq, timestamp=ts)

        return None

    def get_diff_block(self, seq: int) -> str:
        """ Downloads the diff with the given sequence number and returns
            it as a byte sequence. Throws an :code:`requests.HTTPError`
            if the file cannot be downloaded.
        """
        with self.open_url(self.make_request(self.get_diff_url(seq))) as resp:
            if hasattr(resp, 'content'):
                # generated by requests
                resp.raise_for_status()
                return cast(str, resp.content)

            # generated by urllib.request
            return cast(str, resp.read())

    def get_state_url(self, seq: Optional[int]) -> str:
        """ Returns the URL of the state.txt files for a given sequence id.

            If seq is `None` the URL for the latest state info is returned,
            i.e. the state file in the root directory of the replication
            service.
        """
        if seq is None:
            return self.baseurl + '/state.txt'

        return '%s/%03i/%03i/%03i.state.txt' % \
               (self.baseurl, seq / 1000000, (seq % 1000000) / 1000, seq % 1000)

    def get_diff_url(self, seq: int) -> str:
        """ Returns the URL to the diff file for the given sequence id.
        """
        return '%s/%03i/%03i/%03i.%s' % \
               (self.baseurl,
                seq / 1000000, (seq % 1000000) / 1000, seq % 1000,
                self.diff_type)
