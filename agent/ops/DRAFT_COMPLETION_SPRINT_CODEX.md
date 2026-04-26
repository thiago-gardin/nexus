# NEXUS — Completion Sprint
## Draft para Codex | Preparado em 2026-04-13

---

Leia AGENTS.md, WORKSPACE_CONTRACT.md, agent/CURRENT_MISSION.md, agent/plan/ACTIVE_TRACK.md, agent/BUILD_PROTOCOL.md e agent/AUTHORITY_MATRIX.md antes de agir.

Você é o build agent local do Nexus. Fique estritamente dentro da autoridade de implementação. Não redesenhe specs. Não modifique arquivos human-owned.

---

## Estado conhecido

O Nexus tem PRD acceptance closure completo (Phase 20). O sistema está operacional.
Esta sprint fecha gaps específicos identificados em revisão pós-closure — não abre novos subsistemas.

Gaps confirmados antes de iniciar:

1. `GovernanceService.override()` provavelmente ausente — `POST /decisions/{id}/override` existe em `governance.py` mas o método pode não estar implementado em `services.py`. Verificar antes de implementar.
2. `GovernanceRuleService` existe no `RuntimeContext` (ver `dependencies.py`) mas não tem nenhuma rota de API exposta em nenhum router.
3. `EventRepository.list()` filtra por `target_object_type`, `target_object_id`, `event_type` — mas não por `performed_by` (ator). `CORE_RUNTIME_SPEC §11` exige `list_events_by_actor`.
4. `compare_versions` não está exposta como função de auditoria. `CORE_RUNTIME_SPEC §11` exige comparação entre versões de um objeto.
5. `agent_surface.py` não menciona `GovernanceRule` na leitura agentiva nem no manifesto.

---

## Missão da sprint

Fechar os gaps de spec remanescentes no menor conjunto de mudanças coerentes possível, sem refatorar o que está funcionando.

### Done da sprint

A sprint só estará concluída se:

1. `GovernanceService.override()` estiver implementado e testado;
2. `GovernanceRule` estiver acessível via API (leitura mínima + criação + update de status);
3. `list_events_by_actor` estiver exposto como filtro real no `EventRepository` e na rota `/events`;
4. `compare_versions` estiver exposto como endpoint de auditoria mínimo;
5. o manifesto agentivo em `/agent` refletir as novas capacidades;
6. todos os testes existentes continuarem passando;
7. `ACTIVE_TRACK.md` e `SYSTEM_STATUS.yaml` estiverem sincronizados.

---

## Bloco A — Verificação inicial (antes de qualquer código)

Execute as verificações a seguir e registre o resultado antes de escrever código:

```bash
# 1. Confirmar se override() existe em services.py
grep -n "def override" system/runtime/core/storage/services.py

# 2. Confirmar rotas de governance_rules
grep -rn "governance_rule" system/runtime/api/routers/

# 3. Confirmar filtro por performed_by no EventRepository
grep -n "performed_by" system/runtime/core/storage/repositories/event_repository.py

# 4. Confirmar se compare_versions existe
grep -rn "compare_versions" system/runtime/
```

Se algum item já estiver implementado, pule o task correspondente e registre no log.

---

## Bloco B — Tasks

### Task 1 — GovernanceService.override()

**Contexto:** `POST /decisions/{id}/override` em `governance.py` chama `runtime.governance_service.override()`. Se o método não existir, o endpoint quebra silenciosamente.

**O que fazer:**
- Se `override()` não existir: implementar em `GovernanceService` dentro de `services.py`
- Semântica: decision pendente → estado `overridden`; registra evento `decision.overridden`; não aplica mutação direta no objeto alvo (override é decisão de governança, não execução)
- Se `override()` já existir: adicionar teste cobrindo o path e marcar task como verificação

**Done quando:** `POST /decisions/{id}/override` retorna resultado coerente e o teste passa.

---

### Task 2 — GovernanceRule API mínima

**Contexto:** `GovernanceRuleRepository` e `GovernanceRuleService` existem. Nenhuma rota os expõe. `CORE_RUNTIME_SPEC §4.6` exige `rule_registry` como componente de core operável.

**O que fazer:**
- Adicionar rotas em `governance.py` (ou novo arquivo `rules.py` se o router estiver grande):
  - `GET /rules` — listar governance rules (com filtro opcional por `scope` e `status`)
  - `GET /rules/{rule_id}` — obter rule por id
  - `POST /rules` — criar nova rule (campos: `rule_type`, `name`, `scope`, `logic_description`, `human_readable_repr`, `applies_to`, `priority`, `created_by`)
  - `POST /rules/{rule_id}/activate` — status → `active`
  - `POST /rules/{rule_id}/deactivate` — status → `inactive`
- Reutilizar `GovernanceRuleService` já disponível no `RuntimeContext`
- NÃO implementar machine-executable rule evaluation agora — apenas CRUD + status

