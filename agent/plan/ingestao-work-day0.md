# Ingestao Work Day 0

Data: 2026-04-21

Dominio proposto: governanca de portfolio pessoal de trabalho.

Pasta analisada: `C:\Users\gardi\OneDrive\Documentos\Work`

## Limites da avaliacao

Esta avaliacao inspecionou a estrutura real da pasta e alguns arquivos de governanca/status, mas nao fez indexacao completa nem leitura exaustiva do conteudo. A pasta e grande: a amostragem encontrou dezenas de milhares de arquivos, incluindo muitos artefatos de e-mail, Markdown, JSON/JSONL, codigo, logs, documentos academicos e dados analiticos. Portanto, as propostas abaixo sao operacionais para Day 0, nao uma ontologia definitiva.

## Evidencia material observada

Estrutura de primeiro nivel:

- `00_Inbox`
- `10_Academic`
- `20_Planing&Projects`
- `50_Memory`
- `99_System`
- `Rproj`
- `Nexus`
- `log`
- `testemvp`
- arquivos raiz de governanca: `AGENTS.md`, `IDENTITY.md`, `TOOLING.md`, `VAULT_PROTOCOL.md`, `ARCHITECTURE_REVIEW.md`
- raiz com `.obsidian`, `.git`, `.github`, `.vscode`, `.agent`, `.opencode`

Volumes por grandes areas, em contagem aproximada via filesystem:

- `Rproj`: 1.238 diretorios e 13.235 arquivos.
- `50_Memory`: 1.208 diretorios e 31.453 arquivos.
- `Nexus`: 480 diretorios e 1.778 arquivos.
- `10_Academic`: 86 diretorios e 776 arquivos.
- `20_Planing&Projects`: 32 diretorios e 182 arquivos.
- `log`: 3 diretorios e 31 arquivos.

Tipos de arquivo mais frequentes observados na arvore:

- `.eml`: 14.366
- `.json`: 8.710
- `.md`: 7.966
- `.py`: 4.409
- `.laz`: 2.345
- `.jsonl`: 2.154
- `.ics`: 784
- `.csv`: 498
- `.pdf`: 373
- `.log`: 297
- `.R`: 131
- `.docx`: 103

Subestruturas materialmente relevantes:

- `20_Planing&Projects/OBP` contem `0.STATUS OBP.md`, `AGENTS.md`, `VAULT_PROTOCOL.md`, `TOOLING.md`, `Status Reports`, `agent_log`, `memoria` e planejamento OBP.
- `20_Planing&Projects/mapa estrategico 2026` contem `_STATUS.md`, `2026_Charter.md`, `2026_Portfolio_WIP.md`, `2026_Stakeholders.md`, `2026_Milestones`, dashboard e logs.
- `Rproj/Faltas see` contem roadmaps, trilhas, planos de execucao e artefatos Quarto/HTML.
- `10_Academic/Randon meta-analysis Papers` contem notas e status de frente academica.
- `log` contem logs de sessao por data.
- `50_Memory/e-mail` contem a base de e-mail/PST e sua superficie `.derived`.

## Proposito cognitivo do dominio

O dominio deve transformar a pasta `Work` em uma memoria operacional de portfolio, capaz de responder:

- Quais frentes de trabalho existem?
- Quais estao ativas, paradas, arquivadas ou em risco?
- Quais documentos sao fonte de verdade para cada frente?
- Quais tarefas, decisoes, logs e status sustentam o estado atual?
- Quais projetos dependem de e-mail, dados, repositorios ou artefatos externos?
- O que mudou recentemente e o que precisa de revisao humana?

O objetivo Day 0 nao deve ser extrair toda a semantica da pasta. O objetivo deve ser estabilizar um inventario governado de portfolio, com objetos minimos e rastreabilidade suficiente para operacao.

## Tipos de fonte esperados

Fontes brutas principais:

