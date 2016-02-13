# -*- coding: utf-8 -*-
"""
Use this module to parse data from a unified diff so that the changes can be
saved and tracked.

The parse function should be enough to extract the information needed to track
a change. It will return a dictionary with each file being the key and the
value is a list of tuples. Each tuple contains the start line of the change and
the end line of the change.
"""

import re

REVIEWS_CONFIG = {"conf": "~/.reviews"}

FILES_RE = re.compile(r"[-|+]{3}\s+([\w|\W][^\t]*)\s*\S*")
HUNK_RE = re.compile(r"^@@\s([-|\+]\d+,\d+)\s(\+\d+,\d+)\s@@")

def is_header(line):
    """ True if the line is a 'header' - meaning file """
    header_markers = ("---", "+++")
    return line[:3] in header_markers


def extract_filename(line):
    """
    extract the file name from the header line.

    :param line: A header line from the diff.
    :return: String containing the file name.
    """
    search_res = FILES_RE.search(line)
    f_name = None

    if search_res:
        f_name = search_res.group(1)

    return f_name


def hunks(lines):
    """
    Parse the hunks from the list of lines, until EOF of another
    file_header.

    :param lines: List of lines to find the hunks from.
    """
    h_ints = lambda hinfo: tuple(int(i) for i in hinfo.split(","))

    file_hunks = []
    for line in lines:
        if is_header(line):
            break
        elif line.startswith("@@"):
            h_res = HUNK_RE.search(line)
            file_hunks.append((
                h_ints(h_res.group(1)),
                h_ints(h_res.group(2))
            ))

    return file_hunks


def parse(unified_diff):
    """
    Parse the unified diff into a dictionary containing the watchable file
    information.

    :param unified_diff: File-like object containing the unified_diff.
    """
    lines = [line.strip() for line in unified_diff.readlines()]
    watchables = dict()
    for l_no, line in enumerate(lines):

        if is_header(line) and line.startswith("--- "):

            file_name = extract_filename(line)
            changed_lines = watchables.get(file_name, [])
            # the hunk will be two tuples, the `to` and `from` ranges
            # for this chunk
            for _, t_info in hunks(lines[l_no+2:]):
                changed_lines.append((t_info[0], t_info[0] + t_info[1]))

            watchables[file_name] = changed_lines

    return watchables


def overlaps(changed_range, watched_range):
    """Return True if there were changes made to lines within the watched
    range."""

    changed_start, changed_end = changed_range
    watched_start, watched_end = watched_range

    overlap = False
    if (changed_start >= watched_start and changed_start <= watched_end) or \
            ((changed_end >= watched_start) and (changed_end <= watched_end)):
        overlap = True

    return overlap


def scan(diff, watching):
    """Find and changes in `diff` that are being watched.

    :param diff: File-like object containing the diff to be scanned.
    :param wathcing: Dictionary containing the hunks that are being watched.

    :return: List of tuples containing watched files and ranges modified in
        the diff, each tuple has form: (filename, (range start, range end)).
    """

    to_diff = parse(diff)
    watched_files = [tf for tf in to_diff.keys() if tf in watching]

    reviews_needed = []
    for watched_file in watched_files:
        to_ranges = to_diff[watched_file]
        watched_ranges = watching[watched_file]

        for to_range in to_ranges:
            for watched_range in watched_ranges:
                if overlaps(to_range, watched_range):
                    reviews_needed.append((watched_file, watched_range))

    return reviews_needed
