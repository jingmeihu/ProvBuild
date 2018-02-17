"""'now merge' command"""
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
    #print(i+1)
    # we use ##### to represent the line of previous script
    # now, 'i+1' is the line
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
        ### ProvScript_trial stores the cleaner version ProvScript
        previous_trial = Trial(trial_ref=previous_trial_id)
        # provscript_trial_id = previous_trial.get_last_runupdate_id()
        # provscript_trial = Trial(trial_ref=provscript_trial_id)

        # print ('You are going to merge')
        # print ('\tTrial {} (original script: {})'.format(previous_trial.id, previous_trial.script)) 
        # print ('\tTrProvScript: {})'.format(provscript_trial.id, provscript_trial.script))
        # print ('\tProvScript: ProvScript.py)')
        # print ('The origin script name is: {}'.format(previous_trial.script))
        # print ('The update script name is: {}'.format(provscript_trial.script))
        origin_file = open(previous_trial.script, "r")
        update_file = open("ProvScript.py", "r")
        new_file_name = 'new-'+previous_trial.script
        # print ('We create a new and complete version for you: {}'.format(new_file_name))
        new_file = open(new_file_name, "w")
        ### line_list stores all the changed line of previous script
        previous_lines = []
        provscript_lines = []
        update_lines = []

        i = 0
        flag = 0
        for line in update_file:
            #print(line[0:24])
            i += 1
            if line[0:24] == '# This is the ProvScript':
                #print(line)
                flag = 1
                continue
            if flag == 1:
                linenumber = check_line_number(line)
                if linenumber != 0:
                    previous_lines.append(linenumber)
                    provscript_lines.append(i)
                else: 
                    update_lines.append(i)
        # print(previous_lines)
        # print(provscript_lines)
        # print(update_lines)

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
        #print(need_update)

        j = 0
        for line in origin_file:
            j = j+1
            if j in previous_lines: # this line has been changed
                # we need to use the update version
                previous_line_index = previous_lines.index(j)
                provscript_line_index = provscript_lines[previous_line_index]
                need_update_res = need_update[previous_line_index]
                #print(need_update_res)
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

        # # function_def
        # ### fitst, we check the function definition table
        # ### ProvScript should contains all the new version
        # ### previous script should keep anything unrelevant the same
        # print ('Step 1: we deal with function definitions')
        # previous_function_def = FunctionDef(trial_ref=previous_trial_id)
        # previous_result_functiondef = previous_function_def.pull_content(previous_trial_id)
        # provscript_function_def = FunctionDef(trial_ref=provscript_trial_id)
        # provscript_result_functiondef = provscript_function_def.pull_content(provscript_trial_id)
        # # print(previous_result_functiondef)
        # # print(provscript_result_functiondef)
        # ### first, we collect all the function names that have been changed in ProvScript
        # changed_func_name = []
        # for p in provscript_result_functiondef:
        # 	changed_func_name.append(p.name)
        # #print(changed_func_name)
        # for p in previous_result_functiondef:
        # 	if p.name in changed_func_name: # if we have changed the function
        # 		for r in provscript_result_functiondef:
        # 			if r.name == p.name:
		      #   		for line in range(r.first_line, r.last_line+1):
		      #   			line_list.append(line)
		      #   			line_script_list.append(2)
        # 	else: # the previous record of this function
        # 		for line in range(p.first_line, p.last_line+1):
        # 			line_list.append(line)
        # 			line_script_list.append(1)
       	# print(line_list)
       	# print(line_script_list)

       	# new_file.write("# This is the Function Definition part\n")
       	# new_file.write("# Function Definition begins\n")
       	# for i in range(0, len(line_list)):
       	# 	if line_script_list[i] == 1:
       	# 		content = linecache.getline(previous_trial.script, line_list[i])
       	# 	else:
       	# 		content = linecache.getline(provscript_trial.script, line_list[i])
       	# 	new_file.write(content)
       	# new_file.write("# Function Definition ends\n\n")
        # print ('Step 1: we have done with function definitions here')

        # print('Step 2: we deal with execution part - ongoing')

        # ### First, the function activation table
        # previous_function_activation = Activation(trial_ref=previous_trial_id)
        # previous_result_functionact = previous_function_activation.pull_content(previous_trial_id)
        # provscript_function_activation = Activation(trial_ref=provscript_trial_id)
        # provscript_result_functionact = provscript_function_activation.pull_content(provscript_trial_id)

        # ### Then, the variable table
        # previous_variable = Variable(trial_ref=previous_trial_id)
        # previous_result_variable = previous_function_activation.pull_content(previous_trial_id)
        # provscript_variable = Variable(trial_ref=provscript_trial_id)
        # provscript_result_variable = provscript_function_activation.pull_content(provscript_trial_id)

        # new_file.write("# This is the Execution part\n")
        # new_file.write("# Execution begins\n")