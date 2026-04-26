# Avaliacao Day 0

Data: 2026-04-21

Pergunta central:

> O plano atual do Nexus aguenta um teste real de operacao Day 0 com dois dominios pre-estruturados: Work portfolio e e-mail/PST?

Resposta curta: o plano recente aguenta como direcao tecnica e produto, mas a implementacao atual do Nexus ainda nao passa no teste operacional Day 0. O veredito e `NAO PASSA AINDA`.

## Base usada

Documentos Nexus recentes:

- `agent/plan/NEXUS_PRODUCT_STATE_COMPARATIVE_MAP_2026-04-21.md`
- `agent/plan/NEXUS_GENERAL_IMPLEMENTATION_PLAN_2026-04-21.md`
- `agent/plan/NEXUS_TECHNICAL_IMPLEMENTATION_PLAN_2026-04-21.md`

Pastas inspecionadas:

- `C:\Users\gardi\OneDrive\Documentos\Work`
- `C:\Users\gardi\OneDrive\Documentos\Work\50_Memory\e-mail`

## Comparacao de complexidade dos dominios

### Dominio Work

Complexidade: media-alta, mas controlavel no Day 0.

Razoes:

- Estrutura de pastas legivel e fortemente semantica.
- Muitos arquivos Markdown/status/log/governanca.
- Presenca de protocolos locais (`AGENTS.md`, `VAULT_PROTOCOL.md`, `TOOLING.md`).
- Projetos e workspaces aparecem como diretorios relativamente reconheciveis.
- Ha ambiguidade e duplicidade, mas a primeira versao pode ser inventario + validacao humana.

Risco principal: confundir estrutura de filesystem com ontologia final de portfolio.

### Dominio e-mail/PST

Complexidade: alta.

Razoes:

- Fonte primaria binaria e grande: PST com cerca de 2,43 GB.
- Superficie derivada factual existe, mas esta `stale` e `partial`.
- Ha mensagens, threads, anexos, calendario, contatos, tasks, notificacoes de Planner e possiveis decisoes.
- Inferencias importantes dependem de revisao humana.
- Links com projetos exigem entidades canonicas do dominio Work.

Risco principal: transformar correlacoes textuais em decisoes, tasks ou relacoes de projeto sem validacao.

## Qual dominio deve entrar primeiro

O dominio Work deve entrar primeiro.

Motivos:

- Ele define os projetos canonicos que o e-mail precisa referenciar.
- Ele pode iniciar com inventario e governanca minima sem parsing externo complexo.
- Ele produz valor operacional rapido: dashboard de portfolio, fontes de verdade, status, logs, tasks e decisoes.
- Ele reduz ambiguidade do e-mail: `OBP`, `Faltas see`, `Radon`, `FGV Cidades`, `CEMASP`, `Docente` deixam de ser apenas strings e passam a ser entidades candidatas.

O dominio e-mail deve entrar depois como dominio factual autonomo, mas sua integracao com portfolio deve ser proposta estruturada e validada, nao mutacao automatica.

## Teste de suporte por capacidade

