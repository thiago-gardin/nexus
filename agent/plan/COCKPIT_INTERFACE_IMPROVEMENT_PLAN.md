# Cockpit Interface Improvement Plan

Date: 2026-04-12
Status: UI-1 executed; UI-2 through UI-6 pending
Scope: interface planning only; no runtime or spec mutation in this slice

## 1. Objective

Improve the Nexus cockpit from a functional operational surface into a more legible institutional cockpit, while preserving the current architecture:

- FastAPI + Jinja + local CSS/JS for the human cockpit.
- REST/local as current local contract.
- MCP as formal agent adapter, unchanged by this UI plan.
- DB as executable authority.
- `tree/` as derived materialization surface.
- `system/00_specs/` as read-only normative layer.

The target is not a visual reskin. The target is to make the cockpit answer, quickly and safely:

- What is active?
- What changed?
- What needs review?
- What is risky or unresolved?
- What evidence supports this object or decision?
- How can the operator inspect or act without bypassing governance?

## 2. Inputs Reviewed

This plan is based on:

- `agent/ops/COCKPIT_USABILITY_REPORT_2026-04-12.md`
- `system/00_specs/PRD.md` read-only
- `system/00_specs/research/Version history` read-only
- V2 reference repo: `thiago-gardin/Nexus-V2---Google-IA-Studio-Bootstrap`
- Earlier Nexus reference repo: `ngthiagpgp/Nexus`
- FigJam planning diagram: <https://www.figma.com/online-whiteboard/create-diagram/cae9c61e-e566-460b-964f-c6fa8f966922?utm_source=other&utm_content=edit_in_figjam&oai_id=&request_id=6aaa4e93-2e2a-4352-b445-7b68103710d0>

Reference commits inspected:

- V2: `d6de8f3fafc93dbba35f21540acda898d1431e65` (`feat: Initialize Nexus Cognitive Memory project`, 2026-03-27)
- Earlier Nexus reference: `f6d721054fdb4a48ad43004bbc173e62c898da1c` (`refactor(topology): finalize minimal repository transfiguration`, 2026-03-16)

Current implementation targets discovered:

- `system/runtime/api/routers/surface.py`: most human surface routes and inline HTML rendering.
- `system/runtime/api/templates/cockpit_graph.html`: graph page template and local JS.
- `system/runtime/api/main.py`: app wiring and possible favicon/static wiring if needed.
- `system/tests/integration/test_operational_surface.py`: governance surface behavior tests.
- `system/tests/integration/test_prd_completion.py`: PRD cockpit, graph, payload, projection, timeline, reentry, and MCP acceptance coverage.
- `output/playwright/cockpit-visual-20260412-193606/`: current visual QA screenshots and seeded visual test DB.

## 3. Constraints

- Do not modify `system/00_specs/`.
- Do not redesign Nexus architecture.
- Do not replace REST/local or MCP authority boundaries.
- Do not add React, Vite, Tailwind, CDN assets, or Node build steps.
- D3 is explicitly approved only as a vendored local static asset for the MAP workbench.
- Do not add dependencies without explicit confirmation.
- Keep the cockpit served by FastAPI + Jinja templates + local CSS/JS.
- Treat V2 as visual and interaction reference, not as a stack migration target.
- Keep governance actions routed through existing governance/reentry APIs.
- Keep `CURRENT_STATE.md` untouched unless explicit human authorization is given.
- Keep `tree/` derived from DB; do not turn it into UI authority.

## 4. Current Cockpit Issues To Resolve

The visual QA report identified these practical gaps:

- Mobile dashboard has horizontal overflow at a `390px` viewport.
- Graph labels overlap and are not sufficiently legible under dense topology.
- Graph query params work for filtering but do not preselect controls, weakening deep links.
- Graph filters need an explicit apply/reset affordance.
- UUID-heavy tables make scanning harder when human labels exist.
- Timeline, payload, projection, and reentry surfaces are reachable but not prominent enough in top-level navigation.
- Favicon request returns 404.
- JSON payload rendering is functionally correct but hard to read for long inspection sessions.

These are not only visual defects. They weaken operational cognition: orientation, focus, inspection, evidence review, and safe intervention.

## 5. Lessons From Version History

The version history frames the UI problem as part of the larger Nexus evolution:

