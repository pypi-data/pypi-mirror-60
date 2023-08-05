# ext/compiler.py
# Copyright (C) 2005-2020 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

r"""Provides an API for creation of custom ClauseElements and compilers.

Synopsis
========

Usage involves the creation of one or more
:class:`~sqlalchemy.sql.expression.ClauseElement` subclasses and one or
more callables defining its compilation::

    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.sql.expression import ColumnClause

    class MyColumn(ColumnClause):
        pass

    @compiles(MyColumn)
    def compile_mycolumn(element, compiler, **kw):
        return "[%s]" % element.name

Above, ``MyColumn`` extends :class:`~sqlalchemy.sql.expression.ColumnClause`,
the base expression element for named column objects. The ``compiles``
decorator registers itself with the ``MyColumn`` class so that it is invoked
when the object is compiled to a string::

    from sqlalchemy import select

    s = select([MyColumn('x'), MyColumn('y')])
    print str(s)

Produces::

    SELECT [x], [y]

Dialect-specific compilation rules
==================================

Compilers can also be made dialect-specific. The appropriate compiler will be
invoked for the dialect in use::

    from sqlalchemy.schema import DDLElement

    class AlterColumn(DDLElement):

        def __init__(self, column, cmd):
            self.column = column
            self.cmd = cmd

    @compiles(AlterColumn)
    def visit_alter_column(element, compiler, **kw):
        return "ALTER COLUMN %s ..." % element.column.name

    @compiles(AlterColumn, 'postgresql')
    def visit_alter_column(element, compiler, **kw):
        return "ALTER TABLE %s ALTER COLUMN %s ..." % (element.table.name,
                                                       element.column.name)

The second ``visit_alter_table`` will be invoked when any ``postgresql``
dialect is used.

Compiling sub-elements of a custom expression construct
=======================================================

The ``compiler`` argument is the
:class:`~sqlalchemy.engine.interfaces.Compiled` object in use. This object
can be inspected for any information about the in-progress compilation,
including ``compiler.dialect``, ``compiler.statement`` etc. The
:class:`~sqlalchemy.sql.compiler.SQLCompiler` and
:class:`~sqlalchemy.sql.compiler.DDLCompiler` both include a ``process()``
method which can be used for compilation of embedded attributes::

    from sqlalchemy.sql.expression import Executable, ClauseElement

    class InsertFromSelect(Executable, ClauseElement):
        def __init__(self, table, select):
            self.table = table
            self.select = select

    @compiles(InsertFromSelect)
    def visit_insert_from_select(element, compiler, **kw):
        return "INSERT INTO %s (%s)" % (
            compiler.process(element.table, asfrom=True, **kw),
            compiler.process(element.select, **kw)
        )

    insert = InsertFromSelect(t1, select([t1]).where(t1.c.x>5))
    print insert

Produces::

    "INSERT INTO mytable (SELECT mytable.x, mytable.y, mytable.z
                          FROM mytable WHERE mytable.x > :x_1)"

.. note::

    The above ``InsertFromSelect`` construct is only an example, this actual
    functionality is already available using the
    :meth:`.Insert.from_select` method.

.. note::

   The above ``InsertFromSelect`` construct probably wants to have "autocommit"
   enabled.  See :ref:`enabling_compiled_autocommit` for this step.

Cross Compiling between SQL and DDL compilers
---------------------------------------------

SQL and DDL constructs are each compiled using different base compilers -
``SQLCompiler`` and ``DDLCompiler``.   A common need is to access the
compilation rules of SQL expressions from within a DDL expression. The
``DDLCompiler`` includes an accessor ``sql_compiler`` for this reason, such as
below where we generate a CHECK constraint that embeds a SQL expression::

    @compiles(MyConstraint)
    def compile_my_constraint(constraint, ddlcompiler, **kw):
        kw['literal_binds'] = True
        return "CONSTRAINT %s CHECK (%s)" % (
            constraint.name,
            ddlcompiler.sql_compiler.process(
                constraint.expression, **kw)
        )

Above, we add an additional flag to the process step as called by
:meth:`.SQLCompiler.process`, which is the ``literal_binds`` flag.  This
indicates that any SQL expression which refers to a :class:`.BindParameter`
object or other "literal" object such as those which refer to strings or
integers should be rendered **in-place**, rather than being referred to as
a bound parameter;  when emitting DDL, bound parameters are typically not
supported.


.. _enabling_compiled_autocommit:

Enabling Autocommit on a Construct
==================================

Recall from the section :ref:`autocommit` that the :class:`.Engine`, when
asked to execute a construct in the absence of a user-defined transaction,
detects if the given construct represents DML or DDL, that is, a data
modification or data definition statement, which requires (or may require,
in the case of DDL) that the transaction generated by the DBAPI be committed
(recall that DBAPI always has a transaction going on regardless of what
SQLAlchemy does).   Checking for this is actually accomplished by checking for
the "autocommit" execution option on the construct.    When building a
construct like an INSERT derivation, a new DDL type, or perhaps a stored
procedure that alters data, the "autocommit" option needs to be set in order
for the statement to function with "connectionless" execution
(as described in :ref:`dbengine_implicit`).

Currently a quick way to do this is to subclass :class:`.Executable`, then
add the "autocommit" flag to the ``_execution_options`` dictionary (note this
is a "frozen" dictionary which supplies a generative ``union()`` method)::

    from sqlalchemy.sql.expression import Executable, ClauseElement

    class MyInsertThing(Executable, ClauseElement):
        _execution_options = \
            Executable._execution_options.union({'autocommit': True})

More succinctly, if the construct is truly similar to an INSERT, UPDATE, or
DELETE, :class:`.UpdateBase` can be used, which already is a subclass
of :class:`.Executable`, :class:`.ClauseElement` and includes the
``autocommit`` flag::

    from sqlalchemy.sql.expression import UpdateBase

    class MyInsertThing(UpdateBase):
        def __init__(self, ...):
            ...




DDL elements that subclass :class:`.DDLElement` already have the
"autocommit" flag turned on.




Changing the default compilation of existing constructs
=======================================================

The compiler extension applies just as well to the existing constructs.  When
overriding the compilation of a built in SQL construct, the @compiles
decorator is invoked upon the appropriate class (be sure to use the class,
i.e. ``Insert`` or ``Select``, instead of the creation function such
as ``insert()`` or ``select()``).

Within the new compilation function, to get at the "original" compilation
routine, use the appropriate visit_XXX method - this
because compiler.process() will call upon the overriding routine and cause
an endless loop.   Such as, to add "prefix" to all insert statements::

    from sqlalchemy.sql.expression import Insert

    @compiles(Insert)
    def prefix_inserts(insert, compiler, **kw):
        return compiler.visit_insert(insert.prefix_with("some prefix"), **kw)

The above compiler will prefix all INSERT statements with "some prefix" when
compiled.

.. _type_compilation_extension:

Changing Compilation of Types
=============================

``compiler`` works for types, too, such as below where we implement the
MS-SQL specific 'max' keyword for ``String``/``VARCHAR``::

    @compiles(String, 'mssql')
    @compiles(VARCHAR, 'mssql')
    def compile_varchar(element, compiler, **kw):
        if element.length == 'max':
            return "VARCHAR('max')"
        else:
            return compiler.visit_VARCHAR(element, **kw)

    foo = Table('foo', metadata,
        Column('data', VARCHAR('max'))
    )

Subclassing Guidelines
======================

A big part of using the compiler extension is subclassing SQLAlchemy
expression constructs. To make this easier, the expression and
schema packages feature a set of "bases" intended for common tasks.
A synopsis is as follows:

* :class:`~sqlalchemy.sql.expression.ClauseElement` - This is the root
  expression class. Any SQL expression can be derived from this base, and is
  probably the best choice for longer constructs such as specialized INSERT
  statements.

* :class:`~sqlalchemy.sql.expression.ColumnElement` - The root of all
  "column-like" elements. Anything that you'd place in the "columns" clause of
  a SELECT statement (as well as order by and group by) can derive from this -
  the object will automatically have Python "comparison" behavior.

  :class:`~sqlalchemy.sql.expression.ColumnElement` classes want to have a
  ``type`` member which is expression's return type.  This can be established
  at the instance level in the constructor, or at the class level if its
  generally constant::

      class timestamp(ColumnElement):
          type = TIMESTAMP()

* :class:`~sqlalchemy.sql.functions.FunctionElement` - This is a hybrid of a
  ``ColumnElement`` and a "from clause" like object, and represents a SQL
  function or stored procedure type of call. Since most databases support
  statements along the line of "SELECT FROM <some function>"
  ``FunctionElement`` adds in the ability to be used in the FROM clause of a
  ``select()`` construct::

      from sqlalchemy.sql.expression import FunctionElement

      class coalesce(FunctionElement):
          name = 'coalesce'

      @compiles(coalesce)
      def compile(element, compiler, **kw):
          return "coalesce(%s)" % compiler.process(element.clauses, **kw)

      @compiles(coalesce, 'oracle')
      def compile(element, compiler, **kw):
          if len(element.clauses) > 2:
              raise TypeError("coalesce only supports two arguments on Oracle")
          return "nvl(%s)" % compiler.process(element.clauses, **kw)

* :class:`~sqlalchemy.schema.DDLElement` - The root of all DDL expressions,
  like CREATE TABLE, ALTER TABLE, etc. Compilation of ``DDLElement``
  subclasses is issued by a ``DDLCompiler`` instead of a ``SQLCompiler``.
  ``DDLElement`` also features ``Table`` and ``MetaData`` event hooks via the
  ``execute_at()`` method, allowing the construct to be invoked during CREATE
  TABLE and DROP TABLE sequences.

* :class:`~sqlalchemy.sql.expression.Executable` - This is a mixin which
  should be used with any expression class that represents a "standalone"
  SQL statement that can be passed directly to an ``execute()`` method.  It
  is already implicit within ``DDLElement`` and ``FunctionElement``.

Further Examples
================

"UTC timestamp" function
-------------------------

A function that works like "CURRENT_TIMESTAMP" except applies the
appropriate conversions so that the time is in UTC time.   Timestamps are best
stored in relational databases as UTC, without time zones.   UTC so that your
database doesn't think time has gone backwards in the hour when daylight
savings ends, without timezones because timezones are like character
encodings - they're best applied only at the endpoints of an application
(i.e. convert to UTC upon user input, re-apply desired timezone upon display).

For PostgreSQL and Microsoft SQL Server::

    from sqlalchemy.sql import expression
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.types import DateTime

    class utcnow(expression.FunctionElement):
        type = DateTime()

    @compiles(utcnow, 'postgresql')
    def pg_utcnow(element, compiler, **kw):
        return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

    @compiles(utcnow, 'mssql')
    def ms_utcnow(element, compiler, **kw):
        return "GETUTCDATE()"

Example usage::

    from sqlalchemy import (
                Table, Column, Integer, String, DateTime, MetaData
            )
    metadata = MetaData()
    event = Table("event", metadata,
        Column("id", Integer, primary_key=True),
        Column("description", String(50), nullable=False),
        Column("timestamp", DateTime, server_default=utcnow())
    )

"GREATEST" function
-------------------

The "GREATEST" function is given any number of arguments and returns the one
that is of the highest value - its equivalent to Python's ``max``
function.  A SQL standard version versus a CASE based version which only
accommodates two arguments::

    from sqlalchemy.sql import expression, case
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.types import Numeric

    class greatest(expression.FunctionElement):
        type = Numeric()
        name = 'greatest'

    @compiles(greatest)
    def default_greatest(element, compiler, **kw):
        return compiler.visit_function(element)

    @compiles(greatest, 'sqlite')
    @compiles(greatest, 'mssql')
    @compiles(greatest, 'oracle')
    def case_greatest(element, compiler, **kw):
        arg1, arg2 = list(element.clauses)
        return compiler.process(case([(arg1 > arg2, arg1)], else_=arg2), **kw)

Example usage::

    Session.query(Account).\
            filter(
                greatest(
                    Account.checking_balance,
                    Account.savings_balance) > 10000
            )

"false" expression
------------------

Render a "false" constant expression, rendering as "0" on platforms that
don't have a "false" constant::

    from sqlalchemy.sql import expression
    from sqlalchemy.ext.compiler import compiles

    class sql_false(expression.ColumnElement):
        pass

    @compiles(sql_false)
    def default_false(element, compiler, **kw):
        return "false"

    @compiles(sql_false, 'mssql')
    @compiles(sql_false, 'mysql')
    @compiles(sql_false, 'oracle')
    def int_false(element, compiler, **kw):
        return "0"

Example usage::

    from sqlalchemy import select, union_all

    exp = union_all(
        select([users.c.name, sql_false().label("enrolled")]),
        select([customers.c.name, customers.c.enrolled])
    )

"""
from .. import exc
from ..sql import visitors


