# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.
# This file is part of ProvBuild.

"""Module Dependency Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr, PrologNullableRepr

from .. import relational, content, persistence_config
from .base import AlchemyProxy, proxy_class, one, backref_one


@proxy_class
class Dependency(AlchemyProxy):
    """Dependency proxy

    Use it to have different objects with the same primary keys
    Use it also for re-attaching objects to SQLAlchemy (e.g. for cache)
    """

    __tablename__ = "dependency"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "module_id"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["module_id"], ["module.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, nullable=False, index=True)
    module_id = Column(Integer, nullable=False, index=True)

    module = one("Module")

    trial = backref_one("trial")  # Trial.module_dependencies

    prolog_description = PrologDescription("module", (
        PrologTrial("trial_id", link="trial.id"),
        PrologAttribute("id", attr_name="module.id"),
        PrologRepr("name", attr_name="module.name"),
        PrologNullableRepr("version", attr_name="module.version"),
        PrologNullableRepr("path", attr_name="module.path"),
        PrologNullableRepr("code_hash", attr_name="module.code_hash"),
    ), description=(
        "informs that a given trial (*trial_id*)\n"
        "imported the *version* of a module (*name*),\n"
        "with content (*code_hash*) written in *path*."
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
        obj = Dependency.load_dependency(trial_ref, session=session)

        if obj is not None:
            super(Dependency, self).__init__(obj)

    def __repr__(self):
        return "Dependency({0.trial_id}, {0.module})".format(self)

    @classmethod  # query
    def load_dependency(cls, trial_ref, session=None):
        """Load dependency by dependency reference

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
                {"trial_id": id, "module_id": res.module_id}
            )
            session.commit()
