# NEXUS — Active Track
## Maintenance Readiness Sync | Updated: 2026-04-24

---

## Completed Slice

**Sprint: Phase 20 — PRD Acceptance Closure**
Status: DONE

---

## Task Queue

| # | Task | Status | Blocker |
|---|---|---|---|
| 1 | Project scaffold and config | DONE | — |
| 2 | Database and migrations (14 tables) | DONE | — |
| 3 | Core repositories | DONE | — |
| 4 | Event emission | DONE | — |
| 5 | Core read API | DONE | — |
| 6 | Treefolder skeleton | DONE | — |
| 7 | Workspace status sync + commit | DONE | — |
| 8 | First seeded domain and end-to-end publication | DONE | — |
| 9 | Minimal governance proposal and decision flow | DONE | — |
| 10 | Minimal governance API surface | DONE | — |
| 11 | Governance model hardening | DONE | — |
| 12 | History and traceability clarity | DONE | — |
| 13 | Reentry decision | DONE | — |
| 14 | Verification and coordination sync | DONE | — |
| 15 | Treefolder publication enrichment | DONE | — |
| 16 | Minimal published object views | DONE | — |
| 17 | Proposal-from-edit decision | DONE | — |
| 18 | Verification and coordination sync | DONE | — |
| 19 | Minimal human surface router | DONE | — |
| 20 | Live inspection pages | DONE | — |
| 21 | Surface verification | DONE | — |
| 22 | Coordination sync and closure | DONE | — |
| 23 | Agent surface router | DONE | — |
| 24 | Structured reads | DONE | — |
| 25 | Structured proposal submission | DONE | — |
| 26 | Verification and coordination sync | DONE | — |
| 27 | Agent surface expansion | DONE | — |
| 28 | Capability manifest hardening | DONE | — |
| 29 | Reentry and approve/reject boundaries | DONE | — |
| 30 | Verification and coordination sync | DONE | — |
| 31 | Circulation trace publication | DONE | — |
| 32 | Agent publication read route | DONE | — |
| 33 | Boundary decisions | DONE | — |
| 34 | Verification and coordination sync | DONE | — |
| 35 | Human review queue | DONE | — |
| 36 | Gated human approve/reject | DONE | — |
| 37 | Explicit limits | DONE | — |
| 38 | Verification and coordination sync | DONE | — |
| 39 | Eligible edit case | DONE | — |
| 40 | Edit-to-proposal conversion | DONE | — |
| 41 | Explicit limits | DONE | — |
| 42 | Verification and coordination sync | DONE | — |
| 43 | Editability contract | DONE | — |
| 44 | Second eligible case | DONE | — |
| 45 | Explicit limits | DONE | — |
| 46 | Verification and coordination sync | DONE | — |
| 47 | Projection contract | DONE | — |
| 48 | Projection publication | DONE | — |
| 49 | Surface navigation | DONE | — |
| 50 | Verification and coordination sync | DONE | — |
| 51 | Actionable queue contract | DONE | — |
| 52 | Projection publication | DONE | — |
| 53 | Surface navigation | DONE | — |
| 54 | Verification and coordination sync | DONE | — |
| 55 | Definition of done draft | DONE | — |
| 56 | Governance doc alignment | DONE | — |
| 57 | REST vs MCP decision record | DONE | — |
| 58 | Roadmap alignment artifact | DONE | — |
| 59 | Verification and coordination sync | DONE | — |

---

## Previous Completed Slice

**Sprint: Phase 20 — PRD Acceptance Closure**
Status: DONE

**Program status:** DONE under approved local-first PRD assumptions

| # | Task | Status | Blocker |
|---|---|---|---|
| 60 | Source/payload/projection/rule/job repositories and services | DONE | — |
| 61 | Generic ingest endpoint with raw/parsed payload persistence | DONE | — |
| 62 | Minimum typing and duplicate reconciliation proposals | DONE | — |
| 63 | Read/search/materialization/export/reentry APIs | DONE | — |
| 64 | Formal MCP adapter with 9 normative tools | DONE | — |
| 65 | Cockpit graph endpoint and local Jinja/JS page | DONE | — |
| 66 | Integration tests and full system regression run | DONE | — |
| 67 | Governance sync and residual PRD gap record | DONE | — |
| 68 | Full PRD acceptance closure across remaining Phase 15-20 targets | DONE | — |
| 69 | Pipeline jobs plus alias/scored merge and separation reconciliation | DONE | — |
| 70 | Meeting/project projections and treefolder indexes | DONE | — |
| 71 | Modular cockpit panels and graph filters | DONE | — |
| 72 | Tree inbox proposal import and MCP real-call hardening | DONE | — |
| 73 | Multi-domain PRD acceptance scenario | DONE | — |
| 74 | Governance closure docs and residual drift record | DONE | — |

