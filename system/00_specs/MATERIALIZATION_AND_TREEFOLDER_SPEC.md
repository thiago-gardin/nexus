# NEXUS — Materialization and Treefolder Specification
## Version 0.3

## 1. Purpose
This document specifies the operational materialization regime of the Nexus and the minimum remote-readable treefolder publication model.

## 2. Scope
Included:
- payload model;
- projection model;
- semantic publication rules;
- remote-readable treefolder structure;
- reentry boundaries.

## 3. Out of Scope
Excluded:
- executable core schema beyond referenced IDs;
- cockpit UI behavior;
- MCP command surface.

## 4. Materialization Regime
### 4.1 Definition
The materialization regime transforms executable state into legible, versionable artifacts while preserving:
- identity;
- provenance;
- validation status;
- governance linkage;
- controlled reentry potential.

### 4.2 Core Functions
The materialization regime must:
- materialize payloads and projections;
- publish stable views;
- preserve object-to-artifact traceability;
- generate legible diffs;
- support remote reading;
- accept authorized edits in declared zones;
- convert eligible edits into structured proposals;
- trigger governed reentry.

## 5. Payload Model
```yaml
Payload:
  payload_id: string
  payload_type: raw_body|parsed_body|bio|description|transcript|attachment_extract|note|summary
  owner_object_type: source|entity|relation|decision|projection
  owner_object_id: string
  storage_ref: string
  format: md|txt|json|html|pdf|bin
  checksum: string
  editability: read_only|proposable_edit|editable_under_rule
  canonical_flag: boolean
  created_at: datetime
  updated_at: datetime
  version: integer
```

## 6. Projection Model
```yaml
Projection:
  projection_id: string
  projection_type: entity_view|relation_view|decision_view|domain_snapshot|meeting_context|project_state|thread_view
  source_refs: string[]
  payload_refs: string[]
  materialization_format: md|json|yaml
  storage_ref: string
  generated_by: string
  generation_scope: local|remote|published
  freshness_status: fresh|stale|rebuilding
  created_at: datetime
  updated_at: datetime
```

## 7. Publication Rules
1. Materialized artifacts never redefine primary identity.
2. External edits never mutate the executable core silently.
3. Editable artifacts must declare editability regime.
4. Materialized artifacts must be regenerable.
5. Reentry depends on rule, proposal, or authorized mutation.

## 8. Treefolder as Remote Interface
### 8.1 Status
While remote runtime access is not institutionally stable, the treefolder is the official remote navigation surface for humans and remote agents.

### 8.2 Requirements
The treefolder must be:
- human-legible;
- agent-navigable;
- convention-stable;
- versionable;
- indexed;
- partitioned by domain;
- ID-oriented;
- explicit about freshness, provenance, and artifact type.

### 8.3 Minimum Structure
```text
treefolder/
  START_HERE.md
  INDEX.md
  SYSTEM_STATUS.yaml

  domains/
    <domain_id>/
      DOMAIN_CONTRACT.yaml
      INDEX.md
      entities/
      projections/

  canonical/
    entities/
    relations/

  inbox/
    proposals/
```

### 8.4 Required Navigation Files
#### `START_HERE.md`
Must explain:
- what the treefolder is;
- how to navigate it;
- executable truth vs publishable truth;
- remote write restrictions;
- ID and status conventions.

#### `INDEX.md`
Must expose:
- domain list;
- links to local indexes;
- canonical zones;
- proposal areas;
- primary projections.

#### `SYSTEM_STATUS.yaml`
Must expose at minimum:
- publication_timestamp;
- publication_version;
- freshness_status;
- available_domains;
- pending_proposals_count;
- remote_write_policy.

## 9. Domain Publication Requirements
Each published domain must contain:
- `DOMAIN_CONTRACT.yaml`
- `INDEX.md`
- `entities/`
- `projections/`

## 10. Remote Write Policy
Remote agents may:
- read materialized artifacts;
- navigate indexes;
- inspect payloads and projections;
- write structured proposals only in explicitly allowed proposal zones.

Remote agents may not:
- mutate the executable core directly;
- overwrite canonical artifacts as sovereign truth;
- redefine identity outside governed reentry.

## 11. Reentry
### 11.1 Pipeline
```text
detect_edit_or_annotation
→ validate_editability_rule
→ parse_delta
→ map_to_structured_proposal
→ enqueue_decision_or_safe_mutation
→ emit_reentry_event
```

### 11.2 Reentry Constraints
- every reentry originates from a declared artifact;
- every reentry preserves source artifact reference;
- every accepted reentry produces event and version update.

## 12. Dependencies
- `CORE_RUNTIME_SPEC.md`
- `DOMAIN_AND_PIPELINE_SPEC.md`
- `AGENT_SURFACE_AND_MCP_SPEC.md`
