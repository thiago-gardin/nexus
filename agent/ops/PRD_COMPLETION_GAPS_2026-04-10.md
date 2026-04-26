# PRD Completion Gaps — Phase 14 Foundation Slice

## Status

Recorded after the Phase 14 foundation implementation slice.

This is not a proposal to rewrite `system/00_specs/`. The specs remain read-only and authoritative.

**Superseded by:** `agent/ops/PRD_ACCEPTANCE_CLOSURE_2026-04-10.md` for Phase 20 closure status.

The table below is retained as historical Phase 14 evidence. It should no longer be read as the current active PRD gap list.

## Implemented In This Slice

- Schema-backed repositories/services now cover sources, payloads, projections, governance rules, and existing job tables.
- `POST /ingest` persists raw and parsed payloads for local `md`, `txt`, and `json` content.
- Minimum typing creates proposed entity/relation candidates without silent canonical promotion.
- Minimum reconciliation detects duplicate entity labels and creates merge proposals.
- Payload, projection, search, materialization, export, decision override, and reentry APIs exist.
- Formal MCP adapter exists and smoke test lists the 9 normative tools.
- Human cockpit has a local graph endpoint and Jinja/JS graph page.
- Full system regression passed with `python -m unittest discover -s system/tests -v`.

## Remaining Gaps

| Area | Remaining gap | Reason not closed in this slice |
|---|---|---|
| Full cockpit | Domain explorer/object inspector/payload viewer/timeline/decision queue/provenance/reentry panels are not yet fully modularized as a complete cockpit | This slice delivered graph foundation and preserved the existing human review surface; full cockpit breadth needs a dedicated UI slice |
| Canonicalization | Merge proposal approval exists, but advanced canonical/separation handling is still minimal | The current slice implemented safe proposal-first duplicate handling, not a full canonicalization engine |
| Projections | Projection records are persisted, but meeting/project semantics remain minimal | The persistence path exists; domain-specific projection builders still need follow-up implementation |
| Tree expansion | Existing `tree/` publication remains derived and operational, but canonical zones/inbox/proposals are not expanded to full PRD breadth | Avoided broad materialization restructuring in the same runtime/API slice |
| Source connectors | Generic local ingestion exists, but external email/calendar/chat connectors are not implemented | The agreed assumption defined multi-source ingestion as local generic API, not real connector work |
| PRD acceptance closure | No single full multi-domain acceptance scenario yet exercises all Phase 14-20 targets end-to-end | Requires a dedicated closure slice after remaining cockpit/projection/tree gaps are addressed |

## Historical Interpretation At Time Of Recording

At the time of this record, the repository had moved from governance realignment into the Phase 14 Spec Completion Program.

That interpretation has since been superseded by the Phase 20 PRD acceptance closure record.
Current work should be read from `agent/CURRENT_MISSION.md`, `agent/plan/ACTIVE_TRACK.md`, `SYSTEM_STATUS.yaml`, and `agent/ops/PRD_ACCEPTANCE_CLOSURE_2026-04-10.md`.
