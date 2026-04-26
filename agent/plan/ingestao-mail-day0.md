# Ingestao Mail Day 0

Data: 2026-04-21

Dominio proposto: ingestao de e-mail via PST.

Pasta analisada: `C:\Users\gardi\OneDrive\Documentos\Work\50_Memory\e-mail`

## Limites da avaliacao

Esta avaliacao nao abriu nem reexportou o PST. A analise usou a estrutura local e a superficie `.derived`, seguindo o principio de verificar primeiro e executar depois. A superficie atual deve ser tratada como factual, mas com ressalvas de frescor e completude registradas nos metadados.

## Evidencia material observada

Estrutura de primeiro nivel:

- `.derived`
- `_cache`
- `_legacy`
- `inbox`
- `tools`
- `thiago.gardin@fgv.br.pst`
- `e-mailbuckup.zip`
- `AGENTS.md`, `CURRENT_STATE.md`, `TASK.md`, `EXECUTION_LOG.md`, `ACCEPTANCE.md`, `DERIVATION_POLICY.revised.md`, `README-pst-query.md`
- `ONTOLOGY_SCHEMA.agent1.v0_1_0.json`

Fonte PST:

- `thiago.gardin@fgv.br.pst`
- tamanho observado: cerca de 2,43 GB
- `pst_last_write_utc` registrado na superficie derivada: `2026-04-09T00:37:35.576288+00:00`

Superficie `.derived`:

- `00_meta`
- `10_raw`
- `20_index`
- `25_drive`
- `30_ops`
- `40_human`

Status factual da superficie:

- `freshness_state`: `stale`
- `completeness_state`: `partial`
- ultima mensagem indexada: `2026-04-08T13:07:58+00:00`
- primeira mensagem indexada: `2022-12-08T13:27:54+00:00`
- mensagens indexadas: 5.069
- threads indexadas: 2.872
- anexos: 9.981
- itens de calendario: 280
- contatos: 12
- tasks: 25
- pastas: 17
- erros de parse: 0

Lacunas registradas:

- PST mais novo que exportacao.
- `Deleted Items`: contagem do PST excede materializado.
- `Inbox`: contagem do PST excede materializado.
- `Sent Items`: contagem do PST excede materializado.
- `Notes`: 2 itens presentes, mas nao materializados.
- `source_audit_gap_count`: 11.

Observacao importante: os caminhos antigos de `agent_view` citados em memoria operacional nao estavam presentes na estrutura atual observada; a superficie canonica atual parece estar diretamente sob `.derived/00_meta`, `.derived/10_raw`, `.derived/20_index`, `.derived/25_drive`, `.derived/30_ops` e `.derived/40_human`.

## Proposito cognitivo do dominio

O dominio de e-mail deve transformar PST e seus derivados em memoria factual e governada de comunicacoes, capaz de:

- localizar mensagens, threads, anexos, contatos, tasks e eventos;
- preservar proveniencia ate o PST/exportacao/arquivo `.eml`;
- produzir candidatos de projeto, pendencia, decisao e relacao com workspaces;
- distinguir fato bruto de inferencia;
- permitir revisao humana antes de estabilizar decisoes ou links com projetos;
- suportar replay e auditoria de como uma afirmacao foi derivada de uma mensagem ou thread.

O objetivo Day 0 nao e interpretar semanticamente todo o correio. O objetivo e estabilizar a cadeia PST -> exportacao -> raw/index -> candidatos -> validacao.

## PST como fonte

O PST deve ser modelado como `Source` do tipo `pst_archive`.

Metadados minimos:

- caminho absoluto;
- tamanho;
- last write time;
- store display name;
- hash/checksum quando viavel;
- data da exportacao usada;
- ferramenta/processo de exportacao;
- status de frescor;
- status de completude;
- lacunas de auditoria;
- politica de reexportacao.

O PST em si nao deve ser tratado como payload integral dentro do Nexus no Day 0. O payload operacional deve ser a camada derivada factual:

- `.eml` exportados;
- `messages.jsonl`;
- `messages/by_day`;
- `thread_index.jsonl`;
- `message_locator.jsonl`;
- `task_index.jsonl`;
- `attachments/by_month`;
- `calendar_items.jsonl`;
- `contacts.jsonl`;
- `SOURCE_AUDIT.json`;
- `DATASET_STATUS.json`;
- `QUALITY_CHECKS.json`.

## Modelo Day 0

### Payload

Payloads primarios:

- linha de `10_raw/messages.jsonl`;
- particao `10_raw/messages/by_day/YYYY/YYYY-MM-DD.jsonl`;
- `.eml` exportado referenciado por `relative_path`;
- linha de `20_index/message_locator.jsonl`;
- linha de `20_index/thread_index.jsonl`;
- bundle `20_index/group_views/by_thread/*.json`;
- linha de `10_raw/tasks.jsonl`;
- linha de indice de anexo;
- item de calendario ou contato;
- metadados de auditoria em `00_meta`.

