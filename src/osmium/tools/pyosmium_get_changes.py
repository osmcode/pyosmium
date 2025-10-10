# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
"""
Fetch diffs from an OSM planet server.

The starting point of the diff must be given either as a sequence ID or a date
or can be computed from an OSM file. If no output file is given, the program
will just print the initial sequence ID it would use (or save it in a file, if
requested) and exit. This can be used to bootstrap the update process.

The program tries to download until the latest change on the server is found
or the maximum requested diff size is reached. Note that diffs are kept in
memory during download.

On success, the program will print a single number to stdout, the sequence
number where to continue updates in the next run. This output can also be
written to (and later read from) a file.

*Note:* you may pipe the diff also to standard output using '-o -'. Then
the sequence number will not be printed. You must write it to a file in that
case.

Some OSM data sources require a cookie to be sent with the HTTP requests.
pyosmium-get-changes does not fetch the cookie from these services for you.
However, it can read cookies from a Netscape-style cookie jar file, send these
cookies to the server and will save received cookies to the jar file.
"""
from typing import List
import sys
import logging
from textwrap import dedent as msgfmt
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import http.cookiejar

from ..replication import server as rserv
from ..version import pyosmium_release
from .. import SimpleWriter
from .common import ReplicationStart


log = logging.getLogger()


def write_end_sequence(fname: str, seqid: int) -> None:
    """Either writes out the sequence file or prints the sequence id to stdout.
    """
    if fname is None:
        print(seqid)
    else:
        with open(fname, 'w') as fd:
            fd.write(str(seqid))


def get_arg_parser(from_main: bool = False) -> ArgumentParser:
    parser = ArgumentParser(prog='pyosmium-get-changes',
                            description=__doc__,
                            usage=None if from_main else 'pyosmium-get-changes [options]',
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-v', dest='loglevel', action='count', default=0,
                        help='Increase verbosity (can be used multiple times)')
    parser.add_argument('-o', '--outfile', dest='outfile',
                        help='Name of diff output file. If omitted, only the '
                             'sequence ID will be printed where updates would start.')
    parser.add_argument('--format', dest='outformat', metavar='FORMAT',
                        help="Format the data should be saved in.")
    parser.add_argument('--server', action='store', dest='server_url',
                        help='Base URL of the replication server')
    parser.add_argument('--diff-type', action='store', dest='server_diff_type', default='osc.gz',
                        help='File format used by the replication server (default: osc.gz)')
    parser.add_argument('--cookie', dest='cookie',
                        help='Netscape-style cookie jar file to read cookies from '
                             'and where received cookies will be written to.')
    parser.add_argument('-s', '--size', dest='outsize', type=int,
                        help='Maximum data to load in MB '
                             '(Defaults to 100MB when no end date/ID has been set).')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-I', '--start-id', dest='start',
                       type=ReplicationStart.from_id, metavar='ID',
                       help='Sequence ID to start with')
    group.add_argument('-D', '--start-date', dest='start', metavar='DATE',
                       type=ReplicationStart.from_date,
                       help='Date when to start updates')
    group.add_argument('-O', '--start-osm-data', dest='start_file', metavar='OSMFILE',
                       help='start at the date of the newest OSM object in the file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--end-id', dest='end',
                       type=ReplicationStart.from_id, metavar='ID',
                       help='Last sequence ID to download.')
    group.add_argument('-E', '--end-date', dest='end', metavar='DATE',
                       type=ReplicationStart.from_date,
                       help='Do not download diffs later than the given date.')
    parser.add_argument('-f', '--sequence-file', dest='seq_file',
                        help='Sequence file. If the file exists, then updates '
                             'will start after the id given in the file. At the '
                             'end of the process, the last sequence ID contained '
                             'in the diff is written.')
    parser.add_argument('--ignore-osmosis-headers', dest='ignore_headers',
                        action='store_true',
                        help='When determining the start from an OSM file, '
                             'ignore potential replication information in the '
                             'header and search for the newest OSM object.')
    parser.add_argument('-d', '--no-deduplicate', action='store_false', dest='simplify',
                        help='Do not deduplicate diffs.')
    parser.add_argument('--socket-timeout', dest='socket_timeout', type=int, default=60,
                        help='Set timeout for file downloads.')
    parser.add_argument('--version', action='version', version='pyosmium ' + pyosmium_release)

    return parser


