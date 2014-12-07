# -*- coding: utf-8 -*-
"""
See README.md
"""

import re


FILES_RE = re.compile(r"[-|+]{3}\s+([\w|\W][^\t]*)\s*\S*")


def files(u_diff):
    """
    Parse the files that were modified by changes in this unified diff.

    :param u_diff: File-like object containing the unified diff.
    :return: List of file names that were in the diff.
    """

    f_markers = ("---", "+++")
    f_lines = [line for line in u_diff.readlines() if line[:3] in f_markers]
    diff_files = []

    for f_line in [l.strip() for l in f_lines]:
        search_res = FILES_RE.search(f_line)
        if search_res:
            diff_files.append(search_res.group(1))

    return diff_files
