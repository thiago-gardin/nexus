from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_domain_version_record, row_to_domain_version, utc_now


class DomainVersionRepository:
    def create(self, connection: sqlite3.Connection, version_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_domain_version_record(version_data)
        connection.execute(
            """
            INSERT INTO domain_versions (
                domain_version_id, domain_id, version_label, status, charter,
                allowed_entity_types, allowed_relation_types, allowed_payload_types,
                required_fields, promotion_rules, created_at, activated_at, last_event_id
            ) VALUES (
                :domain_version_id, :domain_id, :version_label, :status, :charter,
                :allowed_entity_types, :allowed_relation_types, :allowed_payload_types,
                :required_fields, :promotion_rules, :created_at, :activated_at, :last_event_id
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["domain_version_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, domain_version_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                domain_version_id, domain_id, version_label, status, charter,
                allowed_entity_types, allowed_relation_types, allowed_payload_types,
                required_fields, promotion_rules, created_at, activated_at, last_event_id
            FROM domain_versions
            WHERE domain_version_id = ?
            """,
            (domain_version_id,),
        ).fetchone()
        return row_to_domain_version(row)

    def list(self, connection: sqlite3.Connection, *, domain_id: str | None = None) -> list[dict[str, Any]]:
        if domain_id is None:
            rows = connection.execute(
                """
                SELECT
                    domain_version_id, domain_id, version_label, status, charter,
                    allowed_entity_types, allowed_relation_types, allowed_payload_types,
                    required_fields, promotion_rules, created_at, activated_at, last_event_id
                FROM domain_versions
                ORDER BY created_at, domain_version_id
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    domain_version_id, domain_id, version_label, status, charter,
                    allowed_entity_types, allowed_relation_types, allowed_payload_types,
                    required_fields, promotion_rules, created_at, activated_at, last_event_id
                FROM domain_versions
                WHERE domain_id = ?
                ORDER BY created_at, domain_version_id
                """,
                (domain_id,),
            ).fetchall()
        return [row_to_domain_version(row) for row in rows if row is not None]

    def get_active_for_domain(self, connection: sqlite3.Connection, domain_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                domain_version_id, domain_id, version_label, status, charter,
                allowed_entity_types, allowed_relation_types, allowed_payload_types,
                required_fields, promotion_rules, created_at, activated_at, last_event_id
            FROM domain_versions
            WHERE domain_id = ? AND status = 'active'
            """,
            (domain_id,),
        ).fetchone()
        return row_to_domain_version(row)

    def update(self, connection: sqlite3.Connection, domain_version_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, domain_version_id)
        if current is None:
            return None
        record = prepare_domain_version_record({**current, **dict(changes), "domain_version_id": domain_version_id}, current=current)
        connection.execute(
            """
            UPDATE domain_versions
            SET
                version_label = :version_label,
                status = :status,
                charter = :charter,
                allowed_entity_types = :allowed_entity_types,
                allowed_relation_types = :allowed_relation_types,
                allowed_payload_types = :allowed_payload_types,
                required_fields = :required_fields,
                promotion_rules = :promotion_rules,
                activated_at = :activated_at,
                last_event_id = :last_event_id
            WHERE domain_version_id = :domain_version_id
            """,
            record,
        )
        return self.get_by_id(connection, domain_version_id)

    def activate(self, connection: sqlite3.Connection, domain_version_id: str, *, event_id: str | None = None) -> dict[str, Any] | None:
        current = self.get_by_id(connection, domain_version_id)
        if current is None:
            return None
        now = utc_now()
        connection.execute(
            """
            UPDATE domain_versions
            SET status = 'inactive'
            WHERE domain_id = ? AND status = 'active' AND domain_version_id != ?
            """,
            (current["domain_id"], domain_version_id),
        )
        connection.execute(
            """
            UPDATE domain_versions
            SET status = 'active', activated_at = ?, last_event_id = ?
            WHERE domain_version_id = ?
            """,
            (now, event_id, domain_version_id),
        )
        return self.get_by_id(connection, domain_version_id)
