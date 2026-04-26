fase atual: maintenance-ready / local-first operational use
objetivo: operar o Nexus como infraestrutura cognitiva local, manter o núcleo estável, executar hardening direcionado e apoiar ingestão real sem redesenhar a arquitetura
non-goals: hosted SaaS, multi-user general availability, conectores externos email/calendar/chat, novo frontend separado, reescrita de specs, troca de stack
estado do build: phase_20_prd_acceptance_complete + post_closure_completion_sprint_done
product_readiness: ready_for_local_first_operational_use; not_general_availability
agent_lifecycle: maintenance_agent
last_regression: "2026-04-13 — python -m unittest discover -s system/tests -t . -p \"test_*.py\" — 40 tests passed"

capacidades operacionais:
  - núcleo executável SQLite com 15 tabelas migradas
  - ingestão local genérica para json, md e txt
  - persistência de sources, payloads, projections, jobs e governance rules
  - entidades, relações, eventos, decisões e object_versions com identidade estável
  - governança: proposals, decision queue, approve/reject/override, GovernanceRule API, object history, actor-filtered events, compare versions
  - reconciliação: candidate groups, alias matching, scored duplicate groups, merge proposals e separation proposals
  - materialização: treefolder derivado do DB com projections, payload indexes, canonical indexes, proposal inbox e governance traces
  - reentry: proposal-from-edit, parse-diff e tree inbox proposal import com deduplicação tree-proposal:<relative_path>
  - superfície humana: cockpit local FastAPI/Jinja/JS com dashboard, graph, inspector, payload/projection panels, timeline, reentry diff e review surfaces
  - superfície agentiva: REST /agent operacional e MCP adapter formal com 9 tools normativas
  - auditoria mínima: event log, object versions, decision traces, list_events_by_actor e compare_versions

limites conhecidos:
  - conectores externos email/calendar/chat estão fora de escopo até decisão humana
  - reconciliação não é full semantic canonicalization engine
  - MCP é adapter funcional; hardening de transporte/protocolo é futuro
  - cockpit é usável localmente, mas ainda precisa polish de produto
  - replay_change_sequence e compare_core_vs_materialization seguem deferidos
  - GovernanceService ainda deve ser separado de core/storage/services.py em hardening futuro
  - _apply_approved_proposal ainda deve convergir para paths de service-level update em hardening futuro

próximo foco recomendado:
  - usar o Nexus em ingestões reais locais
  - executar hardening de GovernanceService e mutation path convergence
  - continuar UI-2+ do cockpit se a prioridade for produto humano
  - aprofundar MCP transport apenas se houver necessidade operacional

nota de autoridade: este arquivo é human-owned e foi sincronizado nesta rodada sob autorização humana explícita para atualizar documentos de governança.
