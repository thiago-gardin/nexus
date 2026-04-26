from __future__ import annotations

import sqlite3
from pathlib import Path

from system.runtime.config import settings

from .migrations import apply_migrations


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    path = Path(db_path).expanduser() if db_path is not None else settings.db_path
    return path.expanduser()


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database(db_path: str | Path | None = None) -> sqlite3.Connection:
    connection = connect(db_path)
    apply_migrations(connection)
    return connection
