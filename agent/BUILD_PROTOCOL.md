# NEXUS — Build Protocol

## Version 0.5 · Phase: `maintenance_agent` / current mission

### Maintenance Discipline for the Local Executable Core

---

## 1. Purpose

This document defines the implementation discipline for maintaining and hardening the **Nexus local executable core** after PRD acceptance closure.

It governs:

* code organization
* mutation discipline
* event emission
* transaction boundaries
* API segmentation
* materialization boundaries
* testing and commit hygiene

It does **not** redefine:

* product architecture
* technical precedence
* institutional rules
* human/agent governance already established elsewhere

This is a **build protocol**, not the full technical specification.

---

## 2. Normative Technical Principles

### P1 — Executable Precedence

The DB-backed local core is the source of **executable truth**.
Materialized files are **publishable artifacts**, never sovereign runtime truth.

### P2 — Proposal vs Mutation Distinction

The implementation must preserve the distinction between:

* **Read**
* **Proposal**
* **Authorized Mutation**
* **Critical Mutation**

These regimes must remain explicit in code, APIs, tests, and audit traces.

### P3 — Evented State Change

No relevant state mutation may occur without a corresponding event emitted **in the same transaction**.

### P4 — Controlled Reentry

Changes originating from materialized artifacts may reenter the executable core only through:

* governed proposal
* reconciliation
* authorized mutation

Never through silent overwrite.

### P5 — Remote Readability Without Remote Sovereignty

Remote agents may:

* read projections
* read published payloads
* submit structured proposals

Remote agents may **not** directly mutate the executable core.

---

## 3. Language and Runtime

* **Language:** Python 3.11+
* **Web framework:** FastAPI
* **Primary database:** SQLite (bootstrap)
* **Analytical companion:** DuckDB when needed
* **Scale-up option:** local Postgres if required
* **Query layer:** SQLAlchemy Core or parameterized raw SQL
* **Migrations:** Alembic or manual scripts under runtime migrations
* **Testing:** `unittest` in the current repository test suite
* **Packaging:** `pyproject.toml` preferred

### Hard rules

* no hidden ORM behavior
* no magic schema generation
* no framework-driven architecture shortcuts

---

## 4. Root Layout

The workspace must preserve the tripartite distinction:

```text
agent/
system/
tree/
```

### `agent/`

Local build governance, authority, plans, session logs, and audit artifacts.

### `system/`

Executable code, specs, runtime, APIs, tests, ingestion, and services.

### `tree/`

Materialized, publishable, remote-readable semantic artifacts.

### Rule

These three regimes must **never** collapse into a single undifferentiated code tree.

---

## 5. System Layout

Inside `system/`, the minimum structure is:

```text
system/
  00_specs/
  runtime/
    core/
      storage/
        db.py
        transaction_manager.py
        migrations/
        repositories/
    api/
      routers/
      schemas/
      dependencies.py
      main.py
    config/
      settings.py
  tests/
    unit/
    integration/
```

### Structural rule

* `tree/` is **not** application code
* `agent/` is **not** runtime code
* `system/runtime/` is the only place where executable truth is implemented

---

## 6. Naming Conventions

| Element             | Convention                    | Example                     |
| ------------------- | ----------------------------- | --------------------------- |
| Files               | `snake_case.py`               | `domain_repository.py`      |
| Classes             | `PascalCase`                  | `DomainRepository`          |
| Functions / methods | `snake_case`                  | `get_by_id()`               |
| DB table names      | `snake_case`, plural          | `domains`, `entity_aliases` |
| DB column names     | `snake_case`                  | `domain_id`, `created_at`   |
| IDs                 | UUID4 stored as `TEXT`        | `"a1b2..."`                 |
| Timestamps          | ISO 8601 UTC stored as `TEXT` | `"2026-04-09T12:00:00Z"`    |
| Status enums        | lowercase string              | `"active"`, `"pending"`     |

---

## 7. Core Identity Rules

Every core institutional object must have:

* primary id as UUID4 `TEXT`
* `version INTEGER NOT NULL DEFAULT 1`
* `created_at TEXT NOT NULL`
* `updated_at TEXT NOT NULL`

### Hard rules

* identity must never be derived from mutable fields
* no auto-increment integer PKs for core objects
* no “natural key” may act as canonical identity unless explicitly formalized in spec

---

## 8. Mutation Classes

### Class A — Read

No state change.

### Class B — Proposal

Creates or updates proposal queue objects only.
Does **not** stabilize executable state.

### Class C — Authorized Mutation

Allowed mutation within pre-approved safe classes.

### Class D — Critical Mutation

Requires explicit gate, decision, or approved governance rule.

### Rule

No implementation may blur these classes.
Proposal endpoints must not behave like mutation endpoints.
Materialization endpoints must not mutate executable truth unless explicitly routed through reentry/governance.

---

## 9. Event Emission Rules

Every create or update affecting **Domain, Source, Entity, Relation, Decision, GovernanceRule, Payload, or Projection** must:

1. execute inside a single transaction
2. persist the object mutation
3. persist the corresponding event in the same transaction
4. preserve at minimum:

   * `performed_by`
   * `performed_via`
   * `target_object_type`
   * `target_object_id`
   * `reason` when applicable
   * `before_state_ref` or equivalent serialized snapshot
   * `after_state_ref` or equivalent serialized snapshot
   * reversibility metadata where applicable

### Hard rules

* never commit state without event
* never emit event outside transaction
* never update a core object silently

---

## 10. Repository Discipline

Repositories must:

