# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
"""
Update an OSM file with changes from a OSM replication server.

Diffs are downloaded and kept in memory. To avoid running out of memory,
the maximum size of diffs that can be downloaded at once is limited
to 1 GB per default. This corresponds to approximately 3 days of update.
The limit can be changed with the --size parameter. However, you should
take into account that processing the files requires additional memory
(about 1GB more).

The starting time is automatically determined from the data in the file.
For PBF files, it is also possible to read and write the replication
information from the osmosis headers. That means that after the first update,
subsequent calls to pyosmium-up-to-date will continue the updates from the same
server exactly where they have left of.

This program can update normal OSM data files as well as OSM history files.
It detects automatically on what type of file it is called.

The program returns 0, if updates have been successfully applied up to
the newest data or no new data was available. It returns 1, if some updates
have been applied but there is still data available on the server (either
because the size limit has been reached or there was a network error which
could not be resolved). Any other error results in a return code larger than 1.
The output file is guaranteed to be unmodified in that case.

Some OSM data sources require a cookie to be sent with the HTTP requests.
pyosmium-up-to-date does not fetch the cookie from these services for you.
However, it can read cookies from a Netscape-style cookie jar file, send these
cookies to the server and will save received cookies to the jar file.
"""
from typing import Any, List
import sys
import traceback
import logging
import http.cookiejar

from argparse import ArgumentParser, RawDescriptionHelpFormatter, ArgumentTypeError
import datetime as dt
from textwrap import dedent as msgfmt
from tempfile import mktemp
import os.path

from ..replication import server as rserv
from ..version import pyosmium_release
from .common import ReplicationStart

log = logging.getLogger()


def update_from_osm_server(start: ReplicationStart, options: Any) -> int:
    """ Update the OSM file using the official OSM servers at
        https://planet.osm.org/replication. This strategy will attempt
        to start with daily updates before going down to minutelies.
        TODO: only updates from hourlies currently implemented.
    """
    start.source = "https://planet.osm.org/replication/hour/"
    return update_from_custom_server(start, options)


def update_from_custom_server(start: ReplicationStart, options: Any) -> int:
    """ Update from a custom URL, simply using the diff sequence as is.
    """
    assert start.source

    with rserv.ReplicationServer(start.source, options.server_diff_type) as svr:
        log.info(f"Using replication service at {start.source}")

        svr.set_request_parameter('timeout', options.socket_timeout or None)

        if options.cookie is not None:
            cookie_jar = http.cookiejar.MozillaCookieJar(options.cookie)
            cookie_jar.load(options.cookie)
            svr.set_request_parameter('cookies', cookie_jar)

        current = svr.get_state_info()
        if current is None:
            log.error("Cannot download state information. Is the replication URL correct?")
            return 3
        log.debug(f"Server is at sequence {current.sequence} ({current.timestamp}).")

        if start.seq_id is not None and start.seq_id >= current.sequence:
            log.info("File is already up to date.")
            return 0

        startseq = start.get_sequence(svr)
        if startseq is None:
            log.error(f"No starting point found for time {start.date} on server {start.source}")
            return 3

        if not options.force_update:
            cmpdate = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)
            cmpdate = cmpdate.replace(tzinfo=dt.timezone.utc)
            if start.date is None or start.date < cmpdate:
                log.error(
                  """The OSM file is more than 3 months old. You should download a
                     more recent file instead of updating. If you really want to
                     update the file, use --force-update-of-old-planet.""")
                return 3

        log.info("Starting download at ID %d (max %f MB)"
                 % (startseq, options.outsize or float('inf')))

        outfile = options.outfile
        infile = options.infile

        if outfile is None:
            fdir, fname = os.path.split(infile)
            if options.tmpdir is not None:
                fdir = options.tmpdir
            ofname = mktemp(suffix='-' + fname, dir=fdir)
        else:
            ofname = outfile

        if options.outsize is not None:
            max_size = options.outsize * 1024
        elif options.end is None:
            max_size = 1024 * 1024
        else:
            max_size = None

        if options.end is None:
            end_id = None
        else:
            end_id = options.end.get_end_sequence(svr)
            if end_id is None:
                log.error("Cannot find the end date/ID on the server.")
                return 1

        try:
            extra_headers = {'generator': 'pyosmium-up-to-date/' + pyosmium_release}
            outseqs = svr.apply_diffs_to_file(infile, ofname, startseq,
                                              max_size=max_size, end_id=end_id,
                                              extra_headers=extra_headers,
                                              outformat=options.outformat)

            if outseqs is None:
                log.info("No new updates found.")
                return 3

            if outfile is None:
                os.replace(ofname, infile)
        finally:
            if outfile is None:
                try:
                    os.remove(ofname)
                except FileNotFoundError:
                    pass

    log.info("Downloaded until %d. Server has data available until %d." % outseqs)

    # save cookies
    if options.cookie:
        cookie_jar.save(options.cookie)

    return 0 if (end_id or outseqs[1]) == outseqs[0] else 1


