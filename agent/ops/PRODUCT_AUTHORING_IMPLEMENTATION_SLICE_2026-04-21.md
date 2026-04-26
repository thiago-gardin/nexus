# Product Authoring Implementation Slice — 2026-04-21

## Escopo

Implementacao parcial dos planos `NEXUS_GENERAL_IMPLEMENTATION_PLAN_2026-04-21.md` e `NEXUS_TECHNICAL_IMPLEMENTATION_PLAN_2026-04-21.md`, focada no menor slice executavel para operacao Day 0:

- versionamento de dominio;
- registro de fontes;
- disparo e consulta de jobs de ingestao;
- autoria operacional de entidades e relacoes;
- validacao/rejeicao manual basica;
- cobertura de integracao para o fluxo API/core.

Nao foram alterados os specs em `system/00_specs/`.

## Mudancas realizadas

- Criada tabela `domain_versions` com indice de versao ativa unica por dominio.
- Criado repositório `DomainVersionRepository`.
- Criado `DomainVersionService` para criar, listar, consultar e ativar versoes de dominio com eventos auditaveis.
- Exposto `domain_version_service` no runtime da API.
- Criado router operacional `system/runtime/api/routers/authoring.py` com endpoints para dominios, versoes, fontes, ingestao, entidades, relacoes e validacao/rejeicao.
- Acrescentado `JobService.get_job_by_id`.
- Atualizado teste de migracao para cobrir `domain_versions`.
- Criado teste de integracao `test_product_authoring_api.py` cobrindo o fluxo minimo de authoring.

## Validacao

Comandos executados:

```powershell
python -m py_compile system/runtime/core/storage/migrations/bootstrap.py system/runtime/core/storage/repositories/_mappers.py system/runtime/core/storage/repositories/domain_version_repository.py system/runtime/core/storage/services.py system/runtime/api/dependencies.py system/runtime/api/routers/authoring.py system/runtime/api/main.py system/tests/integration/test_product_authoring_api.py system/tests/integration/test_storage_migrations.py
python -m unittest system.tests.integration.test_storage_migrations system.tests.integration.test_product_authoring_api -v
python -m unittest discover -s system/tests -t . -p "test_*.py" -v
```

Resultado da suite completa: `42 tests OK`.

## Limites restantes

- A superficie MCP ainda nao expoe diretamente os novos comandos operacionais de authoring.
- O cockpit ainda nao possui UI dedicada para criar versoes de dominio, fontes, entidades e relacoes por esse fluxo.
- O pipeline ainda usa job inicial simples; parsing especializado de PST/workspaces e reconciliacao rica continuam pendentes.
- O registro de fonte cria payload bruto antes da fonte; em falha intermediaria, pode existir payload orfao, exigindo hardening posterior.
- Materializacao especifica de `domain_versions` ainda nao foi ampliada.

## Estado

Slice implementado e validado como base API/core. Ainda nao equivale a implementacao completa dos planos gerais e tecnicos.
