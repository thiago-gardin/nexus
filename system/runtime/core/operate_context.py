from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .materialization.operational_projections import build_domain_active_decision_queue
from .materialization.operational_projections import build_domain_recent_changes
from .materialization.operational_projections import build_domain_review_queue


def build_active_domain_charter(runtime: Any, domain_id: str) -> dict[str, Any]:
    active = runtime.domain_version_service.get_active_domain_version(domain_id)
    if active is None:
        return {
            "domain_id": domain_id,
            "domain_version_id": None,
            "version_label": None,
            "charter": {},
            "allowed_entity_types": [],
            "allowed_relation_types": [],
            "allowed_payload_types": [],
            "required_fields": {},
            "promotion_rules": [],
            "ui_schema": {},
        }
    return {
        "domain_id": domain_id,
        "domain_version_id": active.get("domain_version_id"),
        "version_label": active.get("version_label"),
        "charter": dict(active.get("charter") or {}),
        "allowed_entity_types": list(active.get("allowed_entity_types") or []),
        "allowed_relation_types": list(active.get("allowed_relation_types") or []),
        "allowed_payload_types": list(active.get("allowed_payload_types") or []),
        "required_fields": dict(active.get("required_fields") or {}),
        "promotion_rules": list(active.get("promotion_rules") or []),
        "ui_schema": dict(active.get("charter") or {}).get("ui_schema") or {},
    }


def build_operate_context(
    runtime: Any,
    domain_id: str | None = None,
    *,
    tree_root: Path | None = None,
    last_object_type: str | None = None,
    last_object_id: str | None = None,
    last_result: str | None = None,
) -> dict[str, Any]:
    domains = runtime.domain_service.list_domains()
    selected_domain = runtime.domain_service.get_domain_by_id(domain_id) if domain_id else None
    if domain_id and selected_domain is None:
        selected_domain = None
        domain_id = None

    domain_versions: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    ingestion_runs: list[dict[str, Any]] = []
    charter = build_active_domain_charter(runtime, domain_id) if domain_id else build_active_domain_charter(runtime, "__none__")
    active_version = None
    publication = _empty_publication_status()
    recent_event = None
    pending_review_count = 0
    recent_changes: list[dict[str, Any]] = []
    review_queue: list[dict[str, Any]] = []
    active_decision_items: list[dict[str, Any]] = []
    domain_record = selected_domain or {}

    if domain_id is not None:
        active_version = runtime.domain_version_service.get_active_domain_version(domain_id)
        domain_versions = runtime.domain_version_service.list_domain_versions(domain_id=domain_id)
        sources = runtime.source_service.list_sources(domain_id=domain_id)
        entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
        relations = [relation for relation in runtime.relation_service.list_relations() if relation.get("domain_context") == domain_id]
        ingestion_runs = [
            job
            for job in runtime.ingestion_job_service.list_jobs()
            if job.get("target_ref") == f"domain:{domain_id}"
        ]
        charter = build_active_domain_charter(runtime, domain_id)
        publication = _build_publication_status(
            runtime,
            domain_id,
            tree_root=tree_root,
            domain=selected_domain,
            active_version=active_version,
            sources=sources,
            entities=entities,
            relations=relations,
        )
        recent_event = _build_recent_event(runtime, domain_id, entities=entities, relations=relations, sources=sources)
        pending_review_count = sum(
            1
            for candidate in [*entities, *relations]
            if candidate.get("validation_status") in {"proposed", "contested"}
        )
        recent_changes = _summarize_recent_changes(runtime, domain_id)
        review_queue = _summarize_review_queue(runtime, domain_id)
        active_decision_items = _summarize_active_decisions(runtime, domain_id)

    last_object = _resolve_last_object(runtime, last_object_type, last_object_id)
    entity_type_options = _resolve_entity_type_options(domain_record, charter, entities)
    relation_type_options = _resolve_relation_type_options(domain_record, charter, relations)
    source_type_options = _resolve_source_type_options(domain_record, sources)
    entity_picker_options = _build_entity_picker_options(entities)
    object_picker_options = _build_object_picker_options(entities, relations)
    ui_schema = _build_ui_schema(
        charter=charter,
        entity_types=entity_type_options,
        relation_types=relation_type_options,
        entities=entities,
    )
    next_actions = _build_next_actions(
        domain_id=domain_id,
        has_active_version=active_version is not None,
        entities=entities,
        relations=relations,
        sources=sources,
        domain_versions=domain_versions,
        last_object=last_object,
        pending_review_count=pending_review_count,
        publication_state=publication["status"],
    )

    return {
        "available_domains": [
            {
                "domain_id": record["domain_id"],
                "name": record.get("name") or record["domain_id"],
                "status": record.get("status"),
            }
            for record in domains
        ],
        "domain_id": domain_id,
        "domain_name": selected_domain.get("name") if selected_domain else None,
        "domain_status": selected_domain.get("status") if selected_domain else None,
        "active_domain_version_id": active_version.get("domain_version_id") if active_version else None,
        "active_domain_version_label": active_version.get("version_label") if active_version else None,
        "domain_version_count": len(domain_versions),
        "domain_versions": [
            {
                "domain_version_id": version["domain_version_id"],
                "version_label": version.get("version_label") or version["domain_version_id"],
                "status": version.get("status"),
            }
            for version in domain_versions
        ],
        "last_object": last_object,
        "last_result": last_result,
        "publication": publication,
        "charter": charter,
        "counts": {
            "sources": len(sources),
            "entities": len(entities),
            "relations": len(relations),
            "ingestion_runs": len(ingestion_runs),
            "pending_review": pending_review_count,
        },
        "recent_event": recent_event,
        "next_actions": next_actions,
        "source_type_options": source_type_options,
        "entity_type_options": entity_type_options,
        "relation_type_options": relation_type_options,
        "entity_picker_options": entity_picker_options,
        "object_picker_options": object_picker_options,
        "ui_schema": ui_schema,
        "recent_changes": recent_changes,
        "review_queue": review_queue,
        "active_decisions": active_decision_items,
    }


