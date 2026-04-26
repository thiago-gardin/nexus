from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def new_uuid() -> str:
    return str(uuid4())


def dumps_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def loads_json(value: str | None, default: Any) -> Any:
    if value is None or value == "":
        return default
    return json.loads(value)


def row_to_dict(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def ensure_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    raise TypeError(f"Expected mapping value, received {type(value)!r}")


DOMAIN_JSON_FIELDS = (
    "source_types_supported",
    "local_entity_types",
    "relation_types",
    "promotion_rules",
    "governance_dependencies",
)

DOMAIN_VERSION_JSON_FIELDS = (
    "charter",
    "allowed_entity_types",
    "allowed_relation_types",
    "allowed_payload_types",
    "required_fields",
    "promotion_rules",
)


def prepare_domain_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
        version = int(source.get("version") or 1)
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
        version = int(current["version"]) + 1
    record = {
        "domain_id": source.get("domain_id") or (current["domain_id"] if current else new_uuid()),
        "name": source["name"],
        "description": source["description"],
        "cognitive_purpose": source["cognitive_purpose"],
        "status": source.get("status") or "draft",
        "owner_human": source.get("owner_human"),
        "owner_agent": source.get("owner_agent"),
        "source_types_supported": dumps_json(ensure_list(source.get("source_types_supported"))),
        "local_entity_types": dumps_json(ensure_list(source.get("local_entity_types"))),
        "relation_types": dumps_json(ensure_list(source.get("relation_types"))),
        "promotion_rules": dumps_json(ensure_list(source.get("promotion_rules"))),
        "governance_dependencies": dumps_json(ensure_list(source.get("governance_dependencies"))),
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return record


def row_to_domain(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in DOMAIN_JSON_FIELDS:
        data[field] = loads_json(data[field], [])
    return data


def prepare_domain_version_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    created_at = source.get("created_at") or (current["created_at"] if current else utc_now())
    return {
        "domain_version_id": source.get("domain_version_id") or (current["domain_version_id"] if current else new_uuid()),
        "domain_id": source["domain_id"],
        "version_label": source["version_label"],
        "status": source.get("status") or "draft",
        "charter": dumps_json(ensure_mapping(source.get("charter"))),
        "allowed_entity_types": dumps_json(ensure_list(source.get("allowed_entity_types"))),
        "allowed_relation_types": dumps_json(ensure_list(source.get("allowed_relation_types"))),
        "allowed_payload_types": dumps_json(ensure_list(source.get("allowed_payload_types"))),
        "required_fields": dumps_json(ensure_mapping(source.get("required_fields"))),
        "promotion_rules": dumps_json(ensure_list(source.get("promotion_rules"))),
        "created_at": created_at,
        "activated_at": source.get("activated_at"),
        "last_event_id": source.get("last_event_id"),
    }


def row_to_domain_version(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in DOMAIN_VERSION_JSON_FIELDS:
        data[field] = loads_json(data[field], {} if field in {"charter", "required_fields"} else [])
    return data


ENTITY_JSON_FIELDS = ("attributes", "aliases", "provenance_refs", "payload_refs")


def prepare_entity_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
        version = int(source.get("version") or 1)
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
        version = int(current["version"]) + 1
    record = {
        "entity_id": source.get("entity_id") or (current["entity_id"] if current else new_uuid()),
        "scope": source.get("scope") or "local",
        "domain_id": source.get("domain_id"),
        "entity_type": source["entity_type"],
        "label": source["label"],
        "short_description": source.get("short_description"),
        "attributes": dumps_json(ensure_mapping(source.get("attributes"))),
        "aliases": dumps_json(ensure_list(source.get("aliases"))),
        "confidence": float(source.get("confidence") or 0.0),
        "validation_status": source.get("validation_status") or "proposed",
        "canonical_candidate_flag": int(bool(source.get("canonical_candidate_flag"))),
        "provenance_refs": dumps_json(ensure_list(source.get("provenance_refs"))),
        "payload_refs": dumps_json(ensure_list(source.get("payload_refs"))),
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return record


def row_to_entity(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["attributes"] = loads_json(data["attributes"], {})
    data["aliases"] = loads_json(data["aliases"], [])
    data["provenance_refs"] = loads_json(data["provenance_refs"], [])
    data["payload_refs"] = loads_json(data["payload_refs"], [])
    data["canonical_candidate_flag"] = bool(data["canonical_candidate_flag"])
    return data


RELATION_JSON_FIELDS = ("evidence_refs",)


def prepare_relation_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
        version = int(source.get("version") or 1)
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
        version = int(current["version"]) + 1
    record = {
        "relation_id": source.get("relation_id") or (current["relation_id"] if current else new_uuid()),
        "source_entity_id": source["source_entity_id"],
        "target_entity_id": source["target_entity_id"],
        "relation_type": source["relation_type"],
        "directionality": source.get("directionality") or "directed",
        "domain_context": source.get("domain_context"),
        "evidence_refs": dumps_json(ensure_list(source.get("evidence_refs"))),
        "confidence": float(source.get("confidence") or 0.0),
        "validation_status": source.get("validation_status") or "proposed",
        "asserted_by": source.get("asserted_by") or "system",
        "validated_by": source.get("validated_by"),
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return record


def row_to_relation(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["evidence_refs"] = loads_json(data["evidence_refs"], [])
    return data


def prepare_event_record(data: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(data)
    return {
        "event_id": source.get("event_id") or new_uuid(),
        "event_type": source["event_type"],
        "target_object_type": source["target_object_type"],
        "target_object_id": source["target_object_id"],
        "performed_by": source.get("performed_by") or "system",
        "performed_via": source.get("performed_via") or "system",
        "reason": source.get("reason"),
        "payload": dumps_json(source.get("payload") or {}),
        "before_state_ref": source.get("before_state_ref"),
        "after_state_ref": source.get("after_state_ref"),
        "reversible_flag": int(bool(source.get("reversible_flag"))),
        "created_at": source.get("created_at") or utc_now(),
    }


def row_to_event(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["payload"] = loads_json(data["payload"], {})
    data["reversible_flag"] = bool(data["reversible_flag"])
    return data


PROPOSAL_JSON_FIELDS = ("target_refs", "proposed_changes", "evidence_refs")


def prepare_proposal_record(data: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(data)
    target_refs = ensure_list(source.get("target_refs"))
    if not target_refs and source.get("target_object_id") is not None:
        target_refs = [source["target_object_id"]]
    return {
        "proposal_id": source.get("proposal_id") or new_uuid(),
        "proposal_type": source["proposal_type"],
        "target_object_type": source["target_object_type"],
        "target_object_id": source["target_object_id"],
        "target_refs": dumps_json(target_refs),
        "proposed_changes": dumps_json(ensure_mapping(source.get("proposed_changes"))),
        "proposed_by": source.get("proposed_by") or "system",
        "rationale": source.get("rationale"),
        "evidence_refs": dumps_json(ensure_list(source.get("evidence_refs"))),
        "proposal_state": source.get("proposal_state") or "pending",
        "decision_id": source.get("decision_id"),
        "created_at": source.get("created_at") or utc_now(),
        "updated_at": source.get("updated_at") or utc_now(),
    }


def row_to_proposal(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in PROPOSAL_JSON_FIELDS:
        data[field] = loads_json(data[field], [] if field == "target_refs" or field == "evidence_refs" else {})
    return data


DECISION_JSON_FIELDS = ("target_refs",)


def prepare_decision_record(data: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(data)
    return {
        "decision_id": source.get("decision_id") or new_uuid(),
        "decision_type": source.get("decision_type") or "edit_acceptance",
        "proposal_ref": source["proposal_ref"],
        "target_refs": dumps_json(ensure_list(source.get("target_refs"))),
        "proposed_by": source.get("proposed_by") or "system",
        "decided_by": source.get("decided_by"),
        "rationale": source.get("rationale"),
        "decision_state": source.get("decision_state") or "pending",
        "created_at": source.get("created_at") or utc_now(),
        "updated_at": source.get("updated_at") or utc_now(),
    }


def row_to_decision(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in DECISION_JSON_FIELDS:
        data[field] = loads_json(data[field], [])
    return data


def prepare_object_version_record(data: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(data)
    return {
        "version_id": source.get("version_id") or new_uuid(),
        "object_type": source["object_type"],
        "object_id": source["object_id"],
        "version_number": int(source["version_number"]),
        "serialized_state_ref": source["serialized_state_ref"],
        "created_at": source.get("created_at") or utc_now(),
        "created_by": source.get("created_by") or "system",
    }


def row_to_object_version(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


SOURCE_JSON_FIELDS = ("metadata", "provenance_record")


def prepare_source_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
    return {
        "source_id": source.get("source_id") or (current["source_id"] if current else new_uuid()),
        "domain_id": source["domain_id"],
        "source_type": source["source_type"],
        "source_origin": source.get("source_origin") or "local_api",
        "source_uri": source.get("source_uri"),
        "storage_ref": source.get("storage_ref"),
        "raw_payload_ref": source["raw_payload_ref"],
        "parsed_payload_ref": source.get("parsed_payload_ref"),
        "checksum": source["checksum"],
        "ingestion_status": source.get("ingestion_status") or "pending",
        "metadata": dumps_json(ensure_mapping(source.get("metadata"))),
        "provenance_record": dumps_json(ensure_mapping(source.get("provenance_record"))),
        "created_at": created_at,
        "updated_at": updated_at,
    }


def row_to_source(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in SOURCE_JSON_FIELDS:
        data[field] = loads_json(data[field], {})
    return data


def prepare_payload_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
        version = int(source.get("version") or 1)
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
        version = int(current["version"]) + 1
    return {
        "payload_id": source.get("payload_id") or (current["payload_id"] if current else new_uuid()),
        "payload_type": source["payload_type"],
        "owner_object_type": source["owner_object_type"],
        "owner_object_id": source["owner_object_id"],
        "storage_ref": source["storage_ref"],
        "format": source.get("format") or "txt",
        "checksum": source["checksum"],
        "editability": source.get("editability") or "read_only",
        "canonical_flag": int(bool(source.get("canonical_flag"))),
        "created_at": created_at,
        "updated_at": updated_at,
        "version": version,
    }


def row_to_payload(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["canonical_flag"] = bool(data["canonical_flag"])
    return data


PROJECTION_JSON_FIELDS = ("source_refs", "payload_refs")


def prepare_projection_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
    return {
        "projection_id": source.get("projection_id") or (current["projection_id"] if current else new_uuid()),
        "projection_type": source["projection_type"],
        "source_refs": dumps_json(ensure_list(source.get("source_refs"))),
        "payload_refs": dumps_json(ensure_list(source.get("payload_refs"))),
        "materialization_format": source.get("materialization_format") or "md",
        "storage_ref": source["storage_ref"],
        "generated_by": source.get("generated_by") or "system",
        "generation_scope": source.get("generation_scope") or "local",
        "freshness_status": source.get("freshness_status") or "fresh",
        "created_at": created_at,
        "updated_at": updated_at,
    }


def row_to_projection(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in PROJECTION_JSON_FIELDS:
        data[field] = loads_json(data[field], [])
    return data


GOVERNANCE_RULE_JSON_FIELDS = ("applies_to",)


def prepare_governance_rule_record(data: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(current or {})
    source.update(dict(data))
    if current is None:
        created_at = source.get("created_at") or utc_now()
        updated_at = source.get("updated_at") or created_at
        version = int(source.get("version") or 1)
    else:
        created_at = current["created_at"]
        updated_at = utc_now()
        version = int(current["version"]) + 1
    return {
        "rule_id": source.get("rule_id") or (current["rule_id"] if current else new_uuid()),
        "rule_type": source["rule_type"],
        "name": source["name"],
        "scope": source["scope"],
        "logic_description": source["logic_description"],
        "machine_executable_repr": source.get("machine_executable_repr"),
        "human_readable_repr": source["human_readable_repr"],
        "applies_to": dumps_json(ensure_list(source.get("applies_to"))),
        "priority": int(source.get("priority") or 0),
        "status": source.get("status") or "draft",
        "created_by": source.get("created_by") or "system",
        "approved_by": source.get("approved_by"),
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def row_to_governance_rule(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for field in GOVERNANCE_RULE_JSON_FIELDS:
        data[field] = loads_json(data[field], [])
    return data


def prepare_job_record(data: Mapping[str, Any], *, table: str) -> dict[str, Any]:
    source = dict(data)
    status = source.get("status") or "pending"
    return {
        "job_id": source.get("job_id") or new_uuid(),
        "job_type": source.get("job_type") or table.removesuffix("_jobs"),
        "status": status,
        "target_ref": source["target_ref"],
        "started_at": source.get("started_at"),
        "finished_at": source.get("finished_at"),
        "logs_ref": source.get("logs_ref"),
    }


def row_to_job(row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None
