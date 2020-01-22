# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""'merge' command"""
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

def check_line_number(content):
    numberofhash = 0
    cont = 0
    for i in range(0, len(content)):
        if(numberofhash == 5):
            break
        if content[i] == '#':
            cont = 1
            numberofhash = numberofhash +1
        else:
            cont = 0
            numberofhash = 0
    # we use ##### to represent the line of previous script
    if i+1 < len(content):
        linenumberstr = content[i+1:]
        linenumber = int(linenumberstr)
        return linenumber
    else:
        return 0

def remove_comment_lineno(content):
    numberofhash = 0
    cont = 0
    for i in range(0, len(content)):
        if(numberofhash == 5):
            break
        if content[i] == '#':
            cont = 1
            numberofhash = numberofhash +1
        else:
            cont = 0
            numberofhash = 0
    ret_content = content[0:i-5] + '\n'
    return ret_content



class Merge(Command):
    """ Merge ProvScript into the previous script based on the user input (trial id) """

    def __init__(self, *args, **kwargs):
        super(Merge, self).__init__(*args, **kwargs)

    def add_arguments(self):
        add_arg = self.add_argument

        add_arg("-t", "--trial", type=non_negative,
                help="get the previous trial id")

    def execute(self, args):
        persistence_config.connect_existing(os.getcwd())
        previous_trial_id = args.trial

        ### check for the most recent runupdate trial id
        ### previous_trial stores the previous script trial
        previous_trial = Trial(trial_ref=previous_trial_id)
        origin_file = open(previous_trial.script, "r")
        update_file = open("ProvScript.py", "r")
        new_file_name = 'new-'+previous_trial.script
        new_file = open(new_file_name, "w")
        previous_lines = []
        provscript_lines = []
        update_lines = []

        i = 0
        before_script_flag = 0
        useless_thing_flag = 0
        for line in update_file:
            i += 1
            if '# This is the ProvScript part' in line:
                before_script_flag = 1
                continue
            if before_script_flag == 1:
                linenumber = check_line_number(line)
                if linenumber != 0:
                    previous_lines.append(linenumber)
                    provscript_lines.append(i)
                else: 
                    if '# The previous script does something here, but we ignore them here' in line:
                        useless_thing_flag = 1
                    elif '# Please check the previous script' in line:
                        useless_thing_flag = 0
                    elif useless_thing_flag == 0:
                        update_lines.append(i)

        cnt = 0
        need_update = [0] * len(provscript_lines)
        for cnt in range(0, len(update_lines)):
            flag = 0
            for idx in range(0, len(provscript_lines)):
                if flag == 1: # already find the closest
                    break
                if(update_lines[cnt] < provscript_lines[idx]):
                    need_update[idx] = need_update[idx] + 1
                    flag = 1

        j = 0
        for line in origin_file:
            j = j+1
            if j in previous_lines: # this line has been changed
                # we need to use the update version
                previous_line_index = previous_lines.index(j)
                provscript_line_index = provscript_lines[previous_line_index]
                need_update_res = need_update[previous_line_index]
                if need_update_res != 0: # the user add something before this line
                    for n in range(0, need_update_res):
                        ln = update_lines[0]
                        content = linecache.getline('ProvScript.py', ln)
                        new_file.write(content)
                        # we've added this line, remove it from the list
                        update_lines.remove(ln)
                # add the ProvScript version
                content = linecache.getline('ProvScript.py', provscript_line_index)
                new_content = remove_comment_lineno(content)
                new_file.write(new_content)
            else:
                content = linecache.getline(previous_trial.script, j)
                new_file.write(content)

        new_file.close()
