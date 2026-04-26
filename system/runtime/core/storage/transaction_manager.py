from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import sqlite3

from .db import connect
from .migrations import apply_migrations


class TransactionManager:
    def __init__(self, db_path: str | None = None, connection_factory=connect) -> None:
        self.db_path = db_path
        self.connection_factory = connection_factory

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = self.connection_factory(self.db_path)
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            apply_migrations(connection)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise
            else:
                connection.commit()
