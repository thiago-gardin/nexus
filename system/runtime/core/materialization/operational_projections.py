from __future__ import annotations

from typing import Any


def build_domain_review_queue(runtime: Any, domain_id: str) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    pending_entries: list[dict[str, Any]] = []
    for proposal in runtime.governance_service.list_proposals(proposal_state="pending"):
        entry = _build_review_entry(runtime, proposal)
        if entry is None or entry["domain_id"] != domain_id:
            continue
        pending_entries.append(entry)

    pending_entries.sort(
        key=lambda entry: (
            entry["proposal"].get("created_at") or "",
            entry["proposal"]["proposal_id"],
        ),
        reverse=True,
    )

    return {
        "domain": domain,
        "pending_proposals": pending_entries,
        "pending_proposal_count": len(pending_entries),
    }


def build_domain_operational_summary(runtime: Any, domain_id: str) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
    relations = [
        relation
        for relation in runtime.relation_service.list_relations()
        if relation.get("domain_context") == domain_id
    ]
    review_queue = build_domain_review_queue(runtime, domain_id)

    recent_entries: list[dict[str, Any]] = []
    approved_count = 0
    rejected_count = 0
    for bundle in runtime.governance_service.list_decisions(decision_state=None):
        decision = bundle["decision"]
        decision_state = decision.get("decision_state")
        if decision_state not in {"approved", "rejected"}:
            continue
        entry = _build_review_entry(runtime, bundle["proposal"], decision=decision)
        if entry is None or entry["domain_id"] != domain_id:
            continue
        recent_entries.append(entry)
        if decision_state == "approved":
            approved_count += 1
        elif decision_state == "rejected":
            rejected_count += 1

    recent_entries.sort(
        key=lambda entry: (
            entry["decision"].get("updated_at") or entry["decision"].get("created_at") or "",
            entry["decision"]["decision_id"],
        ),
        reverse=True,
    )

    return {
        "domain": domain,
        "entity_count": len(entities),
        "relation_count": len(relations),
        "pending_proposal_count": review_queue["pending_proposal_count"],
        "approved_decision_count": approved_count,
        "rejected_decision_count": rejected_count,
        "recent_decisions": recent_entries,
        "pending_proposals": review_queue["pending_proposals"],
    }


def build_domain_active_decision_queue(runtime: Any, domain_id: str) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    active_items: list[dict[str, Any]] = []
    pending_proposals = runtime.governance_service.list_proposals(proposal_state="pending")
    for proposal in pending_proposals:
        entry = _build_review_entry(runtime, proposal)
        if entry is None or entry["domain_id"] != domain_id:
            continue
        active_items.append(
            _build_active_queue_entry(
                entry,
                item_kind="pending_proposal",
                item_status="pending",
                next_action="review",
            )
        )

    closed_decision_bundles = runtime.governance_service.list_decisions(decision_state=None)
    for bundle in closed_decision_bundles:
        decision = bundle["decision"]
        decision_state = decision.get("decision_state")
        if decision_state not in {"approved", "rejected"}:
            continue
        entry = _build_review_entry(runtime, bundle["proposal"], decision=decision)
        if entry is None or entry["domain_id"] != domain_id:
            continue
        active_items.append(
            _build_active_queue_entry(
                entry,
                item_kind="recent_decision",
                item_status=decision_state,
                next_action="observe",
            )
        )

    active_items.sort(
        key=lambda entry: (
            1 if entry["kind"] == "pending_proposal" else 0,
            entry["sort_timestamp"] or "",
            entry["sort_id"],
        ),
        reverse=True,
    )

    approved_count = 0
    rejected_count = 0
    for item in active_items:
        if item["status"] == "approved":
            approved_count += 1
        elif item["status"] == "rejected":
            rejected_count += 1

    pending_count = sum(1 for item in active_items if item["status"] == "pending")
    return {
        "domain": domain,
        "active_items": active_items,
        "active_item_count": len(active_items),
        "pending_proposal_count": pending_count,
        "approved_decision_count": approved_count,
        "rejected_decision_count": rejected_count,
    }