def _resolve_last_object(runtime: Any, object_type: str | None, object_id: str | None) -> dict[str, Any] | None:
    if not object_type or not object_id:
        return None
    record = None
    label = object_id
    if object_type == "domain":
        record = runtime.domain_service.get_domain_by_id(object_id)
        label = (record or {}).get("name") or object_id
    elif object_type == "domain_version":
        record = runtime.domain_version_service.get_domain_version_by_id(object_id)
        label = (record or {}).get("version_label") or object_id
    elif object_type == "source":
        record = runtime.source_service.get_source_by_id(object_id)
        label = (record or {}).get("source_uri") or (record or {}).get("source_id") or object_id
    elif object_type == "entity":
        record = runtime.entity_service.get_entity_by_id(object_id)
        label = (record or {}).get("label") or object_id
    elif object_type == "relation":
        record = runtime.relation_service.get_relation_by_id(object_id)
        label = (record or {}).get("relation_type") or object_id
    elif object_type == "payload":
        record = runtime.payload_service.get_payload_by_id(object_id)
    elif object_type == "event":
        record = runtime.event_service.get_event_by_id(object_id)
        label = (record or {}).get("event_type") or object_id
    if record is None:
        return None
    return {
        "type": object_type,
        "id": object_id,
        "label": label,
        "status": record.get("status") or record.get("validation_status") or record.get("ingestion_status"),
    }


