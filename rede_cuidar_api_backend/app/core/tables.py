from typing import Any

from sqlalchemy import MetaData, Table

from app.database import engine


def get_table(table_name: str) -> Table:
    metadata = MetaData()
    return Table(table_name, metadata, autoload_with=engine)


def row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row._mapping)
