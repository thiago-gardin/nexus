# Unified Workbench v1 Slice
## Date
2026-04-24

## Scope

Implement the operator-first cockpit slice that turns the Day 0 `Operate Workspace` into a unified workbench shared with the graph surface, without changing the FastAPI + Jinja + local JS stack or crossing the existing governance boundaries.

The target of this slice was human usability, not additional backend authority:

- stop exposing raw JSON authoring as the default human path;
- stop relying on manual ID recall/copy-paste;
- move action entry into a contextual drawer;
- keep graph, inspector, event stream, and publication context in the same workspace.

## Delivered

- Consolidated `/surface/operate` and `/surface/graph` into the same cockpit workbench shell.
- Replaced exposed action-card stacking with an `Action Drawer` that opens contextual forms inside the workbench.
- Added automatic human-oriented ID suggestion for cockpit domain creation instead of requiring manual technical IDs in the main flow.
- Added label-based pickers for entities, relations, and review targets so humans do not operate by memorized IDs.
- Added inferred `ui_schema` support in operate-context helpers and rendered dynamic entity fields from domain-aware schema data instead of raw JSON entry.
- Kept graph canvas, inspector, decision/review context, publication state, and live event stream visible in the same workbench.
- Preserved service/governance boundaries: cockpit actions still flow through the same authoring/materialization services and did not introduce a parallel mutation path.

## Files

- `system/runtime/core/operate_context.py`
- `system/runtime/api/routers/surface.py`
- `system/runtime/api/static/cockpit_map.js`
- `system/runtime/api/templates/cockpit_workbench.html`
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_product_day0_operations.py`
- `system/tests/integration/test_prd_completion.py`
- `SYSTEM_STATUS.yaml`
- `agent/plan/ACTIVE_TRACK.md`

## Verification

Command:

```powershell
python -m unittest discover -s system/tests -t . -p "test_*.py"
```

Result:

- `45 tests OK`

## Residual limitations

- `ui_schema` is inferred from charter/observed data and is good enough for Day 0 human operation, but it is not yet a full explicit product-grade form-contract layer.
- The legacy `_render_operate_workspace()` function still contains now-unreached HTML from the prior slice; it is cleanup debt, not a current behavior path.
- The graph/workbench shell is now coherent, but higher-order UX work such as inline editing, richer picker search, and stronger visual publication feedback can still be improved in later slices.
- No broad commit was made in this slice; the repository still contains unrelated pre-existing drift that should not be absorbed accidentally.
