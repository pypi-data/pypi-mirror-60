import re

from sqlalchemy import __version__
from sqlalchemy import schema
from sqlalchemy import sql
from sqlalchemy import types as sqltypes
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.sql.expression import _BindParamClause
from sqlalchemy.sql.expression import _TextClause as TextClause
from sqlalchemy.sql.visitors import traverse

from . import compat


def _safe_int(value):
    try:
        return int(value)
    except:
        return value


_vers = tuple(
    [_safe_int(x) for x in re.findall(r"(\d+|[abc]\d)", __version__)]
)
sqla_110 = _vers >= (1, 1, 0)
sqla_1115 = _vers >= (1, 1, 15)
sqla_120 = _vers >= (1, 2, 0)
sqla_1216 = _vers >= (1, 2, 16)
sqla_13 = _vers >= (1, 3)
sqla_14 = _vers >= (1, 4)
try:
    from sqlalchemy import Computed  # noqa

    has_computed = True
except ImportError:
    has_computed = False

AUTOINCREMENT_DEFAULT = "auto"


def _server_default_is_computed(column):
    if not has_computed:
        return False
    else:
        return isinstance(column.computed, Computed)


def _table_for_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        return constraint.parent
    else:
        return constraint.table


def _columns_for_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        return [fk.parent for fk in constraint.elements]
    elif isinstance(constraint, CheckConstraint):
        return _find_columns(constraint.sqltext)
    else:
        return list(constraint.columns)


def _fk_spec(constraint):
    source_columns = [
        constraint.columns[key].name for key in constraint.column_keys
    ]

    source_table = constraint.parent.name
    source_schema = constraint.parent.schema
    target_schema = constraint.elements[0].column.table.schema
    target_table = constraint.elements[0].column.table.name
    target_columns = [element.column.name for element in constraint.elements]
    ondelete = constraint.ondelete
    onupdate = constraint.onupdate
    deferrable = constraint.deferrable
    initially = constraint.initially
    return (
        source_schema,
        source_table,
        source_columns,
        target_schema,
        target_table,
        target_columns,
        onupdate,
        ondelete,
        deferrable,
        initially,
    )


def _fk_is_self_referential(constraint):
    spec = constraint.elements[0]._get_colspec()
    tokens = spec.split(".")
    tokens.pop(-1)  # colname
    tablekey = ".".join(tokens)
    return tablekey == constraint.parent.key


def _is_type_bound(constraint):
    # this deals with SQLAlchemy #3260, don't copy CHECK constraints
    # that will be generated by the type.
    # new feature added for #3260
    return constraint._type_bound


def _find_columns(clause):
    """locate Column objects within the given expression."""

    cols = set()
    traverse(clause, {}, {"column": cols.add})
    return cols


def _remove_column_from_collection(collection, column):
    """remove a column from a ColumnCollection."""

    # workaround for older SQLAlchemy, remove the
    # same object that's present
    to_remove = collection[column.key]
    collection.remove(to_remove)


def _textual_index_column(table, text_):
    """a workaround for the Index construct's severe lack of flexibility"""
    if isinstance(text_, compat.string_types):
        c = Column(text_, sqltypes.NULLTYPE)
        table.append_column(c)
        return c
    elif isinstance(text_, TextClause):
        return _textual_index_element(table, text_)
    else:
        raise ValueError("String or text() construct expected")


class _textual_index_element(sql.ColumnElement):
    """Wrap around a sqlalchemy text() construct in such a way that
    we appear like a column-oriented SQL expression to an Index
    construct.

    The issue here is that currently the Postgresql dialect, the biggest
    recipient of functional indexes, keys all the index expressions to
    the corresponding column expressions when rendering CREATE INDEX,
    so the Index we create here needs to have a .columns collection that
    is the same length as the .expressions collection.  Ultimately
    SQLAlchemy should support text() expressions in indexes.

    See SQLAlchemy issue 3174.

    """

    __visit_name__ = "_textual_idx_element"

    def __init__(self, table, text):
        self.table = table
        self.text = text
        self.key = text.text
        self.fake_column = schema.Column(self.text.text, sqltypes.NULLTYPE)
        table.append_column(self.fake_column)

    def get_children(self):
        return [self.fake_column]


@compiles(_textual_index_element)
def _render_textual_index_column(element, compiler, **kw):
    return compiler.process(element.text, **kw)


class _literal_bindparam(_BindParamClause):
    pass


@compiles(_literal_bindparam)
def _render_literal_bindparam(element, compiler, **kw):
    return compiler.render_literal_bindparam(element, **kw)


def _get_index_expressions(idx):
    return list(idx.expressions)


def _get_index_column_names(idx):
    return [getattr(exp, "name", None) for exp in _get_index_expressions(idx)]


def _column_kwargs(col):
    if sqla_13:
        return col.kwargs
    else:
        return {}


def _get_index_final_name(dialect, idx):
    if sqla_14:
        return _get_constraint_final_name(idx, dialect)

    # prior to SQLAlchemy 1.4, work around quoting logic to get at the
    # final compiled name without quotes.
    if hasattr(idx.name, "quote"):
        # might be quoted_name, might be truncated_name, keep it the
        # same
        quoted_name_cls = type(idx.name)
        new_name = quoted_name_cls(str(idx.name), quote=False)
        idx = schema.Index(name=new_name)
    return dialect.ddl_compiler(dialect, None)._prepared_index_name(idx)


def _get_constraint_final_name(constraint, dialect):
    if sqla_14:
        if constraint.name is None:
            return None

        # for SQLAlchemy 1.4 we would like to have the option to expand
        # the use of "deferred" names for constraints as well as to have
        # some flexibility with "None" name and similar; make use of new
        # SQLAlchemy API to return what would be the final compiled form of
        # the name for this dialect.
        return dialect.identifier_preparer.format_constraint(
            constraint, _alembic_quote=False
        )
    else:
        return constraint.name


def _constraint_is_named(constraint, dialect):
    if sqla_14:
        if constraint.name is None:
            return False
        name = dialect.identifier_preparer.format_constraint(
            constraint, _alembic_quote=False
        )
        return name is not None
    else:
        return constraint.name is not None


def _dialect_supports_comments(dialect):
    if sqla_120:
        return dialect.supports_comments
    else:
        return False


def _comment_attribute(obj):
    """return the .comment attribute from a Table or Column"""

    if sqla_120:
        return obj.comment
    else:
        return None


def _is_mariadb(mysql_dialect):
    return (
        mysql_dialect.server_version_info
        and "MariaDB" in mysql_dialect.server_version_info
    )


def _mariadb_normalized_version_info(mysql_dialect):
    if len(mysql_dialect.server_version_info) > 5:
        return mysql_dialect.server_version_info[3:]
    else:
        return mysql_dialect.server_version_info


if sqla_14:
    from sqlalchemy import create_mock_engine
else:
    from sqlalchemy import create_engine

    def create_mock_engine(url, executor):
        return create_engine(
            "postgresql://", strategy="mock", executor=executor
        )
