from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_proposal_record, row_to_proposal, utc_now


class ProposalRepository:
    def create(self, connection: sqlite3.Connection, proposal_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_proposal_record(proposal_data)
        connection.execute(
            """
            INSERT INTO proposals (
                proposal_id, proposal_type, target_object_type, target_object_id,
                target_refs, proposed_changes, proposed_by, rationale,
                evidence_refs, proposal_state, decision_id, created_at, updated_at
            ) VALUES (
                :proposal_id, :proposal_type, :target_object_type, :target_object_id,
                :target_refs, :proposed_changes, :proposed_by, :rationale,
                :evidence_refs, :proposal_state, :decision_id, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["proposal_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, proposal_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                proposal_id, proposal_type, target_object_type, target_object_id,
                target_refs, proposed_changes, proposed_by, rationale,
                evidence_refs, proposal_state, decision_id, created_at, updated_at
            FROM proposals
            WHERE proposal_id = ?
            """,
            (proposal_id,),
        ).fetchone()
        return row_to_proposal(row)

    def list(
        self,
        connection: sqlite3.Connection,
        *,
        proposal_state: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if proposal_state is not None:
            clauses.append("proposal_state = ?")
            params.append(proposal_state)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                proposal_id, proposal_type, target_object_type, target_object_id,
                target_refs, proposed_changes, proposed_by, rationale,
                evidence_refs, proposal_state, decision_id, created_at, updated_at
            FROM proposals
            {where_clause}
            ORDER BY created_at, proposal_id
            """,
            params,
        ).fetchall()
        return [row_to_proposal(row) for row in rows if row is not None]

    def update_state(
        self,
        connection: sqlite3.Connection,
        proposal_id: str,
        proposal_state: str,
        *,
        decision_id: str | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_by_id(connection, proposal_id)
        if current is None:
            return None
        next_decision_id = decision_id if decision_id is not None else current.get("decision_id")
        updated_at = utc_now()
        connection.execute(
            """
            UPDATE proposals
            SET proposal_state = ?, decision_id = ?, updated_at = ?
            WHERE proposal_id = ?
            """,
            (proposal_state, next_decision_id, updated_at, proposal_id),
        )
        return self.get_by_id(connection, proposal_id)
