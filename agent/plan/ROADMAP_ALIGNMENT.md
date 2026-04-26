# NEXUS — Roadmap Alignment
## 2026-04-10

This artifact maps the normative macro phases in `system/00_specs/IMPLEMENTATION_ROADMAP_TECHNICAL.md` to the sprint history that actually exists in this repository.

It is descriptive, not normative.
The macro roadmap remains authoritative for intent, but the repo's execution history is more granular and must be read through `agent/plan/ACTIVE_TRACK.md`.

## Macro Phases vs Real Sprints

| Macro phase | Normative intent from spec | Real sprint range in repo | Current state | Remaining gaps |
|---|---|---|---|---|
| Phase 1 | Minimum executable core: local DB, central tables, domain registration, basic ingestion, entity/relation/event persistence, minimum payload refs, simple materialization | Sprints 1-8 | Complete | No material runtime gap remains in the bootstrap core slice |
| Phase 2 | Minimum governance: decision queue, approval engine, rules registry, object versioning, minimum reentry rule | Sprints 9-14 | Complete | Governance is operational; remaining work is coordination and future hardening, not the minimum phase deliverable |
| Phase 3 | Operational materialization regime: payload store, stable projections, legible diffs, proposal-from-edit support, semantic exports, remote-readable treefolder | Sprints 15-18 | Complete | No current gap against the minimum phase deliverable |
| Phase 4 | Human and agent surfaces: minimum human cockpit, read/proposal MCP surface, payload/projection viewers, decision and reentry queues | Sprints 19-38 plus Phase 14 and Phase 17-18 slices | Complete under local-first assumptions | REST/local remains operational; MCP is initialized and real-call tested as a formal adapter over current services; cockpit is FastAPI/Jinja/local JS, not a separate frontend |
| Phase 5 | Advanced reconciliation and projections: improved matching, canonicalization refinement, meeting/project projections, improved history and diffs, full review loops | Sprints 39-54 plus Phase 14-19 slices | Complete for PRD acceptance under approved scope | Alias/scored merge and separation proposals, meeting/project projections, tree inbox proposal import, and audit reconstruction exist; full semantic canonicalization and external connectors remain explicitly not claimed |

## Local Sprint Decomposition

The repo's execution history is intentionally finer-grained than the macro roadmap:

- Sprints 1-8: runtime core bootstrap and persistence foundation;
- Sprints 9-14: governance minimum and traceability;
- Sprints 15-18: treefolder publication and object views;
- Sprints 19-22: human surface;
- Sprints 23-34: agent surface, structured reads, proposals, and circulation;
- Sprints 35-38: human review queue and approve/reject loop;
- Sprints 39-46: proposal-from-edit and controlled reentry;
- Sprints 47-54: operational projections and actionable queues;
- Sprints 60-67: PRD completion foundation for object services, generic ingestion, minimum typing/reconciliation, payload/projection/materialization/reentry APIs, MCP adapter, cockpit graph, and regression coverage.
- Sprints 68-74: PRD acceptance closure across pipeline jobs, scored reconciliation, meeting/project projections, treefolder expansion, modular cockpit, tree inbox imports, real MCP calls, multi-domain acceptance, and governance closure.
- Sprints 75-80: post-closure completion sprint closing remaining spec gaps for override semantics, GovernanceRule API exposure, actor-filtered event reads, minimum version comparison, and agent manifest/read-route reflection.
- Sprints 81-85: product/spec readiness review and governance documentation synchronization.
- Sprints 86-92: Day 0 operational control plane baseline for domain versions, source registration, authoring, cockpit actions, local MCP operation, materialized charters/sources/runs, and Work/Mail templates.

## Post-Roadmap Institutional Slices

The repository now has additional governance-oriented slices beyond the macro roadmap:

- Sprints 55-59: definition of done, governance doc alignment, REST vs MCP decision record, macro-roadmap alignment artifact, and coordination sync.
- Sprints 60-74: Phase 14-20 Spec Completion Program and PRD acceptance closure under the approved local-first assumptions.
- Sprints 75-85: post-closure spec gap closure, product readiness review, and governance synchronization.

Sprints 55-59 did not add new runtime capabilities. Sprints 60-74 add runtime/API/surface/MCP/materialization capability and should be read as the PRD acceptance closure sequence, not as a claim that out-of-scope external connectors or a full semantic canonicalization engine were implemented.
Sprints 75-80 close narrow post-closure spec gaps and should be read as completion hardening, not a new subsystem.
Sprints 81-85 are governance/product-readiness synchronization and do not modify normative specs.
Sprints 86-92 add a local Day 0 control plane as maintenance/product-readiness work. They do not claim external connector completion, PST parsing, hosted product readiness, or full semantic canonicalization.

## Current Reading

- Macro Phases 1-3 are complete in practice.
- Macro Phase 4 is complete for the approved local-first PRD acceptance scope: human cockpit modules and formal MCP adapter now exist over the local runtime.
- Macro Phase 5 is complete for the approved local-first PRD acceptance scope: scored reconciliation, separation proposals, meeting/project projections, reentry, tree inbox import, and audit reconstruction are covered.
- Residual drift is explicit: external connectors and a full semantic canonicalization engine remain not claimed.
- The latest completed work is the 2026-04-21 Day 0 operational control plane baseline after the 2026-04-13 product readiness review.
- Product status is ready for local-first operational use and maintenance; hosted, connector-complete, or general-availability readiness is not claimed.
