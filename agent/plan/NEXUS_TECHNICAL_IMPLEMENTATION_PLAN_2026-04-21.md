# Nexus Technical Implementation Plan

Date: 2026-04-21

Derived from: `agent/plan/NEXUS_GENERAL_IMPLEMENTATION_PLAN_2026-04-21.md`

Implementation base: current Python/FastAPI/SQLite/Jinja Nexus runtime.

## Technical stance

Do not port the runtime to the IA-Studio stack. Use IA-Studio Bootstrap as a behavioral prototype for cockpit actions and product workflows. Implement the product-complete version in the existing Python runtime so that governance, tests, transactions, and materialization remain coherent.

## Target vertical slice pattern

Every new capability should land as one vertical slice:

1. Migration/schema.
2. Repository methods.
3. Service-layer operation.
4. Event emission and object versioning.
5. API route.
6. Cockpit view/form where human-facing.
7. MCP tool where agent-facing.
8. Materialization output.
9. Unit/integration tests.

## Slice T0 - Baseline verification

Tasks:

- Run the existing test suite.
- Capture current DB schema and migration state.
- Verify current cockpit and MCP tool registration.
- Record known failures separately from new work.

Acceptance:

- Existing behavior is reproducible before schema expansion.
- New failures can be attributed to new slices.

## Slice T1 - Domain versions

Schema:

- Add `domain_versions` with:
  - `domain_version_id`
  - `domain_id`
  - `version_label`
  - `status`
  - `charter`
  - `allowed_entity_types`
  - `allowed_relation_types`
  - `allowed_payload_types`
  - `required_fields`
  - `promotion_rules`
  - `created_at`
  - `activated_at`
  - `last_event_id`

Services:

- `DomainVersionService.create_domain_version`
- `DomainVersionService.activate_domain_version`
- `DomainVersionService.get_active_domain_version`

API:

- `POST /domains`
- `POST /domains/{domain_id}/versions`
- `POST /domain-versions/{domain_version_id}/activate`
- `GET /domains/{domain_id}/active-version`

Cockpit:

- Domain create page.
- Domain version editor.
- Active charter view.

MCP:

- `list_domains`
- `create_domain`
- `create_domain_version`
- `activate_domain_version`
- `get_domain_version`

Tests:

- Domain creation emits event.
- Domain version activation deactivates prior active version.
- Active charter is used by later entity/relation validation.

## Slice T2 - Source registration

Schema:

- Reuse current source table if sufficient; otherwise add missing fields for:
  - `source_type`
  - `uri_or_path`
  - `domain_id`
  - `domain_version_id`
  - `checksum`
  - `ingestion_status`
  - `metadata`

Services:

- `SourceService.register_source`
- `SourceService.update_source_status`
- `SourceService.list_sources_by_domain`

API:

- `POST /sources`
- `GET /domains/{domain_id}/sources`
- `GET /sources/{source_id}`

Cockpit:

- Source registration form.
- Source detail page with runs and generated objects.

MCP:

- `register_source`
- `list_sources`

Tests:

- Registering a source creates provenance and event trace.
- Duplicate source handling is deterministic.

## Slice T3 - Ingestion runs as first-class objects

Schema:

- Reuse jobs if appropriate, or add `ingestion_runs` with:
  - `ingestion_run_id`
  - `source_id`
  - `domain_id`
  - `domain_version_id`
  - `status`
  - `started_at`
  - `completed_at`
  - `error`
  - `candidate_counts`
  - `last_event_id`

Services:

- `IngestionRunService.start_run`
- `IngestionRunService.complete_run`
- `IngestionRunService.fail_run`
- Integrate existing `IngestionService.ingest`

API:

- `POST /ingestion-runs`
- `GET /ingestion-runs/{run_id}`
- `GET /domains/{domain_id}/ingestion-runs`

Cockpit:

- Run ingestion button from source detail.
- Run detail and candidate review.

MCP:

- `run_ingestion`
- `get_ingestion_run`

Tests:

- Successful `md/txt/json` ingestion creates run, candidates, events, and materialization.
- Failed runs preserve errors without partial silent success.

## Slice T4 - Manual entity authoring

Services:

- Add an authoring entrypoint that validates against active domain version.
- Route all entity creation through the same service used by ingestion when possible.

API:

- `POST /entities`
- `GET /domains/{domain_id}/entities`

Cockpit:

- Entity form with dynamic fields from active domain version.
- Evidence/provenance fields.

MCP:

- `create_local_entity`
- `list_entities`

Tests:

- Required fields are enforced.
- Created entities carry domain, active domain version, provenance, validation status, and event trace.

## Slice T5 - Manual relation authoring

Services:

- Validate source/target entity existence.
- Validate relation type against active domain version.
- Require evidence/provenance or explicit manual-origin reason.

API:

- `POST /relations`
- `GET /domains/{domain_id}/relations`

Cockpit:

- Relation form with source/target search.
- Relation type selection from active charter.

MCP:

- `create_relation_assertion`
- `list_relations`

Tests:

- Invalid relation type is rejected.
- Missing endpoints are rejected.
- Relation event and materialization are produced.

