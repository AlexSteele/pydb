from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, Optional, Protocol, Sequence, Tuple

from .error import SchemaError
from .index import Index

# TODO: Move public schema stuff to schema.py?


class DataType(Enum):
    INT = "INT"
    STRING = "STRING"


class ColumnAttr(Enum):
    AUTO_INCREMENT = "AUTO_INCREMENT"
    DEFAULT = "DEFAULT"
    FOREIGN_KEY = "FOREIGN_KEY"
    NOT_NULL = "NOT_NULL"
    PRIMARY_KEY = "PRIMARY_KEY"
    UNIQUE = "UNIQUE"

@dataclass(init=False)
class Column:
    name: str
    dtype: DataType
    attrs: Dict[ColumnAttr, Any]

    def __init__(self, name, dtype, *attrs, kwattrs={}):
        self.name = name
        self.dtype = dtype
        self.attrs = {
            **{attr: True for attr in attrs},
            **kwattrs,
        }

    def hasattr(self, attr):
        return attr in self.attrs


def check_column(col: Column):
    if not col.name:
        raise SchemaError("column name must not be empty")


@dataclass(init=False)
class Schema:
    name: str
    columns: Sequence[Column]

    def __init__(self, name, *columns):
        self.name = name
        self.columns = columns

    def columnid(self, name):
        return next(i for i, c in enumerate(self.columns) if c.name == name)

    def columnids(self, *names) -> Sequence[int]:
        return tuple(map(self.columnid, names) if names else range(len(self.columns)))

    def column_names(self):
        return tuple(c.name for c in self.columns)


def check_schema(schema: Schema):
    if not schema.name:
        raise SchemaError("name must not be empty")
    if not schema.columns:
        raise SchemaError("columns must not be empty")
    if len(set(schema.column_names())) != len(schema.column_names()):
        raise SchemaError("duplicate column name")
    for col in schema.columns:
        check_column(col)


class ITable(Protocol):
    def name(self) -> str:
        return self.schema().name

    def schema(self) -> Schema:
        pass

    def insert(self, row: Tuple) -> Tuple[int, Tuple]:
        pass

    def get(self, rowid: int) -> Optional[Tuple]:
        pass

    def rows(self) -> Iterator[Tuple]:
        pass

    def indexes(self, column: Optional[str] = None) -> Sequence[Index]:
        pass

    def __str__(self):
        return f"{type(self).__name__}(name={self.name()})"
