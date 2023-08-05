# mssql/pyodbc.py
# Copyright (C) 2005-2020 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

r"""
.. dialect:: mssql+pyodbc
    :name: PyODBC
    :dbapi: pyodbc
    :connectstring: mssql+pyodbc://<username>:<password>@<dsnname>
    :url: http://pypi.python.org/pypi/pyodbc/

Connecting to PyODBC
--------------------

The URL here is to be translated to PyODBC connection strings, as
detailed in `ConnectionStrings <https://code.google.com/p/pyodbc/wiki/ConnectionStrings>`_.

DSN Connections
^^^^^^^^^^^^^^^

A DSN connection in ODBC means that a pre-existing ODBC datasource is
configured on the client machine.   The application then specifies the name
of this datasource, which encompasses details such as the specific ODBC driver
in use as well as the network address of the database.   Assuming a datasource
is configured on the client, a basic DSN-based connection looks like::

    engine = create_engine("mssql+pyodbc://scott:tiger@some_dsn")

Which above, will pass the following connection string to PyODBC::

    dsn=mydsn;UID=user;PWD=pass

If the username and password are omitted, the DSN form will also add
the ``Trusted_Connection=yes`` directive to the ODBC string.

Hostname Connections
^^^^^^^^^^^^^^^^^^^^

Hostname-based connections are also supported by pyodbc.  These are often
easier to use than a DSN and have the additional advantage that the specific
database name to connect towards may be specified locally in the URL, rather
than it being fixed as part of a datasource configuration.

When using a hostname connection, the driver name must also be specified in the
query parameters of the URL.  As these names usually have spaces in them, the
name must be URL encoded which means using plus signs for spaces::

    engine = create_engine("mssql+pyodbc://scott:tiger@myhost:port/databasename?driver=SQL+Server+Native+Client+10.0")

Other keywords interpreted by the Pyodbc dialect to be passed to
``pyodbc.connect()`` in both the DSN and hostname cases include:
``odbc_autotranslate``, ``ansi``, ``unicode_results``, ``autocommit``.
Note that in order for the dialect to recognize these keywords
(including the ``driver`` keyword above) they must be all lowercase.

Pass through exact Pyodbc string
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A PyODBC connection string can also be sent in pyodbc's format directly, as
specified in `ConnectionStrings
<https://code.google.com/p/pyodbc/wiki/ConnectionStrings>`_ into the driver
using the parameter ``odbc_connect``.  The delimeters must be URL encoded, as
illustrated below using ``urllib.parse.quote_plus``::

    import urllib
    params = urllib.parse.quote_plus("DRIVER={SQL Server Native Client 10.0};SERVER=dagger;DATABASE=test;UID=user;PWD=password")

    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


Driver / Unicode Support
-------------------------

PyODBC works best with Microsoft ODBC drivers, particularly in the area
of Unicode support on both Python 2 and Python 3.

Using the FreeTDS ODBC drivers on Linux or OSX with PyODBC is **not**
recommended; there have been historically many Unicode-related issues
in this area, including before Microsoft offered ODBC drivers for Linux
and OSX.   Now that Microsoft offers drivers for all platforms, for
PyODBC support these are recommended.  FreeTDS remains relevant for
non-ODBC drivers such as pymssql where it works very well.


Rowcount Support
----------------

Pyodbc only has partial support for rowcount.  See the notes at
:ref:`mssql_rowcount_versioning` for important notes when using ORM
versioning.

.. _mssql_pyodbc_fastexecutemany:

Fast Executemany Mode
---------------------

The Pyodbc driver has added support for a "fast executemany" mode of execution
which greatly reduces round trips for a DBAPI ``executemany()`` call when using
Microsoft ODBC drivers.  The feature is enabled by setting the flag
``.fast_executemany`` on the DBAPI cursor when an executemany call is to be
used.   The SQLAlchemy pyodbc SQL Server dialect supports setting this flag
automatically when the ``.fast_executemany`` flag is passed to
:func:`.create_engine`; note that the ODBC driver must be the Microsoft driver
in order to use this flag::

    engine = create_engine(
        "mssql+pyodbc://scott:tiger@mssql2017:1433/test?driver=ODBC+Driver+13+for+SQL+Server",
        fast_executemany=True)

.. versionadded:: 1.3

.. seealso::

    `fast executemany <https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API#fast_executemany>`_
    - on github


"""  # noqa

import datetime
import decimal
import re
import struct

