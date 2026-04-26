# Cockpit UI-1 Execution Report

Date: 2026-04-12
Slice: UI-1 - Cockpit Shell And Responsive Baseline
Status: completed for this slice

## Scope Executed

- Added a shared institutional cockpit shell to the FastAPI surface pages rendered through `system/runtime/api/routers/surface.py`.
- Added a persistent mode rail with `Overview`, `MAP`, `FLOW`, `INSPECT`, `AUDIT`, `Decisions`, and `Reentry` links.
- Added a global context bar that keeps DB authority, derived tree status, and governed actions visible.
- Reworked the shared cockpit CSS for a dark, dense, long-session-friendly surface without external dependencies.
- Added responsive table wrappers and safer overflow behavior for long IDs, payload blocks, and tables.
- Updated the graph template in `system/runtime/api/templates/cockpit_graph.html` to use the same cockpit shell and navigation frame.
- Added a low-risk `/favicon.ico` route returning `204` to remove the unexpected favicon 404.
- Added integration coverage for shell navigation and favicon behavior.

## Files Changed

- `system/runtime/api/routers/surface.py`
- `system/runtime/api/templates/cockpit_graph.html`
- `system/runtime/api/main.py`
- `system/tests/integration/test_operational_surface.py`
- `agent/plan/COCKPIT_INTERFACE_IMPROVEMENT_PLAN.md`
- `agent/ops/COCKPIT_UI1_EXECUTION_REPORT_2026-04-12.md`
- `output/playwright/cockpit-ui1-20260412-visual/screenshots/01-dashboard.png`
- `output/playwright/cockpit-ui1-20260412-visual/screenshots/02-graph.png`
- `output/playwright/cockpit-ui1-20260412-visual/screenshots/03-dashboard-mobile.png`

## Validation

Commands run:

```powershell
python -m py_compile system/runtime/api/main.py system/runtime/api/routers/surface.py
python -m unittest system.tests.integration.test_operational_surface -v
python -m unittest discover -s system/tests -v
```

Results:

- `py_compile`: passed.
- Targeted operational surface tests: 6 tests passed.
- Full test suite: 36 tests passed.

Visual smoke:

- Local server: `http://127.0.0.1:8124`
- DB: `output/playwright/cockpit-visual-20260412-193606/cockpit-visual.db`
- Screenshots:
  - `output/playwright/cockpit-ui1-20260412-visual/screenshots/01-dashboard.png`
  - `output/playwright/cockpit-ui1-20260412-visual/screenshots/02-graph.png`
  - `output/playwright/cockpit-ui1-20260412-visual/screenshots/03-dashboard-mobile.png`
- Browser console: 0 warnings, 0 errors.
- Mobile viewport check at `390x844`: `innerWidth=390`, `documentWidth=375`, `bodyWidth=375`, no horizontal document overflow.

## Remaining Drift

- UI-2 remains pending: graph controls still need explicit `Apply`, `Reset`, `Copy link`, and query-param preselection.
- UI-2 remains pending: graph labels are more visually integrated but dense-label management and selected object inspection are not complete.
- UI-3 remains pending: object/payload/projection inspector still needs full label-first evidence rail treatment.
- UI-4 remains pending: `FLOW` and `AUDIT` are now navigable, but event/job/proposal reconstructability has not been redesigned.
- UI-5 remains pending: global search/command overlay is not implemented.
- UI-6 remains pending: this was a UI-1 visual smoke, not full usability closure for the complete cockpit plan.

## Authority Notes

- `system/00_specs/` was not modified.
- No dependency files were modified.
- REST/MCP semantics were not changed.
- Governance approval/rejection still routes through existing governance services.
- `tree/` remains derived publication state.
- `CURRENT_STATE.md` was not modified.
