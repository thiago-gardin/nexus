from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from ..dependencies import RuntimeContext, get_runtime
from ...core.operate_context import build_active_domain_charter, build_operate_context


REPO_ROOT = Path(__file__).resolve().parents[4]

router = APIRouter(prefix="/agent", tags=["agent"])


AGENT_MINIMUM_PROPOSAL_CONTRACTS: tuple[dict[str, str], ...] = (
    {
        "proposal_type": "entity_update",
        "target_object_type": "entity",
        "mutation_kind": "update",
        "submission_route": "/agent/proposals/entity-update",
    },
    {
        "proposal_type": "relation_create",
        "target_object_type": "relation",
        "mutation_kind": "create",
        "submission_route": "/agent/proposals/relation-create",
    },
    {
        "proposal_type": "merge",
        "target_object_type": "entity",
        "mutation_kind": "proposal_only",
        "submission_route": "/agent/proposals/merge",
    },
    {
        "proposal_type": "payload_edit",
        "target_object_type": "payload",
        "mutation_kind": "update",
        "submission_route": "/agent/proposals/payload-edit",
    },
    {
        "proposal_type": "reentry",
        "target_object_type": "payload|projection",
        "mutation_kind": "proposal_only",
        "submission_route": "/agent/proposals/reentry",
    },
)


class _LooseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class AgentSurfaceManifest(_LooseModel):
    surface: str = "agent"
    mode: str = "structured-read-and-propose"
    surface_boundary: str = "separate-from-human-surface"
    human_surface: str = "/surface"
    proposal_surface: str = "/agent/proposals"
    tree_publication_status: str = "/agent/publications/tree/status"
    read_routes: list[str] = Field(
        default_factory=lambda: [
            "/agent/domains",
            "/agent/domains/{domain_id}",
            "/agent/entities/{entity_id}",
            "/agent/relations/{relation_id}",
            "/agent/events?performed_by={actor}",
            "/agent/events/{event_id}",
            "/agent/rules",
            "/agent/rules/{rule_id}",
            "/agent/payloads/{payload_id}",
            "/agent/projections/{projection_id}",
            "/agent/search",
            "/agent/proposals",
            "/agent/proposals/{proposal_id}",
            "/agent/decisions",
            "/agent/decisions/{decision_id}",
            "/agent/domains/{domain_id}/operate-context",
            "/agent/domains/{domain_id}/active-charter",
            "/agent/objects/{object_type}/{object_id}/history",
            "/agent/objects/{object_type}/{object_id}/versions/compare",
            "/agent/publications/tree/status",
            "/agent/publications/tree/domains/{domain_id}/governance",
            "/agent/publications/tree/domains/{domain_id}/operational-summary",
            "/agent/publications/tree/domains/{domain_id}/review-queue",
            "/agent/publications/tree/domains/{domain_id}/active-decision-queue",
            "/agent/publications/tree/domains/{domain_id}/recent-changes",
        ]
    )
    proposal_types: list[str] = Field(default_factory=lambda: [contract["proposal_type"] for contract in AGENT_MINIMUM_PROPOSAL_CONTRACTS])
    proposal_contracts: list[dict[str, str]] = Field(default_factory=lambda: [dict(contract) for contract in AGENT_MINIMUM_PROPOSAL_CONTRACTS])
    proposal_submission_routes: list[str] = Field(default_factory=lambda: [contract["submission_route"] for contract in AGENT_MINIMUM_PROPOSAL_CONTRACTS])
    publication_routes: list[str] = Field(
        default_factory=lambda: [
            "/agent/publications/tree/status",
            "/agent/publications/tree/domains/{domain_id}/governance",
            "/agent/publications/tree/domains/{domain_id}/operational-summary",
            "/agent/publications/tree/domains/{domain_id}/review-queue",
            "/agent/publications/tree/domains/{domain_id}/active-decision-queue",
            "/agent/publications/tree/domains/{domain_id}/recent-changes",
        ]
    )
    governance_mutation_routes: list[str] = Field(
        default_factory=lambda: [
            "/decisions/{decision_id}/approve",
            "/decisions/{decision_id}/reject",
            "/decisions/{decision_id}/override",
        ]
    )
    circulation_policy: str = "proposal -> governance-api -> published-trace"
    approval_policy: str = "outside_agent_surface"
    reentry_policy: str = "structured-proposal-only"
    proposal_from_edit_policy: str = "out_of_sprint"
    mutation_policy: str = "governance-api-only"


class AgentDomainSummary(_LooseModel):
    domain_id: str
    name: str | None = None
    status: str | None = None
    version: int | None = None
    entity_count: int = 0
    relation_count: int = 0


