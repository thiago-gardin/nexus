from __future__ import annotations

import json
from collections import Counter, deque
from html import escape
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..dependencies import RuntimeContext, get_runtime
from ..materialization import materialize_domain_publication
from ...core.operate_context import build_operate_context
from ...core.materialization.operational_projections import build_domain_active_decision_queue
from ...core.materialization.operational_projections import build_domain_operational_summary
from ...core.materialization.operational_projections import build_domain_recent_changes
from ...core.materialization.operational_projections import build_domain_review_queue


router = APIRouter(prefix="/surface", tags=["surface"])
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

_SUPPORTED_HISTORY_TYPES = {"domain", "entity", "relation", "payload"}
_CONTROLLED_REENTRY_EDITABILITY: dict[str, dict[str, Any]] = {
    "entity": {
        "editable_field": "short_description",
        "proposal_type": "entity_update",
        "artifact_subdir": "entities",
        "summary_label": "Entity short_description",
        "form_label": "Edited Short Description",
        "current_label": "Current Short Description",
        "input_kind": "textarea",
        "allowed_values": None,
        "sprint_note": "Only entity short_description edits are eligible in this sprint.",
        "read_only_note": "All other entity fields remain read-only in this sprint.",
    },
    "relation": {
        "editable_field": "validation_status",
        "proposal_type": "relation_update",
        "artifact_subdir": "relations",
        "summary_label": "Relation validation_status",
        "form_label": "Edited Validation Status",
        "current_label": "Current Validation Status",
        "input_kind": "text",
        "allowed_values": ("proposed", "validated", "rejected", "contested"),
        "sprint_note": "Only relation validation_status edits are eligible in this sprint.",
        "read_only_note": "All other relation fields remain read-only in this sprint.",
    },
}


def _not_found(resource_name: str, resource_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource_name} '{resource_id}' not found")