---

## Previous Completed Slice

**Sprint: Post-Closure Completion Sprint — Spec Gap Closure**
Status: DONE

**Program status:** DONE; Phase 20 acceptance remains the baseline, with post-closure spec gaps patched and verified.

| # | Task | Status | Blocker |
|---|---|---|---|
| 75 | Verify `GovernanceService.override()` and harden pending-decision semantics | DONE | — |
| 76 | Expose GovernanceRule create/read/status API | DONE | — |
| 77 | Add actor-based event filtering to service, repository, REST, and agent surface | DONE | — |
| 78 | Expose minimum object version comparison for audit | DONE | — |
| 79 | Update agent manifest and agent read routes for rules, actor events, and compare | DONE | — |
| 80 | Run full regression and synchronize coordination status | DONE | — |

---

## Current Slice

**Sprint: Product Readiness Review and Governance Sync**
Status: DONE

**Program status:** Nexus is ready for local-first operational use and maintenance; external/general-availability product readiness is not claimed.

| # | Task | Status | Blocker |
|---|---|---|---|
| 81 | Evaluate Nexus as product against approved local-first PRD scope | DONE | — |
| 82 | Evaluate Nexus implementation against read-only specs | DONE | — |
| 83 | Record readiness review and residual limits in `agent/ops/` | DONE | — |
| 84 | Rebaseline governance docs to maintenance/product-ready state | DONE | — |
| 85 | Validate textual/YAML coherence and regression baseline | DONE | — |

---

## Active Implementation Slice

**Sprint: Day 0 Operational Control Plane Baseline**
Status: DONE

**Program status:** Minimum Day 0 local operation is implemented across API/core, cockpit, MCP local profile, materialization, and tests. The slice is closed as a maintenance/product-readiness unit; unrelated pre-existing worktree drift remains outside this slice.

| # | Task | Status | Blocker |
|---|---|---|---|
| 86 | Harden authoring API/core around source registration, object validation, and domain version activation | DONE | — |
| 87 | Materialize domain charters, source indexes, ingestion run indexes, and authoring summaries | DONE | — |
| 88 | Add cockpit action panel for domain/version/source/ingestion/entity/relation/validate/reject | DONE | — |
| 89 | Add explicit MCP `local_operator` profile while preserving default 9-tool restricted profile | DONE | — |
| 90 | Add Day 0 Work and Mail domain templates | DONE | — |
| 91 | Add integration tests for Day 0 operational control plane | DONE | — |
| 92 | Synchronize `SYSTEM_STATUS.yaml`, `ACTIVE_TRACK.md`, and `agent/ops/` log | DONE | — |

---

## Execution Log

