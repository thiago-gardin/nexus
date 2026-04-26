# PRD Acceptance Closure — Phase 20

## Status

Phase 20 PRD acceptance closure is complete under the approved local-first assumptions.

This is not a proposal to rewrite `system/00_specs/`. The specs remain read-only and authoritative.

## Closure Evidence

- Phase 15 commit: `19bc7e7` — pipeline jobs and reconciliation completion.
- Phase 16 commit: `aa65687` — meeting/project projections and treefolder indexes.
- Phase 17 commit: `2a6bb3b` — modular cockpit panels and graph filters.
- Phase 18 commit: `e382c5d` — tree inbox proposal import and real MCP calls.
- Phase 19 commit: `ccc3c7b` — multi-domain PRD acceptance scenario.
- Final validation before governance closure: `python -m unittest discover -s system/tests -v`, 35 tests passed.

## Acceptance Coverage

The acceptance scenario covers:

- multiple domains;
- local `json`, `md`, and `txt` ingestion;
- source, raw payload, parsed payload, entity candidate, and relation candidate creation;
- duplicate reconciliation with proposal-first merge handling;
- human approval through the decision API;
- object versioning and event/audit reconstruction;
- useful projection generation;
- `tree/` publication with payload/projection/canonical/proposal indexes;
- MCP read through the formal adapter;
- cockpit object/payload/projection/timeline surfaces.

## REST vs MCP Closure

The registered thesis remains:

- REST/local is the current operational local contract.
- MCP is a formal adapter over the current services.
- MCP does not replace REST/local in this closure.
- The MCP surface is not merely listed; all 9 normative tools are real-call tested.

## Residual Drift

| Area | Residual drift | Disposition |
|---|---|---|
| External connectors | Email/calendar/chat connectors are not implemented | Explicitly out of scope by approved assumption; local generic ingestion satisfies this closure |
| Canonicalization | Reconciliation has alias/scored groups, merge proposals, and separation proposals, but not a full semantic canonicalization engine | Not claimed; future hardening can extend matching semantics without changing the proposal-first authority model |
| Cockpit frontend | Cockpit is FastAPI/Jinja/local JS, not a separate frontend build | Intentional; plan required no Node build and no CDN |
| MCP transport | MCP is an adapter over services, REST/local remains operational | Intentional; transport hardening can proceed without removing REST/local |
| CURRENT_STATE.md | Human-owned state may still require narrative sync | Not edited by agent; sync should be proposed separately if the human wants the state summary updated |

## Closure Statement

The Nexus repo now has a verified local-first PRD acceptance slice across object layer, ingestion, reconciliation, projections, materialization, human cockpit, agent/MCP surface, remote proposal import, and audit reconstruction.

Remaining items are not hidden blockers for this closure; they are explicitly scoped as future hardening or out-of-scope assumptions.
