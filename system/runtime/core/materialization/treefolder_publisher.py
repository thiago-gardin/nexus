from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ..storage import (
    DomainService,
    DomainVersionService,
    EntityService,
    EventService,
    GovernanceService,
    JobService,
    PayloadService,
    ProjectionService,
    RelationService,
    SourceService,
    TransactionManager,
)
from .operational_projections import build_domain_active_decision_queue
from .operational_projections import build_domain_meeting_context
from .operational_projections import build_domain_operational_summary
from .operational_projections import build_domain_project_state
from .operational_projections import build_domain_recent_changes


ROOT_START_HERE_TEMPLATE = """# Start Here

`tree/` is the remote-readable publication surface for Nexus.

## How to navigate

- Start with `INDEX.md` for the current domain list and primary links.
- Use `SYSTEM_STATUS.yaml` to confirm freshness and publication scope.
- Follow each domain's `INDEX.md` to reach the published contract, object views, projections, and governance trace.
- Use the governance trace to follow proposal -> decision -> history/version trail -> publication.
- Use `tree/inbox/proposals/` only for structured proposals.

## Executable truth vs publishable truth

- Executable truth lives in the SQLite-backed runtime.
- Publishable truth is a derived treefolder snapshot generated from that runtime.
- Treefolder artifacts are publication outputs, not the source of identity or mutation authority.

## Remote write restrictions

- Remote agents may read published artifacts.
- Remote agents may write only structured proposals in `tree/inbox/proposals/`.
- Canonical artifacts and domain publications are regenerated from the executable core, not edited as sovereign truth.

## ID and status conventions

- Stable IDs come from the executable core.
- `tree/SYSTEM_STATUS.yaml` carries freshness and publication metadata.
- Domain folders are partitioned by `domain_id` and are navigation surfaces, not alternate truth sources.
"""