- `v0`: knowledge organization in files.
- `v1`: local MVP with CLI, DB, Markdown, API, and early cockpit; human reading still weak.
- `v2`: architectural turn toward `core`, `modules`, `adapters`, `agents`, MCP-first thinking, and detachable cockpit.
- `v3`: ontological turn toward cognitive-operational infrastructure, structural graph, operational cockpit, and human-agent symmetry.
- `v4`: institutional infrastructure with domains as fundamental units, explicit governance, auditability, human-agent symmetry, and DB + treefolder dual architecture.

The UI should therefore move from "pages that expose tables" toward "institutional cockpit that shows relations, evidence, flow, and governance state."

## 6. Lessons From V2

V2 provides usable interaction patterns that should be adapted into the current local cockpit without importing its frontend stack:

- A compact left mode rail keeps navigation stable while the center surface changes.
- The overview should behave like a pulse surface: health, deltas, recent events, and decision queue before deep inventory.
- Graph work benefits from visible controls: domain, focus entity, depth, status, entity type, relation type, label density, color mode, and scope.
- A right inspection panel should expose provenance, validation state, confidence, related events, and safe proposal/decision actions.
- Governance deserves its own review surface with conflict cases, promotion candidates, and decision status.
- Search should be global and object-aware, not isolated to one table.
- Semantic color and state rules should be centralized so status, actor, and validation state remain consistent across panels.
- A graph toolbar should expose zoom/fit/reset/refresh-like actions even if implemented simply in local JS first.
- A selected object panel should show label, type, status, confidence, provenance, last event, and action links.

The V2 React/Tailwind implementation is not a direct migration target. The transferable unit is the information architecture and interaction behavior.

## 7. Lessons From The Earlier Nexus UI Specs

The earlier UI planning materials point to a stronger cockpit framing:

- The cockpit is a shared supervision surface for human and agent work, not a generic dashboard or DB browser.
- The UI should answer orientation first: what is active, what changed, what needs review, what is risky.
- The graph/MAP should become the dominant cognitive field when the operator is reasoning about structure.
- Metadata should be available but visually secondary to labels, relations, evidence, and decision state.
- Primary regimes should be stable: `MAP`, `FLOW`, `INSPECT`, `AUDIT`.
- Governance must be visible, but it should not dominate every screen when no intervention is needed.
- Detail should be opened by intention rather than forcing every table to expose raw object internals.
- Spatial memory matters: main navigation should not move radically between tasks.
- The operator needs a "3-second read" before deeper inspection.

## 8. Target Interface Model

The next cockpit iteration should converge toward this model:

- Global context bar: system status, active domain, decision queue count, last event, search entry.
- Left mode rail: `Overview`, `MAP`, `FLOW`, `INSPECT`, `AUDIT`, `Search`.
- Center work field: dominant panel for the selected mode.
- Right evidence rail: selected object/proposal/payload/projection details with provenance and safe actions.
- Bottom flow strip: recent events, active jobs, pending proposals, and reentry signals.
- Mobile mode: stacked cards and collapsible rails; no horizontal overflow.

Mode meanings:

- `Overview`: pulse surface for health, recent changes, decision queue, and quick links.
- `MAP`: graph-first domain/relation exploration.
- `FLOW`: events, jobs, materialization, reentry, and change chronology.
- `INSPECT`: object, payload, projection, and provenance inspection.
- `AUDIT`: decisions, proposals, governance rules, and reconstructability.
- `Search`: global object search with sectioned results.

## 9. UI Information Architecture

The cockpit should preserve the current routes while adding a clearer mental model.

Recommended navigation:

| Mode | Primary route | Existing route fit | Purpose |
| --- | --- | --- | --- |
| Overview | `/surface` | Existing dashboard | Pulse, health, recent events, pending decisions |
| MAP | `/surface/graph` | Existing graph page | Domain/relation topology and selected object map |
| FLOW | `/surface/events/timeline` | Existing timeline | Event flow, jobs, reentry signals, materialization sequence |
| INSPECT | `/surface/objects/{object_type}/{object_id}` | Existing inspector | Object/payload/projection details and provenance |
| AUDIT | `/surface/proposals`, `/surface/decisions` | Existing governance pages | Proposal review, decisions, reconstructability |
| Search | overlay or `/surface/search` if added later | Backed by `/search` | Global retrieval across object types |

The implementation can start without adding many new routes. First improve shell/navigation and route prominence. Add new route only when an existing endpoint cannot cleanly support the interaction.

## 10. Visual System Direction

The visual direction should be sober, dense, and long-session friendly:

