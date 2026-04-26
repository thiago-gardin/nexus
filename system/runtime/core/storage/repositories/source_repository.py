from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_source_record, row_to_source, utc_now


class SourceRepository:
    def create(self, connection: sqlite3.Connection, source_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_source_record(source_data)
        connection.execute(
            """
            INSERT INTO sources (
                source_id, domain_id, source_type, source_origin, source_uri,
                storage_ref, raw_payload_ref, parsed_payload_ref, checksum,
                ingestion_status, metadata, provenance_record, created_at, updated_at
            ) VALUES (
                :source_id, :domain_id, :source_type, :source_origin, :source_uri,
                :storage_ref, :raw_payload_ref, :parsed_payload_ref, :checksum,
                :ingestion_status, :metadata, :provenance_record, :created_at, :updated_at
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["source_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, source_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT
                source_id, domain_id, source_type, source_origin, source_uri,
                storage_ref, raw_payload_ref, parsed_payload_ref, checksum,
                ingestion_status, metadata, provenance_record, created_at, updated_at
            FROM sources
            WHERE source_id = ?
            """,
            (source_id,),
        ).fetchone()
        return row_to_source(row)

    def list(self, connection: sqlite3.Connection, *, domain_id: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if domain_id is not None:
            clauses.append("domain_id = ?")
            params.append(domain_id)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT
                source_id, domain_id, source_type, source_origin, source_uri,
                storage_ref, raw_payload_ref, parsed_payload_ref, checksum,
                ingestion_status, metadata, provenance_record, created_at, updated_at
            FROM sources
            {where_clause}
            ORDER BY created_at, source_id
            """,
            params,
        ).fetchall()
        return [row_to_source(row) for row in rows if row is not None]

    def update(self, connection: sqlite3.Connection, source_id: str, changes: Mapping[str, Any]) -> dict[str, Any] | None:
        current = self.get_by_id(connection, source_id)
        if current is None:
            return None
        record = prepare_source_record({**current, **dict(changes), "source_id": source_id}, current=current)
        connection.execute(
            """
            UPDATE sources
            SET
                domain_id = :domain_id,
                source_type = :source_type,
                source_origin = :source_origin,
                source_uri = :source_uri,
                storage_ref = :storage_ref,
                raw_payload_ref = :raw_payload_ref,
                parsed_payload_ref = :parsed_payload_ref,
                checksum = :checksum,
                ingestion_status = :ingestion_status,
                metadata = :metadata,
                provenance_record = :provenance_record,
                updated_at = :updated_at
            WHERE source_id = :source_id
            """,
            record,
        )
        return self.get_by_id(connection, source_id)

    def update_status(
        self,
        connection: sqlite3.Connection,
        source_id: str,
        ingestion_status: str,
        *,
        parsed_payload_ref: str | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_by_id(connection, source_id)
        if current is None:
            return None
        connection.execute(
            """
            UPDATE sources
            SET ingestion_status = ?, parsed_payload_ref = COALESCE(?, parsed_payload_ref), updated_at = ?
            WHERE source_id = ?
            """,
            (ingestion_status, parsed_payload_ref, utc_now(), source_id),
        )
        return self.get_by_id(connection, source_id)
