# Actionable Queue Views

Date: 2026-04-10

Decision: Phase 12 is limited to actionable operational queues and views derived from executable state.

In scope:
- `ACTIVE_DECISION_QUEUE` as the combined actionable queue for pending proposals and recent decision outcomes;
- `RECENT_CHANGES` as the live event-driven feed for domain-scoped changes;
- publication into `tree/domains/<domain_id>/projections/`;
- navigation from the human and agent surfaces back to proposal, decision, object history, and published snapshot artifacts.

Out of scope:
- cockpit rich;
- graph UI;
- reentry complete;
- approve/reject agentive;
- MCP complete;
- reconciliation/canonicalization;
- advanced project/reunion projections;
- advanced agent automation.

Operational effect:
- projections remain derived from executable SQLite state;
- treefolder artifacts stay non-sovereign;
- no new mutation path is introduced by these views.
