# NEXUS — Task Protocol
## Version 0.2 | Phase: build_agent

---

## 1. Task Lifecycle

```
ASSIGNED → IN PROGRESS → BLOCKED | DONE
```

Every task passes through these states. No task is closed without explicit state update.

---

## 2. Receiving a Task

When a task is assigned (either via `agent/CURRENT_MISSION.md` or direct instruction):

1. Read `AGENTS.md`, `WORKSPACE_CONTRACT.md`, `agent/AUTHORITY_MATRIX.md` if not already loaded
2. Read the relevant spec sections referenced in the task
3. Set task status to `IN PROGRESS` in `agent/plan/ACTIVE_TRACK.md`
4. Write a one-line execution plan to the `Execution Log` section of `ACTIVE_TRACK.md`

Do not begin implementation before completing steps 1–4.

---

## 3. Executing a Task

- Work on one slice at a time
- If a decision point arises that is not covered by spec: stop, write to `agent/ops/BLOCKERS.md`, set status to `BLOCKED`
- If a decision is clearly covered by spec: proceed and log the decision in `ACTIVE_TRACK.md`
- Never make Class D mutations (see `AUTHORITY_MATRIX.md §3`) without human gate
- Keep implementation aligned with `BUILD_PROTOCOL.md` at all times

---

## 4. Closing a Task

A task is closed only when:

- [ ] Done criteria from `agent/CURRENT_MISSION.md` are fully met
- [ ] The closure evidence in `agent/plan/DEFINITION_OF_DONE.md` is satisfied
- [ ] `SYSTEM_STATUS.yaml` is updated to reflect the new state
- [ ] `agent/plan/ACTIVE_TRACK.md` is updated: task status → `DONE`, log entry added
- [ ] Changes are committed: `[phase{N}] <description>`

Do not mark done if any criterion is unmet. Partial progress = `IN PROGRESS`, not `DONE`.

---

## 5. Blocking

When blocked:

1. Write to `agent/ops/BLOCKERS.md` (create if absent):
   - Task name
   - What is blocked
   - Why (ambiguous spec / missing dependency / authority limit)
   - What human decision is needed
2. Set task status to `BLOCKED` in `ACTIVE_TRACK.md`
3. Stop. Do not proceed past a blocker by inference.

---

## 6. Proposing Spec Changes

If implementation reveals a gap or contradiction in the specs:

1. Do not modify `system/00_specs/` files
2. Write the proposal to `agent/ops/` as `PROPOSAL_<topic>_<date>.md`:
   - What the spec says (or doesn't say)
   - What the implementation requires
   - Proposed resolution
3. Flag in `ACTIVE_TRACK.md` as a pending proposal
4. Await human decision before proceeding on the affected area

---

## 7. Session Discipline

Each Codex session should:
- Begin with reading orientation files (see `SYSTEM_PROMPT.md`)
- Cover at most 1–2 task slices
- End with a commit and updated `SYSTEM_STATUS.yaml`
- Never leave the repo in an inconsistent state (partial migration, uncommitted schema change, etc.)

---

## 8. Transmutation Handoff

When the handoff criteria in the active mission are met, the build agent prepares transmutation by:

1. Writing `agent/ops/TRANSMUTATION_READY.md` with:
   - Summary of what was built
   - Known gaps or deferred items
   - Recommended first tasks for the maintenance agent
2. Flagging for human review
3. Awaiting explicit human declaration in `AGENTS.md` before changing operating mode
