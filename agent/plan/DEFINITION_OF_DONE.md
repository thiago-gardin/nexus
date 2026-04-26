# NEXUS — Definition of Done

## Version 0.2 | 2026-04-10

This document defines the minimum evidence required before a **slice**, **mission**, or **phase** can be closed as `DONE`.

It exists to prevent false closure by narrative momentum, partial implementation, or unsynchronized governance.

---

## 1. Scope

This Definition of Done applies to:

* implementation slices;
* governance alignment slices;
* docs-only synchronization slices;
* refactor / hardening slices;
* materialization / publication slices;
* handoff packaging for the next slice;
* mission-level and phase-level closure.

---

## 2. Core Principle

Work is not done because code exists.

Work is done only when:

* the intended change is actually complete;
* the relevant state is verified;
* the operational governance artifacts reflect the same reality;
* unresolved drift is surfaced explicitly;
* closure is evidenced, not implied.

---

## 3. Slice Types

Different slices require different emphasis.

### 3.1 Implementation slice

Examples:

* runtime code;
* API behavior;
* schema or repository logic;
* surface behavior.

Primary requirement:

* behavior implemented and verified.

### 3.2 Governance slice

Examples:

* mission rebasing;
* authority clarifications;
* status synchronization;
* explicit boundary decisions.

Primary requirement:

* coordination artifacts reflect reality and authority boundaries remain clear.

### 3.3 Docs-only synchronization slice

Examples:

* README sync;
* status narrative updates;
* phase labeling alignment.

Primary requirement:

* documentation reflects implemented state without overstating it.

### 3.4 Refactor / hardening slice

Examples:

* service separation;
* code path convergence;
* cleanup of duplicate mutation logic.

Primary requirement:

* behavior preserved, drift reduced, no regression introduced.

### 3.5 Materialization / publication slice

Examples:

* treefolder updates;
* projection publishing;
* published trace enhancements.

Primary requirement:

* published artifacts remain derived from executable state and are reproducible.

---

## 4. Slice-Level Done

A slice is `DONE` only when all applicable conditions below are satisfied.

### 4.1 Mission fit

* the slice satisfies the relevant part of the active mission;
* the result is materially aligned with the intended slice scope;
* anything intentionally left out is explicitly stated.

### 4.2 Verification

* the relevant validation has been executed;
* the validation method is appropriate to the slice type;
* results are known, not assumed.

Examples:

* tests for runtime behavior;
* publication check for tree artifacts;
* diff review for docs/governance slices;
* regression check for refactors.

### 4.3 Coordination sync

* `agent/plan/ACTIVE_TRACK.md` reflects the slice as actually executed;
* `SYSTEM_STATUS.yaml` reflects the resulting repository state when meaningful state changed;
* `agent/CURRENT_MISSION.md` remains coherent with the active mission.

### 4.4 Drift handling

* any drift in immutable or human-owned artifacts is captured in `agent/ops/`;
* no known material contradiction is left implicit;
* if the agent cannot edit the authoritative or human-owned file, the gap is recorded as proposal or blocker.

### 4.5 Commit discipline

* a commit exists when the slice changed repository content;
* the commit represents one logical unit;
* unrelated workspace noise was not silently absorbed.

### 4.6 Evidence

* evidence of closure is recorded and recoverable.

---

## 5. Mission-Level Done

A mission is `DONE` only when:

* all intended slices for that mission are complete or explicitly deferred;
* the current mission statement matches what was actually executed;
* all relevant slice evidence exists;
* the repo state is coherent enough that the next mission can begin without hidden ambiguity;
* known unresolved gaps are explicitly parked in `agent/ops/` or the active track.

A mission is **not** done if the runtime moved but the governance layer still materially describes an older state.

---

## 6. Phase-Level Done

A phase is `DONE` only when:

* its intended capability threshold has been reached in practice, not only in code fragments;
* the active track shows the phase as complete with evidence;
* the state snapshot and mission layer no longer present the phase as active work;
* any remaining work has been explicitly rebased into the next phase.

A phase is **not** done merely because one or two representative tasks were completed.

---

## 7. Repo-Level Operational Done

The repo is operationally coherent for a mission or phase only when:

* `SYSTEM_STATUS.yaml` matches the live build state;
* `agent/CURRENT_MISSION.md` matches the active mission;
* `agent/plan/ACTIVE_TRACK.md` matches the active slice or current phase focus;
* published `tree/` artifacts remain derived from executable state;
* surfaces do not imply authority they do not possess;
* human-owned or immutable drift has an explicit proposal path;
* no material governance artifact silently contradicts the implemented runtime.

---

## 8. Anti-Drift Rule

A slice, mission, or phase must not be closed as `DONE` when the coordination layer materially misrepresents the implemented system, unless:

* the mismatch is explicitly captured in `agent/ops/`; and
* the remaining gap is outside the agent’s authority to fix directly.

This rule exists to prevent “implemented but institutionally false” closure.

---

## 9. Evidence Checklist

Every closed slice should leave enough evidence to reconstruct what happened.

Minimum evidence:

* command(s) run;
* validation or test result;
* paths changed;
* proposal or blocker artifact if drift was found;
* commit hash, or explicit handoff note if no commit was appropriate;
* explicit note of what was left out, when relevant.

---

## 10. Authority-Sensitive Policy Points

* `CURRENT_STATE.md` is human-owned and must be synchronized by proposal, not silent agent edit.
* `AGENTS.md` and `WORKSPACE_CONTRACT.md` are immutable unless explicit human authorization is given.
* if stable or human-owned artifacts drift from implemented reality, the gap belongs in `agent/ops/`.
* lack of authority to edit a file does **not** excuse silent inconsistency; it requires explicit recording.

---

## 11. Practical Closure Formula

Before marking `DONE`, verify:

1. **Built** — the slice actually exists in code or governance artifacts.
2. **Verified** — the relevant checks were run.
3. **Synchronized** — mutable coordination artifacts reflect the same state.
4. **Escalated** — immutable or human-owned drift was explicitly surfaced.
5. **Committed** — the logical unit was recorded cleanly when repo content changed.

If one of these is missing, the slice is not done yet.
