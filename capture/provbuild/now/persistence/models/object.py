# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Object Model"""
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
class Object(AlchemyProxy):
    """Represent an object (global, argument, function call)"""

    __tablename__ = "object"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "function_def_id", "id"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id", "function_def_id"],
                             ["function_def.trial_id",
                              "function_def.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    function_def_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    name = Column(Text)
    type = Column(                                                               # pylint: disable=invalid-name
        Text,
        CheckConstraint("type IN ('GLOBAL', 'ARGUMENT', 'FUNCTION_CALL')"))

    trial = backref_one("trial")  # Trial.objects
    function_def = backref_one("function_def")  # FunctionDef.objects

    prolog_description = PrologDescription("object", (
        PrologTrial("trial_id", link="function_def.trial_id"),
        PrologAttribute("function_def_id", link="function_def.id"),
        PrologAttribute("id"),
        PrologRepr("name"),
        PrologRepr("type"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "a given function definition (*function_def_id*),\n"
        "has a GLOBAL/ARGUMENT/FUNCTION_CALL (*type*),\n"
        "with *name*.\n"
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
        obj = Object.load_object(trial_ref, session=session)
        super(Object, self).__init__(obj)

    def __repr__(self):
        return (
            "Object({0.trial_id}, {0.function_def_id}, "
            "{0.id}, {0.name}, {0.type})"
        ).format(self)

    @classmethod  # query
    def load_object(cls, trial_ref, session=None):
        """Load object by object reference

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
                {"trial_id": id, "function_def_id": res.function_def_id, "id": res.id, "name": res.name, "type": res.type}
            )
            session.commit()