- 2026-04-09: start Task 1 by scaffolding `system/runtime/`, initializing `pyproject.toml`, and adding a minimal FastAPI app plus config settings.
- 2026-04-09: completed Task 1 after py_compile, import, and uvicorn health smoke verified the runtime entry point.
- 2026-04-09: start Task 2 by implementing the SQLite storage layer, 14-table migrations, and transaction manager.
- 2026-04-09: completed Task 2 after unittest verified the 14-table migrations, idempotence, and transaction rollback/commit behavior.
- 2026-04-09: start Task 3 by adding persistence repositories and service-layer event emission for Domain, Entity, Relation, and Event.
- 2026-04-09: completed Task 3 after unittest verified domain registration/retrieval, entity and relation create/update event emission, and stable IDs.
- 2026-04-09: reconciled Task 4 as already implemented in Task 3 after code/test inspection; starting Task 6 to materialize the minimum treefolder skeleton from executable state.
- 2026-04-09: completed Task 6 after publishing the treefolder skeleton from executable state and verifying the generated root files, domain publication flow, and repeatable publication.
- 2026-04-09: start Task 5 by exposing minimal read-only HTTP endpoints for the executable core via FastAPI and wiring the runtime context through app startup.
- 2026-04-09: completed Task 5 after verifying the FastAPI health/read endpoints against a live SQLite runtime and persisted core objects.
- 2026-04-10: start Task 8 by bootstrapping the first real domain in the executable DB and republishing the treefolder from live state.
- 2026-04-10: completed Task 8 after verifying the seeded domain in the DB, API, and published treefolder.
- 2026-04-10: completed Task 7 after syncing the root status and closing the coordination slice in the tracker.
- 2026-04-10: start Task 9 by adding the minimum proposal/decision flow for entity updates and relation edits.
- 2026-04-10: completed Task 9 after verifying proposal creation, approval/rejection state transitions, object versioning, and decision events.
- 2026-04-10: start Task 10 by exposing the minimum governance API surface over the existing proposal/decision flow.
- 2026-04-10: completed Task 10 after verifying proposal and decision HTTP endpoints, approve/reject behavior, and object history access.
- 2026-04-10: start Phase 2 governance minimum closure sprint by hardening proposal types, queue semantics, history readability, and the explicit reentry decision.
- 2026-04-10: completed Phase 2 governance minimum closure sprint after explicit proposal-type validation, legible history envelopes, reentry-out-of-sprint documentation, and full governance test verification.
- 2026-04-10: start Phase 3 operational materialization sprint by enriching treefolder publication, publishing minimum object views, and explicitly deferring proposal-from-edit.
- 2026-04-10: completed Phase 3 operational materialization sprint after publishing legible domain/object views, proving repeatable publication, and recording proposal-from-edit as out of scope.
- 2026-04-10: start Phase 4 minimal operational surfaces sprint by adding a read-only human surface over the live runtime and explicitly leaving MCP/read-proposal out of scope.
- 2026-04-10: completed Phase 4 minimal operational surfaces sprint after adding the read-only HTML surface, linking live domain/proposal/decision/history inspection, and verifying the full system test suite.
- 2026-04-10: start Phase 5 minimal agent-facing surface sprint by adding a dedicated agent router with structured reads and one controlled proposal submission path.
- 2026-04-10: completed Phase 5 minimal agent-facing surface sprint after adding the structured agent router, the controlled entity-update proposal path, tree publication reads, and full system test verification.
- 2026-04-10: start Phase 6 minimal agent operation sprint by expanding the agent surface to a second proposal type while keeping approve/reject and reentry outside the surface.
- 2026-04-10: completed Phase 6 minimal agent operation sprint after adding relation_create proposal submission, contract clarity, and full system test verification.
- 2026-04-10: start Phase 7 controlled circulation sprint by reflecting approved agent proposals in published governance traces and exposing a minimal agent read route for the published trace.
- 2026-04-10: completed Phase 7 controlled circulation sprint after approving an agent-originated entity update, publishing the governance trace into treefolder, and verifying the end-to-end circulation path.
- 2026-04-10: start Phase 8 human review loop sprint by expanding the human surface into a gated review surface over proposals, decisions, and history.
- 2026-04-10: completed Phase 8 human review loop sprint after wiring approve/reject into the existing governance service, exposing the review bundle on the human surface, and verifying the full system test suite.
- 2026-04-10: start Phase 9 proposal-from-edit sprint by opening a controlled proposal path from published entity snapshots into governance.
- 2026-04-10: completed Phase 9 proposal-from-edit sprint after adding the entity short_description proposal-from-edit path, preserving source-artifact traceability, and verifying the full system test suite.
- 2026-04-10: start Phase 10 controlled reentry sprint by generalizing the proposal-from-edit contract to relation validation_status alongside entity short_description.
- 2026-04-10: completed Phase 10 controlled reentry sprint after adding the relation validation_status proposal-from-edit path, preserving source-artifact traceability, and verifying the full system test suite.
- 2026-04-10: start Phase 11 operational projections sprint by adding live domain summary and review queue projections derived from executable state.
- 2026-04-10: completed Phase 11 operational projections sprint after publishing live domain operational summary and review queue projections from executable state and verifying the full system test suite.
- 2026-04-10: start Phase 12 actionable operational queues sprint by adding active decision queues and recent changes views derived from executable state.
- 2026-04-10: completed Phase 12 actionable operational queues sprint after publishing active decision queue and recent changes views from executable state and verifying the full system test suite.
- 2026-04-10: start Phase 13 institutional realignment slice by rebaselining governance docs, recording the REST/local agent surface contract, and mapping the macro roadmap to the sprint history that actually exists in this repository.
- 2026-04-10: completed Task 59 after verifying the active governance docs, `SYSTEM_STATUS.yaml`, and the published tree state remained coherent, and after recording the remaining human-owned current-state drift in `agent/ops/`.
- 2026-04-10: completed Phase 14 foundation slice after adding schema-backed object services, generic local ingestion, minimum typing/reconciliation, payload/projection/materialization/reentry APIs, formal MCP adapter smoke-tested against 9 tools, a local cockpit graph, and full system test verification (`python -m unittest discover -s system/tests -v`).
- 2026-04-10: completed Phase 15 after wiring ingestion/materialization/reentry jobs, exposing reconciliation candidate groups with scores, adding alias-based merge proposals and separation proposals, and verifying the full system test suite.
- 2026-04-10: completed Phase 16 after adding meeting-context and project-state materialization endpoints, expanding `tree/` with payload indexes, projection indexes, canonical indexes and DB-derived proposal inbox artifacts, and verifying the full system test suite.
- 2026-04-10: completed Phase 17 after adding object inspector, payload viewer, projection panel, event timeline, reentry parse-diff panel, graph filters, and verifying the full system test suite.
- 2026-04-10: completed Phase 18 after adding `POST /reentry/from-tree-inbox`, deduplicating imports with `tree-proposal:<relative_path>`, adding real MCP calls for all 9 normative tools, and verifying the full system test suite.
- 2026-04-10: completed Phase 19 after adding a multi-domain PRD acceptance scenario covering local `json/md/txt` ingestion, reconciliation, human approval, versioning, projection, `tree/`, MCP, cockpit, and audit reconstruction.
- 2026-04-10: completed Phase 20 governance closure after synchronizing `agent/CURRENT_MISSION.md`, `agent/plan/ACTIVE_TRACK.md`, `SYSTEM_STATUS.yaml`, `agent/plan/ROADMAP_ALIGNMENT.md`, recording residual drift in `agent/ops/`, and preserving `CURRENT_STATE.md` as human-owned.
- 2026-04-13: started post-closure completion sprint after verifying `GovernanceService.override()` already existed, governance rule routes were absent, `EventRepository.list()` lacked `performed_by`, and `compare_versions` was absent.
- 2026-04-13: completed post-closure completion sprint after adding GovernanceRule API exposure, actor-filtered event reads, minimum object version comparison, agent manifest/read-route updates, override pending-state hardening, and full regression verification (`python -m unittest discover -s system/tests -t . -p "test_*.py"`; 40 tests passed).
- 2026-04-13: completed product readiness review and governance synchronization after recording `agent/ops/PRODUCT_READINESS_REVIEW_2026-04-13.md`, rebasing governance docs to maintenance/product-ready state, and preserving the limits against external/general-availability readiness.
- 2026-04-21: completed the Day 0 operational control plane baseline after hardening authoring source registration and object validation, adding cockpit action panel, MCP `local_operator` profile, Day 0 Work/Mail templates, materialization for charters/sources/runs/authoring summaries, and verifying full regression (`python -m unittest discover -s system/tests -t . -p "test_*.py"`; 45 tests passed). Commit performed with explicit slice paths only; unrelated pre-existing worktree drift remains outside this closure.
- 2026-04-23: completed the Operate Workspace v1 slice after replacing the isolated cockpit action panel with a context-preserving operate surface, adding inline receipt/error handling, explicit materialization control, agent/MCP operate-context reads, MCP import fallback hardening for the local test environment, and verifying full regression (`python -m unittest discover -s system/tests -t . -p "test_*.py"`; 45 tests passed).
- 2026-04-24: completed the Unified Workbench v1 slice after converging `/surface/operate` and `/surface/graph` into the same cockpit shell, replacing exposed action cards with an action drawer, adding human-oriented automatic ID suggestion, label-based dependency pickers, inferred schema-driven entity forms, and keeping inspector/event/publication context visible in the same workflow. Full regression remained green (`python -m unittest discover -s system/tests -t . -p "test_*.py"`; 45 tests passed).

---

## Current Implementation Slice

**Sprint: Unified Workbench v1**
Status: DONE

**Program status:** The Day 0 control plane now runs through a shared graph/operate workbench with human-usable action entry, label-based selection, schema-driven forms, and visible inspection/publication context.

| # | Task | Status | Blocker |
|---|---|---|---|
| 100 | Consolidate `/surface/operate` and `/surface/graph` into a shared cockpit workbench shell | DONE | — |
| 101 | Replace exposed `ActionCard` layout with an action drawer tied to workspace context | DONE | — |
| 102 | Add automatic ID suggestion and remove raw ID dependence from main human flow | DONE | — |
| 103 | Add label-based pickers for entities, relations, and review targets | DONE | — |
| 104 | Render dynamic human forms from inferred domain `ui_schema` instead of raw JSON fields | DONE | — |
| 105 | Keep inspector, event stream, decision queue, and publication state in the same operational surface | DONE | — |
| 106 | Re-run full regression and sync governance docs/logs | DONE | — |

---

## Blockers

- No active blockers for the Day 0 operational control plane baseline.
- Pre-existing unrelated worktree drift remains outside this slice and must not be committed broadly without separate review.
