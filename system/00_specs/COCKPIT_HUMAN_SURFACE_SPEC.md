# NEXUS — Cockpit Human Surface Specification
## Version 0.3

## 1. Purpose
This document specifies the human cockpit as the primary operational human surface of the Nexus.

## 2. Scope
Included:
- cockpit design principles;
- minimum human capabilities;
- isomorphism, transparency, and auditability requirements;
- minimum component composition;
- graph requirements;
- modularity requirements.

## 3. Out of Scope
Excluded:
- detailed implementation framework choice;
- VS Code or Antigravity integration specifics beyond directionality;
- MCP command semantics.

## 4. Mandatory Principles
### P1 — Operational Isomorphism
Every object class relevant to agent operation must have corresponding human exposure and action surface.

### P2 — Constitutive Transparency
No critical operation may depend exclusively on opaque backend behavior.

### P3 — Native Auditability
The cockpit must expose the system as an auditable process, not only as present state.

### P4 — Institutional Legibility
The cockpit must privilege structural clarity, traceability, and judgment capacity over purely aesthetic simplification.

### P5 — Relational Centrality
The graph is the central navigable structure of cockpit UX.

### P6 — Editable Modularity
The cockpit must be composed of explicit, decoupled, editable components.

## 5. Minimum Capabilities
### 5.1 Observation
The cockpit must allow:
- inspection of entities, relations, events, decisions, payloads, projections, and rules;
- reading of current system state;
- navigation by domain, context, type, status, and relational linkage.

### 5.2 Interrogation
The cockpit must allow:
- evidence and provenance reading;
- comparison between states and versions;
- inspection of diffs between core and materialization;
- reading temporal and causal trails;
- reading justifications, applied rules, and validation criteria.

### 5.3 Action
The cockpit must allow:
- creation and submission of structured proposals;
- approval, rejection, and override where authorized;
- governed editing under reentry regime;
- triggering of permitted review and reconciliation flows.

### 5.4 Review and Governance
The cockpit must allow:
- decision queue consultation;
- reentry queue consultation;
- conflict and ambiguity inspection;
- reconstruction of critical changes and their grounds.

### 5.5 Relational Navigation
The cockpit must allow:
- graph-based exploration of objects and contexts;
- filtering by entity type, relation type, status, time, domain, and scope;
- local focus and progressive expansion;
- opening linked projections and payloads from the graph field.

## 6. Isomorphism Requirements
The human surface must guarantee:
- observational parity;
- interpretive parity;
- revisional parity;
- navigational parity.

## 7. Transparency Requirements
The cockpit must make visible at minimum:
- object identity;
- object type;
- validation status;
- provenance;
- primary relations;
- associated payloads;
- affecting decisions;
- related events;
- applied rule, if any;
- actor;
- execution surface;
- timestamp;
- difference between successive states.

## 8. Auditability Requirements
The cockpit must allow:
- opening full object history;
- comparing versions;
- tracing decision chains;
- tracing provenance chains;
- visualizing related event sequences;
- comparing executable vs materialized state;
- identifying reversibility and overrides.

## 9. Minimum Components
1. **Domain Explorer** — institutional navigation by domain, subdomain, context, and object type.
2. **Object Inspector** — detailed inspection of entities, relations, events, decisions, rules, payloads, and projections.
3. **Payload Viewer** — reading of extended referenced content with explicit structural linkage.
4. **Event Timeline** — sequence of changes, actions, validations, reentries, and decisions.
5. **Decision Queue** — pending proposals, approvals, rejections, overrides, and conflicts.
6. **Relational Visualization** — central graph field for navigation, context, density, and filtering.
7. **Projection Panel** — reading and comparison of publishable projections.
8. **Provenance Panel** — evidence, origin, documentary basis, and transformation links.
9. **Reentry and Diff Panel** — differences between materialization and core, and reentry flows.

## 10. Relational Visualization Requirements
The relational visualization must:
- be the central UX field of the cockpit;
- support local focus and progressive contextual expansion;
- support semantic and visual customization;
- outperform generic note-graph navigation in multidimensional readability;
- remain operational, not decorative;
- maintain explicit linkage with inspector, payloads, events, decisions, and projections.

## 11. Modularity Requirements
Cockpit components must be:
- explicit;
- decoupled;
- replaceable;
- editable across multiple scripts/modules;
- reconfigurable by authorized local agents.

## 12. Initial Exposure Form
The cockpit should initially be exposed as its own operational app, with later possible materialization as:
- VS Code extension; or
- compatible environment fork.

## 13. Minimum Readiness Criteria
The human surface is minimally adequate only if a human operator can:
1. locate a domain and its main objects;
2. navigate by graph and institutional structure;
3. open an object and inspect relations, payloads, provenance, and history;
4. understand what an agent did and why;
5. compare states and versions;
6. assess a proposal or conflict;
7. approve, reject, or override where authorized;
8. reconstruct a critical change without tacit external knowledge.

## 14. Dependencies
- `CORE_RUNTIME_SPEC.md`
- `MATERIALIZATION_AND_TREEFOLDER_SPEC.md`
- `AGENT_SURFACE_AND_MCP_SPEC.md`
