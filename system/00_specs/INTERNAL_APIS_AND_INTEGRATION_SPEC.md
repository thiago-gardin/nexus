# NEXUS — Internal APIs and Integration Specification
## Version 0.3

## 1. Purpose
This document specifies the internal API surface and integration contracts between core runtime, materialization, human surfaces, and agent surfaces.

## 2. Scope
Included:
- read APIs;
- proposal APIs;
- decision APIs;
- materialization APIs;
- reentry APIs;
- integration boundaries.

## 3. Out of Scope
Excluded:
- authentication implementation specifics;
- transport-layer production hardening;
- UI framework bindings.

## 4. Read API
```yaml
GET /domains
GET /domains/{id}
GET /entities/{id}
GET /relations/{id}
GET /events/{id}
GET /decisions/{id}
GET /payloads/{id}
GET /projections/{id}
GET /search?query=&type=&domain=
```

## 5. Proposal API
```yaml
POST /proposals/entity-update
POST /proposals/relation-create
POST /proposals/merge
POST /proposals/decision
POST /proposals/payload-edit
POST /proposals/reentry
```

Proposal contracts must preserve at minimum:
- proposal type;
- target references;
- proposer identity;
- rationale;
- evidence references where relevant.

## 6. Decision API
```yaml
POST /decisions/{id}/approve
POST /decisions/{id}/reject
POST /decisions/{id}/override
```

## 7. Materialization API
```yaml
POST /materialize/domain/{id}
POST /materialize/entity/{id}
POST /materialize/payload/{id}
POST /materialize/projection/{id}
GET /exports/{projection_id}
```

## 8. Reentry API
```yaml
POST /reentry/from-payload/{id}
POST /reentry/from-projection/{id}
POST /reentry/parse-diff
```

## 9. Integration Rules
1. APIs must never invert executable precedence.
2. APIs must preserve stable object identities.
3. APIs must preserve proposal vs mutation distinction.
4. APIs must support both human and agent consumption with equivalent semantic meaning.
5. Materialization-facing APIs must preserve artifact-to-object traceability.

## 10. Consumers
Primary consumers:
- human cockpit;
- local agents;
- MCP surface;
- materialization runtime;
- audit tooling.

## 11. Dependencies
- `CORE_RUNTIME_SPEC.md`
- `MATERIALIZATION_AND_TREEFOLDER_SPEC.md`
- `AGENT_SURFACE_AND_MCP_SPEC.md`
