"""'runupdate' command"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import argparse
import os
import sys

from ..collection.metadata import Metascript
from ..persistence.models import Tag, Trial
from ..utils import io, metaprofiler
from ..utils.cross_version import PY3

from .command import Command


class ScriptArgs(argparse.Action):                                               # pylint: disable=too-few-public-methods
    """Action to create script attribute"""
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            raise argparse.ArgumentError(
                self, "can't be empty")

        script = os.path.realpath(values[0])

        if not os.path.exists(script):
            raise argparse.ArgumentError(
                self, "can't open file '{}': "
                "[Errno 2] No such file or directory".format(values[0]))

        setattr(namespace, self.dest, script)
        setattr(namespace, "argv", values)


def run(metascript):
    """Execute noWokflow to capture provenance from script"""
    try:
        metascript.trial_id = Trial.store(*metascript.create_trial_args(args="runupdate"))
        Tag.create_automatic_tag(*metascript.create_automatic_tag_args())

        # io.print_msg("collecting definition provenance")
        # metascript.definition.collect_provenance()
        # metascript.definition.store_provenance()

        # io.print_msg("collecting deployment provenance")
        # metascript.deployment.collect_provenance()
        # metascript.deployment.store_provenance()

        io.print_msg("collection execution provenance")
        metascript.execution.collect_provenance()
        metascript.execution.store_provenance()

        metaprofiler.meta_profiler.save()

    finally:
        metascript.create_last()

class RunUpdate(Command):
    """Run ProvScript and collect its provenance"""

    def __init__(self, *args, **kwargs):
        super(RunUpdate, self).__init__(*args, **kwargs)
        self.context = "main"
        self.call_storage_frequency = 10000
        self.save_frequency = 0
        self.execution_provenance = "Tracer"
        self.depth = sys.getrecursionlimit()
        self.non_user_depth = 1
        self.verbose = True

        self.add_help = False

    def add_arguments(self):
        add_arg = self.add_argument
        add_cmd = self.add_argument_cmd

        # It will create both script and argv var
        add_cmd("script", nargs=argparse.REMAINDER, action=ScriptArgs,
                help="Python script to be executed")

        add_arg("-h", "--help", action="help",
                help="show this help message and exit")
        add_arg("--dir", type=str,
                help="set project path. The noworkflow database folder will "
                     "be created in this path. Default to script directory")
        # add_arg("-v", "--verbose", action="store_true",
        #         help="increase output verbosity")

    def execute(self, args):
    	io.verbose = True # instead of using 'args.verbose', we always enable verbose
        io.print_msg("removing noWorkflow boilerplate")

        # script_name = 'ProvScript.py'
        # script = os.path.realpath(script_name)
        # # Create Metascript with params
        # metascript = Metascript().read_cmd_args_runupdate(script_name, script)

        # Create Metascript with params
        metascript = Metascript().read_cmd_args_runupdate(args)

        # Set __main__ namespace
        import __main__
        metascript.namespace = __main__.__dict__

        # Clear boilerplate
        metascript.clear_sys()
        metascript.clear_namespace()

        # Run script
        run(metascript)


