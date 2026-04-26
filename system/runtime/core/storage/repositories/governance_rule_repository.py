from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_governance_rule_record, row_to_governance_rule


class GovernanceRuleRepository:
    def create(self, connection: sqlite3.Connection, rule_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_governance_rule_record(rule_data)
        connection.execute(
            """
            INSERT INTO governance_rules (
                rule_id, rule_type, name, scope, logic_description,
                machine_executable_repr, human_readable_repr, applies_to,
                priority, status, created_by, approved_by, version, created_at, updated_at
            ) VALUES (
                :rule_id, :rule_type, :name, :scope, :logic_description,
                :machine_executable_repr, :human_readable_repr, :applies_to,
                :priority, :status, :created_by, :approved_by, :version, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["rule_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, rule_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                rule_id, rule_type, name, scope, logic_description,
                machine_executable_repr, human_readable_repr, applies_to,
                priority, status, created_by, approved_by, version, created_at, updated_at
            FROM governance_rules
            WHERE rule_id = ?
            """,
            (rule_id,),
        ).fetchone()
        return row_to_governance_rule(row)

    def list(
        self,
        connection: sqlite3.Connection,
        *,
        scope: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if scope is not None:
            clauses.append("scope = ?")
            params.append(scope)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                rule_id, rule_type, name, scope, logic_description,
                machine_executable_repr, human_readable_repr, applies_to,
                priority, status, created_by, approved_by, version, created_at, updated_at
            FROM governance_rules
            {where_clause}
            ORDER BY priority DESC, created_at, rule_id
            """,
            params,
        ).fetchall()
        return [row_to_governance_rule(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, rule_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, rule_id)
        if current is None:
            return None
        record = prepare_governance_rule_record({**current, **dict(changes), "rule_id": rule_id}, current=current)
        connection.execute(
            """
            UPDATE governance_rules
            SET
                rule_type = :rule_type,
                name = :name,
                scope = :scope,
                logic_description = :logic_description,
                machine_executable_repr = :machine_executable_repr,
                human_readable_repr = :human_readable_repr,
                applies_to = :applies_to,
                priority = :priority,
                status = :status,
                created_by = :created_by,
                approved_by = :approved_by,
                version = :version,
                updated_at = :updated_at
            WHERE rule_id = :rule_id
            """,
            record,
        )
        return self.get_by_id(connection, rule_id)
