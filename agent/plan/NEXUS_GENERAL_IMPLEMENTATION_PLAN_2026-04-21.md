# Nexus General Implementation Plan

Date: 2026-04-21

Purpose: define a complete product implementation plan for Nexus based on the current local repo, the expected capabilities in the specs, and useful ideas from V1 and IA-Studio Bootstrap. This plan deliberately does not treat prior scoping decisions as fixed constraints when they block the product.

## Target product

Nexus should become a local-first operational knowledge system where a human and authorized local agents can:

- Create and version domains.
- Register sources.
- Run ingestion.
- Create and edit entities and relations.
- Attach evidence and provenance.
- Validate, reject, override, open conflict cases, and promote canonical objects.
- Inspect full history and materialized projections.
- Operate the same capabilities through cockpit, local API, and MCP according to explicit authority policies.

Remote or delegated agents may remain proposal-first by default. The missing piece is a complete local operational control plane.

## Principles

1. Keep the current Python/FastAPI/SQLite runtime as the implementation base.
2. Preserve evented governance and materialization as non-negotiable product strengths.
3. Add product operations vertically: schema, service, API, cockpit, MCP, tests, materialization.
4. Separate authority modes instead of forcing every surface into one policy:
   - human cockpit: direct governed mutation;
   - local trusted agent: policy-controlled mutation plus proposal where required;
   - remote agent: read/proposal by default.
5. Use IA-Studio Bootstrap as a product prototype, not as the runtime architecture.
6. Treat V1 as intent lineage: event log, conflict visibility, and causal audit remain central.

## Phase 0 - Product rebaseline

Objective: establish a new implementation baseline that acknowledges the current gap between local-first acceptance and full product readiness.

Deliverables:

- Update planning docs to define the next product phase.
- Freeze the comparative map as the rationale for reopening product completion.
- Define acceptance criteria for authoring, ingestion, governance, MCP parity, and materialization.

Acceptance:

- The team can distinguish "current local-first runtime works" from "full product workflows are complete".
- Missing capabilities are tracked as product gaps, not only hardening backlog.

## Phase 1 - Domain authoring and versioned charters

Objective: make domains operationally creatable and evolvable.

Deliverables:

- Domain creation flow.
- Domain version / charter model.
- Active domain version selection.
- Allowed entity types, relation types, payload/source types, required fields, and promotion rules.
- Cockpit domain and charter forms.
- API and MCP tools for domain lifecycle.

Acceptance:

- A user can create a new domain from the cockpit.
- A user can create and activate a domain version.
- Entity and relation authoring use the active domain charter.
- All changes emit events and are materialized.

## Phase 2 - Operational cockpit authoring

Objective: turn the cockpit from review/inspection into the primary local product surface.

Deliverables:

- Action panel modeled after the IA-Studio Bootstrap workflow.
- Create entity form.
- Create relation form.
- Register source form.
- Edit object metadata under governance.
- Search/select source and target objects.
- Validation and rejection controls for objects, not only proposals.

Acceptance:

- A user can build a small domain graph manually from the cockpit.
- A user can see evidence, status, and provenance immediately after creation.
- Cockpit actions use the same services and transaction/event discipline as API and MCP.

## Phase 3 - Source and ingestion control plane

Objective: expose ingestion as an operational workflow, not just an API endpoint.

Deliverables:

- Source registry cockpit.
- Ingestion run page.
- Run ingestion for `md`, `txt`, and `json` sources.
- Candidate review queue by source/run/domain.
- Re-run and failure inspection.
- Materialized ingestion summaries.

Acceptance:

- A user can register a local Markdown or JSON source and run ingestion from the cockpit.
- Generated candidates are visible with evidence and validation status.
- Failed ingestion runs are explainable and auditable.

## Phase 4 - Governance, conflict, and canonical workflows

Objective: make the institutional layer usable, not only internally coherent.

Deliverables:

- Object-level validate/reject.
- Conflict case model and cockpit flow.
- Canonical entity/relation promotion flow.
- Merge/separation review improvements.
- Decision queue with clearer action types.

Acceptance:

- A user can resolve candidate objects into accepted, rejected, conflicted, or canonical states.
- Conflicts are visible and cannot silently disappear.
- Canonical promotion records evidence and decision provenance.

## Phase 5 - API and MCP operational parity

Objective: expose complete local operations to agents without weakening remote safety.

Deliverables:

- Expand local API around domain, source, authoring, validation, conflict, canonical, ingestion, and audit operations.
- Add MCP tools for local trusted operation.
- Keep remote proposal-only policy available.
- Document tool authority and expected actor types.

Acceptance:

- The MCP can create domains, domain versions, sources, entities, relations, validations, conflict cases, and canonical promotions when running under local trusted authority.
- Remote profiles can still be limited to read/proposal tools.
- Every mutation path uses service-layer governance.

## Phase 6 - Materialization and audit completion

Objective: make every new product operation visible in `tree/` and auditable.

Deliverables:

- Domain charter pages.
- Source registry pages.
- Ingestion run pages.
- Conflict case pages.
- Canonical object indexes.
- Object lifecycle timelines.
- Core-vs-materialization comparison.
- Replay/audit report for selected objects or domains.

Acceptance:

- A human can reconstruct why an entity or relation exists from materialized artifacts.
- A user can compare runtime state and materialized state.
- Audit tools cover the new authoring and governance flows.

## Phase 7 - Project Governance domain module

Objective: implement the first practical domain module using the new product surface.

Deliverables:

- Project Governance domain template.
- Entity and relation type charter.
- Markdown/manual ingestion recipe.
- Cockpit workflow for project status, decisions, tasks, and sessions.
- Materialized project dashboard.

Acceptance:

- Nexus can manage its own project governance domain using the general product capabilities.
- Manual and Markdown ingestion both work without custom bypasses.

## Phase 8 - Email/PST domain module

Objective: add a deferred external-source module after the ingestion control plane is mature.

Deliverables:

- Email domain charter.
- PST/source registration adapter.
- Batch ingestion with provenance.
- Message/thread/contact entities.
- Evidence links back to source records.
- Conflict and canonicalization workflows for contacts/projects/topics.

Acceptance:

- Email ingestion is an optional module, not a core dependency.
- It uses the same source, ingestion, entity, relation, evidence, validation, and materialization infrastructure.

## Phase 9 - Product hardening and packaging

Objective: make local operation dependable for repeated use.

Deliverables:

- Test expansion for all vertical flows.
- Cockpit usability hardening.
- MCP transport hardening.
- Backup/export/import routine.
- Startup/health command.
- Documentation for human and local-agent operation.

Acceptance:

- A new local workspace can bootstrap Nexus, create a domain, ingest sources, validate objects, publish materialization, and operate through cockpit/MCP without code edits.

## Recommended sequencing

1. Rebaseline product truth.
2. Add domain versioning and source registration.
3. Add cockpit action panel for manual entity/relation/source creation.
4. Add object validation/rejection and conflict/canonical flows.
5. Expand MCP/API parity.
6. Expand materialization and audit.
7. Build practical domain modules.
8. Harden packaging and tests.
