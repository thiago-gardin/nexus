# Nexus — Avaliacao de Usabilidade Day 0
## Data: 2026-04-23
## Escopo: fluxo humano no cockpit e fluxo agente via MCP local_operator

## 1. Objetivo

Avaliar a usabilidade operacional real do baseline Day 0 implementado em 2026-04-21, com foco em dois perfis:

- operador humano usando o cockpit local (`/surface/actions`);
- operador agente usando o MCP com perfil `local_operator`.

O foco aqui nao e validar arquitetura abstrata. O foco e medir friccao real de operacao: descobrir a superficie, executar um fluxo minimo, receber feedback legivel, completar a tarefa e entender o que ainda trava o uso cotidiano.

## 2. Ambiente e evidencias

- API local iniciada com `python -m system.runtime.api.main`
- Healthcheck OK em `http://127.0.0.1:8000/health`
- Banco usado no teste: `C:\Dev\nexus\.nexus\nexus.db`
- Evidencias persistidas:
  - `output/usability/api_stderr.log`
  - `output/usability/agent_mcp_usability.json`
- Evidencias observadas em sessao:
  - navegacao Playwright no cockpit;
  - snapshot do fluxo humano de sucesso;
  - snapshot do fluxo humano de erro;
  - verificacao de console do browser: `0 errors`, `0 warnings`

Observacao: a inicializacao da API emitiu um `RuntimeWarning` de `runpy` por importacao previa do modulo `system.runtime.api.main`, mas nao houve falha funcional nem erro HTTP durante o teste.

## 3. Cenarios executados

### 3.1 Fluxo humano no cockpit

Dominio de teste criado:

- `ux_human_day0_20260423`

Sequencia executada:

1. abrir `/surface/actions`;
2. criar dominio manualmente;
3. criar domain version;
4. copiar `domain_version_id` a partir da tela de resultado;
5. ativar a version manualmente;
6. criar entidade `project` com `workspace_path`;
7. validar a entidade;
8. executar um erro controlado criando `project` sem `workspace_path`.

Resultado do caminho feliz:

- dominio criado com sucesso;
- version criada com sucesso;
- ativacao concluida com `last_event_id` coerente na tela de retorno;
- entidade criada com sucesso;
- validacao concluida com sucesso;
- nenhuma falha de browser observada no console.

Resultado do caminho de erro:

- a tentativa de criar `project` sem `workspace_path` falhou corretamente;
- a tela retornou `Entity Creation Failed`;
- a superficie exibiu erro legivel:
  - `Error Type: ValueError`
  - `Detail: Missing required fields for 'project': workspace_path`
- nao houve stack trace exposta ao operador.

### 3.2 Fluxo agente via MCP `local_operator`

Dominio de teste criado:

- `ux_agent_day0_20260423`

Sequencia executada:

1. listar ferramentas do perfil padrao;
2. listar ferramentas do perfil `local_operator`;
3. criar dominio;
4. criar domain version;
5. ativar version;
6. criar entidade local `project`;
7. validar entidade;
8. testar tentativa de mutacao pelo perfil restrito;
9. testar erro de charter criando `project` sem `workspace_path`.

Resultado:

- perfil padrao exposto com `9` ferramentas;
- perfil `local_operator` exposto com `18` ferramentas;
- tentativa de `create_domain` no perfil padrao falhou corretamente com:
  - `ToolError: Unknown tool: create_domain`
- fluxo completo no `local_operator` concluiu com sucesso;
- entidade final ficou com `validation_status = validated`;
- erro de charter no agente retornou mensagem legivel:
  - `ToolError: Error executing tool create_local_entity: Missing required fields for 'project': workspace_path`

## 4. Achados principais

### 4.1 O que esta bom o suficiente

1. O sistema e operavel nos dois perfis.
   - O caminho humano concluiu dominio -> version -> ativacao -> entidade -> validacao.
   - O caminho agente concluiu dominio -> version -> ativacao -> entidade -> validacao.

2. As fronteiras de autoridade estao claras.
   - O cockpit muta localmente via servico.
   - O MCP padrao continua restrito.
   - O MCP mutante existe apenas no perfil `local_operator`.

3. O feedback de erro esta melhor do que o baseline anterior.
   - No cockpit, o erro e legivel e sem stack trace.
   - No MCP, o erro de tool preserva a causa funcional.

4. A friccao tecnica de bootstrap e baixa.
   - API sobe sem ajustes adicionais.
   - Healthcheck responde.
   - O cockpit e carregavel.
   - O MCP esta utilizavel no proprio ambiente.

### 4.2 Friccoes reais observadas

1. O fluxo humano ainda e excessivamente manual.
   - Depois de criar a domain version, o operador precisa copiar manualmente o `domain_version_id` da tela de resultado para conseguir ativar.
   - O mesmo padrao vale para validacao de objetos: e preciso copiar o `entity_id` antes de validar.

2. O cockpit nao preserva contexto operacional entre etapas.
   - Nao ha contexto persistido de `domain_id` ativo.
   - Nao ha preenchimento automatico da etapa seguinte.
   - Nao ha encadeamento do tipo "Create and activate version" ou "Create and validate entity".

3. As telas de retorno sao informativas, mas pouco acionaveis.
   - O bloco `Navigation` exibiu caminhos como texto e nao como links claros na leitura observada.
   - O operador recebe o resultado, mas a proxima acao ainda depende de leitura manual e copia de IDs.

4. A materializacao nao esta no fluxo de authoring visivel.
   - Logo apos criar os dominios, `tree/domains/ux_human_day0_20260423` e `tree/domains/ux_agent_day0_20260423` nao existiam.
   - Foi necessario chamar manualmente `POST /materialize/domain/{domain_id}` para que os artefatos aparecessem em `tree/`.
   - Isso contraria a expectativa operacional de Day 0 de ver rapidamente o efeito publicado do que acabou de ser criado.

5. O fluxo agente e potente, mas ainda muito baixo nivel.
   - O agente precisa conhecer a ordem correta de operacao.
   - O agente precisa conhecer previamente o charter ativo e seus campos obrigatorios.
   - Nao existe uma tool composta do tipo `bootstrap_domain_day0` ou uma introspeccao curta de "what should I do next?".

### 4.3 Gravidade

- Gravidade alta:
  - materializacao fora do fluxo visivel;
  - excesso de copy/paste de IDs no cockpit.

- Gravidade media:
  - falta de contexto persistente entre etapas;
  - retorno de navegacao pouco acionavel;
  - MCP mutante sem helper de fluxo.

- Gravidade baixa:
  - `RuntimeWarning` de startup sem impacto funcional direto;
  - ausencia de warnings/erros de console no browser foi positiva.

## 5. Veredito

### Veredito humano

`PASSA COM RESTRICOES`

O operador humano consegue concluir o fluxo, mas a experiencia ainda e de painel tecnico, nao de cockpit operacional fluido. O principal problema nao e falha funcional; e a quantidade de estado que o usuario precisa carregar na cabeca e copiar manualmente entre uma etapa e outra.

### Veredito agente

`PASSA COM RESTRICOES`

O agente local consegue operar com confiabilidade pelo perfil `local_operator`, e o isolamento do perfil restrito esta correto. A principal limitacao e ergonomica: o fluxo exige conhecimento procedural detalhado e nao oferece um helper de alto nivel nem uma exposicao resumida do charter ativo antes da mutacao.

### Veredito consolidado Day 0

`PASSA COM RESTRICOES`

O baseline Day 0 esta funcional e governado. Ele nao esta bloqueado para uso real local. Mas ainda nao entrega uma experiencia realmente eficiente de operacao continuada sem conhecimento previo do sistema.

## 6. Menor pacote de correcoes recomendado

1. Adicionar encadeamento de acoes no cockpit:
   - criar version e oferecer botao direto de ativacao;
   - criar entidade e oferecer botao direto de validacao;
   - manter `domain_id` e `domain_version_id` no contexto visivel da sessao.

2. Tornar a navegacao de retorno explicitamente clicavel:
   - links reais para dominio, objeto, history e action panel;
   - CTA claro de proximo passo.

3. Expor materializacao no proprio fluxo operacional:
   - botao no cockpit para materializar o dominio atual;
   - opcionalmente checkbox `materialize after success` nas acoes de Day 0.

4. Adicionar introspeccao curta para agente:
   - tool/read route para obter charter ativo e campos obrigatorios antes da criacao;
   - helper de fluxo para bootstrap local Day 0.

5. Reduzir copy/paste de IDs:
   - exibir IDs com acao de copiar;
   - ou substituir por seletores quando o objeto acabou de ser criado na mesma sessao.

## 7. Conclusao objetiva

O Nexus ja aguenta um uso Day 0 real por humano local e por agente local. O problema atual nao e ausencia de capacidade; e custo operacional desnecessario entre as etapas. O sistema cruzou a fronteira de "nao funciona" para "funciona, mas ainda pede operador especialista".
