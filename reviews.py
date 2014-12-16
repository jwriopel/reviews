# -*- coding: utf-8 -*-
"""
See README.md
"""

import re


FILES_RE = re.compile(r"[-|+]{3}\s+([\w|\W][^\t]*)\s*\S*")
HUNK_RE = re.compile(r"^@@\s([-|\+]\d+,\d+)\s(\+\d+,\d+)\s@@")


class Parser(object):
    """
    Type used for parsing diff files and extracting watchable hunks of files.
    """

    def __init__(self, unified_diff):
        """
        Create an instance of the Parser.

        :param unified_diff: File-like object containing the contents of a
            unified diff.
        """
        self.unified_diff = unified_diff


    def is_header(self, line):
        """ True if the line is a 'header' - meaning file """
        header_markers = ("---", "+++")
        return line[:3] in header_markers

    def extract_filename(self, line):
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


    def __hunk_ints(self, hunk_info):
        """
        Convert the tuple of hunk info from strings to ints

        :param hunk_pair: String containing the raw line information for a
            hunk ("xxx,yyy").
        :return: Tuple containig hunk info as ints (xxx, yyy).
        """
        return tuple(int(i) for i in hunk_info.split(","))


    def hunks(self, lines):
        """
        Parse the hunks from the list of lines, until EOF of another
        file_header.

        :param lines: List of lines to find the hunks from.
        """
        file_hunks = []
        for line in lines:
            if self.is_header(line):
                break
            elif line.startswith("@@"):
                h_res = HUNK_RE.search(line)
                file_hunks.append((
                    self.__hunk_ints(h_res.group(1)),
                    self.__hunk_ints(h_res.group(2))
                ))

        return file_hunks

    def parse(self):
        """
        Parse the unified diff into a dictionary containing the
        watchables.
        """
        lines = [line.strip() for line in self.unified_diff.readlines()]
        watchables = dict()
        for l_no, line in enumerate(lines):

            if self.is_header(line) and line.startswith("--- "):
                file_name = self.extract_filename(line)
                watchables[file_name] = self.hunks(lines[l_no+2:])

                continue

        return watchables