class AgentDomainDetail(AgentDomainSummary):
    description: str | None = None
    cognitive_purpose: str | None = None
    source_types_supported: list[str] = Field(default_factory=list)
    local_entity_types: list[str] = Field(default_factory=list)
    relation_types: list[str] = Field(default_factory=list)
    promotion_rules: list[str] = Field(default_factory=list)
    governance_dependencies: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class AgentEntityView(_LooseModel):
    entity_id: str
    domain_id: str
    scope: str
    entity_type: str
    label: str
    short_description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    aliases: list[str] = Field(default_factory=list)
    confidence: float | None = None
    validation_status: str | None = None
    canonical_candidate_flag: bool | None = None
    provenance_refs: list[Any] = Field(default_factory=list)
    payload_refs: list[Any] = Field(default_factory=list)
    version: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AgentRelationView(_LooseModel):
    relation_id: str
    domain_context: str | None = None
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    directionality: str
    evidence_refs: list[Any] = Field(default_factory=list)
    confidence: float | None = None
    validation_status: str | None = None
    asserted_by: str | None = None
    validated_by: str | None = None
    version: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AgentEventView(_LooseModel):
    event_id: str
    event_type: str
    target_object_type: str
    target_object_id: str
    performed_by: str | None = None
    performed_via: str | None = None
    reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    before_state_ref: str | None = None
    after_state_ref: str | None = None
    reversible_flag: bool | None = None
    created_at: str | None = None


class AgentGovernanceRuleView(_LooseModel):
    rule_id: str
    rule_type: str
    name: str
    scope: str
    logic_description: str
    machine_executable_repr: str | None = None
    human_readable_repr: str
    applies_to: list[Any] = Field(default_factory=list)
    priority: int | None = None
    status: str | None = None
    created_by: str | None = None
    approved_by: str | None = None
    version: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AgentProposalView(_LooseModel):
    proposal_id: str
    proposal_type: str
    target_object_type: str
    target_object_id: str
    target_refs: list[Any] = Field(default_factory=list)
    proposed_changes: dict[str, Any] = Field(default_factory=dict)
    proposed_by: str | None = None
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)
    proposal_state: str | None = None
    decision_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AgentDecisionView(_LooseModel):
    decision_id: str
    decision_type: str
    proposal_ref: str
    target_refs: list[Any] = Field(default_factory=list)
    proposed_by: str | None = None
    decided_by: str | None = None
    rationale: str | None = None
    decision_state: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AgentDecisionBundle(_LooseModel):
    proposal: AgentProposalView
    decision: AgentDecisionView


class AgentObjectHistory(_LooseModel):
    object_type: str
    object_id: str
    current_object: dict[str, Any] | None = None
    version_count: int
    latest_version_number: int | None = None
    versions: list[dict[str, Any]] = Field(default_factory=list)


class AgentTreeStatus(_LooseModel):
    publication_timestamp: str | None = None
    publication_version: int | None = None
    freshness_status: str | None = None
    available_domains: list[str] = Field(default_factory=list)
    pending_proposals_count: int = 0
    remote_write_policy: str | None = None
    published_object_views: dict[str, int] = Field(default_factory=dict)


class AgentPublicationArtifact(_LooseModel):
    domain_id: str
    tree_path: str
    publication_timestamp: str | None = None
    publication_version: int | None = None
    freshness_status: str | None = None
    content: str


class AgentPayloadBundle(_LooseModel):
    payload: dict[str, Any]
    content: str | None = None


class AgentProjectionBundle(_LooseModel):
    projection: dict[str, Any]
    content: str | None = None


class EntityUpdateProposalRequest(_LooseModel):
    entity_id: str
    changes: dict[str, Any]
    proposed_by: str = "agent"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)


class RelationCreateProposalRequest(_LooseModel):
    relation_id: str | None = None
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    directionality: str
    domain_context: str
    asserted_by: str = "agent"
    proposed_by: str = "agent"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)
    confidence: float | None = None
    validation_status: str = "proposed"
    validated_by: str | None = None


class StructuredProposalRequest(_LooseModel):
    target_object_type: str
    target_object_id: str
    proposed_changes: dict[str, Any]
    proposed_by: str = "agent"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


def _count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        bucket = item.get(key)
        if bucket is None:
            continue
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def _tree_root(request: Request) -> Path:
    tree_root = getattr(request.app.state, "tree_root", None)
    if tree_root is None:
        return REPO_ROOT / "tree"
    return Path(tree_root)


