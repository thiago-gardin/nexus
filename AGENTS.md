
# NEXUS — Agent Orientation File
## Version 0.4 | Phase: maintenance_agent (local-first product ready)

---

## 1. What This Repo Is

This is the Nexus repository. It is simultaneously:
- the **application codebase** (`system/runtime/`);
- the **materialization surface** (`tree/`);
- the **agent coordination layer** (`agent/`);
- the **authoritative specs** (`system/00_specs/` — read-only).

Nexus is a local-first cognitive-operational infrastructure:
- local executable core (SQLite-backed, authoritative);
- materialization regime (`tree/`, legible, versionable);
- human cockpit and agent/MCP surfaces under explicit governance.

---

## 2. Current Phase

**Phase: POST-PRD ACCEPTANCE — Maintenance, Hardening, and Real-Use Operation**

The system is operationally complete under the approved local-first PRD acceptance scope.
The post-closure completion sprint is also complete: `override`, GovernanceRule API exposure, actor-filtered event reads, and minimum version comparison are implemented and tested.

Current product label:

**Ready for local-first operational use and maintenance. Not yet general-availability external product.**

Active work is now maintenance, hardening, real-use ingestion, and usability refinement — not architecture redesign.

Primary deferred items for this phase:
- Separate `GovernanceService` from `core/storage/services.py` into `core/governance/`
- Resolve dual code path in `_apply_approved_proposal` (bypasses `entity_service.update_entity`)
- MCP transport hardening (current adapter is functional; protocol depth is future work)
- Advanced audit functions such as replay and core-vs-materialization comparison
- Cockpit UI hardening beyond the current local operational surface
- External source connectors (email, calendar, chat) — explicitly out of scope until further decision

See `CURRENT_STATE.md` for operative focus.
See `agent/CURRENT_MISSION.md` and `agent/plan/ACTIVE_TRACK.md` for active task state.
See `agent/ops/PRODUCT_READINESS_REVIEW_2026-04-13.md` for the current product/spec readiness assessment.

---

## 3. Agent Lifecycle

| Stage | Status | Trigger |
|---|---|---|
| Build agent | ✅ COMPLETE | Phases 1–20, PRD acceptance closure |
| **Maintenance agent** | **ACTIVE** | Declared by human — this file update |
| Retirement / successor | Future | When system requires architectural revision |

The transmutation from build to maintenance was declared by the human owner on 2026-04-13.

**Maintenance agent authorities (vs build agent):**
- May propose schema patches via `agent/ops/`
- May modify existing core logic via targeted patches only
- May read MCP surface and propose via it
- May NOT make architectural changes without human gate
- May NOT invert executable precedence
- May NOT modify `system/00_specs/` files

---

## 4. Authoritative Specs (read-only)

| File | What it defines |
|---|---|
| `system/00_specs/1.TECH_SPEC_OVERVIEW.md` | Macro architecture and normative principles |
| `system/00_specs/CORE_RUNTIME_SPEC.md` | DB schema, object model, mutation regime, authority matrix |
| `system/00_specs/DOMAIN_AND_PIPELINE_SPEC.md` | Domain contracts, ingestion/typing/reconciliation pipelines |
| `system/00_specs/MATERIALIZATION_AND_TREEFOLDER_SPEC.md` | Materialization model, treefolder structure, reentry |
| `system/00_specs/AGENT_SURFACE_AND_MCP_SPEC.md` | MCP tool set, agent authority, proposal model |
| `system/00_specs/IMPLEMENTATION_ROADMAP_TECHNICAL.md` | Phase order and done criteria |
| `system/00_specs/PRD.md` | Product requirements — acceptance criteria |

---

## 5. Repo Structure

```
nexus/
  agent/                        ← coordination layer (this directory)
    plan/                       ← ACTIVE_TRACK, ROADMAP_ALIGNMENT, DEFINITION_OF_DONE
    ops/                        ← decision records, blockers, proposals, drift records
  system/
    00_specs/                   ← authoritative specs (read-only)
    runtime/
      core/
        storage/                ← db.py, transaction_manager, migrations/, repositories/, services.py
        materialization/        ← treefolder_publisher, operational_projections
        bootstrap/              ← seed data
      mcp/                      ← MCP server adapter (9 normative tools)
      api/
        routers/                ← read, governance, agent_surface, surface (human), pipelines
        dependencies.py
        main.py
      config/settings.py
    tests/
      unit/
      integration/              ← 40 tests as of completion sprint validation
  tree/                         ← materialization surface (treefolder)
  output/                       ← ephemeral tool output (Playwright, etc.) — not committed
  AGENTS.md
  CURRENT_STATE.md
  SYSTEM_STATUS.yaml
  WORKSPACE_CONTRACT.md
  pyproject.toml
  .gitignore
```

---

## 6. Authority Model

| Action | Maintenance Agent |
|---|---|
| Read any file | ✅ |
| Patch `system/runtime/` code | ✅ targeted patches |
| Write `tree/` | ✅ |
| Update `SYSTEM_STATUS.yaml` | ✅ |
| Update `agent/plan/` and `agent/ops/` | ✅ |
| Modify `system/00_specs/` | ❌ — read-only |
| Modify `AGENTS.md` | Human decision only |
| Modify `WORKSPACE_CONTRACT.md` | Human decision only |
| Modify `CURRENT_STATE.md` | Human-owned; direct sync only under explicit human authorization |
| Architectural changes (schema inversion, new object model) | ❌ — human gate required |

---

## 7. Known Hardening Backlog

| Item | Priority | Type |
|---|---|---|
| Separate `GovernanceService` into `core/governance/` | High | Refactor |
| Fix dual code path: `_apply_approved_proposal` → route through `entity_service` | High | Bug risk |
| MCP transport protocol depth | Medium | Hardening |
| Advanced audit replay and core-vs-materialization comparison | Medium | Hardening |
| Cockpit usability hardening after UI-1 | Medium | Product polish |
| External source connectors | Low / deferred | Future scope |

---

## 8. Prohibited Actions

- Do not modify `system/00_specs/` files.
- Do not make architectural changes without human gate.
- Do not mark tasks done without updating `SYSTEM_STATUS.yaml` and `ACTIVE_TRACK.md`.
- Do not hallucinate spec content — flag gaps in `agent/ops/`.
- Do not declare lifecycle changes — human decision only.
