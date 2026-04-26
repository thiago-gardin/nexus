from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.domain_templates import get_day0_domain_template, list_day0_domain_templates
from ..dependencies import RuntimeContext, get_runtime


router = APIRouter(tags=["authoring"])


class DomainCreatePayload(BaseModel):
    domain_id: str | None = None
    name: str
    description: str
    cognitive_purpose: str
    status: str = "draft"
    owner_human: str | None = None
    owner_agent: str | None = None
    source_types_supported: list[Any] = Field(default_factory=list)
    local_entity_types: list[Any] = Field(default_factory=list)
    relation_types: list[Any] = Field(default_factory=list)
    promotion_rules: list[Any] = Field(default_factory=list)
    governance_dependencies: list[Any] = Field(default_factory=list)
    performed_by: str = "human"
    reason: str | None = None


class DomainVersionCreatePayload(BaseModel):
    version_label: str
    status: str = "draft"
    charter: dict[str, Any] = Field(default_factory=dict)
    allowed_entity_types: list[Any] = Field(default_factory=list)
    allowed_relation_types: list[Any] = Field(default_factory=list)
    allowed_payload_types: list[Any] = Field(default_factory=list)
    required_fields: dict[str, Any] = Field(default_factory=dict)
    promotion_rules: list[Any] = Field(default_factory=list)
    performed_by: str = "human"
    reason: str | None = None


class ActionPayload(BaseModel):
    performed_by: str = "human"
    reason: str | None = None


class SourceRegisterPayload(BaseModel):
    domain_id: str
    source_type: str
    source_origin: str = "local_api"
    source_uri: str | None = None
    storage_ref: str | None = None
    content: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance_record: dict[str, Any] = Field(default_factory=dict)
    performed_by: str = "human"
    reason: str | None = None


class IngestionRunPayload(BaseModel):
    domain_id: str
    source_type: str
    content: str | None = None
    payload_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    proposed_by: str = "system"


class EntityCreatePayload(BaseModel):
    domain_id: str
    entity_type: str
    label: str
    scope: str = "local"
    short_description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    aliases: list[Any] = Field(default_factory=list)
    confidence: float = 1.0
    validation_status: str = "proposed"
    canonical_candidate_flag: bool = False
    provenance_refs: list[Any] = Field(default_factory=list)
    payload_refs: list[Any] = Field(default_factory=list)
    performed_by: str = "human"
    reason: str | None = None


class RelationCreatePayload(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    directionality: str = "directed"
    domain_context: str | None = None
    evidence_refs: list[Any] = Field(default_factory=list)
    confidence: float = 1.0
    validation_status: str = "proposed"
    asserted_by: str = "human"
    performed_by: str = "human"
    reason: str | None = None


class ObjectStatusPayload(BaseModel):
    performed_by: str = "human"
    reason: str | None = None


class TemplateInstantiatePayload(BaseModel):
    domain_id: str | None = None
    activate: bool = True
    performed_by: str = "human"
    reason: str | None = None


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=409, detail=message)


