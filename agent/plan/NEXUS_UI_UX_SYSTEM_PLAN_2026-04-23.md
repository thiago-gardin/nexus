# Nexus - UI/UX System Plan
## Data: 2026-04-23
## Status: planejamento derivado do teste de usabilidade Day 0
## Escopo: sistema de UI/UX para o cockpit humano e paridade operacional com o fluxo agente

## 1. Objetivo

Planejar o proximo sistema de UI/UX do Nexus a partir de tres bases:

- specs oficiais de cockpit e PRD;
- plano de cockpit existente em `agent/plan/COCKPIT_INTERFACE_IMPROVEMENT_PLAN.md`;
- achados do teste mais recente em `agent/ops/USABILITY_EVALUATION_DAY0_2026-04-23.md`.

O objetivo nao e redesenhar arquitetura nem trocar stack. O objetivo e transformar o cockpit de um conjunto de paginas corretas em um sistema operacional de interface que:

1. reduza carga cognitiva;
2. preserve governanca explicita;
3. elimine passos manuais desnecessarios;
4. torne o fluxo humano tao guiado quanto o fluxo agente deveria ser;
5. mantenha isomorfismo com o espaco institucional do Nexus.

## 2. Leitura consolidada dos specs

### 2.1 O que o spec de cockpit exige

`system/00_specs/COCKPIT_HUMAN_SURFACE_SPEC.md` exige:

- isomorfismo operacional;
- transparencia constitutiva;
- auditabilidade nativa;
- legibilidade institucional;
- centralidade relacional;
- modularidade explicita.

Traducao pratica:

- o cockpit nao pode ser apenas leitura de tabelas;
- o operador precisa ver objetos, relacoes, historico, evidencia, decisao e trilha causal;
- toda acao relevante precisa ser compreensivel como processo, nao so como resultado final;
- o grafo continua central para navegacao estrutural, mas nao resolve sozinho o problema de operacao.

### 2.2 O que o PRD exige

`system/00_specs/PRD.md` exige:

- continuidade contextual;
- simetria humano-agente sob governanca;
- separacao entre nucleo, artefatos publicaveis e superficies;
- reducao de friccao entre memoria e acao;
- eficiencia operacional e confiabilidade agentiva.

Traducao pratica:

- o cockpit precisa ajudar o operador a continuar de onde parou;
- a UX nao pode depender de memoria tacita de IDs, ordem procedural ou endpoints invisiveis;
- a superficie humana e a superficie agente precisam compartilhar a mesma gramatica operacional, mesmo com interfaces diferentes.

## 3. O que o teste Day 0 mudou

O plano anterior de cockpit acertou no shell, navegacao principal, MAP e auditoria visual. O teste Day 0 mostrou um problema novo e mais importante:

- o cockpit atual e legivel como superficie de leitura;
- o cockpit ainda nao e fluido como superficie de operacao.

O gargalo nao esta mais em "ter tela".
O gargalo agora esta em "costurar as telas em fluxo".

Achados decisivos do teste:

1. a action panel funciona, mas cada formulario e isolado;
2. o usuario precisa copiar `domain_version_id` e `entity_id` manualmente entre etapas;
3. o cockpit nao preserva contexto de dominio, versao ativa ou ultimo objeto criado;
4. a materializacao existe como API, mas nao aparece como parte natural do fluxo;
5. o agente local consegue operar, mas ainda sem uma gramatica de fluxo explicita.

Conclusao:

O proximo salto de UI/UX do Nexus nao e "deixar mais bonito".
E transformar a UX de paginas isoladas em UX de operacao encadeada.

## 4. Decisao de produto para UI/UX

O Nexus deve adotar um sistema de UI/UX com duas camadas:

### Camada A - Shell institucional

Responsavel por orientacao, navegacao, contexto e continuidade.

### Camada B - Workspace operacional

Responsavel por executar fluxos concretos: criar, revisar, validar, publicar, comparar, reconstruir.

Isso implica uma mudanca de framing:

- hoje: "o cockpit tem varias paginas"
- alvo: "o cockpit e um sistema operacional local de governanca"

## 5. Modelo de modos do cockpit

O sistema deve convergir para seis modos estaveis:

1. `Overview`
   - pulso do sistema;
   - dominios ativos;
   - mudancas recentes;
   - filas pendentes;
   - atalhos operacionais.

2. `Operate`
   - novo modo central para Day 0 e authoring local;
   - substitui a ideia de "painel de formularios";
   - opera por workflow e contexto, nao por pagina estatica.

3. `Map`
   - campo central de navegacao relacional;
   - permanece a principal vista de estrutura e contexto;
   - nao vira lugar de formularios.

4. `Flow`
   - eventos, jobs, materializacao, reentry, timeline causal;
   - mostra o sistema como processo.

5. `Inspect`
   - objetos, payloads, projections, provenance, history;
   - leitura aprofundada e comparacao.