| Capacidade | Estado atual | Plano recente | Avaliacao Day 0 |
|---|---|---|---|
| Criacao/versionamento de dominio | Parcial. Ha suporte interno a dominio, mas sem cockpit/MCP operacional e sem `domain_versions` completo | T1 cobre dominio e charter versionado | Bloqueio para operacao produto |
| Source registration | Parcial. Fontes existem no core, mas nao como fluxo cockpit/MCP claro | T2 cobre source registration | Bloqueio para Day 0 real |
| Ingestao inicial | Parcial. `md/txt/json` existe; PST nao; ingestion run nao e objeto operacional completo | T3 e T12 cobrem runs e modulo e-mail | Work pode iniciar limitado; mail nao passa robustamente |
| Autoria de entidades | Parcial. Servico interno existe; superficie operacional ausente | T4 cobre authoring | Bloqueio para cockpit/MCP |
| Autoria de relacoes | Parcial. `relation_create` existe via proposal; cockpit nao tem fluxo completo | T5 cobre authoring | Parcial demais para Day 0 |
| Validacao/rejeicao | Parcial. Propostas podem ser aprovadas/rejeitadas; objetos nao tem fluxo amplo | T6 cobre object validation | Bloqueio para revisar candidatos reais |
| Conflitos/canonicalizacao | Parcial. Merge/separacao por proposta; sem fluxo rico | T7/T8 cobrem conflito e canonical | Necessario antes de escalar mail |
| Materializacao | Forte para estado atual; nao cobre todos os novos objetos planejados | T9 cobre expansao | Suficiente como base, incompleta para Day 0 dos dominios |
| Cockpit | Inspecao/review/grafo/reentry limitado | T11 cobre action panel | Bloqueio central |
| MCP | Nove ferramentas read/proposal | T10 cobre perfis e mutacao local | Bloqueio central |
| Rastreabilidade | Forte no nucleo atual | Preservada no plano | Sustentado |
| Reentry | Controlado, mas estreito | Deve expandir apos authoring | Parcial |
| PST/e-mail | Fora do escopo atual; superficie `.derived` externa existe | T12 coloca modulo e-mail depois do core | Nao passa ainda |

## O que ja esta suficientemente sustentado

- Tese local-first.
- SQLite como fonte executavel.
- Eventos e auditabilidade basica.
- Separacao entre runtime, `tree` e `agent`.
- Propostas/decisoes como regime de governanca.
- Materializacao como superficie legivel.
- Ingestao local simples para `md/txt/json`.
- Uso de `.derived` de e-mail como fonte factual externa ja estruturada.
- Diagnostico correto do plano recente: o produto precisa de authoring, source registration, ingestion runs, cockpit action panel e MCP local.

## O que esta parcialmente sustentado

- Dominio Work como inventario inicial: possivel com scripts e revisao humana, mas sem produto completo.
- Criacao de candidatos de projeto/status/task/decisao: tecnicamente plausivel, operacionalmente sem cockpit adequado.
- E-mail como dominio factual: a superficie `.derived` e madura o bastante para leitura, mas nao para decisao automatica.
- Relacoes Mail -> Work: viaveis como propostas, nao como relacoes validadas automaticamente.
- Reentry: existe, mas ainda e limitado a casos estreitos e nao resolve authoring amplo.

## O que ainda e bloqueio

1. Cockpit nao cria/edita os objetos centrais do Day 0.

   Sem action panel, o usuario nao consegue operar dominio, fontes, entidades, relacoes, validacao e conflitos como produto.

2. MCP nao e superficie operacional suficiente.

   As nove ferramentas atuais servem para leitura/proposta, nao para configurar e operar dominios locais.

3. Falta versionamento de dominio/charter.

   Sem charter ativo, a tipificacao de Work e e-mail fica informal e dificil de testar.

4. Falta source registration produto.

   Registrar `Work`, subpastas, PST e `.derived` como fontes precisa ser operacao de primeira classe.

5. Falta ingestion run como objeto auditavel de Day 0.

   Work e e-mail precisam de runs com status, contagens, erros, lacunas e candidates.

6. Falta validacao/rejeicao de objetos.

   Candidatos reais de projeto, task, mensagem, thread, decisao e relacao precisam de estado validado/rejeitado.

7. Falta politica pratica para PST stale/partial.

   A superficie atual pode ser usada, mas precisa carregar lacunas em todas as projecoes e impedir claims de completude.

8. Falta ponte governada entre dominios.

   E-mail depende do Work para gerar valor operacional, mas links devem nascer como propostas estruturadas.

## Gargalos reais do Day 0

### Gargalo 1 - Autoria operacional

O maior gargalo nao e parser. E a ausencia de um fluxo local para criar e revisar objetos centrais.

### Gargalo 2 - Fonte e run como objetos visiveis