class TreefolderPublisher:
    def __init__(self, transaction_manager: TransactionManager, tree_root: str | Path = "tree") -> None:
        self.transaction_manager = transaction_manager
        self.tree_root = Path(tree_root)
        self.event_service = EventService(transaction_manager)
        self.domain_service = DomainService(transaction_manager, event_service=self.event_service)
        self.domain_version_service = DomainVersionService(transaction_manager, event_service=self.event_service)
        self.entity_service = EntityService(transaction_manager, event_service=self.event_service)
        self.relation_service = RelationService(transaction_manager, event_service=self.event_service)
        self.source_service = SourceService(transaction_manager, event_service=self.event_service)
        self.ingestion_job_service = JobService(transaction_manager, "ingestion_jobs")
        self.payload_service = PayloadService(transaction_manager, event_service=self.event_service)
        self.projection_service = ProjectionService(transaction_manager, event_service=self.event_service)
        self.governance_service = GovernanceService(
            transaction_manager,
            event_service=self.event_service,
            domain_service=self.domain_service,
            entity_service=self.entity_service,
            relation_service=self.relation_service,
            payload_service=self.payload_service,
        )

    def publish(self) -> dict[str, Any]:
        domains = self.domain_service.list_domains()
        entities = self.entity_service.list_entities()
        relations = self.relation_service.list_relations()
        payloads = self.payload_service.list_payloads()
        projections = self.projection_service.list_projections()
        domain_ids = [domain["domain_id"] for domain in domains]

        domain_versions_by_domain = self._group_domain_versions_by_domain()
        sources_by_domain = self._group_sources_by_domain()
        ingestion_jobs_by_domain = self._group_ingestion_jobs_by_domain()
        entities_by_domain = self._group_entities_by_domain(entities)
        relations_by_domain = self._group_relations_by_domain(relations)
        payloads_by_domain = self._group_payloads_by_domain(payloads)
        projections_by_domain = self._group_projections_by_domain(projections)
        governance_traces_by_domain = self._group_governance_traces(domains)

        self._ensure_base_skeleton()
        self._write_start_here()
        self._write_index(domains, entities_by_domain, relations_by_domain, governance_traces_by_domain)
        self._write_canonical_indexes(entities, relations)
        self._write_global_projection_index(projections)
        self._write_proposal_inbox_index()
        artifact_counts = self._write_domain_publications(
            domains,
            domain_versions_by_domain,
            sources_by_domain,
            ingestion_jobs_by_domain,
            entities_by_domain,
            relations_by_domain,
            payloads_by_domain,
            projections_by_domain,
            governance_traces_by_domain,
        )
        status = self._build_system_status(domain_ids, artifact_counts)
        self._write_yaml(self.tree_root / "SYSTEM_STATUS.yaml", status)

        return status

    def _ensure_base_skeleton(self) -> None:
        self._ensure_directory(self.tree_root / "domains", keep_placeholder=True)
        self._ensure_directory(self.tree_root / "canonical" / "entities", keep_placeholder=True)
        self._ensure_directory(self.tree_root / "canonical" / "relations", keep_placeholder=True)
        self._ensure_directory(self.tree_root / "inbox" / "proposals", keep_placeholder=True)
        self._ensure_directory(self.tree_root / "projections", keep_placeholder=True)

    def _write_start_here(self) -> None:
        self._write_text(self.tree_root / "START_HERE.md", ROOT_START_HERE_TEMPLATE)

    def _write_index(
        self,
        domains: list[dict[str, Any]],
        entities_by_domain: dict[str, list[dict[str, Any]]],
        relations_by_domain: dict[str, list[dict[str, Any]]],
        governance_traces_by_domain: dict[str, list[dict[str, Any]]],
    ) -> None:
        lines = [
            "# Nexus Treefolder Index",
            "",
            "## Primary Navigation",
            "- [Start Here](./START_HERE.md)",
            "- [System Status](./SYSTEM_STATUS.yaml)",
            "",
            "## Domains",
        ]
        if domains:
            for domain in domains:
                domain_id = domain["domain_id"]
                name = domain.get("name") or domain_id
                entity_count = len(entities_by_domain.get(domain_id, []))
                relation_count = len(relations_by_domain.get(domain_id, []))
                lines.append(
                    f"- [{domain_id} - {name}](./domains/{domain_id}/INDEX.md) "
                    f"(entities: {entity_count}, relations: {relation_count})"
                )
        else:
            lines.append("- No domains published yet.")
        lines.extend(
            [
                "",
                "## Primary Projections",
            ]
        )
        if domains:
            for domain in domains:
                domain_id = domain["domain_id"]
                name = domain.get("name") or domain_id
                lines.append(f"- [{domain_id} overview](./domains/{domain_id}/projections/DOMAIN_OVERVIEW.md) - {name}")
                lines.append(
                    f"- [{domain_id} operational summary](./domains/{domain_id}/projections/DOMAIN_OPERATIONAL_SUMMARY.md) - {name}"
                )
                lines.append(
                    f"- [{domain_id} review queue](./domains/{domain_id}/projections/PENDING_REVIEW_QUEUE.md) - {name}"
                )
                lines.append(
                    f"- [{domain_id} active decision queue](./domains/{domain_id}/projections/ACTIVE_DECISION_QUEUE.md) - {name}"
                )
                lines.append(
                    f"- [{domain_id} recent changes](./domains/{domain_id}/projections/RECENT_CHANGES.md) - {name}"
                )
                lines.append(
                    f"- [{domain_id} meeting context](./domains/{domain_id}/projections/MEETING_CONTEXT.md) - {name}"
                )
                lines.append(
                    f"- [{domain_id} project state](./domains/{domain_id}/projections/PROJECT_STATE.md) - {name}"
                )
        else:
            lines.append("- No published views yet.")
        lines.extend(["", "## Governance Reflections"])
        governance_trace_links_added = False
        if domains:
            for domain in domains:
                domain_id = domain["domain_id"]
                traces = governance_traces_by_domain.get(domain_id, [])
                if not traces:
                    continue
                name = domain.get("name") or domain_id
                governance_trace_links_added = True
                lines.append(
                    f"- [{domain_id} governance trace](./domains/{domain_id}/projections/GOVERNANCE_TRACE.md) "
                    f"(reflections: {len(traces)}) - {name}"
                )
        if not governance_trace_links_added:
            lines.append("- No governance reflections published yet.")
        lines.extend(
            [
                "",
                "## Canonical Zones",
                "- [Canonical Entities](./canonical/entities/INDEX.md)",
                "- [Canonical Relations](./canonical/relations/INDEX.md)",
                "",
                "## Projection Index",
                "- [All Projection Records](./projections/INDEX.md)",
                "",
                "## Proposals",
                "- [Structured Proposals](./inbox/proposals/INDEX.md)",
                "",
                "## Local Indexes",
            ]
        )
        if domains:
            for domain in domains:
                domain_id = domain["domain_id"]
                lines.append(f"- [./domains/{domain_id}/INDEX.md](./domains/{domain_id}/INDEX.md)")
        else:
            lines.append("- No local domain indexes yet.")
        lines.append("")
        self._write_text(self.tree_root / "INDEX.md", "\n".join(lines))

    def _write_domain_publications(
        self,
        domains: list[dict[str, Any]],
        domain_versions_by_domain: dict[str, list[dict[str, Any]]],
        sources_by_domain: dict[str, list[dict[str, Any]]],
        ingestion_jobs_by_domain: dict[str, list[dict[str, Any]]],
        entities_by_domain: dict[str, list[dict[str, Any]]],
        relations_by_domain: dict[str, list[dict[str, Any]]],
        payloads_by_domain: dict[str, list[dict[str, Any]]],
        projections_by_domain: dict[str, list[dict[str, Any]]],
        governance_traces_by_domain: dict[str, list[dict[str, Any]]],
    ) -> dict[str, int]:
        counts = {
            "domain_overviews": 0,
            "domain_operational_summaries": 0,
            "pending_review_queues": 0,
            "active_decision_queues": 0,
            "recent_changes": 0,
            "meeting_contexts": 0,
            "project_states": 0,
            "entity_snapshots": 0,
            "relation_snapshots": 0,
            "payload_snapshots": 0,
            "projection_indexes": 0,
            "domain_charters": 0,
            "source_indexes": 0,
            "ingestion_run_indexes": 0,
            "authoring_summaries": 0,
            "canonical_entity_indexes": 1,
            "canonical_relation_indexes": 1,
            "proposal_inbox_indexes": 1,
            "governance_traces": 0,
        }
        for domain in domains:
            domain_id = domain["domain_id"]
            domain_root = self.tree_root / "domains" / domain_id
            domain_versions = domain_versions_by_domain.get(domain_id, [])
            domain_sources = sources_by_domain.get(domain_id, [])
            domain_ingestion_jobs = ingestion_jobs_by_domain.get(domain_id, [])
            domain_entities = entities_by_domain.get(domain_id, [])
            domain_relations = relations_by_domain.get(domain_id, [])
            domain_payloads = payloads_by_domain.get(domain_id, [])
            domain_projections = projections_by_domain.get(domain_id, [])
            governance_traces = governance_traces_by_domain.get(domain_id, [])
            operational_summary = build_domain_operational_summary(self, domain_id)
            meeting_context = build_domain_meeting_context(self, domain_id)
            project_state = build_domain_project_state(self, domain_id)
            review_queue = {
                "domain": domain,
                "pending_proposals": operational_summary["pending_proposals"],
                "pending_proposal_count": operational_summary["pending_proposal_count"],
            }
            active_decision_queue = build_domain_active_decision_queue(self, domain_id)
            recent_changes = build_domain_recent_changes(self, domain_id)

            self._ensure_directory(domain_root / "entities", keep_placeholder=True)
            self._ensure_directory(domain_root / "relations", keep_placeholder=True)
            self._ensure_directory(domain_root / "payloads", keep_placeholder=True)
            self._ensure_directory(domain_root / "projections", keep_placeholder=True)
            self._ensure_directory(domain_root / "sources", keep_placeholder=True)
            self._ensure_directory(domain_root / "ingestion_runs", keep_placeholder=True)

            contract = self._build_domain_contract(domain)
            self._write_yaml(domain_root / "DOMAIN_CONTRACT.yaml", {"domain_contract": contract})
            self._write_yaml(
                domain_root / "DOMAIN_CHARTER.yaml",
                {
                    "domain_id": domain_id,
                    "active_domain_version": self.domain_version_service.get_active_domain_version(domain_id),
                    "domain_versions": domain_versions,
                    "publication_note": "Published from executable state; edit via cockpit/API/MCP local operator, not by editing this file.",
                },
            )
            self._write_text(
                domain_root / "INDEX.md",
                self._build_domain_index(
                    domain,
                    domain_versions,
                    domain_sources,
                    domain_ingestion_jobs,
                    domain_entities,
                    domain_relations,
                    governance_traces,
                ),
            )
            self._write_sources_index(domain_root, domain, domain_sources)
            self._write_ingestion_runs_index(domain_root, domain, domain_ingestion_jobs)
            self._write_entity_views(domain_root, domain, domain_entities)
            self._write_relation_views(domain_root, domain, domain_relations)
            self._write_payload_views(domain_root, domain, domain_payloads)
            self._write_projection_index(domain_root, domain, domain_projections)
            self._write_governance_trace(domain_root, domain, governance_traces)
            self._write_text(
                domain_root / "projections" / "DOMAIN_OVERVIEW.md",
                self._build_domain_overview(domain, domain_entities, domain_relations, governance_traces),
            )
            self._write_text(
                domain_root / "projections" / "DOMAIN_OPERATIONAL_SUMMARY.md",
                self._build_domain_operational_summary(domain, operational_summary),
            )
            self._write_text(
                domain_root / "projections" / "PENDING_REVIEW_QUEUE.md",
                self._build_pending_review_queue(domain, review_queue),
            )
            self._write_text(
                domain_root / "projections" / "ACTIVE_DECISION_QUEUE.md",
                self._build_active_decision_queue(domain, active_decision_queue),
            )
            self._write_text(
                domain_root / "projections" / "RECENT_CHANGES.md",
                self._build_recent_changes(domain, recent_changes),
            )
            self._write_text(
                domain_root / "projections" / "MEETING_CONTEXT.md",
                self._build_meeting_context(domain, meeting_context),
            )
            self._write_text(
                domain_root / "projections" / "PROJECT_STATE.md",
                self._build_project_state(domain, project_state),
            )
            self._write_text(
                domain_root / "projections" / "AUTHORING_SUMMARY.md",
                self._build_authoring_summary(
                    domain,
                    domain_versions,
                    domain_sources,
                    domain_ingestion_jobs,
                    domain_entities,
                    domain_relations,
                ),
            )

            counts["domain_overviews"] += 1
            counts["domain_operational_summaries"] += 1
            counts["pending_review_queues"] += 1
            counts["active_decision_queues"] += 1
            counts["recent_changes"] += 1
            counts["meeting_contexts"] += 1
            counts["project_states"] += 1
            counts["entity_snapshots"] += len(domain_entities)
            counts["relation_snapshots"] += len(domain_relations)
            counts["payload_snapshots"] += len(domain_payloads)
            counts["projection_indexes"] += 1
            counts["domain_charters"] += 1
            counts["source_indexes"] += 1
            counts["ingestion_run_indexes"] += 1
            counts["authoring_summaries"] += 1
            counts["governance_traces"] += len(governance_traces)

        return counts

    def _build_domain_contract(self, domain: dict[str, Any]) -> dict[str, Any]:
        active_version = self.domain_version_service.get_active_domain_version(domain["domain_id"])
        return {
            "domain_id": domain["domain_id"],
            "name": domain["name"],
            "description": domain.get("description"),
            "cognitive_purpose": domain["cognitive_purpose"],
            "source_types_supported": domain.get("source_types_supported", []),
            "local_entity_types": domain.get("local_entity_types", []),
            "relation_types": domain.get("relation_types", []),
            "payload_types": [],
            "promotion_rules": domain.get("promotion_rules", []),
            "governance_dependencies": domain.get("governance_dependencies", []),
            "status": domain.get("status"),
            "version": domain.get("version"),
            "owner_human": domain.get("owner_human"),
            "owner_agent": domain.get("owner_agent"),
            "active_domain_version_id": active_version.get("domain_version_id") if active_version else None,
            "active_domain_version_label": active_version.get("version_label") if active_version else None,
            "created_at": domain.get("created_at"),
            "updated_at": domain.get("updated_at"),
        }

    def _build_domain_index(
        self,
        domain: dict[str, Any],
        domain_versions: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        ingestion_jobs: list[dict[str, Any]],
        entities: list[dict[str, Any]],
        relations: list[dict[str, Any]],
        governance_traces: list[dict[str, Any]],
    ) -> str:
        domain_id = domain["domain_id"]
        name = domain.get("name") or domain_id
        lines = [
            f"# Domain Index: {name}",
            "",
            f"- Domain ID: `{domain_id}`",
            f"- Status: `{domain.get('status', 'unknown')}`",
            f"- Version: `{domain.get('version', 'unknown')}`",
            f"- Domain Versions: `{len(domain_versions)}`",
            f"- Registered Sources: `{len(sources)}`",
            f"- Ingestion Runs: `{len(ingestion_jobs)}`",
            f"- Entity Snapshots: `{len(entities)}`",
            f"- Relation Snapshots: `{len(relations)}`",
            f"- Governance Reflections: `{len(governance_traces)}`",
            "",
            "## Navigation",
            "- [Domain Contract](./DOMAIN_CONTRACT.yaml)",
            "- [Domain Charter](./DOMAIN_CHARTER.yaml)",
            "- [Sources Index](./sources/INDEX.md)",
            "- [Ingestion Runs Index](./ingestion_runs/INDEX.md)",
            "- [Domain Overview](./projections/DOMAIN_OVERVIEW.md)",
            "- [Authoring Summary](./projections/AUTHORING_SUMMARY.md)",
            "- [Domain Operational Summary](./projections/DOMAIN_OPERATIONAL_SUMMARY.md)",
            "- [Pending Review Queue](./projections/PENDING_REVIEW_QUEUE.md)",
            "- [Active Decision Queue](./projections/ACTIVE_DECISION_QUEUE.md)",
            "- [Recent Changes](./projections/RECENT_CHANGES.md)",
            "- [Meeting Context](./projections/MEETING_CONTEXT.md)",
            "- [Project State](./projections/PROJECT_STATE.md)",
            "- [Governance Trace](./projections/GOVERNANCE_TRACE.md)",
            "- [Entities Index](./entities/INDEX.md)",
            "- [Relations Index](./relations/INDEX.md)",
            "- [Payloads Index](./payloads/INDEX.md)",
            "- [Projection Records Index](./projections/PROJECTIONS_INDEX.md)",
            "",
            "This index is generated from executable state and exists only as a published navigation surface.",
            "",
        ]
        return "\n".join(lines)

    def _build_domain_overview(
        self,
        domain: dict[str, Any],
        entities: list[dict[str, Any]],
        relations: list[dict[str, Any]],
        governance_traces: list[dict[str, Any]],
    ) -> str:
        domain_id = domain["domain_id"]
        name = domain.get("name") or domain_id
        lines = [
            f"# Domain Overview: {name}",
            "",
            f"- Domain ID: `{domain_id}`",
            f"- Domain Version: `{domain.get('version', 'unknown')}`",
            f"- Executable Source: `SQLite runtime`",
            f"- Domain Status: `{domain.get('status', 'unknown')}`",
            "",
            "## Materialized Content",
            f"- Entity snapshots: `{len(entities)}`",
            f"- Relation snapshots: `{len(relations)}`",
            f"- Governance reflections: `{len(governance_traces)}`",
            "",
            "## Traceability",
            "- Each snapshot below carries the executable object ID, type, version, and source state.",
            "- Approved governance reflections link proposal, decision, object history, and the published snapshot.",
            "- The treefolder remains derived from the executable core, not sovereign truth.",
            "",
        ]
        if governance_traces:
            lines.append("## Governance Reflections")
            for trace in governance_traces:
                lines.append(
                    f"- Proposal `{trace['proposal_id']}` / Decision `{trace['decision_id']}` "
                    f"for `{trace['object_type']}` `{trace['object_id']}` (v{trace['object_version']})"
                )
            lines.append("")
        if entities:
            lines.append("## Entity Snapshots")
            for entity in entities:
                lines.append(
                    f"- [{entity['label']}](../entities/{entity['entity_id']}.md) "
                    f"(`{entity['entity_id']}`, v{entity['version']})"
                )
            lines.append("")
        if relations:
            lines.append("## Relation Snapshots")
            for relation in relations:
                lines.append(
                    f"- [{relation['relation_id']}](../relations/{relation['relation_id']}.md) "
                    f"(`{relation['source_entity_id']}` -> `{relation['target_entity_id']}`, v{relation['version']})"
                )
            lines.append("")
        lines.extend(
            [
                "## Navigation",
                "- [Domain Contract](../DOMAIN_CONTRACT.yaml)",
                "- [Entities Index](../entities/INDEX.md)",
                "- [Relations Index](../relations/INDEX.md)",
                "- [Domain Operational Summary](./DOMAIN_OPERATIONAL_SUMMARY.md)",
                "- [Pending Review Queue](./PENDING_REVIEW_QUEUE.md)",
                "- [Active Decision Queue](./ACTIVE_DECISION_QUEUE.md)",
                "- [Recent Changes](./RECENT_CHANGES.md)",
                "- [Meeting Context](./MEETING_CONTEXT.md)",
                "- [Project State](./PROJECT_STATE.md)",
                "- [Governance Trace](./GOVERNANCE_TRACE.md)",
                "",
            ]
        )
        return "\n".join(lines)

    def _build_domain_operational_summary(self, domain: dict[str, Any], operational_summary: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        pending_proposals = operational_summary["pending_proposals"]
        recent_decisions = operational_summary["recent_decisions"]
        lines = [
            f"# Domain Operational Summary: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Status: `{domain.get('status', 'unknown')}`",
            f"- Version: `{domain.get('version', 'unknown')}`",
            f"- Entity Snapshots: `{operational_summary['entity_count']}`",
            f"- Relation Snapshots: `{operational_summary['relation_count']}`",
            f"- Pending Proposals: `{operational_summary['pending_proposal_count']}`",
            f"- Approved Decisions: `{operational_summary['approved_decision_count']}`",
            f"- Rejected Decisions: `{operational_summary['rejected_decision_count']}`",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Domain Overview](./DOMAIN_OVERVIEW.md)",
            "- [Pending Review Queue](./PENDING_REVIEW_QUEUE.md)",
            "- [Active Decision Queue](./ACTIVE_DECISION_QUEUE.md)",
            "- [Recent Changes](./RECENT_CHANGES.md)",
            "- [Governance Trace](./GOVERNANCE_TRACE.md)",
            "",
        ]
        if pending_proposals:
            lines.extend(["## Pending Review Highlights", ""])
            for entry in pending_proposals[:5]:
                proposal = entry["proposal"]
                decision = entry["decision"] or {}
                target_object_type = proposal["target_object_type"]
                target_object_id = proposal["target_object_id"]
                history_href = f"/surface/objects/{target_object_type}/{target_object_id}/history"
                review_href = f"/surface/proposals/{proposal['proposal_id']}"
                lines.extend(
                    [
                        f"### Proposal `{proposal['proposal_id']}`",
                        "",
                        f"- Proposal Type: `{proposal['proposal_type']}`",
                        f"- Target: `{target_object_type}` `{target_object_id}`",
                        f"- Proposal State: `{proposal.get('proposal_state', 'unknown')}`",
                        f"- Decision State: `{decision.get('decision_state', 'unknown')}`",
                        f"- Proposed By: `{proposal.get('proposed_by', 'unknown')}`",
                        f"- Rationale: {proposal.get('rationale') or '—'}",
                        f"- Review Surface: [{proposal['proposal_id']}]({review_href})",
                        f"- Object History: [{target_object_id}]({history_href})",
                    ]
                )
                if entry.get("snapshot_path"):
                    lines.append(f"- Published Snapshot: [{entry['snapshot_path']}]({entry['snapshot_path']})")
                lines.append("")
        else:
            lines.extend(["## Pending Review Highlights", "", "No pending proposals are currently queued for review.", ""])
        if recent_decisions:
            lines.extend(["## Recent Decisions", ""])
            for entry in recent_decisions[:5]:
                proposal = entry["proposal"]
                decision = entry["decision"]
                target_object_type = proposal["target_object_type"]
                target_object_id = proposal["target_object_id"]
                history_href = f"/surface/objects/{target_object_type}/{target_object_id}/history"
                proposal_href = f"/surface/proposals/{proposal['proposal_id']}"
                decision_href = f"/surface/decisions/{decision['decision_id']}"
                lines.extend(
                    [
                        f"### Decision `{decision['decision_id']}`",
                        "",
                        f"- Decision State: `{decision.get('decision_state', 'unknown')}`",
                        f"- Proposal Type: `{proposal['proposal_type']}`",
                        f"- Target: `{target_object_type}` `{target_object_id}`",
                        f"- Decided By: `{decision.get('decided_by') or 'unknown'}`",
                        f"- Version: `{entry.get('object_version') or 'unknown'}`",
                        f"- Decision Surface: [{decision['decision_id']}]({decision_href})",
                        f"- Proposal Surface: [{proposal['proposal_id']}]({proposal_href})",
                        f"- Object History: [{target_object_id}]({history_href})",
                    ]
                )
                if entry.get("snapshot_path"):
                    lines.append(f"- Published Snapshot: [{entry['snapshot_path']}]({entry['snapshot_path']})")
                lines.append("")
        else:
            lines.extend(["## Recent Decisions", "", "No approved or rejected decisions were published for this domain yet.", ""])
        return "\n".join(lines)

    def _build_pending_review_queue(self, domain: dict[str, Any], review_queue: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        pending_proposals = review_queue["pending_proposals"]
        lines = [
            f"# Pending Review Queue: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Pending Proposals: `{review_queue['pending_proposal_count']}`",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Domain Operational Summary](./DOMAIN_OPERATIONAL_SUMMARY.md)",
            "- [Domain Overview](./DOMAIN_OVERVIEW.md)",
            "- [Governance Trace](./GOVERNANCE_TRACE.md)",
            "",
        ]
        if pending_proposals:
            for entry in pending_proposals:
                proposal = entry["proposal"]
                decision = entry["decision"] or {}
                target_object_type = proposal["target_object_type"]
                target_object_id = proposal["target_object_id"]
                history_href = f"/surface/objects/{target_object_type}/{target_object_id}/history"
                review_href = f"/surface/proposals/{proposal['proposal_id']}"
                decision_href = f"/surface/decisions/{decision.get('decision_id') or proposal['decision_id']}"
                lines.extend(
                    [
                        f"### Proposal `{proposal['proposal_id']}`",
                        "",
                        f"- Proposal Type: `{proposal['proposal_type']}`",
                        f"- Target: `{target_object_type}` `{target_object_id}`",
                        f"- Proposal State: `{proposal.get('proposal_state', 'unknown')}`",
                        f"- Decision State: `{decision.get('decision_state', 'unknown')}`",
                        f"- Proposed By: `{proposal.get('proposed_by', 'unknown')}`",
                        f"- Rationale: {proposal.get('rationale') or '—'}",
                        f"- Review Surface: [{proposal['proposal_id']}]({review_href})",
                        f"- Decision Surface: [{decision['decision_id']}]({decision_href})",
                        f"- Object History: [{target_object_id}]({history_href})",
                    ]
                )
                if entry.get("snapshot_path"):
                    lines.append(f"- Published Snapshot: [{entry['snapshot_path']}]({entry['snapshot_path']})")
                lines.append("")
        else:
            lines.extend(["No pending proposals are currently queued for review.", ""])
        return "\n".join(lines)

    def _build_active_decision_queue(self, domain: dict[str, Any], active_queue: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        active_items = active_queue["active_items"]
        lines = [
            f"# Active Decision Queue: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Active Items: `{active_queue['active_item_count']}`",
            f"- Pending Proposals: `{active_queue['pending_proposal_count']}`",
            f"- Approved Decisions: `{active_queue['approved_decision_count']}`",
            f"- Rejected Decisions: `{active_queue['rejected_decision_count']}`",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Domain Operational Summary](./DOMAIN_OPERATIONAL_SUMMARY.md)",
            "- [Pending Review Queue](./PENDING_REVIEW_QUEUE.md)",
            "- [Recent Changes](./RECENT_CHANGES.md)",
            "- [Governance Trace](./GOVERNANCE_TRACE.md)",
            "",
        ]
        if active_items:
            for item in active_items:
                proposal = item["proposal"]
                decision = item["decision"] or {}
                target_object_type = proposal["target_object_type"]
                target_object_id = proposal["target_object_id"]
                history_href = f"/surface/objects/{target_object_type}/{target_object_id}/history"
                proposal_href = f"/surface/proposals/{proposal['proposal_id']}"
                decision_href = f"/surface/decisions/{decision.get('decision_id') or proposal['decision_id']}"
                lines.extend(
                    [
                        f"### {item['kind'].replace('_', ' ').title()} `{item['proposal_id']}`",
                        "",
                        f"- Queue State: `{item['status']}`",
                        f"- Next Action: `{item['next_action']}`",
                        f"- Proposal Type: `{proposal['proposal_type']}`",
                        f"- Target: `{target_object_type}` `{target_object_id}`",
                        f"- Decision State: `{decision.get('decision_state', 'unknown')}`",
                        f"- Proposal Surface: [{proposal['proposal_id']}]({proposal_href})",
                        f"- Decision Surface: [{decision['decision_id']}]({decision_href})",
                        f"- Object History: [{target_object_id}]({history_href})",
                    ]
                )
                if item.get("snapshot_path"):
                    lines.append(f"- Published Snapshot: [{item['snapshot_path']}]({item['snapshot_path']})")
                lines.append("")
        else:
            lines.extend(["No active decisions or pending proposals are currently queued for review.", ""])
        return "\n".join(lines)

    def _build_recent_changes(self, domain: dict[str, Any], recent_changes: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        changes = recent_changes["recent_changes"]
        lines = [
            f"# Recent Changes: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Recent Change Count: `{recent_changes['recent_change_count']}`",
            f"- Latest Event ID: `{recent_changes['latest_event_id'] or 'unknown'}`",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Domain Operational Summary](./DOMAIN_OPERATIONAL_SUMMARY.md)",
            "- [Pending Review Queue](./PENDING_REVIEW_QUEUE.md)",
            "- [Active Decision Queue](./ACTIVE_DECISION_QUEUE.md)",
            "- [Governance Trace](./GOVERNANCE_TRACE.md)",
            "",
        ]
        if changes:
            for entry in changes:
                event = entry["event"]
                proposal = entry["proposal"]
                decision = entry["decision"] or {}
                if proposal is not None:
                    target_object_type = proposal["target_object_type"]
                    target_object_id = proposal["target_object_id"]
                else:
                    target_object_type = event["target_object_type"]
                    target_object_id = event["target_object_id"]
                history_href = f"/surface/objects/{target_object_type}/{target_object_id}/history"
                lines.extend(
                    [
                        f"### Event `{event['event_id']}`",
                        "",
                        f"- Event Type: `{event['event_type']}`",
                        f"- Target: `{target_object_type}` `{target_object_id}`",
                        f"- Performed By: `{event.get('performed_by') or 'unknown'}`",
                        f"- Performed Via: `{event.get('performed_via') or 'unknown'}`",
                        f"- Reason: {event.get('reason') or '—'}",
                        f"- Object Version: `{entry.get('object_version') or 'unknown'}`",
                        f"- History Version Count: `{entry['history_version_count']}`",
                        f"- Latest Version Number: `{entry['latest_version_number']}`",
                        f"- Object History: [{target_object_id}]({history_href})",
                    ]
                )
                if proposal is not None:
                    lines.append(f"- Proposal Surface: [{proposal['proposal_id']}](/surface/proposals/{proposal['proposal_id']})")
                if decision:
                    lines.append(f"- Decision Surface: [{decision['decision_id']}](/surface/decisions/{decision['decision_id']})")
                mutation_event_id = (event.get("payload") or {}).get("mutation_event_id")
                if mutation_event_id:
                    lines.append(f"- Mutation Event ID: `{mutation_event_id}`")
                if entry.get("snapshot_path"):
                    lines.append(f"- Published Snapshot: [{entry['snapshot_path']}]({entry['snapshot_path']})")
                lines.append("")
        else:
            lines.extend(["No recent changes are currently published for this domain.", ""])
        return "\n".join(lines)

    def _build_meeting_context(self, domain: dict[str, Any], meeting_context: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        lines = [
            f"# Meeting Context: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Pending Proposals: `{meeting_context['pending_proposal_count']}`",
            f"- Recent Changes: `{meeting_context['recent_change_count']}`",
            "",
            "## Agenda Seed",
        ]
        for item in meeting_context["agenda_seed"]:
            lines.append(f"- {item}")
        lines.extend(["", "## Entity Highlights"])
        if meeting_context["entity_highlights"]:
            for entity in meeting_context["entity_highlights"]:
                lines.append(f"- `{entity['entity_id']}` / {entity['label']} (`{entity['validation_status']}`)")
        else:
            lines.append("- No entity highlights are currently available.")
        lines.extend(["", "## Relation Highlights"])
        if meeting_context["relation_highlights"]:
            for relation in meeting_context["relation_highlights"]:
                lines.append(
                    f"- `{relation['relation_id']}`: `{relation['source_entity_id']}` -> `{relation['target_entity_id']}`"
                )
        else:
            lines.append("- No relation highlights are currently available.")
        lines.extend(["", "## Pending Proposals"])
        if meeting_context["pending_proposals"]:
            for entry in meeting_context["pending_proposals"]:
                proposal = entry["proposal"]
                lines.append(
                    f"- `{proposal['proposal_id']}` (`{proposal['proposal_type']}`) "
                    f"for `{proposal['target_object_type']}` `{proposal['target_object_id']}`"
                )
        else:
            lines.append("- No pending proposals.")
        lines.extend(
            [
                "",
                "## Navigation",
                "- [Domain Index](../INDEX.md)",
                "- [Project State](./PROJECT_STATE.md)",
                "- [Active Decision Queue](./ACTIVE_DECISION_QUEUE.md)",
                "",
            ]
        )
        return "\n".join(lines)

    def _build_project_state(self, domain: dict[str, Any], project_state: dict[str, Any]) -> str:
        name = domain.get("name") or domain["domain_id"]
        counts = project_state["counts"]
        lines = [
            f"# Project State: {name}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Domain Status: `{domain.get('status', 'unknown')}`",
            "",
            "## Counts",
        ]
        for key, value in counts.items():
            lines.append(f"- {key}: `{value}`")
        lines.extend(["", "## Open Work"])
        pending = project_state["operational_summary"]["pending_proposals"]
        if pending:
            for entry in pending:
                proposal = entry["proposal"]
                lines.append(f"- `{proposal['proposal_id']}` / `{proposal['proposal_type']}`")
        else:
            lines.append("- No pending proposals.")
        lines.extend(
            [
                "",
                "## Navigation",
                "- [Domain Index](../INDEX.md)",
                "- [Meeting Context](./MEETING_CONTEXT.md)",
                "- [Domain Operational Summary](./DOMAIN_OPERATIONAL_SUMMARY.md)",
                "",
            ]
        )
        return "\n".join(lines)

    def _write_entity_views(self, domain_root: Path, domain: dict[str, Any], entities: list[dict[str, Any]]) -> None:
        index_lines = [
            f"# Entity Index: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Published snapshots: `{len(entities)}`",
            "",
        ]
        if entities:
            index_lines.append("## Snapshots")
            for entity in entities:
                index_lines.append(
                    f"- [{entity['label']}](./{entity['entity_id']}.md) "
                    f"(`{entity['entity_id']}`, v{entity['version']}, `{entity['validation_status']}`)"
                )
        else:
            index_lines.append("No entity snapshots were published for this domain.")
        index_lines.extend(["", "## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "entities" / "INDEX.md", "\n".join(index_lines))

        for entity in entities:
            self._write_text(domain_root / "entities" / f"{entity['entity_id']}.md", self._build_entity_snapshot(domain, entity))

    def _write_relation_views(self, domain_root: Path, domain: dict[str, Any], relations: list[dict[str, Any]]) -> None:
        index_lines = [
            f"# Relation Index: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Published snapshots: `{len(relations)}`",
            "",
        ]
        if relations:
            index_lines.append("## Snapshots")
            for relation in relations:
                index_lines.append(
                    f"- [{relation['relation_id']}](./{relation['relation_id']}.md) "
                    f"(`{relation['source_entity_id']}` -> `{relation['target_entity_id']}`, v{relation['version']}, `{relation['validation_status']}`)"
                )
        else:
            index_lines.append("No relation snapshots were published for this domain.")
        index_lines.extend(["", "## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "relations" / "INDEX.md", "\n".join(index_lines))

        for relation in relations:
            self._write_text(
                domain_root / "relations" / f"{relation['relation_id']}.md",
                self._build_relation_snapshot(domain, relation),
            )

    def _write_payload_views(self, domain_root: Path, domain: dict[str, Any], payloads: list[dict[str, Any]]) -> None:
        index_lines = [
            f"# Payload Index: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Published payload records: `{len(payloads)}`",
            "",
        ]
        if payloads:
            index_lines.append("## Payload Records")
            for payload in payloads:
                index_lines.append(
                    f"- [{payload['payload_id']}](./{payload['payload_id']}.md) "
                    f"(`{payload['payload_type']}`, v{payload['version']}, canonical: `{payload['canonical_flag']}`)"
                )
        else:
            index_lines.append("No payload records were published for this domain.")
        index_lines.extend(["", "## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "payloads" / "INDEX.md", "\n".join(index_lines))

        for payload in payloads:
            self._write_text(domain_root / "payloads" / f"{payload['payload_id']}.md", self._build_payload_snapshot(domain, payload))

    def _write_sources_index(self, domain_root: Path, domain: dict[str, Any], sources: list[dict[str, Any]]) -> None:
        lines = [
            f"# Source Registry: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Registered sources: `{len(sources)}`",
            "- Content policy: metadata and payload references only; raw payload content is not expanded here.",
            "",
        ]
        if sources:
            lines.append("## Sources")
            for source in sources:
                lines.extend(
                    [
                        f"### `{source['source_id']}`",
                        "",
                        f"- Type: `{source.get('source_type')}`",
                        f"- Origin: `{source.get('source_origin')}`",
                        f"- URI: `{source.get('source_uri') or 'none'}`",
                        f"- Storage Ref: `{source.get('storage_ref') or 'none'}`",
                        f"- Raw Payload Ref: `{source.get('raw_payload_ref') or 'none'}`",
                        f"- Ingestion Status: `{source.get('ingestion_status')}`",
                        f"- Created At: `{source.get('created_at')}`",
                        "",
                    ]
                )
        else:
            lines.append("No sources are registered for this domain.")
            lines.append("")
        lines.extend(["## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "sources" / "INDEX.md", "\n".join(lines))

    def _write_ingestion_runs_index(self, domain_root: Path, domain: dict[str, Any], jobs: list[dict[str, Any]]) -> None:
        lines = [
            f"# Ingestion Runs: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Runs: `{len(jobs)}`",
            "",
        ]
        if jobs:
            lines.append("## Runs")
            for job in jobs:
                lines.extend(
                    [
                        f"### `{job['job_id']}`",
                        "",
                        f"- Type: `{job.get('job_type')}`",
                        f"- Status: `{job.get('status')}`",
                        f"- Target: `{job.get('target_ref')}`",
                        f"- Started At: `{job.get('started_at')}`",
                        f"- Finished At: `{job.get('finished_at') or 'not finished'}`",
                        f"- Logs Ref: `{job.get('logs_ref') or 'none'}`",
                        "",
                    ]
                )
        else:
            lines.append("No ingestion runs are recorded for this domain.")
            lines.append("")
        lines.extend(["## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "ingestion_runs" / "INDEX.md", "\n".join(lines))

    def _build_authoring_summary(
        self,
        domain: dict[str, Any],
        domain_versions: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        ingestion_jobs: list[dict[str, Any]],
        entities: list[dict[str, Any]],
        relations: list[dict[str, Any]],
    ) -> str:
        active_version = next((version for version in domain_versions if version.get("status") == "active"), None)
        entity_status_counts: dict[str, int] = {}
        relation_status_counts: dict[str, int] = {}
        for entity in entities:
            status = str(entity.get("validation_status") or "unknown")
            entity_status_counts[status] = entity_status_counts.get(status, 0) + 1
        for relation in relations:
            status = str(relation.get("validation_status") or "unknown")
            relation_status_counts[status] = relation_status_counts.get(status, 0) + 1
        record = {
            "domain_id": domain["domain_id"],
            "domain_name": domain.get("name"),
            "active_domain_version_id": active_version.get("domain_version_id") if active_version else None,
            "active_domain_version_label": active_version.get("version_label") if active_version else None,
            "domain_version_count": len(domain_versions),
            "source_count": len(sources),
            "ingestion_run_count": len(ingestion_jobs),
            "entity_count": len(entities),
            "relation_count": len(relations),
            "entity_status_counts": entity_status_counts,
            "relation_status_counts": relation_status_counts,
        }
        return "\n".join(
            [
                f"# Authoring Summary: {domain.get('name') or domain['domain_id']}",
                "",
                "This projection summarizes local operational authoring state from the executable runtime.",
                "",
                "```yaml",
                yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip("\n"),
                "```",
                "",
                "## Navigation",
                "- [Domain Index](../INDEX.md)",
                "- [Domain Charter](../DOMAIN_CHARTER.yaml)",
                "- [Sources Index](../sources/INDEX.md)",
                "- [Ingestion Runs Index](../ingestion_runs/INDEX.md)",
                "",
            ]
        )

    def _write_projection_index(self, domain_root: Path, domain: dict[str, Any], projections: list[dict[str, Any]]) -> None:
        lines = [
            f"# Projection Records Index: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Projection records: `{len(projections)}`",
            "",
        ]
        if projections:
            lines.append("## Projection Records")
            for projection in projections:
                lines.append(
                    f"- `{projection['projection_id']}` "
                    f"(`{projection['projection_type']}`, `{projection['materialization_format']}`, `{projection['freshness_status']}`)"
                )
        else:
            lines.append("No persisted projection records are currently linked to this domain.")
        lines.extend(["", "## Navigation", "- [Domain Index](../INDEX.md)", ""])
        self._write_text(domain_root / "projections" / "PROJECTIONS_INDEX.md", "\n".join(lines))

    def _build_payload_snapshot(self, domain: dict[str, Any], payload: dict[str, Any]) -> str:
        record = self._ordered_snapshot_record(
            {
                "payload_id": payload["payload_id"],
                "domain_id": domain["domain_id"],
                "payload_type": payload["payload_type"],
                "owner_object_type": payload["owner_object_type"],
                "owner_object_id": payload["owner_object_id"],
                "storage_ref": payload["storage_ref"],
                "format": payload["format"],
                "checksum": payload["checksum"],
                "editability": payload["editability"],
                "canonical_flag": payload["canonical_flag"],
                "version": payload["version"],
                "created_at": payload["created_at"],
                "updated_at": payload["updated_at"],
            }
        )
        return "\n".join(
            [
                f"# Payload Snapshot: {payload['payload_id']}",
                "",
                "- Object Type: `payload`",
                f"- Object ID: `{payload['payload_id']}`",
                f"- Domain ID: `{domain['domain_id']}`",
                "- Executable Source: `SQLite runtime`",
                f"- Version: `{payload.get('version', 'unknown')}`",
                f"- Editability: `{payload.get('editability', 'unknown')}`",
                "",
                "## Executable Record",
                "```yaml",
                yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip("\n"),
                "```",
                "",
                "## Navigation",
                "- [Domain Index](../INDEX.md)",
                "- [Payloads Index](./INDEX.md)",
                "",
            ]
        )

    def _write_canonical_indexes(self, entities: list[dict[str, Any]], relations: list[dict[str, Any]]) -> None:
        canonical_entities = [
            entity
            for entity in entities
            if entity.get("scope") == "canonical" or entity.get("canonical_candidate_flag") or entity.get("validation_status") == "validated"
        ]
        validated_relations = [relation for relation in relations if relation.get("validation_status") == "validated"]
        entity_lines = [
            "# Canonical Entity Index",
            "",
            "- Executable Source: `SQLite runtime`",
            f"- Published records: `{len(canonical_entities)}`",
            "",
        ]
        if canonical_entities:
            entity_lines.append("## Records")
            for entity in canonical_entities:
                domain_id = entity.get("domain_id") or "unscoped"
                entity_lines.append(
                    f"- `{entity['entity_id']}` / `{entity['label']}` "
                    f"-> ../../domains/{domain_id}/entities/{entity['entity_id']}.md"
                )
        else:
            entity_lines.append("No canonical or validated entity records are currently published.")
        self._write_text(self.tree_root / "canonical" / "entities" / "INDEX.md", "\n".join(entity_lines))

        relation_lines = [
            "# Canonical Relation Index",
            "",
            "- Executable Source: `SQLite runtime`",
            f"- Published records: `{len(validated_relations)}`",
            "",
        ]
        if validated_relations:
            relation_lines.append("## Records")
            for relation in validated_relations:
                domain_id = relation.get("domain_context") or "unscoped"
                relation_lines.append(
                    f"- `{relation['relation_id']}` "
                    f"-> ../../domains/{domain_id}/relations/{relation['relation_id']}.md"
                )
        else:
            relation_lines.append("No validated relation records are currently published.")
        self._write_text(self.tree_root / "canonical" / "relations" / "INDEX.md", "\n".join(relation_lines))

    def _write_global_projection_index(self, projections: list[dict[str, Any]]) -> None:
        lines = [
            "# Global Projection Records Index",
            "",
            "- Executable Source: `SQLite runtime`",
            f"- Projection records: `{len(projections)}`",
            "",
        ]
        if projections:
            lines.append("## Records")
            for projection in projections:
                lines.append(
                    f"- `{projection['projection_id']}` "
                    f"(`{projection['projection_type']}`, `{projection['freshness_status']}`)"
                )
        else:
            lines.append("No persisted projection records are currently published.")
        self._write_text(self.tree_root / "projections" / "INDEX.md", "\n".join(lines))

    def _write_proposal_inbox_index(self) -> None:
        proposals = self.governance_service.list_proposals(proposal_state="pending")
        lines = [
            "# Proposal Inbox Index",
            "",
            "- Executable Source: `SQLite runtime`",
            "- Authority: this folder may receive remote proposal artifacts, but DB proposals remain authoritative after import.",
            f"- Pending DB proposals exported: `{len(proposals)}`",
            "",
        ]
        if proposals:
            lines.append("## DB-Derived Proposal Artifacts")
            for proposal in proposals:
                artifact_name = f"{proposal['proposal_id']}.yaml"
                lines.append(
                    f"- [{proposal['proposal_id']}](./{artifact_name}) "
                    f"(`{proposal['proposal_type']}`, target `{proposal['target_object_type']}` `{proposal['target_object_id']}`)"
                )
                self._write_yaml(
                    self.tree_root / "inbox" / "proposals" / artifact_name,
                    {
                        "source": "db-derived",
                        "proposal_id": proposal["proposal_id"],
                        "proposal_type": proposal["proposal_type"],
                        "target_object_type": proposal["target_object_type"],
                        "target_object_id": proposal["target_object_id"],
                        "proposed_changes": proposal.get("proposed_changes") or {},
                        "proposed_by": proposal.get("proposed_by"),
                        "rationale": proposal.get("rationale"),
                        "evidence_refs": proposal.get("evidence_refs") or [],
                        "proposal_state": proposal.get("proposal_state"),
                        "decision_id": proposal.get("decision_id"),
                    },
                )
        else:
            lines.append("No pending DB proposals are currently exported.")
        lines.append("")
        self._write_text(self.tree_root / "inbox" / "proposals" / "INDEX.md", "\n".join(lines))

    def _build_entity_snapshot(self, domain: dict[str, Any], entity: dict[str, Any]) -> str:
        record = self._ordered_snapshot_record(
            {
                "entity_id": entity["entity_id"],
                "domain_id": entity.get("domain_id"),
                "scope": entity["scope"],
                "entity_type": entity["entity_type"],
                "label": entity["label"],
                "short_description": entity.get("short_description"),
                "attributes": entity.get("attributes", {}),
                "aliases": entity.get("aliases", []),
                "confidence": entity.get("confidence"),
                "validation_status": entity.get("validation_status"),
                "canonical_candidate_flag": entity.get("canonical_candidate_flag"),
                "provenance_refs": entity.get("provenance_refs", []),
                "payload_refs": entity.get("payload_refs", []),
                "version": entity.get("version"),
                "created_at": entity.get("created_at"),
                "updated_at": entity.get("updated_at"),
            }
        )
        lines = [
            f"# Entity Snapshot: {entity['label']}",
            "",
            f"- Object Type: `entity`",
            f"- Object ID: `{entity['entity_id']}`",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Executable Source: `SQLite runtime`",
            f"- Version: `{entity.get('version', 'unknown')}`",
            f"- Validation Status: `{entity.get('validation_status', 'unknown')}`",
            "",
            "## Summary",
            entity.get("short_description") or "No short description was published for this entity.",
            "",
            "## Executable Record",
            "```yaml",
            yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip("\n"),
            "```",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Entities Index](./INDEX.md)",
            "",
        ]
        return "\n".join(lines)

    def _build_relation_snapshot(self, domain: dict[str, Any], relation: dict[str, Any]) -> str:
        record = self._ordered_snapshot_record(
            {
                "relation_id": relation["relation_id"],
                "domain_context": relation.get("domain_context"),
                "source_entity_id": relation["source_entity_id"],
                "target_entity_id": relation["target_entity_id"],
                "relation_type": relation["relation_type"],
                "directionality": relation["directionality"],
                "evidence_refs": relation.get("evidence_refs", []),
                "confidence": relation.get("confidence"),
                "validation_status": relation.get("validation_status"),
                "asserted_by": relation.get("asserted_by"),
                "validated_by": relation.get("validated_by"),
                "version": relation.get("version"),
                "created_at": relation.get("created_at"),
                "updated_at": relation.get("updated_at"),
            }
        )
        lines = [
            f"# Relation Snapshot: {relation['relation_id']}",
            "",
            f"- Object Type: `relation`",
            f"- Object ID: `{relation['relation_id']}`",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Executable Source: `SQLite runtime`",
            f"- Version: `{relation.get('version', 'unknown')}`",
            f"- Validation Status: `{relation.get('validation_status', 'unknown')}`",
            "",
            "## Summary",
            f"{relation['source_entity_id']} references {relation['target_entity_id']}.",
            "",
            "## Executable Record",
            "```yaml",
            yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip("\n"),
            "```",
            "",
            "## Navigation",
            "- [Domain Index](../INDEX.md)",
            "- [Relations Index](./INDEX.md)",
            "",
        ]
        return "\n".join(lines)

    def _group_governance_traces(self, domains: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {domain["domain_id"]: [] for domain in domains}
        approved_bundles = self.governance_service.list_decisions(decision_state="approved")
        for bundle in approved_bundles:
            trace = self._build_governance_trace_entry(bundle)
            if trace is None:
                continue
            grouped.setdefault(trace["domain_id"], []).append(trace)
        for traces in grouped.values():
            traces.sort(key=lambda trace: (trace["object_type"], trace["object_id"], trace["decision_id"]))
        return grouped

    def _build_governance_trace_entry(self, bundle: dict[str, Any]) -> dict[str, Any] | None:
        proposal = bundle["proposal"]
        decision = bundle["decision"]
        object_type = proposal["target_object_type"]
        object_id = proposal["target_object_id"]
        history = self.governance_service.get_object_history(object_type, object_id)
        current_object = history.get("current_object")
        if not current_object:
            return None
        domain_id = self._domain_id_for_object(object_type, current_object)
        if domain_id is None:
            return None
        approval_events = self.event_service.list_events(
            target_object_type="decision",
            target_object_id=decision["decision_id"],
            event_type="decision.approved",
        )
        approval_event = approval_events[-1] if approval_events else None
        mutation_event_id = None
        if approval_event is not None:
            payload = approval_event.get("payload") or {}
            mutation_event_id = payload.get("mutation_event_id")
        mutation_object = None
        if approval_event is not None:
            mutation_object = (approval_event.get("payload") or {}).get("mutation_object")
        if mutation_object is None:
            mutation_object = current_object
        snapshot_path = self._snapshot_path_for_object(domain_id, object_type, object_id)
        return {
            "domain_id": domain_id,
            "object_type": object_type,
            "object_id": object_id,
            "proposal_id": proposal["proposal_id"],
            "proposal_type": proposal["proposal_type"],
            "decision_id": decision["decision_id"],
            "decision_state": decision["decision_state"],
            "decided_by": decision.get("decided_by"),
            "rationale": decision.get("rationale"),
            "object_version": mutation_object.get("version"),
            "history_version_count": history["version_count"],
            "latest_version_number": history["latest_version_number"],
            "mutation_event_id": mutation_event_id,
            "snapshot_path": snapshot_path,
            "version_trail": [version["version_number"] for version in history["versions"]],
        }

    def _write_governance_trace(
        self,
        domain_root: Path,
        domain: dict[str, Any],
        governance_traces: list[dict[str, Any]],
    ) -> None:
        lines = [
            f"# Governance Trace: {domain.get('name') or domain['domain_id']}",
            "",
            f"- Domain ID: `{domain['domain_id']}`",
            f"- Domain Version: `{domain.get('version', 'unknown')}`",
            f"- Executable Source: `SQLite runtime`",
            f"- Approved Reflections: `{len(governance_traces)}`",
            "",
            "## Traceability",
            "- Every reflection links a proposal, a decision, the executable object history, and the published snapshot.",
            "- The treefolder remains a derived publication surface; approval still occurs in the governance flow.",
            "",
        ]
        if governance_traces:
            for trace in governance_traces:
                lines.extend(
                    [
                        f"### {trace['object_type'].title()} `{trace['object_id']}`",
                        "",
                        f"- Proposal ID: `{trace['proposal_id']}`",
                        f"- Proposal Type: `{trace['proposal_type']}`",
                        f"- Decision ID: `{trace['decision_id']}`",
                        f"- Decision State: `{trace['decision_state']}`",
                        f"- Decided By: `{trace['decided_by'] or 'unknown'}`",
                        f"- Object Version: `{trace['object_version']}`",
                        f"- History Version Count: `{trace['history_version_count']}`",
                        f"- Latest Version Number: `{trace['latest_version_number']}`",
                        f"- Version Trail: `{trace['version_trail']}`",
                        f"- Mutation Event ID: `{trace['mutation_event_id'] or 'unknown'}`",
                        f"- Snapshot: [{trace['snapshot_path']}]({trace['snapshot_path']})",
                        "",
                        "```yaml",
                        yaml.safe_dump(trace, sort_keys=False, allow_unicode=True).rstrip("\n"),
                        "```",
                        "",
                    ]
                )
        else:
            lines.append("No approved governance reflections were published for this domain yet.")
            lines.append("")
        lines.extend(
            [
                "## Navigation",
                "- [Domain Index](../INDEX.md)",
                "- [Domain Overview](./DOMAIN_OVERVIEW.md)",
                "- [Active Decision Queue](./ACTIVE_DECISION_QUEUE.md)",
                "- [Recent Changes](./RECENT_CHANGES.md)",
                "",
            ]
        )
        self._write_text(domain_root / "projections" / "GOVERNANCE_TRACE.md", "\n".join(lines))

    def _domain_id_for_object(self, object_type: str, object_record: dict[str, Any]) -> str | None:
        if object_type == "entity":
            return object_record.get("domain_id")
        if object_type == "relation":
            return object_record.get("domain_context")
        if object_type == "domain":
            return object_record.get("domain_id")
        if object_type == "payload":
            return self._payload_domain_id(object_record)
        if object_type == "projection":
            return self._projection_domain_ids(object_record)[0] if self._projection_domain_ids(object_record) else None
        return None

    def _snapshot_path_for_object(self, domain_id: str, object_type: str, object_id: str) -> str | None:
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

    def _build_system_status(self, available_domains: list[str], artifact_counts: dict[str, int]) -> dict[str, Any]:
        return {
            "publication_timestamp": self._utc_now(),
            "publication_version": self._next_publication_version(),
            "freshness_status": "fresh",
            "available_domains": available_domains,
            "pending_proposals_count": self._count_pending_proposals(),
            "remote_write_policy": "read-only; structured proposals only in tree/inbox/proposals/",
            "published_object_views": artifact_counts,
        }

    def _next_publication_version(self) -> int:
        status_path = self.tree_root / "SYSTEM_STATUS.yaml"
        if not status_path.exists():
            return 1
        try:
            previous = yaml.safe_load(status_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return 1
        previous_version = previous.get("publication_version", 0)
        try:
            return int(previous_version) + 1
        except (TypeError, ValueError):
            return 1

    def _count_pending_proposals(self) -> int:
        return len(self.governance_service.list_proposals(proposal_state="pending"))

    def _group_domain_versions_by_domain(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for version in self.domain_version_service.list_domain_versions():
            grouped.setdefault(version["domain_id"], []).append(version)
        return grouped

    def _group_sources_by_domain(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for source in self.source_service.list_sources():
            grouped.setdefault(source["domain_id"], []).append(source)
        return grouped

    def _group_ingestion_jobs_by_domain(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for job in self.ingestion_job_service.list_jobs():
            target_ref = str(job.get("target_ref") or "")
            if not target_ref.startswith("domain:"):
                continue
            domain_id = target_ref.removeprefix("domain:")
            grouped.setdefault(domain_id, []).append(job)
        return grouped

    def _group_entities_by_domain(self, entities: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for entity in entities:
            domain_id = entity.get("domain_id") or "unscoped"
            grouped.setdefault(domain_id, []).append(entity)
        return grouped

    def _group_relations_by_domain(self, relations: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for relation in relations:
            domain_id = relation.get("domain_context") or "unscoped"
            grouped.setdefault(domain_id, []).append(relation)
        return grouped

    def _group_payloads_by_domain(self, payloads: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for payload in payloads:
            domain_id = self._payload_domain_id(payload)
            if domain_id is None:
                continue
            grouped.setdefault(domain_id, []).append(payload)
        return grouped

    def _group_projections_by_domain(self, projections: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for projection in projections:
            domain_ids = self._projection_domain_ids(projection)
            for domain_id in domain_ids:
                grouped.setdefault(domain_id, []).append(projection)
        return grouped

    def _payload_domain_id(self, payload: dict[str, Any]) -> str | None:
        owner_type = payload.get("owner_object_type")
        owner_id = payload.get("owner_object_id")
        if owner_type == "domain":
            return owner_id
        if owner_type == "source":
            source = self.source_service.get_source_by_id(str(owner_id))
            return source.get("domain_id") if source else None
        if owner_type == "entity":
            entity = self.entity_service.get_entity_by_id(str(owner_id))
            return entity.get("domain_id") if entity else None
        if owner_type == "relation":
            relation = self.relation_service.get_relation_by_id(str(owner_id))
            return relation.get("domain_context") if relation else None
        return None

    def _projection_domain_ids(self, projection: dict[str, Any]) -> list[str]:
        domain_ids: list[str] = []
        for source_ref in projection.get("source_refs") or []:
            source_ref = str(source_ref)
            if self.domain_service.get_domain_by_id(source_ref) is not None and source_ref not in domain_ids:
                domain_ids.append(source_ref)
                continue
            entity = self.entity_service.get_entity_by_id(source_ref)
            if entity and entity.get("domain_id") and entity["domain_id"] not in domain_ids:
                domain_ids.append(entity["domain_id"])
                continue
            relation = self.relation_service.get_relation_by_id(source_ref)
            if relation and relation.get("domain_context") and relation["domain_context"] not in domain_ids:
                domain_ids.append(relation["domain_context"])
        for payload_ref in projection.get("payload_refs") or []:
            payload = self.payload_service.get_payload_by_id(str(payload_ref))
            domain_id = self._payload_domain_id(payload) if payload else None
            if domain_id and domain_id not in domain_ids:
                domain_ids.append(domain_id)
        return domain_ids

    def _ordered_snapshot_record(self, data: dict[str, Any]) -> dict[str, Any]:
        ordered: dict[str, Any] = {}
        for key in (
            "entity_id",
            "relation_id",
            "payload_id",
            "projection_id",
            "domain_id",
            "domain_context",
            "payload_type",
            "projection_type",
            "owner_object_type",
            "owner_object_id",
            "scope",
            "entity_type",
            "label",
            "short_description",
            "source_entity_id",
            "target_entity_id",
            "relation_type",
            "directionality",
            "attributes",
            "aliases",
            "confidence",
            "validation_status",
            "canonical_candidate_flag",
            "evidence_refs",
            "source_refs",
            "storage_ref",
            "format",
            "materialization_format",
            "checksum",
            "editability",
            "canonical_flag",
            "generated_by",
            "generation_scope",
            "freshness_status",
            "asserted_by",
            "validated_by",
            "provenance_refs",
            "payload_refs",
            "version",
            "created_at",
            "updated_at",
        ):
            if key in data:
                ordered[key] = data[key]
        for key, value in data.items():
            if key not in ordered:
                ordered[key] = value
        return ordered

    def _ensure_directory(self, path: Path, *, keep_placeholder: bool = False) -> None:
        path.mkdir(parents=True, exist_ok=True)
        if keep_placeholder:
            self._write_text(path / ".gitkeep", "")

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if content.endswith("\n") or not content else f"{content}\n", encoding="utf-8")

    def _write_yaml(self, path: Path, data: dict[str, Any]) -> None:
        yaml_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
        self._write_text(path, yaml_text.rstrip("\n"))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
