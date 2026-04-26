# Operate Workspace v1 Slice
## Date
2026-04-23

## Scope

Implement the first UI/UX execution slice that replaces the isolated cockpit action panel with a single operational workspace while preserving the existing FastAPI + Jinja + local JS stack and authority boundaries.

## Delivered

- Added `GET /surface/operate` as the primary local authoring surface.
- Kept `GET /surface/actions` as compatibility, redirecting to the operate workspace.
- Reworked cockpit action responses to re-render the same workspace with:
  - preserved domain/object context;
  - inline `ResultReceipt`;
  - inline `ActionErrorCard`;
  - auto-prefill for activation and validation follow-ups.
- Added explicit cockpit materialization control and publication-state visibility (`not_materialized`, `materialized`, `out_of_sync`).
- Added shared operate-context helpers for cockpit, REST, and MCP.
- Added agent REST reads:
  - `/agent/domains/{domain_id}/operate-context`
  - `/agent/domains/{domain_id}/active-charter`
- Added MCP normative read tools:
  - `get_operate_context`
  - `get_active_domain_charter`
- Hardened `build_mcp_server()` with a lightweight local fallback when the optional `mcp` dependency chain is broken in the environment.

## Files

- `system/runtime/core/operate_context.py`
- `system/runtime/api/materialization.py`
- `system/runtime/api/routers/surface.py`
- `system/runtime/api/routers/pipelines.py`
- `system/runtime/api/routers/agent_surface.py`
- `system/runtime/mcp/server.py`
- `system/tests/integration/test_product_day0_operations.py`
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_agent_surface.py`
- `system/tests/integration/test_prd_completion.py`
- `SYSTEM_STATUS.yaml`
- `agent/plan/ACTIVE_TRACK.md`
- `agent/CURRENT_MISSION.md`

## Verification

Command:

```powershell
python -m unittest discover -s system/tests -t . -p "test_*.py"
```

Result:

- `45 tests OK`

## Notes

- The MCP fallback is an environment-hardening measure for local operation and testability. It does not claim deeper transport/protocol completeness.
- The worktree remains dirty with unrelated pre-existing changes outside this slice. No broad commit was made in this run.
