# Phase 5 Agent Surface Decision

Date: 2026-04-10

Decision:
- The new Phase 5 agent-facing surface is structured read + proposal only.
- Approve/reject remains outside the agent surface and stays on the governance API.
- MCP/full remote-agent plumbing remains out of this sprint.

Rationale:
- This preserves the separation between read, proposal, and mutation regimes.
- The surface remains minimal while still allowing an agent to inspect live state and submit a controlled entity-update proposal.
