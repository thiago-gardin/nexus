# NEXUS — Technical Implementation Roadmap
## Version 0.3

## 1. Purpose
This document sequences the implementation of the Nexus technical base from minimum executable core to operationally usable multi-surface system.

## 2. Scope
Included:
- phase ordering;
- technical milestones;
- minimum done criteria.

## 3. Out of Scope
Excluded:
- sprint-level tasks;
- contributor-specific assignment;
- product experimentation backlog.

## 4. Recommended Phase Order
### Phase 1 — Minimum Executable Core
Deliver:
- local database;
- central tables;
- domain registration;
- basic ingestion;
- entity, relation, and event persistence;
- minimum payload references;
- simple materialization.

### Phase 2 — Minimum Governance
Deliver:
- decision queue;
- approval engine;
- rules registry;
- object versioning;
- minimum reentry rule.

### Phase 3 — Operational Materialization Regime
Deliver:
- payload store;
- stable projections;
- legible diffs;
- proposal-from-edit support;
- stable semantic exports;
- remote-readable treefolder.

### Phase 4 — Human and Agent Surfaces
Deliver:
- minimum human cockpit;
- read/proposal MCP surface;
- payload/projection viewers;
- decision and reentry queues.

### Phase 5 — Advanced Reconciliation and Projections
Deliver:
- improved matching;
- canonicalization refinement;
- meeting/project projection classes;
- improved history and diffs;
- full review loops.

## 5. Readiness Criteria by Milestone
### 5.1 Core Ready
- executable database is authoritative;
- core objects persist with stable identity and version;
- every relevant mutation emits an event.

### 5.2 Materialization Ready
- canonical payloads are referenced and versioned;
- at least one legible projection is published;
- at least one eligible external edit can become structured proposal.

### 5.3 Remote Readability Ready
- remote agent can read treefolder projections;
- remote agent can submit structured proposal without runtime access.

### 5.4 Human Surface Ready
- human can inspect object, provenance, history, and proposal;
- human can approve or reject proposal;
- human can reconstruct a critical change.

## 6. Global Technical Done Criteria
The technical base is considered minimally ready only when:
1. the database operates as executable truth;
2. core objects are versioned;
3. payloads are referenceable and versioned;
4. materialized projections exist;
5. at least one domain runs end-to-end;
6. remote proposal flow works without direct runtime dependency;
7. human review flow works;
8. audit reconstruction of a critical change is possible.

## 7. Dependencies
This roadmap depends on all component specs and should be revised only after changes in:
- executable precedence;
- materialization model;
- surface model;
- authority model.
