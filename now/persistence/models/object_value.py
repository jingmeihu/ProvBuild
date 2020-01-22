# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""Object Value Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy import CheckConstraint

from .. import relational, content, persistence_config
from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr

from .base import AlchemyProxy, proxy_class, backref_one


@proxy_class
class ObjectValue(AlchemyProxy):
    """Represent an object value (global, argument)"""

    __tablename__ = "object_value"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "function_activation_id", "id"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "function_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    function_activation_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    name = Column(Text)
    value = Column(Text)
    type = Column(Text, CheckConstraint("type IN ('GLOBAL', 'ARGUMENT')"))       # pylint: disable=invalid-name

    trial = backref_one("trial")  # Trial.object_values
    activation = backref_one("activation")  # Ativation.object_values

    prolog_description = PrologDescription("object_value", (
        PrologTrial("trial_id", link="activation.trial_id"),
        PrologAttribute("activation_id", attr_name="function_activation_id",
                        link="activation.id"),
        PrologAttribute("id"),
        PrologRepr("name"),
        PrologRepr("value"),
        PrologRepr("type"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "a given activation (*function_activation_id*),\n"
        "has a GLOBAL/ARGUMENT (*type*) variable *name*,\n"
        "with *value*.\n"
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
        obj = ObjectValue.load_objectvalue(trial_ref, session=session)
        super(ObjectValue, self).__init__(obj)

    def __repr__(self):
        return (
            "ObjectValue({0.trial_id}, {0.function_activation_id}, {0.id}, "
            "{0.name}, {0.value}, {0.type})"
        ).format(self)

    def __str__(self):
        return "{0.name} = {0.value}".format(self)

    @classmethod  # query
    def load_objectvalue(cls, trial_ref, session=None):
        """Load object_value by lobject_value reference

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
                {"trial_id": id, "function_activation_id": res.function_activation_id, "id": res.id, "name": res.name, "value": res.value, "type": res.type}
            )
            session.commit()