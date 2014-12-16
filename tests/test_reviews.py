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

    parser = reviews.Parser(read_diff("multi_file_diff"))
    watchables = parser.parse()

    actuals = watchables.keys()
    assert sorted(actuals) == sorted(expected)


@pytest.mark.parametrize("h_line", HEADER_LINES)
def test_is_header(h_line):
    """ test for the Parser.is_header method """
    parser = reviews.Parser(None)
    assert parser.is_header(h_line)


def compare_watchables(actual, expected):
    """ Assert that the actual watchables are the same as the expected """
    actual_files = actual.keys()
    for exp_file in expected:
        exp_hunk = expected[exp_file]

        assert exp_file in actual_files
        actual_hunk = actual[exp_file]

        assert actual_hunk == exp_hunk


@pytest.mark.parametrize("h_line", HEADER_LINES)
def test_extract_filename(h_line):
    """ test that the filenames from a header is properly parsed """
    parser = reviews.Parser(simple_diff)
    file_name = parser.extract_filename(h_line)

    if h_line.startswith("---"):
        assert file_name == "from_file"
    else:
        assert file_name == "to_file"


def test_parse_hunks(simple_diff):
    """ test the parser can parse the hunks properly """

    expected = [((-2, 9), (+2, 9))]
    parser = reviews.Parser(None)

    lines = [l.strip() for l in simple_diff.readlines()]
    actual_hunks = parser.hunks(lines[2:])
    assert len(actual_hunks) == len(expected)

    for actual_hunk in actual_hunks:
        assert actual_hunk in expected


def test_build_simple_watchable(simple_diff):
    """ use the Parser to parse out the 'watchable' things  in diff """

    parser = reviews.Parser(simple_diff)
    expected = {
            "from_file": [((-2, 9), (+2, 9))]
    }
    actual = parser.parse()
    compare_watchables(actual, expected)


def test_multi_file_watchables():
    """
    Test that the watchables are parsed properly, from a diff that contains
    changes from multiple files.
    """

    expected = {
            "a/requests/__init__.py": [((-42, 8), (+42, 8))],
            "a/HISTORY.rst": [((-3, 6), (+3, 41))],
            "a/test_requests.py": [
                ((-258, 7), (258, 7)),
                ((-1008, 12), (1008, 12)),
                ((-1350, 7), (1350, 7)),
                ((-1450, 7), (1450, 7)),
                ((-1534, 12), (1534, 12))
            ]
    }

    parser = reviews.Parser(read_diff("multi_file_diff"))
    actuals = parser.parse()

    assert len(actuals) == len(expected)

    compare_watchables(actuals, expected)