Sem fonte registrada e ingestion run, nao ha como auditar "o que entrou", "quando entrou", "com quais lacunas" e "com qual resultado".

### Gargalo 3 - Canonicalizacao por validacao humana

Work e e-mail sao cheios de aliases: projetos, nomes de pessoas, threads, tasks e documentos. O sistema precisa de proposta + validacao, nao de auto-merge.

### Gargalo 4 - Escopo de e-mail

E-mail tem alto risco de excesso: anexos, HTML, Teams, Planner, calendario, contatos, newsletters e mensagens pessoais. Day 0 deve ser factual e restrito.

## Menor sequencia de correcoes para passar

Sequencia minima para o Nexus passar no teste Day 0 com restricao operacional aceitavel:

1. Implementar T1 minimo: criar dominio e versao de charter.

   Necessario para `work_portfolio_governance` e `mail_archive`.

2. Implementar T2 minimo: source registration.

   Registrar `Work`, subpastas prioritarias, PST e `.derived`.

3. Implementar T3 minimo: ingestion runs.

   Uma run de inventario Work e uma run de carga `.derived` mail, ambas com status e contagens.

4. Implementar T4/T5 minimo: criar entidades e relacoes manualmente.

   Sem isso, a operacao depende de scripts e nao de produto.

5. Implementar T6 minimo: validar/rejeitar objetos.

   Especialmente projetos, tasks, status, threads, action candidates e project links.

6. Implementar T9 minimo: materializar charter, fontes, runs, candidatos e gaps.

   O Day 0 precisa ser legivel fora do cockpit.

7. Implementar T11 minimo: cockpit action panel simples.

   Mesmo sem frontend polido, precisa haver formulario/acao para dominio, source, run, entity, relation e validation.

8. Implementar T10 minimo apenas depois do cockpit local.

   MCP local deve espelhar operacao, mas nao substituir a primeira superficie humana de controle.

9. Para e-mail, implementar uma ingestao inicial baseada em `.derived`, nao no PST bruto.

   O PST bruto entra como fonte primaria registrada; `.derived` entra como superficie factual usada no Day 0.

## Ordem recomendada de entrada

### Dia 0A - Work minimo

Entrada:

- registrar dominio Work;
- registrar fontes raiz e subpastas prioritarias;
- gerar candidatos de workspace/projeto/status/log;
- validar manualmente 5 a 10 projetos prioritarios;
- publicar dashboard minimo de portfolio.

Resultado esperado:

- inventario inicial confiavel;
- projetos canonicos minimos;
- matriz fonte -> projeto;
- pendencias e lacunas visiveis.

### Dia 0B - Mail factual

Entrada:

- registrar dominio Mail;
- registrar PST e `.derived`;
- ingerir metadados de auditoria;
- carregar mensagens/threads/tasks como candidatos factuais;
- nao extrair decisoes automaticamente.

Resultado esperado:

- arquivo e-mail auditable;
- mensagens e threads localizaveis;
- gaps materializados;
- zero claim de completude.

### Dia 0C - Ponte Mail -> Work

Entrada:

- gerar propostas de relacao entre threads/tasks e projetos canonicos;
- revisar manualmente links de alto valor: OBP, Faltas see, Radon, FGV Cidades;
- materializar links aceitos e rejeitados.

Resultado esperado:

- e-mail passa a alimentar portfolio sem contaminar estado com inferencias nao validadas.

## Veredito

`NAO PASSA AINDA`

Justificativa:

- O plano recente identifica as pecas certas e esta bem orientado para resolver o problema.
- A implementacao atual ainda nao expoe as capacidades minimas de Day 0 por cockpit/MCP.
- O dominio Work poderia ser iniciado de modo assistido e manual, mas nao como produto robusto.
- O dominio e-mail so e seguro como leitura factual da `.derived`; nao como ingestao Nexus completa nem como motor automatico de decisoes.
- Para passar, o Nexus precisa primeiro fechar o conjunto minimo T1, T2, T3, T4/T5, T6, T9 e T11.
