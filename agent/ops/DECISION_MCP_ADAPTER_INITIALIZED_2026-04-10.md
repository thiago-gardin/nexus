# Decision: MCP Adapter Initialized Over REST/Service Contract
## Date: 2026-04-10 | Scope: Phase 14 Spec Completion Program

## Decision

Nexus now includes a formal MCP adapter over the current local runtime services.

REST/local remains the operational contract for local API and cockpit use. MCP is a protocol adapter over the same service layer, not a replacement for the existing REST/local surface and not an architectural redesign.

## Implemented Tool Surface

The MCP adapter exposes exactly the normative tool names:

- `get_domain`
- `get_entity`
- `get_relation`
- `get_payload`
- `search_objects`
- `get_projection`
- `create_proposal`
- `get_decision_queue`
- `explain_object`

## Verification

Smoke test executed:

```text
python -m unittest system.tests.integration.test_prd_completion -v
```

The test `test_mcp_server_smoke_lists_normative_tools` builds the MCP server and verifies that `list_tools()` returns exactly those 9 names.

The full regression suite also passed:

```text
python -m unittest discover -s system/tests -v
```

## Status Implication

`SYSTEM_STATUS.yaml` may now report:

```yaml
agent_surface:
  mcp_server_status: initialized
  tools_registered: 9
```

This does not claim full PRD closure. It only closes the transport-status gap identified in the Phase 13 REST vs MCP decision record.
