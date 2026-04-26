from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from ._mappers import prepare_job_record, row_to_job


ALLOWED_JOB_TABLES = {"ingestion_jobs", "materialization_jobs", "reentry_jobs"}


class JobRepository:
    def __init__(self, table: str) -> None:
        if table not in ALLOWED_JOB_TABLES:
            raise ValueError(f"Unsupported job table '{table}'")
        self.table = table

    def create(self, connection: sqlite3.Connection, job_data: Mapping[str, Any]) -> dict[str, Any]:
        record = prepare_job_record(job_data, table=self.table)
        connection.execute(
            f"""
            INSERT INTO {self.table} (
                job_id, job_type, status, target_ref, started_at, finished_at, logs_ref
            ) VALUES (
                :job_id, :job_type, :status, :target_ref, :started_at, :finished_at, :logs_ref
            )
            """,
            record,
        )
        return self.get_by_id(connection, record["job_id"])  # type: ignore[return-value]

    def get_by_id(self, connection: sqlite3.Connection, job_id: str) -> dict[str, Any] | None:
        row = connection.execute(
            f"""
            SELECT job_id, job_type, status, target_ref, started_at, finished_at, logs_ref
            FROM {self.table}
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()
        return row_to_job(row)

    def list(self, connection: sqlite3.Connection, *, status: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = connection.execute(
            f"""
            SELECT job_id, job_type, status, target_ref, started_at, finished_at, logs_ref
            FROM {self.table}
            {where_clause}
            ORDER BY started_at, job_id
            """,
            params,
        ).fetchall()
        return [row_to_job(row) for row in rows if row is not None]

    def update_status(
        self,
        connection: sqlite3.Connection,
        job_id: str,
        status: str,
        *,
        started_at: str | None = None,
        finished_at: str | None = None,
        logs_ref: str | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_by_id(connection, job_id)
        if current is None:
            return None
        connection.execute(
            f"""
            UPDATE {self.table}
            SET
                status = ?,
                started_at = COALESCE(?, started_at),
                finished_at = COALESCE(?, finished_at),
                logs_ref = COALESCE(?, logs_ref)
            WHERE job_id = ?
            """,
            (status, started_at, finished_at, logs_ref, job_id),
        )
        return self.get_by_id(connection, job_id)
