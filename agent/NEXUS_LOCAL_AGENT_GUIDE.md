# Nexus Local Agent Guide

Date: 2026-04-13
Status: active reference for the local Nexus agent

This guide is the operational handoff for a local agent working inside the Nexus repository. It does not replace `AGENTS.md`, `WORKSPACE_CONTRACT.md`, `agent/AUTHORITY_MATRIX.md`, or `agent/BUILD_PROTOCOL.md`; it gives the practical product, system, run, and governance map needed to operate without rediscovering the repo.

---

## 1. Identidade

### Nexus as product

Nexus is a local-first cognitive-operational infrastructure for preserving institutional memory, managing knowledge objects, and operating governed cognitive workflows.

The current product claim is intentionally bounded:

- Ready for local-first operational use and maintenance.
- Not a general-availability hosted product.
- Not connector-complete for external email, calendar, or chat systems.

The product thesis:

- The SQLite-backed executable core is the authority for live state.
- `tree/` is a materialized publication surface, not a source of executable truth.
- The human cockpit and agent/MCP surfaces expose the same core through governed routes.
- Agent work is proposal-first when a mutation is not already authorized.
- Auditability matters as much as object storage: events, versions, proposals, decisions, evidence refs, and materialization traces must remain legible.

What Nexus is not:

- It is not a generic note app.
- It is not a treefolder-first knowledge base.
- It is not a hosted SaaS.
- It is not an external connector platform yet.
- It is not an unconstrained autonomous-agent runtime.

### Local Nexus agent identity

The local Nexus agent is a maintenance agent operating in the same workspace as the human owner.

Current lifecycle:

- Build agent lifecycle: complete.
- PRD acceptance closure: complete under approved local-first assumptions.
- Post-closure completion sprint: complete.
- Active mode: maintenance, hardening, real-use ingestion, and usability refinement.

The local agent's job:

- preserve executable precedence;
- apply targeted patches when authorized;
- keep documentation and coordination artifacts aligned with actual state;
- run relevant validation;
- record significant work in `agent/ops/`;
- surface drift or authority conflicts instead of silently improvising architecture.

The local agent must not:

- modify `system/00_specs/`;
- redesign the architecture without explicit human gate;
- claim general-availability readiness;
- edit `CURRENT_STATE.md` without explicit human authorization;
- treat `tree/` as sovereign runtime truth;
- silently absorb unrelated dirty worktree changes.

### Primary orientation order

Before major work, read in this order:

1. `AGENTS.md`
2. `WORKSPACE_CONTRACT.md`
3. `agent/CURRENT_MISSION.md`
4. `agent/plan/ACTIVE_TRACK.md`
5. `agent/plan/DEFINITION_OF_DONE.md`
6. `agent/BUILD_PROTOCOL.md`
7. `agent/AUTHORITY_MATRIX.md`
8. `SYSTEM_STATUS.yaml`

Use `agent/plan/ROADMAP_ALIGNMENT.md` when you need to map spec phases to the sprint history that actually happened.

---

## 2. Sistema

### Repository layers

The repository has four active layers:

| Layer | Path | Role |
| --- | --- | --- |
| Specs | `system/00_specs/` | Read-only normative architecture and PRD |
| Runtime | `system/runtime/` | Executable core, API, MCP, materialization code |
| Tests | `system/tests/` | Unit and integration verification |
| Coordination | `agent/` | Plans, authority, execution logs, drift records, skills |
| Materialization | `tree/` | Published derived artifacts for human/agent reading |
| Output | `output/` | Ephemeral run artifacts such as screenshots and local browser evidence |

There is no separate app repo. Nexus is the application, workspace, coordination layer, and materialization surface in one repository.

### Runtime components

| Component | Path | Responsibility |
| --- | --- | --- |
| Settings | `system/runtime/config/settings.py` | Reads environment and resolves DB path |
| API app | `system/runtime/api/main.py` | Creates FastAPI app, mounts routers, mounts `/static`, exposes `/health` |
| Runtime context | `system/runtime/api/dependencies.py` | Builds services, repositories, payload/projection roots |
| Read router | `system/runtime/api/routers/read.py` | Core object read and search endpoints |
| Governance router | `system/runtime/api/routers/governance.py` | Proposals, decisions, rules, events, audit comparison |
| Pipeline router | `system/runtime/api/routers/pipelines.py` | Ingest, reconciliation, materialization, reentry |
| Agent REST router | `system/runtime/api/routers/agent_surface.py` | Local agent manifest and structured read/proposal surface |
| Human surface router | `system/runtime/api/routers/surface.py` | FastAPI/Jinja cockpit pages and workbench routes |
| MCP adapter | `system/runtime/mcp/server.py` | Formal MCP server exposing 9 normative tools |
| Storage DB | `system/runtime/core/storage/db.py` | SQLite connection and initialization |
| Migrations | `system/runtime/core/storage/migrations/bootstrap.py` | Bootstrap schema |
| Repositories | `system/runtime/core/storage/repositories/` | DB object persistence with no HTTP responsibility |
| Services | `system/runtime/core/storage/services.py` | Domain, object, governance, ingest, materialization orchestration |
| Materialization | `system/runtime/core/materialization/` | Operational projections and treefolder publisher |
| Bootstrap | `system/runtime/core/bootstrap/` | Minimum domain seed content |
| Cockpit MAP JS | `system/runtime/api/static/cockpit_map.js` | Local D3 graph workbench behavior |
| Vendored D3 | `system/runtime/api/static/vendor/d3.v7.9.0.min.js` | Local graph dependency, no CDN/Node pipeline |

