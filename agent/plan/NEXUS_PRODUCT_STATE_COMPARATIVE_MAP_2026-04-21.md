# Nexus Product State Comparative Map

Date: 2026-04-21

Scope: compare the current local Nexus repository in `C:\Dev\nexus`, the authoritative specs in `system/00_specs/`, the GitHub V1 repository `https://github.com/ngthiagpgp/Nexus`, and the IA-Studio Bootstrap repository `https://github.com/thiago-gardin/Nexus-V2---Google-IA-Studio-Bootstrap`.

Remote snapshots inspected:

- V1 / public Nexus: `d391082f93577c248f60197cf352bc03115613d0`
- IA-Studio Bootstrap: `d6de8f3fafc93dbba35f21540acda898d1431e65`

## Executive finding

The current Nexus is a strong local-first governed runtime, but it is not yet the full operational product implied by the specs and by the IA-Studio Bootstrap prototype.

The key gap is not that the core cannot create domains, entities, relations, and sources. The service layer already has internal primitives for much of that. The gap is that the shipped operational surfaces do not expose a complete authoring and ingestion workflow:

- The current MCP surface is intentionally limited to nine normative read/proposal tools.
- The current cockpit is mainly an inspection, review, graph, and limited reentry surface.
- The ingestion pipeline exists as an API operation, but not as a cockpit or MCP operational flow.
- Domain creation/versioning, manual entity creation, manual relation creation, source registration, validation/rejection, conflict cases, and canonical promotion are not exposed as first-class product workflows.

The IA-Studio Bootstrap prototype contains many of the missing product operations: domain forms, domain version forms, entity and relation authoring, source registration, validation/rejection, conflict and canonical promotion flows, and a mutation-capable MCP subset. It is weaker than the current repo in governance discipline, materialization, tests, and local-first institutional traceability.

The V1 public repo preserves the earlier ledger/event-sourcing direction and simple MCP operations, but it is closer to a technical memory substrate than to a complete cockpit-driven product.

## Comparative map

| Capability | Expected by specs | Current local Nexus | V1 GitHub Nexus | IA-Studio Bootstrap | Product assessment |
|---|---|---|---|---|---|
| Product frame | Local-first cognitive-operational infrastructure with cockpit, agent/MCP surface, governed object model, materialization, and ingestion | Declared local-first operational ready under scoped PRD assumptions; maintenance phase | Same local-first maintenance framing in the public baseline, plus earlier ledger scripts | Product-style React/Express app with richer operational surface | Current repo is rigorous, but the readiness label was scoped too narrowly for product expectations |
| Domain creation | Domain contracts and multiple domains are required | Internal service support exists; no cockpit/MCP first-class creation workflow | Similar core framing; not a mature product workflow | `POST /api/domains` plus `DomainForm` | IA provides the missing product workflow; current repo provides stronger governance substrate |
| Domain versioning / charters | Domain contract/versioning expected for evolving rules | Domain metadata exists, but no full `domain_versions` product layer | Earlier specs discuss policies/assertions, not rich domain charters | `domain_versions`, activate flow, dynamic entity/relation schema | IA has the right product concept; current repo needs a governed implementation |
| Source registration | Sources are part of ingestion and provenance | Service layer supports sources; no cockpit source registration workflow | Minimal event-source orientation | `SourceForm` and source API | Current repo needs source registration as a visible operation |
| Ingestion execution | Ingest multiple source types and generate candidates with evidence | `POST /ingest` supports local `md/txt/json`, requires existing domain; cockpit/MCP flow absent | Not product-complete; earlier scripts focus on ledger events | Ingestion run tables/API, but parser depth is limited | Current parser is stronger; IA run UX is useful |
| Manual entity creation | Cockpit and MCP should support operational knowledge authoring, at least under governance | `create_entity` exists internally; cockpit cannot create entity; MCP cannot create entity | Simple assertion append via MCP, not domain-aware entity authoring | `EntityForm`, entity API, MCP `create_local_entity` | Current product is blocked by surface exposure, not core impossibility |
| Manual relation creation | Relation assertions expected with evidence/provenance | Governance proposal type supports `relation_create`; cockpit lacks manual relation form; MCP only `create_proposal` | MCP appends generic assertions | `RelationForm`, relation API, MCP `create_relation_assertion` | Relation creation is partially present but too indirect for product use |
| Validation/rejection | Human cockpit validates or rejects objects | Approve/reject proposals exists; object-level validate/reject not broadly exposed | Conflict/resolve concepts exist but primitive | `validate_object` and `reject_object` API/MCP | Current proposal governance is strong, but object validation needs product-level commands |
| Conflict cases | Conflict materialization and resolution are core concepts | Merge/separation proposals and decision queue exist; no rich conflict case object surface | Early `nexus_conflicts` table and conflict resolution MCP | `conflict_cases`, open/resolve UI/API | IA model should be adapted, not copied wholesale |
| Canonical promotion | Semantic canonicalization and promotion expected | Canonical promotion is proposal-oriented and minimum; full engine not claimed | Not mature | `canonical_entities` and promote flow | Current repo needs a practical canonical promotion workflow |
| Evidence/provenance | Every object/change must be traceable | Strong event log, object versions, provenance fields, materialized traces | Strong event log thesis | Thin-core metadata exists but less operationally proven | Preserve current approach |
| Materialization to `tree/` | Required as legible/versionable surface | Strong and implemented | Present in public baseline | Absent | Current repo is the source of truth for this capability |
| Reentry from materialized tree | Controlled reentry expected | Implemented for structured diffs and proposal inbox; limited fields | Present in current-line baseline | Absent | Preserve but expand after authoring workflows |
| Cockpit | Inspect, review, approve/reject/override, author/operate workflows | Local Jinja cockpit for review, graph, inspector, events, reentry; not a full authoring cockpit | Same general product line | React cockpit with action panel and forms | Current cockpit needs IA-style action symmetry |
| MCP | Agent surface with read/proposal contract | Nine normative tools: read, search, projection, proposal, decision queue, explain | Earlier MCP has object state, causal chain, append assertion, resolve conflict | MCP supports list/create entity/relation and validate/reject | Current MCP is safer but too narrow for local operational use |
| External connectors | Email/calendar/chat deferred unless decided; IA spec mentions Outlook PST | Explicitly out of scope | Not complete | Spec includes Outlook PST domain, but implementation is not complete parser | Treat connectors as product modules after core authoring |
| Testing | Acceptance and regression should protect core | 40 tests reported in status; local runtime tests exist | Public baseline reports same closure line | No equivalent test suite observed | Current repo has the quality base to extend |

