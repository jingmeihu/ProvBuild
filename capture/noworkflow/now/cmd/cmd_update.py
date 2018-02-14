"""'now update' command"""
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

import linecache

def debug_print(string, content, arg=True):
    if arg == True:
        print('{} is {}'.format(string, content))
    return

def non_negative(string):
    """Check if argument is >= 0"""
    value = int(string)
    if value < 0:
        raise argparse.ArgumentTypeError(
            "{} is not a non-negative integer value".format(string))
    return value

def get_closest_graybox(fileid, result_variable):
    res = -1
    for i in range(fileid-1, 0, -1):
        if result_variable[i].name == '--graybox--':
            res = i;
            break;
    return (res+1) ### actual variable id needs +1

def get_same_line_call(line, result_variable):
    res = []
    for r in result_variable:
        if r.line == line and r.type == 'call' and r.id not in res:
            res.append(r.id)
    return res
    
# check if content contains if(return 1), elif(return 2), else(return 3)
def check_cond(line, result_functiondef):
    res = []
    for i in result_functiondef:
        if line not in res and line >= i.first_line and line <= i.last_line:
            for j in range(i.first_line, i.last_line+1):
                res.append(j)
    return res
    
# given current line, check its function definition ID (or cond ID or loop ID)
def check_def_id(line, result_functiondef):
    for i in result_functiondef:
        if line >= i.first_line and line <= i.last_line:
            return i.id
    return 0
    
def find_active_id(name, line, result_functionactivation):
    for r in result_functionactivation:
        if r.line == line and r.name == name:
            return r.id
    return 0