- Diretorios de primeiro e segundo nivel.
- Arquivos de governanca: `AGENTS.md`, `VAULT_PROTOCOL.md`, `TOOLING.md`, `README.md`, `CURRENT_STATE.md`, `_STATUS.md`, `STATUS.md`, `TASK.md`, `EXECUTION_LOG.md`.
- Logs de sessao: `log/*log-sessao.md`, `agent_log/*.md`, `logs/sessions/*.md`.
- Planejamentos e roadmaps: arquivos com `PLAN`, `PLANO`, `ROADMAP`, `Charter`, `Milestones`, `Dashboard`.
- Artefatos de projeto: `.Rproj`, `pyproject.toml`, `package.json`, `renv.lock`, notebooks, `.Rmd`, `.qmd`, `.html`, `.docx`, `.pdf`.
- Dados e outputs analiticos: `.csv`, `.rds`, `.json`, `.jsonl`, `.laz`, outputs Quarto/HTML.
- Superficies derivadas ja existentes: especialmente `.derived` em e-mail.

## Modelo Day 0

### Fonte bruta

Fonte bruta e aquilo que deve entrar no Nexus como evidência ou payload, sem ser confundido com objeto estabilizado:

- Uma pasta inteira como `Rproj/Faltas see`.
- Um arquivo de status como `20_Planing&Projects/OBP/0.STATUS OBP.md`.
- Um log de sessao.
- Um README.
- Um arquivo de planejamento.
- Um pacote de dados ou output analitico.
- Um repositorio Git ou subworkspace.

### Entidade

Entidades centrais no Day 0:

- `Workspace`: uma area de trabalho material, como `Rproj`, `20_Planing&Projects`, `10_Academic`, `50_Memory`.
- `Program`: agrupamento estrategico, como "portfolio 2026", "academico", "OBP", "Nexus", "memoria operacional".
- `Project`: frente com objetivo, artefatos e estado, como `OBP`, `Faltas see`, `valuation`, `Radon meta-analysis`, `mapa estrategico 2026`, `Nexus`.
- `Task`: pendencia operacional extraida de status, logs, Outlook tasks ou planejamento.
- `StatusRecord`: registro de estado em data/fonte especifica.
- `Decision`: decisao estabilizada em status, log, memoria ou artefato de governanca.
- `SessionLog`: registro de sessao de trabalho.
- `SourceArtifact`: arquivo ou pasta que funciona como evidência.
- `DataAsset`: dataset, planilha, output analitico ou base local.
- `AgentSurface`: contrato local de agente, skill, plugin, MCP, vault ou protocolo.

### Relacao

Relacoes iniciais:

- `belongs_to_workspace`: projeto pertence a workspace.
- `part_of_program`: projeto pertence a programa.
- `has_status`: projeto possui status record.
- `has_task`: projeto possui task.
- `decided_by`: estado ou acao foi definido por decisao.
- `evidenced_by`: entidade/relacao sustentada por fonte.
- `depends_on`: projeto depende de outro projeto, dataset, e-mail, fonte ou decisao.
- `produces`: projeto produz artefato.
- `uses_tooling`: projeto usa protocolo, script, repo ou ambiente.
- `updated_in_session`: projeto ou task foi atualizado em log de sessao.
- `linked_to_email_thread`: projeto possui relacao com thread/mensagem do dominio de e-mail.

### Evento

Eventos no Day 0:

- `SourceRegistered`: arquivo ou pasta registrada como fonte.
- `WorkspaceScanned`: workspace amostrado.
- `ProjectCandidateExtracted`: candidato a projeto extraido.
- `StatusCandidateExtracted`: status candidato extraido.
- `TaskCandidateExtracted`: task candidata extraida.
- `DecisionCandidateExtracted`: decisao candidata extraida.
- `EntityValidated` ou `EntityRejected`: validacao humana.
- `RelationValidated` ou `RelationRejected`: validacao humana.
- `ProjectionPublished`: resumo materializado no `tree/`.

### Decisao ou projecao

Decisao:

- Algo que altera autoridade operacional: "OBP ativo", "Faltas see e frente prioritaria", "usar versao derivada mais recente de anexo", "nao mover/deletar sem confirmacao".