- Prefer dark analytical cockpit styling already implied by previous UI references, unless it conflicts with current CSS.
- Use semantic color only for state: health, risk, proposal status, validation status, actor/source, and domain grouping.
- Avoid decorative gradients or motion that do not clarify state.
- Make object labels the primary visual text; UUIDs should be secondary metadata.
- Use compact cards for overview and mobile; use tables only where comparison matters.
- Use monospace for IDs, timestamps, and raw payloads.
- Use a readable preformatted block or JSON details component for payloads.
- Keep governance actions visually distinct from navigation links.

Suggested semantic classes:

- `state-ok`
- `state-attention`
- `state-critical`
- `state-proposed`
- `state-approved`
- `state-rejected`
- `actor-human`
- `actor-agent`
- `actor-system`
- `evidence-ref`
- `object-id-muted`
- `governance-action`

This can be implemented in local CSS, either inline in `surface.py` initially or extracted later if a local static path is established.

## 11. Data And View Contracts

The cockpit should rely on existing data sources first:

- `/surface/graph.json` for graph nodes and edges.
- `/search` for global search results.
- Existing surface routes for proposals and decisions.
- Existing object inspector routes for object history and evidence.
- Existing payload/projection routes for content inspection.
- Existing reentry parse-diff route for non-mutating change proposals.

Required behavior:

- Query params in `/surface/graph` must map to visible control state and to `/surface/graph.json`.
- UI controls must not mutate canonical DB objects directly.
- Approval/rejection must continue through governance decision routes.
- Reentry must continue through proposal generation paths.
- Payload/projection display must not imply `tree/` is source of truth.

Potential additions if implementation proves necessary:

- A local favicon route or asset.
- A reusable shell helper in `surface.py`.
- A local static mount for CSS/JS only if it simplifies maintainability; otherwise keep inline CSS/JS for the first slice.
- A `/surface/search` page only if overlay-only search is too brittle for tests/accessibility.

## 12. Detailed Implementation Slices

### Slice UI-1: Cockpit Shell And Responsive Baseline

Status: executed on 2026-04-12. Evidence is recorded in `agent/ops/COCKPIT_UI1_EXECUTION_REPORT_2026-04-12.md`.

Goal: fix the outer cockpit frame without changing backend semantics.

Likely files:

- `system/runtime/api/routers/surface.py`
- `system/runtime/api/main.py` only if favicon/static wiring is needed
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_prd_completion.py` only if PRD cockpit assertions need extension

Tasks:

- Introduce a consistent shell helper for page chrome: context bar, mode rail, content region, optional side rail, footer/flow strip.
- Replace duplicated dashboard navigation links with mode-based navigation.
- Add persistent links for graph, events timeline, proposals, decisions, payload/projection inspection entry points where relevant, and reentry parse-diff.
- Add responsive wrappers for tables and preformatted blocks.
- Make long IDs break safely or render in muted/copyable metadata blocks.
- Fix favicon 404 with the lowest-risk local approach.
- Keep all existing forms and action URLs unchanged.

Acceptance:

- Dashboard, graph, object inspector, payload, projection, timeline, and reentry pages load with consistent shell.
- At `390px` viewport, document width does not exceed viewport by more than a small scrollbar tolerance.
- Favicon no longer appears as an unexpected 404 in visual QA.
- Existing governance tests still pass.
- No new external frontend dependency is introduced.

Validation:

- `python -m py_compile system/runtime/api/main.py system/runtime/api/routers/surface.py`
- `python -m unittest discover -s system/tests -v`
- Playwright mobile screenshot of `/surface`.

### Slice UI-2: MAP Graph Controls And Deep Links

Status: executed on 2026-04-13 as MAP Workbench with local vendored D3. Evidence is recorded in `agent/ops/COCKPIT_MAP_WORKBENCH_D3_DECISION_2026-04-13.md`.

Goal: make the graph usable as an operational map instead of a static visualization.

Likely files:

- `system/runtime/api/templates/cockpit_graph.html`
- `system/runtime/api/routers/surface.py`
- `system/runtime/api/main.py`
- `system/runtime/api/static/cockpit_map.js`
- `system/runtime/api/static/vendor/d3.v7.9.0.min.js`
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_prd_completion.py`

Tasks:

