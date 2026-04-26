from __future__ import annotations

from copy import deepcopy
from typing import Any


DAY0_DOMAIN_TEMPLATES: dict[str, dict[str, Any]] = {
    "work_portfolio_governance": {
        "domain": {
            "domain_id": "work_portfolio_governance",
            "name": "Work Portfolio Governance",
            "description": "Day 0 domain for local work portfolio governance.",
            "cognitive_purpose": "Stabilize workspaces, projects, tasks, status records, decisions and source artifacts as operational memory.",
            "status": "active",
            "source_types_supported": ["directory", "md", "json", "jsonl", "txt"],
            "local_entity_types": [
                "workspace",
                "program",
                "project",
                "task",
                "status_record",
                "decision",
                "session_log",
                "source_artifact",
            ],
            "relation_types": [
                "belongs_to_workspace",
                "part_of_program",
                "has_status",
                "has_task",
                "decided_by",
                "evidenced_by",
                "depends_on",
                "produces",
                "updated_in_session",
                "linked_to_email_thread",
            ],
            "promotion_rules": ["manual_review", "provenance_required"],
            "governance_dependencies": ["human_validation", "source_registration"],
        },
        "version": {
            "version_label": "day0",
            "charter": {
                "purpose": "Operate a reliable Day 0 portfolio inventory from local folders and governance/status artifacts.",
                "raw_source_policy": "Folders and files are evidence; project/task/decision entities require review before validation.",
            },
            "allowed_entity_types": [
                "workspace",
                "program",
                "project",
                "task",
                "status_record",
                "decision",
                "session_log",
                "source_artifact",
            ],
            "allowed_relation_types": [
                "belongs_to_workspace",
                "part_of_program",
                "has_status",
                "has_task",
                "decided_by",
                "evidenced_by",
                "depends_on",
                "produces",
                "updated_in_session",
                "linked_to_email_thread",
            ],
            "allowed_payload_types": ["directory_manifest", "md", "json", "jsonl", "txt"],
            "required_fields": {
                "workspace": ["path"],
                "project": ["workspace_path"],
                "source_artifact": ["path"],
            },
            "promotion_rules": ["manual_review", "provenance_required"],
        },
    },
    "mail_archive_day0": {
        "domain": {
            "domain_id": "mail_archive_day0",
            "name": "Mail Archive Day 0",
            "description": "Day 0 domain for factual PST/.derived email archive operation.",
            "cognitive_purpose": "Preserve provenance for messages, threads, tasks, participants and project-link candidates without automatic decision mutation.",
            "status": "active",
            "source_types_supported": ["pst_archive", "derived_mail_surface", "json", "jsonl"],
            "local_entity_types": [
                "mail_archive",
                "mailbox_folder",
                "message",
                "thread",
                "participant",
                "attachment",
                "calendar_item",
                "outlook_task",
                "topic_candidate",
                "decision_candidate",
                "action_item_candidate",
                "project_link_candidate",
            ],
            "relation_types": [
                "message_in_folder",
                "message_in_thread",
                "sent_by",
                "sent_to",
                "cc_to",
                "has_attachment",
                "mentions_topic",
                "mentions_project",
                "creates_action_candidate",
                "records_decision_candidate",
                "evidenced_by_payload",
                "linked_to_workspace_project",
            ],
            "promotion_rules": ["manual_review", "derived_status_required", "no_automatic_project_status_mutation"],
            "governance_dependencies": ["human_validation", "work_portfolio_canonical_projects"],
        },
        "version": {
            "version_label": "day0",
            "charter": {
                "purpose": "Load factual mail metadata and candidates from .derived before attempting any PST parsing.",
                "freshness_policy": "Every projection must preserve stale/partial status from the derived surface.",
            },
            "allowed_entity_types": [
                "mail_archive",
                "mailbox_folder",
                "message",
                "thread",
                "participant",
                "attachment",
                "calendar_item",
                "outlook_task",
                "topic_candidate",
                "decision_candidate",
                "action_item_candidate",
                "project_link_candidate",
            ],
            "allowed_relation_types": [
                "message_in_folder",
                "message_in_thread",
                "sent_by",
                "sent_to",
                "cc_to",
                "has_attachment",
                "mentions_topic",
                "mentions_project",
                "creates_action_candidate",
                "records_decision_candidate",
                "evidenced_by_payload",
                "linked_to_workspace_project",
            ],
            "allowed_payload_types": ["pst_archive_metadata", "derived_status", "json", "jsonl"],
            "required_fields": {
                "mail_archive": ["pst_path"],
                "message": ["message_key"],
                "thread": ["thread_key"],
                "project_link_candidate": ["target_project_hint"],
            },
            "promotion_rules": ["manual_review", "derived_status_required", "no_automatic_project_status_mutation"],
        },
    },
}


def list_day0_domain_templates() -> list[dict[str, Any]]:
    return [
        {
            "template_id": template_id,
            "domain_id": template["domain"]["domain_id"],
            "name": template["domain"]["name"],
            "description": template["domain"]["description"],
            "entity_types": template["version"]["allowed_entity_types"],
            "relation_types": template["version"]["allowed_relation_types"],
        }
        for template_id, template in DAY0_DOMAIN_TEMPLATES.items()
    ]


def get_day0_domain_template(template_id: str) -> dict[str, Any] | None:
    template = DAY0_DOMAIN_TEMPLATES.get(template_id)
    return deepcopy(template) if template is not None else None
