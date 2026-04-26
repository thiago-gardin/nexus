from __future__ import annotations

from pathlib import Path
from typing import Any

from system.runtime.config import settings

from ..storage import EntityService, EventService, RelationService, TransactionManager, resolve_db_path
from .minimum_domain import MINIMUM_DOMAIN_ID, ensure_minimum_domain


MINIMUM_DOMAIN_ENTITY_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "entity_id": "nexus-core-anchor",
        "domain_id": MINIMUM_DOMAIN_ID,
        "scope": "local",
        "entity_type": "concept",
        "label": "Nexus Core Anchor",
        "short_description": "Anchor concept published to make the treefolder useful.",
        "attributes": {
            "role": "anchor",
            "publication_surface": "treefolder",
        },
        "aliases": ["core anchor"],
        "confidence": 0.9,
        "validation_status": "validated",
        "canonical_candidate_flag": False,
        "provenance_refs": ["bootstrap:minimum-domain-content"],
        "payload_refs": [],
    },
    {
        "entity_id": "nexus-core-view",
        "domain_id": MINIMUM_DOMAIN_ID,
        "scope": "local",
        "entity_type": "concept",
        "label": "Nexus Core View",
        "short_description": "View concept published to demonstrate legible object materialization.",
        "attributes": {
            "role": "view",
            "publication_surface": "treefolder",
        },
        "aliases": ["core view"],
        "confidence": 0.88,
        "validation_status": "validated",
        "canonical_candidate_flag": False,
        "provenance_refs": ["bootstrap:minimum-domain-content"],
        "payload_refs": [],
    },
)

MINIMUM_DOMAIN_RELATION_RECORD: dict[str, Any] = {
    "relation_id": "nexus-core-view-references-anchor",
    "source_entity_id": "nexus-core-view",
    "target_entity_id": "nexus-core-anchor",
    "relation_type": "references",
    "directionality": "directed",
    "domain_context": MINIMUM_DOMAIN_ID,
    "evidence_refs": ["bootstrap:minimum-domain-content"],
    "confidence": 0.9,
    "validation_status": "validated",
    "asserted_by": "system",
}


def ensure_minimum_domain_content(transaction_manager: TransactionManager) -> dict[str, Any]:
    event_service = EventService(transaction_manager)
    entity_service = EntityService(transaction_manager, event_service=event_service)
    relation_service = RelationService(transaction_manager, event_service=event_service)

    domain = ensure_minimum_domain(transaction_manager)
    entities = [_ensure_entity(entity_service, entity_record) for entity_record in MINIMUM_DOMAIN_ENTITY_RECORDS]
    relation = _ensure_relation(relation_service, MINIMUM_DOMAIN_RELATION_RECORD)

    return {
        "domain": domain,
        "entities": entities,
        "relation": relation,
    }


def bootstrap_minimum_domain_content(db_path: str | Path | None = None) -> dict[str, Any]:
    resolved_db_path = str(resolve_db_path(db_path if db_path is not None else settings.db_path))
    transaction_manager = TransactionManager(resolved_db_path)
    transaction_manager.initialize()
    return ensure_minimum_domain_content(transaction_manager)


def _ensure_entity(entity_service: EntityService, entity_data: dict[str, Any]) -> dict[str, Any]:
    existing = entity_service.get_entity_by_id(entity_data["entity_id"])
    if existing is not None:
        return existing
    return entity_service.create_entity(entity_data)


def _ensure_relation(relation_service: RelationService, relation_data: dict[str, Any]) -> dict[str, Any]:
    existing = relation_service.get_relation_by_id(relation_data["relation_id"])
    if existing is not None:
        return existing
    return relation_service.create_relation(relation_data)