Payload deve preservar campos factuais: `message_key`, `thread_key`, `relative_path`, `folder_path`, `date_utc`, `sender_email`, `recipients`, `subject_raw`, `body_excerpt`, `attachment_refs`, `epistemic_status`.

### Entidade

Entidades iniciais:

- `MailArchive`: o PST como arquivo-fonte.
- `MailboxFolder`: Inbox, Sent Items, OBP, Noticias, Archive etc.
- `Message`: unidade factual primaria.
- `Thread`: agrupamento normalizado, inicialmente por assunto normalizado.
- `Participant`: e-mail/nome de remetente ou destinatario.
- `Attachment`: arquivo anexo ou convite de calendario.
- `CalendarItem`: item de calendario.
- `OutlookTask`: task do Outlook.
- `TopicCandidate`: tema candidato extraido de assunto/corpo.
- `DecisionCandidate`: possivel decisao mencionada em mensagem/thread.
- `ActionItemCandidate`: possivel pendencia.
- `ProjectLinkCandidate`: candidato de relacao com projeto/workspace do dominio Work.

### Relacao

Relacoes iniciais:

- `message_in_folder`: mensagem pertence a pasta.
- `message_in_thread`: mensagem pertence a thread.
- `sent_by`: mensagem enviada por participante.
- `sent_to`: mensagem enviada para participante.
- `cc_to`: mensagem copiada para participante.
- `has_attachment`: mensagem tem anexo.
- `mentions_topic`: mensagem ou thread menciona tema candidato.
- `mentions_project`: mensagem ou thread menciona projeto candidato.
- `creates_action_candidate`: mensagem/thread gera pendencia candidata.
- `records_decision_candidate`: mensagem/thread contem decisao candidata.
- `evidenced_by_payload`: entidade/relacao sustentada por linha/arquivo derivado.
- `linked_to_workspace_project`: relacao validada com projeto do dominio Work.

### Evento

Eventos iniciais:

- `MailArchiveRegistered`
- `DerivedSurfaceRegistered`
- `SourceAuditLoaded`
- `MailIngestionRunStarted`
- `MailIngestionRunCompleted`
- `MessageCandidateLoaded`
- `ThreadCandidateLoaded`
- `TaskCandidateLoaded`
- `AttachmentCandidateLoaded`
- `ProjectLinkProposed`
- `DecisionCandidateProposed`
- `ActionItemCandidateProposed`
- `HumanValidated`
- `HumanRejected`

## Pipeline Day 0 plausivel

### Etapa 1 - Registrar fonte PST e superficie derivada

Registrar:

- PST como fonte primaria;
- `.derived/00_meta` como fonte de auditoria;
- `.derived/10_raw` como fonte factual;
- `.derived/20_index` como fonte de indices;
- `.derived/25_drive` como publicacao read-only;
- scripts em `tools` como mecanismo de derivacao, nao como fonte semantica.

O Nexus deve registrar que o dataset atual esta `stale` e `partial`. Isso nao bloqueia todo uso, mas impede conclusoes de completude.

### Etapa 2 - Carregar metadados de auditoria

Antes de qualquer mensagem:

- ler `START_HERE.json`;
- ler `DATASET_STATUS.json`;
- ler `QUALITY_CHECKS.json`;
- ler `SOURCE_AUDIT.json`;
- persistir status de frescor/completude;
- abrir ou atualizar alerta de ingestao para lacunas.

### Etapa 3 - Ingestao factual minima

Carregar como candidatos:

- pastas;
- mensagens via `message_locator.jsonl`;
- threads via `thread_index.jsonl`;
- tasks via `task_index.jsonl`;
- anexos por metadados, nao binario;
- calendario e contatos, se arquivos presentes.

Day 0 deve evitar corpo completo para todas as mensagens dentro do Nexus. O corpo pode ficar como payload referenciado em `.derived`, com excerpts ou campos chave indexados.

### Etapa 4 - Tipificacao leve

Semi-automatizavel:

- classificar mensagens por folder;
- montar threads;
- normalizar participantes por e-mail;
- listar anexos;
- detectar tasks factuais;
- detectar candidatos de projeto por termos de pastas/assuntos conhecidos: `OBP`, `Faltas`, `Radon`, `FGV Cidades`, `Docente`, `CEMASP`.

Nao automatizar:

- decisao final;
- pendencia final;
- link canonico com projeto;
- prioridade;
- interpretacao de compromisso institucional.

### Etapa 5 - Propostas estruturadas

Devem nascer como propostas, nao mutacao automatica:

- `ProjectLinkCandidate`: mensagem/thread possivelmente ligada a `OBP`, `Faltas see`, `Radon`, `FGV Cidades`.
- `DecisionCandidate`: trecho que parece conter decisao.
- `ActionItemCandidate`: pendencia extraida de mensagem, Planner ou task.
- `TopicCandidate`: tema substantivo alem do assunto.
- `CanonicalParticipantCandidate`: unificacao de participante por nome/e-mail.

### Etapa 6 - Validacao humana minima

Obrigatoria para:

