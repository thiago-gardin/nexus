# Phase 4 Surface Decision

Date: 2026-04-10

Decision:
- The new Phase 4 operational surface is read-only HTML on top of the live FastAPI runtime.
- Approve/reject remains on the existing governance API.
- MCP/read-proposal remains out of this sprint.

Rationale:
- This keeps the new surface minimal and avoids duplicating governance mutation logic.
- The surface still satisfies the need for human-readable inspection of domains, proposals, decisions, and history/version trails.
