# DRAFT — WORKSPACE_CONTRACT.md v0.3
# Aguarda revisão e aprovação humana antes de substituir o arquivo original.
# Caminho de destino: C:\Dev\nexus\WORKSPACE_CONTRACT.md

# NEXUS — Workspace Contract
## Version 0.3 | Phase: maintenance_agent (post-PRD acceptance)

---

## 1. What This Repo Is

Single repository containing application, specs, coordination, and materialization surface.
PRD acceptance closure complete. System is in maintenance phase.

---

## 2. Stable (Require Human Authorization to Modify)

| Path | Why stable |
|---|---|
| `system/00_specs/*.md` | Authoritative technical specs — v0.3 |
| `AGENTS.md` | Agent orientation — transmutation or scope change requires human decision |
| `WORKSPACE_CONTRACT.md` | This file |
| `CURRENT_STATE.md` | Human-owned operative narrative |

---

## 3. Mutable by Maintenance Agent

| Path | Mutability rule |
|---|---|
| `system/runtime/` | Targeted patches; no architectural inversions |
| `tree/` | Materialization output — derived from DB, regenerable |
| `SYSTEM_STATUS.yaml` | Update after every meaningful state change |
| `agent/CURRENT_MISSION.md` | Update when mission changes |
| `agent/plan/ACTIVE_TRACK.md` | Update during and after execution |
| `agent/ops/` | Decision records, blockers, proposals |
| `output/` | Ephemeral — not managed by agent |
| `.gitignore` | Maintenance permitted |

---

## 4. Mutation Authority

| Class | Rule |
|---|---|
| Bug fixes and targeted patches in `system/runtime/` | Permitted |
| Refactors within existing spec scope | Permitted — flag in `agent/ops/` before acting |
| Schema changes not covered by `CORE_RUNTIME_SPEC` | ❌ Requires human gate |
| Architectural changes (new object model, inversion of precedence) | ❌ Requires human gate |
| Spec changes | ❌ Propose in `agent/ops/` for human review |
| Lifecycle changes | ❌ Human decision only |

---

## 5. Commit Discipline

- Format: `[maint] <imperative description>` for maintenance; `[hardening] <description>` for refactors
- One logical unit per commit
- `SYSTEM_STATUS.yaml` updated before each commit
- `output/` and `.nexus/` are gitignored — never committed

---

## 6. Escalation

Flag for human review when:
- a patch affects schema or object model beyond spec coverage;
- a refactor changes behavior, not just structure;
- a decision falls under Class D mutation;
- any action would modify stable/human-owned files.

Escalation target: `agent/ops/BLOCKERS.md` (create if absent).
