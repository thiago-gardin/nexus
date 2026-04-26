# Cockpit Usability Report
## Date: 2026-04-12 | Scope: visual Playwright review

## Summary

The cockpit is usable for local operational inspection and governance review. The tested pages loaded with HTTP 200, showed live runtime data, and preserved the intended authority framing: review actions call governance, and reentry creates proposals rather than mutating objects directly.

The main usability gaps are not functional blockers. They are interaction and readability issues: mobile horizontal overflow, graph filter/deep-link friction, ID-heavy tables, and limited primary navigation for newer panels.

## Test Setup

- Runtime URL: `http://127.0.0.1:8123`
- DB: `output/playwright/cockpit-visual-20260412-193606/cockpit-visual.db`
- Scenario domain: `visual-alpha`
- Browser viewport: desktop `1440x1000`, mobile `390x844`
- Console: only observed error was `favicon.ico` 404.
- Network: all cockpit pages tested returned HTTP 200.

## Screenshots

| Screen | File |
| --- | --- |
| Dashboard | `output/playwright/cockpit-visual-20260412-193606/screenshots/01-dashboard.png` |
| Domain explorer | `output/playwright/cockpit-visual-20260412-193606/screenshots/02-domain-explorer.png` |
| Graph | `output/playwright/cockpit-visual-20260412-193606/screenshots/03-graph.png` |
| Proposal review | `output/playwright/cockpit-visual-20260412-193606/screenshots/04-proposal-review.png` |
| Object inspector | `output/playwright/cockpit-visual-20260412-193606/screenshots/05-object-inspector.png` |
| Payload viewer | `output/playwright/cockpit-visual-20260412-193606/screenshots/06-payload-viewer.png` |
| Projection panel | `output/playwright/cockpit-visual-20260412-193606/screenshots/07-projection-panel.png` |
| Event timeline | `output/playwright/cockpit-visual-20260412-193606/screenshots/08-event-timeline.png` |
| Reentry diff panel | `output/playwright/cockpit-visual-20260412-193606/screenshots/09-reentry-diff.png` |
| Mobile dashboard | `output/playwright/cockpit-visual-20260412-193606/screenshots/10-dashboard-mobile.png` |

## Positive Findings

- The dashboard gives a quick operational summary with counts for domains, entities, relations, events, proposals, and pending decisions.
- The authority model is visible on the main cockpit pages: review-capable surface, gated governance, and proposal-from-edit limits are stated clearly.
- The proposal review page is complete enough for a human reviewer: proposal summary, decision summary, target object, proposed changes, and approve/reject forms are all visible in one flow.
- Payload and projection panels expose both metadata and readable content.
- The reentry diff panel clearly states that it creates a structured reentry proposal and does not mutate the target object.
- Graph data is rendered from the live executable state and filter behavior works when the user applies filters through the controls.

## Usability Findings

| Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- |
| Medium | Mobile dashboard has horizontal overflow. | At `390px` viewport, document width was `643px`; overflow came from cards/tables for Controlled Reentry Contract, Pending Proposals, and Decisions. | Add responsive table wrappers or card-style row rendering below a breakpoint. |
| Medium | Graph page is visually fragile with long labels. | Long node labels overlap and crowd the SVG, especially source-candidate nodes. | Truncate labels in-node, expose full label in title/tooltip, and add spacing or simple force/row layout for larger graphs. |
| Medium | Graph filter state is not URL-persistent/deep-linkable. | Opening `/surface/graph?domain=visual-alpha` did not preselect the domain control. | Initialize controls from query params and update the URL when filters change. |
| Medium | Graph filters lack an explicit apply affordance. | Text filters require `Enter` or change/blur behavior; this is easy to miss. | Add an explicit `Apply filters` button and optionally debounce input. |
| Medium | UUID-heavy tables reduce scanability. | Dashboard, domain explorer, proposal review, and decision tables show full UUIDs as primary visible content. | Use labels first, truncate IDs with copyable full value, and add object-type badges. |
| Medium | New cockpit panels are not first-class in global navigation. | Timeline, payload viewer, projection panel, and reentry diff are reachable through known URLs or contextual links, not from top-level nav. | Add nav links for Timeline, Reentry, and maybe Search/Inspector entry points. |
| Low | Missing favicon causes console noise. | Browser console reported `GET /favicon.ico` 404. | Add a tiny local favicon route or static asset to keep visual QA console clean. |
| Low | Payload JSON is hard to scan. | Payload content renders as compact JSON in a dark code block. | Pretty-print JSON payloads or add a formatted/object view when `format=json`. |

## Suggested Next Slice

Run a focused `Cockpit Usability Hardening` slice:

1. Responsive table/card treatment for mobile.
2. Graph filter state persistence and explicit apply button.
3. Graph label truncation/tooltip behavior.
4. Top-level navigation links for timeline, reentry, and inspector/search entry.
5. Favicon/static no-op cleanup.

No runtime authority change is required for these improvements.
