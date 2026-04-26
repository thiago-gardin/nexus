from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..dependencies import RuntimeContext, get_runtime


router = APIRouter(tags=["governance"])


class DecisionActionPayload(BaseModel):
    decided_by: str = "system"
    rationale: str | None = None


class StructuredProposalPayload(BaseModel):
    target_object_type: str
    target_object_id: str
    proposed_changes: dict[str, Any]
    proposed_by: str = "system"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)


class EntityUpdateProposalPayload(BaseModel):
    entity_id: str
    changes: dict[str, Any]
    proposed_by: str = "system"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)


class RelationCreateProposalPayload(BaseModel):
    relation_data: dict[str, Any]
    proposed_by: str = "system"
    rationale: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)


class GovernanceRulePayload(BaseModel):
    rule_type: str
    name: str
    scope: str
    logic_description: str
    human_readable_repr: str
    applies_to: list[Any] = Field(default_factory=list)
    priority: int = 0
    created_by: str = "system"
    machine_executable_repr: str | None = None
    status: str | None = None


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


@router.get("/rules")
def list_rules(
    scope: str | None = None,
    status: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[dict[str, Any]]:
    return runtime.governance_rule_service.list_rules(scope=scope, status=status)


@router.get("/rules/{rule_id}")
def get_rule(rule_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    rule = runtime.governance_rule_service.get_rule_by_id(rule_id)
    if rule is None:
        raise _not_found("rule", rule_id)
    return rule


@router.post("/rules")
def create_rule(
    payload: GovernanceRulePayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    rule_data = payload.model_dump(exclude_none=True)
    return runtime.governance_rule_service.create_rule(rule_data)


@router.post("/rules/{rule_id}/activate")
def activate_rule(
    rule_id: str,
    payload: DecisionActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or DecisionActionPayload()
    try:
        return runtime.governance_rule_service.update_rule_status(
            rule_id,
            "active",
            performed_by=action.decided_by,
            performed_via="api",
            rationale=action.rationale,
        )
    except KeyError as exc:
        raise _not_found("rule", rule_id) from exc


@router.post("/rules/{rule_id}/deactivate")
def deactivate_rule(
    rule_id: str,
    payload: DecisionActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or DecisionActionPayload()
    try:
        return runtime.governance_rule_service.update_rule_status(
            rule_id,
            "inactive",
            performed_by=action.decided_by,
            performed_via="api",
            rationale=action.rationale,
        )
    except KeyError as exc:
        raise _not_found("rule", rule_id) from exc


@router.get("/proposals")
def list_proposals(runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    return runtime.governance_service.list_proposals()


@router.get("/proposals/{proposal_id}")
def get_proposal(proposal_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    proposal = runtime.governance_service.get_proposal_by_id(proposal_id)
    if proposal is None:
        raise _not_found("proposal", proposal_id)
    return proposal


@router.post("/proposals/entity-update")
def create_entity_update_proposal(
    payload: EntityUpdateProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_entity_update_proposal(
        payload.entity_id,
        payload.changes,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.post("/proposals/relation-create")
def create_relation_create_proposal(
    payload: RelationCreateProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_relation_create_proposal(
        payload.relation_data,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.post("/proposals/merge")
def create_merge_proposal(
    payload: StructuredProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_structured_proposal(
        proposal_type="merge",
        target_object_type=payload.target_object_type,
        target_object_id=payload.target_object_id,
        proposed_changes=payload.proposed_changes,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.post("/proposals/decision")
def create_decision_suggestion_proposal(
    payload: StructuredProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_structured_proposal(
        proposal_type="decision_suggestion",
        target_object_type=payload.target_object_type,
        target_object_id=payload.target_object_id,
        proposed_changes=payload.proposed_changes,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.post("/proposals/payload-edit")
def create_payload_edit_proposal(
    payload: StructuredProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_structured_proposal(
        proposal_type="payload_edit",
        target_object_type=payload.target_object_type,
        target_object_id=payload.target_object_id,
        proposed_changes=payload.proposed_changes,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.post("/proposals/reentry")
def create_reentry_proposal(
    payload: StructuredProposalPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.create_structured_proposal(
        proposal_type="reentry",
        target_object_type=payload.target_object_type,
        target_object_id=payload.target_object_id,
        proposed_changes=payload.proposed_changes,
        proposed_by=payload.proposed_by,
        rationale=payload.rationale,
        evidence_refs=payload.evidence_refs,
    )


@router.get("/decisions")
def list_decisions(runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    return runtime.governance_service.list_decision_queue()


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    bundle = runtime.governance_service.get_decision_by_id(decision_id)
    if bundle is None:
        raise _not_found("decision", decision_id)
    return bundle


@router.post("/decisions/{decision_id}/approve")
def approve_decision(
    decision_id: str,
    payload: DecisionActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or DecisionActionPayload()
    return runtime.governance_service.approve(
        decision_id,
        decided_by=action.decided_by,
        performed_via="api",
        rationale=action.rationale,
    )


@router.post("/decisions/{decision_id}/reject")
def reject_decision(
    decision_id: str,
    payload: DecisionActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or DecisionActionPayload()
    return runtime.governance_service.reject(
        decision_id,
        decided_by=action.decided_by,
        performed_via="api",
        rationale=action.rationale,
    )


@router.post("/decisions/{decision_id}/override")
def override_decision(
    decision_id: str,
    payload: DecisionActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or DecisionActionPayload()
    return runtime.governance_service.override(
        decision_id,
        decided_by=action.decided_by,
        performed_via="api",
        rationale=action.rationale,
    )


@router.get("/objects/{object_type}/{object_id}/history")
def get_object_history(
    object_type: str,
    object_id: str,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    return runtime.governance_service.get_object_history(object_type, object_id)


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
