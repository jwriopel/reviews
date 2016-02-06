# -*- coding: utf-8 -*-
"""
See README.md

Most programs can use this module by simply calling the `parse` method, which
will return file information from a diff file-like object. This dictionary
contains the changes that can be tracked by reviews, the structure is
{file_name: [hunk_info]} hunk_info is a list  of tuples containing the ranges
of lines that were changed in the file.

"""

import re


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
            watchables[file_name] = hunks(lines[l_no+2:])

    return watchables