class Update(Command):
    """ Create ProvScript based on the user input """

    def __init__(self, *args, **kwargs):
        super(Update, self).__init__(*args, **kwargs)

    def add_arguments(self):
        add_arg = self.add_argument

        add_arg("--dir", type=str,
                help="set project path where is the database. Default to "
                     "current directory")
        add_arg("-t", "--trial", type=non_negative,
                help="get the previous trial id")
        add_arg("-fn", "--funcname", type=str,
                help="function name input")
        add_arg("-vn", "--varname", type=str,
                help="variable name input")
        add_arg("--debug", type = int, default=1, help="enable debug")

    def execute(self, args):
        # first, we need to restore the metascript based on trial id
        persistence_config.connect_existing(args.dir or os.getcwd())
        metascript = Metascript().read_restore_args(args)
        self.trial = trial = metascript.trial = Trial(trial_ref=args.trial)
        metascript.trial_id = trial.id
        metascript.name = trial.script
        metascript.fake_path(trial.script, "")
        metascript.paths[trial.script].code_hash = None

        metascript.trial_id = Trial.store(
            *metascript.create_trial_args(
                args="<update {}>".format(metascript.trial_id), run=False
            )
        )
        debug_mode = args.debug

        # print ('Before we start, let me be clear:')
        print ('You are dealing with Trial {} '.format(args.trial))
        if args.funcname is not None:
            print ('You are dealing with Function {} '.format(args.funcname))
        else:
            print ('You are dealing with Variable {} '.format(args.varname))

        # for trial table
        result_trial = trial.pull_content(trial.id)
        # metascript.trial.push_content(metascript.trial_id, result_trial)
        trial_table = trial.__table__
        ### print ('Step 0: Trial prov: {}'.format(trial_table))

        # definition provenance part
        # for function_def
        function_def = FunctionDef(trial_ref=args.trial)
        result_functiondef = function_def.pull_content(trial.id)
        # function_def.push_content(metascript.trial_id, result_functiondef)
        function_def_table = function_def.__table__
        ### print ('Step 1: Definition prov: {}'.format(function_def_table))

        # collect all the function definitions
        func_defs = []
        for r in result_functiondef:
            func_defs.append(r.name)
        #print(func_defs)

        # # for object
        # object = Object(trial_ref=args.trial)
        # result_object = object.pull_content(trial.id)
        # object.push_content(metascript.trial_id, result_object)
        # object_table = object.__table__
        # ### print ('Step 2: we have done with {} table'.format(object_table))

        # # for object_value
        # object_value = ObjectValue(trial_ref=args.trial)
        # result_objectvalue = object_value.pull_content(trial.id)
        # object_value.push_content(metascript.trial_id, result_objectvalue)
        # object_value_table = object_value.__table__
        # ### print ('Step 3: we have done with {} table'.format(object_value_table))

        # # deployment provenance part
        # # for dependency
        # dependency = Dependency(trial_ref=args.trial)
        # result_dependency = dependency.pull_content(trial.id)
        # dependency.push_content(metascript.trial_id, result_dependency)
        # dependency_table = dependency.__table__
        # print ('Step 2.1: we have done with {} table'.format(dependency_table))

        # # for environment_attr
        # environment_attr = EnvironmentAttr(trial_ref=args.trial)
        # result_environmentattr = environment_attr.pull_content(trial.id)
        # environment_attr_table = environment_attr.__table__
        # environment_attr.push_content(metascript.trial_id, result_environmentattr)
        # print ('Step 2.2: we have done with {} table'.format(environment_attr_table))

        # # for module
        # # we don't need to copy the module table here
        # print("Step 2: we don't need to deal with module table")

        # execution
        # # for file_access
        # file_access = FileAccess(trial_ref=args.trial)
        # result_fileaccess = file_access.pull_content(trial.id)
        # file_access.push_content(metascript.trial_id, result_fileaccess)
        # file_access_table = file_access.__table__
        # print ('Step 3.1: we have done with {} table'.format(file_access_table))

        # for variable
        variable = Variable(trial_ref=args.trial)
        result_variable = variable.pull_content(trial.id)
        # variable.push_content(metascript.trial_id, result_variable)
        variable_table = variable.__table__
        ### print ('Step 4: Variable prov: {}'.format(variable_table))

        # get the global variable declarations here
        var_defs = []
        for r in result_variable:
            if r.activation_id == 1 and r.type == 'normal':
                var_defs.append(r.name)
        var_defs = list(set(var_defs))
        #print(var_defs)

        # for variable_dependency
        variable_dependency = VariableDependency(trial_ref=args.trial)
        result_variabledependency = variable_dependency.pull_content(trial.id)
        # variable_dependency.push_content(metascript.trial_id, result_variabledependency)
        variable_dependency_table = variable_dependency.__table__
        ### print ('Step 3: Variable Dependency prov: {}'.format(variable_dependency_table))

        # for variable_usage
        variable_usage = VariableUsage(trial_ref=args.trial)
        result_variableusage = variable_usage.pull_content(trial.id)
        # variable_usage.push_content(metascript.trial_id, result_variableusage)
        variable_usage_table = variable_usage.__table__
        # print ('Step 3.4: we have done with {} table'.format(variable_usage_table))

        # for function_activation

        function_activation = Activation(trial_ref=args.trial)
        result_functionactivation = function_activation.pull_content(trial.id)
        ### if the input is function name, we are dealing with function
        if args.funcname is not None:
            ### store function_activation_id
            downstream_func = []
            given_funcids = []
            upstream_func = [] ## if given func is not global function, collect its upstream functions
            ### first, we get function_activation id for given function
            for r in result_functionactivation:
                if(r.name == args.funcname):
                    downstream_func.append(r.id)
                    upstream_func.append(r.id)
                    given_funcids.append(r.id)
            given_funcname = args.funcname
            debug_print("given function ID", given_funcids, debug_mode)
            debug_print("given function name", given_funcname, debug_mode)
            ### if the caller_id of this function is not global, we should get their upstream as well
            debug_print("downstream function", downstream_func, debug_mode)
            debug_print("upstream function", upstream_func, debug_mode)
            for i in upstream_func:
                for r in result_functionactivation:
                    if r.id == i and r.caller_id != 1 and r.caller_id not in upstream_func:
                        upstream_func.append(r.caller_id)
            ### then, we get the downstream function_activation ids
            for i in downstream_func:
                for r in result_functionactivation:
                    if (r.caller_id == i) and r.id not in downstream_func:
                        downstream_func.append(r.id)
            debug_print("updated downstream function", downstream_func, debug_mode)
            debug_print("updated upstream function", upstream_func, debug_mode)
            related_func = downstream_func + upstream_func
            debug_print("related function", related_func, debug_mode)

            # ### store the sub function_activation provenance
            # new_result_functionactivation = []
            # for r in result_functionactivation:
            #     if r.id in downstream_func:
            #         new_result_functionactivation.append(r)
            # ### get all related function names
            # # fnames = funcnames
        ### this time, we are dealing with variable instead of function
        else:
            given_varname = args.varname
            debug_print("given variable name", given_varname)
        # function_activation.push_content(metascript.trial_id, new_result_functionactivation)
        function_activation_table = function_activation.__table__
        # print ('Step 4: Execution prov: {}'.format(function_activation_table))

        # # for object_value
        # object_value = ObjectValue(trial_ref=args.trial)
        # result_objectvalue = object_value.pull_content(trial.id)

        # ### if the input is function name, we are dealing with function
        # if args.funcname is not None:
        #     objectids = []
        #     ### we have function_activation_id list -> downstream_func (not complete yet), and find the corresponding object value for them
        #     for r in result_objectvalue:
        #         if r.function_activation_id in related_func:
        #             objectids.append(r.id)
        #     # print('\tThe object ID list is {}'.format(objectids))
        # ### this time, we are dealing with variable instead of function
        # else:
        #     new_result_objectvalue = result_objectvalue
        # # object_value.push_content(metascript.trial_id, new_result_objectvalue)
        # object_value_table = object_value.__table__
        # print ('Step 5: Execution prov: {}'.format(object_value_table))

        #########################################
        # print("I think we are done with the provenance part")
        # print("So, now we will start to create a ProvScript for you")
        #########################################

        # print ('The origin script name is: {}'.format(metascript.name))
        origin_file = open(metascript.name, "r")
        ### open a new file to store sub script
        update_file = open("ProvScript.py", "w")

        ### function definition bound
        update_file.write("# This is the function declaration part\n")
        update_file.write("# - Your previous script contains the following function definitions:\n")
        func_defs_str = ""
        for f in func_defs:
            func_defs_str = func_defs_str + '###' + f + '\n'
        update_file.write(func_defs_str)

        update_file.write("# This is the global variable declaration part\n")
        update_file.write("# - Your previous script contains the following global variable:\n")
        var_defs_str = ""
        for f in var_defs:
            var_defs_str = var_defs_str + '###' + f + '\n'
        update_file.write(var_defs_str)

        line_list = []

        ### first, we will deal with the function name input
        if args.funcname is not None:
            ### first, given_funcid might be activated several times
            ### we already store all the ids in given_funcids

            ### function return setup
            ### get the return id
            returnids = []
            for r in result_variable:
                if r.activation_id in related_func:
                    returnids.append(r.id)
            # returnids.sort()
            debug_print("given function's return value ID", returnids, debug_mode)

            ### trace the return dependency and update returnids list to store all related functions, variables and so on
            ### TODO: need more efficient algorithm here!!!
            # source_id is dependent on target_id, so we need all source_id if we change target_id
            for c in returnids:
                for r in result_variabledependency:
                    if r.target_id == c and r.source_id not in returnids:
                        # print("{} -> {}".format(r.target_id, r.source_id))
                        returnids.append(r.source_id)
            # returnids.sort()
            debug_print("updated dependency list (with source_id)", returnids, debug_mode)
            # also, some source_id may depend on something else, we will trace back (for normal and arg), add them as well
            loop_list = []
            condition_list = []
            for c in returnids:
                for r in result_variabledependency:
                    if r.source_id == c: 
                        if r.type == "loop":
                            # loop_list.append(r.id)
                            loop_list.append(r.target_id)
                            if r.target_id not in returnids:
                                returnids.append(r.target_id)
                        if r.type == "conditional":
                            # condition_list.append(r.id)
                            condition_list.append(r.target_id)
                            if r.target_id not in returnids:
                                returnids.append(r.target_id)
            returnids.sort()
            debug_print("dependency list (with loop and cond)", returnids, debug_mode)
            debug_print("loop list", loop_list, debug_mode)
            debug_print("cond list", condition_list, debug_mode)

            ### deal with loop and condition cases
            for u in result_variableusage:
                if u.variable_id in loop_list and u.line not in line_list:
                    line_list.append(u.line)
            if_line_list = []
            for u in result_variableusage:
                if u.variable_id in condition_list and u.line not in if_line_list:
                    if_line_list.append(u.line)
            for i in if_line_list:
                line_list += check_cond(i, result_functiondef)
            # print(line_list)

            argids = []
            callids = []
            param_ids = []
            filewriteids = []
            grayboxids = []
            active_funcall = []
            normal_ids = []
            remove_returnids = []
            add_returnids = []
            for t in returnids:
                r = result_variable[t-1]
                if r.type == '--graybox--': # don't need graybox, discuss later
                    grayboxids.append(t)
                    remove_returnids.append(t)
                if r.type == '--blackbox--': # don't need blackbox
                    remove_returnids.append(t)
                if r.type == 'normal': # add the variable assignment
                    normal_ids.append(t)
                    if r.line not in line_list:
                        line_list.append(r.line)
                    remove_returnids.append(t)
                if r.type == 'virtual': # don't need return value
                    remove_returnids.append(t)
                if r.type == 'param': # deal with param later
                    param_ids.append(t)
                    if r.line not in line_list:
                        line_list.append(r.line)
                    if r.activation_id not in active_funcall:
                        active_funcall.append(r.activation_id)
                    remove_returnids.append(t)
                if r.type == 'arg': # deal with arg later
                    argids.append(t)
                    remove_returnids.append(t)
                if r.type == 'call':
                    callids.append(t)
                    add_returnids += get_same_line_call(r.line, result_variable)
                    if r.activation_id not in active_funcall:
                        active_funcall.append(r.activation_id)
                if r.name == 'file.write': # file write is special case here
                    ### since file.write depends on the previous one, we might add some unrelevant file.write here
                    filewriteids.append(t)
            # filewriteids = list(set(filewriteids))
            for i in remove_returnids:
                if i in returnids:
                    returnids.remove(i)
            for i in add_returnids:
                if i not in returnids:
                    returnids.append(i)
            debug_print("graybox list", grayboxids, debug_mode)
            debug_print("normal list", normal_ids, debug_mode)
            debug_print("active_funcall list", active_funcall, debug_mode)
            debug_print("arg list", argids, debug_mode)
            debug_print("call list", callids, debug_mode)
            debug_print("param list", param_ids, debug_mode)
            # debug_print("filewrite list", filewriteids, debug_mode)
            debug_print("updated dependency list", returnids, debug_mode)
            # print(line_list)

            # # XXX: it will include redundant calls without graybox 
            # # XXX: we should check each varid there
            # # XXX: if varids doesn't include the closest graybox in front of it -> invalid function call
            # ### here, we will deal with file.write
            # useless_ids = []
            # for f in filewriteids:
            #     res = get_closest_graybox(f, result_variable)
            #     if res in grayboxids:
            #         continue
            #     else: # this means we add some unrelevant file.write, we need to remove those
            #         useless_ids.append(f)
            #         returnids.remove(f)
            # print(useless_ids)

            ### the only thing left in returnids is function calls
            returnids = list(set(returnids))
            returnids.sort()
            debug_print("updated dependency list", returnids, debug_mode)
            # print("\tUpdated dependency list is {}".format(returnids))

            ### deal with arg - buildin func argment
            ### might be 'file' in 'file.write', we need to include the file.open as well
            argnames = []
            for r in result_variable:
                if r.id in argids:
                    argnames.append(r.name)
            # argnames = list(set(argnames))
            arg2normalids = []
            if 'file' in argnames:
                for r in result_variable:
                    if r.name == 'file' and r.type == 'normal':
                            arg2normalids.append(r.id)
            # print("\targ to normal ID list is {}".format(arg2normalids))

            for r in result_variable:
                if r.id in arg2normalids and r.line not in line_list:
                    line_list.append(r.line)
            # print(line_list)

            ### get the func name that relate to the given function
            var_id = []
            for r in result_variable:
                if r.id in returnids:
                    var_id.append(find_active_id(r.name, r.line, result_functionactivation))
                    var_id.append(r.activation_id)
            var_id = list(set(var_id + downstream_func))
            if 0 in var_id:
                var_id.remove(0)
            var_id.remove(1)
            debug_print("var_id", var_id, debug_mode)


            ### for all related func, get their upstream (if not global)
            var_upstream_func = []
            for r in result_functionactivation:
                if r.id in var_id and r.caller_id != 1 and r.id != 1:
                    var_upstream_func.append(r.caller_id)

            ### we might need to add upstream functions (if given function is not global)
            var_all = list(set(var_id + upstream_func + var_upstream_func))
            debug_print("var_all", var_all, debug_mode)

            ### var_name_all: all the related functions (given function) and its upstream functions
            var_name_all = []
            for r in result_functionactivation:
                if r.id in var_all:
                    var_name_all.append(r.name)
            debug_print("var_all_name", var_name_all, debug_mode)

            # collect global function activation id - need to add the param for it (they might use some edited variable)
            global_func = []
            ### add the func execute line and definitions
            for r in result_functionactivation:
                if r.id in var_all and r.name in func_defs:
                    if r.line not in line_list:
                        line_list.append(r.line)
                    if r.caller_id == 1:
                        global_func.append(r.id)
            for r in result_functiondef:
                if r.name in var_name_all:
                    for line in range(r.first_line, r.last_line+1):
                        if line not in line_list:
                            line_list.append(line)
            for r in result_functionactivation:
                if r.id in var_all and r.caller_id == 1:
                    global_func.append(r.id)
            global_func = list(set(global_func))
            debug_print("global func activeID", global_func, debug_mode)
            # print(line_list)

            ### get the previous param id for global function
            paramids = []
            paramvalues = []
            for r in result_variable:
                if r.activation_id in global_func and r.type == 'param' and r.id not in paramids:
                    paramids.append(r.id)
                    paramvalues.append(r.value)
            paramids.sort()
            debug_print("global func paramID", paramids, debug_mode)

            ### trace the param dependency
            param2directids = []
            for p in paramids:
                for r in result_variabledependency:
                    if r.source_id == p:
                        if result_variable[r.target_id-1].type != 'normal' and r.target_id not in paramids:
                            paramids.append(r.target_id)
                        elif result_variable[r.target_id-1].type == 'normal' and r.target_id not in param2directids:
                            param2directids.append(r.target_id)
            debug_print("global func paramID (updated)", paramids, debug_mode)
            debug_print("global func direct paramID", param2directids, debug_mode)

            ### remove those param are modified in ProvScript
            ### first, we collect those param assignment lines and compare them with line_list, if they already exist (means that it will modify inside ProvScript), we don't need to do assignment for them
            param2directlines = []
            for p in param2directids:
                for r in result_variable:
                    if r.id == p:
                        # we will use it later after we collect line_list
                        param2directlines.append(r.line)
            # print(line_list)

            ### if the param is included, we should included the function activation as well
            for r in result_functionactivation:
                if r.id in var_all and r.line not in line_list:
                    line_list.append(r.line)
            # print(line_list)

            ### function param setup
            update_file.write("\n# This is the param setup part - We are going to setup the function params - The following params will be assigned in your original script, but the values are not relevant to your update\n")
            # print(line_list)
            ### get the useless param ids (modified in ProvScript)
            useless_param2directids = []
            for i in range(0,len(param2directids)):
                if param2directlines[i] in line_list:
                    useless_param2directids.append(param2directids[i])
            # print(useless_param2directids)

            for u in useless_param2directids:
                param2directids.remove(u)
            # print(param2directids)
            param2directids = list(set(param2directids))
            debug_print("global func direct paramID (updated)", param2directids, debug_mode)

            ### compare with normal_ids list with param
            for p in param2directids:
                if p in normal_ids:
                    normal_ids.remove(p)
            # print("\tvariable ID list (updated) is {}".format(normal_ids))
            for i in result_variable:
                if i.id in normal_ids and i.line not in line_list:
                    line_list.append(i.line)
            # print(line_list)


            ### get the corresponding names
            param2directnames = []
            param2directvalues = []
            for r in result_variable:
                for p in param2directids:
                    if r.id == p:
                        param2directnames.append(r.name)
                        param2directvalues.append(r.value)

            ### write param setup to file
            for i in range(0,len(param2directnames)):
                update_file.write(
                    "{} = {}\n".format(
                        param2directnames[i],
                        param2directvalues[i]
                        )
                    )

        # then we deal with the variable input
        else:
            # try to find the variable name when it first appears
            varid = []
            varid_copy = []
            for r in result_variable:
                if r.name == given_varname and r.activation_id == 1:
                    varid.append(r.id)
                    varid_copy.append(r.id)
            debug_print("variable ID", varid)

            varid_end = []
            for v in varid_copy:
                for r in result_variabledependency:
                    if r.source_id == v and r.target_id not in varid_copy:
                        print("{} <- {}, type = {}".format(r.source_id, r.target_id, r.type))
                        if result_variable[r.target_id-1].type == 'normal' and result_variable[r.target_id-1].activation_id == 1:
                            if r.target_id not in varid_end:
                                varid_end.append(r.target_id)
                        elif result_variable[r.target_id-1].type == 'function definition':
                            pass
                        else:
                            varid_copy.append(r.target_id)
            debug_print("variable ID sub list(updated target_id)", varid_copy)
            debug_print("variable ID end list (updated target_id)", varid_end)
            varid_copy += varid_end
            debug_print("variable ID list (updated target_id)", varid_copy)

            for v in varid_copy:
                for r in result_variabledependency:
                    if r.target_id == v and r.source_id not in varid_copy:
                        print("{} -> {}, type = {}".format(r.target_id, r.source_id, r.type))
                        varid_copy.append(r.source_id)
            debug_print("variable ID list (updated source_id)", varid_copy)
            for i in varid_end:
                varid_copy.remove(i)
            varids = varid_copy

            loop_list = []
            cond_list = []
            for v in varids:
                for r in result_variabledependency:
                    if r.source_id == v:
                        if r.type == "loop":
                            loop_list.append(r.target_id)
                            if r.target_id not in varids:
                                varids.append(r.target_id)
                        if r.type == "conditional":
                            cond_list.append(r.target_id)
                            if r.target_id not in varids:
                                varids.append(r.target_id)
            debug_print("var ID (with loop and cond)", varids, debug_mode)
            debug_print("loop list", loop_list, debug_mode)
            debug_print("cond list", cond_list, debug_mode)

            graybox_varid = []
            for v in varids:
                if result_variable[v-1].type == '--graybox--':
                    graybox_varid.append(v)
            debug_print("graybox variable list", graybox_varid, debug_mode)

            # related functions' parameters
            func_params = []
            for v in graybox_varid:
                for r in result_variabledependency:
                    if r.source_id == v:
                        if r.type == "parameter":
                            if result_variable[r.target_id-1].activation_id == 1 and r.target_id not in func_params and r.target_id not in varids:
                                func_params.append(r.target_id)
            debug_print("var ID list (graybox updated)", varids, debug_mode)
            debug_print("function param list", func_params, debug_mode)

            related_funcdef_list = []
            varids_remove = []
            for v in varids:
                if result_variable[v-1].activation_id != 0: # and result_variable[v-1].activation_id != 1:
                    ### this means it belongs to some functions (or loop or cond or even global functions), we will include their definitions
                    current_line = result_variable[v-1].line
                    belong_funcdef = check_def_id(current_line, result_functiondef)
                    if belong_funcdef != 0:
                        # include all the related function definition list.
                        if belong_funcdef not in related_funcdef_list:
                            related_funcdef_list.append(belong_funcdef)
                        # remove those called by some function, we will include all the function definition
                        if result_variable[v-1].activation_id != 1:
                            varids_remove.append(v)
                        # remove those function definition, we will include them 
                        if result_variable[v-1].type == 'function definition':
                            varids_remove.append(v)

            debug_print("varid remove list", varids_remove, debug_mode)
            debug_print("related function definition list", related_funcdef_list, debug_mode)

            for i in varids_remove:
                varids.remove(i)
            for i in graybox_varid:
                varids.remove(i)
            debug_print("var ID list (updated)", varids, debug_mode)

            varids_remove = []
            related_func_calls = []
            normal_varid = []
            for v in varids:
                if result_variable[v-1].type == 'call':
                    related_func_calls.append(v)
                    varids_remove.append(v)
                if result_variable[v-1].type == 'normal':
                    normal_varid.append(v)
                    varids_remove.append(v)
            for i in varids_remove:
                varids.remove(i)

            debug_print("related funcion activation list", related_func_calls, debug_mode)
            debug_print("related normal variable list", normal_varid, debug_mode)
            # it should be nothing left in varids
            debug_print("var ID list (final)", varids, debug_mode)

            # double check whether we include all active functions' definition
            for v in related_func_calls:
                for r in result_variabledependency:
                    if r.source_id == v and r.type == 'direct':
                        print("{} <- {}, type = {}".format(r.source_id, r.target_id, r.type))
                        current_line = result_variable[r.target_id-1].line
                        belong_funcdef = check_def_id(current_line, result_functiondef)
                        if belong_funcdef != 0:
                            # include all the related function definition list.
                            if belong_funcdef not in related_funcdef_list:
                                related_funcdef_list.append(belong_funcdef)
            debug_print("related function definition list (updated)", related_funcdef_list, debug_mode)

            line_list = []
            # add function definition
            for i in related_funcdef_list:
                tmp = result_functiondef[i-1]
                for line in range(tmp.first_line, tmp.last_line + 1):
                    if line not in line_list:
                        line_list.append(line)

            # add function activation
            for i in related_func_calls:
                func_call_line = result_variable[i-1].line
                if func_call_line not in line_list:
                    line_list.append(func_call_line)

            # add normal variable
            for i in normal_varid:
                var_line = result_variable[i-1].line
                if var_line not in line_list:
                    line_list.append(var_line)

            param_name = []
            param_value = []
            for i in func_params:
                tmp = result_variable[i-1]
                param_name.append(tmp.name)
                param_value.append(tmp.value)

            ### function param setup
            update_file.write("\n# This is the param setup part - We are going to setup the function params - The following params will be assigned in your original script, but the values are not relevant to your update\n")
            ### write param setup to file
            for i in range(0,len(func_params)):
                update_file.write(
                    "{} = {}\n".format(
                        param_name[i],
                        param_value[i]
                        )
                    )

        ### copy the script
        update_file.write("\n# This is the ProvScript part\n")

        # This is the module part
        origin_filelines = origin_file.readlines()
        file_index = 0
        for line in origin_filelines:
            file_index = file_index + 1
            if line[0:6] == 'import' or line[0:4] == 'from':
                ### haha, this is import module part!
                ###update_file.write(line)
                line_list.append(file_index)

        # This is the execution part
        line_list = list(set(line_list))
        line_list.sort()

        ### read from original script and store content to new file
        for l in line_list:    
            content = linecache.getline(metascript.name, l)
            content_comment = content.rstrip() + ' #####L' + str(l) + '\n'
            #print(content_comment)
            update_file.write(content_comment)

        update_file.close()

        print ('Trial {} has been created'.format(metascript.trial_id))
        print ("Now, we generate a ProvScript for you: ProvScript.py")


