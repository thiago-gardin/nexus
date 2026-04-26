# Phase 6 Agent Operation Decision

Date: 2026-04-10

Decision:
- The agent-facing surface now supports `entity_update` and `relation_create`.
- Approve/reject remains outside the agent surface and continues to live in the governance API.
- Proposal-from-edit and reentry remain out of this sprint.

Rationale:
- This expands agent utility without letting the agent surface bypass governance.
- The boundary stays explicit: agent surface submits structured proposals, governance performs the only authorized mutation path, and history/versioning remains traceable through the existing runtime.