- Preselect graph controls from query params.
- Add explicit `Apply`, `Reset`, and `Copy link` controls.
- Preserve and expose filters for `domain`, `entity_type`, `relation_type`, `status`, and `scope`.
- Add focus/depth, view, label, color, size, and cross-domain controls.
- Add label density control: `off`, `key`, `all`, `zoom`.
- Add a graph toolbar: zoom in/out, fit, reset, refresh.
- Truncate long labels visually while preserving full label in SVG title or inspector.
- Add selected-node/edge inspection panel with object type, label, status, domain, provenance/evidence links when available.
- Keep node click routing compatible with existing history/inspector behavior.
- Use D3 force simulation from local vendored static asset only; no CDN and no Node build pipeline.

Acceptance:

- `/surface/graph?domain=...&status=...` restores visible control state.
- `/surface/graph.json` remains backward compatible with existing tests.
- Dense graph screenshots no longer have labels as the primary source of visual noise.
- Selecting a node or edge exposes evidence/provenance context without direct mutation.
- Double-clicking a node can move the MAP into focus mode through URL state.
- Cross-domain graph filtering is available through `/surface/graph.json`.

Validation:

- `python -m py_compile system/runtime/api/routers/surface.py`
- `python -m unittest discover -s system/tests -v`
- Playwright screenshots for default graph and filtered graph.
- Browser console/network check.

### Slice UI-3: Inspector And Evidence Rail

Status: pending.

Goal: reduce UUID-first scanning and make provenance/decision state primary.

Likely files:

