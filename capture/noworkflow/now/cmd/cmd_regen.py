"""'now regen' command"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

import argparse
import os
import sys

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

import linecache

def non_negative(string):
    """Check if argument is >= 0"""
    value = int(string)
    if value < 0:
        raise argparse.ArgumentTypeError(
            "{} is not a non-negative integer value".format(string))
    return value

class ReGen(Command):
    """ Regenerate ProvScript with a particular function definition. """

    def __init__(self, *args, **kwargs):
        super(ReGen, self).__init__(*args, **kwargs)

    def add_arguments(self):
        add_arg = self.add_argument

        add_arg("-t", "--trial", type=non_negative,
                help="get the previous trial id")
        add_arg("-f", "--funcname", type=str, default=None,
                help="undefined function")

    def execute(self, args):
        persistence_config.connect_existing(os.getcwd())
        more_func_name = args.funcname
        print("undefined function name: " + more_func_name)

        trial = Trial(trial_ref=args.trial)
        function_def = FunctionDef(trial_ref=args.trial)
        if function_def is not None:
            result_functiondef = function_def.pull_content(trial.id)

        line_list = []
        flag = 0
        if more_func_name is not None:
        	for i in result_functiondef:
        		if i.name == more_func_name:
                                flag = 1
        			for line in range(i.first_line, i.last_line + 1):
        				if line not in line_list:
        					line_list.append(line)
        if flag == 0:
            print("UNFOUND")

        origin_file = open(trial.script, "r")
        prov_file = open("ProvScript.py", "r")
        prov_filelines = prov_file.readlines()

        update_file = open("ProvScript.py", "w")

        for line in prov_filelines:
            if '# This is the ProvScript part' in line:
            	update_file.write(line)
            	for i in line_list:
	        		content = linecache.getline(trial.script, i)
	        		content_comment = content.rstrip() + ' #####L' + str(i) + '\n'
	        		update_file.write(content_comment)
            else:
            	update_file.write(line)

        update_file.close()