## Slice T6 - Object validation and rejection

Services:

- `GovernanceService.validate_object`
- `GovernanceService.reject_object`
- Keep proposal approval separate from object validation.

API:

- `POST /objects/{object_type}/{object_id}/validate`
- `POST /objects/{object_type}/{object_id}/reject`

Cockpit:

- Validate/reject controls on entity, relation, payload, and candidate views.

MCP:

- `validate_object`
- `reject_object`

Tests:

- Validation status transitions are constrained.
- Rejection requires reason.
- Events record actor and authority.

## Slice T7 - Conflict cases

Schema:

- Add or expand `conflict_cases` with:
  - `conflict_case_id`
  - `domain_id`
  - `object_type`
  - `object_id`
  - `conflict_type`
  - `status`
  - `description`
  - `resolution`
  - `opened_by`
  - `resolved_by`
  - `last_event_id`

Services:

- `ConflictService.open_conflict`
- `ConflictService.resolve_conflict`

API:

- `POST /conflict-cases`
- `POST /conflict-cases/{id}/resolve`
- `GET /domains/{domain_id}/conflict-cases`

Cockpit:

- Conflict queue.
- Conflict detail and resolution form.

MCP:

- `open_conflict_case`
- `resolve_conflict_case`

Tests:

- Contested objects are visible in queues.
- Resolution emits decision events and updates status.

## Slice T8 - Canonical promotion

Schema:

- Add `canonical_entities` and, if needed, `canonical_relations`.
- Link local entities/relations to canonical objects with evidence.

Services:

- `CanonicalService.promote_entity`
- `CanonicalService.link_local_entity`
- `CanonicalService.merge_canonical_entities`

API:

- `POST /canonical/entities`
- `POST /entities/{entity_id}/promote`
- `GET /domains/{domain_id}/canonical-entities`

Cockpit:

- Promotion candidates.
- Canonical detail page.

MCP:

- `promote_to_canonical`
- `list_canonical_entities`

Tests:

- Promotion is idempotent where possible.
- Canonical links are auditable.
- Merge conflicts require explicit decision.

## Slice T9 - Materialization expansion

Publisher outputs:

- `tree/domains/<domain_id>/charter.md`
- `tree/domains/<domain_id>/sources.md`
- `tree/domains/<domain_id>/ingestion_runs.md`
- `tree/domains/<domain_id>/conflicts.md`
- `tree/domains/<domain_id>/canonical_entities.md`
- Object lifecycle timelines.

Audit:

- Add core-vs-materialization comparison.
- Add replay for selected object or event chain.

Tests:

- Materialization includes all new object classes.
- Published indexes match DB counts.

## Slice T10 - MCP authority profiles

Implementation:

- Keep the existing nine normative read/proposal tools.
- Add local trusted tools behind explicit actor/profile configuration.
- Enforce remote proposal-only mode by configuration, not by missing product capability.

Profiles:

- `remote_read_propose`: current restrictive surface.
- `local_operator`: controlled mutation surface.
- `human_supervised`: mutation allowed when tied to cockpit/session context.

Tests:

- Restricted profile cannot mutate.
- Local profile can mutate through service layer.
- All MCP mutations emit events and respect validation rules.

## Slice T11 - Cockpit action panel

Implementation:

- Add an action panel route and partial templates.
- Keep Jinja unless a separate frontend migration is explicitly approved.
- Mirror IA-Studio Bootstrap's practical grouping:
  - Entity
  - Relation
  - Domain/charter
  - Source/ingestion
  - Governance

Tests:

- Form submissions work end-to-end.
- Error states are visible.
- Created/changed objects are inspectable immediately.

## Slice T12 - Domain modules

Project Governance module:

- Domain template.
- Entity types: project, task, decision, session, source, milestone.
- Relation types: depends_on, decided_by, belongs_to, updates, references.
- Markdown/manual ingestion recipes.

Email/PST module:

- Domain template.
- Source adapter after source/ingestion plane is stable.
- Entity types: message, thread, person, organization, topic, attachment.
- Relation types: sent_by, sent_to, replies_to, mentions, attached_to, relates_to_project.

Acceptance:

- Modules use general infrastructure and do not create bypass-only code paths.

## Required regression suite

Commands should be finalized after implementation starts, but each slice should preserve:

- `python -m unittest discover -s system/tests -t . -p "test_*.py"`
- API integration tests for new routes.
- MCP registration/call tests.
- Cockpit form submission tests.
- Materialization count and file-existence tests.

## Main implementation risks

1. Schema growth without service convergence.

   Mitigation: every new table gets repository and service tests before cockpit work.

2. Direct mutation bypassing governance.

   Mitigation: all API, cockpit, ingestion, and MCP mutation paths call service-layer operations.

3. Confusing proposal approval with object validation.

   Mitigation: keep separate state machines and document transitions.

4. Over-importing IA-Studio architecture.

   Mitigation: copy workflow ideas, not stack or data shortcuts.

5. MCP safety regression.

   Mitigation: profile-based tool exposure and tests for restricted mode.
