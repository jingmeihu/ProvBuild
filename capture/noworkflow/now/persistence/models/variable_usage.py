# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Slicing Usage Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy import CheckConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr

from .. import relational, content, persistence_config
from .base import AlchemyProxy, proxy_class, backref_one


@proxy_class
class VariableUsage(AlchemyProxy):
    """Represent a variable usage during program slicing"""

    __tablename__ = "variable_usage"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id"],
                             ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "activation_id", "variable_id"],
                             ["variable.trial_id",
                              "variable.activation_id",
                              "variable.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    activation_id = Column(Integer, index=True)
    variable_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    line = Column(Integer)
    context = Column(Text, CheckConstraint("context IN ('Load', 'Del')"))

    trial = backref_one("trial")  # Trial.variable_usages
    activation = backref_one("activation")  # Activation.variables_usages
    variable = backref_one("variable")  # Variable.usages

    prolog_description = PrologDescription("usage", (
        PrologTrial("trial_id", link="variable.trial_id"),
        PrologAttribute("activation_id", link="variable.activation_id"),
        PrologAttribute("variable_id", link="variable.id"),
        PrologAttribute("id"),
        PrologRepr("name", attr_name="variable.name"),
        PrologAttribute("line"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "during a specific function activation (*activation_id*),\n"
        "in a specific *line* of code,\n"
        "a variable *name* was accessed (read, delete)."
    ))

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], relational.base):
            obj = args[0]
            trial_ref = obj.id
        elif args:
            trial_ref = kwargs.get("trial_ref", args[0])
        else:
            trial_ref = kwargs.get("trial_ref", None)
        session = relational.session
        obj = VariableUsage.load_variableusage(trial_ref, session=session)
        if obj is not None:
            super(VariableUsage, self).__init__(obj)

    def __repr__(self):
        name = self.variable.name
        return (
            "VariableUsage({self.trial_id}, {self.activation_id}, "
            "{self.variable_id}, {self.id}, {name}, {self.line}, "
            "{self.context})"
        ).format(**locals())

    def __str__(self):
        name = self.variable.name
        return "(L{self.line}, {name}, <{self.context}>)".format(**locals())

    @classmethod  # query
    def load_variableusage(cls, trial_ref, session=None):
        """Load variableusage by variableusage reference

        Find reference on trials id and tags name
        """
        session = session or relational.session
        result = session.query(cls.m).filter(cls.m.trial_id == trial_ref)
        return result.first()

    def pull_content(cls, tid, session=None):
        session = session or relational.session
        ttrial = cls.__table__
        result = session.query(ttrial).filter(ttrial.c.trial_id == tid).all()
        return result

    def push_content(cls, id, reslist, session=None):
        session = session or relational.session
        ttrial = cls.__table__
        for res in reslist:
            result = session.execute(
                ttrial.insert(),
                {"trial_id": id, "activation_id": res.activation_id, "variable_id": res.variable_id,"id": res.id, "line": res.line, "context": res.context}
            )
            session.commit()