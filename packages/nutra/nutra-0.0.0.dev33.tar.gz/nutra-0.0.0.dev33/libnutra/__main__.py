# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:02:19 2020

@author: shane

This file is part of nutra, a nutrient analysis program.
    https://github.com/nutratech/cli
    https://pypi.org/project/nutra/

nutra is an extensible nutrient analysis and composition application.
Copyright (C) 2018  Shane Jaroch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import sys

from . import __version__
from .search import search

# Check Python version
if sys.version_info < (3, 6, 5):
    ver = ".".join([str(x) for x in sys.version_info[0:3]])
    print(
        "ERROR: nutra requires Python 3.6.5 or later to run",
        f"HINT:  You're running Python {ver}",
        sep="\n",
    )
    exit(1)


def _search(args, unknown):
    # _args = vars(args)
    # if len(unknown) < 1:
    #     # Print help if no args
    #     search_parser.print_help()
    #     return
    search(words=unknown)


def build_argparser():
    global search_parser

    usage = f"""
    An extensible food database to analyze recipes and aid in fitness.

    %(prog)s [options] <command> [options]
    """

    arg_parser = argparse.ArgumentParser(prog="nutra", usage=usage)

    arg_parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    # --------------------------
    # Sub-command parsers
    # --------------------------
    subparsers = arg_parser.add_subparsers(
        title="nutra subcommands",
        description="valid subcommands",
        help="additional help",
    )

    # Search subcommand
    search_parser = subparsers.add_parser(
        "search", help="use to search foods and recipes"
    )
    search_parser.set_defaults(func=_search)

    # # Login subcommand
    # login_parser = subparsers.add_parser(
    #     "search", help="use to search foods and recipes"
    # )
    # search_parser.set_defaults(func=_search)

    return arg_parser


def main(argv):
    arg_parser = build_argparser()
    # Used for testing
    if not argv:
        argv = ["search"]
    try:
        args, unknown = arg_parser.parse_known_args()
        output = args.func(args, unknown)
        # print(output)
    except Exception as e:
        print("There was an unforseen error: ", e)
        arg_parser.print_help()
