from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_entity_record, row_to_entity


class EntityRepository:
    def create(self, connection: sqlite3.Connection, entity_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_entity_record(entity_data)
        connection.execute(
            """
            INSERT INTO entities (
                entity_id, scope, domain_id, entity_type, label,
                short_description, attributes, aliases, confidence,
                validation_status, canonical_candidate_flag, provenance_refs,
                payload_refs, version, created_at, updated_at
            ) VALUES (
                :entity_id, :scope, :domain_id, :entity_type, :label,
                :short_description, :attributes, :aliases, :confidence,
                :validation_status, :canonical_candidate_flag, :provenance_refs,
                :payload_refs, :version, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["entity_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, entity_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                entity_id, scope, domain_id, entity_type, label,
                short_description, attributes, aliases, confidence,
                validation_status, canonical_candidate_flag, provenance_refs,
                payload_refs, version, created_at, updated_at
            FROM entities
            WHERE entity_id = ?
            """,
            (entity_id,),
        ).fetchone()
        return row_to_entity(row)

    def list(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT
                entity_id, scope, domain_id, entity_type, label,
                short_description, attributes, aliases, confidence,
                validation_status, canonical_candidate_flag, provenance_refs,
                payload_refs, version, created_at, updated_at
            FROM entities
            ORDER BY created_at, entity_id
            """
        ).fetchall()
        return [row_to_entity(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, entity_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, entity_id)
        if current is None:
            return None
        record = prepare_entity_record({**current, **dict(changes), "entity_id": entity_id}, current=current)
        connection.execute(
            """
            UPDATE entities
            SET
                scope = :scope,
                domain_id = :domain_id,
                entity_type = :entity_type,
                label = :label,
                short_description = :short_description,
                attributes = :attributes,
                aliases = :aliases,
                confidence = :confidence,
                validation_status = :validation_status,
                canonical_candidate_flag = :canonical_candidate_flag,
                provenance_refs = :provenance_refs,
                payload_refs = :payload_refs,
                version = :version,
                updated_at = :updated_at
            WHERE entity_id = :entity_id
            """,
            record,
        )
        return self.get_by_id(connection, entity_id)

    def update_status(self, connection: sqlite3.Connection, entity_id: str, status: str) -> dict[str, Any] | None:
        return self.update(connection, entity_id, {"validation_status": status})
