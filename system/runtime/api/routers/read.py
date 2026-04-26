from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import RuntimeContext, get_runtime


router = APIRouter(tags=["read"])


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


@router.get("/domains")
def list_domains(runtime: RuntimeContext = Depends(get_runtime)) -> list[dict[str, Any]]:
    return runtime.domain_service.list_domains()


@router.get("/domains/{domain_id}")
def get_domain(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)
    return domain


@router.get("/entities/{entity_id}")
def get_entity(entity_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    entity = runtime.entity_service.get_entity_by_id(entity_id)
    if entity is None:
        raise _not_found("entity", entity_id)
    return entity


@router.get("/relations/{relation_id}")
def get_relation(relation_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    relation = runtime.relation_service.get_relation_by_id(relation_id)
    if relation is None:
        raise _not_found("relation", relation_id)
    return relation


@router.get("/events")
def list_events(
    target_object_type: str | None = None,
    target_object_id: str | None = None,
    event_type: str | None = None,
    performed_by: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[dict[str, Any]]:
    return runtime.event_service.list_events(
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        event_type=event_type,
        performed_by=performed_by,
    )


@router.get("/events/{event_id}")
def get_event(event_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    event = runtime.event_service.get_event_by_id(event_id)
    if event is None:
        raise _not_found("event", event_id)
    return event


@router.get("/sources/{source_id}")
def get_source(source_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    source = runtime.source_service.get_source_by_id(source_id)
    if source is None:
        raise _not_found("source", source_id)
    return source


@router.get("/payloads/{payload_id}")
def get_payload(payload_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    payload = runtime.payload_service.get_payload_by_id(payload_id)
    if payload is None:
        raise _not_found("payload", payload_id)
    content = runtime.payload_service.read_payload_content(payload_id)
    return {"payload": payload, "content": content}


@router.get("/projections/{projection_id}")
def get_projection(projection_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    projection = runtime.projection_service.get_projection_by_id(projection_id)
    if projection is None:
        raise _not_found("projection", projection_id)
    content = runtime.projection_service.read_projection_content(projection_id)
    return {"projection": projection, "content": content}


@router.get("/search")
def search(
    query: str,
    type: str | None = None,
    domain: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> list[dict[str, Any]]:
    return runtime.search_service.search(query=query, object_type=type, domain_id=domain)