6. `Audit`
   - proposals, decisions, conflitos, overrides, reversibilidade;
   - governanca explicita.

Utilitarios globais:

- busca;
- seletor de dominio;
- contexto atual;
- atalho para materializacao;
- contadores de fila.

## 6. Novo principio-chave de UX

### P-UX1 - Operacao guiada por contexto

Nenhuma acao frequente do Day 0 deve depender de o operador lembrar e transportar estado manualmente entre paginas.

Exemplos:

- se uma version acabou de ser criada, o cockpit deve oferecer "ativar agora";
- se uma entidade acabou de ser criada, o cockpit deve oferecer "validar agora";
- se um dominio acabou de ser alterado, o cockpit deve oferecer "materializar agora";
- se um charter exige campos obrigatorios, a interface deve mostralos antes da submissao.

### P-UX2 - Resultado vira proxima acao

A tela de resultado nao pode ser um fim morto. Ela deve se comportar como recibo operacional com proximos passos claros.

### P-UX3 - Mesmo fluxo, duas superficies

Humano e agente nao precisam da mesma UI, mas precisam da mesma gramatica de operacao:

- contexto atual;
- pre-condicoes;
- acao;
- validacao;
- publicacao;
- trilha.

## 7. Sistema de componentes

O proximo sistema deve padronizar os seguintes componentes.

### 7.1 Componentes de shell

- `ContextBar`
  - dominio atual;
  - version ativa;
  - ultimo evento;
  - fila pendente;
  - estado de publicacao/materializacao.

- `ModeRail`
  - Overview / Operate / Map / Flow / Inspect / Audit.

- `WorkspaceHeader`
  - titulo do modo;
  - resumo de contexto;
  - CTA principal;
  - avisos de governanca.

### 7.2 Componentes operacionais

- `WorkflowStepper`
  - mostra etapas do fluxo atual;
  - ex.: dominio -> version -> ativacao -> entidade -> validacao -> materializacao.

- `ActionCard`
  - formulario com contexto pre-preenchido;
  - regras de validacao visiveis;
  - ajuda local curta.

- `ResultReceipt`
  - resultado da acao;
  - objeto criado/alterado;
  - proximas acoes;
  - links reais, nao caminhos em texto.

- `ActionQueue`
  - proximas acoes sugeridas para o contexto atual.

- `MaterializationControl`
  - publicar agora;
  - publicar apos sucesso;
  - ultimo status de materializacao;
  - trilha para `tree/`.

### 7.3 Componentes de leitura e evidencia

- `ObjectIdentityBlock`
  - label primeiro;
  - tipo, status e dominio em badges;
  - UUID secundario e copiavel.

- `EvidenceRail`
  - provenance;
  - payloads;
  - projections;
  - last event;
  - decisions relacionadas.

- `HistoryStrip`
  - versoes;
  - diff;
  - eventos relacionados.

- `GovernanceBadgeSet`
  - actor;
  - validation status;
  - proposal state;
  - mutability regime.

### 7.4 Componentes de erro

- `ActionErrorCard`
  - erro em linguagem operacional;
  - causa;
  - campo faltante ou regra violada;
  - volta segura;
  - proxima acao recomendada.

Nao basta dizer "falhou". A UI precisa dizer "o que faltou para passar".

## 8. Gramatica de estados e sinais

O sistema precisa de uma linguagem visual estavel para:

- `draft`
- `active`
- `proposed`
- `validated`
- `rejected`
- `pending`
- `approved`
- `stale`
- `fresh`
- `not_materialized`
- `materialized`
- `out_of_sync`

Tambem precisa padronizar autoria:

- `human`
- `agent`
- `system`

E regimes:

- `read`
- `proposal`
- `governed mutation`
- `published artifact`

Sem isso, o cockpit continua correto tecnicamente, mas cognitivamente caro.

## 9. Fluxos UX prioritarios

### 9.1 Fluxo Day 0 de authoring humano

Fluxo alvo:

1. selecionar ou criar dominio;
2. criar version;
3. ativar version sem copiar ID;
4. criar entidade/relacao com validacao guiada pelo charter;
5. validar ou rejeitar no mesmo contexto;
6. materializar o dominio;
7. abrir inspector ou flow.

Regras:

- `domain_id` e `domain_version_id` persistem no contexto de sessao local;
- o sistema mostra o charter ativo antes de criar entidade/relacao;
- a acao seguinte e oferecida explicitamente.

### 9.2 Fluxo de erro humano

Quando faltar `workspace_path`, por exemplo, a UI deve:

- mostrar o erro;
- destacar o campo exigido;
- manter o formulario preenchido;
- mostrar a regra do charter que falhou.

### 9.3 Fluxo de publicacao

Depois de uma acao mutante relevante:

- a UI deve mostrar se o dominio esta materializado ou nao;
- deve existir CTA para materializar imediatamente;
- o operador precisa ver o efeito em `tree/` como parte do fluxo, nao como endpoint escondido.