### Core object model

The runtime persists and operates at least these object classes:

| Object | Role |
| --- | --- |
| Domain | Primary cognitive/operational scope |
| Source | Origin of ingested content |
| Payload | Raw/parsed/editable content bundle |
| Entity | Typed object inside a domain |
| Relation | Typed edge between entities |
| Event | Audit trace of meaningful state change |
| Proposal | Proposed mutation or review object |
| Decision | Human/governance decision state |
| GovernanceRule | Registered rule metadata and status |
| ObjectVersion | Snapshot for reconstructability and comparison |
| Projection | Generated operational view |
| Jobs | Ingestion/materialization/reentry execution tracking |

Rule: relevant mutations must emit events and preserve traceability.

### Human surfaces

Primary cockpit:

```text
http://127.0.0.1:8000/surface
```

Important pages:

| Route | Purpose |
| --- | --- |
| `/surface` | Overview and navigation |
| `/surface/graph` | MAP Workbench for graph navigation, focus, filters, D3 interaction |
| `/surface/events/timeline` | FLOW view for event chronology |
| `/surface/proposals` | AUDIT view for proposal review |
| `/surface/decisions` | Decision review trail |
| `/surface/reentry/parse-diff` | Parse text diff into governed reentry proposal |
| `/surface/objects/{object_type}/{object_id}` | Unified object inspector |
| `/surface/payloads/{payload_id}` | Payload viewer |
| `/surface/projections/{projection_id}` | Projection panel |

The cockpit is local FastAPI/Jinja/local JS. It is not React/Vite/Tailwind. MAP uses local D3 served from `/static`.

### REST and MCP surfaces

