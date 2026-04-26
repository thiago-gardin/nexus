from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .dependencies import RuntimeContext
from ..core.materialization.treefolder_publisher import TreefolderPublisher


def materialize_domain_publication(
    runtime: RuntimeContext,
    *,
    tree_root: Path,
    domain_id: str,
    generated_by: str = "materialization_api",
    reason: str | None = None,
) -> dict[str, Any]:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise KeyError(domain_id)
    job = runtime.materialization_job_service.create_job(
        {
            "job_type": "domain_materialization",
            "status": "running",
            "target_ref": f"domain:{domain_id}",
        }
    )
    try:
        publisher = TreefolderPublisher(runtime.transaction_manager, tree_root=tree_root)
        status = publisher.publish()
        projection = runtime.projection_service.create_projection(
            {
                "projection_type": "domain_snapshot",
                "source_refs": [domain_id],
                "payload_refs": [],
                "materialization_format": "yaml",
                "generated_by": generated_by,
                "generation_scope": "published",
                "freshness_status": status["freshness_status"],
            },
            content=yaml.safe_dump(status, sort_keys=False),
            performed_by="system",
            performed_via="api",
            reason=reason or f"materialize domain {domain_id}",
        )
        completed_job = runtime.materialization_job_service.update_job_status(
            job["job_id"],
            "completed",
            logs_ref=f"projection:{projection['projection_id']}",
        )
        return {"domain": domain, "status": status, "projection": projection, "job": completed_job}
    except Exception as exc:
        runtime.materialization_job_service.update_job_status(job["job_id"], "failed", logs_ref=f"{type(exc).__name__}: {exc}")
        raise
