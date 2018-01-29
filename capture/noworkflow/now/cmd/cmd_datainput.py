"""'now datainput' command"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import os
import sys
import argparse
from future.utils import viewitems

from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy import ForeignKeyConstraint, select, func, distinct
from ..persistence import relational, content, persistence_config

from ..persistence.models.base import AlchemyProxy, proxy_class, query_many_property, proxy_gen
from ..persistence.models.base import one, many_ref, many_viewonly_ref, backref_many, is_none
from ..persistence.models.base import proxy


from ..utils import io, metaprofiler
from ..collection.metadata import Metascript
from ..persistence.models import Tag, Trial, FunctionDef, Module, Dependency, FileAccess, EnvironmentAttr, Object, Activation, ObjectValue, Variable, VariableDependency, VariableUsage
from ..persistence import persistence_config, content
from ..utils.io import print_msg
from .command import Command


def non_negative(string):
    """Check if argument is >= 0"""
    value = int(string)
    if value < 0:
        raise argparse.ArgumentTypeError(
            "{} is not a non-negative integer value".format(string))
    return value

class DataInput(Command):
    """ Create ProvScript based on the user input """

    def __init__(self, *args, **kwargs):
        super(DataInput, self).__init__(*args, **kwargs)

    def add_arguments(self):
        add_arg = self.add_argument

        add_arg("--dir", type=str,
                help="set project path where is the database. Default to "
                     "current directory")
        add_arg("-t", "--trial", type=non_negative,
                help="get the previous trial id")
        add_arg("-pd", "--previous_data", type=str,
                help="previous data input, you might want to replace it by new input")
        add_arg("-ud", "--update_data", type=str,
                help="new data input, you might want to use it to replace the previous one")
    def execute(self, args):
        persistence_config.connect_existing(args.dir or os.getcwd())
        metascript = Metascript().read_restore_args(args)
        self.trial = trial = metascript.trial = Trial(trial_ref=args.trial)
        metascript.trial_id = trial.id
        metascript.name = trial.script
        metascript.fake_path(trial.script, "")
        metascript.paths[trial.script].code_hash = None

        metascript.trial_id = Trial.store(
            *metascript.create_trial_args(
                args="<datainput {}>".format(metascript.trial_id), run=False
            )
        )

        print ('Before we start, let me be clear:')
        print ('You are dealing with Trial {} '.format(args.trial))
        print ('You are going to replace {} with {}'.format(args.previous_data, args.update_data))

        # for trial table
        result_trial = trial.pull_content(trial.id)
        metascript.trial.push_content(metascript.trial_id, result_trial)
        trial_table = trial.__table__
        print ('Step 1.1: we have done with {} table'.format(trial_table))