### 9.4 Fluxo agente equivalente

O agente precisa da mesma sequencia conceitual:

- descobrir contexto;
- ler charter ativo;
- executar acao;
- validar;
- publicar;
- explicar o que mudou.

Isso nao exige UI grafica para o agente, mas exige um contrato de UX operacional equivalente.

## 10. Contrato de UX entre cockpit e MCP

Para preservar simetria funcional, o sistema deve ter um contrato compartilhado:

### Leitura pre-acao

- contexto atual;
- charter ativo;
- campos obrigatorios;
- ultimo estado de materializacao;
- filas relacionadas.

### Resultado pos-acao

- objeto resultante;
- novo status;
- evento gerado;
- publicacao pendente ou concluida;
- proxima acao recomendada.

No cockpit isso vira componente.
No MCP isso vira envelope/tool helper.

## 11. Plano de implementacao de UI/UX

### Fase UX-1 - Contexto operacional compartilhado

Objetivo:

Criar o estado minimo de sessao do cockpit para reduzir copy/paste de IDs.

Escopo:

- contexto ativo de dominio;
- version ativa conhecida;
- ultimo objeto criado;
- ultimo job de materializacao.

Arquivos provaveis:

- `system/runtime/api/routers/surface.py`
- `system/tests/integration/test_operational_surface.py`

Aceite:

- o operador nao precisa copiar `domain_version_id` logo apos criar uma version;
- o operator nao precisa copiar `entity_id` logo apos criar uma entidade para valida-la.

### Fase UX-2 - Operate Workspace v1

Objetivo:

Substituir a action panel como pagina de formularios por um workspace guiado.

Escopo:

- `WorkflowStepper`;
- `ActionCard`;
- `ResultReceipt`;
- `ActionQueue`.

Regra:

- sem trocar stack;

Aceite:

- um fluxo dominio -> version -> ativacao -> entidade -> validacao acontece dentro de um contexto coerente.

### Fase UX-3 - Publicacao e materializacao como parte da UX

Objetivo:

Trazer a materializacao para dentro do fluxo principal.

Escopo:

- CTA de materializacao no cockpit;
- opcao `materialize after success` em operacoes relevantes;
- status de publicacao visivel na `ContextBar`.

Aceite:

- apos mutacao relevante, o operador entende imediatamente se o estado publicavel esta sincronizado.

### Fase UX-4 - Inspector e Audit acoplados ao fluxo

Objetivo:

Fazer o operador saltar naturalmente de operacao para inspecao e auditoria.

Escopo:

- links reais e clicaveis para objeto, history, flow, audit;
- recibos de acao com proximos passos claros;
- EvidenceRail consistente.

Aceite:

- a tela de resultado deixa de ser um beco sem saida.

### Fase UX-5 - Paridade operacional com agente

Objetivo:

Diminuir o custo procedural do `local_operator`.

Escopo:

- leitura curta do charter ativo;
- helper de bootstrap Day 0;
- envelope de resultado com proxima acao.

Aceite:

- o agente nao precisa conhecer de memoria a ordem procedural minima para operar.

### Fase UX-6 - Validacao de usabilidade

Objetivo:

Reexecutar os cenarios humano e agente e comparar contra o teste de 2026-04-23.

Aceite:

- menos copy/paste;
- menos telas mortas;
- materializacao visivel;
- erro mais acionavel;
- menos dependencia de conhecimento tacito.

## 12. Prioridade real

Ordem recomendada:

1. `UX-1 Contexto operacional compartilhado`
2. `UX-2 Operate Workspace v1`
3. `UX-3 Publicacao/materializacao`
4. `UX-4 Inspector + Audit no fluxo`
5. `UX-5 Paridade com agente`
6. `UX-6 Novo teste de usabilidade`

Motivo:

O maior problema de UX hoje nao e navegacao geral. E friccao de fluxo.
Entao a prioridade precisa sair de "mais paginas" para "menos custo por acao".

## 13. O que este plano substitui e o que preserva

### Preserva do plano anterior

- shell institucional;
- mode rail;
- MAP como campo central de navegacao;
- FLOW e AUDIT como superficies de processo;
- stack FastAPI + Jinja + CSS/JS local;
- ausencia de dependencias novas.

### Corrige no plano anterior

- acrescenta `Operate` como modo formal;
- troca foco de shell/visual para fluxo operacional;
- incorpora materializacao como parte da UX;
- inclui paridade de fluxo com agente;
- transforma resultado de acao em componente de proxima acao.

## 14. Veredito de planejamento

O proximo sistema de UI/UX do Nexus nao deve ser concebido como "melhoria do cockpit".

Deve ser concebido como:

> um sistema de operacao local com shell institucional, contexto persistente, workflow guiado, auditoria explicita e paridade funcional entre humano e agente.

Essa e a mudanca minima que responde ao ultimo teste sem trair os specs nem reabrir a arquitetura.