## Decisions binding the product too tightly

These decisions protected coherence and auditability, but now constrain product completion:

1. Maintenance-agent lifecycle became a product freeze.

   The repo declares the build complete and active work as maintenance/hardening. That is valid for the approved local-first acceptance scope, but it discourages the product-level additions now clearly needed: cockpit authoring, domain versioning, source registration, canonical promotion, and MCP parity.

2. PRD acceptance was narrowed by assumptions.

   The current status says "local-first operational ready" under approved assumptions, while explicitly excluding hosted readiness, connector completion, full semantic canonicalization, and broad UI polish. This made acceptance true, but only for a minimal operational slice.

3. MCP was treated as a formal adapter, not an operational surface.

   The nine-tool MCP surface is coherent with a read/proposal-only remote-agent regime. It is insufficient for local controlled operation where the human or local agent needs to create domains, sources, entities, relations, validation decisions, conflicts, and canonical promotions.

4. Cockpit readiness focused on review and inspection.

   The current cockpit can review, approve/reject, inspect objects, view graph/events, and manage limited reentry. It does not expose the expected product operations needed for ingestion and knowledge construction.

5. External connectors were deferred before a complete ingestion control plane existed.

   Deferring email/calendar/chat connectors is reasonable. However, the same decision also left the product without a cockpit/MCP ingestion console and source lifecycle. The connector decision should not block local source registration and ingestion operations.

6. Governance is proposal-first everywhere except where the core bypasses it.

   Remote agents should remain constrained, but local product operations need explicit policy modes: direct human mutation, local-agent governed mutation, and remote proposal-only mutation. A single read/proposal-only MCP policy is too coarse.

7. Architecture hardening items are being treated as the main backlog.

   Items like `GovernanceService` extraction and `_apply_approved_proposal` path convergence matter, but they do not by themselves produce the missing product capabilities. They should become enabling technical work inside a broader product-completion plan.

## What each lineage should contribute

Current local Nexus should remain the authoritative implementation base for:

- SQLite-backed local-first runtime.
- Evented transaction discipline.
- Governance proposals, decisions, override, actor-filtered events, and version comparison.
- Materialization to `tree/`.
- FastAPI/Jinja local cockpit unless a later decision explicitly changes frontend stack.
- Test discipline and acceptance regression.

IA-Studio Bootstrap should be mined for product shape, not adopted as architecture wholesale:

- Action panel pattern for operational symmetry.
- Domain creation and domain version/charter editing.
- Dynamic entity forms based on active domain schema.
- Relation authoring with source/target search and allowed relation types.
- Source registration UX.
- Validate/reject, conflict case, canonical promotion workflows.
- Expanded MCP command inventory for local controlled mutation.

V1 should be mined for original intent and cautionary lessons:

- Event log as constitutional source.
- Conflict materialization as first-class concept.
- Causal chain/audit ergonomics.
- The risk of staying at substrate level without a full product surface.

## Product reset

The current Nexus should not be framed as "feature-complete maintenance" for the next cycle. A better operational label for the next work phase is:

**Product completion and operational authoring sprint.**

This does not require abandoning the current core. It requires expanding the product surface and MCP/API command model around the existing governed runtime.
