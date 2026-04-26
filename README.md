# Nexus

Local-first cognitive-operational infrastructure.

---

## What This Is

Nexus is a local-first product for preserving institutional memory, managing knowledge objects, and operating cognitive workflows under explicit governance.

It consists of:
- **Executable core** — local SQLite-backed database that is the authoritative source of truth
- **Materialization regime** — governed publication of semantic artifacts to `tree/`
- **Operation surfaces** — human cockpit, local REST agent surface, and formal MCP adapter over the same services

This repository contains everything: specs, application code, agent coordination layer, and materialization output.

---

## Product Status

Current state:

- **Ready for local-first operational use and maintenance.**
- **Not a general-availability hosted product.**
- **Not connector-complete for external email, calendar, or chat systems.**

Use Nexus when you need:

- domains as the main unit of knowledge organization;
- governed proposals and decisions instead of silent canonical mutation;
- object versions, events, provenance, and audit paths;
- a human cockpit for inspection and review;
- local REST and MCP agent surfaces over the same executable core.

Fastest entry point after startup:

```text
http://127.0.0.1:8000/surface
```

---

## Repository Layout

```
nexus/
  system/runtime/    ← application runtime: storage, domain runtime, ingestion, governance, events
  system/tests/      ← unit and integration tests
  tree/              ← materialization surface (treefolder — human and agent readable)
  agent/             ← build/maintenance agent coordination layer
  system/00_specs/   ← authoritative technical specifications (read-only)
  AGENTS.md          ← agent orientation (start here if you are an agent)
  CURRENT_STATE.md   ← human-owned operational summary
  SYSTEM_STATUS.yaml ← machine-readable system state snapshot
  WORKSPACE_CONTRACT.md ← what is stable vs mutable
```

---

## Current Phase

**Post-PRD acceptance — maintenance and hardening**

Nexus is ready for local-first operational use and maintenance under the approved PRD assumptions.

This does not claim hosted, connector-complete, or general-availability product readiness. External email/calendar/chat connectors, full semantic canonicalization, advanced audit replay, deeper MCP transport hardening, and UI polish remain future hardening or expansion work.

See `SYSTEM_STATUS.yaml` for the machine-readable build state.
See `agent/CURRENT_MISSION.md` for the active maintenance mission.
See `agent/plan/DEFINITION_OF_DONE.md` for closure criteria.
See `agent/plan/ROADMAP_ALIGNMENT.md` for the macro-roadmap to sprint-history mapping.
See `agent/ops/PRODUCT_READINESS_REVIEW_2026-04-13.md` for the product/spec readiness assessment.

---

## Install Locally

Prerequisite:

- Python 3.11+

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

By default, Nexus uses:

```text
.nexus/nexus.db
```

To use another local database path:

```powershell
$env:NEXUS_DB_PATH = "C:\Dev\nexus\.nexus\nexus.db"
```

---

## Initialize Local Content

To create the default local domain seed:

```powershell
python -c "from system.runtime.core.bootstrap import bootstrap_minimum_domain_content; bootstrap_minimum_domain_content()"
```

This initializes the local database and creates a minimum `nexus-core` domain. It does not modify the read-only specs in `system/00_specs/`.

---

## Start Nexus

Recommended local start:

```powershell
python -m system.runtime.api.main
```

Equivalent explicit Uvicorn command:

```powershell
uvicorn system.runtime.api.main:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/surface
```

---

## First UI Path

Use these cockpit routes first:

1. `/surface` — overview, status, navigation, and operational entry point.
2. `/surface/graph` — MAP Workbench for dynamic domain/entity/relation topology, focus navigation, graph filters, and read-only inspection.
3. `/surface/events/timeline` — FLOW view for events and change chronology.
4. `/surface/proposals` — AUDIT view for pending or historical proposals.
5. `/surface/decisions` — decision review and governance trail.
6. `/surface/reentry/parse-diff` — parse a proposed text diff into a governed reentry proposal.

Useful technical surfaces:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/agent
http://127.0.0.1:8000/docs
```

To install the local Nexus MCP server into Codex, use the repo skill:

```text
agent/skills/nexus-install-mcp/SKILL.md
```

Object inspection is usually reached from cockpit links. Direct route pattern:

```text
/surface/objects/{object_type}/{object_id}
```

The MAP Workbench uses a vendored local D3 asset served by FastAPI. It does not require Node, Vite, React, Tailwind, or CDN access at runtime.

---

## For Agents

Start with `AGENTS.md`. It indexes everything you need before acting.

Then use `agent/NEXUS_LOCAL_AGENT_GUIDE.md` for the practical local-agent guide covering product identity, runtime components, runs/scripts, and governance.

---

## For Humans

Start with `SYSTEM_STATUS.yaml` for the live build snapshot.
Start with `agent/CURRENT_MISSION.md` for the active slice and `agent/plan/DEFINITION_OF_DONE.md` for closure criteria.
Use `agent/plan/ROADMAP_ALIGNMENT.md` when you need the spec-roadmap to execution-sprint mapping.
`CURRENT_STATE.md` is a human-owned operational summary synchronized under explicit human authorization in the governance sync slice.
Start with `system/00_specs/1.TECH_SPEC_OVERVIEW.md` for architectural grounding.
Start with `tree/START_HERE.md` (once materialized) for knowledge navigation.

---

## Validate The Local Runtime

Run the full test suite:

```powershell
python -m unittest discover -s system/tests -t . -p "test_*.py"
```

For a documentation-only change, runtime tests are not required unless code or executable behavior changed.

---

## Tech Stack

- Python 3.11+ / FastAPI / SQLite
- Jinja2 for the local cockpit templates
- MCP Python package for the formal adapter
- SQLite bootstrap migrations
- unittest
- `tree/` published as Markdown/YAML
