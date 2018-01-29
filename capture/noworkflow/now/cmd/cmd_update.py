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

        print ('Before we start, let me be clear:')
        print ('You are dealing with Trial {} '.format(args.trial))
        if args.funcname is not None:
            print ('You are dealing with Function {} '.format(args.funcname))
        else:
            print ('You are dealing with Variable {} '.format(args.varname))

        # for trial table
        result_trial = trial.pull_content(trial.id)
        # metascript.trial.push_content(metascript.trial_id, result_trial)
        trial_table = trial.__table__
        print ('Step 0: Trial prov: {}'.format(trial_table))

        # definition provenance part
        # for function_def
        function_def = FunctionDef(trial_ref=args.trial)
        result_functiondef = function_def.pull_content(trial.id)
        # function_def.push_content(metascript.trial_id, result_functiondef)
        function_def_table = function_def.__table__
        print ('Step 1: Definition prov: {}'.format(function_def_table))

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
        # print ('Step 1.2: we have done with {} table'.format(object_table))

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
        print ('Step 2: Execution prov: {}'.format(variable_table))

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
        print ('Step 3: Execution prov: {}'.format(variable_dependency_table))

        # # for variable_usage
        # variable_usage = VariableUsage(trial_ref=args.trial)
        # result_variableusage = variable_usage.pull_content(trial.id)
        # variable_usage.push_content(metascript.trial_id, result_variableusage)
        # variable_usage_table = variable_usage.__table__
        # print ('Step 3.4: we have done with {} table'.format(variable_usage_table))

        # for function_activation

        function_activation = Activation(trial_ref=args.trial)
        result_functionactivation = function_activation.pull_content(trial.id)
        ### get the script file name - full path
        # for r in result_functionactivation:
        #     if (r.id == 1):
        #         script_name = r.name
        #         break

        ### if the input is function name, we are dealing with function
        if args.funcname is not None:
            ### store function_activation_id
            funcids = []
            funcnames = []
            upstream_func = [] ## if given func is not global function, collect its upstream functions
            upstream_funcname = []
            ### first, we get function_activation id for given function
            for r in result_functionactivation:
                if(r.name == args.funcname):
                    funcids.append(r.id)
                    #funcnames.append(r.name)
                    #given_funcid = r.id
                    given_funcname = r.name
                    #break
            #print(funcids)
            ### if the caller_id of this function is not global, we should get some upstream as well
            for i in funcids:
                for r in result_functionactivation:
                    if r.id == i and r.caller_id != 1:
                        funcids.append(r.caller_id)
                        upstream_func.append(r.caller_id)
                        #funcnames.append(r.name)
            ### then, we get the downstream function_activation ids
            for i in funcids:
                for r in result_functionactivation:
                    if (r.caller_id == i):
                        funcids.append(r.id)
                        #funcnames.append(r.name)
            # print(funcids)
            funcids.append(1)
            funcids = list(set(funcids))
            funcids.sort()
            # print(funcids)
            upstream_func = list(set(upstream_func))
            upstream_func.sort()
            #print(upstream_func)

            for i in funcids:
                for r in result_functionactivation:
                    if r.id == i:
                        funcnames.append(r.name)
            for i in upstream_func:
                for r in result_functionactivation:
                    if r.id == i:
                        upstream_funcname.append(r.name)

            ### store the sub function_activation provenance
            new_result_functionactivation = []
            for i in funcids:
                for r in result_functionactivation:
                    if(r.id == i):
                        new_result_functionactivation.append(r)
            ### get the downstream function names
            fnames = funcnames
        ### this time, we are dealing with variable instead of function
        else:
            given_varname = args.varname
            new_result_functionactivation = result_functionactivation
        # function_activation.push_content(metascript.trial_id, new_result_functionactivation)
        function_activation_table = function_activation.__table__
        print ('Step 4: Execution prov: {}'.format(function_activation_table))

        # for object_value
        object_value = ObjectValue(trial_ref=args.trial)
        result_objectvalue = object_value.pull_content(trial.id)

        ### if the input is function name, we are dealing with function
        if args.funcname is not None:
            ### we have function_activation_id list, and find the corresponding object value for them
            new_result_objectvalue = []
            for i in funcids:
                for r in result_objectvalue:
                    if (r.function_activation_id == i):
                        new_result_objectvalue.append(r)
        ### this time, we are dealing with variable instead of function
        else:
            new_result_objectvalue = result_objectvalue
        # object_value.push_content(metascript.trial_id, new_result_objectvalue)
        object_value_table = object_value.__table__
        print ('Step 5: Execution prov: {}'.format(object_value_table))

        #########################################
        print("I think we are done with the provenance part")
        print("So, now we will start to create a ProvScript for you")
        #########################################

        print ('The origin script name is: {}'.format(metascript.name))
        origin_file = open(metascript.name, "r")
        ### open a new file to store sub script
        update_file = open("ProvScript.py", "w")

        ### function definition bound
        update_file.write("# This is the function declaration part - Your previous script contains the following function definitions:\n")
        func_defs_str = ""
        for f in func_defs:
            func_defs_str = func_defs_str + '###' + f + '\n'
        update_file.write(func_defs_str)

        update_file.write("# This is the variable declaration part - Your previous script contains the following variable:\n")
        var_defs_str = ""
        for f in var_defs:
            var_defs_str = var_defs_str + '###' + f + '\n'
        update_file.write(var_defs_str)

        line_list = []

        ### first, we will deal with the function name input
        if args.funcname is not None:
            ### first, given_funcid might be activated several times
            ### so, we have to collect all the activation id for this given_func
            #print(given_funcname)
            given_funcids = []
            for r in result_functionactivation:
                if r.name == given_funcname:
                    given_funcids.append(r.id)
            #print(given_funcids)


            ### function return setup
            ### get the return id
            returnids = []
            for r in result_variable:
                if r.activation_id in given_funcids:
                    if r.name == 'return':
                        returnids.append(r.id)
            # print(returnids)

            ### trace the return dependency and update returnids list to store all related functions, variables and so on
            for t in returnids:
                for r in result_variabledependency:
                    if r.target_id == t and r.source_id not in returnids:
                        returnids.append(r.source_id)
            # print(list(set(returnids)))
            argids = []
            filewriteids = []
            grayboxids = []
            funcall = []
            for r in result_variable:
                for t in returnids:
                    if r.id == t:
                        if r.type == '--graybox--': # don't need graybox
                            grayboxids.append(t)
                            returnids.remove(t)
                        if r.type == '--blackbox--': # don't need blackbox
                            returnids.remove(t)
                        if r.type == 'normal': # add the variable assignment
                            line_list.append(r.line)
                            returnids.remove(t)
                        if r.type == 'virtual': # don't need return value
                            returnids.remove(t)
                        if r.type == 'param': # don't need param value
                            line_list.append(r.line)
                            funcall.append(r.activation_id)
                            returnids.remove(t)
                        if r.type == 'arg': # deal with arg later
                            argids.append(t)
                            returnids.remove(t)
                        if r.name == 'file.write': # file write is special case here
                            ### since file.write depends on the previous one, we might add some unrelevant file.write here
                            filewriteids.append(t)

            # XXX: it will include redundant calls without graybox 
            # XXX: we should check each varid there
            # XXX: if varids doesn't include the closest graybox in front of it -> invalid function call
            ### here, we will deal with file.write
            # print(list(set(varids)))
            # print(filewriteids)
            # print(grayboxids)
            useless_ids = []
            for f in filewriteids:
                res = get_closest_graybox(f, result_variable)
                if res in grayboxids:
                    continue
                else: # this means we add some unrelevant file.write, we need to remove those
                    useless_ids.append(f)
                    returnids.remove(f)


            ### the only thing left in returnids is function calls
            returnids = list(set(returnids))
            # print(argids)
            # print(returnids)

            argids = list(set(argids))
            ### deal with arg - might be 'file' in 'file.write', we need to include the file.open as well
            argnames = []
            for r in result_variable:
                for a in argids:
                    if r.id == a:
                        argnames.append(r.name)
            #print(argnames)
            arg2normalids = []
            for r in result_variable:
                for a in argnames:
                    if r.name == a:
                        if r.type == 'normal':
                            arg2normalids.append(r.id)
            #print(arg2normalids)

            for r in result_variable:
                for a in arg2normalids:
                    if r.id == a:
                        line_list.append(r.line)
            #print(line_list)

            ### get the func name that relate to the given function
            var_name = []
            var_line = []
            var_id = []
            for r in result_variable:
                for t in returnids:
                    if r.id == t:
                        var_name.append(r.name)
                        var_id.append(r.activation_id)
                        var_line.append(r.line)
            # print(var_name)
            var_id = list(set(var_id))
            var_id.sort()
            #print(var_line)

            ### for all related func, get their upstream (if not global)
            var_upstream_func = []
            var_upstream_funcname = []
            for i in var_id:
                for r in result_functionactivation:
                    if r.id == i and r.caller_id != 1:
                        var_upstream_func.append(r.caller_id)
            for i in var_upstream_func:
                for r in result_functionactivation:
                    if r.id == i:
                        var_upstream_funcname.append(r.name)
            # print(var_upstream_funcname)
            #print(upstream_funcname)


            ### we might need to add upstream functions (if given function is not global)
            var_name_upstream = upstream_funcname + var_upstream_funcname
            var_name_all = var_name + var_name_upstream
            var_name_upstream = list(set(var_name_upstream))
            for r in result_variable:
                if r.name in var_name_upstream:
                    if result_functionactivation[r.activation_id-1].name in var_name_upstream or r.activation_id == 1:
                        var_line.append(r.line)

            # print(var_name_upstream)
            # print(var_line)
            # print(var_name_all)

            # collect global function activation id - need to add the param for it (they might use some edited variable)
            global_func = []
            for r in result_functionactivation:
                if r.name == given_funcname:
                    if r.caller_id == 1:
                        global_func.append(r.id)

            ### add the func execute line and definitions
            for r in result_functionactivation:
                for v in var_name_all:
                    if r.name == v:
                        if r.line in var_line:
                            line_list.append(r.line)
                            if r.caller_id == 1:
                                global_func.append(r.id)
            for r in result_functiondef:
                for v in var_name_all:
                    if r.name == v:
                        for line in range(r.first_line, r.last_line+1):
                            line_list.append(line)
            #global_func = list(set(global_func))
            # print(global_func)

            #print(line_list)

            ### get the previous param id for global function
            paramids = []
            paramvalues = []
            for r in result_variable:
                for g in global_func:
                    if r.activation_id == g:
                        if r.type == 'param':
                            paramids.append(r.id)
                            paramvalues.append(r.value)
            paramids = list(set(paramids))
            paramids.sort()
            # print(paramids)
            # print (paramnames)
            # print (paramvalues)

            ### trace the param dependency
            param2directids = []
            for p in paramids:
                for r in result_variabledependency:
                    if r.source_id == p:
                        if result_variable[r.target_id-1].type != 'normal':
                            paramids.append(r.target_id)
                        else:
                            param2directids.append(r.target_id)

            ### remove those param are modified in ProvScript
            ### first, we collect those param assignment lines and compare them with line_list, if they already exist (means that it will modify inside ProvScript), we don't need to do assignment for them
            param2directlines = []
            for p in param2directids:
                for r in result_variable:
                    if r.id == p:
                        # we will use it later after we collect line_list
                        param2directlines.append(r.line)
            # print(param2directlines)
            # print(line_list)
            # print (param2directnames)

            ### if the param is included, we should included the function activation as well
            for r in result_functionactivation:
                if r.id in funcall:
                    line_list.append(r.line)

            ### get the function definition line
            for r in result_functiondef:
                for i in fnames:
                    if r.name == i:
                        for line in range(r.first_line, r.last_line+1):
                            line_list.append(line)
            # print(fnames)

            ### get the execution line
            for r in new_result_functionactivation:
                if r.id != 1:
                    if r.line in line_list:
                        continue;
                    else:
                        line_list.append(r.line)

            ### function param setup
            update_file.write("\n# This is the param setup part - We are going to setup the function params - The following params will be assigned in your original script, but the values are not relevant to your update\n")

            ### get the useless param ids (modified in ProvScript)
            useless_param2directids = []
            for i in range(0,len(param2directids)):
                if param2directlines[i] in line_list:
                    useless_param2directids.append(param2directids[i])

            for u in useless_param2directids:
                param2directids.remove(u)
            # print(param2directids)
            param2directids = list(set(param2directids))

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
            given_varid = []
            for r in result_variable:
                if r.name == given_varname:
                    given_varid.append(r.id)
            #print (given_varid)

            varids1 = given_varid
            for v in varids1:
                for r in result_variabledependency:
                    ### check those depends on given_varid 
                    if r.target_id == v and r.source_id not in varids1:
                        varids1.append(r.source_id)
            #print(varids1)

            varids2 = given_varid
            for v in varids2:
                for r in result_variabledependency:
                    ### check those given_varid depends on
                    if r.source_id == v and r.target_id not in varids2:
                        varids2.append(r.target_id)
            # print(varids1)
            #print(varids2)
            varids = varids1 + varids2
            varids = list(set(varids))
            #print(varids)

            argids = []
            filewriteids = []
            grayboxids = []
            for r in result_variable:
                for t in varids:
                    if r.id == t:
                        if r.type == '--graybox--': # don't need graybox
                            grayboxids.append(t)
                            varids.remove(t)
                        if r.type == '--blackbox--': # don't need blackbox
                            varids.remove(t)
                        if r.type == 'normal': # add the variable assignment
                            #print(r.line)
                            line_list.append(r.line)
                            varids.remove(t)
                        if r.type == 'virtual': # don't need return value
                            varids.remove(t)
                        if r.type == 'param': # don't need param value
                            varids.remove(t)
                        if r.type == 'arg': # deal with arg later
                            argids.append(t)
                            varids.remove(t)
                        if r.name == 'file.write': # file write is special case here
                            ### since file.write depends on the previous one, we might add some unrelevant file.write here
                            filewriteids.append(t)


            # XXX: it will include redundant calls without graybox 
            # XXX: we should check each varid there
            # XXX: if varids doesn't include the closest graybox in front of it -> invalid function call
            ### here, we will deal with file.write
            # print(list(set(varids)))
            # print(filewriteids)
            # print(grayboxids)
            useless_ids = []
            for f in filewriteids:
                res = get_closest_graybox(f, result_variable)
                if res in grayboxids:
                    continue
                else: # this means we add some unrelevant file.write, we need to remove those
                    useless_ids.append(f)
                    varids.remove(f)

            ### the only thing left in varids is function calls
            varids = list(set(varids))
            #print(argids)
            #print(varids)

            ### deal with arg - might be 'file' in 'file.write', we need to include the file.open as well
            argids = list(set(argids))
            argnames = []
            for r in result_variable:
                for a in argids:
                    if r.id == a:
                        argnames.append(r.name)
            #print(argnames)
            arg2normalids = []
            for r in result_variable:
                for a in argnames:
                    if r.name == a:
                        if r.type == 'normal':
                            arg2normalids.append(r.id)
            #print(arg2normalids)

            for r in result_variable:
                for a in arg2normalids:
                    if r.id == a:
                        line_list.append(r.line)
            #print(line_list)

            ### deal with function calls
            ### get the func name that relate to the given function
            var_name = []
            var_line = []
            var_id = []
            for r in result_variable:
                for t in varids:
                    if r.id == t:
                        var_name.append(r.name)
                        var_id.append(r.activation_id)
                        var_line.append(r.line)
            #print(var_name)
            #print(var_line)
            var_id = list(set(var_id))
            var_id.sort()
            #print(var_id)

            ### for all related func, get their upstream (if not global)
            var_upstream_func = []
            var_upstream_funcname = []
            for i in var_id:
                for r in result_functionactivation:
                    if r.id == i and r.caller_id != 1:
                        var_upstream_func.append(r.caller_id)
            for i in var_upstream_func:
                for r in result_functionactivation:
                    if r.id == i:
                        var_upstream_funcname.append(r.name)
            # print(var_upstream_funcname)
            # print(upstream_funcname)


            ### we might need to add upstream functions (if given function is not global)
            var_name_upstream = var_upstream_funcname
            var_name_all = var_name + var_name_upstream
            var_name_upstream = list(set(var_name_upstream))
            for r in result_variable:
                if r.name in var_name_upstream:
                    var_line.append(r.line)
            # print(var_name_upstream)
            #print(var_line)

            ### collect global function activation id - need to add the param for it (they might use some edited variable)
            global_func = []
            ### add the func execute line and definitions
            for r in result_functionactivation:
                for v in var_name_all:
                    if r.name == v:
                        if r.line in var_line:
                            line_list.append(r.line)
                            if r.caller_id == 1:
                                ### we need to deal with its params later
                                global_func.append(r.id)
            for r in result_functiondef:
                for v in var_name_all:
                    if r.name == v:
                        for line in range(r.first_line, r.last_line+1):
                            line_list.append(line)
            global_func = list(set(global_func))
            global_func.sort()
            #print(line_list)

            ### get the previous param id for global function
            paramids = []
            paramvalues = []
            for r in result_variable:
                for g in global_func:
                    if r.activation_id == g:
                        if r.type == 'param':
                            paramids.append(r.id)
                            paramvalues.append(r.value)
            paramids = list(set(paramids))
            paramids.sort()
            #print (paramids)
            #print (paramvalues)

            ### trace the param dependency
            param2directids = []
            for r in result_variabledependency:
                for p in paramids:
                    if r.source_id == p:
                        param2directids.append(r.target_id)
            #print(param2directids)

            ### remove those param are modified in ProvScript
            ### first, we collect those param assignment lines and compare them with line_list, if they already exist (means that it will modify inside ProvScript), we don't need to do assignment for them
            param2directlines = []
            for p in param2directids:
                for r in result_variable:
                    if r.id == p:
                        # we will use it later after we collect line_list
                        param2directlines.append(r.line)


            ### temporarily get the return values for global function 

            ### function param setup
            update_file.write("\n# This is the param setup part\n")
            update_file.write("# We are going to setup the function params\n")
            update_file.write("# The following params will be assigned in your original script, but the values are not relevant to your update\n")

            ### get the useless param ids (modified in ProvScript)
            useless_param2directids = []
            for i in range(0,len(param2directids)):
                if param2directlines[i] in line_list:
                    useless_param2directids.append(param2directids[i])

            for u in useless_param2directids:
                param2directids.remove(u)
            # print(param2directids)

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