def build_domain_recent_changes(runtime: Any, domain_id: str, limit: int = 8) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    change_entries: list[dict[str, Any]] = []
    for event in runtime.event_service.list_events():
        entry = _build_recent_change_entry(runtime, event)
        if entry is None or entry["domain_id"] != domain_id:
            continue
        change_entries.append(entry)

    change_entries.sort(
        key=lambda entry: (
            entry["sort_timestamp"] or "",
            entry["event"]["event_id"],
        ),
        reverse=True,
    )

    recent_changes = change_entries[:limit]
    return {
        "domain": domain,
        "recent_changes": recent_changes,
        "recent_change_count": len(change_entries),
        "latest_event_id": recent_changes[0]["event"]["event_id"] if recent_changes else None,
    }


def build_domain_meeting_context(runtime: Any, domain_id: str) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
    relations = [
        relation
        for relation in runtime.relation_service.list_relations()
        if relation.get("domain_context") == domain_id
    ]
    review_queue = build_domain_review_queue(runtime, domain_id)
    recent_changes = build_domain_recent_changes(runtime, domain_id, limit=5)
    return {
        "domain": domain,
        "agenda_seed": [
            "Review pending proposals",
            "Inspect recent object changes",
            "Confirm canonicalization candidates before promotion",
        ],
        "entity_highlights": entities[:10],
        "relation_highlights": relations[:10],
        "pending_proposals": review_queue["pending_proposals"],
        "pending_proposal_count": review_queue["pending_proposal_count"],
        "recent_changes": recent_changes["recent_changes"],
        "recent_change_count": recent_changes["recent_change_count"],
    }


def build_domain_project_state(runtime: Any, domain_id: str) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)

    entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
    relations = [
        relation
        for relation in runtime.relation_service.list_relations()
        if relation.get("domain_context") == domain_id
    ]
    sources = _list_if_available(runtime, "source_service", "list_sources", domain_id=domain_id)
    payloads = [
        payload
        for payload in _list_if_available(runtime, "payload_service", "list_payloads")
        if _payload_belongs_to_domain(runtime, payload, domain_id)
    ]
    projections = [
        projection
        for projection in _list_if_available(runtime, "projection_service", "list_projections")
        if _projection_belongs_to_domain(runtime, projection, domain_id)
    ]
    operational_summary = build_domain_operational_summary(runtime, domain_id)
    return {
        "domain": domain,
        "counts": {
            "entities": len(entities),
            "relations": len(relations),
            "sources": len(sources),
            "payloads": len(payloads),
            "projections": len(projections),
            "pending_proposals": operational_summary["pending_proposal_count"],
            "approved_decisions": operational_summary["approved_decision_count"],
            "rejected_decisions": operational_summary["rejected_decision_count"],
        },
        "entities": entities,
        "relations": relations,
        "sources": sources,
        "payloads": payloads,
        "projections": projections,
        "operational_summary": operational_summary,
    }


def _build_active_queue_entry(
    review_entry: dict[str, Any],
    *,
    item_kind: str,
    item_status: str,
    next_action: str,
) -> dict[str, Any]:
    proposal = review_entry["proposal"]
    decision = review_entry["decision"] or {}
    sort_timestamp = proposal.get("created_at") or decision.get("updated_at") or decision.get("created_at") or ""
    item_id = proposal["proposal_id"] if item_kind == "pending_proposal" else decision.get("decision_id") or proposal["proposal_id"]
    return {
        "kind": item_kind,
        "status": item_status,
        "next_action": next_action,
        "proposal_id": proposal["proposal_id"],
        "decision_id": decision.get("decision_id") or proposal.get("decision_id"),
        "proposal": proposal,
        "decision": review_entry["decision"],
        "history": review_entry["history"],
        "current_object": review_entry["current_object"],
        "domain_id": review_entry["domain_id"],
        "snapshot_path": review_entry["snapshot_path"],
        "object_version": review_entry["object_version"],
        "history_version_count": review_entry["history_version_count"],
        "latest_version_number": review_entry["latest_version_number"],
        "sort_timestamp": sort_timestamp,
        "sort_id": item_id,
    }