* accept a DB connection or transaction handle
* not open or close transactions themselves
* not contain HTTP logic
* not decide approval gates
* not materialize files directly

### Responsibility split

* transaction control belongs to `TransactionManager`
* governance decisions belong to services / approval layer
* route handlers orchestrate transport, not business logic

### Minimum repository pattern

```python
class DomainRepository:
    def create(self, data: DomainCreate) -> Domain: ...
    def get_by_id(self, domain_id: str) -> Domain | None: ...
    def list(self, filters: dict | None = None) -> list[Domain]: ...
    def update_status(self, domain_id: str, status: str) -> Domain: ...
```

---

## 11. API Segmentation

The API layer must preserve technical segmentation by regime.

### 11.1 Read API

Examples:

* `/v1/domains`
* `/v1/entities/{id}`
* `/v1/relations/{id}`
* `/v1/events/{id}`
* `/v1/projections/{id}`

### 11.2 Proposal API

Examples:

* `/v1/proposals/entity-update`
* `/v1/proposals/relation-create`
* `/v1/proposals/merge`
* `/v1/proposals/reentry`

### 11.3 Decision API

Examples:

* `/v1/decisions/{id}/approve`
* `/v1/decisions/{id}/reject`
* `/v1/decisions/{id}/override`

### 11.4 Materialization API

Examples:

* `/v1/materialize/domain/{id}`
* `/v1/materialize/projection/{id}`

### 11.5 Reentry API

Examples:

* `/v1/reentry/from-payload/{id}`
* `/v1/reentry/parse-diff`

### Hard rules

* route handlers must not mix regimes casually
* read routes must not mutate state
* proposal routes must not perform critical mutation
* materialization routes must not redefine executable truth

---

## 12. Response and Error Conventions

### Request / response bodies

* use explicit Pydantic models
* no raw dict returns for public routes
* no untyped payloads in stable endpoints

### Error model

Use:

```json
{
  "error": "<code>",
  "detail": "<message>"
}
```

with appropriate HTTP status.

### Hard rules

* no opaque `500` as normal control flow
* no framework-default error leakage in stable endpoints
* validation errors must remain legible

---

## 13. Materialization Rules

`tree/` is an official remote-readable interface, not an incidental export folder.

Therefore:

* no test writes to canonical `tree/` by default
* no application code treats `tree/` artifacts as executable truth
* all materialized artifacts must preserve object-to-artifact traceability
* **payload** and **projection** are distinct object classes
* external edits never silently mutate core
* editable artifacts must declare editability regime

### Hard rules

* no treefolder-first implementation that bypasses DB precedence
* no artifact may redefine canonical identity
* materialization is publication, not sovereignty

---

## 14. Remote Agent Safety

Remote agents may:

* read projections
* read published payloads
* submit structured proposals

Remote agents may **not**:

* mutate executable core directly
* redefine canonical identity
* bypass decision queues
* treat materialized files as sovereign truth

### Rule

Remote operation is **read-mostly / proposal-only** unless a stricter local regime says otherwise.

---

## 15. Testing Requirements

Minimum requirements:

* every repository method gets unit coverage
* every API regime gets at least one integration test
* proposal / decision / materialization / reentry each get at least one path test
* tests run with `python -m unittest discover -s system/tests -t . -p "test_*.py"` from repo root unless a narrower targeted run is explicitly justified
* tests use isolated DBs
* tests do not write to production DB paths
* tests do not publish into canonical `tree/` unless explicitly marked as materialization integration tests

### Hard rules

* no test may depend on local manual state
* no test may use production paths implicitly
* no untracked side effects in `tree/`

---

## 16. Commit and Session Discipline

### Commit rules

* one logical unit per commit
* no mixed concerns in the same commit
* no speculative refactor bundled with implementation

### Session discipline

Before closing a cycle:

* update session log
* update current active track if scope changed
* update system status if build state changed materially

### Suggested commit format

* `[maint] harden governance service boundary`
* `[hardening] converge approved proposal mutation path`
* `[completion] close spec gaps — override, governance rules, audit functions`
* `[phaseN] <description>` only when a human opens a new numbered implementation phase

---

## 17. Boundary Rules

This protocol does **not** authorize the local agent to decide alone:

* product scope expansion
* schema changes that contradict core specs
* remote write privileges beyond proposal mode
* inversion of executable precedence
* surface-driven shortcuts that redefine runtime architecture

When in doubt, stop and escalate through the appropriate governance artifact rather than improvising architecture in code.

---

## 18. What Not to Do

* no auto-increment PKs for core objects
* no silent mutations
* no business logic inside migrations
* no hardcoded paths
* no print-debugging left committed
* no direct remote-agent write path into core
* no treefolder-first implementation that bypasses DB precedence
* no schema changes contradicting `CORE_RUNTIME_SPEC.md`
* no surface-driven shortcuts that redefine runtime architecture
* no mixing of proposal logic with authorized mutation logic

---

## 19. Done Criteria for the Active Mission

A slice is complete only when:

1. the active mission criteria are met
2. the relevant mutable docs have been updated to the same state
3. verification evidence has been recorded
4. any proposal or blocker required by drift has been written
5. the resulting changes are committed

Current mission note: Nexus is in maintenance/hardening mode. New broad build phases, architecture redesign, hosted-product claims, or connector expansion require explicit human decision before implementation.

---

## 20. Final Rule

If implementation convenience conflicts with:

* executable precedence
* auditability
* proposal/mutation distinction
* controlled reentry
* remote read/proposal boundaries

implementation convenience loses.
