"""Add missing SQLite columns/indexes so local DBs stay usable after model changes."""
from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.db.base_class import Base

logger = logging.getLogger(__name__)


def sync_sqlite_schema(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                table.create(bind=conn)
                continue
            existing_cols = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_cols:
                    continue
                col_type = column.type.compile(dialect=engine.dialect)
                nullable = "" if column.nullable else ""
                default = ""
                if column.default is not None and column.default.arg is not None and not callable(column.default.arg):
                    value = column.default.arg
                    if isinstance(value, str):
                        default = f" DEFAULT '{value}'"
                    elif isinstance(value, bool):
                        default = f" DEFAULT {1 if value else 0}"
                    elif isinstance(value, (int, float)):
                        default = f" DEFAULT {value}"
                stmt = f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type}{nullable}{default}'
                logger.info("SQLite schema sync: %s", stmt)
                conn.execute(text(stmt))
