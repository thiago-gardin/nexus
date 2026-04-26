from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .repositories import (
    DecisionRepository,
    DomainRepository,
    DomainVersionRepository,
    EntityRepository,
    EventRepository,
    GovernanceRuleRepository,
    JobRepository,
    ObjectVersionRepository,
    PayloadRepository,
    ProjectionRepository,
    ProposalRepository,
    RelationRepository,
    SourceRepository,
)
from .transaction_manager import TransactionManager
from .repositories._mappers import new_uuid
from .repositories._mappers import utc_now


DEFAULT_ACTOR = "system"
DEFAULT_SURFACE = "system"

GOVERNANCE_MINIMUM_PROPOSAL_RULES: dict[str, dict[str, str]] = {
    "entity_update": {
        "target_object_type": "entity",
        "mutation_kind": "update",
    },
    "relation_create": {
        "target_object_type": "relation",
        "mutation_kind": "create",
    },
    "relation_update": {
        "target_object_type": "relation",
        "mutation_kind": "update",
    },
    "merge": {
        "target_object_type": "entity",
        "mutation_kind": "proposal_only",
    },
    "separation": {
        "target_object_type": "entity",
        "mutation_kind": "proposal_only",
    },
    "decision_suggestion": {
        "target_object_type": "decision",
        "mutation_kind": "proposal_only",
    },
    "payload_edit": {
        "target_object_type": "payload",
        "mutation_kind": "update",
    },
    "reentry": {
        "target_object_type": "*",
        "mutation_kind": "proposal_only",
    },
}

GOVERNANCE_MINIMUM_DECISION_STATES: tuple[str, ...] = ("pending", "approved", "rejected", "overridden", "expired")


def _event_payload(object_type: str, object_id: str, action: str, before: Any, after: Any, changes: Mapping[str, Any] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "operation": action,
        "object_type": object_type,
        "object_id": object_id,
        "before": before,
        "after": after,
    }
    if changes is not None:
        payload["changes"] = dict(changes)
    return payload


class EventService:
    def __init__(self, transaction_manager: TransactionManager, repository: EventRepository | None = None) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or EventRepository()

    def record_event(self, connection, event_data: Mapping[str, Any]) -> dict[str, Any]:
        return self.repository.create(connection, event_data)

    def create_event(self, event_data: Mapping[str, Any]) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            return self.repository.create(connection, event_data)

    def get_event_by_id(self, event_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, event_id)

    def list_events(
        self,
        *,
        target_object_type: str | None = None,
        target_object_id: str | None = None,
        event_type: str | None = None,
        performed_by: str | None = None,
    ) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(
                connection,
                target_object_type=target_object_type,
                target_object_id=target_object_id,
                event_type=event_type,
                performed_by=performed_by,
            )