@router.post("/domains")
def create_domain(payload: DomainCreatePayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    data = payload.model_dump(exclude={"performed_by", "reason"}, exclude_none=True)
    try:
        return runtime.domain_service.create_domain(
            data,
            performed_by=payload.performed_by,
            performed_via="api",
            reason=payload.reason or "create domain through operational authoring API",
        )
    except sqlite3.IntegrityError as exc:
        raise _conflict(f"Domain '{data.get('domain_id') or data.get('name')}' already exists or violates schema constraints") from exc


@router.get("/domain-templates")
def list_domain_templates() -> list[dict[str, Any]]:
    return list_day0_domain_templates()


@router.get("/domain-templates/{template_id}")
def get_domain_template(template_id: str) -> dict[str, Any]:
    template = get_day0_domain_template(template_id)
    if template is None:
        raise _not_found("domain template", template_id)
    return template


@router.post("/domain-templates/{template_id}/instantiate")
def instantiate_domain_template(
    template_id: str,
    payload: TemplateInstantiatePayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or TemplateInstantiatePayload()
    template = get_day0_domain_template(template_id)
    if template is None:
        raise _not_found("domain template", template_id)
    domain_data = dict(template["domain"])
    if action.domain_id:
        domain_data["domain_id"] = action.domain_id
    version_data = dict(template["version"])
    version_data["domain_id"] = domain_data["domain_id"]
    try:
        domain = runtime.domain_service.create_domain(
            domain_data,
            performed_by=action.performed_by,
            performed_via="api",
            reason=action.reason or f"instantiate domain template {template_id}",
        )
        version = runtime.domain_version_service.create_domain_version(
            version_data,
            performed_by=action.performed_by,
            performed_via="api",
            reason=action.reason or f"create domain version from template {template_id}",
        )
        if action.activate:
            version = runtime.domain_version_service.activate_domain_version(
                version["domain_version_id"],
                performed_by=action.performed_by,
                performed_via="api",
                reason=action.reason or f"activate domain version from template {template_id}",
            )
        return {"template_id": template_id, "domain": domain, "domain_version": version}
    except sqlite3.IntegrityError as exc:
        raise _conflict(f"Template '{template_id}' could not be instantiated because the domain already exists or violates schema constraints") from exc


@router.post("/domains/{domain_id}/versions")
def create_domain_version(
    domain_id: str,
    payload: DomainVersionCreatePayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    data = payload.model_dump(exclude={"performed_by", "reason"})
    data["domain_id"] = domain_id
    try:
        return runtime.domain_version_service.create_domain_version(
            data,
            performed_by=payload.performed_by,
            performed_via="api",
            reason=payload.reason or "create domain version through operational authoring API",
        )
    except KeyError as exc:
        raise _not_found("domain", str(exc)) from exc


@router.get("/domains/{domain_id}/versions")
def list_domain_versions(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    if runtime.domain_service.get_domain_by_id(domain_id) is None:
        raise _not_found("domain", domain_id)
    return runtime.domain_version_service.list_domain_versions(domain_id=domain_id)


@router.get("/domains/{domain_id}/active-version")
def get_active_domain_version(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    active = runtime.domain_version_service.get_active_domain_version(domain_id)
    if active is None:
        raise _not_found("active domain version", domain_id)
    return active


@router.post("/domain-versions/{domain_version_id}/activate")
def activate_domain_version(
    domain_version_id: str,
    payload: ActionPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or ActionPayload()
    try:
        return runtime.domain_version_service.activate_domain_version(
            domain_version_id,
            performed_by=action.performed_by,
            performed_via="api",
            reason=action.reason or "activate domain version",
        )
    except KeyError as exc:
        raise _not_found("domain version", str(exc)) from exc


@router.post("/sources")
def register_source(payload: SourceRegisterPayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    if runtime.domain_service.get_domain_by_id(payload.domain_id) is None:
        raise _not_found("domain", payload.domain_id)
    source_manifest = payload.content
    if source_manifest is None:
        source_manifest = json.dumps(
            {
                "source_uri": payload.source_uri,
                "storage_ref": payload.storage_ref,
                "metadata": payload.metadata,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    return runtime.source_service.register_source_with_payload(
        {
            "domain_id": payload.domain_id,
            "source_type": payload.source_type,
            "source_origin": payload.source_origin,
            "source_uri": payload.source_uri,
            "storage_ref": payload.storage_ref,
            "checksum": payload.checksum,
            "ingestion_status": "pending",
            "metadata": payload.metadata,
            "provenance_record": payload.provenance_record,
        },
        content=source_manifest,
        payload_format="txt",
        performed_by=payload.performed_by,
        performed_via="api",
        reason=payload.reason or "register source through operational authoring API",
    )


@router.get("/domains/{domain_id}/sources")
def list_domain_sources(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    if runtime.domain_service.get_domain_by_id(domain_id) is None:
        raise _not_found("domain", domain_id)
    return runtime.source_service.list_sources(domain_id=domain_id)


@router.post("/ingestion-runs")
def run_ingestion(payload: IngestionRunPayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    try:
        return runtime.ingestion_service.ingest(
            domain_id=payload.domain_id,
            source_type=payload.source_type,
            content=payload.content,
            payload_ref=payload.payload_ref,
            metadata=payload.metadata,
            proposed_by=payload.proposed_by,
        )
    except KeyError as exc:
        raise _not_found("domain", str(exc)) from exc
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.get("/ingestion-runs/{job_id}")
def get_ingestion_run(job_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    job = runtime.ingestion_job_service.get_job_by_id(job_id)
    if job is None:
        raise _not_found("ingestion run", job_id)
    return job


@router.get("/domains/{domain_id}/ingestion-runs")
def list_domain_ingestion_runs(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    target_ref = f"domain:{domain_id}"
    return [job for job in runtime.ingestion_job_service.list_jobs() if job.get("target_ref") == target_ref]


@router.post("/entities")
def create_entity(payload: EntityCreatePayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    if runtime.domain_service.get_domain_by_id(payload.domain_id) is None:
        raise _not_found("domain", payload.domain_id)
    try:
        runtime.domain_version_service.validate_entity_against_active_charter(payload.domain_id, payload.entity_type, payload.attributes)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
    data = payload.model_dump(exclude={"performed_by", "reason"})
    return runtime.entity_service.create_entity(
        data,
        performed_by=payload.performed_by,
        performed_via="api",
        reason=payload.reason or "create entity through operational authoring API",
    )


@router.get("/domains/{domain_id}/entities")
def list_domain_entities(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    return [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]


@router.post("/relations")
def create_relation(payload: RelationCreatePayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    source = runtime.entity_service.get_entity_by_id(payload.source_entity_id)
    target = runtime.entity_service.get_entity_by_id(payload.target_entity_id)
    if source is None:
        raise _not_found("entity", payload.source_entity_id)
    if target is None:
        raise _not_found("entity", payload.target_entity_id)
    domain_context = payload.domain_context or source.get("domain_id") or target.get("domain_id")
    try:
        runtime.domain_version_service.validate_relation_against_active_charter(domain_context, payload.relation_type)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
    data = payload.model_dump(exclude={"performed_by", "reason"})
    data["domain_context"] = domain_context
    return runtime.relation_service.create_relation(
        data,
        performed_by=payload.performed_by,
        performed_via="api",
        reason=payload.reason or "create relation through operational authoring API",
    )


@router.get("/domains/{domain_id}/relations")
def list_domain_relations(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    return [relation for relation in runtime.relation_service.list_relations() if relation.get("domain_context") == domain_id]


@router.post("/objects/{object_type}/{object_id}/validate")
def validate_object(
    object_type: str,
    object_id: str,
    payload: ObjectStatusPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or ObjectStatusPayload()
    try:
        return runtime.object_validation_service.validate_object(
            object_type,
            object_id,
            performed_by=action.performed_by,
            performed_via="api",
            reason=action.reason,
        )
    except KeyError as exc:
        raise _not_found(object_type, str(exc)) from exc
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.post("/objects/{object_type}/{object_id}/reject")
def reject_object(
    object_type: str,
    object_id: str,
    payload: ObjectStatusPayload | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    action = payload or ObjectStatusPayload()
    try:
        return runtime.object_validation_service.reject_object(
            object_type,
            object_id,
            performed_by=action.performed_by,
            performed_via="api",
            reason=action.reason,
        )
    except KeyError as exc:
        raise _not_found(object_type, str(exc)) from exc
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
