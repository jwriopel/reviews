#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" unit tests for the reviews module """

from StringIO import StringIO
import os
import pytest
import reviews


HEADER_LINES = [
    "--- from_file	2014-12-02 21:16:58.331853527 -0500",
    "+++ to_file	2014-12-02 21:21:43.235849519 -0500"
]


def read_diff(file_name):
    """ read the diff, at `path`, into a file-like object """

    path = os.path.sep.join(
            [os.path.dirname(__file__), "data", file_name])

    with open(path, "r") as s_file:
        return StringIO(s_file.read())


@pytest.fixture
def simple_diff():
    """ this fixture provides a file like object containing the contents of
    tests/data/simple.diff.
    """

    return read_diff("simple_diff")


def test_multiple_files():
    """ test all the expected files appear """

    expected = [
            "a/requests/__init__.py",
            "a/test_requests.py",
            "a/HISTORY.rst",
    ]

    watchables = reviews.parse(read_diff("multi_file_diff"))

    actuals = watchables.keys()
    assert sorted(actuals) == sorted(expected)


@pytest.mark.parametrize("h_line", HEADER_LINES)
def test_is_header(h_line):
    """ test for the Parser.is_header method """
    assert reviews.is_header(h_line)


def compare_watchables(actual, expected):
    """ Assert that the actual watchables are the same as the expected """
    assert len(actual) == len(expected)
    actual_files = actual.keys()
    for exp_file in expected:
        exp_hunk = expected[exp_file]

        assert exp_file in actual_files
        actual_hunk = actual[exp_file]

        assert actual_hunk == exp_hunk


@pytest.mark.parametrize("h_line", HEADER_LINES)
def test_extract_filename(h_line):
    """ test that the filenames from a header is properly parsed """
    file_name = reviews.extract_filename(h_line)

    if h_line.startswith("---"):
        assert file_name == "from_file"
    else:
        assert file_name == "to_file"


def test_parse_hunks(simple_diff):
    """ test the parser can parse the hunks properly """

    expected = [((-2, 9), (+2, 9))]

    lines = [l.strip() for l in simple_diff.readlines()]
    actual_hunks = reviews.hunks(lines[2:])
    assert len(actual_hunks) == len(expected)

    for actual_hunk in actual_hunks:
        assert actual_hunk in expected


def test_build_simple_watchable(simple_diff):
    """ use the Parser to parse out the 'watchable' things  in diff """

    expected = {
            "from_file": [((2, 11))]
    }
    actual = reviews.parse(simple_diff)
    compare_watchables(actual, expected)


def test_multi_file_watchables():
    """
    Test that the watchables are parsed properly, from a diff that contains
    changes from multiple files.
    """

    expected = {
            "a/requests/__init__.py": [(42, 50)],
            "a/HISTORY.rst": [(3, 44)],
            "a/test_requests.py": [
                (258, 265),
                (1008, 1020),
                (1350, 1357),
                (1450, 1457),
                (1534, 1546)
            ]
    }

    actuals = reviews.parse(read_diff("multi_file_diff"))
    assert len(actuals) == len(expected)

    compare_watchables(actuals, expected)


def test_overlaps():
    """Test that changes overlapping with watching ranges are caught."""

    changed_range = (45, 75)
    watched_range = (35, 51)
    expected = True
    actual = reviews.overlaps(changed_range, watched_range)

    assert actual == expected


def test_scan():
    """Test that all ranges being watched are returned by scan."""
    expected = [
        ("a/requests/__init__.py", [[42, 50]]),
        ("a/HISTORY.rst", [[3, 44]]),
        ("a/test_requests.py", [[258, 265]]),
        ("a/test_requests.py", [[1008, 1020]]),
        ("a/test_requests.py", [[1350, 1357]]),
        ("a/test_requests.py", [[1450, 1457]]),
        ("a/test_requests.py", [[1534, 1546]])
    ]
    watching = reviews.parse(read_diff("multi_file_diff"))
    new_changes = reviews.scan(reviews.parse(read_diff("multi_file_diff")),
            watching)
    assert len(expected) == len(new_changes)