Projecao:

- Dashboard de portfolio.
- Lista de projetos ativos.
- Lista de pendencias por projeto.
- Linha do tempo de sessoes.
- Matriz projeto -> fonte de verdade.
- Matriz projeto -> e-mail/thread relacionado.
- Mapa de riscos de duplicidade e stale status.

## Pipeline Day 0 realista

### Etapa 1 - Registrar dominio e charter

Criar dominio `work_portfolio_governance`.

Charter inicial:

- Escopo: `C:\Users\gardi\OneDrive\Documentos\Work`.
- Unidade factual primaria: fonte local rastreavel.
- Entidades iniciais: workspace, program, project, task, status record, decision, session log, source artifact, data asset.
- Relacoes iniciais: pertence, evidencia, atualiza, depende, produz, linka e-mail.
- Politica Day 0: candidatos automaticos entram como `proposed`; projetos e decisoes so viram `validated` apos revisao humana.

No Nexus atual, a criacao desse dominio e possivel apenas por caminho interno/API existente, nao por cockpit/MCP operacional completo. Pelo plano tecnico recente, isto depende de T1.

### Etapa 2 - Inventario de fontes

Semi-automatizavel no Day 0:

- Listar diretorios de primeiro e segundo nivel.
- Detectar arquivos de status/governanca por nome.
- Detectar repositorios Git e projetos R/Python/Node por marcadores.
- Calcular contagens por tipo de arquivo.
- Registrar fontes com caminho, tipo, tamanho, data de modificacao e checksum quando viavel.

Manual no Day 0:

- Confirmar quais diretorios sao projetos reais versus cache, legado, experimento ou output.
- Definir prioridade operacional: ativo, monitorar, arquivo, ignorar.
- Marcar areas sensiveis ou fora de escopo.

### Etapa 3 - Tipificacao inicial

Semi-automatizavel:

- Diretórios sob `20_Planing&Projects`, `Rproj`, `10_Academic`, `Nexus` e `50_Memory` viram candidatos a `Project` ou `Workspace`.
- Arquivos `_STATUS.md`, `0.STATUS*.md`, `CURRENT_STATE.md` viram candidatos a `StatusRecord`.
- Arquivos `AGENTS.md`, `VAULT_PROTOCOL.md`, `TOOLING.md` viram candidatos a `AgentSurface` ou `GovernanceArtifact`.
- Logs viram candidatos a `SessionLog`.
- Arquivos com `PLAN`, `PLANO`, `ROADMAP`, `Charter`, `Milestones` viram candidatos a `PlanningArtifact`.

Manual:

- Validar nome canonico do projeto.
- Unificar aliases: `Faltas see`, "faltas", "trilhas"; `OBP`, "OBP 2026", "Pitch do Bem Publico"; `Nexus`, `testemvp`, `50_Memory/nexus`.
- Definir programas agregadores.

### Etapa 4 - Extracao minima de conteudo

Day 0 nao deve tentar sumarizar tudo. Deve extrair apenas campos seguros:

- titulo/nome;
- caminho;
- tipo de fonte;
- data de modificacao;
- status textual quando houver marcador claro;
- links/relacoes explicitas por caminho ou nome de projeto;
- trecho curto de evidência para status/task/decisao, sem transformar inferência em fato.

### Etapa 5 - Revisao humana

Necessaria para:

- confirmar projetos ativos;
- aceitar aliases canonicos;
- validar tasks;
- validar decisoes;
- marcar artefatos human-owned;
- distinguir projeto de subproduto/output;
- decidir se e-mail pode criar relacoes com projetos.

## O que nasce manual vs semi-automatizado

Manual no Day 0:

- Charter do dominio.
- Lista canonica de programas.
- Validacao dos projetos prioritarios.
- Decisoes de status ativo/inativo.
- Resolucao de duplicidades.
- Promocao de entidades canonicas.

Semi-automatizado no Day 0:

- Inventario de pastas e arquivos.
- Registro de fontes.
- Deteccao de candidatos por padrao de nome.
- Candidatos de projeto por diretorio.
- Candidatos de status/log/task por arquivo.
- Relacoes `evidenced_by` e `belongs_to_workspace`.

Nao deve ser automatizado no Day 0:

- Decidir prioridade estrategica.
- Inferir decisao a partir de texto solto sem trecho e validacao.
- Mover, renomear ou limpar pastas.
- Unificar projetos por similaridade sem revisao.
- Tratar outputs gerados como fonte soberana.

## Encaixe na arquitetura atual do Nexus

O nucleo atual ja ajuda em:

- persistencia SQLite;
- entidades, relacoes, fontes, payloads e eventos;
- ingestao local de `md/txt/json`;
- propostas e decisoes;
- materializacao em `tree`;
- rastreabilidade por eventos;
- reentry controlado via propostas.

Mas o Day 0 real depende de capacidades que hoje estao no plano, nao plenamente expostas:

- criacao/versionamento de dominio pelo cockpit/MCP;
- source registration visivel;
- authoring manual de entidade e relacao;
- validacao/rejeicao de objetos, nao apenas propostas;
- fila de candidatos por fonte/run;
- cockpit action panel;
- MCP local com perfil operacional;
- materializacao expandida para charter, fontes, runs e conflitos.

## Necessidades minimas de cockpit e MCP

Cockpit precisa expor:

- criar dominio e versao de charter;
- registrar fonte: pasta, arquivo, repo, status, log, dataset;
- rodar inventario Day 0;
- revisar candidatos por fonte e por workspace;
- criar/editar entidade manualmente;
- criar/editar relacao manualmente;
- validar/rejeitar projeto, task, status, decisao e relacao;
- ver dashboard de portfolio;
- abrir conflito/duplicidade;
- publicar materializacao.

MCP precisa expor, no minimo em perfil local:

- `create_domain`
- `create_domain_version`
- `activate_domain_version`
- `register_source`
- `run_ingestion`
- `list_sources`
- `create_local_entity`
- `create_relation_assertion`
- `validate_object`
- `reject_object`
- `open_conflict_case`
- `promote_to_canonical`
- `get_projection`

O MCP atual de nove ferramentas nao basta para operar esse dominio no Day 0; ele permite leitura/proposta, mas nao construcao operacional suficiente.

## Riscos principais

1. Duplicidade de projeto.

   Exemplo: `Nexus`, `testemvp/Nexus`, `50_Memory/nexus` e `C:\Dev\nexus` podem representar linhagens, copias, memoria ou produto atual. A reconciliacao precisa preservar linhagem, nao colapsar tudo em um unico objeto.

2. Confusao entre workspace, projeto e output.

   `Rproj/Faltas see` e projeto; subpastas de output Quarto/HTML nao devem virar projetos canonicos.

3. Status stale.

   Muitos status e logs tem datas diferentes. O Nexus deve representar "estado afirmado por fonte X em data Y", nao fingir que o status mais recente foi validado.

4. Raiz `Work` e tambem vault Obsidian e repo Git.

   A fonte tem semantica multipla: filesystem, vault, repo e workspace. O dominio deve preservar esses papeis.

5. Dados sensiveis e historico pessoal.

   O dominio deve registrar metadados primeiro e conteudo seletivamente. Nem todo arquivo precisa virar payload integral.

6. E-mail como dependencia cruzada.

   Projetos como OBP e Faltas aparecem em e-mail e filesystem. A relacao entre dominios deve nascer como proposta, nao como mutacao automatica.

## Conclusao Day 0 para Work

Este dominio e o melhor candidato para entrar primeiro. Ele tem estrutura local legivel, muitos arquivos Markdown/status/log, governanca existente e baixa dependencia de parsing externo complexo.

Ainda assim, o Nexus atual nao oferece uma operacao Day 0 completa por cockpit/MCP. A operacao seria possivel como prototipo assistido por agente usando scripts e APIs internas, mas nao como produto operacional robusto. O plano recente cobre as lacunas corretas, especialmente T1 a T6 e T9 a T11.
