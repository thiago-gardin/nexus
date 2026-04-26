from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_projection_record, row_to_projection


class ProjectionRepository:
    def create(self, connection: sqlite3.Connection, projection_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_projection_record(projection_data)
        connection.execute(
            """
            INSERT INTO projections (
                projection_id, projection_type, source_refs, payload_refs,
                materialization_format, storage_ref, generated_by,
                generation_scope, freshness_status, created_at, updated_at
            ) VALUES (
                :projection_id, :projection_type, :source_refs, :payload_refs,
                :materialization_format, :storage_ref, :generated_by,
                :generation_scope, :freshness_status, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["projection_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, projection_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                projection_id, projection_type, source_refs, payload_refs,
                materialization_format, storage_ref, generated_by,
                generation_scope, freshness_status, created_at, updated_at
            FROM projections
            WHERE projection_id = ?
            """,
            (projection_id,),
        ).fetchone()
        return row_to_projection(row)

    def list(self, connection: sqlite3.Connection, *, projection_type: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if projection_type is not None:
            clauses.append("projection_type = ?")
            params.append(projection_type)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                projection_id, projection_type, source_refs, payload_refs,
                materialization_format, storage_ref, generated_by,
                generation_scope, freshness_status, created_at, updated_at
            FROM projections
            {where_clause}
            ORDER BY created_at, projection_id
            """,
            params,
        ).fetchall()
        return [row_to_projection(row) for row in rows if row is not None]

    def update(
        self,
        connection: sqlite3.Connection,
        projection_id: str,
        changes: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        current = self.get_by_id(connection, projection_id)
        if current is None:
            return None
        record = prepare_projection_record({**current, **dict(changes), "projection_id": projection_id}, current=current)
        connection.execute(
            """
            UPDATE projections
            SET
                projection_type = :projection_type,
                source_refs = :source_refs,
                payload_refs = :payload_refs,
                materialization_format = :materialization_format,
                storage_ref = :storage_ref,
                generated_by = :generated_by,
                generation_scope = :generation_scope,
                freshness_status = :freshness_status,
                updated_at = :updated_at
            WHERE projection_id = :projection_id
            """,
            record,
        )
        return self.get_by_id(connection, projection_id)
