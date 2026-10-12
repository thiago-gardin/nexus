# Proposal — Federated ontology / workflow alignment (V0)

Status: **DRAFT / HUMAN REVIEW** | Date: 2026-10-12
Scope: Nexus semantic federation ↔ Thiago's OS Control Plane procedural supervision.
Authority: Design proposal only; not a runtime migration, schema change, or normative spec.
Control Plane: https://docs.google.com/spreadsheets/d/1h3wjNxaQQhCK0FAwcA1hvnI49HMck2xjPHcv6LUUwy0/edit

## Thesis

Every workflow presupposes a representation of the context in which it operates. Its presupposed ontology can be explicit, implicit, or ambiguous. Compatibility with related federated domain ontologies must be assessed independently from workflow execution, maturity, usage, and health. Procedures can reveal domain ontology gaps; existing domains can require procedure adaptation. Neither should be silently modified.

## Preserve existing ontology

- **Workflow** remains the stable functional end-to-end identity. Protocol, skill, pipeline, script, automation, agent/runtime and state are implementations, not competing workflow classes.
- **Domain** is a contextual, semantic and authority boundary; its knowledge store can be federated, not necessarily owned or physically stored in Nexus.
- **System/subsystem, capability, implementation, workflow, relation** continue to have their existing Thiago's OS Control Plane meanings. A Nexus domain is **not automatically** an OS system/subsystem.
- Nexus SQLite executable core remains authoritative for Nexus objects. `tree/` remains materialization. The Google Sheet remains the supervisory Control Plane for Thiago's OS.
- Existing Nexus governance: proposals/decisions and human approval for critical mutations; never mutate `system/00_specs/`, `AGENTS.md`, `WORKSPACE_CONTRACT.md`, or human-owned `CURRENT_STATE.md` as part of this proposal.

## Candidate conceptual objects (not enacted schema)

1. **Federated domain**: `domain_id`, scope, ontology reference/version, authority, source/provenance.
2. **Federated relation**: `relation_id`, source_domain_id, target_domain_id, relation semantics, direction, evidence, allowed usage.
3. **Workflow**: existing `workflow_id`, purpose, input/transformation/output, current implementations.
4. **Ontological contract**: `contract_id`, workflow_id, concept/relation requirements, semantics, constraints, source/version, explicitness (`EXPLICIT|IMPLICIT|AMBIGUOUS|UNKNOWN`).
5. **Alignment assessment**: `assessment_id`, workflow_id, domain_id, contract_id, domain ontology version, assertion/evidence, compatibility (`COMPATIBLE|PARTIAL|INCOMPATIBLE|UNDETERMINED`), issue type (`GAP|CONFLICT|AMBIGUITY|LEGITIMATE_VARIANCE|NONE`), resolution proposal, authority gate, verification status.

Assessment grain is **workflow × domain × contract × domain ontology version**, not one global workflow rating. If a workflow uses multiple domains, evaluate each and their relevant cross-domain mappings. The same vocabulary can represent different things in legitimate contexts; compatibility does not imply identity.

## Candidate relation vocabulary (do not register before evaluation)

- `WORKFLOW_USES_DOMAIN` (scope of contextual operation, not ownership).
- `WORKFLOW_REQUIRES_CONCEPT` (semantic precondition).
- `CONCEPT_MAPPED_TO` (typed, directional, provenance-carrying correspondence).
- `DOMAIN_RELATED_TO_DOMAIN` (only with an explicit relation type and authority).
- `ALIGNMENT_ASSESSES` (evaluation evidence, not ontological truth).
- `PROPOSAL_REMEDIATES` (proposed intervention, not automatic approval).

Evaluate whether the current Nexus entity/relation/version/proposal primitives and the Control Plane's existing `06_RELATIONS` can express these without new types. Avoid an unnecessary parallel graph.

## Reconciliation routes

1. Procedure adapts to stable, authoritative domain semantics.
2. Domain evolves when a valid previously unrepresented concept is demonstrated.
3. Subdomain is considered if the conceptual boundary has distinct, durable semantics and authority.
4. Semantic mapping is preferred if two valid representations can interoperate without collapse.

Consolidation is **gated**: inspect dependents, sources, object versions, authority and impact; submit a proposal; validate acceptance before any mutation. "Unknown" and absence of evidence are not failures.

## V0 pilot (read-only)

Pick one *existing* Nexus workflow and at least two *existing* related domains, only after checking actual canonical identities. Extract concepts, relation assumptions, inputs/outputs; compare against domain ontology and versions; produce assessments with provenance, unresolved issues and candidate resolution. No synthetic IDs shall enter a live canonical registry as observed fact.

## Acceptance gates

- Crosswalk preserves Control Plane workflow identity and Nexus domain identity without conflation.
- Evidence labels distinguish OBSERVED, DECLARED, INFERRED, UNAVAILABLE.
- Explicitness and compatibility are separate fields; maturity, usage, health and criticality remain separate.
- At least one mapping or incompatibility claim is traceable to source text/object version.
- Human gate applied to domain edits, new subdomains, workflow semantics or schema changes.
- Reversibility: pilot can be removed without changing core domain/workflow state.
- No new runtime code or schema until a narrowly scoped implementation plan is approved.

## Control Plane mapping

Use existing `08_SUPERVISION` and `09_OBSERVATIONS` for this design run/architectural hypothesis, linked to SYS-007. Keep `02_SYSTEMS`, `03_CAPABILITIES`, `04_IMPLEMENTATION`, `05_WORKFLOWS`, `06_RELATIONS`, `07_REFERENCES` unchanged pending a pilot. If confirmed, propose a minimal crosswalk/assessment table rather than injecting ad-hoc columns throughout the workbook.

## Open decisions

- Is alignment a versioned first-class object or a specialized evaluation over current Nexus relations?
- Who owns authoritative domain ontology version references when knowledge is external?
- What minimum concept contract can be extracted reliably from implicit procedures?
- Which existing workflow + two domains make the most informative no-mutation pilot?
- Should the Control Plane store the full alignment facts or only their supervision/decision pointers?

No evidence of operational compatibility is claimed in this V0 proposal.
