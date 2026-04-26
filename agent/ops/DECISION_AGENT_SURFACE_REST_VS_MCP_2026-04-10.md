# Decision: REST/local agent surface is current contract, MCP is future compatibility target
## Date: 2026-04-10 | Scope: agent-surface alignment

## Update

This decision records the Phase 13 state.

It is superseded for transport-status purposes by the Phase 14 implementation slice, which initializes a formal MCP adapter over the existing services while preserving REST/local as the operational contract.

Current status is tracked in `SYSTEM_STATUS.yaml` and `agent/CURRENT_MISSION.md`.

## Current contract

The agent-facing surface in this repository is the `/agent/*` REST surface built on FastAPI.
At the time of this decision, that surface was the only operational agent contract used by the workspace.

## Semantic equivalence

The REST surface preserves the object-space semantics called for by `system/00_specs/AGENT_SURFACE_AND_MCP_SPEC.md`:

- read routes cover the `get_domain`, `get_entity`, `get_relation`, `get_payload`, `search_objects`, and `get_projection` intents;
- proposal routes cover `create_proposal` and the current proposal families;
- queue and history routes cover `get_decision_queue` and `explain_object` intents;
- the same object identities, history trails, and proposal/decision linkages are exposed through the local surface.

## Protocol deviations at decision time

At Phase 13, the implementation was not a formal MCP server.

- there is no MCP transport;
- there is no tool-call handshake;
- there is no registered MCP tool manifest;
- `SYSTEM_STATUS.yaml` therefore remained correct at that time in reporting `mcp_server_status: not_initialized` and `tools_registered: 0`;
- the surface is repository-local and FastAPI-native, not protocol-neutral.

## Why this was acceptable now

- the workspace is local-first and does not need a new transport layer to remain operational;
- REST keeps the surface testable, auditable, and easy to evolve alongside the runtime;
- the spec-level semantics are preserved even though the wire protocol is not MCP;
- introducing MCP now would add infrastructure cost without improving the current build outcome.

## Thesis

REST/local is the current contract.
MCP was a future compatibility target at the time of this decision.
This is an intermediate institutional contract, not a rejection of MCP and not a redesign of the architecture.

## Roadmap implications

- spec items that reference an agent surface should be read as semantically satisfied only where the current REST/local surface covers the same object-space behavior;
- formal MCP remained an open gap for the Phase 13 slice and was tracked separately from runtime feature work;
- any future MCP work should be implemented as an adapter or bridge over the existing local contract unless a human explicitly chooses a different path.

## Status

Accepted for the Phase 13 build era.
No MCP-native server was created in that slice.
Phase 14 supersedes the transport-status portion by adding the adapter and smoke test.