def _load_tree_status(request: Request) -> AgentTreeStatus:
    tree_status_path = _tree_root(request) / "SYSTEM_STATUS.yaml"
    if not tree_status_path.exists():
        raise _not_found("tree publication status", str(tree_status_path))
    raw = yaml.safe_load(tree_status_path.read_text(encoding="utf-8")) or {}
    return AgentTreeStatus(
        publication_timestamp=raw.get("publication_timestamp"),
        publication_version=raw.get("publication_version"),
        freshness_status=raw.get("freshness_status"),
        available_domains=list(raw.get("available_domains") or []),
        pending_proposals_count=int(raw.get("pending_proposals_count") or 0),
        remote_write_policy=raw.get("remote_write_policy"),
        published_object_views=dict(raw.get("published_object_views") or {}),
    )


@router.get("", response_model=AgentSurfaceManifest)
@router.get("/", response_model=AgentSurfaceManifest)
def manifest() -> AgentSurfaceManifest:
    return AgentSurfaceManifest()


@router.get("/domains", response_model=list[AgentDomainSummary])
def list_domains(runtime: RuntimeContext = Depends(get_runtime)) -> list[AgentDomainSummary]:
    domains = runtime.domain_service.list_domains()
    entity_counts = _count_by_key(runtime.entity_service.list_entities(), "domain_id")
    relation_counts = _count_by_key(runtime.relation_service.list_relations(), "domain_context")
    return [
        AgentDomainSummary(
            domain_id=domain["domain_id"],
            name=domain.get("name"),
            status=domain.get("status"),
            version=domain.get("version"),
            entity_count=entity_counts.get(domain["domain_id"], 0),
            relation_count=relation_counts.get(domain["domain_id"], 0),
        )
        for domain in domains
    ]


@router.get("/domains/{domain_id}", response_model=AgentDomainDetail)
def get_domain(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentDomainDetail:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)
    entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
    relations = [relation for relation in runtime.relation_service.list_relations() if relation.get("domain_context") == domain_id]
    return AgentDomainDetail(
        domain_id=domain["domain_id"],
        name=domain.get("name"),
        status=domain.get("status"),
        version=domain.get("version"),
        entity_count=len(entities),
        relation_count=len(relations),
        description=domain.get("description"),
        cognitive_purpose=domain.get("cognitive_purpose"),
        source_types_supported=list(domain.get("source_types_supported") or []),
        local_entity_types=list(domain.get("local_entity_types") or []),
        relation_types=list(domain.get("relation_types") or []),
        promotion_rules=list(domain.get("promotion_rules") or []),
        governance_dependencies=list(domain.get("governance_dependencies") or []),
        created_at=domain.get("created_at"),
        updated_at=domain.get("updated_at"),
    )


