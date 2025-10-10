# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import Optional
import logging
from dataclasses import dataclass
import datetime as dt
from argparse import ArgumentTypeError

from ..replication import newest_change_from_file
from ..replication.server import ReplicationServer
from ..replication.utils import get_replication_header


log = logging.getLogger()


@dataclass
class ReplicationStart:
    """ Represents the point where changeset download should begin.
    """
    date: Optional[dt.datetime] = None
    seq_id: Optional[int] = None
    source: Optional[str] = None

    def get_sequence(self, svr: ReplicationServer) -> Optional[int]:
        if self.seq_id is not None:
            log.debug("Using given sequence ID %d" % self.seq_id)
            if self.seq_id > 0:
                start_state = svr.get_state_info(seq=self.seq_id)
                if start_state is None:
                    log.error(
                        f"Cannot download state information for ID {self.seq_id}."
                        " Server may not have this diff anymore.")
                    return None
                self.date = start_state.timestamp
            return self.seq_id + 1

        assert self.date is not None
        log.debug("Looking up sequence ID for timestamp %s" % self.date)
        return svr.timestamp_to_sequence(self.date, limit_by_oldest_available=True)

    def get_end_sequence(self, svr: ReplicationServer) -> Optional[int]:
        if self.seq_id is not None:
            log.debug("Using end sequence ID %d" % self.seq_id)
            return self.seq_id

        assert self.date is not None
        log.debug("Looking up end sequence ID for timestamp %s" % self.date)
        return svr.timestamp_to_sequence(self.date)

    @staticmethod
    def from_id(idstr: str) -> 'ReplicationStart':
        try:
            seq_id = int(idstr)
        except ValueError:
            raise ArgumentTypeError("Sequence id '%s' is not a number" % idstr)

        if seq_id < -1:
            raise ArgumentTypeError("Sequence id '%s' is negative" % idstr)

        return ReplicationStart(seq_id=seq_id)

    @staticmethod
    def from_date(datestr: str) -> 'ReplicationStart':
        try:
            date = dt.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
            date = date.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            raise ArgumentTypeError(
                "Date needs to be in ISO8601 format (e.g. 2015-12-24T08:08:08Z).")

        return ReplicationStart(date=date)

    @staticmethod
    def from_osm_file(fname: str, ignore_headers: bool) -> 'ReplicationStart':
        if ignore_headers:
            ts = None
            seq = None
            url = None
        else:
            try:
                (url, seq, ts) = get_replication_header(fname)
            except RuntimeError as e:
                raise ArgumentTypeError(e)

        if ts is None and seq is None:
            log.debug("OSM file has no replication headers. Looking for newest OSM object.")
            try:
                ts = newest_change_from_file(fname)
            except RuntimeError as e:
                raise ArgumentTypeError(e)

            if ts is None:
                raise ArgumentTypeError("OSM file does not seem to contain valid data.")

        return ReplicationStart(seq_id=seq, date=ts, source=url)