def pyosmium_get_changes(args: List[str]) -> int:
    logging.basicConfig(stream=sys.stderr,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    options = get_arg_parser(from_main=True).parse_args(args)

    log.setLevel(max(3 - options.loglevel, 0) * 10)

    if options.outfile == '-' and options.outformat is None:
        log.error("You must define a format when using stdout. See --format.")
        return 1

    if options.start_file is not None:
        options.start = ReplicationStart.from_osm_file(options.start_file,
                                                       options.ignore_headers)
    if options.start is None:
        if options.seq_file is None:
            log.error(msgfmt("""
              Don't know with which change to start. One of the parameters
                -I / -D / -O / -f
              needs to be given."""))
            return 1

        with open(options.seq_file, 'r') as f:
            seq = f.readline()
            options.start = ReplicationStart.from_id(seq)

    if options.server_url is not None and options.start.source is not None:
        if options.server_url != options.start.source:
            log.error(msgfmt(f"""
                You asked to use server URL:
                  {options.server_url}
                but the referenced OSM file points to replication server:
                  {options.start.source}
                If you really mean to overwrite the URL, use --ignore-osmosis-headers."""))
            return 2
    url = options.server_url \
        or options.start.source \
        or 'https://planet.osm.org/replication/minute/'
    logging.info("Using replication server at %s" % url)

    with rserv.ReplicationServer(url, diff_type=options.server_diff_type) as svr:
        svr.set_request_parameter('timeout', options.socket_timeout or None)

        if options.cookie is not None:
            cookie_jar = http.cookiejar.MozillaCookieJar(options.cookie)
            cookie_jar.load(options.cookie)
            svr.set_request_parameter('cookies', cookie_jar)

        # Sanity check if server URL is correct and server is responding.
        current = svr.get_state_info()
        if current is None:
            log.error("Cannot download state information. Is the replication URL correct?")
            return 3
        log.debug(f"Server is at sequence {current.sequence} ({current.timestamp}).")

        startseq = options.start.get_sequence(svr)
        if startseq is None:
            log.error(f"No starting point found for time {options.start.date} on server {url}")
            return 1

        if options.outfile is None:
            write_end_sequence(options.seq_file, startseq - 1)
            return 0

        log.debug("Starting download at ID %d (max %f MB)"
                  % (startseq, options.outsize or float('inf')))
        if options.outformat is not None:
            outhandler = SimpleWriter(options.outfile, filetype=options.outformat)
        else:
            outhandler = SimpleWriter(options.outfile)

        if options.outsize is not None:
            max_size = options.outsize * 1024
        elif options.end is None:
            max_size = 100 * 1024
        else:
            max_size = None

        if options.end is None:
            end_id = None
        else:
            end_id = options.end.get_end_sequence(svr)
            if end_id is None:
                log.error("Cannot find the end date/ID on the server.")
                return 1

        endseq = svr.apply_diffs(outhandler, startseq, max_size=max_size,
                                 end_id=end_id, simplify=options.simplify)
        outhandler.close()

    # save cookies
    if options.cookie:
        cookie_jar.save(options.cookie)

    if endseq is None:
        log.error("Error while downloading diffs.")
        return 3

    if options.outfile != '-' or options.seq_file is not None:
        write_end_sequence(options.seq_file, endseq)

    return 0


def main() -> int:
    logging.basicConfig(stream=sys.stderr,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    return pyosmium_get_changes(sys.argv[1:])
