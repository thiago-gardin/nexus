# Cockpit UI Regression Report

Date: 2026-04-12
Scope: post-UI-1 Playwright regression
Status: passed with known UI-2/UI-3 residuals

## Setup

- Runtime URL: `http://127.0.0.1:8126`
- DB: `output/playwright/cockpit-visual-20260412-193606/cockpit-visual.db`
- Scenario domain: `visual-alpha`
- Desktop viewport: `1440x900`
- Mobile viewport: `390x844`
- Metrics: `output/playwright/cockpit-ui-regression-20260412-2118/ui_metrics.json`

## Screenshots

| Screen | File |
| --- | --- |
| Dashboard | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/01-dashboard.png` |
| Domain explorer | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/02-domain-explorer.png` |
| Graph filtered URL | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/03-graph-filtered.png` |
| Proposal review | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/04-proposal-review.png` |
| Object inspector | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/05-object-inspector.png` |
| Payload viewer | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/06-payload-viewer.png` |
| Projection panel | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/07-projection-panel.png` |
| Event timeline | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/08-event-timeline.png` |
| Reentry diff | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/09-reentry-diff.png` |
| Dashboard mobile | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/10-dashboard-mobile.png` |
| Graph mobile | `output/playwright/cockpit-ui-regression-20260412-2118/screenshots/11-graph-mobile.png` |

## Automated Results

- Pages checked: 11.
- HTTP failures: 0.
- Browser console warnings/errors: 0.
- Network responses `>=400`: 0.
- Desktop document overflow failures: 0.
- Mobile document overflow failures: 0.
- Persistent mode rail present: yes on checked pages.
- Global context bar present: yes on checked pages.
- Reentry link present on desktop checked pages: yes.

## Findings

### Pass

- The post-UI-1 shell loads consistently across dashboard, domain, graph, proposal, inspector, payload, projection, timeline, and reentry pages.
- All checked routes returned HTTP 200.
- Favicon noise is gone in this run: no console or network 404 was observed.
- The `390px` mobile viewport no longer has document-level horizontal overflow: dashboard and graph reported `documentWidth=375` with `innerWidth=390`.
- The cockpit mode rail and global context bar remain present on checked desktop and mobile views.

### Residual Issues

- Graph deep-link control preselection is still not implemented. Opening `/surface/graph?domain=visual-alpha` renders graph data but leaves the domain select value empty (`graphDomainControlValue=""`). This belongs to UI-2.
- Graph labels are improved visually by the dark shell but still need explicit label-density controls and selected node/edge inspection. This belongs to UI-2.
- Mobile tables no longer overflow the document, but long table rows still require internal horizontal scanning and have awkward narrow columns in cards such as `Controlled Reentry Contract`, `Pending Proposals`, and `Decisions`. This belongs to UI-3 or a small UI-1 follow-up if prioritized.
- Object and proposal pages still expose raw UUIDs prominently in titles and tables. This belongs to UI-3 label-first inspector work.

## Verdict

UI-1 remains validated after a fresh UI regression pass. The next implementation slice should be UI-2: graph control state, explicit apply/reset/copy-link affordances, label-density controls, and selected graph object inspection.

## Authority Notes

- `system/00_specs/` was not modified.
- No runtime mutation was performed through the UI test.
- No dependency changes were made.
- REST/MCP semantics were not changed.