def _render_page(title: str, *, sections: list[str], note: str | None = None) -> str:
    note_html = ""
    if note is not None:
        note_html = f"<div class='banner'>{note}</div>"
    sections_html = "\n".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b1114;
      --bg-2: #101a1f;
      --panel: #121d23;
      --panel-2: #17242b;
      --border: #28404a;
      --border-strong: #44636f;
      --text: #eef5f2;
      --muted: #9fb0b7;
      --quiet: #72868d;
      --accent: #66d9c7;
      --accent-2: #f0b35a;
      --danger: #f87171;
      --soft: rgba(102, 217, 199, 0.12);
      --shadow: rgba(0, 0, 0, 0.34);
    }}
    * {{
      box-sizing: border-box;
    }}
    html {{
      overflow-x: hidden;
    }}
    body {{
      margin: 0;
      min-width: 0;
      font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 8%, rgba(102, 217, 199, 0.18), transparent 26rem),
        radial-gradient(circle at 86% 0%, rgba(240, 179, 90, 0.10), transparent 24rem),
        linear-gradient(180deg, #0e171b 0%, var(--bg) 100%);
    }}
    .shell {{
      width: min(100%, 1480px);
      margin: 0 auto;
      padding: 18px clamp(14px, 2vw, 28px) 36px;
    }}
    .context-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      justify-content: space-between;
      align-items: center;
      border: 1px solid var(--border);
      background: rgba(18, 29, 35, 0.86);
      border-radius: 18px;
      padding: 12px 14px;
      margin-bottom: 16px;
      box-shadow: 0 16px 44px var(--shadow);
    }}
    .brand {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: baseline;
      min-width: 0;
    }}
    .brand-mark {{
      color: var(--accent);
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 0.83rem;
    }}
    .context-pill-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .context-pill {{
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.04);
      border-radius: 999px;
      color: var(--muted);
      font-size: 0.82rem;
      padding: 5px 10px;
      white-space: nowrap;
    }}
    .cockpit-grid {{
      display: grid;
      grid-template-columns: 160px minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }}
    .mode-rail {{
      position: sticky;
      top: 18px;
      display: grid;
      gap: 8px;
      border: 1px solid var(--border);
      background: rgba(18, 29, 35, 0.82);
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 16px 44px var(--shadow);
    }}
    .mode-rail a {{
      display: block;
      border: 1px solid transparent;
      border-radius: 12px;
      color: var(--text);
      font-weight: 750;
      padding: 9px 10px;
      text-decoration: none;
    }}
    .mode-rail a:hover,
    .mode-rail a:focus {{
      border-color: var(--border-strong);
      background: var(--soft);
      color: var(--accent);
    }}
    .mode-rail span {{
      display: block;
      color: var(--quiet);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.10em;
      margin: 4px 8px;
      text-transform: uppercase;
    }}
    .main-field {{
      min-width: 0;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, 380px);
      gap: 16px;
      align-items: end;
      margin-bottom: 16px;
      border: 1px solid var(--border);
      background:
        linear-gradient(135deg, rgba(102, 217, 199, 0.11), rgba(240, 179, 90, 0.04)),
        var(--panel);
      border-radius: 22px;
      padding: clamp(16px, 2vw, 24px);
      box-shadow: 0 18px 52px var(--shadow);
    }}
    h1, h2, h3 {{
      margin: 0;
      line-height: 1.15;
    }}
    h1 {{
      font-size: clamp(1.55rem, 3vw, 2.7rem);
      letter-spacing: -0.03em;
    }}
    h2 {{
      font-size: clamp(1.05rem, 1.8vw, 1.32rem);
    }}
    h3 {{
      font-size: 1rem;
    }}
    .subtitle {{
      margin-top: 8px;
      color: var(--muted);
      max-width: 72ch;
    }}
    .banner {{
      border: 1px solid var(--border);
      background: linear-gradient(90deg, rgba(102, 217, 199, 0.14), rgba(240, 179, 90, 0.08));
      border-radius: 14px;
      padding: 12px 14px;
      margin: 16px 0 20px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px 18px;
      box-shadow: 0 14px 40px rgba(0, 0, 0, 0.20);
      min-width: 0;
    }}
    .card + .card {{
      margin-top: 16px;
    }}
    .card h2 {{
      margin-bottom: 12px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .evidence-rail {{
      border: 1px solid var(--border);
      border-radius: 16px;
      background: rgba(11, 17, 20, 0.42);
      padding: 12px;
    }}
    .evidence-rail div + div {{
      margin-top: 6px;
    }}
    .kv {{
      display: grid;
      grid-template-columns: 220px 1fr;
      gap: 8px 16px;
      margin-top: 8px;
    }}
    .kv dt {{
      font-weight: 700;
      color: var(--muted);
    }}
    .kv dd {{
      margin: 0;
      overflow-wrap: anywhere;
      min-width: 0;
    }}
    .table-wrap {{
      overflow-x: auto;
      max-width: 100%;
      border-radius: 12px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 640px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-top: 1px solid var(--border);
      vertical-align: top;
      overflow-wrap: anywhere;
    }}
    th {{
      font-size: 0.92rem;
      color: var(--muted);
      font-weight: 700;
    }}
    code {{
      background: rgba(238, 245, 242, 0.08);
      border-radius: 6px;
      padding: 1px 6px;
      color: #c4f4ec;
      overflow-wrap: anywhere;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #060a0d;
      color: #dce8e5;
      padding: 14px;
      border-radius: 12px;
      overflow-x: auto;
      max-width: 100%;
    }}
    .muted {{
      color: var(--muted);
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.05);
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 0.9rem;
      margin-right: 6px;
      margin-bottom: 6px;
    }}
    a {{
      color: var(--accent);
    }}
    .actions {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .action-form {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: var(--panel-2);
    }}
    .action-form label {{
      display: grid;
      gap: 6px;
      font-weight: 600;
      color: var(--muted);
    }}
    .action-form input,
    .action-form textarea {{
      width: 100%;
      box-sizing: border-box;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      background: #0c1418;
      color: var(--text);
    }}
    .action-form button {{
      justify-self: start;
      border: 0;
      border-radius: 999px;
      padding: 10px 16px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      background: var(--accent);
      color: #06100f;
    }}
    .reject-form button {{
      background: var(--danger);
      color: #220607;
    }}
    .action-form select {{
      width: 100%;
      box-sizing: border-box;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      background: #0c1418;
      color: var(--text);
    }}
    .workspace-shell {{
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.95fr);
      gap: 16px;
      align-items: start;
    }}
    .workspace-main,
    .workspace-side {{
      display: grid;
      gap: 16px;
      min-width: 0;
    }}
    .workspace-header {{
      display: grid;
      gap: 12px;
    }}
    .workspace-header p {{
      margin: 0;
    }}
    .status-row,
    .quick-links,
    .stepper,
    .inline-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 0.84rem;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.04);
    }}
    .status-badge-primary {{
      border-color: rgba(102, 217, 199, 0.36);
      color: var(--accent);
      background: rgba(102, 217, 199, 0.09);
    }}
    .status-badge-warning {{
      border-color: rgba(240, 179, 90, 0.32);
      color: var(--accent-2);
      background: rgba(240, 179, 90, 0.08);
    }}
    .status-badge-danger {{
      border-color: rgba(248, 113, 113, 0.34);
      color: #ffc1c1;
      background: rgba(248, 113, 113, 0.08);
    }}
    .step {{
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 6px 10px;
      color: var(--quiet);
      background: rgba(255, 255, 255, 0.03);
      font-size: 0.86rem;
    }}
    .step-active {{
      border-color: rgba(102, 217, 199, 0.36);
      color: var(--accent);
      background: rgba(102, 217, 199, 0.10);
    }}
    .step-complete {{
      border-color: rgba(102, 217, 199, 0.2);
      color: var(--text);
    }}
    .action-queue {{
      display: grid;
      gap: 10px;
      padding-left: 18px;
      margin: 0;
    }}
    .action-queue li {{
      color: var(--muted);
    }}
    .inline-note {{
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .form-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .action-form h3 {{
      margin-bottom: 4px;
    }}
    .action-form p {{
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .receipt-card {{
      border: 1px solid rgba(102, 217, 199, 0.28);
      background: rgba(102, 217, 199, 0.08);
    }}
    .error-card {{
      border: 1px solid rgba(248, 113, 113, 0.28);
      background: rgba(248, 113, 113, 0.08);
    }}
    .helper-box {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.03);
    }}
    .helper-box + .helper-box {{
      margin-top: 10px;
    }}
    .toggle-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .toggle-row input[type='checkbox'] {{
      width: 16px;
      height: 16px;
      margin: 0;
    }}
    .form-actions {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
    }}
    .footer {{
      margin-top: 26px;
      color: var(--muted);
      font-size: 0.93rem;
    }}
    @media (max-width: 760px) {{
      .shell {{
        padding: 12px 10px 28px;
      }}
      .context-bar,
      .hero,
      .card {{
        border-radius: 16px;
      }}
      .cockpit-grid {{
        display: block;
      }}
      .mode-rail {{
        position: static;
        display: flex;
        flex-wrap: nowrap;
        gap: 6px;
        margin-bottom: 12px;
        overflow-x: auto;
        padding: 8px;
      }}
      .mode-rail span {{
        display: none;
      }}
      .mode-rail a {{
        flex: 0 0 auto;
        padding: 8px 10px;
      }}
      .hero {{
        grid-template-columns: 1fr;
      }}
      .context-pill-row {{
        justify-content: flex-start;
      }}
      .kv {{
        grid-template-columns: 1fr;
        gap: 4px;
      }}
      .kv dt {{
        margin-top: 8px;
      }}
      table {{
        min-width: 560px;
      }}
      .actions {{
        grid-template-columns: 1fr;
      }}
      .workspace-shell {{
        grid-template-columns: 1fr;
      }}
      .form-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="context-bar" aria-label="Global cockpit context">
      <div class="brand">
        <span class="brand-mark">Nexus</span>
        <span>Institutional Cockpit</span>
      </div>
      <div class="context-pill-row">
        <span class="context-pill">DB authority</span>
        <span class="context-pill">Tree derived</span>
        <span class="context-pill">Governed actions</span>
      </div>
    </div>
    <div class="cockpit-grid">
      <nav class="mode-rail" aria-label="Cockpit modes">
        <span>Modes</span>
        <a href="/surface">Overview</a>
        <a href="/surface/operate">OPERATE</a>
        <a href="/surface/graph">MAP</a>
        <a href="/surface/events/timeline">FLOW</a>
        <a href="/surface/domains">INSPECT</a>
        <a href="/surface/proposals">AUDIT</a>
        <span>Queues</span>
        <a href="/surface/decisions">Decisions</a>
        <a href="/surface/reentry/parse-diff">Reentry</a>
      </nav>
      <main class="main-field">
        <section class="hero">
          <div>
        <h1>{escape(title)}</h1>
        <p class="subtitle">Minimal operational surface derived from the live SQLite runtime. It is review-capable and exposes controlled proposal-from-edit paths for entity short_description and relation validation_status edits on published snapshots.</p>
          </div>
          <div class="meta evidence-rail">
        <div><strong>Surface</strong>: Review-capable</div>
        <div><strong>Governance</strong>: approve/reject gated via runtime service</div>
        <div><strong>Proposal-from-edit</strong>: entity short_description + relation validation_status</div>
          </div>
        </section>
    {note_html}
    {sections_html}
    <div class="footer">
      Review actions on this surface call the live governance service. Proposal-from-edit is limited to entity short_description and relation validation_status edits on published snapshots. Broader reentry and MCP access are available through their structured API/adapter paths.
    </div>
      </main>
    </div>
  </div>
</body>
</html>"""


def _render_card(title: str, content: str) -> str:
    return f"<section class='card'><h2>{escape(title)}</h2>{content}</section>"


def _render_kv(items: list[tuple[str, Any]]) -> str:
    parts = ["<dl class='kv'>"]
    for label, value in items:
        parts.append(f"<dt>{escape(label)}</dt><dd>{_format_value(value)}</dd>")
    parts.append("</dl>")
    return "".join(parts)


def _render_table(headers: list[str], rows: list[list[str]], empty_message: str) -> str:
    if not rows:
        return f"<p class='muted'>{escape(empty_message)}</p>"
    head_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<div class='table-wrap'><table><thead><tr>{head_html}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"


def _format_value(value: Any) -> str:
    if value is None:
        return "<span class='muted'>—</span>"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return escape(str(value))
    if isinstance(value, (list, tuple, set)):
        if not value:
            return "<span class='muted'>[]</span>"
        return "".join(f"<span class='pill'><code>{escape(str(item))}</code></span>" for item in value)
    if isinstance(value, dict):
        dumped = yaml.safe_dump(value, sort_keys=False, allow_unicode=True).rstrip("\n")
        return f"<pre>{escape(dumped)}</pre>"
    return escape(str(value))


def _split_csv(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def _parse_json_mapping(value: str | None, *, field_name: str) -> dict[str, Any]:
    if not value or not value.strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return parsed


def _link(href: str, label: str) -> str:
    return f"<a href='{escape(href)}'>{escape(label)}</a>"


def _object_record(runtime: RuntimeContext, object_type: str, object_id: str) -> dict[str, Any] | None:
    if object_type == "domain":
        return runtime.domain_service.get_domain_by_id(object_id)
    if object_type == "entity":
        return runtime.entity_service.get_entity_by_id(object_id)
    if object_type == "relation":
        return runtime.relation_service.get_relation_by_id(object_id)
    if object_type == "source":
        return runtime.source_service.get_source_by_id(object_id)
    if object_type == "payload":
        return runtime.payload_service.get_payload_by_id(object_id)
    if object_type == "projection":
        return runtime.projection_service.get_projection_by_id(object_id)
    if object_type == "event":
        return runtime.event_service.get_event_by_id(object_id)
    if object_type == "proposal":
        return runtime.governance_service.get_proposal_by_id(object_id)
    if object_type == "decision":
        bundle = runtime.governance_service.get_decision_by_id(object_id)
        return bundle["decision"] if bundle is not None else None
    if object_type == "rule":
        return runtime.governance_rule_service.get_rule_by_id(object_id)
    return None


def _render_record_table(record: dict[str, Any] | None) -> str:
    rows = []
    if record is not None:
        rows = [[escape(key), _format_value(value)] for key, value in record.items()]
    return _render_table(["Field", "Value"], rows, "No live record is currently persisted for this identifier.")


def _domain_id_for_review(proposal: dict[str, Any], current_object: dict[str, Any] | None) -> str | None:
    target_type = proposal.get("target_object_type")
    if current_object is not None:
        if target_type == "entity":
            return current_object.get("domain_id")
        if target_type == "relation":
            return current_object.get("domain_context")
        if target_type == "domain":
            return current_object.get("domain_id")
    if target_type == "relation":
        proposed_changes = proposal.get("proposed_changes") or {}
        return proposed_changes.get("domain_context")
    return None


def _build_review_context(runtime: RuntimeContext, proposal_id: str) -> dict[str, Any]:
    proposal = runtime.governance_service.get_proposal_by_id(proposal_id)
    if proposal is None:
        raise _not_found("proposal", proposal_id)

    bundle = runtime.governance_service.get_decision_by_id(proposal["decision_id"])
    if bundle is None:
        raise _not_found("decision", proposal.get("decision_id") or proposal_id)

    decision = bundle["decision"]
    history = runtime.governance_service.get_object_history(
        proposal["target_object_type"],
        proposal["target_object_id"],
    )
    current_object = history.get("current_object")
    domain_id = _domain_id_for_review(proposal, current_object)
    publication_href = f"/agent/publications/tree/domains/{domain_id}/governance" if domain_id else None
    object_history_href = f"/surface/objects/{proposal['target_object_type']}/{proposal['target_object_id']}/history"

    return {
        "proposal": proposal,
        "decision": decision,
        "history": history,
        "current_object": current_object,
        "domain_id": domain_id,
        "publication_href": publication_href,
        "object_history_href": object_history_href,
    }


def _tree_root(request: Request) -> Path:
    tree_root = getattr(request.app.state, "tree_root", None)
    if tree_root is None:
        return Path("tree")
    return Path(tree_root)


def _entity_snapshot_path(request: Request, domain_id: str, entity_id: str) -> Path:
    return _tree_root(request) / "domains" / domain_id / "entities" / f"{entity_id}.md"


def _relation_snapshot_path(request: Request, domain_id: str, relation_id: str) -> Path:
    return _tree_root(request) / "domains" / domain_id / "relations" / f"{relation_id}.md"


def _controlled_reentry_rule(object_type: str) -> dict[str, Any] | None:
    return _CONTROLLED_REENTRY_EDITABILITY.get(object_type)


def _build_controlled_reentry_context(
    runtime: RuntimeContext,
    request: Request,
    object_type: str,
    object_id: str,
) -> dict[str, Any]:
    rule = _controlled_reentry_rule(object_type)
    if rule is None:
        raise HTTPException(
            status_code=404,
            detail=f"object type '{object_type}' is not eligible for proposal-from-edit",
        )

    history = runtime.governance_service.get_object_history(object_type, object_id)
    current_object = history.get("current_object")
    if current_object is None:
        raise _not_found(object_type, object_id)

    if object_type == "entity":
        domain_id = current_object.get("domain_id")
    elif object_type == "relation":
        domain_id = current_object.get("domain_context")
    else:
        domain_id = None
    if not domain_id:
        raise HTTPException(
            status_code=409,
            detail=f"{object_type.title()} '{object_id}' is not eligible for proposal-from-edit because it is not domain-scoped",
        )

    if object_type == "entity":
        artifact_path = _entity_snapshot_path(request, domain_id, object_id)
    else:
        artifact_path = _relation_snapshot_path(request, domain_id, object_id)
    if not artifact_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Published artifact '{artifact_path.as_posix()}' is not available for proposal-from-edit",
        )

    return {
        "object_type": object_type,
        "rule": rule,
        "history": history,
        "current_object": current_object,
        "domain_id": domain_id,
        "artifact_path": artifact_path,
        "history_href": f"/surface/objects/{object_type}/{object_id}/history",
        "edit_href": f"/surface/objects/{object_type}/{object_id}/proposal-from-edit",
    }


def _render_controlled_reentry_contract_card() -> str:
    rows = []
    for object_type, rule in _CONTROLLED_REENTRY_EDITABILITY.items():
        allowed_values = rule.get("allowed_values")
        allowed_values_text = ", ".join(allowed_values) if allowed_values else "free text"
        rows.append(
            [
                escape(object_type),
                escape(rule["editable_field"]),
                escape(rule["proposal_type"]),
                escape(rule["summary_label"]),
                escape(allowed_values_text),
            ]
        )
    return _render_card(
        "Controlled Reentry Contract",
        _render_table(
            ["Object Type", "Editable Field", "Proposal Type", "Snapshot Zone", "Allowed Values"],
            rows,
            "No editable snapshot zones are currently declared.",
        ),
    )


def _render_controlled_reentry_form(context: dict[str, Any]) -> str:
    current_object = context["current_object"]
    rule = context["rule"]
    artifact_path = context["artifact_path"].as_posix()
    editable_field = rule["editable_field"]
    current_value = current_object.get(editable_field) or ""
    input_kind = rule.get("input_kind") or "text"
    allowed_values = rule.get("allowed_values")
    allowed_values_html = ""
    if allowed_values:
        allowed_values_html = (
            "<div class='muted'>Allowed values: "
            + ", ".join(f"<code>{escape(value)}</code>" for value in allowed_values)
            + "</div>"
        )
    return f"""
<div class='actions'>
  <form class='action-form' method='post' action='{escape(context["edit_href"])}'>
    <h3>Propose Snapshot Edit</h3>
    <p class='muted'>{escape(rule["sprint_note"])}</p>
    <label>
      Proposed By
      <input type='text' name='proposed_by' value='human' />
    </label>
    <label>
      {escape(rule["form_label"])}
      {"<textarea name='edited_value' rows='6'>" + escape(str(current_value)) + "</textarea>" if input_kind == "textarea" else "<input type='text' name='edited_value' value='" + escape(str(current_value)) + "' />"}
    </label>
    {allowed_values_html}
    <label>
      Rationale
      <textarea name='rationale' rows='4' placeholder='Optional edit rationale'></textarea>
    </label>
    <button type='submit'>Create proposal</button>
  </form>
</div>
<p class='muted'>Published artifact: <code>{escape(artifact_path)}</code>. This action captures a proposal only; it does not mutate the live {escape(context["object_type"])}.</p>
"""


def _render_controlled_reentry_page(
    context: dict[str, Any],
    *,
    note: str | None = None,
) -> str:
    current_object = context["current_object"]
    history = context["history"]
    artifact_path = context["artifact_path"].as_posix()
    rule = context["rule"]
    object_type = context["object_type"]
    object_id_key = f"{object_type}_id"
    object_id = current_object[object_id_key]
    current_rows = [[escape(key), _format_value(value)] for key, value in current_object.items()]
    allowed_values = rule.get("allowed_values")
    contract_items = [
        ("Object Type", object_type),
        ("Editable Field", rule["editable_field"]),
        ("Proposal Type", rule["proposal_type"]),
        ("Read-Only Scope", rule["read_only_note"]),
        ("Published Artifact", artifact_path),
        ("Object History", context["history_href"]),
    ]
    if allowed_values:
        contract_items.append(("Allowed Values", allowed_values))
    sections = [
        _render_card(
            "Published Snapshot Source",
            _render_kv(
                [
                    (f"{object_type.title()} ID", object_id),
                    ("Domain ID", context["domain_id"]),
                    ("Source Artifact", artifact_path),
                    ("Current Version", current_object.get("version")),
                    (rule["current_label"], current_object.get(rule["editable_field"])),
                    ("Object History", context["history_href"]),
                ]
            ),
        ),
        _render_card("Eligibility Contract", _render_kv(contract_items)),
        _render_card(
            "Current Object",
            _render_table(
                ["Field", "Value"],
                current_rows,
                "No live object is currently persisted for this identifier.",
            ),
        ),
        _render_card("Proposal Form", _render_controlled_reentry_form(context)),
        _render_card("Version Trail", _render_version_table(history.get("versions", []))),
    ]
    title = f"Proposal From Edit: {object_id}"
    return _render_page(
        title,
        sections=sections,
        note=note or f"Controlled proposal-from-edit path. Only {object_type} {rule['editable_field']} edits are eligible.",
    )


def _submit_controlled_reentry_proposal(
    *,
    runtime: RuntimeContext,
    request: Request,
    object_type: str,
    object_id: str,
    edited_value: str,
    proposed_by: str,
    rationale: str | None,
) -> str:
    context = _build_controlled_reentry_context(runtime, request, object_type, object_id)
    rule = context["rule"]
    current_object = context["current_object"]
    editable_field = rule["editable_field"]
    new_value = edited_value.strip()
    current_value = str(current_object.get(editable_field) or "").strip()
    if not new_value:
        raise HTTPException(status_code=400, detail=f"Edited {editable_field} is required")
    allowed_values = rule.get("allowed_values")
    if allowed_values and new_value not in allowed_values:
        raise HTTPException(
            status_code=400,
            detail=f"Edited {editable_field} must be one of: {', '.join(allowed_values)}",
        )
    if new_value == current_value:
        raise HTTPException(status_code=409, detail="No change was submitted")

    artifact_path = context["artifact_path"].as_posix()
    review_rationale = rationale or (
        f"Published {object_type} {editable_field} changed from {current_value!r} to {new_value!r}."
    )
    evidence_refs = [
        f"artifact:{artifact_path}",
        "origin:human_surface_controlled_reentry",
        f"target:{object_type}:{object_id}",
        f"field:{editable_field}",
        f"source-value:{current_value}",
        f"edited-value:{new_value}",
        f"source-version:{current_object.get('version')}",
        f"history:{context['history_href']}",
    ]
    create_proposal = getattr(runtime.governance_service, f"create_{object_type}_update_proposal")
    proposal_bundle = create_proposal(
        object_id,
        {editable_field: new_value},
        proposed_by=proposed_by,
        rationale=review_rationale,
        evidence_refs=evidence_refs,
    )
    note = (
        f"Proposal created from published snapshot {artifact_path}. "
        f"The live {object_type} remains unchanged until governance approves it."
    )
    return _render_proposal_review_page(runtime, proposal_bundle["proposal"]["proposal_id"], note=note)


def _render_entity_proposal_from_edit_form(context: dict[str, Any]) -> str:
    return _render_controlled_reentry_form(context)


def _render_entity_proposal_from_edit_page(
    context: dict[str, Any],
    *,
    note: str | None = None,
) -> str:
    return _render_controlled_reentry_page(context, note=note)


def _render_relation_proposal_from_edit_form(context: dict[str, Any]) -> str:
    return _render_controlled_reentry_form(context)


def _render_relation_proposal_from_edit_page(
    context: dict[str, Any],
    *,
    note: str | None = None,
) -> str:
    return _render_controlled_reentry_page(context, note=note)


def _render_review_actions(decision_id: str, decision_state: str) -> str:
    if decision_state != "pending":
        return "<p class='muted'>This decision is closed. Review actions are disabled.</p>"
    return f"""
<div class='actions'>
  <form class='action-form approve-form' method='post' action='/surface/decisions/{escape(decision_id)}/approve'>
    <h3>Approve</h3>
    <label>
      Decided By
      <input type='text' name='decided_by' value='human' />
    </label>
    <label>
      Rationale
      <textarea name='rationale' rows='4' placeholder='Optional review rationale'></textarea>
    </label>
    <button type='submit'>Approve proposal</button>
  </form>
  <form class='action-form reject-form' method='post' action='/surface/decisions/{escape(decision_id)}/reject'>
    <h3>Reject</h3>
    <label>
      Decided By
      <input type='text' name='decided_by' value='human' />
    </label>
    <label>
      Rationale
      <textarea name='rationale' rows='4' placeholder='Optional rejection rationale'></textarea>
    </label>
    <button type='submit'>Reject proposal</button>
  </form>
</div>
<p class='muted'>These actions call the existing governance service. They do not mutate the core through a second path.</p>
"""


def _render_version_table(versions: list[dict[str, Any]]) -> str:
    version_rows = [
        [
            escape(str(version.get("version_number"))),
            escape(version.get("version_id") or "—"),
            escape(version.get("serialized_state_ref") or "—"),
            escape(version.get("created_by") or "—"),
            escape(version.get("created_at") or "—"),
        ]
        for version in versions
    ]
    return _render_table(
        ["Version", "Version ID", "Serialized State Ref", "Created By", "Created At"],
        version_rows,
        "No approved object versions are recorded yet.",
    )


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(runtime: RuntimeContext = Depends(get_runtime)) -> str:
    domains = runtime.domain_service.list_domains()
    proposals = runtime.governance_service.list_proposals()
    decisions = runtime.governance_service.list_decisions(decision_state=None)
    pending_proposals = [proposal for proposal in proposals if proposal["proposal_state"] == "pending"]
    entity_count = len(runtime.entity_service.list_entities())
    relation_count = len(runtime.relation_service.list_relations())
    event_count = len(runtime.event_service.list_events())
    decision_counts = Counter(bundle["decision"]["decision_state"] for bundle in decisions)
    proposal_counts = Counter(item["proposal_state"] for item in proposals)

    domain_rows = [
        [
            _link(f"/surface/domains/{domain['domain_id']}", domain["domain_id"]),
            escape(domain.get("name") or domain["domain_id"]),
            escape(str(domain.get("status", "unknown"))),
            escape(str(domain.get("version", "unknown"))),
        ]
        for domain in domains
    ]
    proposal_rows = [
        [
            _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"]),
            escape(proposal["proposal_type"]),
            escape(proposal["target_object_type"]),
            escape(proposal["target_object_id"]),
            escape(proposal["proposal_state"]),
            escape(proposal.get("decision_id") or "—"),
        ]
        for proposal in pending_proposals[:8]
    ]
    decision_rows = [
        [
            _link(f"/surface/decisions/{decision['decision_id']}", decision["decision_id"]),
            escape(decision["decision_type"]),
            escape(decision["decision_state"]),
            escape(", ".join(decision.get("target_refs", []))),
            escape(decision.get("decided_by") or "—"),
        ]
        for decision in [bundle["decision"] for bundle in decisions[:8]]
    ]

    sections = [
        _render_card(
            "Live Runtime Snapshot",
            _render_kv(
                [
                    ("Domains", len(domains)),
                    ("Entities", entity_count),
                    ("Relations", relation_count),
                    ("Events", event_count),
                    ("Proposals", len(proposals)),
                    ("Pending decisions", decision_counts.get("pending", 0)),
                ]
            ),
        ),
        _render_card(
            "How This Surface Behaves",
            "<p>This page and the linked detail pages are review-capable. They reuse the live SQLite-backed runtime for inspection and call the existing governance service for approve/reject.</p>"
            "<p>Controlled proposal-from-edit paths exist for entity short_description and relation validation_status edits on published snapshots. Broader reentry and MCP access are handled through structured API/adapter paths, not arbitrary cockpit mutation.</p>",
        ),
        _render_controlled_reentry_contract_card(),
        _render_card(
            "Limits",
            "<p>Everything outside the explicitly declared editability contract remains read-only on this surface.</p>",
        ),
        _render_card(
            "Domains",
            _render_table(
                ["Domain ID", "Name", "Status", "Version"],
                domain_rows,
                "No domains are currently persisted in the executable core.",
            ),
        ),
        _render_card(
            "Pending Proposals",
            _render_table(
                ["Proposal ID", "Type", "Target Type", "Target ID", "State", "Decision ID"],
                proposal_rows,
                "No proposals are currently pending human review.",
            ),
        ),
        _render_card(
            "Decisions",
            _render_table(
                ["Decision ID", "Type", "State", "Targets", "Decided By"],
                decision_rows,
                "No decisions are currently recorded.",
            ),
        ),
    ]
    state_note = (
        f"<strong>Proposal states:</strong> pending {proposal_counts.get('pending', 0)}, "
        f"approved {proposal_counts.get('approved', 0)}, rejected {proposal_counts.get('rejected', 0)}."
    )
    return _render_page("Nexus Operational Surface", sections=sections, note=state_note)


def _escape_attr(value: Any) -> str:
    return escape("" if value is None else str(value), quote=True)


def _checked_attr(value: bool) -> str:
    return " checked" if value else ""


def _parse_checkbox(value: str | None) -> bool:
    return value is not None and value.lower() in {"on", "true", "1", "yes"}


def _form_value(form_state: dict[str, Any] | None, field_name: str, default: Any = "") -> str:
    if form_state is not None:
        data = form_state.get("data") or {}
        if field_name in data and data[field_name] is not None:
            return str(data[field_name])
    return "" if default is None else str(default)


def _context_query_params(workspace_context: dict[str, Any]) -> dict[str, str]:
    params: dict[str, str] = {}
    if workspace_context.get("domain_id"):
        params["domain_id"] = str(workspace_context["domain_id"])
    if workspace_context.get("active_domain_version_id"):
        params["active_domain_version_id"] = str(workspace_context["active_domain_version_id"])
    last_object = workspace_context.get("last_object") or {}
    if last_object.get("type"):
        params["last_object_type"] = str(last_object["type"])
    if last_object.get("id"):
        params["last_object_id"] = str(last_object["id"])
    return params


def _render_hidden_operate_context(workspace_context: dict[str, Any]) -> str:
    params = _context_query_params(workspace_context)
    return "".join(
        f"<input type='hidden' name='_context_{escape(key)}' value='{_escape_attr(value)}' />"
        for key, value in params.items()
    )


def _build_receipt(title: str, result: dict[str, Any], links: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    return {
        "title": title,
        "result": result,
        "links": links or [],
    }


def _render_link_list(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<p class='muted'>No follow-up links.</p>"
    parts = ["<ul class='action-queue'>"]
    for label, href in items:
        parts.append(f"<li>{_link(href, label)}</li>")
    parts.append("</ul>")
    return "".join(parts)


def _build_action_error(title: str, exc: Exception) -> dict[str, Any]:
    detail = str(exc)
    expected_field = None
    if "Missing required fields for" in detail and ":" in detail:
        expected_field = detail.rsplit(":", 1)[-1].strip()
    return {
        "title": title,
        "error_type": type(exc).__name__,
        "detail": detail,
        "expected_field": expected_field,
    }


def _status_badge(status: str) -> str:
    klass = "status-badge"
    if status == "materialized":
        klass += " status-badge-primary"
    elif status == "out_of_sync":
        klass += " status-badge-warning"
    elif status == "not_materialized":
        klass += " status-badge-danger"
    return f"<span class='{klass}'>{escape(status)}</span>"


def _build_required_fields_text(required_fields: dict[str, Any] | None) -> str:
    if not isinstance(required_fields, dict):
        return ""
    lines: list[str] = []
    for entity_type, fields in required_fields.items():
        if not isinstance(fields, list):
            continue
        normalized_fields = [str(field).strip() for field in fields if str(field).strip()]
        lines.append(f"{entity_type}: {', '.join(normalized_fields)}")
    return "\n".join(lines)


def _parse_required_fields_text(text: str | None) -> dict[str, list[str]]:
    if not text:
        return {}
    result: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError("Required fields must use the format 'entity_type: field_a, field_b'")
        entity_type, raw_fields = line.split(":", 1)
        key = entity_type.strip()
        if not key:
            raise ValueError("Required fields must declare an entity type before ':'")
        result[key] = [field.strip() for field in raw_fields.split(",") if field.strip()]
    return result


def _extract_charter_purpose(charter: dict[str, Any]) -> str:
    if not isinstance(charter, dict):
        return ""
    purpose = charter.get("purpose")
    return "" if purpose is None else str(purpose)


def _map_form_action_to_drawer(form_state: dict[str, Any] | None, workspace_context: dict[str, Any], error: dict[str, Any] | None) -> str:
    if workspace_context.get("domain_id") is None:
        return "domain"
    action = (form_state or {}).get("action") or ""
    action_map = {
        "domains": "domain",
        "domain_versions": "domain",
        "activate_domain_version": "domain",
        "entities": "entity",
        "relations": "relation",
        "sources": "source",
        "ingestion_runs": "source",
        "validate_object": "review",
        "reject_object": "review",
        "materialize": "review",
    }
    if action in action_map:
        return action_map[action]
    if error is not None:
        return "review"
    if workspace_context["counts"]["pending_review"]:
        return "review"
    if workspace_context.get("active_domain_version_id") is None:
        return "domain"
    if workspace_context["counts"]["entities"] == 0:
        return "entity"
    return "relation"


def _build_focus_options(runtime: RuntimeContext, domain_id: str | None) -> list[dict[str, Any]]:
    entities = runtime.entity_service.list_entities()
    if domain_id is not None:
        entities = [entity for entity in entities if entity.get("domain_id") == domain_id]
    entities.sort(key=lambda item: (str(item.get("label") or "").casefold(), str(item.get("entity_id") or "")))
    return [
        {
            "id": entity["entity_id"],
            "label": entity.get("label") or entity["entity_id"],
            "entity_type": entity.get("entity_type"),
        }
        for entity in entities
    ]


def _graph_filters_from_request(request: Request, domain_id: str | None, *, default_view: str) -> dict[str, Any]:
    depth_value = request.query_params.get("depth") or "2"
    try:
        depth = max(1, min(int(depth_value), 5))
    except ValueError:
        depth = 2
    return {
        "domain": request.query_params.get("domain") or domain_id or "",
        "focus": request.query_params.get("focus") or "",
        "depth": depth,
        "view": request.query_params.get("view") or default_view,
        "cross_domain": request.query_params.get("cross_domain") or "show_all",
    }


def _summarize_receipt_result(result: Any) -> str:
    if result is None:
        return "Completed."
    if isinstance(result, dict):
        keys = sorted(str(key) for key in result.keys())
        return f"Updated: {', '.join(keys)}"
    if isinstance(result, list):
        return f"{len(result)} items"
    return str(result)


def _render_workbench_template(
    request: Request,
    runtime: RuntimeContext,
    *,
    page_mode: str,
    domain_id: str | None = None,
    last_object_type: str | None = None,
    last_object_id: str | None = None,
    last_result: str | None = None,
    receipt: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
    form_state: dict[str, Any] | None = None,
    drawer_open: bool,
) -> Any:
    workspace_context = build_operate_context(
        runtime,
        domain_id,
        tree_root=_tree_root(request),
        last_object_type=last_object_type,
        last_object_id=last_object_id,
        last_result=last_result,
    )
    graph_filters = _graph_filters_from_request(
        request,
        workspace_context.get("domain_id"),
        default_view="domain" if workspace_context.get("domain_id") else "global",
    )
    focus_options = _build_focus_options(runtime, graph_filters["domain"] or None)
    default_action = _map_form_action_to_drawer(form_state, workspace_context, error)
    action_tabs = (
        {"id": "domain", "label": "Domain"},
        {"id": "entity", "label": "Entity"},
        {"id": "relation", "label": "Relation"},
        {"id": "source", "label": "Source"},
        {"id": "review", "label": "Review"},
    )
    receipt_payload = None
    if receipt is not None:
        receipt_payload = {
            "title": receipt.get("title") or "Result",
            "result": _summarize_receipt_result(receipt.get("result")),
            "links": receipt.get("links") or [],
        }
    workbench_payload = {
        "page_mode": page_mode,
        "workspace": workspace_context,
    }
    return TEMPLATES.TemplateResponse(
        request,
        "cockpit_workbench.html",
        {
            "page_title": "Nexus Workbench",
            "page_heading": "Operate Workspace" if page_mode == "operate" else "Nexus Cockpit Graph",
            "page_subtitle": (
                "Unified authoring, inspection, validation, and publication for human operation."
                if page_mode == "operate"
                else "Graph-led inspection with the same action system, inspector, and publication context."
            ),
            "page_mode": page_mode,
            "domains": runtime.domain_service.list_domains(),
            "workspace": workspace_context,
            "graph_filters": graph_filters,
            "focus_options": focus_options,
            "action_tabs": action_tabs,
            "default_action": default_action,
            "drawer_open": drawer_open,
            "receipt": receipt_payload,
            "error": error,
            "form_data": (form_state or {}).get("data") or {},
            "required_fields_text": _build_required_fields_text(workspace_context["charter"].get("required_fields")),
            "charter_purpose": _extract_charter_purpose(workspace_context["charter"].get("charter") or {}),
            "workbench_payload": workbench_payload,
        },
    )


def _render_operate_workspace(
    request: Request,
    runtime: RuntimeContext,
    *,
    domain_id: str | None = None,
    last_object_type: str | None = None,
    last_object_id: str | None = None,
    last_result: str | None = None,
    receipt: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
    form_state: dict[str, Any] | None = None,
    compatibility_note: str | None = None,
) -> str:
    return _render_workbench_template(
        request,
        runtime,
        page_mode="operate",
        domain_id=domain_id,
        last_object_type=last_object_type,
        last_object_id=last_object_id,
        last_result=last_result,
        receipt=receipt,
        error=error,
        form_state=form_state,
        drawer_open=True,
    )

    workspace_context = build_operate_context(
        runtime,
        domain_id,
        tree_root=_tree_root(request),
        last_object_type=last_object_type,
        last_object_id=last_object_id,
        last_result=last_result,
    )
    charter = workspace_context["charter"]
    publication = workspace_context["publication"]
    recent_event = workspace_context.get("recent_event") or {}
    last_object = workspace_context.get("last_object") or {}
    domain_links = "".join(
        f"<a class='pill' href='/surface/operate?domain_id={_escape_attr(item['domain_id'])}'>{escape(item['name'])}</a>"
        for item in workspace_context["available_domains"]
    ) or "<span class='muted'>No domains yet.</span>"
    next_actions = workspace_context["next_actions"]
    next_action_items = "".join(
        f"<li><a href='{_escape_attr(item['href'])}'>{escape(item['label'])}</a></li>" for item in next_actions
    )
    receipt_html = ""
    if receipt is not None:
        receipt_html = _render_card(
            "ResultReceipt",
            (
                f"<div class='receipt-card helper-box'><strong>{escape(receipt['title'])}</strong></div>"
                f"{_render_kv([('Result', receipt.get('result')), ('Last result', workspace_context.get('last_result'))])}"
                f"{_render_link_list(receipt.get('links') or [('Operate', '/surface/operate')])}"
            ),
        )
    error_html = ""
    if error is not None:
        error_items = [
            ("Error Type", error.get("error_type")),
            ("Detail", error.get("detail")),
        ]
        if error.get("expected_field"):
            error_items.append(("Expected Field", error["expected_field"]))
        error_html = _render_card(
            "ActionErrorCard",
            f"<div class='error-card helper-box'><strong>{escape(error['title'])}</strong></div>{_render_kv(error_items)}",
        )
    workflow_steps = []
    step_state = {
        "domain": workspace_context.get("domain_id") is not None,
        "version": workspace_context.get("domain_version_count", 0) > 0,
        "activation": workspace_context.get("active_domain_version_id") is not None,
        "entity_relation": workspace_context["counts"]["entities"] > 0 or workspace_context["counts"]["relations"] > 0,
        "validation": workspace_context["counts"]["pending_review"] == 0 and (workspace_context["counts"]["entities"] > 0 or workspace_context["counts"]["relations"] > 0),
        "materialization": publication["status"] == "materialized",
    }
    for key, label in [
        ("domain", "domain"),
        ("version", "version"),
        ("activation", "activation"),
        ("entity_relation", "entity/relation"),
        ("validation", "validation"),
        ("materialization", "materialization"),
    ]:
        klass = "step"
        if step_state[key]:
            klass += " step-complete"
        if key == "domain" and workspace_context.get("domain_id") is None:
            klass += " step-active"
        if key == "version" and workspace_context.get("domain_id") and workspace_context.get("domain_version_count", 0) == 0:
            klass += " step-active"
        if key == "activation" and workspace_context.get("domain_version_count", 0) > 0 and workspace_context.get("active_domain_version_id") is None:
            klass += " step-active"
        if key == "entity_relation" and workspace_context.get("active_domain_version_id") and workspace_context["counts"]["entities"] == 0:
            klass += " step-active"
        if key == "validation" and workspace_context["counts"]["pending_review"] > 0:
            klass += " step-active"
        if key == "materialization" and publication["status"] in {"not_materialized", "out_of_sync"}:
            klass += " step-active"
        workflow_steps.append(f"<span class='{klass}'>{escape(label)}</span>")
    last_object_label = last_object.get("label") or "No object yet"
    active_domain_version_id = workspace_context.get("active_domain_version_id") or _form_value(form_state, "domain_version_id")
    if not active_domain_version_id and last_object.get("type") == "domain_version":
        active_domain_version_id = last_object.get("id")
    required_fields_json = json.dumps(charter.get("required_fields") or {}, ensure_ascii=True)
    charter_json = json.dumps(charter.get("charter") or {}, ensure_ascii=True)
    script_payload = json.dumps(_context_query_params(workspace_context), ensure_ascii=True)
    operate_html = f"""
<section class='workspace-shell'>
  <div class='workspace-main'>
    <section class='card workspace-header'>
      <div class='status-row'>
        {_status_badge(publication['status'])}
        <span class='status-badge'>domain {escape(workspace_context.get('domain_id') or 'not_selected')}</span>
        <span class='status-badge'>version {escape(workspace_context.get('active_domain_version_label') or 'inactive')}</span>
        <span class='status-badge'>pending review {escape(str(workspace_context['counts']['pending_review']))}</span>
      </div>
      <div>
        <h2>Operate Workspace</h2>
        <p class='inline-note'>Single-surface local authoring with context persistence, inline governance feedback, and visible publication state.</p>
      </div>
      <div class='quick-links' id='workspace-context'>
        {domain_links}
      </div>
    </section>

    <section class='card'>
      <h2>WorkflowStepper</h2>
      <div class='stepper'>{''.join(workflow_steps)}</div>
    </section>

    <section class='card'>
      <h2>ActionQueue</h2>
      <ol class='action-queue'>{next_action_items}</ol>
    </section>

    {error_html}

    <section class='card' id='create-domain'>
      <h2>ActionCard: Create Domain</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/domains'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Create or select a domain</h3>
          <p>Use this when no domain is active in the workspace context.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' /></label>
          <label>Name <input type='text' name='name' value='{_escape_attr(_form_value(form_state, 'name'))}' required /></label>
          <label>Description <textarea name='description' rows='2' required>{escape(_form_value(form_state, 'description'))}</textarea></label>
          <label>Cognitive Purpose <textarea name='cognitive_purpose' rows='2' required>{escape(_form_value(form_state, 'cognitive_purpose'))}</textarea></label>
          <label>Status <input type='text' name='status' value='{_escape_attr(_form_value(form_state, 'status', 'active'))}' /></label>
          <label>Source Types <input type='text' name='source_types_supported' value='{_escape_attr(_form_value(form_state, 'source_types_supported'))}' placeholder='md,json,txt' /></label>
          <label>Entity Types <input type='text' name='local_entity_types' value='{_escape_attr(_form_value(form_state, 'local_entity_types'))}' placeholder='project,task,decision' /></label>
          <label>Relation Types <input type='text' name='relation_types' value='{_escape_attr(_form_value(form_state, 'relation_types'))}' placeholder='depends_on,evidenced_by' /></label>
          <div class='form-actions'>
            <button type='submit'>Create domain</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>
      </div>
    </section>

    <section class='card' id='domain-version'>
      <h2>ActionCard: Domain Version</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/domain-versions'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Create version</h3>
          <p>Active charter rules appear in the workspace side rail after activation.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' required /></label>
          <label>Version Label <input type='text' name='version_label' value='{_escape_attr(_form_value(form_state, 'version_label', 'day0'))}' required /></label>
          <label>Allowed Entity Types <input type='text' name='allowed_entity_types' value='{_escape_attr(_form_value(form_state, 'allowed_entity_types', ','.join(charter.get('allowed_entity_types') or [])))}' placeholder='project,task' /></label>
          <label>Allowed Relation Types <input type='text' name='allowed_relation_types' value='{_escape_attr(_form_value(form_state, 'allowed_relation_types', ','.join(charter.get('allowed_relation_types') or [])))}' placeholder='depends_on,evidenced_by' /></label>
          <label>Required Fields JSON <textarea name='required_fields_json' rows='3' placeholder='{{"project":["workspace_path"]}}'>{escape(_form_value(form_state, 'required_fields_json', required_fields_json if required_fields_json != '{}' else ''))}</textarea></label>
          <label>Charter JSON <textarea name='charter_json' rows='3' placeholder='{{"purpose":"Day 0 operation"}}'>{escape(_form_value(form_state, 'charter_json', charter_json if charter_json != '{}' else ''))}</textarea></label>
          <div class='form-actions'>
            <button type='submit'>Create version</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>

        <form class='action-form' method='post' action='/surface/actions/domain-versions/activate' id='activate-version'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Activate now</h3>
          <p>Use the latest created domain version or paste another one.</p>
          <label>Domain Version ID <input type='text' name='domain_version_id' value='{_escape_attr(active_domain_version_id)}' required /></label>
          <label>Reason <input type='text' name='reason' value='{_escape_attr(_form_value(form_state, 'reason', 'Activate cockpit charter'))}' /></label>
          <div class='form-actions'>
            <button type='submit'>Activate version</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>
      </div>
    </section>

    <section class='card' id='source-ingestion'>
      <h2>ActionCard: Source and Ingestion</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/sources'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Register source</h3>
          <p>Register raw source metadata and payload through the live service layer.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' required /></label>
          <label>Source Type <input type='text' name='source_type' value='{_escape_attr(_form_value(form_state, 'source_type', 'md'))}' required /></label>
          <label>Source URI <input type='text' name='source_uri' value='{_escape_attr(_form_value(form_state, 'source_uri'))}' /></label>
          <label>Metadata JSON <textarea name='metadata_json' rows='3'>{escape(_form_value(form_state, 'metadata_json'))}</textarea></label>
          <label>Manifest Content <textarea name='content' rows='4'>{escape(_form_value(form_state, 'content'))}</textarea></label>
          <div class='form-actions'>
            <button type='submit'>Register source</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>

        <form class='action-form' method='post' action='/surface/actions/ingestion-runs'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Run ingestion</h3>
          <p>Prefer this for lightweight Day 0 extraction before broader automation.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' required /></label>
          <label>Source Type <input type='text' name='source_type' value='{_escape_attr(_form_value(form_state, 'source_type', 'json'))}' required /></label>
          <label>Content <textarea name='content' rows='5'>{escape(_form_value(form_state, 'content'))}</textarea></label>
          <div class='form-actions'>
            <button type='submit'>Run ingestion</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>
      </div>
    </section>

    <section class='card' id='entity-relation'>
      <h2>ActionCard: Entity and Relation</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/entities'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Create entity</h3>
          <p>Charter-aware authoring. Required fields are shown in the side rail.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' required /></label>
          <label>Entity Type <input type='text' name='entity_type' value='{_escape_attr(_form_value(form_state, 'entity_type'))}' required /></label>
          <label>Label <input type='text' name='label' value='{_escape_attr(_form_value(form_state, 'label'))}' required /></label>
          <label>Short Description <textarea name='short_description' rows='2'>{escape(_form_value(form_state, 'short_description'))}</textarea></label>
          <label>Attributes JSON <textarea name='attributes_json' rows='3'>{escape(_form_value(form_state, 'attributes_json'))}</textarea></label>
          <div class='form-actions'>
            <button type='submit'>Create entity</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>

        <form class='action-form' method='post' action='/surface/actions/relations'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Create relation</h3>
          <p>Relation validation still follows the same governance path.</p>
          <label>Source Entity ID <input type='text' name='source_entity_id' value='{_escape_attr(_form_value(form_state, 'source_entity_id'))}' required /></label>
          <label>Target Entity ID <input type='text' name='target_entity_id' value='{_escape_attr(_form_value(form_state, 'target_entity_id'))}' required /></label>
          <label>Relation Type <input type='text' name='relation_type' value='{_escape_attr(_form_value(form_state, 'relation_type'))}' required /></label>
          <label>Domain Context <input type='text' name='domain_context' value='{_escape_attr(_form_value(form_state, 'domain_context', workspace_context.get('domain_id')))}' /></label>
          <div class='form-actions'>
            <button type='submit'>Create relation</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>
      </div>
    </section>

    <section class='card' id='validate-object'>
      <h2>ActionCard: Validate or Reject</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/objects/validate'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Validate now</h3>
          <p>The last created object is prefilled when possible.</p>
          <label>Object Type <input type='text' name='object_type' value='{_escape_attr(_form_value(form_state, 'object_type', last_object.get('type', 'entity')))}' required /></label>
          <label>Object ID <input type='text' name='object_id' value='{_escape_attr(_form_value(form_state, 'object_id', last_object.get('id')))}' required /></label>
          <label>Reason <input type='text' name='reason' value='{_escape_attr(_form_value(form_state, 'reason', 'Validated in operate workspace'))}' /></label>
          <div class='form-actions'>
            <button type='submit'>Validate object</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>

        <form class='action-form reject-form' method='post' action='/surface/actions/objects/reject'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Reject object</h3>
          <p>Use explicit reasons so the next operator can reenter cleanly.</p>
          <label>Object Type <input type='text' name='object_type' value='{_escape_attr(_form_value(form_state, 'object_type', last_object.get('type', 'entity')))}' required /></label>
          <label>Object ID <input type='text' name='object_id' value='{_escape_attr(_form_value(form_state, 'object_id', last_object.get('id')))}' required /></label>
          <label>Reason <input type='text' name='reason' value='{_escape_attr(_form_value(form_state, 'reason'))}' required /></label>
          <div class='form-actions'>
            <button type='submit'>Reject object</button>
            <label class='toggle-row'><input type='checkbox' name='materialize_after_success'{_checked_attr(_parse_checkbox(_form_value(form_state, 'materialize_after_success')))} /> materialize after success</label>
          </div>
        </form>
      </div>
    </section>

    <section class='card' id='materialize-domain'>
      <h2>MaterializationControl</h2>
      <div class='form-grid'>
        <form class='action-form' method='post' action='/surface/actions/materialize'>
          {_render_hidden_operate_context(workspace_context)}
          <h3>Publish current domain</h3>
          <p>Make charter, sources, runs, and authoring summaries visible in <code>tree/</code>.</p>
          <label>Domain ID <input type='text' name='domain_id' value='{_escape_attr(_form_value(form_state, 'domain_id', workspace_context.get('domain_id')))}' required /></label>
          <button type='submit'>Materialize domain</button>
        </form>
      </div>
    </section>
  </div>

  <aside class='workspace-side'>
    {receipt_html}
    <section class='card'>
      <h2>ContextBar</h2>
      {_render_kv([
        ('Domain', workspace_context.get('domain_id')),
        ('Active Version', workspace_context.get('active_domain_version_label')),
        ('Pending Review', workspace_context['counts']['pending_review']),
        ('Last Result', workspace_context.get('last_result')),
        ('Publication', publication['status']),
      ])}
    </section>
    <section class='card'>
      <h2>Charter</h2>
      {_render_kv([
        ('Domain Version ID', workspace_context.get('active_domain_version_id')),
        ('Allowed Entity Types', charter.get('allowed_entity_types')),
        ('Allowed Relation Types', charter.get('allowed_relation_types')),
        ('Required Fields', charter.get('required_fields')),
      ])}
    </section>
    <section class='card'>
      <h2>EvidenceRail</h2>
      {_render_kv([
        ('Last Object', last_object_label),
        ('Last Event', recent_event.get('event_type')),
        ('Performed By', recent_event.get('performed_by')),
        ('Last Event At', recent_event.get('created_at')),
        ('Tree Path', publication.get('tree_domain_path')),
      ])}
      <div class='helper-box'>
        <div><strong>Inspect</strong>: {_link(f"/surface/domains/{workspace_context['domain_id']}", 'Domain inspector') if workspace_context.get('domain_id') else "<span class='muted'>Select a domain</span>"}</div>
        <div><strong>Flow</strong>: {_link('/surface/events/timeline', 'Timeline')}</div>
        <div><strong>Audit</strong>: {_link('/surface/proposals', 'Proposal queue')}</div>
      </div>
    </section>
  </aside>
</section>
<script>
(() => {{
  const params = {script_payload};
  const next = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {{
    if (value) {{
      next.set(key, value);
    }}
  }});
  const target = "/surface/operate" + (next.toString() ? "?" + next.toString() : "");
  if (window.location.pathname !== "/surface/operate" || window.location.search.slice(1) !== next.toString()) {{
    history.replaceState({{}}, "", target);
  }}
  try {{
    localStorage.setItem("nexus.operate.context", JSON.stringify(params));
  }} catch (error) {{
    console.debug("nexus operate context persistence skipped", error);
  }}
}})();
</script>
"""
    return _render_page(
        "Operate Workspace",
        sections=[operate_html],
        note=compatibility_note or "Local cockpit actions mutate executable state through runtime services, preserve context in the workspace, and make publication state explicit.",
    )


@router.get("/operate", response_class=HTMLResponse)
def get_operate_workspace(
    request: Request,
    domain_id: str | None = None,
    last_object_type: str | None = None,
    last_object_id: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    return _render_operate_workspace(
        request,
        runtime,
        domain_id=domain_id,
        last_object_type=last_object_type,
        last_object_id=last_object_id,
    )


@router.get("/actions", response_class=HTMLResponse)
def get_action_panel(request: Request) -> RedirectResponse:
    target = "/surface/operate"
    if request.query_params:
        target = f"{target}?{request.query_params}"
    return RedirectResponse(url=target, status_code=302)


def _maybe_materialize_domain(
    request: Request,
    runtime: RuntimeContext,
    *,
    domain_id: str | None,
    materialize_after_success: bool,
    reason: str,
) -> tuple[dict[str, Any] | None, list[tuple[str, str]]]:
    if not materialize_after_success or not domain_id:
        return None, []
    publication = materialize_domain_publication(
        runtime,
        tree_root=_tree_root(request),
        domain_id=domain_id,
        generated_by="surface_operate",
        reason=reason,
    )
    return publication, [("Materialization job", publication["job"]["job_id"])]


@router.post("/actions/domains", response_class=HTMLResponse)
def create_domain_from_action_panel(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    cognitive_purpose: str = Form(...),
    domain_id: str | None = Form(None),
    status: str = Form("active"),
    source_types_supported: str | None = Form(None),
    local_entity_types: str | None = Form(None),
    relation_types: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_active_domain_version_id: str | None = Form(None, alias="_context_active_domain_version_id"),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "domains",
        "data": {
            "domain_id": domain_id,
            "name": name,
            "description": description,
            "cognitive_purpose": cognitive_purpose,
            "status": status,
            "source_types_supported": source_types_supported,
            "local_entity_types": local_entity_types,
            "relation_types": relation_types,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        payload = {
            "name": name,
            "description": description,
            "cognitive_purpose": cognitive_purpose,
            "status": status,
            "source_types_supported": _split_csv(source_types_supported),
            "local_entity_types": _split_csv(local_entity_types),
            "relation_types": _split_csv(relation_types),
            "promotion_rules": ["manual_review"],
            "governance_dependencies": ["human_validation"],
        }
        if domain_id:
            payload["domain_id"] = domain_id
        domain = runtime.domain_service.create_domain(payload, performed_by="human", performed_via="human_ui", reason="create domain from cockpit")
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=domain["domain_id"],
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {domain['domain_id']} after cockpit domain creation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain["domain_id"],
            last_object_type="domain",
            last_object_id=domain["domain_id"],
            last_result="Domain Created",
            receipt=_build_receipt(
                "Domain Created",
                {"domain": domain, "materialization": materialization},
                [("Domain inspector", f"/surface/domains/{domain['domain_id']}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Domain Creation Failed",
            error=_build_action_error("Domain Creation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/domain-versions", response_class=HTMLResponse)
def create_domain_version_from_action_panel(
    request: Request,
    domain_id: str = Form(...),
    version_label: str = Form(...),
    allowed_entity_types: str | None = Form(None),
    allowed_relation_types: str | None = Form(None),
    required_fields_text: str | None = Form(None),
    charter_purpose: str | None = Form(None),
    required_fields_json: str | None = Form(None),
    charter_json: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "domain_versions",
        "data": {
            "domain_id": domain_id,
            "version_label": version_label,
            "allowed_entity_types": allowed_entity_types,
            "allowed_relation_types": allowed_relation_types,
            "required_fields_text": required_fields_text,
            "charter_purpose": charter_purpose,
            "required_fields_json": required_fields_json,
            "charter_json": charter_json,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        charter_payload = _parse_json_mapping(charter_json, field_name="charter_json")
        if charter_purpose:
            charter_payload["purpose"] = charter_purpose
        required_fields_payload = (
            _parse_required_fields_text(required_fields_text)
            if required_fields_text
            else _parse_json_mapping(required_fields_json, field_name="required_fields_json")
        )
        version = runtime.domain_version_service.create_domain_version(
            {
                "domain_id": domain_id,
                "version_label": version_label,
                "charter": charter_payload,
                "allowed_entity_types": _split_csv(allowed_entity_types),
                "allowed_relation_types": _split_csv(allowed_relation_types),
                "required_fields": required_fields_payload,
                "promotion_rules": ["manual_review"],
            },
            performed_by="human",
            performed_via="human_ui",
            reason="create domain version from cockpit",
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {domain_id} after cockpit domain version creation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type="domain_version",
            last_object_id=version["domain_version_id"],
            last_result="Domain Version Created",
            receipt=_build_receipt(
                "Domain Version Created",
                {"domain_version": version, "materialization": materialization},
                [("Domain inspector", f"/surface/domains/{domain_id}"), ("Activate now", "#activate-version"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Domain Version Creation Failed",
            error=_build_action_error("Domain Version Creation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/domain-versions/activate", response_class=HTMLResponse)
def activate_domain_version_from_action_panel(
    request: Request,
    domain_version_id: str = Form(...),
    reason: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_domain_id: str | None = Form(None, alias="_context_domain_id"),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "activate_domain_version",
        "data": {
            "domain_version_id": domain_version_id,
            "reason": reason,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        version = runtime.domain_version_service.activate_domain_version(
            domain_version_id,
            performed_by="human",
            performed_via="human_ui",
            reason=reason or "activate domain version from cockpit",
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=version["domain_id"],
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {version['domain_id']} after cockpit domain version activation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=version["domain_id"],
            last_object_type="domain_version",
            last_object_id=version["domain_version_id"],
            last_result="Domain Version Activated",
            receipt=_build_receipt(
                "Domain Version Activated",
                {"domain_version": version, "materialization": materialization},
                [("Domain inspector", f"/surface/domains/{version['domain_id']}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=context_domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Domain Version Activation Failed",
            error=_build_action_error("Domain Version Activation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/sources", response_class=HTMLResponse)
def register_source_from_action_panel(
    request: Request,
    domain_id: str = Form(...),
    source_type: str = Form(...),
    source_uri: str | None = Form(None),
    metadata_json: str | None = Form(None),
    content: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "sources",
        "data": {
            "domain_id": domain_id,
            "source_type": source_type,
            "source_uri": source_uri,
            "metadata_json": metadata_json,
            "content": content,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        manifest = content or json.dumps({"source_uri": source_uri, "metadata": _parse_json_mapping(metadata_json, field_name="metadata_json")}, sort_keys=True)
        result = runtime.source_service.register_source_with_payload(
            {
                "domain_id": domain_id,
                "source_type": source_type,
                "source_origin": "cockpit",
                "source_uri": source_uri,
                "ingestion_status": "pending",
                "metadata": _parse_json_mapping(metadata_json, field_name="metadata_json"),
                "provenance_record": {"registered_via": "cockpit"},
            },
            content=manifest,
            performed_by="human",
            performed_via="human_ui",
            reason="register source from cockpit",
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {domain_id} after cockpit source registration",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type="source",
            last_object_id=result["source"]["source_id"],
            last_result="Source Registered",
            receipt=_build_receipt(
                "Source Registered",
                {"source": result["source"], "materialization": materialization},
                [("Domain inspector", f"/surface/domains/{domain_id}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Source Registration Failed",
            error=_build_action_error("Source Registration Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/ingestion-runs", response_class=HTMLResponse)
def run_ingestion_from_action_panel(
    request: Request,
    domain_id: str = Form(...),
    source_type: str = Form(...),
    content: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "ingestion_runs",
        "data": {
            "domain_id": domain_id,
            "source_type": source_type,
            "content": content,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        result = runtime.ingestion_service.ingest(
            domain_id=domain_id,
            source_type=source_type,
            content=content,
            proposed_by="human",
            metadata={"submitted_via": "cockpit"},
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {domain_id} after cockpit ingestion run",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_result="Ingestion Run Completed",
            receipt=_build_receipt(
                "Ingestion Run Completed",
                {"ingestion": result, "materialization": materialization},
                [("Domain inspector", f"/surface/domains/{domain_id}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Ingestion Run Failed",
            error=_build_action_error("Ingestion Run Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/entities", response_class=HTMLResponse)
def create_entity_from_action_panel(
    request: Request,
    domain_id: str = Form(...),
    entity_type: str = Form(...),
    label: str = Form(...),
    short_description: str | None = Form(None),
    attributes_json: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "entities",
        "data": {
            "domain_id": domain_id,
            "entity_type": entity_type,
            "label": label,
            "short_description": short_description,
            "attributes_json": attributes_json,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        attributes = _parse_json_mapping(attributes_json, field_name="attributes_json")
        runtime.domain_version_service.validate_entity_against_active_charter(domain_id, entity_type, attributes)
        entity = runtime.entity_service.create_entity(
            {
                "domain_id": domain_id,
                "scope": "local",
                "entity_type": entity_type,
                "label": label,
                "short_description": short_description,
                "attributes": attributes,
                "aliases": [],
                "confidence": 1.0,
                "validation_status": "proposed",
                "canonical_candidate_flag": False,
                "provenance_refs": ["cockpit:manual"],
                "payload_refs": [],
            },
            performed_by="human",
            performed_via="human_ui",
            reason="create entity from cockpit",
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {domain_id} after cockpit entity creation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type="entity",
            last_object_id=entity["entity_id"],
            last_result="Entity Created",
            receipt=_build_receipt(
                "Entity Created",
                {"entity": entity, "materialization": materialization},
                [("Entity inspect", f"/surface/objects/entity/{entity['entity_id']}"), ("Validate now", "#validate-object"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Entity Creation Failed",
            error=_build_action_error("Entity Creation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/relations", response_class=HTMLResponse)
def create_relation_from_action_panel(
    request: Request,
    source_entity_id: str = Form(...),
    target_entity_id: str = Form(...),
    relation_type: str = Form(...),
    domain_context: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "relations",
        "data": {
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relation_type": relation_type,
            "domain_context": domain_context,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        source = runtime.entity_service.get_entity_by_id(source_entity_id)
        target = runtime.entity_service.get_entity_by_id(target_entity_id)
        if source is None:
            raise KeyError(source_entity_id)
        if target is None:
            raise KeyError(target_entity_id)
        resolved_domain = domain_context or source.get("domain_id") or target.get("domain_id")
        runtime.domain_version_service.validate_relation_against_active_charter(resolved_domain, relation_type)
        relation = runtime.relation_service.create_relation(
            {
                "source_entity_id": source_entity_id,
                "target_entity_id": target_entity_id,
                "relation_type": relation_type,
                "directionality": "directed",
                "domain_context": resolved_domain,
                "evidence_refs": ["cockpit:manual"],
                "confidence": 1.0,
                "validation_status": "proposed",
                "asserted_by": "human",
            },
            performed_by="human",
            performed_via="human_ui",
            reason="create relation from cockpit",
        )
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=resolved_domain,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {resolved_domain} after cockpit relation creation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=resolved_domain,
            last_object_type="relation",
            last_object_id=relation["relation_id"],
            last_result="Relation Created",
            receipt=_build_receipt(
                "Relation Created",
                {"relation": relation, "materialization": materialization},
                [("Relation inspect", f"/surface/objects/relation/{relation['relation_id']}"), ("Validate now", "#validate-object"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_context,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Relation Creation Failed",
            error=_build_action_error("Relation Creation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/objects/validate", response_class=HTMLResponse)
def validate_object_from_action_panel(
    request: Request,
    object_type: str = Form(...),
    object_id: str = Form(...),
    reason: str | None = Form(None),
    materialize_after_success: str | None = Form(None),
    context_domain_id: str | None = Form(None, alias="_context_domain_id"),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "validate_object",
        "data": {
            "object_type": object_type,
            "object_id": object_id,
            "reason": reason,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        result = runtime.object_validation_service.validate_object(
            object_type,
            object_id,
            performed_by="human",
            performed_via="human_ui",
            reason=reason,
        )
        resolved_domain_id = result.get("domain_id") if object_type == "entity" else result.get("domain_context")
        resolved_domain_id = resolved_domain_id or context_domain_id
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=resolved_domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {resolved_domain_id} after cockpit validation" if resolved_domain_id else "materialize after cockpit validation",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=resolved_domain_id,
            last_object_type=object_type,
            last_object_id=object_id,
            last_result="Object Validated",
            receipt=_build_receipt(
                "Object Validated",
                {"object": result, "materialization": materialization},
                [("Object inspect", f"/surface/objects/{object_type}/{object_id}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=context_domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Object Validation Failed",
            error=_build_action_error("Object Validation Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/objects/reject", response_class=HTMLResponse)
def reject_object_from_action_panel(
    request: Request,
    object_type: str = Form(...),
    object_id: str = Form(...),
    reason: str = Form(...),
    materialize_after_success: str | None = Form(None),
    context_domain_id: str | None = Form(None, alias="_context_domain_id"),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {
        "action": "reject_object",
        "data": {
            "object_type": object_type,
            "object_id": object_id,
            "reason": reason,
            "materialize_after_success": materialize_after_success,
        },
    }
    try:
        result = runtime.object_validation_service.reject_object(
            object_type,
            object_id,
            performed_by="human",
            performed_via="human_ui",
            reason=reason,
        )
        resolved_domain_id = result.get("domain_id") if object_type == "entity" else result.get("domain_context")
        resolved_domain_id = resolved_domain_id or context_domain_id
        materialization, materialization_links = _maybe_materialize_domain(
            request,
            runtime,
            domain_id=resolved_domain_id,
            materialize_after_success=_parse_checkbox(materialize_after_success),
            reason=f"materialize domain {resolved_domain_id} after cockpit rejection" if resolved_domain_id else "materialize after cockpit rejection",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=resolved_domain_id,
            last_object_type=object_type,
            last_object_id=object_id,
            last_result="Object Rejected",
            receipt=_build_receipt(
                "Object Rejected",
                {"object": result, "materialization": materialization},
                [("Object inspect", f"/surface/objects/{object_type}/{object_id}"), *materialization_links],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=context_domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Object Rejection Failed",
            error=_build_action_error("Object Rejection Failed", exc),
            form_state=form_state,
        )


@router.post("/actions/materialize", response_class=HTMLResponse)
def materialize_domain_from_operate(
    request: Request,
    domain_id: str = Form(...),
    context_last_object_type: str | None = Form(None, alias="_context_last_object_type"),
    context_last_object_id: str | None = Form(None, alias="_context_last_object_id"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    form_state = {"action": "materialize", "data": {"domain_id": domain_id}}
    try:
        result = materialize_domain_publication(
            runtime,
            tree_root=_tree_root(request),
            domain_id=domain_id,
            generated_by="surface_operate",
            reason=f"materialize domain {domain_id} from operate workspace",
        )
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Domain Materialized",
            receipt=_build_receipt(
                "Domain Materialized",
                {"status": result["status"], "job": result["job"]},
                [("Domain inspector", f"/surface/domains/{domain_id}")],
            ),
        )
    except Exception as exc:
        return _render_operate_workspace(
            request,
            runtime,
            domain_id=domain_id,
            last_object_type=context_last_object_type,
            last_object_id=context_last_object_id,
            last_result="Domain Materialization Failed",
            error=_build_action_error("Domain Materialization Failed", exc),
            form_state=form_state,
        )


@router.get("/domains", response_class=HTMLResponse)
def list_domains(runtime: RuntimeContext = Depends(get_runtime)) -> str:
    domains = runtime.domain_service.list_domains()
    entity_map = {domain["domain_id"]: [] for domain in domains}
    relation_map = {domain["domain_id"]: [] for domain in domains}
    for entity in runtime.entity_service.list_entities():
        domain_id = entity.get("domain_id")
        if domain_id in entity_map:
            entity_map[domain_id].append(entity)
    for relation in runtime.relation_service.list_relations():
        domain_id = relation.get("domain_context")
        if domain_id in relation_map:
            relation_map[domain_id].append(relation)

    rows = []
    for domain in domains:
        domain_id = domain["domain_id"]
        rows.append(
            [
                _link(f"/surface/domains/{domain_id}", domain_id),
                escape(domain.get("name") or domain_id),
                escape(str(domain.get("status", "unknown"))),
                escape(str(len(entity_map.get(domain_id, [])))),
                escape(str(len(relation_map.get(domain_id, [])))),
            ]
        )
    sections = [
        _render_card(
            "Published Domains",
            _render_table(
                ["Domain ID", "Name", "Status", "Entities", "Relations"],
                rows,
                "No domains are currently persisted in the executable core.",
            ),
        )
    ]
    return _render_page("Nexus Domains", sections=sections)


@router.get("/domains/{domain_id}", response_class=HTMLResponse)
def get_domain(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)

    entities = [entity for entity in runtime.entity_service.list_entities() if entity.get("domain_id") == domain_id]
    relations = [relation for relation in runtime.relation_service.list_relations() if relation.get("domain_context") == domain_id]

    sections = [
        _render_card(
            "Domain Contract",
            _render_kv(
                [
                    ("Domain ID", domain["domain_id"]),
                    ("Name", domain.get("name")),
                    ("Description", domain.get("description")),
                    ("Cognitive Purpose", domain.get("cognitive_purpose")),
                    ("Status", domain.get("status")),
                    ("Source Types Supported", domain.get("source_types_supported", [])),
                    ("Local Entity Types", domain.get("local_entity_types", [])),
                    ("Relation Types", domain.get("relation_types", [])),
                    ("Promotion Rules", domain.get("promotion_rules", [])),
                    ("Governance Dependencies", domain.get("governance_dependencies", [])),
                    ("Version", domain.get("version")),
                    ("Created At", domain.get("created_at")),
                    ("Updated At", domain.get("updated_at")),
                ]
            ),
        ),
        _render_card(
            "Live Objects",
            _render_kv(
                [
                    ("Entity snapshots", len(entities)),
                    ("Relation snapshots", len(relations)),
                    ("Published tree path", f"tree/domains/{domain_id}/"),
                    ("Domain history", f"/surface/objects/domain/{domain_id}/history"),
                    ("Operational projections", f"/surface/domains/{domain_id}/projections"),
                ]
            ),
        ),
    ]

    entity_rows = [
        [
            _link(f"/surface/objects/entity/{entity['entity_id']}/history", entity["label"]),
            escape(entity["entity_id"]),
            escape(str(entity.get("entity_type", "unknown"))),
            escape(str(entity.get("version", "unknown"))),
            escape(str(entity.get("validation_status", "unknown"))),
            _link(f"/surface/objects/entity/{entity['entity_id']}/proposal-from-edit", "Propose edit"),
        ]
        for entity in entities
    ]
    relation_rows = [
        [
            _link(f"/surface/objects/relation/{relation['relation_id']}/history", relation["relation_id"]),
            escape(relation["source_entity_id"]),
            escape(relation["target_entity_id"]),
            escape(str(relation.get("version", "unknown"))),
            escape(str(relation.get("validation_status", "unknown"))),
            _link(f"/surface/objects/relation/{relation['relation_id']}/proposal-from-edit", "Propose edit"),
        ]
        for relation in relations
    ]
    sections.append(
        _render_card(
            "Entity Snapshots",
            _render_table(
                ["Label", "Entity ID", "Type", "Version", "State", "Proposal From Edit"],
                entity_rows,
                "No entity snapshots exist for this domain.",
            ),
        )
    )
    sections.append(
        _render_card(
            "Relation Snapshots",
            _render_table(
                ["Relation ID", "Source", "Target", "Version", "State", "Proposal From Edit"],
                relation_rows,
                "No relation snapshots exist for this domain.",
            ),
        )
    )
    return _render_page(f"Domain Surface: {domain.get('name') or domain_id}", sections=sections)


@router.get("/domains/{domain_id}/projections", response_class=HTMLResponse)
def get_domain_projections(domain_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    domain = runtime.domain_service.get_domain_by_id(domain_id)
    if domain is None:
        raise _not_found("domain", domain_id)

    summary = build_domain_operational_summary(runtime, domain_id)
    queue = build_domain_review_queue(runtime, domain_id)
    active_queue = build_domain_active_decision_queue(runtime, domain_id)
    recent_changes = build_domain_recent_changes(runtime, domain_id)

    summary_items = [
        ("Domain ID", domain["domain_id"]),
        ("Status", domain.get("status")),
        ("Version", domain.get("version")),
        ("Entity snapshots", summary["entity_count"]),
        ("Relation snapshots", summary["relation_count"]),
        ("Pending proposals", summary["pending_proposal_count"]),
        ("Approved decisions", summary["approved_decision_count"]),
        ("Rejected decisions", summary["rejected_decision_count"]),
        ("Tree publication path", f"tree/domains/{domain_id}/projections/"),
        ("Summary artifact", f"tree/domains/{domain_id}/projections/DOMAIN_OPERATIONAL_SUMMARY.md"),
        ("Queue artifact", f"tree/domains/{domain_id}/projections/PENDING_REVIEW_QUEUE.md"),
        ("Active decision artifact", f"tree/domains/{domain_id}/projections/ACTIVE_DECISION_QUEUE.md"),
        ("Recent changes artifact", f"tree/domains/{domain_id}/projections/RECENT_CHANGES.md"),
    ]

    pending_rows = []
    for entry in queue["pending_proposals"][:8]:
        proposal = entry["proposal"]
        decision = entry["decision"] or {}
        target_type = proposal["target_object_type"]
        target_id = proposal["target_object_id"]
        review_href = _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"])
        decision_href = _link(f"/surface/decisions/{decision.get('decision_id', proposal['decision_id'])}", decision.get("decision_id") or proposal["decision_id"])
        history_href = _link(f"/surface/objects/{target_type}/{target_id}/history", f"{target_type}:{target_id}")
        pending_rows.append(
            [
                review_href,
                escape(proposal["proposal_type"]),
                escape(f"{target_type}:{target_id}"),
                escape(proposal.get("proposed_by") or "—"),
                escape(proposal.get("rationale") or "—"),
                decision_href,
                history_href,
            ]
        )

    recent_rows = []
    for entry in summary["recent_decisions"][:8]:
        proposal = entry["proposal"]
        decision = entry["decision"]
        target_type = proposal["target_object_type"]
        target_id = proposal["target_object_id"]
        review_href = _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"])
        decision_href = _link(f"/surface/decisions/{decision['decision_id']}", decision["decision_id"])
        history_href = _link(f"/surface/objects/{target_type}/{target_id}/history", f"{target_type}:{target_id}")
        recent_rows.append(
            [
                decision_href,
                escape(decision.get("decision_state") or "—"),
                escape(proposal["proposal_type"]),
                escape(f"{target_type}:{target_id}"),
                escape(str(entry.get("object_version") or "—")),
                review_href,
                history_href,
            ]
        )

    active_rows = []
    for item in active_queue["active_items"][:8]:
        proposal = item["proposal"]
        decision = item["decision"] or {}
        target_type = proposal["target_object_type"]
        target_id = proposal["target_object_id"]
        proposal_href = _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"])
        decision_href = _link(
            f"/surface/decisions/{decision.get('decision_id') or proposal['decision_id']}",
            decision.get("decision_id") or proposal["decision_id"],
        )
        history_href = _link(f"/surface/objects/{target_type}/{target_id}/history", f"{target_type}:{target_id}")
        snapshot_href = item.get("snapshot_path")
        active_rows.append(
            [
                proposal_href,
                escape(item["kind"].replace("_", " ")),
                escape(item["status"]),
                escape(f"{target_type}:{target_id}"),
                escape(item["next_action"]),
                decision_href,
                history_href,
                _link(snapshot_href, snapshot_href) if snapshot_href else "<span class='muted'>—</span>",
            ]
        )

    change_rows = []
    for entry in recent_changes["recent_changes"][:8]:
        event = entry["event"]
        proposal = entry["proposal"]
        decision = entry["decision"] or {}
        if proposal is not None:
            target_type = proposal["target_object_type"]
            target_id = proposal["target_object_id"]
        else:
            target_type = event["target_object_type"]
            target_id = event["target_object_id"]
        history_href = _link(f"/surface/objects/{target_type}/{target_id}/history", f"{target_type}:{target_id}")
        proposal_href = (
            _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"])
            if proposal is not None
            else "<span class='muted'>—</span>"
        )
        decision_href = (
            _link(f"/surface/decisions/{decision['decision_id']}", decision["decision_id"])
            if decision
            else "<span class='muted'>—</span>"
        )
        snapshot_href = entry.get("snapshot_path")
        change_rows.append(
            [
                escape(event["event_id"]),
                escape(event["event_type"]),
                escape(f"{target_type}:{target_id}"),
                escape(event.get("performed_by") or "—"),
                proposal_href,
                decision_href,
                history_href,
                _link(snapshot_href, snapshot_href) if snapshot_href else "<span class='muted'>—</span>",
            ]
        )

    sections = [
        _render_card("Domain Operational Summary", _render_kv(summary_items)),
        _render_card(
            "Active Decision Queue",
            _render_table(
                ["Item", "Kind", "State", "Target", "Next Action", "Decision", "History", "Snapshot"],
                active_rows,
                "No active decisions or pending proposals are currently queued for review.",
            ),
        ),
        _render_card(
            "Recent Changes",
            _render_table(
                ["Event", "Type", "Target", "Performed By", "Proposal", "Decision", "History", "Snapshot"],
                change_rows,
                "No recent changes are currently published for this domain.",
            ),
        ),
        _render_card(
            "Pending Review Queue",
            _render_table(
                ["Proposal", "Type", "Target", "Proposed By", "Rationale", "Decision", "History"],
                pending_rows,
                "No proposals are currently pending human review.",
            ),
        ),
            _render_card(
                "Recent Decisions",
                _render_table(
                    ["Decision", "State", "Proposal Type", "Target", "Version", "Proposal", "History"],
                    recent_rows,
                "No approved or rejected decisions are currently available for this domain.",
            ),
        ),
    ]
    note = "This view is derived from live runtime state; the treefolder publishes the same projections as Markdown."
    return _render_page(f"Operational Projections: {domain.get('name') or domain_id}", sections=sections, note=note)


@router.get("/proposals", response_class=HTMLResponse)
def list_proposals(runtime: RuntimeContext = Depends(get_runtime)) -> str:
    proposals = runtime.governance_service.list_proposals()
    pending_proposals = [proposal for proposal in proposals if proposal["proposal_state"] == "pending"]
    closed_proposals = [proposal for proposal in proposals if proposal["proposal_state"] != "pending"]
    pending_rows = [
        [
            _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"]),
            escape(proposal["proposal_type"]),
            escape(proposal["target_object_type"]),
            escape(proposal["target_object_id"]),
            escape(proposal["proposal_state"]),
            escape(proposal.get("decision_id") or "—"),
        ]
        for proposal in pending_proposals
    ]
    closed_rows = [
        [
            _link(f"/surface/proposals/{proposal['proposal_id']}", proposal["proposal_id"]),
            escape(proposal["proposal_type"]),
            escape(proposal["target_object_type"]),
            escape(proposal["target_object_id"]),
            escape(proposal["proposal_state"]),
            escape(proposal.get("decision_id") or "—"),
        ]
        for proposal in closed_proposals
    ]
    sections = [
        _render_card(
            "Pending Review Queue",
            _render_table(
                ["Proposal ID", "Type", "Target Type", "Target ID", "State", "Decision ID"],
                pending_rows,
                "No proposals are currently pending human review.",
            ),
        ),
        _render_card(
            "Proposal History",
            _render_table(
                ["Proposal ID", "Type", "Target Type", "Target ID", "State", "Decision ID"],
                closed_rows,
                "No approved or rejected proposals have been recorded yet.",
            ),
        )
    ]
    return _render_page("Nexus Proposals", sections=sections)


def _render_proposal_review_page(runtime: RuntimeContext, proposal_id: str, *, note: str | None = None) -> str:
    context = _build_review_context(runtime, proposal_id)
    proposal = context["proposal"]
    decision = context["decision"]
    history = context["history"]
    current_object = context["current_object"]
    publication_href = context["publication_href"]

    current_rows = []
    if current_object is not None:
        current_rows = [[escape(key), _format_value(value)] for key, value in current_object.items()]

    object_summary_items = [
        ("Target Object Type", proposal.get("target_object_type")),
        ("Target Object ID", proposal.get("target_object_id")),
        ("Decision State", decision.get("decision_state")),
        ("Proposal State", proposal.get("proposal_state")),
        ("Live Object History", context["object_history_href"]),
    ]
    if publication_href is not None:
        object_summary_items.append(("Published Trace", publication_href))

    sections = [
        _render_card(
            "Proposal Summary",
            _render_kv(
                [
                    ("Proposal ID", proposal["proposal_id"]),
                    ("Type", proposal.get("proposal_type")),
                    ("Proposal State", proposal.get("proposal_state")),
                    ("Proposed By", proposal.get("proposed_by")),
                    ("Rationale", proposal.get("rationale")),
                    ("Target Refs", proposal.get("target_refs", [])),
                    ("Evidence Refs", proposal.get("evidence_refs", [])),
                ]
            ),
        ),
        _render_card(
            "Decision Summary",
            _render_kv(
                [
                    ("Decision ID", decision["decision_id"]),
                    ("Decision Type", decision.get("decision_type")),
                    ("Decision State", decision.get("decision_state")),
                    ("Decided By", decision.get("decided_by")),
                    ("Rationale", decision.get("rationale")),
                    ("Target Refs", decision.get("target_refs", [])),
                ]
            ),
        ),
        _render_card(
            "Review Context",
            _render_kv(object_summary_items),
        ),
        _render_card(
            "Current Object",
            _render_table(
                ["Field", "Value"],
                current_rows,
                "No live object is currently persisted for this identifier.",
            ),
        ),
        _render_card(
            "Version Trail",
            _render_version_table(history.get("versions", [])),
        ),
        _render_card(
            "Proposed Changes",
            _format_value(proposal.get("proposed_changes", {})),
        ),
        _render_card(
            "Review Actions",
            _render_review_actions(decision["decision_id"], decision.get("decision_state") or "unknown"),
        ),
    ]
    return _render_page(f"Proposal Review: {proposal_id}", sections=sections, note=note)


@router.get("/proposals/{proposal_id}", response_class=HTMLResponse)
def get_proposal(proposal_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    return _render_proposal_review_page(runtime, proposal_id)


def _handle_human_review_action(
    *,
    decision_id: str,
    action: str,
    decided_by: str,
    rationale: str | None,
    runtime: RuntimeContext,
) -> str:
    bundle = runtime.governance_service.get_decision_by_id(decision_id)
    if bundle is None:
        raise _not_found("decision", decision_id)
    proposal_id = bundle["proposal"]["proposal_id"]
    try:
        if action == "approve":
            runtime.governance_service.approve(
                decision_id,
                decided_by=decided_by,
                performed_via="human_ui",
                rationale=rationale,
            )
            note = "Proposal approved through the human review surface."
        else:
            runtime.governance_service.reject(
                decision_id,
                decided_by=decided_by,
                performed_via="human_ui",
                rationale=rationale,
            )
            note = "Proposal rejected through the human review surface."
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _render_proposal_review_page(runtime, proposal_id, note=note)


@router.post("/decisions/{decision_id}/approve", response_class=HTMLResponse)
def approve_proposal_via_surface(
    decision_id: str,
    decided_by: str = Form("human"),
    rationale: str | None = Form(None),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    return _handle_human_review_action(
        decision_id=decision_id,
        action="approve",
        decided_by=decided_by,
        rationale=rationale,
        runtime=runtime,
    )


@router.post("/decisions/{decision_id}/reject", response_class=HTMLResponse)
def reject_proposal_via_surface(
    decision_id: str,
    decided_by: str = Form("human"),
    rationale: str | None = Form(None),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    return _handle_human_review_action(
        decision_id=decision_id,
        action="reject",
        decided_by=decided_by,
        rationale=rationale,
        runtime=runtime,
    )


@router.get("/decisions", response_class=HTMLResponse)
def list_decisions(runtime: RuntimeContext = Depends(get_runtime)) -> str:
    decision_bundles = runtime.governance_service.list_decisions(decision_state=None)
    rows = [
        [
            _link(f"/surface/decisions/{decision['decision_id']}", decision["decision_id"]),
            escape(decision["decision_type"]),
            escape(decision["decision_state"]),
            escape(", ".join(decision.get("target_refs", []))),
            escape(decision.get("proposed_by") or "—"),
            escape(decision.get("decided_by") or "—"),
        ]
        for bundle in decision_bundles
        for decision in [bundle["decision"]]
    ]
    sections = [
        _render_card(
            "Decision Queue",
            _render_table(
                ["Decision ID", "Type", "State", "Targets", "Proposed By", "Decided By"],
                rows,
                "No decisions are currently recorded.",
            ),
        )
    ]
    return _render_page("Nexus Decisions", sections=sections)


@router.get("/decisions/{decision_id}", response_class=HTMLResponse)
def get_decision(decision_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    bundle = runtime.governance_service.get_decision_by_id(decision_id)
    if bundle is None:
        raise _not_found("decision", decision_id)
    proposal = bundle["proposal"]
    decision = bundle["decision"]

    sections = [
        _render_card(
            "Decision Details",
            _render_kv(
                [
                    ("Decision ID", decision["decision_id"]),
                    ("Decision Type", decision.get("decision_type")),
                    ("Decision State", decision.get("decision_state")),
                    ("Proposal Ref", decision.get("proposal_ref")),
                    ("Proposed By", decision.get("proposed_by")),
                    ("Decided By", decision.get("decided_by")),
                    ("Rationale", decision.get("rationale")),
                    ("Target Refs", decision.get("target_refs", [])),
                    ("Created At", decision.get("created_at")),
                    ("Updated At", decision.get("updated_at")),
                ]
            ),
        ),
        _render_card(
            "Linked Proposal",
            _render_kv(
                [
                    ("Proposal ID", proposal["proposal_id"]),
                    ("Type", proposal.get("proposal_type")),
                    ("Target Object Type", proposal.get("target_object_type")),
                    ("Target Object ID", proposal.get("target_object_id")),
                    ("Proposal State", proposal.get("proposal_state")),
                    ("Decision ID", proposal.get("decision_id")),
                ]
            ),
        ),
        _render_card(
            "Proposed Changes",
            _format_value(proposal.get("proposed_changes", {})),
        ),
        _render_card(
            "Review Links",
            _render_kv(
                [
                    ("Proposal Review", f"/surface/proposals/{proposal['proposal_id']}"),
                    ("Object History", f"/surface/objects/{proposal['target_object_type']}/{proposal['target_object_id']}/history"),
                    ("Published Trace", _build_review_context(runtime, proposal["proposal_id"])["publication_href"]),
                ]
            ),
        ),
        _render_card(
            "Review Actions",
            _render_review_actions(decision["decision_id"], decision.get("decision_state") or "unknown"),
        ),
    ]
    return _render_page(f"Decision Surface: {decision_id}", sections=sections)


@router.get("/graph", response_class=HTMLResponse)
def get_graph_surface(
    request: Request,
    domain: str | None = None,
    last_object_type: str | None = None,
    last_object_id: str | None = None,
    runtime: RuntimeContext = Depends(get_runtime),
) -> Any:
    return _render_workbench_template(
        request,
        runtime,
        page_mode="graph",
        domain_id=domain,
        last_object_type=last_object_type,
        last_object_id=last_object_id,
        drawer_open=False,
    )


@router.get("/graph.json")
def get_graph_json(
    domain: str | None = None,
    entity_type: str | None = None,
    relation_type: str | None = None,
    status: str | None = None,
    scope: str | None = None,
    focus: str | None = None,
    depth: int = 2,
    view: str = "global",
    label_mode: str = "key",
    color_mode: str = "by_domain",
    size_mode: str = "by_degree",
    cross_domain: str = "show_all",
    runtime: RuntimeContext = Depends(get_runtime),
) -> dict[str, Any]:
    allowed_views = {"global", "domain", "focus", "governance", "evidence", "reentry", "cross_domain"}
    if view not in allowed_views:
        view = "global"
    allowed_cross_domain_modes = {"show_all", "proposed_only", "hide", "only"}
    if cross_domain not in allowed_cross_domain_modes:
        cross_domain = "show_all"
    if view == "cross_domain" and cross_domain == "show_all":
        cross_domain = "only"
    depth = max(1, min(depth, 5))

    all_entities = runtime.entity_service.list_entities()
    all_relations = runtime.relation_service.list_relations()
    entity_by_id = {entity["entity_id"]: entity for entity in all_entities}
    governance_statuses = {"proposed", "contested", "rejected"} if view == "governance" and status is None else None

    def status_matches(value: str | None) -> bool:
        if status is not None:
            return value == status
        if governance_statuses is not None:
            return value in governance_statuses
        return True

    def entity_refs(entity: dict[str, Any]) -> list[Any]:
        return list(entity.get("provenance_refs") or []) + list(entity.get("payload_refs") or [])

    def relation_refs(relation: dict[str, Any]) -> list[Any]:
        return list(relation.get("evidence_refs") or [])

    def has_reentry_ref(refs: list[Any]) -> bool:
        return any(
            token in str(ref).lower()
            for ref in refs
            for token in ("reentry", "parse-diff", "payload-edit", "tree-proposal")
        )

    def entity_matches(entity: dict[str, Any], *, include_domain: bool = True) -> bool:
        return (
            (not include_domain or domain is None or entity.get("domain_id") == domain)
            and (entity_type is None or entity.get("entity_type") == entity_type)
            and status_matches(entity.get("validation_status"))
            and (scope is None or entity.get("scope") == scope)
        )

    eligible_entity_ids = {entity["entity_id"] for entity in all_entities if entity_matches(entity, include_domain=False)}
    visible_entity_ids = {entity["entity_id"] for entity in all_entities if entity_matches(entity)}

    relations: list[dict[str, Any]] = []
    for relation in all_relations:
        source_id = relation.get("source_entity_id")
        target_id = relation.get("target_entity_id")
        source = entity_by_id.get(source_id)
        target = entity_by_id.get(target_id)
        if source is None or target is None:
            continue
        if source_id not in eligible_entity_ids or target_id not in eligible_entity_ids:
            continue
        if relation_type is not None and relation.get("relation_type") != relation_type:
            continue
        if not status_matches(relation.get("validation_status")):
            continue

        source_domain = source.get("domain_id")
        target_domain = target.get("domain_id")
        is_cross_domain = bool(source_domain and target_domain and source_domain != target_domain)
        touches_selected_domain = domain is None or source_domain == domain or target_domain == domain or relation.get("domain_context") == domain

        if not touches_selected_domain:
            continue
        if cross_domain == "hide" and is_cross_domain:
            continue
        if cross_domain == "only" and not is_cross_domain:
            continue
        if cross_domain == "proposed_only" and is_cross_domain and relation.get("validation_status") != "proposed":
            continue

        if domain is None or is_cross_domain or source_id in visible_entity_ids or target_id in visible_entity_ids:
            relation = dict(relation)
            relation["cross_domain"] = is_cross_domain
            relation["source_domain_id"] = source_domain
            relation["target_domain_id"] = target_domain
            relations.append(relation)

    if view in {"evidence", "reentry"}:
        entity_has_signal = {
            entity_id: bool(refs) if view == "evidence" else has_reentry_ref(refs)
            for entity_id, entity in entity_by_id.items()
            for refs in [entity_refs(entity)]
        }
        filtered_relations: list[dict[str, Any]] = []
        signal_entity_ids = {entity_id for entity_id, has_signal in entity_has_signal.items() if has_signal}
        for relation in relations:
            refs = relation_refs(relation)
            relation_has_signal = bool(refs) if view == "evidence" else has_reentry_ref(refs)
            if relation_has_signal or relation["source_entity_id"] in signal_entity_ids or relation["target_entity_id"] in signal_entity_ids:
                filtered_relations.append(relation)
                signal_entity_ids.update([relation["source_entity_id"], relation["target_entity_id"]])
        visible_entity_ids = (visible_entity_ids | signal_entity_ids) & eligible_entity_ids
        relations = filtered_relations

    if focus:
        adjacency: dict[str, set[str]] = {}
        for relation in relations:
            source_id = relation["source_entity_id"]
            target_id = relation["target_entity_id"]
            adjacency.setdefault(source_id, set()).add(target_id)
            adjacency.setdefault(target_id, set()).add(source_id)
        reachable = {focus}
        queue: deque[tuple[str, int]] = deque([(focus, 0)])
        while queue:
            current_id, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            for next_id in adjacency.get(current_id, set()):
                if next_id not in reachable:
                    reachable.add(next_id)
                    queue.append((next_id, current_depth + 1))
        visible_entity_ids = reachable & eligible_entity_ids
        relations = [
            relation
            for relation in relations
            if relation["source_entity_id"] in visible_entity_ids and relation["target_entity_id"] in visible_entity_ids
        ]
    else:
        relation_entity_ids = {relation["source_entity_id"] for relation in relations} | {relation["target_entity_id"] for relation in relations}
        visible_entity_ids = (visible_entity_ids | relation_entity_ids) & eligible_entity_ids

    degree = Counter()
    for relation in relations:
        degree.update([relation["source_entity_id"], relation["target_entity_id"]])

    events_by_target: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for event in runtime.event_service.list_events():
        key = (event.get("target_object_type"), event.get("target_object_id"))
        events_by_target.setdefault(key, []).append(event)

    def event_summary(object_type: str, object_id: str) -> tuple[int, str | None]:
        events = events_by_target.get((object_type, object_id), [])
        latest = max((event.get("created_at") for event in events if event.get("created_at")), default=None)
        return len(events), latest

    entities = [entity_by_id[entity_id] for entity_id in visible_entity_ids if entity_id in entity_by_id]

    def node_risk(entity: dict[str, Any]) -> str:
        status_value = entity.get("validation_status")
        if status_value in {"rejected", "contested"}:
            return "critical"
        if status_value == "proposed":
            return "attention"
        return "ok"

    return {
        "nodes": [
            (
                lambda event_count, last_event_at: {
                    "id": entity["entity_id"],
                    "label": entity.get("label") or entity["entity_id"],
                    "object_type": "entity",
                    "domain_id": entity.get("domain_id"),
                    "entity_type": entity.get("entity_type"),
                    "scope": entity.get("scope"),
                    "validation_status": entity.get("validation_status"),
                    "confidence": entity.get("confidence"),
                    "degree": degree[entity["entity_id"]],
                    "is_focal": bool(focus and entity["entity_id"] == focus),
                    "evidence_count": len(entity.get("provenance_refs") or []) + len(entity.get("payload_refs") or []),
                    "event_count": event_count,
                    "last_event_at": last_event_at,
                    "risk": node_risk(entity),
                    "inspector_href": f"/surface/objects/entity/{entity['entity_id']}",
                    "history_href": f"/surface/objects/entity/{entity['entity_id']}/history",
                }
            )(*event_summary("entity", entity["entity_id"]))
            for entity in entities
        ],
        "edges": [
            (
                lambda event_count, last_event_at: {
                    "id": relation["relation_id"],
                    "source": relation["source_entity_id"],
                    "target": relation["target_entity_id"],
                    "label": relation.get("relation_type"),
                    "relation_type": relation.get("relation_type"),
                    "domain_id": relation.get("domain_context"),
                    "source_domain_id": relation.get("source_domain_id"),
                    "target_domain_id": relation.get("target_domain_id"),
                    "validation_status": relation.get("validation_status"),
                    "confidence": relation.get("confidence"),
                    "evidence_refs": relation.get("evidence_refs") or [],
                    "evidence_count": len(relation.get("evidence_refs") or []),
                    "event_count": event_count,
                    "last_event_at": last_event_at,
                    "cross_domain": relation.get("cross_domain", False),
                    "directionality": relation.get("directionality"),
                    "inspector_href": f"/surface/objects/relation/{relation['relation_id']}",
                    "history_href": f"/surface/objects/relation/{relation['relation_id']}/history",
                }
            )(*event_summary("relation", relation["relation_id"]))
            for relation in relations
        ],
        "meta": {
            "filters": {
                "domain": domain,
                "entity_type": entity_type,
                "relation_type": relation_type,
                "status": status,
                "scope": scope,
                "focus": focus,
                "depth": depth,
                "view": view,
                "label_mode": label_mode,
                "color_mode": color_mode,
                "size_mode": size_mode,
                "cross_domain": cross_domain,
            },
            "available_domains": sorted({entity.get("domain_id") for entity in all_entities if entity.get("domain_id")}),
            "available_entity_types": sorted({entity.get("entity_type") for entity in all_entities if entity.get("entity_type")}),
            "available_relation_types": sorted({relation.get("relation_type") for relation in all_relations if relation.get("relation_type")}),
        },
    }


@router.get("/objects/{object_type}/{object_id}", response_class=HTMLResponse)
def get_object_inspector(
    object_type: str,
    object_id: str,
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    record = _object_record(runtime, object_type, object_id)
    if record is None:
        raise _not_found(object_type, object_id)
    links: list[tuple[str, Any]] = [("Inspector", f"/surface/objects/{object_type}/{object_id}")]
    if object_type in _SUPPORTED_HISTORY_TYPES:
        links.append(("History", f"/surface/objects/{object_type}/{object_id}/history"))
    if object_type == "payload":
        links.append(("Payload Viewer", f"/surface/payloads/{object_id}"))
    if object_type == "projection":
        links.append(("Projection Panel", f"/surface/projections/{object_id}"))
    sections = [
        _render_card(
            "Object Summary",
            _render_kv(
                [
                    ("Object Type", object_type),
                    ("Object ID", object_id),
                    ("Live Runtime Record", True),
                ]
            ),
        ),
        _render_card("Navigation", _render_kv(links)),
        _render_card("Record", _render_record_table(record)),
    ]
    return _render_page(f"Object Inspector: {object_type}/{object_id}", sections=sections)


@router.get("/payloads/{payload_id}", response_class=HTMLResponse)
def get_payload_viewer(payload_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    payload = runtime.payload_service.get_payload_by_id(payload_id)
    if payload is None:
        raise _not_found("payload", payload_id)
    content = runtime.payload_service.read_payload_content(payload_id) or ""
    sections = [
        _render_card("Payload Summary", _render_record_table(payload)),
        _render_card("Payload Content", f"<pre>{escape(content)}</pre>" if content else "<p class='muted'>No readable payload content.</p>"),
        _render_card(
            "Reentry",
            _render_kv(
                [
                    ("Parse Diff Panel", "/surface/reentry/parse-diff"),
                    ("Object Inspector", f"/surface/objects/payload/{payload_id}"),
                    ("Object History", f"/surface/objects/payload/{payload_id}/history"),
                ]
            ),
        ),
    ]
    return _render_page(f"Payload Viewer: {payload_id}", sections=sections)


@router.get("/projections/{projection_id}", response_class=HTMLResponse)
def get_projection_panel(projection_id: str, runtime: RuntimeContext = Depends(get_runtime)) -> str:
    projection = runtime.projection_service.get_projection_by_id(projection_id)
    if projection is None:
        raise _not_found("projection", projection_id)
    content = runtime.projection_service.read_projection_content(projection_id) or ""
    sections = [
        _render_card("Projection Summary", _render_record_table(projection)),
        _render_card("Projection Content", f"<pre>{escape(content)}</pre>" if content else "<p class='muted'>No readable projection content.</p>"),
        _render_card(
            "Reentry",
            _render_kv(
                [
                    ("Parse Diff Panel", "/surface/reentry/parse-diff"),
                    ("Object Inspector", f"/surface/objects/projection/{projection_id}"),
                ]
            ),
        ),
    ]
    return _render_page(f"Projection Panel: {projection_id}", sections=sections)


@router.get("/events/timeline", response_class=HTMLResponse)
def get_event_timeline(runtime: RuntimeContext = Depends(get_runtime)) -> str:
    events = sorted(runtime.event_service.list_events(), key=lambda event: (event.get("created_at") or "", event["event_id"]), reverse=True)
    rows = [
        [
            escape(event["created_at"]),
            _link(f"/surface/objects/event/{event['event_id']}", event["event_id"]),
            escape(event["event_type"]),
            escape(event["target_object_type"]),
            _link(f"/surface/objects/{event['target_object_type']}/{event['target_object_id']}", event["target_object_id"]),
            escape(event.get("performed_by") or "—"),
        ]
        for event in events
    ]
    return _render_page(
        "Event Timeline",
        sections=[
            _render_card(
                "Timeline",
                _render_table(
                    ["Created At", "Event", "Type", "Target Type", "Target", "Performed By"],
                    rows,
                    "No events are currently recorded.",
                ),
            )
        ],
        note="Read-only event timeline from executable state.",
    )


@router.get("/reentry/parse-diff", response_class=HTMLResponse)
def get_reentry_parse_diff_panel() -> str:
    form = """
<form class='action-form' method='post' action='/surface/reentry/parse-diff'>
  <h3>Create Reentry Proposal</h3>
  <label>Target Object Type <input type='text' name='target_object_type' value='payload' /></label>
  <label>Target Object ID <input type='text' name='target_object_id' /></label>
  <label>Before <textarea name='before' rows='6'></textarea></label>
  <label>After <textarea name='after' rows='6'></textarea></label>
  <label>Proposed By <input type='text' name='proposed_by' value='human' /></label>
  <button type='submit'>Create proposal</button>
</form>
"""
    return _render_page(
        "Reentry Parse Diff",
        sections=[_render_card("Diff Panel", form)],
        note="This panel creates a structured reentry proposal only; it does not mutate the target object.",
    )


@router.post("/reentry/parse-diff", response_class=HTMLResponse)
def submit_reentry_parse_diff_panel(
    target_object_type: str = Form(...),
    target_object_id: str = Form(...),
    before: str = Form(...),
    after: str = Form(...),
    proposed_by: str = Form("human"),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    if _object_record(runtime, target_object_type, target_object_id) is None:
        raise _not_found(target_object_type, target_object_id)
    result = runtime.reentry_service.parse_diff(
        target_object_type=target_object_type,
        target_object_id=target_object_id,
        before=before,
        after=after,
        proposed_by=proposed_by,
    )
    proposal = result["proposal"]
    return _render_page(
        "Reentry Parse Diff",
        sections=[
            _render_card(
                "Proposal Created",
                _render_kv(
                    [
                        ("Proposal ID", proposal["proposal_id"]),
                        ("Proposal Type", proposal["proposal_type"]),
                        ("Target", f"{proposal['target_object_type']}:{proposal['target_object_id']}"),
                        ("Review Surface", f"/surface/proposals/{proposal['proposal_id']}"),
                    ]
                ),
            ),
            _render_card("Proposed Changes", _format_value(proposal.get("proposed_changes") or {})),
        ],
        note="Structured reentry proposal created. The live target was not mutated.",
    )


@router.get("/objects/{object_type}/{object_id}/history", response_class=HTMLResponse)
def get_object_history(
    object_type: str,
    object_id: str,
    request: Request,
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    if object_type not in _SUPPORTED_HISTORY_TYPES:
        raise _not_found("object type", object_type)

    history = runtime.governance_service.get_object_history(object_type, object_id)
    current_object = history.get("current_object")
    versions = history.get("versions", [])
    current_rows = []
    if current_object is not None:
        current_rows = [
            [escape(key), _format_value(value)]
            for key, value in current_object.items()
        ]

    version_rows = [
        [
            escape(str(version.get("version_number"))),
            escape(version.get("version_id") or "—"),
            escape(version.get("serialized_state_ref") or "—"),
            escape(version.get("created_by") or "—"),
            escape(version.get("created_at") or "—"),
        ]
        for version in versions
    ]
    sections = [
        _render_card(
            "History Summary",
            _render_kv(
                [
                    ("Object Type", history["object_type"]),
                    ("Object ID", history["object_id"]),
                    ("Current Object Present", current_object is not None),
                    ("Version Count", history["version_count"]),
                    ("Latest Version Number", history.get("latest_version_number")),
                ]
            ),
        ),
        _render_card(
            "Current Object",
            _render_table(
                ["Field", "Value"],
                current_rows,
                "No live object is currently persisted for this identifier.",
            ),
        ),
    ]
    if object_type == "entity" and current_object is not None and current_object.get("domain_id"):
        artifact_path = _entity_snapshot_path(request, current_object["domain_id"], object_id)
        edit_items = [
            ("Eligible Edit", "Entity short_description"),
            ("Published Artifact", artifact_path.as_posix()),
            ("Proposal From Edit", f"/surface/objects/entity/{object_id}/proposal-from-edit"),
        ]
        if artifact_path.exists():
            edit_items.append(("Artifact Ready", True))
        else:
            edit_items.append(("Artifact Ready", False))
        sections.append(
            _render_card(
                "Proposal From Edit",
                _render_kv(edit_items),
            )
        )
    if object_type == "relation" and current_object is not None and current_object.get("domain_context"):
        artifact_path = _relation_snapshot_path(request, current_object["domain_context"], object_id)
        edit_items = [
            ("Eligible Edit", "Relation validation_status"),
            ("Published Artifact", artifact_path.as_posix()),
            ("Proposal From Edit", f"/surface/objects/relation/{object_id}/proposal-from-edit"),
            ("Artifact Ready", artifact_path.exists()),
        ]
        if current_object.get("validation_status") is not None:
            edit_items.append(("Current Validation Status", current_object.get("validation_status")))
        sections.append(
            _render_card(
                "Proposal From Edit",
                _render_kv(edit_items),
            )
        )
    sections.append(
        _render_card(
            "Version Trail",
            _render_table(
                ["Version", "Version ID", "Serialized State Ref", "Created By", "Created At"],
                version_rows,
                "No approved object versions are recorded yet.",
            ),
        )
    )
    return _render_page(f"Object History: {object_type}/{object_id}", sections=sections)


@router.get("/objects/entity/{entity_id}/proposal-from-edit", response_class=HTMLResponse)
def get_entity_proposal_from_edit(
    entity_id: str,
    request: Request,
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    context = _build_controlled_reentry_context(runtime, request, "entity", entity_id)
    return _render_entity_proposal_from_edit_page(context)


@router.post("/objects/entity/{entity_id}/proposal-from-edit", response_class=HTMLResponse)
def submit_entity_proposal_from_edit(
    entity_id: str,
    request: Request,
    edited_value: str = Form(...),
    proposed_by: str = Form("human"),
    rationale: str | None = Form(None),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    return _submit_controlled_reentry_proposal(
        runtime=runtime,
        request=request,
        object_type="entity",
        object_id=entity_id,
        edited_value=edited_value,
        proposed_by=proposed_by,
        rationale=rationale,
    )


@router.get("/objects/relation/{relation_id}/proposal-from-edit", response_class=HTMLResponse)
def get_relation_proposal_from_edit(
    relation_id: str,
    request: Request,
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    context = _build_controlled_reentry_context(runtime, request, "relation", relation_id)
    return _render_relation_proposal_from_edit_page(context)


@router.post("/objects/relation/{relation_id}/proposal-from-edit", response_class=HTMLResponse)
def submit_relation_proposal_from_edit(
    relation_id: str,
    request: Request,
    edited_value: str = Form(...),
    proposed_by: str = Form("human"),
    rationale: str | None = Form(None),
    runtime: RuntimeContext = Depends(get_runtime),
) -> str:
    return _submit_controlled_reentry_proposal(
        runtime=runtime,
        request=request,
        object_type="relation",
        object_id=relation_id,
        edited_value=edited_value,
        proposed_by=proposed_by,
        rationale=rationale,
    )
