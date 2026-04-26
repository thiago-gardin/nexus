# DRAFT — CURRENT_STATE.md
# Aguarda revisão e aprovação humana antes de substituir o arquivo original.
# Caminho de destino: C:\Dev\nexus\CURRENT_STATE.md

fase atual: maintenance-ready
objetivo: sistema operacional local com PRD acceptance closure completo; próxima fase é manutenção, hardening e uso real
non-goals: redesenho de arquitetura, troca de stack, substituição de specs
estado do build: phase_20 / prd_acceptance_closure_complete

capacidades operacionais:
  - núcleo executável SQLite com 15 tabelas migradas
  - ingestão local (json, md, txt) com payload bruto e parseado
  - entidades, relações, eventos, decisões com identidade estável e versionamento
  - governança: proposals, decision queue, approve/reject, object_versions, history
  - materialização: treefolder, projections, payload indexes, canonical indexes, proposal inbox
  - superfície humana: cockpit modular com inspeção, review, approve/reject, graph, timeline
  - superfície agentiva: REST /agent + MCP adapter com 9 tools normativos reais
  - reentry: proposal-from-edit (entity.short_description, relation.validation_status), tree inbox import
  - reconciliação: candidate groups, alias matching, merge proposals, separation proposals

lifecycle do agente: build_agent — pronto para transmutação para maintenance_agent
decisão pendente: transmutação formal (requer update em AGENTS.md pelo humano)

build authority: mutações críticas só por proposta; manutenção e hardening permitidos dentro dos specs
próximo passo: atualizar AGENTS.md para declarar transmutação; iniciar backlog de manutenção