- aceitar uma thread como evidência de projeto;
- converter mensagem em task operacional;
- converter mensagem em decisao;
- promover participantes canonicos;
- afirmar que uma lacuna de exportacao nao afeta uma analise especifica;
- vincular anexo a documento fonte de projeto;
- usar e-mail para alterar status de projeto.

## Proveniencia, historico, replay e auditabilidade

Cada objeto derivado de e-mail deve manter:

- `pst_path`;
- `pst_last_write_utc`;
- `export_last_write_utc`;
- `dataset_status_ref`;
- `source_audit_ref`;
- `message_key` ou `task_key`;
- `thread_key`, quando aplicavel;
- `relative_path` do `.eml`;
- `message_partition_path`;
- `bundle_path`;
- `drive_bundle_path`, se existir;
- `epistemic_status`;
- regra de normalizacao usada;
- data de verificacao da derivacao.

Replay Day 0:

1. Identificar entidade ou relacao.
2. Abrir payload derivado por `message_key`/`thread_key`.
3. Verificar status do dataset usado.
4. Reconstituir regra de normalizacao.
5. Checar se houve validacao humana.
6. Verificar se o PST/exportacao estava stale/partial no momento da inferencia.

## Dependencias tecnicas ja suportadas

O Nexus atual ja ajuda em:

- persistir fontes, payloads, entidades, relacoes e eventos;
- registrar propostas e decisoes;
- publicar materializacao em `tree`;
- preservar rastreabilidade;
- ler/incluir JSON/JSONL/Markdown como fonte local, em tese;
- operar com proposta antes de mutacao final.

A pasta de e-mail ja ajuda em:

- exposicao factual file-first;
- metadados de qualidade;
- indices de mensagens, threads, tasks, pastas, anexos;
- publicacao read-only em `25_drive`;
- auditoria de cobertura.

## Dependencias ainda faltantes

Bloqueios para Day 0 robusto:

- Adapter PST/source registration no Nexus.
- Ingestion run de e-mail como objeto de primeira classe.
- Cockpit para registrar PST e revisar status `stale/partial`.
- Cockpit para revisar candidatos de thread, task, decisao e projeto.
- MCP local para registrar fonte e rodar ingestao.
- Perfil de autoridade que permita local mutation controlada sem liberar remote mutation.
- Materializacao Nexus especifica para mail archive, threads, messages, tasks e gaps.
- Politica formal para quando reexportar PST.
- Conexao governada com dominio Work.

## Dependencia logica do dominio Work

O dominio de e-mail nao depende tecnicamente do dominio Work para existir. Ele pode nascer como dominio factual autonomo de comunicacoes.

Mas ele depende logicamente do dominio Work para gerar valor operacional de portfolio:

- Mensagens sobre `OBP`, `Faltas`, `Radon`, `FGV Cidades` e tarefas so viram memoria operacional quando podem se ligar a projetos canonicos.
- Sem dominio Work, o e-mail produz mensagens, threads e participantes, mas nao sabe quais relacoes importam para governanca de portfolio.
- Portanto, a ordem recomendada e:
  1. iniciar dominio Work com projetos canonicos minimos;
  2. iniciar dominio Mail como fonte factual;
  3. criar apenas propostas de link Mail -> Work;
  4. validar manualmente links de alto valor.

## Riscos principais

1. Frescor e completude parcial.

   O PST e mais novo que a exportacao e ha lacunas registradas. O dominio pode operar, mas deve carregar esse alerta em todas as projecoes.

2. Inferencia sem base.

   Assunto e excerpt nao bastam para decisao/task em muitos casos. Mensagens precisam de payload e validacao.

3. Threading por assunto.

   A regra atual de `thread_key` por assunto normalizado e util, mas pode juntar conversas distintas ou separar conversas relacionadas.

4. Participantes duplicados.

   Nome/e-mail/alias institucional podem variar. Canonicalizacao deve ser proposta.

5. Anexos como fonte escondida.

   Muitos documentos importantes podem estar em anexos. Day 0 deve registrar anexos, mas nao tentar extrair todos.

6. Vazamento de dado sensivel.

   Materializacao deve evitar publicar corpo integral ou anexos sensiveis sem regra explicita.

7. Mistura com Outlook tasks e Planner.

   Tasks do PST, notificacoes de Planner e tasks de projeto local sao objetos diferentes. Devem ser reconciliados por proposta.

## Conclusao Day 0 para e-mail

O dominio de e-mail e viavel como dominio factual inicial, desde que comece pela superficie `.derived` e nao pelo parsing total do PST. Ele nao deve ser o primeiro dominio operacional de portfolio, porque sua utilidade depende de projetos canonicos e porque a superficie atual esta `stale` e `partial`.

O Nexus atual ainda nao suporta esse dominio como operacao Day 0 robusta via cockpit/MCP. O plano recente aponta os componentes certos, mas precisa antecipar uma fatia minima de source registration, ingestion run, validacao humana e materializacao de gaps antes de qualquer uso decisorio.