def _build_recent_change_entry(runtime: Any, event: dict[str, Any]) -> dict[str, Any] | None:
    target_object_type = event["target_object_type"]
    target_object_id = event["target_object_id"]

    if target_object_type == "decision":
        if event["event_type"] not in {"decision.approved", "decision.rejected"}:
            return None
        bundle = runtime.governance_service.get_decision_by_id(target_object_id)
        if bundle is None:
            return None
        proposal = bundle["proposal"]
        decision = bundle["decision"]
        target_object_type = proposal["target_object_type"]
        target_object_id = proposal["target_object_id"]
        history = runtime.governance_service.get_object_history(target_object_type, target_object_id)
        current_object = history.get("current_object")
        domain_id = _resolve_domain_id(runtime, target_object_type, proposal, current_object)
        if domain_id is None:
            return None
        snapshot_path = _snapshot_path_for_object(target_object_type, target_object_id, current_object)
        return {
            "event": event,
            "proposal": proposal,
            "decision": decision,
            "history": history,
            "current_object": current_object,
            "domain_id": domain_id,
            "snapshot_path": snapshot_path,
            "object_version": current_object.get("version") if current_object is not None else None,
            "history_version_count": history["version_count"],
            "latest_version_number": history["latest_version_number"],
            "sort_timestamp": event.get("created_at") or decision.get("updated_at") or decision.get("created_at") or "",
        }

    if target_object_type not in {"domain", "entity", "relation", "payload", "projection"}:
        return None

    history = runtime.governance_service.get_object_history(target_object_type, target_object_id)
    current_object = history.get("current_object")
    domain_id = _resolve_domain_id(runtime, target_object_type, {}, current_object)
    if domain_id is None:
        return None
    snapshot_path = _snapshot_path_for_object(target_object_type, target_object_id, current_object)
    return {
        "event": event,
        "proposal": None,
        "decision": None,
        "history": history,
        "current_object": current_object,
        "domain_id": domain_id,
        "snapshot_path": snapshot_path,
        "object_version": current_object.get("version") if current_object is not None else None,
        "history_version_count": history["version_count"],
        "latest_version_number": history["latest_version_number"],
        "sort_timestamp": event.get("created_at") or "",
    }


