# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Slicing Dependency Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text, select
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute

from .. import relational, content, persistence_config
from .base import AlchemyProxy, proxy_class, backref_one


@proxy_class
class VariableDependency(AlchemyProxy):
    """Represent a variable dependency captured during program slicing"""

    __tablename__ = "variable_dependency"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id"],
                             ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "source_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "target_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "source_activation_id",
                              "source_id"],
                             ["variable.trial_id",
                              "variable.activation_id",
                              "variable.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id",
                              "target_activation_id",
                              "target_id"],
                             ["variable.trial_id",
                              "variable.activation_id",
                              "variable.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    source_activation_id = Column(Integer, index=True)
    source_id = Column(Integer, index=True)
    target_activation_id = Column(Integer, index=True)
    target_id = Column(Integer, index=True)
    type = Column(Text)                                                          # pylint: disable=invalid-name

    trial = backref_one("trial")  # Trial.variable_dependencies
    # Activation.source_variables, Variable.dependencies_as_source
    source_activation = backref_one("source_activation")
    source = backref_one("source")
    # Activation.target_variables, Variable.dependencies_as_target
    target_activation = backref_one("target_activation")
    target = backref_one("target")

    prolog_description = PrologDescription("dependency", (
        PrologTrial("trial_id", link="variable.trial_id"),
        PrologAttribute("id"),
        PrologAttribute("source_activation_id", link="variable.activation_id"),
        PrologAttribute("source_id", link="variable.id"),
        PrologAttribute("target_activation_id", link="variable.activation_id"),
        PrologAttribute("target_id", link="variable.id"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "the value of a variable (*target_id*)\n"
        "in a specific function activation (*target_activation_id*),\n"
        "influenced somehow the value of another variable (*source_id*)\n"
        "in another function activation (*source_activation_id*).\n"
        "This influence can occur due to direct assignment,\n"
        "matching of arguments in function activations,\n"
        "changes in mutable arguments of function activations,\n"
        "assignment within control flow structure, and function return."
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
        obj = VariableDependency.load_variabledependency(trial_ref, session=session)
        if obj is not None:
            super(VariableDependency, self).__init__(obj)


    @classmethod  # query
    def fast_load_by_trial(cls, trial_id, session=None):
        """Return tuples with variable ids"""
        session = session or relational.session
        model = cls.m
        return session.execute(select([model.source_id, model.target_id])
            .where(model.trial_id == trial_id)
        )

    def __repr__(self):
        return (
            "VariableDependency({0.trial_id}, {0.id}, "
            "{0.source}, {0.target})"
        ).format(self)

    def __str__(self):
        return "{0.source} <- {0.target}".format(self)


    @classmethod  # query
    def load_variabledependency(cls, trial_ref, session=None):
        """Load variabledependency by variabledependency reference

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
                {"trial_id": id, "id": res.id, "source_activation_id": res.source_activation_id, "source_id": res.source_id, "target_activation_id": res.target_activation_id, "target_id": res.target_id, "type": res.type}
            )
            session.commit()

