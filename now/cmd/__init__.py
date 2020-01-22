# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""Commands and argument parsers"""
from __future__ import (absolute_import, print_function,
                        division)

import argparse
import sys
import sqlalchemy

from .command import Command, SmartFormatter
from .cmd_run import Run
from .cmd_update import Update
from .cmd_runupdate import RunUpdate
from .cmd_regen import ReGen
from .cmd_merge import Merge
from ..utils.io import print_msg


def main():
    """Main function"""
    from ..utils.functions import version
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=SmartFormatter)
    parser.add_argument("-v", "--version", action="version",
                        version="noWorkflow {}".format(version()))
    subparsers = parser.add_subparsers()
    commands = [
        Run(),
        Update(),
        RunUpdate(),
        ReGen(),
        Merge()
    ]
    for cmd in commands:
        cmd.create_parser(subparsers)

    if len(sys.argv) == 1:
        sys.argv.append("-h")

    try:
        args, _ = parser.parse_known_args()
        args.func(args)
    except RuntimeError as exc:
        print_msg(exc, True)
    except sqlalchemy.exc.OperationalError as exc:
        print_msg("invalid noWorkflow database", True)
        print_msg("it is probably outdated", True)


__all__ = [
    "Command",
    "Run",
    "main",
    "Update",
    "RunUpdate",
    "ReGen",
    "Merge"
]