from .base import BINARY
from .base import DATETIMEOFFSET
from .base import MSDialect
from .base import MSExecutionContext
from .base import VARBINARY
from ... import exc
from ... import types as sqltypes
from ... import util
from ...connectors.pyodbc import PyODBCConnector


class _ms_numeric_pyodbc(object):

    """Turns Decimals with adjusted() < 0 or > 7 into strings.

    The routines here are needed for older pyodbc versions
    as well as current mxODBC versions.

    """

    def bind_processor(self, dialect):

        super_process = super(_ms_numeric_pyodbc, self).bind_processor(dialect)

        if not dialect._need_decimal_fix:
            return super_process

        def process(value):
            if self.asdecimal and isinstance(value, decimal.Decimal):
                adjusted = value.adjusted()
                if adjusted < 0:
                    return self._small_dec_to_string(value)
                elif adjusted > 7:
                    return self._large_dec_to_string(value)

            if super_process:
                return super_process(value)
            else:
                return value

        return process

    # these routines needed for older versions of pyodbc.
    # as of 2.1.8 this logic is integrated.

    def _small_dec_to_string(self, value):
        return "%s0.%s%s" % (
            (value < 0 and "-" or ""),
            "0" * (abs(value.adjusted()) - 1),
            "".join([str(nint) for nint in value.as_tuple()[1]]),
        )

    def _large_dec_to_string(self, value):
        _int = value.as_tuple()[1]
        if "E" in str(value):
            result = "%s%s%s" % (
                (value < 0 and "-" or ""),
                "".join([str(s) for s in _int]),
                "0" * (value.adjusted() - (len(_int) - 1)),
            )
        else:
            if (len(_int) - 1) > value.adjusted():
                result = "%s%s.%s" % (
                    (value < 0 and "-" or ""),
                    "".join([str(s) for s in _int][0 : value.adjusted() + 1]),
                    "".join([str(s) for s in _int][value.adjusted() + 1 :]),
                )
            else:
                result = "%s%s" % (
                    (value < 0 and "-" or ""),
                    "".join([str(s) for s in _int][0 : value.adjusted() + 1]),
                )
        return result


class _MSNumeric_pyodbc(_ms_numeric_pyodbc, sqltypes.Numeric):
    pass


class _MSFloat_pyodbc(_ms_numeric_pyodbc, sqltypes.Float):
    pass


class _ms_binary_pyodbc(object):
    """Wraps binary values in dialect-specific Binary wrapper.
    If the value is null, return a pyodbc-specific BinaryNull
    object to prevent pyODBC [and FreeTDS] from defaulting binary
    NULL types to SQLWCHAR and causing implicit conversion errors.
    """

    def bind_processor(self, dialect):
        if dialect.dbapi is None:
            return None

        DBAPIBinary = dialect.dbapi.Binary

        def process(value):
            if value is not None:
                return DBAPIBinary(value)
            else:
                # pyodbc-specific
                return dialect.dbapi.BinaryNull

        return process


class _ODBCDateTimeOffset(DATETIMEOFFSET):
    def bind_processor(self, dialect):
        def process(value):
            """Convert to string format required by T-SQL."""
            dto_string = value.strftime("%Y-%m-%d %H:%M:%S.%f %z")
            # offset needs a colon, e.g., -0700 -> -07:00
            return dto_string[:30] + ":" + dto_string[30:]

        return process


class _VARBINARY_pyodbc(_ms_binary_pyodbc, VARBINARY):
    pass


class _BINARY_pyodbc(_ms_binary_pyodbc, BINARY):
    pass


class MSExecutionContext_pyodbc(MSExecutionContext):
    _embedded_scope_identity = False

    def pre_exec(self):
        """where appropriate, issue "select scope_identity()" in the same
        statement.

        Background on why "scope_identity()" is preferable to "@@identity":
        http://msdn.microsoft.com/en-us/library/ms190315.aspx

        Background on why we attempt to embed "scope_identity()" into the same
        statement as the INSERT:
        http://code.google.com/p/pyodbc/wiki/FAQs#How_do_I_retrieve_autogenerated/identity_values?

        """

        super(MSExecutionContext_pyodbc, self).pre_exec()

        # don't embed the scope_identity select into an
        # "INSERT .. DEFAULT VALUES"
        if (
            self._select_lastrowid
            and self.dialect.use_scope_identity
            and len(self.parameters[0])
        ):
            self._embedded_scope_identity = True

            self.statement += "; select scope_identity()"

    def post_exec(self):
        if self._embedded_scope_identity:
            # Fetch the last inserted id from the manipulated statement
            # We may have to skip over a number of result sets with
            # no data (due to triggers, etc.)
            while True:
                try:
                    # fetchall() ensures the cursor is consumed
                    # without closing it (FreeTDS particularly)
                    row = self.cursor.fetchall()[0]
                    break
                except self.dialect.dbapi.Error:
                    # no way around this - nextset() consumes the previous set
                    # so we need to just keep flipping
                    self.cursor.nextset()

            self._lastrowid = int(row[0])
        else:
            super(MSExecutionContext_pyodbc, self).post_exec()


