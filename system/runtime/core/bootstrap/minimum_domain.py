from __future__ import annotations

from pathlib import Path
from typing import Any

from system.runtime.config import settings

from ..storage import DomainService, EventService, TransactionManager, resolve_db_path


MINIMUM_DOMAIN_ID = "nexus-core"
MINIMUM_DOMAIN_RECORD: dict[str, Any] = {
    "domain_id": MINIMUM_DOMAIN_ID,
    "name": "Nexus Core Domain",
    "description": "Bootstrap domain used to prove the executable core and treefolder publication flow.",
    "cognitive_purpose": "Provide a real seeded domain for end-to-end verification of the bootstrap runtime.",
    "status": "active",
    "source_types_supported": ["note"],
    "local_entity_types": ["concept"],
    "relation_types": ["references"],
    "promotion_rules": ["manual_review"],
    "governance_dependencies": ["baseline"],
}


def ensure_minimum_domain(transaction_manager: TransactionManager) -> dict[str, Any]:
    event_service = EventService(transaction_manager)
    domain_service = DomainService(transaction_manager, event_service=event_service)
    existing = domain_service.get_domain_by_id(MINIMUM_DOMAIN_ID)
    if existing is not None:
        return existing
    return domain_service.create_domain(MINIMUM_DOMAIN_RECORD)


def bootstrap_minimum_domain(db_path: str | Path | None = None) -> dict[str, Any]:
    resolved_db_path = str(resolve_db_path(db_path if db_path is not None else settings.db_path))
    transaction_manager = TransactionManager(resolved_db_path)
    transaction_manager.initialize()
    return ensure_minimum_domain(transaction_manager)