class DomainService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: DomainRepository | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or DomainRepository()
        self.event_service = event_service or EventService(transaction_manager)

    def create_domain(
        self,
        domain_data: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, domain_data)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "domain.created",
                    "target_object_type": "domain",
                    "target_object_id": created["domain_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("domain", created["domain_id"], "create", None, created, domain_data),
                    "reversible_flag": True,
                },
            )
            return created

    def get_domain_by_id(self, domain_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, domain_id)

    def list_domains(self) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection)

    def update_domain(
        self,
        domain_id: str,
        changes: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, domain_id)
            if before is None:
                raise KeyError(domain_id)
            updated = self.repository.update(connection, domain_id, changes)
            if updated is None:
                raise KeyError(domain_id)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "domain.updated",
                    "target_object_type": "domain",
                    "target_object_id": domain_id,
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("domain", domain_id, "update", before, updated, changes),
                    "reversible_flag": True,
                },
            )
            return updated

    def update_domain_status(
        self,
        domain_id: str,
        status: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return self.update_domain(
            domain_id,
            {"status": status},
            performed_by=performed_by,
            performed_via=performed_via,
            reason=reason,
        )


class DomainVersionService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: DomainVersionRepository | None = None,
        domain_repository: DomainRepository | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or DomainVersionRepository()
        self.domain_repository = domain_repository or DomainRepository()
        self.event_service = event_service or EventService(transaction_manager)

    def create_domain_version(
        self,
        version_data: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            domain = self.domain_repository.get_by_id(connection, str(version_data["domain_id"]))
            if domain is None:
                raise KeyError(str(version_data["domain_id"]))
            created = self.repository.create(connection, version_data)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "domain_version.created",
                    "target_object_type": "domain",
                    "target_object_id": created["domain_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("domain_version", created["domain_version_id"], "create", None, created, version_data),
                    "reversible_flag": True,
                },
            )
            updated = self.repository.update(connection, created["domain_version_id"], {"last_event_id": event["event_id"]})
            return updated or created

    def activate_domain_version(
        self,
        domain_version_id: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, domain_version_id)
            if before is None:
                raise KeyError(domain_version_id)
            activated = self.repository.activate(connection, domain_version_id, event_id=None)
            if activated is None:
                raise KeyError(domain_version_id)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "domain_version.activation_completed",
                    "target_object_type": "domain",
                    "target_object_id": activated["domain_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("domain_version", domain_version_id, "activate", before, activated, {"status": "active"}),
                    "reversible_flag": True,
                },
            )
            final = self.repository.update(connection, domain_version_id, {"last_event_id": event["event_id"]})
            return final or activated

    def get_domain_version_by_id(self, domain_version_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, domain_version_id)

    def get_active_domain_version(self, domain_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_active_for_domain(connection, domain_id)

    def list_domain_versions(self, *, domain_id: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection, domain_id=domain_id)

    def validate_entity_against_active_charter(self, domain_id: str, entity_type: str, attributes: Mapping[str, Any]) -> None:
        active = self.get_active_domain_version(domain_id)
        if active is None:
            return
        allowed = {str(item) for item in active.get("allowed_entity_types") or []}
        if allowed and entity_type not in allowed:
            raise ValueError(f"Entity type '{entity_type}' is not allowed by active domain version")
        required_fields = active.get("required_fields") or {}
        entity_required = required_fields.get(entity_type) if isinstance(required_fields, Mapping) else None
        if isinstance(entity_required, list):
            missing = [field for field in entity_required if field not in attributes or attributes.get(field) in {None, ""}]
            if missing:
                raise ValueError(f"Missing required fields for '{entity_type}': {', '.join(str(item) for item in missing)}")

    def validate_relation_against_active_charter(self, domain_id: str | None, relation_type: str) -> None:
        if domain_id is None:
            return
        active = self.get_active_domain_version(domain_id)
        if active is None:
            return
        allowed = {str(item) for item in active.get("allowed_relation_types") or []}
        if allowed and relation_type not in allowed:
            raise ValueError(f"Relation type '{relation_type}' is not allowed by active domain version")


class EntityService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: EntityRepository | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or EntityRepository()
        self.event_service = event_service or EventService(transaction_manager)

    def create_entity(
        self,
        entity_data: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, entity_data)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "entity.created",
                    "target_object_type": "entity",
                    "target_object_id": created["entity_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("entity", created["entity_id"], "create", None, created, entity_data),
                    "reversible_flag": True,
                },
            )
            return created

    def get_entity_by_id(self, entity_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, entity_id)

    def list_entities(self) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection)

    def update_entity(
        self,
        entity_id: str,
        changes: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, entity_id)
            if before is None:
                raise KeyError(entity_id)
            updated = self.repository.update(connection, entity_id, changes)
            if updated is None:
                raise KeyError(entity_id)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "entity.updated",
                    "target_object_type": "entity",
                    "target_object_id": entity_id,
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("entity", entity_id, "update", before, updated, changes),
                    "reversible_flag": True,
                },
            )
            return updated

    def update_entity_status(
        self,
        entity_id: str,
        status: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return self.update_entity(
            entity_id,
            {"validation_status": status},
            performed_by=performed_by,
            performed_via=performed_via,
            reason=reason,
        )


class RelationService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: RelationRepository | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or RelationRepository()
        self.event_service = event_service or EventService(transaction_manager)

    def create_relation(
        self,
        relation_data: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, relation_data)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "relation.created",
                    "target_object_type": "relation",
                    "target_object_id": created["relation_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("relation", created["relation_id"], "create", None, created, relation_data),
                    "reversible_flag": True,
                },
            )
            return created

    def get_relation_by_id(self, relation_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, relation_id)

    def list_relations(self) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection)

    def update_relation(
        self,
        relation_id: str,
        changes: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, relation_id)
            if before is None:
                raise KeyError(relation_id)
            updated = self.repository.update(connection, relation_id, changes)
            if updated is None:
                raise KeyError(relation_id)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "relation.updated",
                    "target_object_type": "relation",
                    "target_object_id": relation_id,
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("relation", relation_id, "update", before, updated, changes),
                    "reversible_flag": True,
                },
            )
            return updated

    def update_relation_status(
        self,
        relation_id: str,
        status: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return self.update_relation(
            relation_id,
            {"validation_status": status},
            performed_by=performed_by,
            performed_via=performed_via,
            reason=reason,
        )


class ObjectValidationService:
    SUPPORTED_OBJECT_TYPES = {"entity", "relation"}

    def __init__(self, entity_service: EntityService, relation_service: RelationService) -> None:
        self.entity_service = entity_service
        self.relation_service = relation_service

    def validate_object(
        self,
        object_type: str,
        object_id: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return self._update_status(
            object_type,
            object_id,
            "validated",
            performed_by=performed_by,
            performed_via=performed_via,
            reason=reason or "validate object",
        )

    def reject_object(
        self,
        object_type: str,
        object_id: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        if not reason:
            raise ValueError("Rejection requires a reason")
        return self._update_status(
            object_type,
            object_id,
            "rejected",
            performed_by=performed_by,
            performed_via=performed_via,
            reason=reason,
        )

    def _update_status(
        self,
        object_type: str,
        object_id: str,
        status: str,
        *,
        performed_by: str,
        performed_via: str,
        reason: str | None,
    ) -> dict[str, Any]:
        if object_type == "entity":
            return self.entity_service.update_entity_status(
                object_id,
                status,
                performed_by=performed_by,
                performed_via=performed_via,
                reason=reason,
            )
        if object_type == "relation":
            return self.relation_service.update_relation_status(
                object_id,
                status,
                performed_by=performed_by,
                performed_via=performed_via,
                reason=reason,
            )
        raise ValueError("Object validation currently supports entity and relation")


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _safe_payload_suffix(payload_format: str) -> str:
    if payload_format in {"md", "txt", "json", "html"}:
        return payload_format
    return "bin"


class SourceService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: SourceRepository | None = None,
        event_service: EventService | None = None,
        payload_repository: PayloadRepository | None = None,
        object_version_repository: ObjectVersionRepository | None = None,
        payload_root: str | Path | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or SourceRepository()
        self.event_service = event_service or EventService(transaction_manager)
        self.payload_repository = payload_repository or PayloadRepository()
        self.object_version_repository = object_version_repository or ObjectVersionRepository()
        self.payload_root = Path(payload_root) if payload_root is not None else Path(".nexus") / "payloads"

    def create_source(
        self,
        source_data: Mapping[str, Any],
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, source_data)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "source.created",
                    "target_object_type": "source",
                    "target_object_id": created["source_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("source", created["source_id"], "create", None, created, source_data),
                    "reversible_flag": True,
                },
            )
            return created

    def get_source_by_id(self, source_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, source_id)

    def list_sources(self, *, domain_id: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection, domain_id=domain_id)

    def register_source_with_payload(
        self,
        source_data: Mapping[str, Any],
        *,
        content: str,
        payload_format: str = "txt",
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        source_id = str(source_data.get("source_id") or new_uuid())
        payload_id = new_uuid()
        storage_ref = self._write_source_payload_content(payload_id, payload_format, content)
        payload_record = {
            "payload_id": payload_id,
            "payload_type": "raw_body",
            "owner_object_type": "source",
            "owner_object_id": source_id,
            "storage_ref": storage_ref,
            "format": payload_format,
            "checksum": _sha256_text(content),
            "editability": "read_only",
            "canonical_flag": False,
        }
        try:
            with self.transaction_manager.transaction() as connection:
                raw_payload = self.payload_repository.create(connection, payload_record)
                payload_event = self.event_service.record_event(
                    connection,
                    {
                        "event_type": "payload.created",
                        "target_object_type": "payload",
                        "target_object_id": raw_payload["payload_id"],
                        "performed_by": performed_by,
                        "performed_via": performed_via,
                        "reason": "register source manifest payload",
                        "payload": _event_payload("payload", raw_payload["payload_id"], "create", None, raw_payload, payload_record),
                        "reversible_flag": True,
                    },
                )
                self.object_version_repository.create(
                    connection,
                    {
                        "object_type": "payload",
                        "object_id": raw_payload["payload_id"],
                        "version_number": raw_payload["version"],
                        "serialized_state_ref": payload_event["event_id"],
                        "created_by": performed_by,
                    },
                )
                source_record = {
                    **dict(source_data),
                    "source_id": source_id,
                    "storage_ref": source_data.get("storage_ref") or raw_payload["storage_ref"],
                    "raw_payload_ref": raw_payload["payload_id"],
                    "parsed_payload_ref": source_data.get("parsed_payload_ref"),
                    "checksum": source_data.get("checksum") or raw_payload["checksum"],
                }
                source = self.repository.create(connection, source_record)
                self.event_service.record_event(
                    connection,
                    {
                        "event_type": "source.created",
                        "target_object_type": "source",
                        "target_object_id": source["source_id"],
                        "performed_by": performed_by,
                        "performed_via": performed_via,
                        "reason": reason,
                        "payload": _event_payload("source", source["source_id"], "create", None, source, source_record),
                        "reversible_flag": True,
                    },
                )
                return {"source": source, "raw_payload": raw_payload}
        except Exception:
            self._remove_source_payload_content(storage_ref)
            raise

    def _write_source_payload_content(self, payload_id: str, payload_format: str, content: str) -> str:
        suffix = _safe_payload_suffix(payload_format)
        path = self.payload_root / f"{payload_id}.{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"file:{path.relative_to(self.payload_root).as_posix()}"

    def _remove_source_payload_content(self, storage_ref: str) -> None:
        if not storage_ref.startswith("file:"):
            return
        path = Path(storage_ref.removeprefix("file:"))
        if not path.is_absolute():
            path = self.payload_root / path
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


class PayloadService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        *,
        payload_root: str | Path | None = None,
        repository: PayloadRepository | None = None,
        event_service: EventService | None = None,
        object_version_repository: ObjectVersionRepository | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or PayloadRepository()
        self.event_service = event_service or EventService(transaction_manager)
        self.object_version_repository = object_version_repository or ObjectVersionRepository()
        self.payload_root = Path(payload_root) if payload_root is not None else Path(".nexus") / "payloads"

    def create_payload(
        self,
        payload_data: Mapping[str, Any],
        *,
        content: str | None = None,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        prepared = dict(payload_data)
        if content is not None:
            payload_id = str(prepared.get("payload_id") or new_uuid())
            payload_format = str(prepared.get("format") or "txt")
            storage_ref = self._write_payload_content(payload_id, payload_format, content)
            prepared.setdefault("payload_id", payload_id)
            prepared["storage_ref"] = storage_ref
            prepared["checksum"] = _sha256_text(content)
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, prepared)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "payload.created",
                    "target_object_type": "payload",
                    "target_object_id": created["payload_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("payload", created["payload_id"], "create", None, created, prepared),
                    "reversible_flag": True,
                },
            )
            self.object_version_repository.create(
                connection,
                {
                    "object_type": "payload",
                    "object_id": created["payload_id"],
                    "version_number": created["version"],
                    "serialized_state_ref": event["event_id"],
                    "created_by": performed_by,
                },
            )
            return created

    def get_payload_by_id(self, payload_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, payload_id)

    def list_payloads(
        self,
        *,
        owner_object_type: str | None = None,
        owner_object_id: str | None = None,
    ) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(
                connection,
                owner_object_type=owner_object_type,
                owner_object_id=owner_object_id,
            )

    def update_payload(
        self,
        payload_id: str,
        changes: Mapping[str, Any],
        *,
        content: str | None = None,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, payload_id)
            if before is None:
                raise KeyError(payload_id)
            prepared_changes = dict(changes)
            if content is not None:
                payload_format = str(prepared_changes.get("format") or before.get("format") or "txt")
                prepared_changes["storage_ref"] = self._write_payload_content(payload_id, payload_format, content)
                prepared_changes["checksum"] = _sha256_text(content)
            updated = self.repository.update(connection, payload_id, prepared_changes)
            if updated is None:
                raise KeyError(payload_id)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "payload.updated",
                    "target_object_type": "payload",
                    "target_object_id": payload_id,
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("payload", payload_id, "update", before, updated, prepared_changes),
                    "reversible_flag": True,
                },
            )
            self.object_version_repository.create(
                connection,
                {
                    "object_type": "payload",
                    "object_id": payload_id,
                    "version_number": updated["version"],
                    "serialized_state_ref": event["event_id"],
                    "created_by": performed_by,
                },
            )
            return updated

    def read_payload_content(self, payload_id: str) -> str | None:
        payload = self.get_payload_by_id(payload_id)
        if payload is None:
            return None
        storage_ref = str(payload.get("storage_ref") or "")
        if not storage_ref.startswith("file:"):
            return None
        path = Path(storage_ref.removeprefix("file:"))
        if not path.is_absolute():
            path = self.payload_root / path
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _write_payload_content(self, payload_id: str, payload_format: str, content: str) -> str:
        suffix = _safe_payload_suffix(payload_format)
        path = self.payload_root / f"{payload_id}.{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"file:{path.relative_to(self.payload_root).as_posix()}"


