from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import Request

from system.runtime.core.storage import (
    DomainService,
    DomainVersionService,
    EntityService,
    EventService,
    GovernanceRuleService,
    GovernanceService,
    IngestionService,
    JobService,
    ObjectValidationService,
    PayloadService,
    ProjectionService,
    ReconciliationService,
    ReentryService,
    RelationService,
    SearchService,
    SourceService,
    TransactionManager,
    resolve_db_path,
)


@dataclass(slots=True)
class RuntimeContext:
    db_path: str
    transaction_manager: TransactionManager
    event_service: EventService
    domain_service: DomainService
    domain_version_service: DomainVersionService
    entity_service: EntityService
    relation_service: RelationService
    source_service: SourceService
    payload_service: PayloadService
    projection_service: ProjectionService
    governance_rule_service: GovernanceRuleService
    governance_service: GovernanceService
    object_validation_service: ObjectValidationService
    ingestion_service: IngestionService
    reconciliation_service: ReconciliationService
    reentry_service: ReentryService
    search_service: SearchService
    ingestion_job_service: JobService
    materialization_job_service: JobService
    reentry_job_service: JobService


def build_runtime(db_path: str | Path | None = None) -> RuntimeContext:
    resolved_db_path = str(resolve_db_path(db_path))
    transaction_manager = TransactionManager(resolved_db_path)
    transaction_manager.initialize()
    event_service = EventService(transaction_manager)
    domain_service = DomainService(transaction_manager, event_service=event_service)
    domain_version_service = DomainVersionService(transaction_manager, event_service=event_service)
    entity_service = EntityService(transaction_manager, event_service=event_service)
    relation_service = RelationService(transaction_manager, event_service=event_service)
    payload_root = Path(resolved_db_path).parent / "payloads"
    projection_root = Path(resolved_db_path).parent / "projections"
    source_service = SourceService(transaction_manager, event_service=event_service, payload_root=payload_root)
    payload_service = PayloadService(transaction_manager, payload_root=payload_root, event_service=event_service)
    projection_service = ProjectionService(transaction_manager, projection_root=projection_root, event_service=event_service)
    ingestion_job_service = JobService(transaction_manager, "ingestion_jobs")
    materialization_job_service = JobService(transaction_manager, "materialization_jobs")
    reentry_job_service = JobService(transaction_manager, "reentry_jobs")
    governance_rule_service = GovernanceRuleService(transaction_manager, event_service=event_service)
    governance_service = GovernanceService(
        transaction_manager,
        event_service=event_service,
        domain_service=domain_service,
        entity_service=entity_service,
        relation_service=relation_service,
        payload_service=payload_service,
    )
    object_validation_service = ObjectValidationService(entity_service, relation_service)
    return RuntimeContext(
        db_path=resolved_db_path,
        transaction_manager=transaction_manager,
        event_service=event_service,
        domain_service=domain_service,
        domain_version_service=domain_version_service,
        entity_service=entity_service,
        relation_service=relation_service,
        source_service=source_service,
        payload_service=payload_service,
        projection_service=projection_service,
        governance_rule_service=governance_rule_service,
        governance_service=governance_service,
        object_validation_service=object_validation_service,
        ingestion_service=IngestionService(
            domain_service=domain_service,
            source_service=source_service,
            payload_service=payload_service,
            entity_service=entity_service,
            relation_service=relation_service,
            event_service=event_service,
            job_service=ingestion_job_service,
        ),
        reconciliation_service=ReconciliationService(
            entity_service=entity_service,
            governance_service=governance_service,
        ),
        reentry_service=ReentryService(governance_service),
        search_service=SearchService(
            domain_service,
            entity_service,
            relation_service,
            payload_service,
            projection_service,
        ),
        ingestion_job_service=ingestion_job_service,
        materialization_job_service=materialization_job_service,
        reentry_job_service=reentry_job_service,
    )


def get_runtime(request: Request) -> RuntimeContext:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise RuntimeError("Runtime context is not initialized")
    return runtime
