# UI/UX Operator-First Replan
## Data: 2026-04-23
## Tipo: registro operacional de replanejamento
## Status: aberto para execucao futura

## Contexto

A avaliacao humana do `Operate Workspace v1` confirmou que o slice atual nao serve como superficie primaria de operacao humana.

O problema nao e apenas visual.
O problema e de modelo de interacao:

- a interface ainda expõe demais o contrato tecnico da API;
- o authoring continua dependente de IDs, ordem procedural e campos JSON;
- `Operate` e `Map` ainda parecem produtos diferentes;
- o fluxo humano continua distante do modelo operacional observado no Nexus V2.

## Decisao registrada

O proximo ciclo de UI/UX nao deve continuar refinando `ActionCard` empilhado como modelo principal.

O cockpit humano deve convergir para:

- workbench relacional unificado;
- mapa como contexto principal;
- painel lateral de acoes sob demanda;
- inspector persistente;
- formularios dirigidos por schema de dominio;
- selecao por label/picker, nao por ID;
- geracao automatica de identificadores tecnicos.

## Artefato de referencia

O replanejamento consolidado foi registrado em:

- `agent/plan/NEXUS_UI_UX_OPERATOR_FIRST_REPLAN_2026-04-23.md`

## Implicacao pratica

Antes de nova rodada grande de implementacao, o slice `Operate Workspace v1` deve ser tratado como base tecnica transitória, nao como direcao definitiva de UX humana.
