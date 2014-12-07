#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" unit tests for the reviews module """

from StringIO import StringIO
import os
import pytest
import reviews


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


def test_single_file(simple_diff):
    """ test the the files can be parsed and returned correctly """

    expected = ["from_file", "to_file"]
    actuals = reviews.files(simple_diff)

    assert len(actuals) == len(expected)
    for actual in actuals:
        assert actual in expected


def test_multiple_files():
    """ test all the expected files appear """

    expected = [
            "a/requests/__init__.py",
            "b/requests/__init__.py",
            "a/test_requests.py",
            "b/test_requests.py",
            "a/HISTORY.rst",
            "b/HISTORY.rst"
    ]
    
    actuals = sorted(reviews.files(read_diff("multi_file_diff")))

    assert actuals == sorted(expected)