class MSDialect_pyodbc(PyODBCConnector, MSDialect):

    execution_ctx_cls = MSExecutionContext_pyodbc

    colspecs = util.update_copy(
        MSDialect.colspecs,
        {
            sqltypes.Numeric: _MSNumeric_pyodbc,
            sqltypes.Float: _MSFloat_pyodbc,
            BINARY: _BINARY_pyodbc,
            DATETIMEOFFSET: _ODBCDateTimeOffset,
            # SQL Server dialect has a VARBINARY that is just to support
            # "deprecate_large_types" w/ VARBINARY(max), but also we must
            # handle the usual SQL standard VARBINARY
            VARBINARY: _VARBINARY_pyodbc,
            sqltypes.VARBINARY: _VARBINARY_pyodbc,
            sqltypes.LargeBinary: _VARBINARY_pyodbc,
        },
    )

    def __init__(
        self, description_encoding=None, fast_executemany=False, **params
    ):
        if "description_encoding" in params:
            self.description_encoding = params.pop("description_encoding")
        super(MSDialect_pyodbc, self).__init__(**params)
        self.use_scope_identity = (
            self.use_scope_identity
            and self.dbapi
            and hasattr(self.dbapi.Cursor, "nextset")
        )
        self._need_decimal_fix = self.dbapi and self._dbapi_version() < (
            2,
            1,
            8,
        )
        self.fast_executemany = fast_executemany

    def _get_server_version_info(self, connection):
        try:
            # "Version of the instance of SQL Server, in the form
            # of 'major.minor.build.revision'"
            raw = connection.scalar(
                "SELECT CAST(SERVERPROPERTY('ProductVersion') AS VARCHAR)"
            )
        except exc.DBAPIError:
            # SQL Server docs indicate this function isn't present prior to
            # 2008.  Before we had the VARCHAR cast above, pyodbc would also
            # fail on this query.
            return super(MSDialect_pyodbc, self)._get_server_version_info(
                connection, allow_chars=False
            )
        else:
            version = []
            r = re.compile(r"[.\-]")
            for n in r.split(raw):
                try:
                    version.append(int(n))
                except ValueError:
                    pass
            return tuple(version)

    def on_connect(self):
        super_ = super(MSDialect_pyodbc, self).on_connect()

        def on_connect(conn):
            if super_ is not None:
                super_(conn)

            self._setup_timestampoffset_type(conn)

        return on_connect

    def _setup_timestampoffset_type(self, connection):
        # output converter function for datetimeoffset
        def _handle_datetimeoffset(dto_value):
            tup = struct.unpack("<6hI2h", dto_value)
            return datetime.datetime(
                tup[0],
                tup[1],
                tup[2],
                tup[3],
                tup[4],
                tup[5],
                tup[6] // 1000,
                util.timezone(
                    datetime.timedelta(hours=tup[7], minutes=tup[8])
                ),
            )

        odbc_SQL_SS_TIMESTAMPOFFSET = -155  # as defined in SQLNCLI.h
        connection.add_output_converter(
            odbc_SQL_SS_TIMESTAMPOFFSET, _handle_datetimeoffset
        )

    def do_executemany(self, cursor, statement, parameters, context=None):
        if self.fast_executemany:
            cursor.fast_executemany = True
        super(MSDialect_pyodbc, self).do_executemany(
            cursor, statement, parameters, context=context
        )

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.Error):
            for code in (
                "08S01",
                "01002",
                "08003",
                "08007",
                "08S02",
                "08001",
                "HYT00",
                "HY010",
                "10054",
            ):
                if code in str(e):
                    return True
        return super(MSDialect_pyodbc, self).is_disconnect(
            e, connection, cursor
        )


dialect = MSDialect_pyodbc