class ProjectionService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        *,
        projection_root: str | Path | None = None,
        repository: ProjectionRepository | None = None,
        event_service: EventService | None = None,
        object_version_repository: ObjectVersionRepository | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or ProjectionRepository()
        self.event_service = event_service or EventService(transaction_manager)
        self.object_version_repository = object_version_repository or ObjectVersionRepository()
        self.projection_root = Path(projection_root) if projection_root is not None else Path(".nexus") / "projections"

    def create_projection(
        self,
        projection_data: Mapping[str, Any],
        *,
        content: str | None = None,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        reason: str | None = None,
    ) -> dict[str, Any]:
        prepared = dict(projection_data)
        if content is not None:
            projection_id = str(prepared.get("projection_id") or new_uuid())
            fmt = str(prepared.get("materialization_format") or "md")
            prepared.setdefault("projection_id", projection_id)
            prepared["storage_ref"] = self._write_projection_content(projection_id, fmt, content)
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, prepared)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "projection.created",
                    "target_object_type": "projection",
                    "target_object_id": created["projection_id"],
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": reason,
                    "payload": _event_payload("projection", created["projection_id"], "create", None, created, prepared),
                    "reversible_flag": True,
                },
            )
            self.object_version_repository.create(
                connection,
                {
                    "object_type": "projection",
                    "object_id": created["projection_id"],
                    "version_number": 1,
                    "serialized_state_ref": event["event_id"],
                    "created_by": performed_by,
                },
            )
            return created

    def get_projection_by_id(self, projection_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, projection_id)

    def list_projections(self, *, projection_type: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection, projection_type=projection_type)

    def read_projection_content(self, projection_id: str) -> str | None:
        projection = self.get_projection_by_id(projection_id)
        if projection is None:
            return None
        storage_ref = str(projection.get("storage_ref") or "")
        if not storage_ref.startswith("file:"):
            return None
        path = Path(storage_ref.removeprefix("file:"))
        if not path.is_absolute():
            path = self.projection_root / path
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _write_projection_content(self, projection_id: str, projection_format: str, content: str) -> str:
        suffix = _safe_payload_suffix(projection_format)
        path = self.projection_root / f"{projection_id}.{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"file:{path.relative_to(self.projection_root).as_posix()}"


