# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""'%now_ls_magic' magic"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from ...utils.formatter import PrettyLines
from .command import IpythonCommandMagic


class NowLsMagic(IpythonCommandMagic):
    """Return the list of noWorkflow magics"""

    def execute(self, func, line, cell, magic_cls):
        cline, ccell = "%", "%%"
        magics = magic_cls.now_magics
        out = ["Line magics:",
               cline + ("  " + cline).join(sorted(magics["line"])),
               "",
               "Cell magics:",
               ccell + ("  " + ccell).join(sorted(magics["cell"]))]
        return PrettyLines(out)
