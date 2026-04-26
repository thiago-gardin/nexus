# NEXUS — Authority Matrix
## Version 0.4 | Phase: maintenance_agent / current mission

---

## 1. Actor Classes

| Actor | Description |
|---|---|
| **Human** | Thiago — system owner, final decision authority |
| **Local Agent (Build)** | Completed build lifecycle; Phases 1-20 and post-closure completion sprint are closed |
| **Local Agent (Maintenance)** | Codex operating in this repo — targeted patch, hardening, audit, and proposal authority |
| **Remote Agent** | External agent reading/proposing through published tree, REST/local where allowed, or MCP adapter under governance |

---

## 2. Repository Authority

| Action | Human | Local Agent (Build) | Local Agent (Maint.) | Remote Agent |
|---|---|---|---|---|
| Read any file | ✅ | ✅ | ✅ | treefolder only |
| Create application code (`system/runtime/`, `system/tests/`) | ✅ | inactive by default | ✅ patch only | ❌ |
| Modify application code | ✅ | inactive by default | ✅ patch only | ❌ |
| Write `tree/` (materialization) | ✅ | ✅ | ✅ | ❌ |
| Modify `system/00_specs/` | ✅ | ❌ | ❌ | ❌ |
| Modify `AGENTS.md` | ✅ | ❌ | ❌ | ❌ |
| Modify `WORKSPACE_CONTRACT.md` | ✅ | ❌ | ❌ | ❌ |
| Update `SYSTEM_STATUS.yaml` | ✅ | ✅ | ✅ | ❌ |
| Update `agent/plan/ACTIVE_TRACK.md` | ✅ | ✅ | ✅ | ❌ |
| Write `agent/ops/` | ✅ | ✅ | ✅ | ❌ |
| Declare lifecycle transmutation | ✅ | ❌ | ❌ | ❌ |
| Propose spec changes | ✅ | via `agent/ops/` | via `agent/ops/` | ❌ |

---

## 3. Mutation Classes (per CORE_RUNTIME_SPEC §8)

| Class | Description | Agent authority |
|---|---|---|
| **A — Read** | No state change | Unrestricted |
| **B — Proposal** | Changes proposal queues only | Permitted |
| **C — Authorized Mutation** | Changes executable state within pre-approved classes | Permitted if covered by spec |
| **D — Critical Mutation** | Schema inversions, identity redefinition, governance rule changes | Requires human gate |

---

## 4. Executable Core Authority (runtime, governed operations)

| Operation | Human | Local Agent | Remote Agent |
|---|---|---|---|
| Read executable core | ✅ | ✅ | ❌ |
| Create proposal | ✅ | ✅ | ✅ |
| Class C mutation | ✅ | ✅ if spec-covered | ❌ |
| Class D mutation | ✅ | gated only | ❌ |
| Approve decision | ✅ | ❌ by default | ❌ |
| Override | ✅ | ❌ by default | ❌ |

Source: `system/00_specs/CORE_RUNTIME_SPEC.md §9`, `system/00_specs/AGENT_SURFACE_AND_MCP_SPEC.md §9`

Current local product status: ready for local-first operational use and maintenance. General-availability external product readiness is not claimed.

---

## 5. Escalation Triggers

The agent must stop and write to `agent/ops/BLOCKERS.md` when:

- An action is Class D and no human gate exists yet
- A spec is ambiguous or contradictory
- A required dependency is missing
- A schema decision is not covered by CORE_RUNTIME_SPEC
- Any action would modify files in the "never" column above

---

## 6. Lifecycle-Gated Authorities

Some authorities activate only after lifecycle transmutation:

| Authority | Build Agent | Maintenance Agent |
|---|---|---|
| Propose schema patches | ❌ | ✅ via `agent/ops/` |
| Modify existing core logic | ✅ (build only) | ✅ patch only |
| Run governance rules against live data | ❌ | ✅ gated |
| Access MCP surface | build lifecycle complete | ✅ read + proposal |

Transmutation declared by: Human on 2026-04-13, reflected in `AGENTS.md`, `SYSTEM_STATUS.yaml`, and the maintenance governance layer.
