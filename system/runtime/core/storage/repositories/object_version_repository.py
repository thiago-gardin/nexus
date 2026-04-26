from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_object_version_record, row_to_object_version


class ObjectVersionRepository:
    def create(self, connection: sqlite3.Connection, version_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_object_version_record(version_data)
        connection.execute(
            """
            INSERT INTO object_versions (
                version_id, object_type, object_id, version_number,
                serialized_state_ref, created_at, created_by
            ) VALUES (
                :version_id, :object_type, :object_id, :version_number,
                :serialized_state_ref, :created_at, :created_by
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["version_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, version_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                version_id, object_type, object_id, version_number,
                serialized_state_ref, created_at, created_by
            FROM object_versions
            WHERE version_id = ?
            """,
            (version_id,),
        ).fetchone()
        return row_to_object_version(row)

    def list_for_object(self, connection: sqlite3.Connection, object_type: str, object_id: str) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT
                version_id, object_type, object_id, version_number,
                serialized_state_ref, created_at, created_by
            FROM object_versions
            WHERE object_type = ? AND object_id = ?
            ORDER BY version_number, created_at
            """,
            (object_type, object_id),
        ).fetchall()
        return [row_to_object_version(row) for row in rows if row is not None]
