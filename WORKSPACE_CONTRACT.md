# NEXUS — Workspace Contract

## Version 0.4 | Status: maintenance workspace governance

---

## 1. What This Repo Is

This repository is the operative workspace of Nexus.

It contains four distinct but connected layers:

* **authoritative technical specifications** in `system/00_specs/`;
* **agent coordination and governance artifacts** in `agent/`;
* **runtime and application code** in `system/runtime/` and `system/tests/`;
* **published materialization surface** in `tree/`.

There is no separate workspace and no separate application repository.
This repository is the workspace, the runtime host, and the publication surface.

The macro roadmap in `system/00_specs/IMPLEMENTATION_ROADMAP_TECHNICAL.md` is normative, but the execution unit in this workspace is the sprint history tracked in `agent/plan/ACTIVE_TRACK.md` and the macro-to-sprint bridge tracked in `agent/plan/ROADMAP_ALIGNMENT.md`.

Current lifecycle status:

* PRD acceptance closure is complete under approved local-first assumptions.
* The post-closure completion sprint is complete.
* The active mode is maintenance, hardening, real-use ingestion, and product usability refinement.
* Product label: **ready for local-first operational use and maintenance; not yet general-availability external product**.

---

## 2. Stable Artifacts

**Do not modify without explicit human authorization.**

| Path                    | Stability rule                                                                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `system/00_specs/*.md`  | Authoritative technical specifications. They define normative architecture and must not be changed by implementation agents. |
| `AGENTS.md`             | Human-controlled orientation layer. Treat as stable unless a human explicitly authorizes rebasing.                           |
| `WORKSPACE_CONTRACT.md` | Human-controlled workspace constitution. Agents must follow it, not rewrite it autonomously.                                 |

---

## 3. Mutable Artifacts

**Agent may modify these within granted authority and current mission scope.**

| Path                               | Mutability rule                                                                                                            |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `system/runtime/`                  | Full implementation authority within current mission and spec boundaries.                                                  |
| `system/tests/`                    | Full authority for adding or updating tests that validate implemented behavior.                                            |
| `tree/`                            | Materialization output surface. Agent may write or regenerate per the current executable state and publication regime.     |
| `SYSTEM_STATUS.yaml`               | Must be updated after meaningful state change and before closing a slice.                                                  |
| `agent/CURRENT_MISSION.md`         | Must reflect the active mission; update when mission is completed, superseded, or rebased.                                 |
| `agent/plan/ACTIVE_TRACK.md`       | Must be updated during execution and at slice closure.                                                                     |
| `agent/plan/DEFINITION_OF_DONE.md` | Mutable governance artifact; update only when improving execution discipline or closure criteria within current authority. |
| `agent/plan/ROADMAP_ALIGNMENT.md`  | Mutable governance artifact mapping the macro roadmap to executed sprints.                                                |
| `agent/ops/`                       | Write proposals, blockers, drift notices, phase boundary notes, and authority-safe escalation artifacts here.              |
| `README.md`                        | Mutable when necessary to keep the repository entrypoint coherent with the actual operational state.                       |
| `CURRENT_STATE.md`                 | Human-owned. Agent must not edit directly unless explicit authorization is given; use `agent/ops/` proposals instead.      |

---

## 4. Maintenance Authority

| Mutation class                                                                          | Rule                                                                |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Runtime scaffolding and implementation code                                             | Not active default; new build programs require a mission decision   |
| Spec-consistent schema creation or extension                                            | Maintenance patch only; broader schema work requires human gate     |
| Schema or runtime decisions not clearly covered by spec                                 | Allowed only if conservative and explicitly flagged in `agent/ops/` |
| Spec changes                                                                            | Prohibited; propose via `agent/ops/` for human review               |
| Changes to `AGENTS.md` or `WORKSPACE_CONTRACT.md`                                       | Human authorization required                                        |
| Changes to human-owned status artifacts outside explicit authority                      | Prohibited; propose via `agent/ops/`                                |
| Critical mutations that alter authority, governance regime, or institutional boundaries | Human decision only                                                 |

---

## 5. Commit Discipline

* Commit messages must use the active work prefix:
  **`[maint] <what was done>`** for maintenance/hardening,
  **`[completion] <what was done>`** for post-closure spec-gap closure,
  or **`[phaseN] <what was done>`** only when a human opens a new numbered implementation phase.
* One logical unit per commit.
* `SYSTEM_STATUS.yaml` must be synchronized before closing a slice that changes real repository state.
* A slice is not considered closed if its relevant state remains uncommitted.
* Pre-existing unrelated workspace noise must not be silently absorbed into the commit.
* If a slice cannot be cleanly committed because of authority or workspace drift, record that explicitly in `agent/ops/`.

---

## 6. Closure Discipline

A slice may be marked `DONE` only when all of the following are true:

* implementation or governance work for the slice is actually complete;
* the relevant verification has been executed;
* mutable coordination artifacts have been synchronized;
* unresolved drift in stable or human-owned artifacts has been explicitly recorded in `agent/ops/`;
* the slice satisfies the active `agent/plan/DEFINITION_OF_DONE.md`;
* the resulting state is committed, unless the mission is documentation-only and commit authority is intentionally withheld or the file is human-owned/untracked and must be handed off explicitly.

---

## 7. Escalation

Escalate for human review when:

* a spec element is ambiguous, contradictory, or operationally stale;
* a governance artifact materially diverges from implemented reality;
* a schema or runtime decision is not sufficiently covered by the authoritative specs;
* a proposed action would cross authority boundaries;
* a phase boundary or definition of done requires human ratification;
* any action falls into critical mutation territory.
* readiness claims would imply hosted, connector-complete, or general-availability product status.

Primary escalation location:

* `agent/ops/BLOCKERS.md` for blocking issues;
* other clearly named artifacts in `agent/ops/` for proposals, drift notes, and phase-boundary records.

---

## 8. Operational Principle

The repository must remain institutionally legible.

Implementation may advance incrementally, but the agent must not allow:

* stable specs to drift silently from runtime reality;
* coordination artifacts to present obsolete phase status as current truth;
* publication artifacts to imply authority they do not possess.

The executable core remains primary truth.
Materialized artifacts remain published truth.
Coordination artifacts remain governance truth about current work.