def compiles(class_, *specs):
    """Register a function as a compiler for a
    given :class:`.ClauseElement` type."""

    def decorate(fn):
        # get an existing @compiles handler
        existing = class_.__dict__.get("_compiler_dispatcher", None)

        # get the original handler.  All ClauseElement classes have one
        # of these, but some TypeEngine classes will not.
        existing_dispatch = getattr(class_, "_compiler_dispatch", None)

        if not existing:
            existing = _dispatcher()

            if existing_dispatch:

                def _wrap_existing_dispatch(element, compiler, **kw):
                    try:
                        return existing_dispatch(element, compiler, **kw)
                    except exc.UnsupportedCompilationError:
                        raise exc.CompileError(
                            "%s construct has no default "
                            "compilation handler." % type(element)
                        )

                existing.specs["default"] = _wrap_existing_dispatch

            # TODO: why is the lambda needed ?
            setattr(
                class_,
                "_compiler_dispatch",
                lambda *arg, **kw: existing(*arg, **kw),
            )
            setattr(class_, "_compiler_dispatcher", existing)

        if specs:
            for s in specs:
                existing.specs[s] = fn

        else:
            existing.specs["default"] = fn
        return fn

    return decorate


def deregister(class_):
    """Remove all custom compilers associated with a given
    :class:`.ClauseElement` type."""

    if hasattr(class_, "_compiler_dispatcher"):
        # regenerate default _compiler_dispatch
        visitors._generate_dispatch(class_)
        # remove custom directive
        del class_._compiler_dispatcher


class _dispatcher(object):
    def __init__(self):
        self.specs = {}

    def __call__(self, element, compiler, **kw):
        # TODO: yes, this could also switch off of DBAPI in use.
        fn = self.specs.get(compiler.dialect.name, None)
        if not fn:
            try:
                fn = self.specs["default"]
            except KeyError:
                raise exc.CompileError(
                    "%s construct has no default "
                    "compilation handler." % type(element)
                )

        return fn(element, compiler, **kw)