Useful technical routes:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/agent
```

The agent REST surface is operational and local. The MCP adapter is the formal agent transport surface over the same services.

Normative MCP tools:

- `get_domain`
- `get_entity`
- `get_relation`
- `get_payload`
- `search_objects`
- `get_projection`
- `create_proposal`
- `get_decision_queue`
- `explain_object`

Use `agent/skills/nexus-install-mcp/SKILL.md` to install or repair the Codex MCP entry.

### Runs and commands

Run commands from the repository root unless explicitly noted.

Install editable package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Set a DB path explicitly:

```powershell
$env:NEXUS_DB_PATH = "C:\Dev\nexus\.nexus\nexus.db"
```

Seed minimum local content:

```powershell
python -c "from system.runtime.core.bootstrap import bootstrap_minimum_domain_content; bootstrap_minimum_domain_content()"
```

Start the FastAPI runtime:

```powershell
python -m system.runtime.api.main
```

Equivalent explicit server run:

```powershell
uvicorn system.runtime.api.main:app --host 127.0.0.1 --port 8000
```

Start the MCP server directly from repo root:

```powershell
python -m system.runtime.mcp.server
```

Validate changed Python modules:

```powershell
python -m py_compile system/runtime/api/main.py system/runtime/api/routers/surface.py
```

Validate local MAP JavaScript:

```powershell
node --check system/runtime/api/static/cockpit_map.js
```

Run full regression:

```powershell
python -m unittest discover -s system/tests -t . -p "test_*.py"
```

Run a targeted test module:

```powershell
python -m unittest system.tests.integration.test_operational_surface -v
```

Inspect Codex MCP entry:

```powershell
codex mcp get nexus
codex mcp list
```

### Scripts and executable entry points

Nexus currently does not rely on standalone root-level operational scripts. Treat the executable entry points as Python modules/functions:

| Entry point | How to run | Purpose |
| --- | --- | --- |
| API app | `python -m system.runtime.api.main` | Start local FastAPI runtime |
| MCP server | `python -m system.runtime.mcp.server` | Start MCP stdio server |
| Bootstrap content | `python -c "from system.runtime.core.bootstrap import bootstrap_minimum_domain_content; bootstrap_minimum_domain_content()"` | Seed minimum local domain and content |
| Tests | `python -m unittest discover -s system/tests -t . -p "test_*.py"` | Full regression |
| MAP JS syntax | `node --check system/runtime/api/static/cockpit_map.js` | Validate local JS syntax when MAP changes |

If adding a new operational script, prefer putting it under a clear runtime or agent location and documenting its authority boundary. Do not revive deleted root scratch scripts as canonical commands.

### Data and artifact locations

| Path | Meaning |
| --- | --- |
| `.nexus/nexus.db` | Default local executable DB |
| `.nexus/payloads/` | Runtime payload storage when using default DB root |
| `.nexus/projections/` | Runtime projection storage when using default DB root |
| `tree/` | Derived materialized artifacts |
| `output/playwright/` | Ephemeral browser/visual evidence |
| `agent/ops/` | Operational logs, proposals, drift records |

Do not write tests against the production DB path unless the test explicitly intends to inspect local state. Normal tests must use temporary DBs.

---

## 3. Governanca

### Authority hierarchy

The authority order is:

1. Human owner decisions.
2. `system/00_specs/` as read-only normative layer.
3. Executable DB-backed runtime for live state.
4. `tree/` as derived publication.
5. `agent/` as coordination and governance record.

If these conflict, do not silently reconcile by editing specs or human-owned state. Record the drift in `agent/ops/` and ask for a human decision if needed.

### Stable and human-owned artifacts

Do not edit without explicit human authorization:

- `system/00_specs/`
- `AGENTS.md`
- `WORKSPACE_CONTRACT.md`
- `CURRENT_STATE.md`

`CURRENT_STATE.md` is human-owned. If it needs synchronization, create a proposal or drift note in `agent/ops/`.

### Mutable maintenance artifacts

The local maintenance agent may update these within mission scope:

- `system/runtime/` for targeted patches;
- `system/tests/` for validation;
- `tree/` as derived materialization;
- `SYSTEM_STATUS.yaml` after meaningful state change;
- `agent/CURRENT_MISSION.md` when mission state changes;
- `agent/plan/ACTIVE_TRACK.md` when work state changes;
- `agent/plan/ROADMAP_ALIGNMENT.md` for roadmap/execution alignment;
- `agent/ops/` for logs, proposals, blockers, drift records;
- `README.md` when the repository entry point needs to reflect actual operation.

### Mutation classes

Use the mutation regime from `agent/AUTHORITY_MATRIX.md` and `agent/BUILD_PROTOCOL.md`:

| Class | Meaning | Local agent stance |
| --- | --- | --- |
| A | Read only | Allowed |
| B | Proposal | Allowed |
| C | Authorized mutation | Allowed only when spec-covered and mission-scoped |
| D | Critical mutation | Requires human gate |

Examples of critical mutation:

- schema inversion;
- canonical identity redefinition;
- governance rule semantics beyond registered metadata/status;
- remote write authority expansion;
- source-of-truth inversion from DB to `tree/`;
- new product phase declaration.

### Proposal-first rule

When a change affects canonical state and is not already an authorized maintenance patch, route it through proposals and decisions. Do not let UI, REST, MCP, or materialized artifact edits mutate canonical state silently.

Current examples:

- reentry from payload/projection/tree inbox creates proposals;
- proposal approval/rejection routes through governance;
- MAP Workbench is read-only and links to governed inspection surfaces;
- MCP `create_proposal` can create proposals, not directly approve them.

### Event and audit discipline

Every relevant mutation to core institutional objects must preserve:

- event trace;
- actor (`performed_by`);
- route/source (`performed_via`);
- target object type/id;
- before/after state or reconstructable version reference where applicable.

Use object history and version comparison endpoints for audit work. Advanced replay and core-vs-materialization comparison remain deferred hardening items.

### Commit and workspace hygiene

Before editing:

```powershell
git status --short
```

Rules:

- Do not stage unrelated files.
- Do not commit pre-existing workspace noise.
- Do not revert user changes unless explicitly asked.
- Do not use destructive git commands.
- Commit one logical unit at a time when commit authority is present.
- If the worktree is too noisy to commit safely, record that in the final report.

Current expected prefixes:

- `[maint]` for maintenance/hardening;
- `[completion]` for post-closure spec-gap work;
- `[phaseN]` only when a human opens a new numbered implementation phase.

### Closure discipline

A slice is complete only when:

- the actual requested work is done;
- relevant checks were run or explicitly skipped with reason;
- coordination artifacts are updated when state changed materially;
- significant execution is logged under `agent/ops/`;
- unresolved drift is recorded;
- no spec or human-owned artifact was edited without authority;
- a clean commit is made when the worktree and authority allow it.

### Escalation triggers

Stop and escalate when:

- a request requires changing `system/00_specs/`;
- the implementation would contradict the spec;
- a runtime change would redefine authority or identity;
- a dependency is required but not explicitly approved;
- a claim would imply hosted, connector-complete, or GA readiness;
- the worktree has conflicting user changes in the same files;
- the requested action requires editing human-owned artifacts without explicit authorization.

Use `agent/ops/` for non-blocking drift/proposals and `agent/ops/BLOCKERS.md` if a blocking escalation artifact is needed.