def _build_review_entry(
    runtime: Any,
    proposal: dict[str, Any],
    *,
    decision: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    target_object_type = proposal["target_object_type"]
    target_object_id = proposal["target_object_id"]
    if decision is None and proposal.get("decision_id"):
        bundle = runtime.governance_service.get_decision_by_id(proposal["decision_id"])
        if bundle is not None:
            decision = bundle["decision"]
            proposal = bundle["proposal"]

    history = runtime.governance_service.get_object_history(target_object_type, target_object_id)
    current_object = history.get("current_object")
    domain_id = _resolve_domain_id(runtime, target_object_type, proposal, current_object)
    if domain_id is None:
        return None

    snapshot_path = _snapshot_path_for_object(target_object_type, target_object_id, current_object)
    return {
        "proposal": proposal,
        "decision": decision,
        "history": history,
        "current_object": current_object,
        "domain_id": domain_id,
        "snapshot_path": snapshot_path,
        "object_version": current_object.get("version") if current_object is not None else None,
        "history_version_count": history["version_count"],
        "latest_version_number": history["latest_version_number"],
    }


def _resolve_domain_id(
    runtime: Any,
    object_type: str,
    proposal: dict[str, Any],
    current_object: dict[str, Any] | None,
) -> str | None:
    if object_type == "entity":
        if current_object is not None:
            return current_object.get("domain_id")
        return proposal.get("domain_id")
    if object_type == "relation":
        if current_object is not None:
            domain_id = current_object.get("domain_context")
            if domain_id:
                return domain_id
        proposed_changes = proposal.get("proposed_changes") or {}
        domain_id = proposed_changes.get("domain_context")
        if domain_id:
            return domain_id
        return proposal.get("domain_context")
    if object_type == "domain":
        if current_object is not None:
            return current_object.get("domain_id")
        return proposal.get("target_object_id")
    if object_type == "payload" and current_object is not None:
        return _domain_id_for_payload(runtime, current_object)
    if object_type == "projection" and current_object is not None:
        return _domain_id_for_projection(runtime, current_object)
    return None


def _list_if_available(runtime: Any, service_name: str, method_name: str, **kwargs: Any) -> list[dict[str, Any]]:
    service = getattr(runtime, service_name, None)
    if service is None:
        return []
    method = getattr(service, method_name, None)
    if method is None:
        return []
    try:
        return list(method(**kwargs))
    except TypeError:
        return list(method())


def _payload_belongs_to_domain(runtime: Any, payload: dict[str, Any], domain_id: str) -> bool:
    owner_type = payload.get("owner_object_type")
    owner_id = payload.get("owner_object_id")
    if owner_type == "domain":
        return owner_id == domain_id
    if owner_type == "source":
        source = getattr(runtime, "source_service", None).get_source_by_id(owner_id) if getattr(runtime, "source_service", None) else None
        return bool(source and source.get("domain_id") == domain_id)
    if owner_type == "entity":
        entity = runtime.entity_service.get_entity_by_id(owner_id)
        return bool(entity and entity.get("domain_id") == domain_id)
    if owner_type == "relation":
        relation = runtime.relation_service.get_relation_by_id(owner_id)
        return bool(relation and relation.get("domain_context") == domain_id)
    return False


def _projection_belongs_to_domain(runtime: Any, projection: dict[str, Any], domain_id: str) -> bool:
    for source_ref in projection.get("source_refs") or []:
        if source_ref == domain_id:
            return True
        entity = runtime.entity_service.get_entity_by_id(str(source_ref))
        if entity and entity.get("domain_id") == domain_id:
            return True
        relation = runtime.relation_service.get_relation_by_id(str(source_ref))
        if relation and relation.get("domain_context") == domain_id:
            return True
    for payload_ref in projection.get("payload_refs") or []:
        payload = getattr(runtime, "payload_service", None).get_payload_by_id(str(payload_ref)) if getattr(runtime, "payload_service", None) else None
        if payload and _payload_belongs_to_domain(runtime, payload, domain_id):
            return True
    return False


def _domain_id_for_payload(runtime: Any, payload: dict[str, Any]) -> str | None:
    if runtime is None or getattr(runtime, "domain_service", None) is None:
        return None
    for domain in runtime.domain_service.list_domains():
        if _payload_belongs_to_domain(runtime, payload, domain["domain_id"]):
            return domain["domain_id"]
    return None


def _domain_id_for_projection(runtime: Any, projection: dict[str, Any]) -> str | None:
    if runtime is None or getattr(runtime, "domain_service", None) is None:
        return None
    for domain in runtime.domain_service.list_domains():
        if _projection_belongs_to_domain(runtime, projection, domain["domain_id"]):
            return domain["domain_id"]
    return None


def _snapshot_path_for_object(
    object_type: str,
    object_id: str,
    current_object: dict[str, Any] | None,
) -> str | None:
    if current_object is None:
        return None
    if object_type == "entity":
        return f"../entities/{object_id}.md"
    if object_type == "relation":
        return f"../relations/{object_id}.md"
    if object_type == "domain":
        return "../DOMAIN_CONTRACT.yaml"
    if object_type == "payload":
        return f"../payloads/{object_id}.md"
    if object_type == "projection":
        return f"./{object_id}.md"
    return None
