#!/usr/bin/env python

"""

SourceCred Python is dual-licensed under the MIT License and the Apache-2
License. See LICENSE-MIT and LICENSE-APACHE provided with the code
for the terms of these licenses.

"""

import sourcecred
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(description="SourceCred Python")
    parser.add_argument(
        "--version",
        dest="version",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    description = "actions for SourceCred Python"
    subparsers = parser.add_subparsers(
        help="sourcecred actions",
        title="actions",
        description=description,
        dest="command",
    )

    run = subparsers.add_parser("run", help="run sourcecred *under development*")
    return parser


def main():
    """main is the entrypoint to the sourcecred client.
    """

    parser = get_parser()

    # Will exit with subcommand help if doesn't parse
    args, extra = parser.parse_known_args()

    # Show the version and exit
    if args.version:
        print(sourcecred.__version__)
        sys.exit(0)

    # Run text based simulation
    if args.command == "run":
        print("Run sourcecred")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
