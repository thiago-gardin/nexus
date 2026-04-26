from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_relation_record, row_to_relation


class RelationRepository:
    def create(self, connection: sqlite3.Connection, relation_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_relation_record(relation_data)
        connection.execute(
            """
            INSERT INTO relations (
                relation_id, source_entity_id, target_entity_id, relation_type,
                directionality, domain_context, evidence_refs, confidence,
                validation_status, asserted_by, validated_by, version,
                created_at, updated_at
            ) VALUES (
                :relation_id, :source_entity_id, :target_entity_id, :relation_type,
                :directionality, :domain_context, :evidence_refs, :confidence,
                :validation_status, :asserted_by, :validated_by, :version,
                :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["relation_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, relation_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                relation_id, source_entity_id, target_entity_id, relation_type,
                directionality, domain_context, evidence_refs, confidence,
                validation_status, asserted_by, validated_by, version,
                created_at, updated_at
            FROM relations
            WHERE relation_id = ?
            """,
            (relation_id,),
        ).fetchone()
        return row_to_relation(row)

    def list(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT
                relation_id, source_entity_id, target_entity_id, relation_type,
                directionality, domain_context, evidence_refs, confidence,
                validation_status, asserted_by, validated_by, version,
                created_at, updated_at
            FROM relations
            ORDER BY created_at, relation_id
            """
        ).fetchall()
        return [row_to_relation(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, relation_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, relation_id)
        if current is None:
            return None
        record = prepare_relation_record({**current, **dict(changes), "relation_id": relation_id}, current=current)
        connection.execute(
            """
            UPDATE relations
            SET
                source_entity_id = :source_entity_id,
                target_entity_id = :target_entity_id,
                relation_type = :relation_type,
                directionality = :directionality,
                domain_context = :domain_context,
                evidence_refs = :evidence_refs,
                confidence = :confidence,
                validation_status = :validation_status,
                asserted_by = :asserted_by,
                validated_by = :validated_by,
                version = :version,
                updated_at = :updated_at
            WHERE relation_id = :relation_id
            """,
            record,
        )
        return self.get_by_id(connection, relation_id)

    def update_status(self, connection: sqlite3.Connection, relation_id: str, status: str) -> dict[str, Any] | None:
        return self.update(connection, relation_id, {"validation_status": status})
