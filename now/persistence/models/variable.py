# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""Slicing Variable Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text, TIMESTAMP, select, alias
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import aliased

from .. import relational, content, persistence_config

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr, PrologTimestamp, PrologNullableRepr

from .base import AlchemyProxy, proxy_class, many_ref, many_viewonly_ref, proxy
from .base import backref_one, backref_many
from .variable_dependency import VariableDependency


@proxy_class
class Variable(AlchemyProxy):
    """Represent a variable captured during program slicing"""

    __tablename__ = "variable"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "activation_id", "id"),
        ForeignKeyConstraint(["trial_id", "activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    activation_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    name = Column(Text)
    line = Column(Integer)
    value = Column(Text)
    time = Column(TIMESTAMP)
    type = Column(Text)                                                          # pylint: disable=invalid-name

    usages = many_ref("variable", "VariableUsage")

    # dependencies in which this variable is the dependent
    dependencies_as_source = many_viewonly_ref(
        "source", "VariableDependency",
        primaryjoin=(
            (id == VariableDependency.m.source_id) &
            (activation_id == VariableDependency.m.source_activation_id) &
            (trial_id == VariableDependency.m.trial_id))
    )

    # dependencies in which this variable is the dependency
    dependencies_as_target = many_viewonly_ref(
        "target", "VariableDependency",
        primaryjoin=(
            (id == VariableDependency.m.target_id) &
            (activation_id == VariableDependency.m.target_activation_id) &
            (trial_id == VariableDependency.m.trial_id)))

    dependencies = many_viewonly_ref(
        "dependents", "Variable",
        secondary=VariableDependency.__table__,
        primaryjoin=(
            (id == VariableDependency.m.source_id) &
            (activation_id == VariableDependency.m.source_activation_id) &
            (trial_id == VariableDependency.m.trial_id)),
        secondaryjoin=(
            (id == VariableDependency.m.target_id) &
            (activation_id == VariableDependency.m.target_activation_id) &
            (trial_id == VariableDependency.m.trial_id)))

    trial = backref_one("trial")  # Trial.variables
    activation = backref_one("activation")  # Activation.variables
    dependents = backref_many("dependents")  # Variable.dependencies

    prolog_description = PrologDescription("variable", (
        PrologTrial("trial_id", link="activation.trial_id"),
        PrologAttribute("activation_id", link="activation.id"),
        PrologAttribute("id"),
        PrologRepr("name"),
        PrologAttribute("line"),
        PrologNullableRepr("value"),
        PrologTimestamp("timestamp", attr_name="time"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "during a specific function activation (*activation_id*),\n"
        "in a specific *line* of code,\n"
        "and in a specific *timestamp*,\n"
        "a variable *name* was updated\n"
        "to a new *value*."
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
        obj = Variable.load_variable(trial_ref, session=session)
        if obj is not None:
            super(Variable, self).__init__(obj)

    def __key(self):
        return self.id

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        return self.__key() == other.__key()                                     # pylint: disable=protected-access

    @property
    def return_dependency(self):
        """Return "return" dependency. Valid only for call type"""
        return proxy(self._get_instance().dependencies.filter(
            Variable.m.name == "return").first())

    @property
    def box_dependency(self):
        """Return "return" dependency. Valid only for call type"""
        return proxy(self._get_instance().dependencies.filter(
            Variable.m.name.like("%box--")).first())

    @classmethod  # query
    def fast_arg_and_original(cls, trial_id, session=None):
        """Return tuples with variable of type arg and original variable"""
        # ToDo: optimize here
        session = session or relational.session
        avar = alias(cls.t, name="avar")
        abox = alias(VariableDependency.t, name="abox")
        box = alias(cls.t, name="box")
        obox = alias(VariableDependency.t, name="obox")
        ovar = alias(cls.t, name="ovar")


        query = select([avar.c.id, ovar.c.id]).select_from(
            ovar.join(obox, (
                (ovar.c.id == obox.c.target_id) &
                (ovar.c.trial_id == obox.c.trial_id) &
                (ovar.c.activation_id == obox.c.target_activation_id)
            )).join(box, (
                (box.c.id == obox.c.source_id) &
                (box.c.trial_id == obox.c.trial_id) &
                (box.c.activation_id == obox.c.source_activation_id)
            )).join(abox, (
                (box.c.id == abox.c.target_id) &
                (box.c.trial_id == abox.c.trial_id) &
                (box.c.activation_id == abox.c.target_activation_id)
            )).join(avar, (
                (avar.c.id == abox.c.source_id) &
                (avar.c.trial_id == abox.c.trial_id) &
                (avar.c.activation_id == abox.c.source_activation_id)
            ))
        ).where(
            (avar.c.type == "arg") &
            (avar.c.trial_id == trial_id) &
            (ovar.c.name == avar.c.name)
        )
        return session.execute(query)

    def __repr__(self):
        return (
            "Variable({0.trial_id}, {0.activation_id}, "
            "{0.id}, {0.name}, {0.line}, {0.type})"
        ).format(self)

    def __str__(self):
        return "(L{0.line}, {0.name}, {0.value})".format(self)

    @classmethod  # query
    def load_variable(cls, trial_ref, session=None):
        """Load variable by variable reference

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
                {"trial_id": id, "activation_id": res.activation_id, "id": res.id, "name": res.name, "line": res.line, "value": res.value, "type": res.type}
            )
            session.commit()
