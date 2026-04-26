# Cockpit MAP Workbench D3 Decision

Date: 2026-04-13
Status: implemented

## Decision

Use D3 for the Nexus MAP workbench as a vendored local static asset.

## Scope

- D3 version: `7.9.0`
- Local asset: `system/runtime/api/static/vendor/d3.v7.9.0.min.js`
- Source URL used for vendoring: `https://unpkg.com/d3@7.9.0/dist/d3.min.js`
- License: `ISC` from D3 package metadata
- SHA256: `F2094BBF6141B359722C4FE454EB6C4B0F0E42CC10CC7AF921FC158FCEB86539`
- Runtime client: `system/runtime/api/static/cockpit_map.js`

## Rationale

The MAP surface needs Obsidian-like navigation and V2-like graph controls: force layout, zoom/pan, focus graph, label modes, inspector behavior, cross-domain navigation, and graph toolbar actions.

The approved implementation keeps the Nexus cockpit architecture intact:

- FastAPI + Jinja remains the cockpit delivery model.
- D3 is served locally by FastAPI through `/static`.
- No CDN is used at runtime.
- No Node, Vite, React, or Tailwind pipeline is introduced.
- The MAP remains read-only; actions route to governed cockpit pages.

## Implemented Behavior

- `/surface/graph` now loads the local D3 asset and `cockpit_map.js`.
- `/surface/graph.json` remains backward-compatible with `nodes` and `edges`.
- `/surface/graph.json` now accepts `focus`, `depth`, `view`, `label_mode`, `color_mode`, `size_mode`, and `cross_domain`.
- MAP view lenses have minimum server-side semantics: `governance`, `evidence`, `reentry`, and `cross_domain` constrain graph data instead of acting only as UI labels.
- Nodes are enriched with degree, focal state, confidence, evidence count, event count, latest event, risk, and inspector/history hrefs.
- Edges are enriched with cross-domain state, confidence, evidence refs, event count, latest event, and inspector/history hrefs.
- The MAP UI includes Apply, Reset, Copy link, lens presets, zoom, fit, reset, refresh, node/edge inspector, hover highlight, click selection, and double-click focus.

## Explicit Non-Goals

- No React/Vite migration.
- No external graph service.
- No persistent saved views.
- No minimap.
- No graph time-lapse.
- No direct mutation from the MAP.

## Validation

- `python -m py_compile system/runtime/api/main.py system/runtime/api/routers/surface.py`
- `node --check system/runtime/api/static/cockpit_map.js`
- `python -m unittest system.tests.integration.test_operational_surface -v`
- `python -m unittest system.tests.integration.test_prd_completion.PrdCompletionTests.test_generic_ingestion_materialization_reentry_payload_edit_and_graph -v`
- `python -m unittest discover -s system/tests -t . -p "test_*.py"` -> 41 tests OK

Browser verification used a temporary seeded DB under `output/playwright/map-workbench-20260413-023053/`.

- D3 local asset loaded with HTTP 200.
- `cockpit_map.js` loaded with HTTP 200/304.
- `/surface/graph.json` returned HTTP 200 for global and focus views.
- Node click opened the read-only inspector.
- Node double-click updated the URL to focus mode.
- Fit/reset controls executed without console errors.
- Console after load and interactions: 0 errors, 0 warnings.
- Mobile check: `scrollWidth=375` for `viewport=390`.
- Screenshots:
  - `output/playwright/map-workbench-20260413-023053/map-workbench-desktop.png`
  - `output/playwright/map-workbench-20260413-023053/map-workbench-node-inspector.png`
  - `output/playwright/map-workbench-20260413-023053/map-workbench-mobile.png`