def compute_start_point(options: Any) -> ReplicationStart:
    start = ReplicationStart.from_osm_file(options.infile, options.ignore_headers)

    if options.server_url is not None:
        if start.source is not None and start.source != options.server_url:
            log.error(msgfmt(f"""
                  You asked to use server URL:
                    {options.server_url}
                  but the referenced OSM file points to replication server:
                    {start.source}
                  If you really mean to overwrite the URL, use --ignore-osmosis-headers."""))
            raise ArgumentTypeError("Source URL doesn't match replication headers.")
        if start.source is None:
            start.source = options.server_url
            start.seq_id = None
            if start.date is None:
                raise ArgumentTypeError("Cannot determine start date for file.")

    if start.seq_id is None:
        assert start.date is not None
        start.date -= dt.timedelta(minutes=options.wind_back)

    return start


def get_arg_parser(from_main: bool = False) -> ArgumentParser:

    parser = ArgumentParser(prog='pyosmium-up-to-date',
                            description=__doc__,
                            usage=None if from_main else 'pyosmium-up-to-date [options] <osm file>',
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-v', dest='loglevel', action='count', default=0,
                        help='Increase verbosity (can be used multiple times).')
    parser.add_argument('infile', metavar='<osm file>', help="OSM file to update")
    parser.add_argument('-o', '--outfile', dest='outfile',
                        help='Name output of file. If missing, the input file '
                             'will be overwritten.')
    parser.add_argument('--format', dest='outformat', metavar='FORMAT',
                        help='Format the data should be saved in. '
                             'Usually determined from file name.')
    parser.add_argument('--server', action='store', dest='server_url',
                        help='Base URL of the replication server. Default: '
                             'https://planet.osm.org/replication/hour/ '
                             '(hourly diffs from osm.org)')
    parser.add_argument('--diff-type', action='store', dest='server_diff_type', default='osc.gz',
                        help='File format used by the replication server (default: osc.gz)')
    parser.add_argument('-s', '--size', dest='outsize', metavar='SIZE', type=int,
                        help='Maximum size of change to apply at once in MB. '
                             'Defaults to 1GB when no end ID or date was given.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--end-id', dest='end',
                       type=ReplicationStart.from_id, metavar='ID',
                       help='Last sequence ID to download.')
    group.add_argument('-E', '--end-date', dest='end', metavar='DATE',
                       type=ReplicationStart.from_date,
                       help='Do not download diffs later than the given date.')
    parser.add_argument('--tmpdir', dest='tmpdir',
                        help='Directory to use for temporary files. '
                             'Usually the directory of input file is used.')
    parser.add_argument('--ignore-osmosis-headers', dest='ignore_headers',
                        action='store_true',
                        help='Ignore potential replication information in the '
                             'header of the input file and search for the '
                             'newest OSM object in the file instead.')
    parser.add_argument('-b', '--wind-back', dest='wind_back', type=int, default=60,
                        help='Number of minutes to start downloading before '
                             'the newest addition to input data. (Ignored when '
                             'the file contains a sequence ID.) Default: 60')
    parser.add_argument('--force-update-of-old-planet', action='store_true',
                        dest='force_update',
                        help="Apply update even if the input data is really old.")
    parser.add_argument('--cookie', dest='cookie',
                        help='Netscape-style cookie jar file to read cookies from and where '
                             'received cookies will be written to.')
    parser.add_argument('--socket-timeout', dest='socket_timeout', type=int, default=60,
                        help='Set timeout for file downloads.')
    parser.add_argument('--version', action='version',
                        version='pyosmium ' + pyosmium_release)

    return parser


def pyosmium_up_to_date(args: List[str]) -> int:
    options = get_arg_parser(from_main=True).parse_args(args)
    log.setLevel(max(3 - options.loglevel, 0) * 10)

    try:
        start = compute_start_point(options)
    except RuntimeError as e:
        log.error(str(e))
        return 2

    try:
        if start.source is None:
            return update_from_osm_server(start, options)

        return update_from_custom_server(start, options)
    except Exception:
        traceback.print_exc()

    return 254


def main() -> int:
    logging.basicConfig(stream=sys.stderr,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    return pyosmium_up_to_date(sys.argv[1:])
