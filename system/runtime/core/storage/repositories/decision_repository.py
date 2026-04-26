from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_decision_record, row_to_decision, utc_now


class DecisionRepository:
    def create(self, connection: sqlite3.Connection, decision_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_decision_record(decision_data)
        connection.execute(
            """
            INSERT INTO decisions (
                decision_id, decision_type, proposal_ref, target_refs,
                proposed_by, decided_by, rationale, decision_state,
                created_at, updated_at
            ) VALUES (
                :decision_id, :decision_type, :proposal_ref, :target_refs,
                :proposed_by, :decided_by, :rationale, :decision_state,
                :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["decision_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, decision_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                decision_id, decision_type, proposal_ref, target_refs,
                proposed_by, decided_by, rationale, decision_state,
                created_at, updated_at
            FROM decisions
            WHERE decision_id = ?
            """,
            (decision_id,),
        ).fetchone()
        return row_to_decision(row)

    def list(
        self,
        connection: sqlite3.Connection,
        *,
        decision_state: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if decision_state is not None:
            clauses.append("decision_state = ?")
            params.append(decision_state)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                decision_id, decision_type, proposal_ref, target_refs,
                proposed_by, decided_by, rationale, decision_state,
                created_at, updated_at
            FROM decisions
            {where_clause}
            ORDER BY created_at, decision_id
            """,
            params,
        ).fetchall()
        return [row_to_decision(row) for row in rows if row is not None]

    def update_state(
        self,
        connection: sqlite3.Connection,
        decision_id: str,
        decision_state: str,
        *,
        decided_by: str | None = None,
        rationale: str | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_by_id(connection, decision_id)
        if current is None:
            return None
        updated_at = utc_now()
        connection.execute(
            """
            UPDATE decisions
            SET decision_state = ?, decided_by = COALESCE(?, decided_by), rationale = COALESCE(?, rationale), updated_at = ?
            WHERE decision_id = ?
            """,
            (decision_state, decided_by, rationale, updated_at, decision_id),
        )
        return self.get_by_id(connection, decision_id)
