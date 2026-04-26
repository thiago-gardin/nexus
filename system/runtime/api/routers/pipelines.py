from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ...core.materialization.operational_projections import build_domain_meeting_context
from ...core.materialization.operational_projections import build_domain_project_state
from ..dependencies import RuntimeContext, get_runtime
from ..materialization import materialize_domain_publication


router = APIRouter(tags=["pipelines"])


class IngestPayload(BaseModel):
    domain_id: str
    source_type: str
    content: str | None = None
    payload_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    proposed_by: str = "system"


class ReentryDiffPayload(BaseModel):
    target_object_type: str
    target_object_id: str
    before: str
    after: str
    proposed_by: str = "system"


class ReentryEditPayload(BaseModel):
    before: str
    after: str
    proposed_by: str = "system"


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


def _tree_root(request: Request) -> Path:
    return Path(getattr(request.app.state, "tree_root", "tree"))


def _tree_proposal_marker(tree_root: Path, path: Path) -> str:
    return f"tree-proposal:{path.relative_to(tree_root).as_posix()}"


def _load_tree_proposal_artifact(path: Path) -> dict[str, Any]:
    if path.suffix.casefold() == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
    else:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("proposal artifact must be a mapping")
    return loaded


def _existing_evidence_refs(runtime: RuntimeContext) -> set[str]:
    refs: set[str] = set()
    for proposal in runtime.governance_service.list_proposals():
        for ref in proposal.get("evidence_refs") or []:
            refs.add(str(ref))
    return refs


