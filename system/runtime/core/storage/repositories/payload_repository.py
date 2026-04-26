from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_payload_record, row_to_payload


class PayloadRepository:
    def create(self, connection: sqlite3.Connection, payload_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_payload_record(payload_data)
        connection.execute(
            """
            INSERT INTO payloads (
                payload_id, payload_type, owner_object_type, owner_object_id,
                storage_ref, format, checksum, editability, canonical_flag,
                created_at, updated_at, version
            ) VALUES (
                :payload_id, :payload_type, :owner_object_type, :owner_object_id,
                :storage_ref, :format, :checksum, :editability, :canonical_flag,
                :created_at, :updated_at, :version
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["payload_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, payload_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                payload_id, payload_type, owner_object_type, owner_object_id,
                storage_ref, format, checksum, editability, canonical_flag,
                created_at, updated_at, version
            FROM payloads
            WHERE payload_id = ?
            """,
            (payload_id,),
        ).fetchone()
        return row_to_payload(row)

    def list(
        self,
        connection: sqlite3.Connection,
        *,
        owner_object_type: str | None = None,
        owner_object_id: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if owner_object_type is not None:
            clauses.append("owner_object_type = ?")
            params.append(owner_object_type)
        if owner_object_id is not None:
            clauses.append("owner_object_id = ?")
            params.append(owner_object_id)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                payload_id, payload_type, owner_object_type, owner_object_id,
                storage_ref, format, checksum, editability, canonical_flag,
                created_at, updated_at, version
            FROM payloads
            {where_clause}
            ORDER BY created_at, payload_id
            """,
            params,
        ).fetchall()
        return [row_to_payload(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, payload_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, payload_id)
        if current is None:
            return None
        record = prepare_payload_record({**current, **dict(changes), "payload_id": payload_id}, current=current)
        connection.execute(
            """
            UPDATE payloads
            SET
                payload_type = :payload_type,
                owner_object_type = :owner_object_type,
                owner_object_id = :owner_object_id,
                storage_ref = :storage_ref,
                format = :format,
                checksum = :checksum,
                editability = :editability,
                canonical_flag = :canonical_flag,
                updated_at = :updated_at,
                version = :version
            WHERE payload_id = :payload_id
            """,
            record,
        )
        return self.get_by_id(connection, payload_id)