@router.get("/domains/{domain_id}/operate-context", response_model=dict[str, Any])
def get_operate_context(domain_id: str, request: Request, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    if runtime.domain_service.get_domain_by_id(domain_id) is None:
        raise _not_found("domain", domain_id)
    return build_operate_context(runtime, domain_id, tree_root=_tree_root(request))


@router.get("/domains/{domain_id}/active-charter", response_model=dict[str, Any])
def get_active_charter(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    if runtime.domain_service.get_domain_by_id(domain_id) is None:
        raise _not_found("domain", domain_id)
    return build_active_domain_charter(runtime, domain_id)


@router.get("/entities/{entity_id}", response_model=AgentEntityView)
def get_entity(entity_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentEntityView:
    entity = runtime.entity_service.get_entity_by_id(entity_id)
    if entity is None:
        raise _not_found("entity", entity_id)
    return AgentEntityView(**entity)


@router.get("/relations/{relation_id}", response_model=AgentRelationView)
def get_relation(relation_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentRelationView:
    relation = runtime.relation_service.get_relation_by_id(relation_id)
    if relation is None:
        raise _not_found("relation", relation_id)
    return AgentRelationView(**relation)


@router.get("/events", response_model=list[AgentEventView])
def list_events(
    target_object_type: str | None = None,
    target_object_id: str | None = None,
    event_type: str | None = None,
    performed_by: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[AgentEventView]:
    events = runtime.event_service.list_events(
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        event_type=event_type,
        performed_by=performed_by,
    )
    return [AgentEventView(**event) for event in events]


@router.get("/events/{event_id}", response_model=AgentEventView)
def get_event(event_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentEventView:
    event = runtime.event_service.get_event_by_id(event_id)
    if event is None:
        raise _not_found("event", event_id)
    return AgentEventView(**event)


@router.get("/rules", response_model=list[AgentGovernanceRuleView])
def list_rules(
    scope: str | None = None,
    status: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[AgentGovernanceRuleView]:
    rules = runtime.governance_rule_service.list_rules(scope=scope, status=status)
    return [AgentGovernanceRuleView(**rule) for rule in rules]


@router.get("/rules/{rule_id}", response_model=AgentGovernanceRuleView)
def get_rule(rule_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentGovernanceRuleView:
    rule = runtime.governance_rule_service.get_rule_by_id(rule_id)
    if rule is None:
        raise _not_found("rule", rule_id)
    return AgentGovernanceRuleView(**rule)


@router.get("/payloads/{payload_id}", response_model=AgentPayloadBundle)
def get_payload(payload_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentPayloadBundle:
    payload = runtime.payload_service.get_payload_by_id(payload_id)
    if payload is None:
        raise _not_found("payload", payload_id)
    return AgentPayloadBundle(payload=payload, content=runtime.payload_service.read_payload_content(payload_id))


@router.get("/projections/{projection_id}", response_model=AgentProjectionBundle)
def get_projection(projection_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentProjectionBundle:
    projection = runtime.projection_service.get_projection_by_id(projection_id)
    if projection is None:
        raise _not_found("projection", projection_id)
    return AgentProjectionBundle(
        projection=projection,
        content=runtime.projection_service.read_projection_content(projection_id),
    )


@router.get("/search")
def search_objects(
    query: str,
    type: str | None = None,
    domain: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[dict[str, Any]]:
    return runtime.search_service.search(query=query, object_type=type, domain_id=domain)


@router.get("/proposals", response_model=list[AgentProposalView])
def list_proposals(runtime: RuntimeContext = Depends(get_runtime)) -> list[AgentProposalView]:
    return [AgentProposalView(**proposal) for proposal in runtime.governance_service.list_proposals()]


@router.get("/proposals/{proposal_id}", response_model=AgentProposalView)
def get_proposal(proposal_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentProposalView:
    proposal = runtime.governance_service.get_proposal_by_id(proposal_id)
    if proposal is None:
        raise _not_found("proposal", proposal_id)
    return AgentProposalView(**proposal)


@router.get("/decisions", response_model=list[AgentDecisionBundle])
def list_decisions(runtime: RuntimeContext = Depends(get_runtime)) -> list[AgentDecisionBundle]:
    bundles = runtime.governance_service.list_decisions(decision_state=None)
    return [AgentDecisionBundle(**bundle) for bundle in bundles]


@router.get("/decisions/{decision_id}", response_model=AgentDecisionBundle)
def get_decision(decision_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> AgentDecisionBundle:
    bundle = runtime.governance_service.get_decision_by_id(decision_id)
    if bundle is None:
        raise _not_found("decision", decision_id)
    return AgentDecisionBundle(**bundle)


@router.get("/objects/{object_type}/{object_id}/history", response_model=AgentObjectHistory)
def get_object_history(
    object_type: str,
    object_id: str,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentObjectHistory:
    history = runtime.governance_service.get_object_history(object_type, object_id)
    return AgentObjectHistory(**history)


@router.get("/objects/{object_type}/{object_id}/versions/compare")
def compare_object_versions(
    object_type: str,
    object_id: str,
    v_a: int,
    v_b: int,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    try:
        return runtime.governance_service.compare_object_versions(object_type, object_id, v_a, v_b)
    except KeyError as exc:
        raise _not_found("object version", str(exc)) from exc


@router.get("/publications/tree/status", response_model=AgentTreeStatus)
def get_tree_publication_status(request: Request) -> AgentTreeStatus:
    return _load_tree_status(request)


@router.get("/publications/tree/domains/{domain_id}/governance", response_model=AgentPublicationArtifact)
def get_domain_governance_publication(
    domain_id: str,
    request: Request,
) -> AgentPublicationArtifact:
    return _load_tree_publication_artifact(request, domain_id, "GOVERNANCE_TRACE.md", "governance publication")


@router.get("/publications/tree/domains/{domain_id}/operational-summary", response_model=AgentPublicationArtifact)
def get_domain_operational_summary_publication(
    domain_id: str,
    request: Request,
) -> AgentPublicationArtifact:
    return _load_tree_publication_artifact(
        request,
        domain_id,
        "DOMAIN_OPERATIONAL_SUMMARY.md",
        "operational summary publication",
    )


@router.get("/publications/tree/domains/{domain_id}/review-queue", response_model=AgentPublicationArtifact)
def get_domain_review_queue_publication(
    domain_id: str,
    request: Request,
) -> AgentPublicationArtifact:
    return _load_tree_publication_artifact(
        request,
        domain_id,
        "PENDING_REVIEW_QUEUE.md",
        "review queue publication",
    )


@router.get("/publications/tree/domains/{domain_id}/active-decision-queue", response_model=AgentPublicationArtifact)
def get_domain_active_decision_queue_publication(
    domain_id: str,
    request: Request,
) -> AgentPublicationArtifact:
    return _load_tree_publication_artifact(
        request,
        domain_id,
        "ACTIVE_DECISION_QUEUE.md",
        "active decision queue publication",
    )


@router.get("/publications/tree/domains/{domain_id}/recent-changes", response_model=AgentPublicationArtifact)
def get_domain_recent_changes_publication(
    domain_id: str,
    request: Request,
) -> AgentPublicationArtifact:
    return _load_tree_publication_artifact(
        request,
        domain_id,
        "RECENT_CHANGES.md",
        "recent changes publication",
    )


@router.post("/proposals/entity-update", response_model=AgentDecisionBundle)
def submit_entity_update_proposal(
    request: EntityUpdateProposalRequest,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentDecisionBundle:
    bundle = runtime.governance_service.create_entity_update_proposal(
        request.entity_id,
        request.changes,
        proposed_by=request.proposed_by,
        rationale=request.rationale,
        evidence_refs=request.evidence_refs,
    )
    return AgentDecisionBundle(**bundle)


def _load_tree_publication_artifact(
    request: Request,
    domain_id: str,
    filename: str,
    resource_name: str,
) -> AgentPublicationArtifact:
    tree_root = _tree_root(request)
    artifact_path = tree_root / "domains" / domain_id / "projections" / filename
    if not artifact_path.exists():
        raise _not_found(resource_name, f"{domain_id}/projections/{filename}")
    status = _load_tree_status(request)
    return AgentPublicationArtifact(
        domain_id=domain_id,
        tree_path=artifact_path.relative_to(tree_root).as_posix(),
        publication_timestamp=status.publication_timestamp,
        publication_version=status.publication_version,
        freshness_status=status.freshness_status,
        content=artifact_path.read_text(encoding="utf-8"),
    )


@router.post("/proposals/relation-create", response_model=AgentDecisionBundle)
def submit_relation_create_proposal(
    request: RelationCreateProposalRequest,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentDecisionBundle:
    relation_data: dict[str, Any] = {
        "relation_id": request.relation_id,
        "source_entity_id": request.source_entity_id,
        "target_entity_id": request.target_entity_id,
        "relation_type": request.relation_type,
        "directionality": request.directionality,
        "domain_context": request.domain_context,
        "asserted_by": request.asserted_by,
        "confidence": request.confidence,
        "validation_status": request.validation_status,
        "validated_by": request.validated_by,
        "evidence_refs": request.evidence_refs,
    }
    bundle = runtime.governance_service.create_relation_create_proposal(
        relation_data,
        proposed_by=request.proposed_by,
        rationale=request.rationale,
        evidence_refs=request.evidence_refs,
    )
    return AgentDecisionBundle(**bundle)


@router.post("/proposals/merge", response_model=AgentDecisionBundle)
def submit_merge_proposal(
    request: StructuredProposalRequest,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentDecisionBundle:
    bundle = runtime.governance_service.create_structured_proposal(
        proposal_type="merge",
        target_object_type=request.target_object_type,
        target_object_id=request.target_object_id,
        proposed_changes=request.proposed_changes,
        proposed_by=request.proposed_by,
        rationale=request.rationale,
        evidence_refs=request.evidence_refs,
    )
    return AgentDecisionBundle(**bundle)


@router.post("/proposals/payload-edit", response_model=AgentDecisionBundle)
def submit_payload_edit_proposal(
    request: StructuredProposalRequest,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentDecisionBundle:
    bundle = runtime.governance_service.create_structured_proposal(
        proposal_type="payload_edit",
        target_object_type=request.target_object_type,
        target_object_id=request.target_object_id,
        proposed_changes=request.proposed_changes,
        proposed_by=request.proposed_by,
        rationale=request.rationale,
        evidence_refs=request.evidence_refs,
    )
    return AgentDecisionBundle(**bundle)


@router.post("/proposals/reentry", response_model=AgentDecisionBundle)
def submit_reentry_proposal(
    request: StructuredProposalRequest,
    runtime: RuntimeContext = Depends(get_runtime),
) -> AgentDecisionBundle:
    bundle = runtime.governance_service.create_structured_proposal(
        proposal_type="reentry",
        target_object_type=request.target_object_type,
        target_object_id=request.target_object_id,
        proposed_changes=request.proposed_changes,
        proposed_by=request.proposed_by,
        rationale=request.rationale,
        evidence_refs=request.evidence_refs,
    )
    return AgentDecisionBundle(**bundle)
