# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""Function Definition Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr, PrologNullableRepr

from .. import relational, content, persistence_config

from .base import proxy_class, AlchemyProxy, many_ref, backref_one
from .base import query_many_property
from .object import Object


@proxy_class
class FunctionDef(AlchemyProxy):
    """Represent a function definition"""

    __tablename__ = "function_def"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
    )
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    name = Column(Text)
    code_hash = Column(Text)
    trial_id = Column(Integer, index=True)
    first_line = Column(Integer)
    last_line = Column(Integer)
    docstring = Column(Text)

    objects = many_ref("function_def", "Object")

    trial = backref_one("trial")  #  Trial.function_defs

    @query_many_property
    def globals(self):
        """Return function definition globals as a SQLAlchemy query"""
        return self.objects.filter(Object.m.type == "GLOBAL")

    @query_many_property
    def arguments(self):
        """Return function definition arguments as a SQLAlchemy query"""
        return self.objects.filter(Object.m.type == "ARGUMENT")

    @query_many_property
    def function_calls(self):
        """Return function definition calls as a SQLAlchemy query"""
        return self.objects.filter(Object.m.type == "FUNCTION_CALL")

    prolog_description = PrologDescription("function_def", (
        PrologTrial("trial_id", link="trial.id"),
        PrologAttribute("id"),
        PrologRepr("name"),
        PrologNullableRepr("code_hash"),
        PrologAttribute("first_line"),
        PrologAttribute("last_line"),
        PrologNullableRepr("docstring"),
    ), description=(
        "informs that in a given trial (*trial_id*),\n"
        "a function *name* was defined\n"
        "with content (*code_hash*)\n"
        "between *first_line* and *last_line*\n"
        "and with a *docstring*."
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
        obj = FunctionDef.load_functiondef(trial_ref, session=session)
        if obj is not None:
            super(FunctionDef, self).__init__(obj)
        else:
            return None

    def show(self, _print=lambda x, offset=0: print(x)):
        """Show object

        Keyword arguments:
        _print -- custom print function (default=print)
        """
        _print("""\
            Name: {f.name}
            Arguments: {arguments}
            Globals: {globals}
            Function calls: {calls}
            Code hash: {f.code_hash}\
            """.format(arguments=", ".join(x.name for x in self.arguments),      # pylint: disable=not-an-iterable
                       globals=", ".join(x.name for x in self.globals),          # pylint: disable=not-an-iterable
                       calls=", ".join(x.name for x in self.function_calls),     # pylint: disable=not-an-iterable
                       f=self))

    def __repr__(self):
        return "FunctionDef({0.trial_id}, {0.id}, {0.name})".format(self)

    @classmethod  # query
    def load_functiondef(cls, trial_ref, session=None):
        """Load functiondef by functiondef reference

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
                {"id": res.id, "name": res.name, "code_hash": res.code_hash, "trial_id": id, "first_line": res.first_line, "last_line": res.last_line, "docstring": res.docstring}
            )
            session.commit()
