# NEXUS — Domain and Pipeline Specification
## Version 0.3

## 1. Purpose
This document specifies domain contracts and the semantic-operational pipelines that transform heterogeneous sources into executable and publishable Nexus objects.

## 2. Scope
Included:
- domain contracts;
- ingestion pipeline;
- typing pipeline;
- reconciliation pipeline;
- governance touchpoints.

## 3. Out of Scope
Excluded:
- detailed UI behavior;
- remote publication layout details;
- low-level database migration syntax.

## 4. Domain Contract
Each domain must define at minimum:
```yaml
domain_contract:
  domain_id: string
  name: string
  cognitive_purpose: string
  source_types_supported: string[]
  local_entity_types: string[]
  relation_types: string[]
  payload_types: string[]
  promotion_rules: string[]
  governance_dependencies: string[]
```

## 5. Domain Restrictions
- no domain without explicit cognitive purpose;
- no domain without defined local types;
- no stabilized typing outside domain context;
- no promotion rule without governance linkage.

## 6. Ingestion Pipeline
```text
register_source
→ persist_raw
→ extract_metadata
→ parse_source
→ persist_parsed
→ emit_ingestion_event
→ enqueue_typification
```

### 6.1 Interface
```yaml
ingest(input):
  domain_id: string
  source_type: string
  payload_ref: string
  metadata: object
returns:
  source_id: string
  ingestion_status: string
```

## 7. Typing Pipeline
```text
load_parsed_source
→ apply_domain_grammar
→ extract_entity_candidates
→ extract_relation_candidates
→ extract_payload_candidates
→ attach_evidence
→ score_confidence
→ persist_proposals
→ emit_typification_event
→ enqueue_validation_or_reconciliation
```

### 7.1 Typing Obligations
- preserve evidence linkage;
- preserve ambiguity when unresolved;
- avoid silent canonical promotion;
- generate explicit proposal objects where needed.

## 8. Reconciliation Pipeline
```text
load_candidates
→ detect_duplicates
→ score_matches
→ propose_merge_or_separation
→ apply_rule_if_safe
→ enqueue_decision_if_critical
→ persist_result
→ emit_reconciliation_event
```

### 8.1 Reconciliation Principles
- reconciliation is revisable assertion, not metaphysical finality;
- automatic decisions only under approved rules;
- merge operations must preserve lineage;
- uncertain cases must remain inspectable.

## 9. Cross-Domain Promotion
Canonical entities may emerge only when:
- recurrence is sufficient;
- evidence spans enough support;
- governance conditions are satisfied;
- validation status permits stabilization.

## 10. Governance Hooks
The pipeline layer must expose hooks for:
- confidence rules;
- identity rules;
- reconciliation rules;
- promotion rules;
- reentry rules.

## 11. Minimum Domain Outputs
A functioning domain must be able to produce:
- registered sources;
- parsed artifacts;
- local entities;
- local relations;
- evidence links;
- proposal queues;
- domain projections.

## 12. Dependencies
- `CORE_RUNTIME_SPEC.md`
- `MATERIALIZATION_AND_TREEFOLDER_SPEC.md`
- `INTERNAL_APIS_AND_INTEGRATION_SPEC.md`
