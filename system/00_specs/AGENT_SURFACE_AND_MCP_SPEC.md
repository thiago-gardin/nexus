# NEXUS — Agent Surface and MCP Specification
## Version 0.3

## 1. Purpose
This document specifies the agent-facing surface of the Nexus, including local-agent authority boundaries and MCP-based remote interaction.

## 2. Scope
Included:
- local vs remote agent distinctions;
- MCP minimum function set;
- remote read/proposal policy;
- authority boundaries.

## 3. Out of Scope
Excluded:
- cockpit UI behavior;
- full API definition details;
- runtime bridge implementation specifics for third-party IDEs.

## 4. Agent Regimes
### 4.1 Local Agents
Local agents, when authorized and runtime-coupled, may:
- read structured executable state;
- propose and execute mutations within allowed classes;
- emit full events;
- escalate critical actions to human validation.

### 4.2 Remote Agents
Remote agents must:
- read materialized projections and publishable artifacts;
- write structured proposals only;
- avoid dependence on direct runtime access;
- avoid treating private relational logic as primary truth.

## 5. MCP Position
The MCP surface is the formal agent-facing interface for:
- reading structured objects;
- reading projections;
- submitting proposals;
- reading decision queues;
- explaining objects within permitted scope.

## 6. Minimum MCP Tool Set
```yaml
mcp_tools:
  - get_domain
  - get_entity
  - get_relation
  - get_payload
  - search_objects
  - get_projection
  - create_proposal
  - get_decision_queue
  - explain_object
```

## 7. MCP Restrictions
- remote MCP defaults to reading projections and published payloads;
- executable core reading is limited to authorized local agents;
- critical mutations are not exposed without explicit gate.

## 8. Proposal Model
Remote agents may create proposals for:
- entity updates;
- relation creation;
- merge suggestions;
- decision suggestions;
- payload edit suggestions;
- reentry suggestions.

Remote proposals must always preserve:
- proposer identity;
- target object references;
- rationale;
- evidence references where applicable.

## 9. Authority Matrix
| Capability | Human | Local Agent | Remote Agent |
|---|---|---|---|
| Read projections | yes | yes | yes |
| Read published payloads | yes | yes | yes |
| Read executable core | yes | yes | no |
| Create proposal | yes | yes | yes |
| Authorized mutation | yes | yes, if allowed | no |
| Critical mutation | yes | gated only | no |
| Approve decision | yes | no by default | no |
| Override | yes | no by default | no |

## 10. Readability Requirement
The same institutional object space exposed to agents must remain intelligible to qualified human operators through corresponding human surfaces.

## 11. Dependencies
- `MATERIALIZATION_AND_TREEFOLDER_SPEC.md`
- `INTERNAL_APIS_AND_INTEGRATION_SPEC.md`
- `COCKPIT_HUMAN_SURFACE_SPEC.md`