@router.post("/ingest")
def ingest(payload: IngestPayload, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
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
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reconcile/domain/{domain_id}")
def reconcile_domain(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    result = runtime.reconciliation_service.reconcile_entities(domain_id=domain_id, proposed_by="system")
    return {
        "domain_id": domain_id,
        "candidate_groups": result["candidate_groups"],
        "candidate_group_count": len(result["candidate_groups"]),
        "merge_proposals": result["merge_proposals"],
        "merge_proposal_count": len(result["merge_proposals"]),
        "separation_proposals": result["separation_proposals"],
        "separation_proposal_count": len(result["separation_proposals"]),
    }


@router.post("/materialize/domain/{domain_id}")
def materialize_domain(
    domain_id: str,
    request: Request,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    try:
        return materialize_domain_publication(
            runtime,
            tree_root=_tree_root(request),
            domain_id=domain_id,
            generated_by="materialization_api",
            reason=f"materialize domain {domain_id}",
        )
    except KeyError as exc:
        raise _not_found("domain", str(exc)) from exc
    except Exception as exc:
        raise


@router.post("/materialize/domain/{domain_id}/meeting-context")
def materialize_domain_meeting_context(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)
    job = runtime.materialization_job_service.create_job(
        {"job_type": "meeting_context_materialization", "status": "running", "target_ref": f"domain:{domain_id}"}
    )
    try:
        meeting_context = build_domain_meeting_context(runtime, domain_id)
        content = "# Meeting Context\n\n```yaml\n" + yaml.safe_dump(meeting_context, sort_keys=False, allow_unicode=True) + "```\n"
        projection = runtime.projection_service.create_projection(
            {
                "projection_type": "meeting_context",
                "source_refs": [domain_id],
                "payload_refs": [],
                "materialization_format": "md",
                "generated_by": "materialization_api",
                "generation_scope": "local",
                "freshness_status": "fresh",
            },
            content=content,
            performed_by="system",
            performed_via="api",
            reason=f"materialize meeting context for domain {domain_id}",
        )
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection['projection_id']}",
        )
        return {"domain": domain, "meeting_context": meeting_context, "projection": projection, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/materialize/domain/{domain_id}/project-state")
def materialize_domain_project_state(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)
    job = runtime.materialization_job_service.create_job(
        {"job_type": "project_state_materialization", "status": "running", "target_ref": f"domain:{domain_id}"}
    )
    try:
        project_state = build_domain_project_state(runtime, domain_id)
        content = "# Project State\n\n```yaml\n" + yaml.safe_dump(project_state, sort_keys=False, allow_unicode=True) + "```\n"
        projection = runtime.projection_service.create_projection(
            {
                "projection_type": "project_state",
                "source_refs": [domain_id],
                "payload_refs": [],
                "materialization_format": "md",
                "generated_by": "materialization_api",
                "generation_scope": "local",
                "freshness_status": "fresh",
            },
            content=content,
            performed_by="system",
            performed_via="api",
            reason=f"materialize project state for domain {domain_id}",
        )
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection['projection_id']}",
        )
        return {"domain": domain, "project_state": project_state, "projection": projection, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/materialize/entity/{entity_id}")
def materialize_entity(entity_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    entity = runtime.entity_service.get_entity_by_id(entity_id)
    if entity is None:
        raise _not_found("entity", entity_id)
    job = runtime.materialization_job_service.create_job(
        {"job_type": "entity_materialization", "status": "running", "target_ref": f"entity:{entity_id}"}
    )
    try:
        projection = runtime.projection_service.create_projection(
            {
                "projection_type": "entity_view",
                "source_refs": [entity_id],
                "payload_refs": list(entity.get("payload_refs") or []),
                "materialization_format": "md",
                "generated_by": "materialization_api",
                "generation_scope": "local",
                "freshness_status": "fresh",
            },
            content=f"# Entity View: {entity['label']}\n\n```json\n{json.dumps(entity, ensure_ascii=False, indent=2)}\n```\n",
            performed_by="system",
            performed_via="api",
            reason=f"materialize entity {entity_id}",
        )
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection['projection_id']}",
        )
        return {"entity": entity, "projection": projection, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/materialize/payload/{payload_id}")
def materialize_payload(payload_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    payload = runtime.payload_service.get_payload_by_id(payload_id)
    if payload is None:
        raise _not_found("payload", payload_id)
    job = runtime.materialization_job_service.create_job(
        {"job_type": "payload_materialization", "status": "running", "target_ref": f"payload:{payload_id}"}
    )
    try:
        content = runtime.payload_service.read_payload_content(payload_id) or ""
        projection = runtime.projection_service.create_projection(
            {
                "projection_type": "thread_view",
                "source_refs": [payload_id],
                "payload_refs": [payload_id],
                "materialization_format": "md",
                "generated_by": "materialization_api",
                "generation_scope": "local",
                "freshness_status": "fresh",
            },
            content=f"# Payload Export: {payload_id}\n\n{content}\n",
            performed_by="system",
            performed_via="api",
            reason=f"materialize payload {payload_id}",
        )
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection['projection_id']}",
        )
        return {"payload": payload, "projection": projection, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/materialize/projection/{projection_id}")
def materialize_projection(projection_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    projection = runtime.projection_service.get_projection_by_id(projection_id)
    if projection is None:
        raise _not_found("projection", projection_id)
    job = runtime.materialization_job_service.create_job(
        {"job_type": "projection_materialization", "status": "running", "target_ref": f"projection:{projection_id}"}
    )
    try:
        content = runtime.projection_service.read_projection_content(projection_id)
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection_id}",
        )
        return {"projection": projection, "content": content, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.get("/exports/{projection_id}")
def export_projection(projection_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> dict[str, Any]:
    projection = runtime.projection_service.get_projection_by_id(projection_id)
    if projection is None:
        raise _not_found("projection", projection_id)
    return {"projection": projection, "content": runtime.projection_service.read_projection_content(projection_id)}


@router.post("/reentry/from-payload/{payload_id}")
def reentry_from_payload(
    payload_id: str,
    payload: ReentryEditPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    if runtime.payload_service.get_payload_by_id(payload_id) is None:
        raise _not_found("payload", payload_id)
    job = runtime.reentry_job_service.create_job(
        {"job_type": "payload_reentry", "status": "running", "target_ref": f"payload:{payload_id}"}
    )
    try:
        result = runtime.reentry_service.parse_diff(
            target_object_type="payload",
            target_object_id=payload_id,
            before=payload.before,
            after=payload.after,
            proposed_by=payload.proposed_by,
        )
        result["job"] = runtime.reentry_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"proposal:{result['proposal']['proposal_id']}",
        )
        return result
    except Exception as exc:
        runtime.reentry_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/reentry/from-projection/{projection_id}")
def reentry_from_projection(
    projection_id: str,
    payload: ReentryEditPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    if runtime.projection_service.get_projection_by_id(projection_id) is None:
        raise _not_found("projection", projection_id)
    job = runtime.reentry_job_service.create_job(
        {"job_type": "projection_reentry", "status": "running", "target_ref": f"projection:{projection_id}"}
    )
    try:
        result = runtime.reentry_service.parse_diff(
            target_object_type="projection",
            target_object_id=projection_id,
            before=payload.before,
            after=payload.after,
            proposed_by=payload.proposed_by,
        )
        result["job"] = runtime.reentry_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"proposal:{result['proposal']['proposal_id']}",
        )
        return result
    except Exception as exc:
        runtime.reentry_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/reentry/parse-diff")
def parse_reentry_diff(
    payload: ReentryDiffPayload,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    job = runtime.reentry_job_service.create_job(
        {
            "job_type": "parse_diff_reentry",
            "status": "running",
            "target_ref": f"{payload.target_object_type}:{payload.target_object_id}",
        }
    )
    try:
        result = runtime.reentry_service.parse_diff(
            target_object_type=payload.target_object_type,
            target_object_id=payload.target_object_id,
            before=payload.before,
            after=payload.after,
            proposed_by=payload.proposed_by,
        )
        result["job"] = runtime.reentry_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"proposal:{result['proposal']['proposal_id']}",
        )
        return result
    except Exception as exc:
        runtime.reentry_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise


@router.post("/reentry/from-tree-inbox")
def reentry_from_tree_inbox(
    request: Request,
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    tree_root = _tree_root(request)
    inbox_root = tree_root / "inbox" / "proposals"
    job = runtime.reentry_job_service.create_job(
        {"job_type": "tree_inbox_reentry", "status": "running", "target_ref": inbox_root.as_posix()}
    )
    imported: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    try:
        existing_refs = _existing_evidence_refs(runtime)
        if inbox_root.exists():
            for path in sorted(inbox_root.iterdir()):
                if not path.is_file() or path.suffix.casefold() not in {".yaml", ".yml", ".json"}:
                    continue
                marker = _tree_proposal_marker(tree_root, path)
                if marker in existing_refs:
                    skipped.append({"path": path.name, "reason": "duplicate evidence_ref"})
                    continue
                try:
                    artifact = _load_tree_proposal_artifact(path)
                    if artifact.get("source") == "db-derived":
                        skipped.append({"path": path.name, "reason": "db-derived export"})
                        continue
                    missing = [
                        field
                        for field in (
                            "proposal_type",
                            "target_object_type",
                            "target_object_id",
                            "proposed_changes",
                            "proposed_by",
                            "rationale",
                            "evidence_refs",
                        )
                        if field not in artifact
                    ]
                    if missing:
                        skipped.append({"path": path.name, "reason": f"missing fields: {', '.join(missing)}"})
                        continue
                    evidence_refs = list(artifact.get("evidence_refs") or [])
                    evidence_refs.append(marker)
                    bundle = runtime.governance_service.create_structured_proposal(
                        proposal_type=str(artifact["proposal_type"]),
                        target_object_type=str(artifact["target_object_type"]),
                        target_object_id=str(artifact["target_object_id"]),
                        proposed_changes=dict(artifact.get("proposed_changes") or {}),
                        proposed_by=str(artifact.get("proposed_by") or "tree-inbox"),
                        rationale=str(artifact.get("rationale") or "Remote tree inbox proposal"),
                        evidence_refs=evidence_refs,
                    )
                    imported.append({"path": path.name, "marker": marker, "proposal": bundle["proposal"], "decision": bundle["decision"]})
                    existing_refs.add(marker)
                except Exception as exc:
                    skipped.append({"path": path.name, "reason": f"{type(exc).__name__}: {exc}"})
        completed_job = runtime.reentry_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"imported:{len(imported)};skipped:{len(skipped)}",
        )
        return {
            "tree_root": tree_root.as_posix(),
            "inbox": inbox_root.as_posix(),
            "imported": imported,
            "imported_count": len(imported),
            "skipped": skipped,
            "skipped_count": len(skipped),
            "job": completed_job,
        }
    except Exception as exc:
        runtime.reentry_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise
