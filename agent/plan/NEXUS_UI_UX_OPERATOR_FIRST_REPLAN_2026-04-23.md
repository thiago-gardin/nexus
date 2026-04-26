# Nexus - UI/UX Operator-First Replan
## Data: 2026-04-23
## Status: replanejamento apos feedback humano sobre `Operate Workspace v1`
## Escopo: cockpit humano local-first, com foco em authoring operacional real

## 1. Decisao de produto

O `Operate Workspace v1` nao deve ser tratado como base suficiente para UX humana.

Ele resolveu contexto tecnico, mas ainda parte do modelo errado:

- formulario primeiro;
- objeto tecnico primeiro;
- IDs e JSON ainda visiveis demais;
- authoring separado do mapa;
- fluxo humano ainda muito parecido com chamada manual de API.

Para o cockpit humano do Nexus, isso e conceitualmente insuficiente.

### Nova decisao

O cockpit deve migrar de:

- `pagina de authoring com cards empilhados`

para:

- `workbench relacional com painel de acao contextual`.

Em termos praticos:

- `Map` vira o contexto operacional principal para humano;
- `Operate` deixa de ser uma pagina de formularios e passa a ser uma camada de acao do mesmo workbench;
- o humano opera por selecao, foco, contexto, sugestao e painel lateral;
- o humano nao deve escrever JSON nem lembrar UUIDs para operacao normal.

## 2. Leitura consolidada do problema

## 2.1 O erro do cockpit atual

O problema principal do `http://127.0.0.1:8000/surface/operate` nao e estetico.
E de modelo cognitivo.

Hoje a interface assume que o operador:

- sabe qual ID precisa;
- entende a ordem procedural das mutacoes;
- consegue traduzir atributos em JSON;
- entende o charter antes da interface explicar o charter;
- aceita authoring fora do contexto relacional visual.

Isso produz uma superficie tecnicamente correta e humanamente inadequada.

## 2.2 O que o feedback humano fechou

O feedback desta rodada fecha requisitos que nao estavam suficientemente cristalizados:

1. IDs devem ser gerados automaticamente.
2. Campos dependentes nao podem exigir memoria manual de objetos.
3. Dependencias devem aparecer como listas clicaveis, pickers ou busca assistida.
4. Atributos devem nascer de schema de dominio e ser renderizados como campos dinamicos.
5. O formulario nao deve dominar a tela; deve abrir sob demanda em menu/painel.
6. `Operate` e `Map` nao podem seguir filosofias de UX diferentes.
7. A experiencia-alvo e mais proxima de `workbench + drawer + inspector` do que de `dashboard + forms`.

## 3. O que o Nexus V2 ensina

Base usada:

- repo: `https://github.com/thiago-gardin/Nexus-V2---Google-IA-Studio-Bootstrap`
- screenshots anexados nesta conversa

## 3.1 Filosofia extraida do V2

O valor do V2 nao esta em copiar a implementacao literalmente.
Esta em quatro decisoes de UX muito mais corretas para o Nexus:

### A. O grafo e contexto, nao decoracao

O operador entra no sistema vendo:

- dominio ativo;
- foco atual;
- profundidade;
- filtros por tipo e relacao;
- painel de inspeccao;
- stream/eventos.

Isso coloca a operacao dentro de um contexto relacional vivo.

### B. A acao nasce como painel lateral

No V2, a acao aparece como `ActionPanel`/`Symmetry Panel`, acionado por botao de quick action ou por contexto vindo do grafo.

Isso e importante porque:

- o operador nao perde a cena principal;
- a acao e percebida como mutacao sobre um contexto existente;
- o formulario ocupa papel subordinado ao workbench.

### C. A interface trabalha com escolhas humanas, nao com objetos tecnicos

Nos formularios do V2 aparecem:

- `Select Domain`;
- tipos permitidos;
- campos dinamicos obrigatorios;
- busca por label para source/target;
- prefill de relacao a partir do grafo;
- justificativa explicita.

Mesmo quando a implementacao ainda e incompleta, a gramatica e correta:

- selecionar;
- escrever em linguagem humana;
- confirmar.

### D. O sistema tem uma gramatica unificada

O shell, o grafo, o painel lateral, o inspector e o event stream parecem partes do mesmo sistema.

No Nexus atual, `Map` e `Operate` ainda parecem produtos diferentes.
Isso precisa acabar.

## 3.2 O que NAO deve ser copiado do V2

O V2 nao deve ser usado como referencia normativa de dados ou de governanca.

Nao devemos importar sem filtro:

- tipagem ad hoc;
- mutacoes que bypassem o runtime atual;
- dependencias ou store front-end paralelas ao core;
- semantica fraca de ID e status.

O que deve ser copiado e a filosofia de interacao:

- contexto antes de acao;
- selecao antes de digitacao;
- painel lateral em vez de pagina de formulario;
- grafo como superficie operacional;
- inspeccao e mutacao no mesmo ecossistema visual.

## 4. Novo principio de UX do cockpit

### P-UX1 - Humanos operam por rótulo, nao por ID

UUID e `domain_version_id` continuam existindo no sistema, mas:

- nao sao entrada normal de authoring humano;
- aparecem apenas como detalhe secundario, copiavel, auditavel.

### P-UX2 - Humanos operam por campos, nao por JSON

Nenhum fluxo frequente de Day 0 deve exigir JSON manual.

JSON pode continuar existindo:

- para debug;
- para reentry;
- para operador avancado;
- para MCP.

Mas nao como caminho padrao do cockpit humano.

### P-UX3 - Operate e Map compartilham a mesma casca

Nao pode existir uma UX de authoring e outra UX de mapa sem continuidade.

O workbench deve ser um so, com estados diferentes:

- navegar;
- inspecionar;
- criar;
- relacionar;
- validar;
- publicar.

### P-UX4 - A interface deve conhecer o dominio

O dominio ativo precisa dirigir:

- tipos disponiveis;
- relacoes permitidas;
- campos obrigatorios;
- tipos de input;
- dependencias referenciaveis;
- placeholders e ajuda curta.

### P-UX5 - O sistema propoe a proxima acao

Depois de criar, selecionar, validar ou publicar, a interface deve sugerir:

- o que acabou de acontecer;
- o que ainda falta;
- o proximo clique natural.

## 5. Diagnostico do gap tecnico-ux

## 5.1 O que ja existe e pode ser reutilizado

- runtime governado;
- charter ativo por dominio;
- leitura de `operate_context`;
- leitura de charter via REST/MCP;
- `Map` como superficie de relacao;
- materializacao e trilha de auditoria;
- validacao/rejeicao governada;
- eventos e inspectors.

## 5.2 O que falta para UX humana real

O gargalo nao e falta de backend de mutacao.
O gargalo e falta de contrato de interface para authoring humano.

Hoje faltam:

1. geracao automatica de identificadores;
2. selectores pesquisaveis para entidades e relacoes;
3. schema de formulario humano por tipo;
4. campos dinamicos por dominio;
5. continuidade real entre mapa, inspector e painel de acao;
6. visualizacao/editabilidade de propriedades sem JSON;
7. acoplamento natural entre criar -> revisar -> validar -> publicar.

## 5.3 Gap estrutural mais importante

O charter atual sustenta parcialmente a UI, mas ainda nao sustenta uma UI humana boa.

Com o que existe hoje, conseguimos derivar:

- tipos permitidos;
- relacoes permitidas;
- campos obrigatorios.

Mas ainda nao conseguimos derivar bem:

- label humano do campo;
- tipo de widget;
- enum opcoes;
- se o campo referencia outra entidade;
- se o campo e texto curto, longo, data, numero, status, path;
- ordem de exibicao;
- agrupamento visual;
- valor default;
- ajuda contextual.

Conclusao:

o proximo plano de UX precisa incluir um pequeno contrato de `form schema` derivado do dominio.

Isso nao exige reabrir arquitetura.
Exige acrescentar metadados de apresentacao no charter ou uma projecao derivada dele.

## 6. Modelo alvo de UI

## 6.1 Shell unificado

O cockpit deve convergir para um `Nexus Workbench`.

Layout alvo:

- rail lateral fixa de modos;
- topo com dominio, foco, profundidade, busca e estado do sistema;
- canvas central;
- painel lateral direito de inspecao;
- painel inferior opcional para stream/decisions/sessions;
- drawer lateral esquerdo de acao, aberto sob demanda.

## 6.2 Modos do workbench

### `Overview`

Pulso, filas, atividade, propostas, mudancas, alertas.

### `Map`

Modo principal de exploracao e authoring humano.

### `Inspect`

Pode continuar como rota, mas o comportamento principal deve viver no painel lateral do workbench.

### `Flow`

Timeline, jobs, materializacao, reentry, eventos.

### `Audit`

Fila de propostas, decisoes, conflitos, rejeicoes.

### `Operate`

Nao desaparece como conceito.
Mas deixa de ser uma pagina de cards.

`Operate` vira:

- um estado do workbench;
- ou a abertura programatica do drawer de acao no mesmo shell do `Map`.

## 6.3 Novo papel do mapa

O mapa deixa de ser somente leitura estrutural.
Ele passa a ser:

- contexto principal;
- ponto de selecao;
- origem de prefill de relacao;
- origem de abertura de painel de detalhe;
- origem de acao contextual.

Exemplo:

- clicou num node -> abre inspector;
- menu do node -> `criar relacao a partir daqui`;
- selecionou dominio e tipo -> drawer ja abre filtrado;
- criou entidade -> node aparece e inspector muda para o objeto criado.

## 7. Sistema de componentes alvo

## 7.1 Componentes macro

- `WorkbenchShell`
- `ModeRail`
- `TopContextBar`
- `GraphCanvas`
- `InspectorRail`
- `EventStreamDock`
- `ActionDrawer`

## 7.2 Componentes de contexto

- `DomainSelector`
- `FocusSelector`
- `DepthControl`
- `TypeFilterChips`
- `RelationFilterChips`
- `PublicationStatusBadge`
- `PendingQueueBadge`

## 7.3 Componentes de acao

- `ActionMenu`
  - lista curta de acoes;
  - abre o formulario correspondente;
  - ex.: `Nova entidade`, `Nova relacao`, `Novo dominio`, `Nova charter`, `Registrar fonte`, `Validar`, `Materializar`.

- `ActionDrawer`
  - substitui cards jogados na tela;
  - suporta tabs ou submodos:
    - `Entity`
    - `Relation`
    - `Domain`
    - `Charter`
    - `Source`
    - `Other`

- `ActionForm`
  - renderizado dinamicamente pelo tipo de acao.

- `ResultToast` / `InlineReceipt`
  - confirma o resultado sem quebrar o contexto do mapa.

## 7.4 Componentes de formulario humano

- `GeneratedIdPreview`
  - mostra slug/ID sugerido;
  - nao exige digitacao;
  - permite override so quando fizer sentido.

- `DomainTypePicker`
  - usa tipos do charter.

- `EntityPicker`
  - busca por label;
  - lista clicavel;
  - opcao de recentes e relacionados ao contexto.

- `RelationTypeChips`
  - chips clicaveis;
  - indica se esta no charter, se e frequente, se e cross-domain.

- `DynamicFieldGroup`
  - renderiza campos do schema do dominio.

- `JustificationField`
  - permanece obrigatorio quando a governanca exigir;
  - sempre em linguagem humana.

- `PropertyEditor`
  - editavel por campos;
  - nao JSON cru;
  - com fallback avancado para operador especialista.

## 7.5 Componentes de detalhe

- `NodeDetailPanel`
- `PropertyList`
- `RelationList`
- `EventsList`
- `ActionsPanel`
- `AuditTrailBlock`

## 8. Contrato de authoring humano

## 8.1 Regras fechadas

Para humano:

- nao digitar UUID;
- nao montar JSON;
- nao informar `domain_version_id`;
- nao informar `source_entity_id` ou `target_entity_id` por texto tecnico;
- nao navegar para uma tela separada so para continuar o fluxo.

## 8.2 Como cada objeto deve nascer

### Dominio

Entradas humanas:

- nome;
- descricao;
- justificativa;
- eventualmente tipo/template.

Saidas automaticas:

- `domain_id` proposto automaticamente a partir do nome;
- verificacao de conflito;
- preview de slug/id antes de salvar.

### Domain Version / Charter

Nao deve ser um JSON grande em textarea.

Precisa de:

- resumo da charter vigente;
- clone de versao anterior;
- blocos editaveis por secao;
- campos obrigatorios por tipo em tabela estruturada;
- diffs entre versoes.

### Entity

Entradas humanas:

- dominio;
- tipo;
- label;
- justificativa;
- atributos dinamicos renderizados.

Saidas automaticas:

- ID interno;
- defaults;
- sugestoes de propriedades;
- validacao inline por campo.

### Relation

Entradas humanas:

- dominio;
- entidade origem por seletor;
- entidade destino por seletor;
- tipo da relacao por chips/lista;
- directionality por toggle;
- justificativa.

Saidas automaticas:

- ID interno;
- inferencia de contexto;
- warning quando relacao estiver fora do charter.

## 8.3 Visualizacao e edicao

O humano precisa conseguir:

- abrir um objeto;
- ver propriedades legiveis;
- editar propriedades autorizadas em campos nativos;
- ver relacoes incidentes;
- abrir historico;
- acionar validacao/rejeicao/publicacao dali.

O objeto nao pode ser so um YAML/JSON exibido em bloco cru.

## 9. Novo contrato de schema para UI

## 9.1 Minimo derivavel ja

A curto prazo, a UI pode derivar do charter atual:

- `allowed_entity_types`
- `allowed_relation_types`
- `required_fields`

Isso permite um primeiro drawer humano melhor que o atual.

## 9.2 Contrato adicional necessario

Para uma UX realmente boa, cada tipo local deve poder expor um `ui_schema`.

Estrutura sugerida:

```yaml
entity_form:
  project:
    display_name: Projeto
    fields:
      - key: workspace_path
        label: Workspace
        kind: path
        required: true
        placeholder: C:/Dev/nexus
      - key: status
        label: Status
        kind: enum
        options: [draft, active, blocked, done]
      - key: owner
        label: Responsavel
        kind: entity_ref
        entity_types: [person]
```

Equivalente para relacoes:

```yaml
relation_form:
  depends_on:
    display_name: Depende de
    source_types: [project, task]
    target_types: [project, task]
    directionality: directed
```

## 9.3 Regra importante

Esse `ui_schema` nao substitui a regra de dominio.
Ele apenas torna a regra operavel por humano.

## 10. Replanejamento das superfices

## 10.1 `Map`

Passa a ser o primeiro modo de trabalho humano.

Deve concentrar:

- selecao de dominio;
- selecao de foco;
- filtros;
- acao rapida;
- inspector;
- event stream.

## 10.2 `Operate`

Passa a ser:

- uma abertura do drawer;
- ou um estado de `Map`;
- nunca mais uma pagina longa de formularios empilhados.

## 10.3 `Inspect`

Deve sobreviver como rota profunda, mas a leitura diaria deve acontecer no inspector lateral.

## 10.4 `Flow`

Continua importante, mas nao precisa competir com o authoring.
Deve servir de apoio:

- jobs;
- mutacoes recentes;
- materializacao;
- reentry.

## 11. Sequencia correta de implementacao

## Fase UX-R1 - Reframing e contrato de interface

Objetivo:

- abandonar o modelo `ActionCard page`;
- formalizar `Map + Drawer + Inspector + Stream`.

Entregas:

- documento de contrato do workbench;
- inventario dos fluxos humanos prioritarios;
- decisao formal de convergencia `Map/Operate`.

## Fase UX-R2 - Shell unificado do workbench

Objetivo:

- unificar `Map` e `Operate` no mesmo shell.

Entregas:

- rail lateral coerente;
- top bar de dominio/foco/depth;
- areas fixas de canvas, inspector e drawer.

Aceite:

- trocar entre explorar e operar sem mudar de produto mental.

## Fase UX-R3 - Action drawer humano

Objetivo:

- substituir cards empilhados por painel lateral de acao.

Entregas:

- `ActionMenu`;
- tabs `Entity`, `Relation`, `Other`;
- fluxo contextual;
- abertura por quick action e por contexto do mapa.

Aceite:

- o operador abre uma acao sem perder o mapa.

## Fase UX-R4 - IDs automáticos e pickers

Objetivo:

- remover digitacao de IDs do fluxo humano.

Entregas:

- preview de slug/ID;
- busca por label;
- pickers de origem/destino;
- seletores clicaveis de dominio e objeto.

Aceite:

- criar e validar sem copiar UUID.

## Fase UX-R5 - Form schema dinamico

Objetivo:

- trocar JSON por campos dinamicos.

Entregas:

- renderer de campos por schema;
- fallback para required fields;
- infraestrutura para `ui_schema`.

Aceite:

- criar `project`, `task` e outros tipos frequentes sem textarea JSON.

## Fase UX-R6 - Inspector operacional

Objetivo:

- tornar detalhe e acao inseparaveis.

Entregas:

- painel lateral com propriedades, relacoes, eventos e acoes;
- validacao/rejeicao/publicacao a partir do detalhe;
- trilha de auditoria resumida.

Aceite:

- operador consegue abrir, entender e agir sobre um objeto sem navegar por varias paginas.

## Fase UX-R7 - Publicacao e governanca no fluxo

Objetivo:

- integrar materializacao, review e conflito ao workbench.

Entregas:

- badge de sincronizacao;
- CTA de materializacao no contexto certo;
- quick review de propostos;
- conflito visivel no inspector.

Aceite:

- o operador entende o estado do dominio sem sair do workbench.

## Fase UX-R8 - Revalidacao humano/agente

Objetivo:

- provar que o novo modelo resolve o problema real.

Entregas:

- novo teste de usabilidade humano;
- novo teste de usabilidade agente;
- comparacao objetiva contra o baseline `2026-04-23`.

## 12. Critérios de aceite do novo cockpit humano

O replanejamento so deve ser considerado bem sucedido quando:

1. humano cria dominio sem pensar em `domain_id`;
2. humano cria entidade sem JSON;
3. humano cria relacao sem UUID;
4. campos obrigatorios do dominio aparecem como inputs nativos;
5. a acao acontece no mesmo workbench do mapa;
6. o objeto criado fica imediatamente visivel e inspecionavel;
7. validacao e materializacao aparecem como proximas acoes naturais;
8. `Map` e `Operate` parecem a mesma experiencia, nao duas UIs.

## 13. Veredito desta rodada

O `Operate Workspace v1` foi um passo util de backend-to-UX, mas nao e o modelo certo de cockpit humano.

O replanejamento correto e:

- `operator-first`;
- `graph-contextual`;
- `drawer-based`;
- `schema-driven`;
- `selection-over-json`;
- `label-over-id`.

Esse passa a ser o plano de referencia para a proxima execucao de UI/UX.