class GovernanceRuleService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        repository: GovernanceRuleRepository | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.repository = repository or GovernanceRuleRepository()
        self.event_service = event_service or EventService(transaction_manager)

    def create_rule(self, rule_data: Mapping[str, Any]) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            created = self.repository.create(connection, rule_data)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "rule.created",
                    "target_object_type": "rule",
                    "target_object_id": created["rule_id"],
                    "performed_by": created.get("created_by") or DEFAULT_ACTOR,
                    "performed_via": DEFAULT_SURFACE,
                    "reason": created.get("logic_description"),
                    "payload": _event_payload("rule", created["rule_id"], "create", None, created, rule_data),
                    "reversible_flag": True,
                },
            )
            return created

    def get_rule_by_id(self, rule_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, rule_id)

    def list_rules(self, *, scope: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection, scope=scope, status=status)

    def update_rule_status(
        self,
        rule_id: str,
        status: str,
        *,
        performed_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        if status not in {"active", "inactive", "deprecated", "draft"}:
            raise ValueError(f"Unsupported governance rule status '{status}'")
        with self.transaction_manager.transaction() as connection:
            before = self.repository.get_by_id(connection, rule_id)
            if before is None:
                raise KeyError(rule_id)
            changes: dict[str, Any] = {"status": status}
            if status == "active":
                changes["approved_by"] = performed_by
            updated = self.repository.update(connection, rule_id, changes)
            if updated is None:
                raise KeyError(rule_id)
            self.event_service.record_event(
                connection,
                {
                    "event_type": "rule.status_updated",
                    "target_object_type": "rule",
                    "target_object_id": rule_id,
                    "performed_by": performed_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload("rule", rule_id, "status_update", before, updated, changes),
                    "reversible_flag": True,
                },
            )
            return updated


class JobService:
    def __init__(self, transaction_manager: TransactionManager, table: str) -> None:
        self.transaction_manager = transaction_manager
        self.repository = JobRepository(table)

    def create_job(self, job_data: Mapping[str, Any]) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            return self.repository.create(connection, job_data)

    def get_job_by_id(self, job_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.repository.get_by_id(connection, job_id)

    def list_jobs(self, *, status: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.repository.list(connection, status=status)

    def update_job_status(
        self,
        job_id: str,
        status: str,
        *,
        logs_ref: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            updated = self.repository.update_status(
                connection,
                job_id,
                status,
                finished_at=utc_now() if status in {"completed", "failed"} else None,
                logs_ref=logs_ref,
            )
            if updated is None:
                raise KeyError(job_id)
            return updated


class SearchService:
    def __init__(
        self,
        domain_service: DomainService,
        entity_service: EntityService,
        relation_service: RelationService,
        payload_service: PayloadService,
        projection_service: ProjectionService,
    ) -> None:
        self.domain_service = domain_service
        self.entity_service = entity_service
        self.relation_service = relation_service
        self.payload_service = payload_service
        self.projection_service = projection_service

    def search(self, *, query: str, object_type: str | None = None, domain_id: str | None = None) -> list[dict[str, Any]]:
        query_norm = query.casefold()
        results: list[dict[str, Any]] = []
        if object_type in {None, "domain"}:
            for domain in self.domain_service.list_domains():
                if self._matches(domain, query_norm) and (domain_id is None or domain["domain_id"] == domain_id):
                    results.append({"object_type": "domain", "object_id": domain["domain_id"], "record": domain})
        if object_type in {None, "entity"}:
            for entity in self.entity_service.list_entities():
                if domain_id is not None and entity.get("domain_id") != domain_id:
                    continue
                if self._matches(entity, query_norm):
                    results.append({"object_type": "entity", "object_id": entity["entity_id"], "record": entity})
        if object_type in {None, "relation"}:
            for relation in self.relation_service.list_relations():
                if domain_id is not None and relation.get("domain_context") != domain_id:
                    continue
                if self._matches(relation, query_norm):
                    results.append({"object_type": "relation", "object_id": relation["relation_id"], "record": relation})
        if object_type in {None, "payload"}:
            for payload in self.payload_service.list_payloads():
                if self._matches(payload, query_norm):
                    results.append({"object_type": "payload", "object_id": payload["payload_id"], "record": payload})
        if object_type in {None, "projection"}:
            for projection in self.projection_service.list_projections():
                if self._matches(projection, query_norm):
                    results.append({"object_type": "projection", "object_id": projection["projection_id"], "record": projection})
        return results

    def _matches(self, record: Mapping[str, Any], query_norm: str) -> bool:
        return query_norm in json.dumps(record, ensure_ascii=False, sort_keys=True).casefold()


class IngestionService:
    def __init__(
        self,
        *,
        domain_service: DomainService,
        source_service: SourceService,
        payload_service: PayloadService,
        entity_service: EntityService,
        relation_service: RelationService,
        event_service: EventService,
        job_service: JobService | None = None,
    ) -> None:
        self.domain_service = domain_service
        self.source_service = source_service
        self.payload_service = payload_service
        self.entity_service = entity_service
        self.relation_service = relation_service
        self.event_service = event_service
        self.job_service = job_service

    def ingest(
        self,
        *,
        domain_id: str,
        source_type: str,
        content: str | None = None,
        payload_ref: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        proposed_by: str = DEFAULT_ACTOR,
    ) -> dict[str, Any]:
        domain = self.domain_service.get_domain_by_id(domain_id)
        if domain is None:
            raise KeyError(domain_id)
        if content is None and payload_ref is None:
            raise ValueError("Either content or payload_ref must be provided")

        job: dict[str, Any] | None = None
        if self.job_service is not None:
            job = self.job_service.create_job(
                {
                    "job_type": "generic_ingestion",
                    "status": "running",
                    "target_ref": f"domain:{domain_id}",
                    "started_at": utc_now(),
                    "logs_ref": f"source_type:{source_type}",
                }
            )

        source_id = new_uuid()
        try:
            payload_format = self._format_for_source_type(source_type)
            raw_content = content
            if raw_content is None and payload_ref is not None:
                raw_content = self.payload_service.read_payload_content(payload_ref) or ""

            raw_payload = self.payload_service.create_payload(
                {
                    "payload_type": "raw_body",
                    "owner_object_type": "source",
                    "owner_object_id": source_id,
                    "format": payload_format,
                    "editability": "read_only",
                    "canonical_flag": False,
                },
                content=raw_content or "",
                performed_by=proposed_by,
                performed_via="api",
                reason="register raw ingested source payload",
            )
            parsed_content, parsed_metadata = self._parse_content(raw_content or "", payload_format)
            parsed_payload = self.payload_service.create_payload(
                {
                    "payload_type": "parsed_body",
                    "owner_object_type": "source",
                    "owner_object_id": source_id,
                    "format": "json",
                    "editability": "proposable_edit",
                    "canonical_flag": False,
                },
                content=json.dumps(parsed_metadata, ensure_ascii=False, sort_keys=True),
                performed_by=proposed_by,
                performed_via="api",
                reason="persist parsed source payload",
            )
            source = self.source_service.create_source(
                {
                    "source_id": source_id,
                    "domain_id": domain_id,
                    "source_type": source_type,
                    "source_origin": "local_api",
                    "source_uri": payload_ref,
                    "storage_ref": raw_payload["storage_ref"],
                    "raw_payload_ref": raw_payload["payload_id"],
                    "parsed_payload_ref": parsed_payload["payload_id"],
                    "checksum": raw_payload["checksum"],
                    "ingestion_status": "parsed",
                    "metadata": dict(metadata or {}),
                    "provenance_record": {
                        "raw_payload_ref": raw_payload["payload_id"],
                        "parsed_payload_ref": parsed_payload["payload_id"],
                        "ingested_at": utc_now(),
                    },
                },
                performed_by=proposed_by,
                performed_via="api",
                reason="generic local source ingestion",
            )
            candidates = self._persist_typing_candidates(domain_id, source, parsed_content, parsed_metadata, proposed_by)
            completed_job = None
            if self.job_service is not None and job is not None:
                completed_job = self.job_service.update_job_status(
                    job["job_id"],
                    "completed",
                    logs_ref=f"source:{source['source_id']};raw:{raw_payload['payload_id']};parsed:{parsed_payload['payload_id']}",
                )
            return {
                "source": source,
                "raw_payload": raw_payload,
                "parsed_payload": parsed_payload,
                "typing": candidates,
                "job": completed_job,
            }
        except Exception as exc:
            if self.job_service is not None and job is not None:
                self.job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
            raise

    def _format_for_source_type(self, source_type: str) -> str:
        lowered = source_type.casefold()
        if lowered in {"md", "markdown"}:
            return "md"
        if lowered == "json":
            return "json"
        return "txt"

    def _parse_content(self, content: str, payload_format: str) -> tuple[str, dict[str, Any]]:
        if payload_format == "json":
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"text": content}
            return content, {"format": "json", "data": parsed}
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        title = lines[0].lstrip("# ").strip() if lines else "Untitled source"
        return content, {"format": payload_format, "title": title, "text": content}

    def _persist_typing_candidates(
        self,
        domain_id: str,
        source: Mapping[str, Any],
        parsed_content: str,
        parsed_metadata: Mapping[str, Any],
        proposed_by: str,
    ) -> dict[str, Any]:
        entities: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        data = parsed_metadata.get("data") if isinstance(parsed_metadata, Mapping) else None
        if isinstance(data, Mapping) and isinstance(data.get("entities"), list):
            for item in data["entities"]:
                if not isinstance(item, Mapping) or not item.get("label"):
                    continue
                entities.append(
                    self.entity_service.create_entity(
                        {
                            "domain_id": domain_id,
                            "scope": "local",
                            "entity_type": str(item.get("entity_type") or item.get("type") or "source_candidate"),
                            "label": str(item["label"]),
                            "short_description": item.get("short_description") or item.get("description"),
                            "attributes": dict(item.get("attributes") or {}),
                            "aliases": list(item.get("aliases") or []),
                            "confidence": float(item.get("confidence") or 0.5),
                            "validation_status": "proposed",
                            "canonical_candidate_flag": False,
                            "provenance_refs": [source["source_id"]],
                            "payload_refs": [source["parsed_payload_ref"]],
                        },
                        performed_by=proposed_by,
                        performed_via="api",
                        reason="typing pipeline entity candidate",
                    )
                )
        else:
            title = str(parsed_metadata.get("title") or "Untitled source")
            entities.append(
                self.entity_service.create_entity(
                    {
                        "domain_id": domain_id,
                        "scope": "local",
                        "entity_type": "source_candidate",
                        "label": title[:120],
                        "short_description": parsed_content[:240] or None,
                        "attributes": {"source_type": source["source_type"]},
                        "aliases": [],
                        "confidence": 0.5,
                        "validation_status": "proposed",
                        "canonical_candidate_flag": False,
                        "provenance_refs": [source["source_id"]],
                        "payload_refs": [source["parsed_payload_ref"]],
                    },
                    performed_by=proposed_by,
                    performed_via="api",
                    reason="typing pipeline text entity candidate",
                )
            )
        if isinstance(data, Mapping) and isinstance(data.get("relations"), list):
            entity_ids_by_label = {entity["label"]: entity["entity_id"] for entity in entities}
            for item in data["relations"]:
                if not isinstance(item, Mapping):
                    continue
                source_id = item.get("source_entity_id") or entity_ids_by_label.get(str(item.get("source_label")))
                target_id = item.get("target_entity_id") or entity_ids_by_label.get(str(item.get("target_label")))
                if not source_id or not target_id:
                    continue
                relations.append(
                    self.relation_service.create_relation(
                        {
                            "source_entity_id": source_id,
                            "target_entity_id": target_id,
                            "relation_type": str(item.get("relation_type") or "references"),
                            "directionality": str(item.get("directionality") or "directed"),
                            "domain_context": domain_id,
                            "evidence_refs": [source["parsed_payload_ref"]],
                            "confidence": float(item.get("confidence") or 0.5),
                            "validation_status": "proposed",
                            "asserted_by": proposed_by,
                        },
                        performed_by=proposed_by,
                        performed_via="api",
                        reason="typing pipeline relation candidate",
                    )
                )
        return {"entities": entities, "relations": relations}


class ReconciliationService:
    def __init__(self, entity_service: EntityService, governance_service: "GovernanceService") -> None:
        self.entity_service = entity_service
        self.governance_service = governance_service

    def detect_duplicate_entities(self, *, domain_id: str, proposed_by: str = DEFAULT_ACTOR) -> list[dict[str, Any]]:
        return self.reconcile_entities(domain_id=domain_id, proposed_by=proposed_by)["merge_proposals"]

    def reconcile_entities(self, *, domain_id: str, proposed_by: str = DEFAULT_ACTOR) -> dict[str, Any]:
        candidate_groups = self.find_candidate_groups(domain_id=domain_id)
        merge_proposals: list[dict[str, Any]] = []
        separation_proposals: list[dict[str, Any]] = []
        for group in candidate_groups:
            canonical = group["canonical_entity"]
            duplicate_ids = [item["entity"]["entity_id"] for item in group["members"][1:]]
            if group["recommended_action"] == "merge":
                merge_proposals.append(
                    self.governance_service.create_structured_proposal(
                        proposal_type="merge",
                        target_object_type="entity",
                        target_object_id=canonical["entity_id"],
                        proposed_changes={
                            "canonical_entity_id": canonical["entity_id"],
                            "duplicate_entity_ids": duplicate_ids,
                            "match_key": group["match_key"],
                            "match_score": group["score"],
                            "canonical_candidate_flag": True,
                            "signals": group["signals"],
                        },
                        proposed_by=proposed_by,
                        rationale="Potential duplicate entities detected by label/alias matching",
                        evidence_refs=[item["entity"]["entity_id"] for item in group["members"]],
                    )
                )
            elif group["recommended_action"] == "separation":
                separation_proposals.append(
                    self.governance_service.create_structured_proposal(
                        proposal_type="separation",
                        target_object_type="entity",
                        target_object_id=canonical["entity_id"],
                        proposed_changes={
                            "candidate_entity_ids": [item["entity"]["entity_id"] for item in group["members"]],
                            "match_key": group["match_key"],
                            "match_score": group["score"],
                            "reason": "Candidate group requires human separation review before canonicalization",
                            "signals": group["signals"],
                        },
                        proposed_by=proposed_by,
                        rationale="Ambiguous duplicate candidate group detected by reconciliation pipeline",
                        evidence_refs=[item["entity"]["entity_id"] for item in group["members"]],
                    )
                )
        return {
            "candidate_groups": candidate_groups,
            "merge_proposals": merge_proposals,
            "separation_proposals": separation_proposals,
        }

    def find_candidate_groups(self, *, domain_id: str) -> list[dict[str, Any]]:
        entities = [item for item in self.entity_service.list_entities() if item.get("domain_id") == domain_id]
        groups: dict[str, dict[str, Any]] = {}
        for entity in entities:
            labels = self._entity_labels(entity)
            for label in labels:
                key = self._normalized_label(label)
                if not key:
                    continue
                group = groups.setdefault(key, {"match_key": key, "members_by_id": {}})
                score, signals = self._score_against_key(entity, key)
                existing = group["members_by_id"].get(entity["entity_id"])
                if existing is None or score > existing["score"]:
                    group["members_by_id"][entity["entity_id"]] = {
                        "entity": entity,
                        "score": score,
                        "signals": signals,
                    }

        candidate_groups: list[dict[str, Any]] = []
        for group in groups.values():
            members = sorted(group["members_by_id"].values(), key=lambda item: item["entity"]["created_at"])
            if len(members) < 2:
                continue
            scores = [item["score"] for item in members[1:]]
            group_score = round(min(scores) if scores else members[0]["score"], 2)
            entity_types = {item["entity"].get("entity_type") for item in members}
            recommended_action = "merge" if group_score >= 0.8 and len(entity_types) == 1 else "separation"
            signals = sorted({signal for item in members for signal in item["signals"]})
            candidate_groups.append(
                {
                    "match_key": group["match_key"],
                    "score": group_score,
                    "recommended_action": recommended_action,
                    "signals": signals,
                    "canonical_entity": members[0]["entity"],
                    "members": members,
                }
            )
        return candidate_groups

    def _entity_labels(self, entity: Mapping[str, Any]) -> list[str]:
        labels = [str(entity.get("label") or "")]
        labels.extend(str(alias) for alias in entity.get("aliases") or [])
        return labels

    def _score_against_key(self, entity: Mapping[str, Any], key: str) -> tuple[float, list[str]]:
        label_key = self._normalized_label(str(entity.get("label") or ""))
        if label_key == key:
            return 1.0, ["label"]
        alias_keys = {self._normalized_label(str(alias)) for alias in entity.get("aliases") or []}
        if key in alias_keys:
            return 0.85, ["alias"]
        return 0.65, ["weak_label_overlap"]

    def _normalized_label(self, value: str) -> str:
        return " ".join(value.casefold().strip().split())


class ReentryService:
    def __init__(self, governance_service: "GovernanceService") -> None:
        self.governance_service = governance_service

    def parse_diff(
        self,
        *,
        target_object_type: str,
        target_object_id: str,
        before: str,
        after: str,
        proposed_by: str = DEFAULT_ACTOR,
    ) -> dict[str, Any]:
        return self.governance_service.create_structured_proposal(
            proposal_type="reentry",
            target_object_type=target_object_type,
            target_object_id=target_object_id,
            proposed_changes={"before": before, "after": after},
            proposed_by=proposed_by,
            rationale="Structured reentry proposal from parsed diff",
            evidence_refs=[f"target:{target_object_type}:{target_object_id}"],
        )


class GovernanceService:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        proposal_repository: ProposalRepository | None = None,
        decision_repository: DecisionRepository | None = None,
        object_version_repository: ObjectVersionRepository | None = None,
        event_service: EventService | None = None,
        entity_service: EntityService | None = None,
        relation_service: RelationService | None = None,
        domain_service: DomainService | None = None,
        payload_service: PayloadService | None = None,
    ) -> None:
        self.transaction_manager = transaction_manager
        self.proposal_repository = proposal_repository or ProposalRepository()
        self.decision_repository = decision_repository or DecisionRepository()
        self.object_version_repository = object_version_repository or ObjectVersionRepository()
        self.event_service = event_service or EventService(transaction_manager)
        self.entity_service = entity_service or EntityService(transaction_manager, event_service=self.event_service)
        self.relation_service = relation_service or RelationService(transaction_manager, event_service=self.event_service)
        self.domain_service = domain_service
        self.payload_service = payload_service or PayloadService(transaction_manager, event_service=self.event_service)

    def supported_proposal_types(self) -> tuple[str, ...]:
        return tuple(GOVERNANCE_MINIMUM_PROPOSAL_RULES)

    def supported_decision_states(self) -> tuple[str, ...]:
        return GOVERNANCE_MINIMUM_DECISION_STATES

    def create_entity_update_proposal(
        self,
        entity_id: str,
        changes: Mapping[str, Any],
        *,
        proposed_by: str = DEFAULT_ACTOR,
        rationale: str | None = None,
        evidence_refs: list[Any] | tuple[Any, ...] | None = None,
    ) -> dict[str, Any]:
        return self._create_proposal(
            proposal_type="entity_update",
            target_object_type="entity",
            target_object_id=entity_id,
            proposed_changes=changes,
            proposed_by=proposed_by,
            rationale=rationale,
            evidence_refs=evidence_refs,
        )

    def create_relation_create_proposal(
        self,
        relation_data: Mapping[str, Any],
        *,
        proposed_by: str = DEFAULT_ACTOR,
        rationale: str | None = None,
        evidence_refs: list[Any] | tuple[Any, ...] | None = None,
    ) -> dict[str, Any]:
        target_object_id = str(relation_data.get("relation_id") or new_uuid())
        proposed_changes = dict(relation_data)
        proposed_changes["relation_id"] = target_object_id
        return self._create_proposal(
            proposal_type="relation_create",
            target_object_type="relation",
            target_object_id=target_object_id,
            proposed_changes=proposed_changes,
            proposed_by=proposed_by,
            rationale=rationale,
            evidence_refs=evidence_refs,
        )

    def create_relation_update_proposal(
        self,
        relation_id: str,
        changes: Mapping[str, Any],
        *,
        proposed_by: str = DEFAULT_ACTOR,
        rationale: str | None = None,
        evidence_refs: list[Any] | tuple[Any, ...] | None = None,
    ) -> dict[str, Any]:
        return self._create_proposal(
            proposal_type="relation_update",
            target_object_type="relation",
            target_object_id=relation_id,
            proposed_changes=changes,
            proposed_by=proposed_by,
            rationale=rationale,
            evidence_refs=evidence_refs,
        )

    def create_structured_proposal(
        self,
        *,
        proposal_type: str,
        target_object_type: str,
        target_object_id: str,
        proposed_changes: Mapping[str, Any],
        proposed_by: str = DEFAULT_ACTOR,
        rationale: str | None = None,
        evidence_refs: list[Any] | tuple[Any, ...] | None = None,
    ) -> dict[str, Any]:
        return self._create_proposal(
            proposal_type=proposal_type,
            target_object_type=target_object_type,
            target_object_id=target_object_id,
            proposed_changes=proposed_changes,
            proposed_by=proposed_by,
            rationale=rationale,
            evidence_refs=evidence_refs,
        )

    def list_proposals(self, *, proposal_state: str | None = None) -> list[dict[str, Any]]:
        with self.transaction_manager.connection() as connection:
            return self.proposal_repository.list(connection, proposal_state=proposal_state)

    def get_proposal_by_id(self, proposal_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            return self.proposal_repository.get_by_id(connection, proposal_id)

    def list_decision_queue(self, *, decision_state: str | None = "pending") -> list[dict[str, Any]]:
        return self.list_decisions(decision_state=decision_state)

    def list_decisions(self, *, decision_state: str | None = "pending") -> list[dict[str, Any]]:
        if decision_state is not None and decision_state not in self.supported_decision_states():
            raise ValueError(f"Unsupported decision state '{decision_state}'")
        with self.transaction_manager.connection() as connection:
            decisions = self.decision_repository.list(connection, decision_state=decision_state)
            return self._bundle_decisions(connection, decisions)

    def get_decision_by_id(self, decision_id: str) -> dict[str, Any] | None:
        with self.transaction_manager.connection() as connection:
            decision = self.decision_repository.get_by_id(connection, decision_id)
            if decision is None:
                return None
            proposal = self.proposal_repository.get_by_id(connection, decision["proposal_ref"])
            if proposal is None:
                return None
            return {
                "proposal": proposal,
                "decision": decision,
            }

    def list_object_history(self, object_type: str, object_id: str) -> list[dict[str, Any]]:
        return self.get_object_history(object_type, object_id)["versions"]

    def get_object_history(self, object_type: str, object_id: str) -> dict[str, Any]:
        with self.transaction_manager.connection() as connection:
            versions = self.object_version_repository.list_for_object(connection, object_type, object_id)
            current_object = self._current_object_state(connection, object_type, object_id)
            return {
                "object_type": object_type,
                "object_id": object_id,
                "current_object": current_object,
                "version_count": len(versions),
                "latest_version_number": versions[-1]["version_number"] if versions else None,
                "versions": versions,
            }

    def compare_object_versions(
        self,
        object_type: str,
        object_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        with self.transaction_manager.connection() as connection:
            versions = self.object_version_repository.list_for_object(connection, object_type, object_id)
            versions_by_number = {int(version["version_number"]): version for version in versions}
            record_a = versions_by_number.get(version_a)
            record_b = versions_by_number.get(version_b)
            if record_a is None:
                raise KeyError(f"{object_type}:{object_id}@{version_a}")
            if record_b is None:
                raise KeyError(f"{object_type}:{object_id}@{version_b}")

            state_a = self._state_for_object_version(connection, record_a)
            state_b = self._state_for_object_version(connection, record_b)
            return {
                "object_type": object_type,
                "object_id": object_id,
                "version_a": {**record_a, "state": state_a},
                "version_b": {**record_b, "state": state_b},
                "diff": self._diff_version_states(state_a, state_b),
            }

    def approve(
        self,
        decision_id: str,
        *,
        decided_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            decision = self.decision_repository.get_by_id(connection, decision_id)
            if decision is None:
                raise KeyError(decision_id)
            if decision["decision_state"] != "pending":
                raise ValueError(f"Decision '{decision_id}' is not pending")

            proposal = self.proposal_repository.get_by_id(connection, decision["proposal_ref"])
            if proposal is None:
                raise KeyError(decision["proposal_ref"])

            mutation_result = self._apply_approved_proposal(
                connection,
                proposal,
                decided_by=decided_by,
                performed_via=performed_via,
                rationale=rationale or proposal.get("rationale"),
            )
            updated_decision = self.decision_repository.update_state(
                connection,
                decision_id,
                "approved",
                decided_by=decided_by,
                rationale=rationale or proposal.get("rationale"),
            )
            updated_proposal = self.proposal_repository.update_state(
                connection,
                proposal["proposal_id"],
                "approved",
                decision_id=decision_id,
            )
            self.event_service.record_event(
                connection,
                {
                    "event_type": "decision.approved",
                    "target_object_type": "decision",
                    "target_object_id": decision_id,
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale or proposal.get("rationale"),
                    "payload": {
                        "decision": updated_decision,
                        "proposal": updated_proposal,
                        "mutation_event_id": mutation_result["event"]["event_id"],
                        "mutation_object": mutation_result["object"],
                    },
                    "reversible_flag": True,
                },
            )
            return {
                "proposal": updated_proposal,
                "decision": updated_decision,
                "mutation": mutation_result["object"],
            }

    def reject(
        self,
        decision_id: str,
        *,
        decided_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            decision = self.decision_repository.get_by_id(connection, decision_id)
            if decision is None:
                raise KeyError(decision_id)
            if decision["decision_state"] != "pending":
                raise ValueError(f"Decision '{decision_id}' is not pending")

            proposal = self.proposal_repository.get_by_id(connection, decision["proposal_ref"])
            if proposal is None:
                raise KeyError(decision["proposal_ref"])

            updated_decision = self.decision_repository.update_state(
                connection,
                decision_id,
                "rejected",
                decided_by=decided_by,
                rationale=rationale or proposal.get("rationale"),
            )
            updated_proposal = self.proposal_repository.update_state(
                connection,
                proposal["proposal_id"],
                "rejected",
                decision_id=decision_id,
            )
            self.event_service.record_event(
                connection,
                {
                    "event_type": "decision.rejected",
                    "target_object_type": "decision",
                    "target_object_id": decision_id,
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale or proposal.get("rationale"),
                    "payload": {
                        "decision": updated_decision,
                        "proposal": updated_proposal,
                    },
                    "reversible_flag": False,
                },
            )
            return {
                "proposal": updated_proposal,
                "decision": updated_decision,
            }

    def override(
        self,
        decision_id: str,
        *,
        decided_by: str = DEFAULT_ACTOR,
        performed_via: str = DEFAULT_SURFACE,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        with self.transaction_manager.transaction() as connection:
            decision = self.decision_repository.get_by_id(connection, decision_id)
            if decision is None:
                raise KeyError(decision_id)
            if decision["decision_state"] != "pending":
                raise ValueError(f"Decision '{decision_id}' is not pending")
            proposal = self.proposal_repository.get_by_id(connection, decision["proposal_ref"])
            if proposal is None:
                raise KeyError(decision["proposal_ref"])

            updated_decision = self.decision_repository.update_state(
                connection,
                decision_id,
                "overridden",
                decided_by=decided_by,
                rationale=rationale or decision.get("rationale"),
            )
            updated_proposal = self.proposal_repository.update_state(
                connection,
                proposal["proposal_id"],
                "rejected",
                decision_id=decision_id,
            )
            self.event_service.record_event(
                connection,
                {
                    "event_type": "decision.overridden",
                    "target_object_type": "decision",
                    "target_object_id": decision_id,
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": {
                        "before_decision": decision,
                        "decision": updated_decision,
                        "proposal": updated_proposal,
                    },
                    "reversible_flag": False,
                },
            )
            return {"proposal": updated_proposal, "decision": updated_decision}

    def _create_proposal(
        self,
        *,
        proposal_type: str,
        target_object_type: str,
        target_object_id: str,
        proposed_changes: Mapping[str, Any],
        proposed_by: str,
        rationale: str | None,
        evidence_refs: list[Any] | tuple[Any, ...] | None,
    ) -> dict[str, Any]:
        rule = self._proposal_rule(proposal_type)
        if rule["target_object_type"] != "*" and rule["target_object_type"] != target_object_type:
            raise ValueError(
                f"Proposal type '{proposal_type}' must target '{rule['target_object_type']}', not '{target_object_type}'"
            )
        with self.transaction_manager.transaction() as connection:
            proposal_id = new_uuid()
            decision_id = new_uuid()
            proposal = self.proposal_repository.create(
                connection,
                {
                    "proposal_id": proposal_id,
                    "proposal_type": proposal_type,
                    "target_object_type": target_object_type,
                    "target_object_id": target_object_id,
                    "target_refs": [target_object_id],
                    "proposed_changes": proposed_changes,
                    "proposed_by": proposed_by,
                    "rationale": rationale,
                    "evidence_refs": list(evidence_refs or []),
                    "decision_id": decision_id,
                    "proposal_state": "pending",
                },
            )
            decision = self.decision_repository.create(
                connection,
                {
                    "decision_id": decision_id,
                    "decision_type": "edit_acceptance",
                    "proposal_ref": proposal_id,
                    "target_refs": [target_object_id],
                    "proposed_by": proposed_by,
                    "rationale": rationale,
                    "decision_state": "pending",
                },
            )
            return {
                "proposal": proposal,
                "decision": decision,
            }

    def _proposal_rule(self, proposal_type: str) -> Mapping[str, str]:
        try:
            return GOVERNANCE_MINIMUM_PROPOSAL_RULES[proposal_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported proposal type '{proposal_type}'") from exc

    def _bundle_decisions(
        self,
        connection,
        decisions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        queue: list[dict[str, Any]] = []
        for decision in decisions:
            proposal = self.proposal_repository.get_by_id(connection, decision["proposal_ref"])
            if proposal is None:
                continue
            queue.append(
                {
                    "proposal": proposal,
                    "decision": decision,
                }
            )
        return queue

    def _current_object_state(self, connection, object_type: str, object_id: str) -> dict[str, Any] | None:
        if object_type == "entity":
            return self.entity_service.repository.get_by_id(connection, object_id)
        if object_type == "relation":
            return self.relation_service.repository.get_by_id(connection, object_id)
        if object_type == "domain" and self.domain_service is not None:
            return self.domain_service.repository.get_by_id(connection, object_id)
        if object_type == "payload":
            return self.payload_service.repository.get_by_id(connection, object_id)
        return None

    def _state_for_object_version(self, connection, version: Mapping[str, Any]) -> dict[str, Any] | None:
        event = self.event_service.repository.get_by_id(connection, str(version["serialized_state_ref"]))
        if event is None:
            return None
        payload = event.get("payload") or {}
        if isinstance(payload, Mapping):
            after_state = payload.get("after")
            if isinstance(after_state, Mapping):
                return dict(after_state)
            mutation_object = payload.get("mutation_object")
            if isinstance(mutation_object, Mapping):
                return dict(mutation_object)
        return None

    def _diff_version_states(
        self,
        state_a: Mapping[str, Any] | None,
        state_b: Mapping[str, Any] | None,
    ) -> dict[str, dict[str, Any]]:
        left = dict(state_a or {})
        right = dict(state_b or {})
        diff: dict[str, dict[str, Any]] = {}
        for field in sorted(set(left) | set(right)):
            if left.get(field) != right.get(field):
                diff[field] = {"from": left.get(field), "to": right.get(field)}
        return diff

    def _apply_approved_proposal(
        self,
        connection,
        proposal: Mapping[str, Any],
        *,
        decided_by: str,
        performed_via: str,
        rationale: str | None,
    ) -> dict[str, Any]:
        proposal_type = proposal["proposal_type"]
        if proposal_type == "entity_update":
            before = self.entity_service.repository.get_by_id(connection, proposal["target_object_id"])
            if before is None:
                raise KeyError(proposal["target_object_id"])
            updated = self.entity_service.repository.update(connection, proposal["target_object_id"], proposal["proposed_changes"])
            if updated is None:
                raise KeyError(proposal["target_object_id"])
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "entity.updated",
                    "target_object_type": "entity",
                    "target_object_id": proposal["target_object_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload("entity", proposal["target_object_id"], "update", before, updated, proposal["proposed_changes"]),
                    "reversible_flag": True,
                },
            )
            self._record_object_version(
                connection,
                object_type="entity",
                object_id=updated["entity_id"],
                version_number=updated["version"],
                serialized_state_ref=event["event_id"],
                created_by=decided_by,
            )
            return {"object": updated, "event": event}

        if proposal_type == "relation_create":
            proposed_relation = dict(proposal["proposed_changes"])
            proposed_relation.setdefault("relation_id", proposal["target_object_id"])
            created = self.relation_service.repository.create(connection, proposed_relation)
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "relation.created",
                    "target_object_type": "relation",
                    "target_object_id": created["relation_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload("relation", created["relation_id"], "create", None, created, proposed_relation),
                    "reversible_flag": True,
                },
            )
            self._record_object_version(
                connection,
                object_type="relation",
                object_id=created["relation_id"],
                version_number=created["version"],
                serialized_state_ref=event["event_id"],
                created_by=decided_by,
            )
            return {"object": created, "event": event}

        if proposal_type == "relation_update":
            before = self.relation_service.repository.get_by_id(connection, proposal["target_object_id"])
            if before is None:
                raise KeyError(proposal["target_object_id"])
            updated = self.relation_service.repository.update(connection, proposal["target_object_id"], proposal["proposed_changes"])
            if updated is None:
                raise KeyError(proposal["target_object_id"])
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "relation.updated",
                    "target_object_type": "relation",
                    "target_object_id": proposal["target_object_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload("relation", proposal["target_object_id"], "update", before, updated, proposal["proposed_changes"]),
                    "reversible_flag": True,
                },
            )
            self._record_object_version(
                connection,
                object_type="relation",
                object_id=updated["relation_id"],
                version_number=updated["version"],
                serialized_state_ref=event["event_id"],
                created_by=decided_by,
            )
            return {"object": updated, "event": event}

        if proposal_type == "payload_edit":
            before = self.payload_service.repository.get_by_id(connection, proposal["target_object_id"])
            if before is None:
                raise KeyError(proposal["target_object_id"])
            proposed_changes = dict(proposal["proposed_changes"])
            content = proposed_changes.pop("content", None)
            if content is not None:
                payload_format = str(proposed_changes.get("format") or before.get("format") or "txt")
                proposed_changes["storage_ref"] = self.payload_service._write_payload_content(
                    proposal["target_object_id"],
                    payload_format,
                    str(content),
                )
                proposed_changes["checksum"] = _sha256_text(str(content))
            updated = self.payload_service.repository.update(connection, proposal["target_object_id"], proposed_changes)
            if updated is None:
                raise KeyError(proposal["target_object_id"])
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "payload.updated",
                    "target_object_type": "payload",
                    "target_object_id": proposal["target_object_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload(
                        "payload",
                        proposal["target_object_id"],
                        "update",
                        before,
                        updated,
                        proposal["proposed_changes"],
                    ),
                    "reversible_flag": True,
                },
            )
            self._record_object_version(
                connection,
                object_type="payload",
                object_id=updated["payload_id"],
                version_number=updated["version"],
                serialized_state_ref=event["event_id"],
                created_by=decided_by,
            )
            return {"object": updated, "event": event}

        if proposal_type == "merge":
            before = self.entity_service.repository.get_by_id(connection, proposal["target_object_id"])
            if before is None:
                raise KeyError(proposal["target_object_id"])
            proposed_changes = proposal["proposed_changes"]
            aliases = list(before.get("aliases") or [])
            duplicate_ids = list(proposed_changes.get("duplicate_entity_ids") or [])
            for duplicate_id in duplicate_ids:
                duplicate = self.entity_service.repository.get_by_id(connection, duplicate_id)
                if duplicate and duplicate.get("label") not in aliases:
                    aliases.append(duplicate["label"])
            updated = self.entity_service.repository.update(
                connection,
                proposal["target_object_id"],
                {
                    "aliases": aliases,
                    "canonical_candidate_flag": bool(proposed_changes.get("canonical_candidate_flag", True)),
                    "validation_status": "validated",
                    "provenance_refs": list(before.get("provenance_refs") or []) + duplicate_ids,
                },
            )
            if updated is None:
                raise KeyError(proposal["target_object_id"])
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": "reconciliation.merge_applied",
                    "target_object_type": "entity",
                    "target_object_id": proposal["target_object_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": _event_payload("entity", proposal["target_object_id"], "merge", before, updated, proposed_changes),
                    "reversible_flag": True,
                },
            )
            self._record_object_version(
                connection,
                object_type="entity",
                object_id=updated["entity_id"],
                version_number=updated["version"],
                serialized_state_ref=event["event_id"],
                created_by=decided_by,
            )
            return {"object": updated, "event": event}

        if proposal_type in {"separation", "decision_suggestion", "reentry"}:
            event = self.event_service.record_event(
                connection,
                {
                    "event_type": f"proposal.{proposal_type}.accepted",
                    "target_object_type": proposal["target_object_type"],
                    "target_object_id": proposal["target_object_id"],
                    "performed_by": decided_by,
                    "performed_via": performed_via,
                    "reason": rationale,
                    "payload": {
                        "proposal": dict(proposal),
                        "accepted_without_direct_mutation": True,
                    },
                    "reversible_flag": False,
                },
            )
            return {"object": dict(proposal), "event": event}

        raise ValueError(f"Unsupported proposal type '{proposal_type}'")

    def _record_object_version(
        self,
        connection,
        *,
        object_type: str,
        object_id: str,
        version_number: int,
        serialized_state_ref: str,
        created_by: str,
    ) -> dict[str, Any]:
        return self.object_version_repository.create(
            connection,
            {
                "object_type": object_type,
                "object_id": object_id,
                "version_number": version_number,
                "serialized_state_ref": serialized_state_ref,
                "created_by": created_by,
            },
        )
