from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_domain_record, row_to_domain


class DomainRepository:
    def create(self, connection: sqlite3.Connection, domain_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_domain_record(domain_data)
        connection.execute(
            """
            INSERT INTO domains (
                domain_id, name, description, cognitive_purpose, status,
                owner_human, owner_agent, source_types_supported,
                local_entity_types, relation_types, promotion_rules,
                governance_dependencies, version, created_at, updated_at
            ) VALUES (
                :domain_id, :name, :description, :cognitive_purpose, :status,
                :owner_human, :owner_agent, :source_types_supported,
                :local_entity_types, :relation_types, :promotion_rules,
                :governance_dependencies, :version, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["domain_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, domain_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                domain_id, name, description, cognitive_purpose, status,
                owner_human, owner_agent, source_types_supported,
                local_entity_types, relation_types, promotion_rules,
                governance_dependencies, version, created_at, updated_at
            FROM domains
            WHERE domain_id = ?
            """,
            (domain_id,),
        ).fetchone()
        return row_to_domain(row)

    def list(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT
                domain_id, name, description, cognitive_purpose, status,
                owner_human, owner_agent, source_types_supported,
                local_entity_types, relation_types, promotion_rules,
                governance_dependencies, version, created_at, updated_at
            FROM domains
            ORDER BY created_at, domain_id
            """
        ).fetchall()
        return [row_to_domain(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, domain_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, domain_id)
        if current is None:
            return None
        record = prepare_domain_record({**current, **dict(changes), "domain_id": domain_id}, current=current)
        connection.execute(
            """
            UPDATE domains
            SET
                name = :name,
                description = :description,
                cognitive_purpose = :cognitive_purpose,
                status = :status,
                owner_human = :owner_human,
                owner_agent = :owner_agent,
                source_types_supported = :source_types_supported,
                local_entity_types = :local_entity_types,
                relation_types = :relation_types,
                promotion_rules = :promotion_rules,
                governance_dependencies = :governance_dependencies,
                version = :version,
                updated_at = :updated_at
            WHERE domain_id = :domain_id
            """,
            record,
        )
        return self.get_by_id(connection, domain_id)

    def update_status(self, connection: sqlite3.Connection, domain_id: str, status: str) -> dict[str, Any] | None:
        return self.update(connection, domain_id, {"status": status})
