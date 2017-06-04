#!/usr/bin/env python
"""
Parse a diff into a reviews dictionary.
"""
import fileinput
import json
import reviews


def main():
    """ Parse diff from stdin or specified file. """
    print json.dumps(reviews.parse(fileinput.input()), indent=2)


if __name__ == "__main__":
    main()
