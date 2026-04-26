# NEXUS — Core Runtime Specification
## Version 0.3

## 1. Purpose
This document specifies the local executable core of the Nexus.

## 2. Scope
Included:
- persistence model;
- core object model;
- governance and event infrastructure;
- mutation classes;
- audit requirements;
- asynchronous jobs.

## 3. Out of Scope
Excluded:
- remote treefolder publication details;
- cockpit UI composition;
- MCP interface details beyond authority boundaries.

## 4. Core Components
### 4.1 `core/storage`
- `db`
- `migrations`
- `repositories`
- `transaction_manager`

### 4.2 `core/domain_runtime`
- `domain_registry`
- `domain_contract_loader`
- `entity_type_registry`
- `relation_type_registry`
- `rule_scope_resolver`

### 4.3 `core/ingestion`
- `source_registry`
- `parser_router`
- `ingestion_jobs`
- `provenance_manager`

### 4.4 `core/typing`
- `candidate_extractor`
- `attribute_extractor`
- `mention_extractor`
- `confidence_scorer`

### 4.5 `core/reconciliation`
- `candidate_matcher`
- `canonical_resolution`
- `merge_engine`
- `ambiguity_queue`

### 4.6 `core/governance`
- `rule_registry`
- `decision_queue`
- `approval_engine`
- `override_handler`

### 4.7 `core/events`
- `event_log`
- `change_diff`
- `replay_support`

## 5. Persistence
### 5.1 Engine Strategy
Recommended progression:
- SQLite for bootstrap;
- DuckDB as analytical companion;
- Postgres local when runtime scale requires it.

### 5.2 Responsibilities of the Executable Core
- stable identity;
- relational integrity;
- canonical versioning;
- mutation under authority;
- auditability;
- reconciliation;
- decision queues.

## 6. Core Data Model
### 6.1 Domain
```yaml
Domain:
  domain_id: string
  name: string
  description: string
  cognitive_purpose: string
  status: active|inactive|draft|deprecated
  owner_human: string|null
  owner_agent: string|null
  source_types_supported: string[]
  local_entity_types: string[]
  relation_types: string[]
  promotion_rules: string[]
  governance_dependencies: string[]
  version: integer
  created_at: datetime
  updated_at: datetime
```

### 6.2 Source
```yaml
Source:
  source_id: string
  domain_id: string
  source_type: string
  source_origin: string
  source_uri: string|null
  storage_ref: string|null
  raw_payload_ref: string
  parsed_payload_ref: string|null
  checksum: string
  ingestion_status: pending|parsed|failed|reprocessed
  metadata: object
  provenance_record: object
  created_at: datetime
  updated_at: datetime
```

### 6.3 Entity
```yaml
Entity:
  entity_id: string
  scope: local|canonical
  domain_id: string|null
  entity_type: string
  label: string
  short_description: string|null
  attributes: object
  aliases: string[]
  confidence: float
  validation_status: proposed|validated|rejected|contested
  canonical_candidate_flag: boolean
  provenance_refs: string[]
  payload_refs: string[]
  version: integer
  created_at: datetime
  updated_at: datetime
```

### 6.4 Relation
```yaml
Relation:
  relation_id: string
  source_entity_id: string
  target_entity_id: string
  relation_type: string
  directionality: directed|undirected
  domain_context: string|null
  evidence_refs: string[]
  confidence: float
  validation_status: proposed|validated|rejected|contested
  asserted_by: string
  validated_by: string|null
  version: integer
  created_at: datetime
  updated_at: datetime
```

### 6.5 Event
```yaml
Event:
  event_id: string
  event_type: string
  target_object_type: domain|source|entity|relation|decision|rule|payload|projection
  target_object_id: string
  performed_by: string
  performed_via: human_ui|agent_local|agent_remote|system|cli|api
  reason: string|null
  payload: object
  before_state_ref: string|null
  after_state_ref: string|null
  reversible_flag: boolean
  created_at: datetime
```

### 6.6 Decision
```yaml
Decision:
  decision_id: string
  decision_type: approval|rejection|override|merge|split|promotion|demotion|edit_acceptance
  proposal_ref: string
  target_refs: string[]
  proposed_by: string
  decided_by: string|null
  rationale: string|null
  decision_state: pending|approved|rejected|overridden|expired
  created_at: datetime
  updated_at: datetime
```

### 6.7 GovernanceRule
```yaml
GovernanceRule:
  rule_id: string
  rule_type: identity|promotion|confidence|provenance|arbitration|validation|reentry
  name: string
  scope: string
  logic_description: string
  machine_executable_repr: object|null
  human_readable_repr: string
  applies_to: string[]
  priority: integer
  status: active|inactive|deprecated|draft
  created_by: string
  approved_by: string|null
  version: integer
  created_at: datetime
  updated_at: datetime
```

### 6.8 ObjectVersion
```yaml
ObjectVersion:
  version_id: string
  object_type: string
  object_id: string
  version_number: integer
  serialized_state_ref: string
  created_at: datetime
  created_by: string
```

## 7. Minimum Tables
- `domains`
- `sources`
- `entities`
- `entity_aliases`
- `relations`
- `events`
- `decisions`
- `governance_rules`
- `payloads`
- `projections`
- `object_versions`
- `ingestion_jobs`
- `materialization_jobs`
- `reentry_jobs`

## 8. Mutation Regime
### 8.1 Class A — Read
No state change.

### 8.2 Class B — Proposal
Changes proposal queues, not stabilized state.

### 8.3 Class C — Authorized Mutation
Changes executable state within pre-approved safe classes.

### 8.4 Class D — Critical Mutation
Requires explicit rule or validation gate.

## 9. Minimum Authority Matrix
| Operation | Human | Local Agent | Remote Agent |
|---|---|---|---|
| Read executable core | yes | yes | no |
| Create proposal | yes | yes | yes |
| Authorized mutation | yes | yes, if permitted | no |
| Critical mutation | yes | gated only | no |
| Approve decision | yes | no by default | no |
| Override | yes | no by default | no |

## 10. Audit Requirements
Every relevant change must preserve:
- actor;
- execution surface;
- target object;
- rationale;
- previous state;
- resulting state;
- reversibility;
- enabling or gating rule.

## 11. Minimum Audit Functions
```yaml
audit_functions:
  - get_object_history
  - compare_versions
  - list_events_by_actor
  - trace_decision_chain
  - replay_change_sequence
  - compare_core_vs_materialization
```

## 12. Jobs
```yaml
Job:
  job_id: string
  job_type: string
  status: pending|running|completed|failed
  target_ref: string
  started_at: datetime|null
  finished_at: datetime|null
  logs_ref: string|null
```

Minimum job classes:
- ingestion;
- parse;
- typification;
- reconciliation;
- materialization;
- reentry;
- projection refresh.

## 13. Dependencies
- `DOMAIN_AND_PIPELINE_SPEC.md`
- `MATERIALIZATION_AND_TREEFOLDER_SPEC.md`
- `AGENT_SURFACE_AND_MCP_SPEC.md`