def _build_publication_status(
    runtime: Any,
    domain_id: str,
    *,
    tree_root: Path | None,
    domain: dict[str, Any] | None,
    active_version: dict[str, Any] | None,
    sources: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> dict[str, Any]:
    completed_jobs = [
        job
        for job in runtime.materialization_job_service.list_jobs(status="completed")
        if job.get("job_type") == "domain_materialization" and job.get("target_ref") == f"domain:{domain_id}"
    ]
    latest_job = max(completed_jobs, key=lambda item: item.get("finished_at") or item.get("started_at") or "", default=None)
    latest_change_at = max(
        [
            timestamp
            for timestamp in [
                (domain or {}).get("updated_at"),
                (active_version or {}).get("updated_at"),
                *[source.get("updated_at") for source in sources],
                *[entity.get("updated_at") for entity in entities],
                *[relation.get("updated_at") for relation in relations],
            ]
            if timestamp
        ],
        default=None,
    )
    if latest_job is None:
        status = "not_materialized"
    elif latest_change_at is None or (latest_job.get("finished_at") or "") >= latest_change_at:
        status = "materialized"
    else:
        status = "out_of_sync"
    tree_domain_path = tree_root / "domains" / domain_id if tree_root is not None else None
    return {
        "status": status,
        "last_materialization_job_id": latest_job.get("job_id") if latest_job else None,
        "last_materialized_at": latest_job.get("finished_at") if latest_job else None,
        "latest_runtime_change_at": latest_change_at,
        "tree_domain_path": str(tree_domain_path) if tree_domain_path is not None else None,
    }


def _build_recent_event(
    runtime: Any,
    domain_id: str,
    *,
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> dict[str, Any] | None:
    events = list(runtime.event_service.list_events(target_object_type="domain", target_object_id=domain_id))
    for entity in entities:
        events.extend(runtime.event_service.list_events(target_object_type="entity", target_object_id=entity["entity_id"]))
    for relation in relations:
        events.extend(runtime.event_service.list_events(target_object_type="relation", target_object_id=relation["relation_id"]))
    for source in sources:
        events.extend(runtime.event_service.list_events(target_object_type="source", target_object_id=source["source_id"]))
    if not events:
        return None
    latest = max(events, key=lambda item: item.get("created_at") or "")
    return {
        "event_id": latest.get("event_id"),
        "event_type": latest.get("event_type"),
        "target_object_type": latest.get("target_object_type"),
        "target_object_id": latest.get("target_object_id"),
        "performed_by": latest.get("performed_by"),
        "created_at": latest.get("created_at"),
    }


def _build_next_actions(
    *,
    domain_id: str | None,
    has_active_version: bool,
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    domain_versions: list[dict[str, Any]],
    last_object: dict[str, Any] | None,
    pending_review_count: int,
    publication_state: str,
) -> list[dict[str, Any]]:
    if domain_id is None:
        return [
            {"label": "Create a domain", "href": "#create-domain", "intent": "primary"},
            {"label": "Select an existing domain", "href": "#workspace-context", "intent": "secondary"},
        ]
    if not domain_versions:
        return [{"label": "Create a domain version", "href": "#domain-version", "intent": "primary"}]
    if not has_active_version:
        return [{"label": "Activate the latest domain version", "href": "#activate-version", "intent": "primary"}]

    actions: list[dict[str, Any]] = []
    if last_object and last_object.get("type") == "entity" and last_object.get("status") == "proposed":
        actions.append({"label": "Validate the last entity", "href": "#validate-object", "intent": "primary"})
    if last_object and last_object.get("type") == "relation" and last_object.get("status") == "proposed":
        actions.append({"label": "Validate the last relation", "href": "#validate-object", "intent": "primary"})
    if publication_state in {"not_materialized", "out_of_sync"}:
        actions.append({"label": "Materialize the domain", "href": "#materialize-domain", "intent": "primary"})
    if not sources:
        actions.append({"label": "Register the first source", "href": "#source-ingestion", "intent": "secondary"})
    if not entities:
        actions.append({"label": "Create the first entity", "href": "#entity-relation", "intent": "secondary"})
    elif not relations:
        actions.append({"label": "Create a relation", "href": "#entity-relation", "intent": "secondary"})
    if pending_review_count:
        actions.append({"label": f"Review {pending_review_count} pending objects", "href": "#validate-object", "intent": "secondary"})
    if not actions:
        actions.append({"label": "Continue authoring in this domain", "href": "#entity-relation", "intent": "secondary"})
    return actions


def _empty_publication_status() -> dict[str, Any]:
    return {
        "status": "not_materialized",
        "last_materialization_job_id": None,
        "last_materialized_at": None,
        "latest_runtime_change_at": None,
        "tree_domain_path": None,
    }


def _resolve_entity_type_options(
    domain_record: dict[str, Any],
    charter: dict[str, Any],
    entities: list[dict[str, Any]],
) -> list[str]:
    ordered: list[str] = []
    for candidate in [
        *(charter.get("allowed_entity_types") or []),
        *(domain_record.get("local_entity_types") or []),
        *[entity.get("entity_type") for entity in entities],
    ]:
        normalized = str(candidate or "").strip()
        if normalized and normalized not in ordered:
            ordered.append(normalized)
    return ordered


def _resolve_relation_type_options(
    domain_record: dict[str, Any],
    charter: dict[str, Any],
    relations: list[dict[str, Any]],
) -> list[str]:
    ordered: list[str] = []
    for candidate in [
        *(charter.get("allowed_relation_types") or []),
        *(domain_record.get("relation_types") or []),
        *[relation.get("relation_type") for relation in relations],
    ]:
        normalized = str(candidate or "").strip()
        if normalized and normalized not in ordered:
            ordered.append(normalized)
    return ordered


def _resolve_source_type_options(
    domain_record: dict[str, Any],
    sources: list[dict[str, Any]],
) -> list[str]:
    ordered: list[str] = []
    for candidate in [*(domain_record.get("source_types_supported") or []), *[source.get("source_type") for source in sources], "md", "json", "txt"]:
        normalized = str(candidate or "").strip()
        if normalized and normalized not in ordered:
            ordered.append(normalized)
    return ordered


def _build_entity_picker_options(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        entities,
        key=lambda item: (
            str(item.get("label") or "").casefold(),
            str(item.get("entity_type") or "").casefold(),
            str(item.get("entity_id") or ""),
        ),
    )
    return [
        {
            "id": entity["entity_id"],
            "label": entity.get("label") or entity["entity_id"],
            "entity_type": entity.get("entity_type"),
            "validation_status": entity.get("validation_status"),
            "domain_id": entity.get("domain_id"),
        }
        for entity in ordered
    ]


def _build_object_picker_options(
    entities: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for entity in entities:
        if entity.get("validation_status") not in {"proposed", "contested"}:
            continue
        options.append(
            {
                "value": f"entity:{entity['entity_id']}",
                "object_type": "entity",
                "object_id": entity["entity_id"],
                "label": entity.get("label") or entity["entity_id"],
                "description": f"{entity.get('entity_type') or 'entity'} / {entity.get('validation_status') or 'unknown'}",
            }
        )
    for relation in relations:
        if relation.get("validation_status") not in {"proposed", "contested"}:
            continue
        options.append(
            {
                "value": f"relation:{relation['relation_id']}",
                "object_type": "relation",
                "object_id": relation["relation_id"],
                "label": relation.get("relation_type") or relation["relation_id"],
                "description": f"relation / {relation.get('validation_status') or 'unknown'}",
            }
        )
    return options


def _build_ui_schema(
    *,
    charter: dict[str, Any],
    entity_types: list[str],
    relation_types: list[str],
    entities: list[dict[str, Any]],
) -> dict[str, Any]:
    charter_ui = charter.get("ui_schema") or {}
    entity_forms = dict(charter_ui.get("entity_forms") or {})
    relation_forms = dict(charter_ui.get("relation_forms") or {})
    required_fields = charter.get("required_fields") or {}

    inferred_entity_forms: dict[str, Any] = {}
    for entity_type in entity_types:
        existing = entity_forms.get(entity_type)
        if isinstance(existing, dict) and existing.get("fields"):
            inferred_entity_forms[entity_type] = existing
            continue
        observed_entities = [entity for entity in entities if entity.get("entity_type") == entity_type]
        observed_keys: list[str] = []
        observed_values: dict[str, list[Any]] = {}
        for entity in observed_entities:
            attributes = entity.get("attributes") or {}
            if not isinstance(attributes, dict):
                continue
            for key, value in attributes.items():
                field_name = str(key)
                if field_name not in observed_keys:
                    observed_keys.append(field_name)
                observed_values.setdefault(field_name, []).append(value)
        required = required_fields.get(entity_type) if isinstance(required_fields, dict) else None
        required_list = [str(item) for item in required] if isinstance(required, list) else []
        field_names = list(required_list)
        for key in observed_keys:
            if key not in field_names:
                field_names.append(key)
        fields = [
            _build_field_schema(field_name, observed_values.get(field_name) or [], required=field_name in required_list)
            for field_name in field_names
        ]
        inferred_entity_forms[entity_type] = {
            "title": _humanize(entity_type),
            "fields": fields,
        }

    inferred_relation_forms: dict[str, Any] = {}
    for relation_type in relation_types:
        existing = relation_forms.get(relation_type)
        inferred_relation_forms[relation_type] = existing if isinstance(existing, dict) else {"title": _humanize(relation_type), "fields": []}

    return {
        "entity_forms": inferred_entity_forms,
        "relation_forms": inferred_relation_forms,
    }


def _build_field_schema(name: str, observed_values: list[Any], *, required: bool) -> dict[str, Any]:
    normalized = name.casefold()
    options = _collect_select_options(observed_values)
    if options and len(options) <= 8:
        field_kind = "select"
    elif normalized.endswith("_flag") or normalized.startswith("is_") or normalized.startswith("has_"):
        field_kind = "checkbox"
    elif any(token in normalized for token in ("count", "score", "priority", "confidence")) or _observed_numbers(observed_values):
        field_kind = "number"
    elif any(token in normalized for token in ("description", "summary", "notes", "justification")):
        field_kind = "textarea"
    elif any(token in normalized for token in ("date", "_at", "timestamp")):
        field_kind = "datetime"
    else:
        field_kind = "text"
    return {
        "name": name,
        "label": _humanize(name),
        "kind": field_kind,
        "required": required,
        "options": options,
    }


def _collect_select_options(values: list[Any]) -> list[str]:
    options: list[str] = []
    for value in values:
        if value in {None, ""}:
            continue
        normalized = str(value)
        if normalized not in options:
            options.append(normalized)
    return options


def _observed_numbers(values: list[Any]) -> bool:
    if not values:
        return False
    for value in values:
        if value in {None, ""}:
            continue
        if isinstance(value, bool):
            return False
        if isinstance(value, (int, float)):
            continue
        return False
    return True


def _humanize(value: str) -> str:
    cleaned = re.sub(r"[_\-]+", " ", value).strip()
    if not cleaned:
        return value
    return cleaned[:1].upper() + cleaned[1:]


def _summarize_recent_changes(runtime: Any, domain_id: str) -> list[dict[str, Any]]:
    recent = build_domain_recent_changes(runtime, domain_id, limit=8)
    summary: list[dict[str, Any]] = []
    for entry in recent.get("recent_changes") or []:
        event = entry.get("event") or {}
        current = entry.get("current_object") or {}
        summary.append(
            {
                "event_id": event.get("event_id"),
                "event_type": event.get("event_type"),
                "created_at": event.get("created_at"),
                "target_object_type": event.get("target_object_type"),
                "target_object_id": event.get("target_object_id"),
                "label": current.get("label") or current.get("relation_type") or current.get("name") or event.get("target_object_id"),
                "status": current.get("validation_status") or current.get("status"),
            }
        )
    return summary


def _summarize_review_queue(runtime: Any, domain_id: str) -> list[dict[str, Any]]:
    review = build_domain_review_queue(runtime, domain_id)
    summary: list[dict[str, Any]] = []
    for entry in review.get("pending_proposals") or []:
        proposal = entry.get("proposal") or {}
        current = entry.get("current_object") or {}
        summary.append(
            {
                "proposal_id": proposal.get("proposal_id"),
                "proposal_type": proposal.get("proposal_type"),
                "target_object_type": proposal.get("target_object_type"),
                "target_object_id": proposal.get("target_object_id"),
                "label": current.get("label") or current.get("relation_type") or proposal.get("target_object_id"),
                "created_at": proposal.get("created_at"),
            }
        )
    return summary


def _summarize_active_decisions(runtime: Any, domain_id: str) -> list[dict[str, Any]]:
    queue = build_domain_active_decision_queue(runtime, domain_id)
    summary: list[dict[str, Any]] = []
    for item in queue.get("active_items") or []:
        proposal = item.get("proposal") or {}
        decision = item.get("decision") or {}
        current = item.get("current_object") or {}
        summary.append(
            {
                "kind": item.get("kind"),
                "status": item.get("status"),
                "next_action": item.get("next_action"),
                "proposal_id": proposal.get("proposal_id"),
                "decision_id": decision.get("decision_id"),
                "label": current.get("label") or current.get("relation_type") or proposal.get("target_object_id"),
                "sort_timestamp": item.get("sort_timestamp"),
            }
        )
    return summary
