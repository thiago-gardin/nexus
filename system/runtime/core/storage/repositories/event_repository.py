from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_event_record, row_to_event


class EventRepository:
    def create(self, connection: sqlite3.Connection, event_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_event_record(event_data)
        connection.execute(
            """
            INSERT INTO events (
                event_id, event_type, target_object_type, target_object_id,
                performed_by, performed_via, reason, payload,
                before_state_ref, after_state_ref, reversible_flag, created_at
            ) VALUES (
                :event_id, :event_type, :target_object_type, :target_object_id,
                :performed_by, :performed_via, :reason, :payload,
                :before_state_ref, :after_state_ref, :reversible_flag, :created_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["event_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, event_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                event_id, event_type, target_object_type, target_object_id,
                performed_by, performed_via, reason, payload,
                before_state_ref, after_state_ref, reversible_flag, created_at
            FROM events
            WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()
        return row_to_event(row)

    def list(
        self,
        connection: sqlite3.Connection,
        *,
        target_object_type: str | None = None,
        target_object_id: str | None = None,
        event_type: str | None = None,
        performed_by: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if target_object_type is not None:
            clauses.append("target_object_type = ?")
            params.append(target_object_type)
        if target_object_id is not None:
            clauses.append("target_object_id = ?")
            params.append(target_object_id)
        if event_type is not None:
            clauses.append("event_type = ?")
            params.append(event_type)
        if performed_by is not None:
            clauses.append("performed_by = ?")
            params.append(performed_by)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                event_id, event_type, target_object_type, target_object_id,
                performed_by, performed_via, reason, payload,
                before_state_ref, after_state_ref, reversible_flag, created_at
            FROM events
            {where_clause}
            ORDER BY created_at, event_id
            """,
            params,
        ).fetchall()
        return [row_to_event(row) for row in rows if row is not None]