- `system/runtime/api/routers/surface.py`
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_prd_completion.py`

Tasks:

- Render human label/title first when present; place UUID in secondary mono metadata with copy affordance.
- Normalize badges for status, type, actor, confidence, proposal state, and validation state.
- Add evidence/provenance blocks to object, payload, projection, and proposal panels.
- Promote links to object history, proposal review, decision review, payload viewer, projection panel, and reentry parse-diff.
- Improve JSON/payload readability with collapsible or structured sections using local HTML only.
- Make decision actions visibly routed through governance/reentry APIs.

Acceptance:

- Object, payload, projection, and proposal pages can be scanned without reading UUIDs first.
- Every critical action surface shows what API/governance route owns the mutation.
- Provenance is visible on inspection surfaces without needing to open raw JSON.
- Proposal-from-edit remains limited to its declared editability contract.

Validation:

- `python -m py_compile system/runtime/api/routers/surface.py`
- `python -m unittest discover -s system/tests -v`
- Playwright screenshots for object inspector, payload viewer, projection panel, and proposal review.

### Slice UI-4: FLOW And AUDIT Surfaces

Status: pending.

Goal: make timeline, jobs, decisions, and reentry legible as operational flow.

Likely files:

- `system/runtime/api/routers/surface.py`
- `system/tests/integration/test_operational_surface.py`
- `system/tests/integration/test_prd_completion.py`

Tasks:

- Promote event timeline to a first-class `FLOW` view in the shared shell.
- Add a compact bottom flow strip to overview and inspector pages.
- Group events by domain/object/proposal where possible.
- Add `AUDIT` view framing around proposals and decisions without duplicating governance services.
- Link proposals, decisions, events, object history, materializations, and reentry signals in one reconstructable path.
- Add reentry parse-diff panel entry from `FLOW` and `AUDIT`.

Acceptance:

- Operator can reconstruct a critical change from proposal to decision to event to materialization.
- Reentry remains proposal-driven and does not mutate canonical state directly.
- `FLOW` and `AUDIT` are reachable from persistent navigation.
- Empty states are explicit when no events/jobs/proposals exist.

Validation:

- `python -m py_compile system/runtime/api/routers/surface.py`
- `python -m unittest discover -s system/tests -v`
- Targeted TestClient assertions for links and empty states.
- Playwright screenshot for timeline/AUDIT pages.

### Slice UI-5: Global Search And Command Overlay

Status: pending.

Goal: support object retrieval without making every page an inventory table.

Likely files:

- `system/runtime/api/routers/surface.py`
- `system/runtime/api/templates/cockpit_graph.html` only if graph gets search focus integration
- `system/tests/integration/test_prd_completion.py`

Tasks:

- Add a local JS search overlay backed by existing `/search`, or add a simple `/surface/search` page first if it is easier to test.
- Group results by object type.
- Show label, type, domain, status, and short evidence summary when available.
- Route selected results to the correct inspector page.
- Add keyboard shortcut only if it does not interfere with browser or form behavior.
- Provide a visible search entry in the global context bar.

Acceptance:

- Search can locate domains, entities, relations, payloads, projections, and proposals from any cockpit page.
- Result selection routes to the correct inspector page.
- Search works without external JS libraries.
- No action in search mutates state.

Validation:

- `python -m py_compile system/runtime/api/routers/surface.py`
- `python -m unittest discover -s system/tests -v`
- TestClient check for `/search` compatibility and any added `/surface/search` route.
- Playwright interaction check if an overlay is implemented.

### Slice UI-6: Visual Acceptance And Usability Closure

Status: pending.

Goal: verify the cockpit against the actual issues found in visual QA.

Likely files:

- `agent/ops/COCKPIT_USABILITY_REPORT_<date>.md`
- `output/playwright/<run>/screenshots/`
- `agent/plan/COCKPIT_INTERFACE_IMPROVEMENT_PLAN.md` only if closure updates are needed

Checks:

- Playwright screenshots for desktop and mobile views.
- Console/network check with no unexpected errors.
- Mobile width check.
- Graph deep-link restore check.
- 3-second orientation check: active domain, health, pending review, and latest change are visible without drilling down.
- Governance check: no direct UI mutation bypasses governance/reentry endpoints.
- Regression check for proposal approval/rejection flow.

Acceptance:

- Update or create a usability report under `agent/ops/`.
- Screenshots are stored under `output/playwright/` or another non-authoritative output path.
- Remaining drift is explicitly listed rather than treated as done by narrative.
- Full unittest suite passes after UI changes.

Validation:

- `python -m unittest discover -s system/tests -v`
- Playwright visual pass on the seeded scenario used for usability QA.

## 13. Evidence Matrix

| Criterion | Evidence required |
| --- | --- |
| No spec mutation | `git diff -- system/00_specs/` is empty |
| No dependency drift | Dependency files unchanged unless explicitly approved |
| REST/MCP unchanged | Existing REST/MCP tests still pass |
| Governance preserved | Approval/rejection and proposal-from-edit tests still pass |
| Mobile fixed | Playwright width check and mobile screenshot |
| Graph usable | Screenshot plus query-param restore test |
| UUID noise reduced | Inspector screenshot showing label-first layout |
| Timeline/reentry discoverable | Persistent nav screenshots and TestClient route checks |
| Search non-mutating | TestClient/Playwright search path with no mutation side effect |
| Closure recorded | New/updated usability report in `agent/ops/` |

## 14. Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Overbuilding a React-like shell in inline Python HTML | Implement smallest shell helper first; extract only when duplication becomes a real problem |
| Graph D3 complexity creates frontend maintenance risk | Keep D3 vendored locally, isolate behavior in `cockpit_map.js`, and avoid Node/React/Vite migration |
| Mobile table conversion breaks tests that assert text | Preserve visible text and route links; adjust tests only for changed markup, not semantics |
| Search overlay becomes inaccessible or hard to test | Prefer a simple `/surface/search` page first if overlay complexity rises |
| Governance actions look like direct edits | Add explicit route/authority labels near action forms |
| Visual plan drifts from PRD authority | Keep each slice tied to PRD concepts: domain, relation, evidence, proposal, decision, projection, reentry |

## 15. Out Of Scope

- Rewriting the cockpit as React.
- Adding Tailwind, force-graph libraries, CDN dependencies, or a Node frontend build pipeline.
- Adding any graph dependency beyond the approved local D3 asset.
- Changing MCP or REST semantics.
- Altering runtime authority rules.
- Editing `system/00_specs/`.
- Editing `CURRENT_STATE.md`.
- Turning `tree/` into an authority source.
- Adding external connectors.
- Introducing a separate frontend build pipeline.

## 16. Recommended Next Step

Implement `Slice UI-1` first. It is the lowest-risk slice because it fixes navigation, responsive shell, and favicon behavior while preserving all backend and governance contracts.

Minimum implementation sequence for UI-1:

1. Add or refactor shared page shell helper in `system/runtime/api/routers/surface.py`.
2. Add mode rail and context bar to `/surface` and high-traffic surface pages.
3. Add responsive CSS for tables, preformatted blocks, and UUID text.
4. Fix favicon 404 with the lowest-risk local route/asset.
5. Extend only the tests needed to confirm navigation and mobile-safe markup.
6. Run py_compile and unittest.
7. Run targeted Playwright visual check.
8. Record results in `agent/ops/`.

After `Slice UI-1`, run:

```powershell
python -m py_compile system/runtime/api/main.py system/runtime/api/routers/surface.py
python -m unittest discover -s system/tests -v
```

Then run a targeted Playwright visual check against the cockpit pages used in `COCKPIT_USABILITY_REPORT_2026-04-12.md`.
