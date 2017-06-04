#!/usr/bin/env python
"""
Check if there are changes in a diff that are being watched by
a reviewer.
"""

import argparse
import fileinput
import json
import reviews


def main():
    """ Read `diff` from stdin and compare the changes against the reviews
    data in `rfile`.
    """
    parser = argparse.ArgumentParser(
        description="Print files that contain watched changes.")

    parser.add_argument(
        "rfile",
        help="Path to reviews file.",
        type=str
    )

    args = parser.parse_args()
    with open(args.rfile, "r") as wfile:
        watching = json.load(wfile)

    changes = reviews.parse(fileinput.input(files=('-', )))
    print reviews.scan(changes, watching)

if __name__ == "__main__":
    main()

