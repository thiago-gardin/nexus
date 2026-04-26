# Day 0 Operational Control Plane Slice — 2026-04-21

## Escopo

Implementacao do proximo slice do plano Day 0, mantendo Nexus em modo maintenance_agent e sem alterar `system/00_specs/`, `AGENTS.md`, `WORKSPACE_CONTRACT.md` ou `CURRENT_STATE.md`.

Este slice transforma a base API/core de authoring em uma operacao local minima:

- authoring API endurecida;
- registro de fonte com payload e source no mesmo limite transacional de banco;
- validacao/rejeicao movida para servico dedicado;
- materializacao de charters, fontes, runs e resumo de authoring;
- cockpit action panel minimo;
- perfil MCP local mutante explicitamente separado do perfil padrao;
- templates Day 0 para Work e Mail;
- testes de integracao e regressao completa.

## Mudancas implementadas

- `DomainVersionService` agora valida entidades/relacoes contra charter ativo e grava `last_event_id` apontando para o evento final de ativacao.
- `SourceService.register_source_with_payload()` cria payload bruto, versionamento do payload, source e evento de source em uma unica transacao de banco; se a transacao falhar, remove o arquivo de payload criado.
- `ObjectValidationService` centraliza `validate_object` e `reject_object` para entidades e relacoes; rejeicao exige motivo.
- Router `authoring` passou a delegar validacao e registro de source para servicos, com erros 400/404/409 mais previsiveis.
- `TreefolderPublisher` publica `DOMAIN_CHARTER.yaml`, `sources/INDEX.md`, `ingestion_runs/INDEX.md` e `AUTHORING_SUMMARY.md`.
- Cockpit ganhou `/surface/actions` com formularios locais para dominio, versao, source, ingestion, entidade, relacao, validacao e rejeicao.
- MCP manteve o perfil padrao com 9 ferramentas normativas e adicionou perfil explicito `local_operator` com ferramentas mutantes locais.
- Adicionados templates `work_portfolio_governance` e `mail_archive_day0`.

## Validacao

Comandos executados:

```powershell
python -m py_compile system/runtime/core/storage/services.py system/runtime/core/storage/__init__.py system/runtime/api/dependencies.py system/runtime/api/routers/authoring.py system/runtime/core/materialization/treefolder_publisher.py system/runtime/api/routers/surface.py system/runtime/mcp/server.py system/runtime/mcp/__init__.py system/runtime/core/domain_templates.py system/tests/integration/test_product_day0_operations.py
python -m unittest system.tests.integration.test_product_authoring_api system.tests.integration.test_product_day0_operations -v
python -m unittest discover -s system/tests -t . -p "test_*.py" -v
```

Resultado final: `45 tests OK`.

## Limites restantes

- Nao houve parsing bruto de PST.
- Nao houve ingestao real da pasta `Work` nem da superficie `.derived`; foram implementadas capacidades/templates e superficies operacionais para executar essas entradas em seguida.
- Conflitos, canonicalizacao rica, replay avancado e core-vs-materialization compare seguem pendentes.
- O cockpit action panel e funcional e local, mas ainda e uma superficie minima Jinja/HTML.
- O commit foi preparado com pathspec explicito para evitar absorver drift amplo e pre-existente, inclusive arquivos staged/untracked/deleted fora deste slice.

## Estado

Implementado, validado e fechado como baseline operacional Day 0 minimo. O fechamento cobre apenas os paths do slice; drift nao relacionado permanece fora do commit.