**Done quando:** é possível criar uma rule via API, listá-la, e mudar seu status. Teste cobre o ciclo.

---

### Task 3 — list_events_by_actor

**Contexto:** `EventRepository.list()` filtra por `target_object_type`, `target_object_id`, `event_type`. Não filtra por `performed_by`. `CORE_RUNTIME_SPEC §11` exige `list_events_by_actor` como função de auditoria mínima.

**O que fazer:**
- Adicionar parâmetro `performed_by: str | None = None` em `EventRepository.list()` e na query SQL correspondente
- Propagar o parâmetro para `EventService.list_events()`
- Expor como query param na rota `GET /events` (ex: `?performed_by=agent`)
- Adicionar o mesmo filtro na rota `GET /agent/events` se aplicável

**Done quando:** `GET /events?performed_by=agent` retorna apenas eventos daquele ator. Teste cobre o filtro.

---

### Task 4 — compare_versions (auditoria mínima)

**Contexto:** `CORE_RUNTIME_SPEC §11` exige `compare_versions`. `ObjectVersionRepository` existe e persiste snapshots versionados. Falta um endpoint que coloca dois snapshots lado a lado.

**O que fazer:**
- Adicionar em `GovernanceService` (ou serviço de auditoria inline):
  ```python
  def compare_object_versions(
      self,
      object_type: str,
      object_id: str,
      version_a: int,
      version_b: int,
  ) -> dict[str, Any]: ...
  ```
  Retorna: `{version_a: {...}, version_b: {...}, diff: {field: {from: x, to: y}}}` para campos que mudaram
- Expor como endpoint:
  - `GET /objects/{object_type}/{object_id}/versions/compare?v_a=1&v_b=2`
- Adicionar também na surface agentiva: `GET /agent/objects/{object_type}/{object_id}/versions/compare`

**Done quando:** dado um objeto com 2+ versões, o endpoint retorna um diff mínimo entre as versões. Teste cobre o path.

---

### Task 5 — Atualizar manifesto agentivo

**Contexto:** `/agent` manifesto em `agent_surface.py` não reflete as novas rotas após Tasks 1–4.

**O que fazer:**
- Atualizar `read_routes` no `AgentSurfaceManifest` para incluir:
  - `/rules`
  - `/rules/{rule_id}`
  - `/objects/{object_type}/{object_id}/versions/compare`
  - `/events?performed_by={actor}`
- Se `GET /agent/rules` fizer sentido (leitura agentiva de rules ativas), adicionar a rota

**Done quando:** manifesto em `GET /agent` reflete as capacidades reais do sistema.

---

### Task 6 — Testes e sincronização

**O que fazer:**
- Rodar suite completa: `python -m unittest discover -s system/tests -t . -p "test_*.py"`
- Adicionar ou revisar testes que cubram especificamente:
  1. `override()` → decision em estado `overridden`
  2. GovernanceRule: create → list → activate → deactivate
  3. `list_events_by_actor` com ator específico
  4. `compare_versions` com dois estados distintos
- Atualizar `agent/plan/ACTIVE_TRACK.md` com status de cada task
- Atualizar `SYSTEM_STATUS.yaml`:
  - `build_phase: completion_sprint_done`
  - `governance_rule_api: implemented`
  - `audit_functions: override, list_events_by_actor, compare_versions`
- Commit: `[completion] close spec gaps — override, governance rules, audit functions`

---

## Fora de escopo desta sprint

- `replay_change_sequence` — auditoria avançada, defer
- `compare_core_vs_materialization` — complexidade alta, defer
- Provenance Panel dedicado no cockpit — defer
- Evaluação de regras de governança (machine-executable rules) — defer
- External connectors — fora de escopo por decisão explícita
- Qualquer novo subsistema ou superfície

---

## Preferência de implementação

- Reutilizar `GovernanceRuleService`, `EventService`, `ObjectVersionRepository` já existentes no `RuntimeContext`
- Sem dependências novas
- Sem refatoração do `services.py` nesta sprint — patches cirúrgicos apenas
- Manter BUILD_PROTOCOL: UUID4 como PK, ISO 8601 UTC, evento em toda mutação relevante

---

## Higiene de git

- Inspecionar `git status` antes de qualquer staging
- Não absorver ruído pré-existente (`.tmp.driveupload/`, `__pycache__/`, `desktop.ini`)
- Commits coerentes por bloco lógico se a sprint for grande demais para um commit único
- Prefixo: `[completion]`

---

## Verificação final

Ao concluir, reportar exatamente:

- o que foi implementado
- o que já existia (verificado mas não alterado)
- o que foi explicitamente deixado fora
- resultado da suite de testes (contagem e status)
- se arquivos sujos/staged não relacionados ficaram intocados
