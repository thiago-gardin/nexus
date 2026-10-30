# Nexus — Decisão arquitetural: federação ontológica por índices

- **Data:** 2026-10-30
- **Tipo:** decisão arquitetural do proprietário
- **Estado da decisão:** aprovada conceitualmente
- **Estado da implementação:** não implementada / não homologada neste registro
- **Fonte de desenho:** [Thiago's OS Draw — página BackEND](https://www.tldraw.com/f/xYJsLAmNF_G42QFJ8SIqB)
- **Escopo:** arquitetura-alvo do Nexus; não altera automaticamente a autoridade técnica da implementação existente

## Decisão

**Nexus é um mecanismo de indexação de entidades e relações orientado por ontologias, constituído por domínios federados autônomos e um índice geral de integração.**

Cada domínio é, funcionalmente, um Nexus próprio: conserva ontologia, regras, índices de entidades e índices de relações. O Nexus geral integra domínios federados mediante padrões comuns e oferece consulta e projeções consolidadas, sem replicar necessariamente toda a complexidade dos atributos próprios de cada domínio.

## Modelo funcional aprovado

1. **Nexus de domínio:** unidade autônoma, com ontologia e regras semânticas/sintáticas, entidades, atributos, relações e referências a artefatos.
2. **Index_Nexus:** índice geral de integração dos domínios federados; apresenta identidades e relações por um contrato ontológico comum, simplificado para consulta e projeções.
3. **Índices de domínio:** índices de entidades e relações vinculados à definição ontológica e a suas regras.
4. **Armazenamento e navegação:** implementação-alvo leve em Google Drive e Google Sheets, organizada por pasta Nexus, índice geral e pastas/índices dos domínios. Hiperlinks permitem referenciar documentos e outros artefatos.
5. **Projeções:** representações derivadas opcionais — por exemplo, bases de conhecimento em formato OKF, grafos, dashboards e outras interfaces — sem obrigar o domínio a adotar a estrutura de uma projeção como armazenamento primário.
6. **Relações multidomínio:** entidades de domínios distintos podem ser relacionadas por referências federadas; um domínio de integração próprio se justifica quando há semântica, ciclo de vida ou responsabilidade de governança próprios, e não apenas por existir uma ligação.

## Princípios de desenho

- Autonomia ontológica local e interoperabilidade por contrato comum.
- Identidade estável e referência ao domínio de origem.
- Simplificação no índice federado, sem perda compulsória de atributos locais.
- Separação entre estado canônico e projeções derivadas.
- Preservação de procedência e autoridade dos domínios.
- Governança verificável; consultas federadas não autorizam mutações indiscriminadas dos domínios.
- Não criar domínios intermediários artificiais para cada relacionamento.

## Questões de especificação ainda abertas

1. Contrato mínimo de federação: identidade global, tipos, referências, mapeamentos ontológicos, autoridade e integridade referencial.
2. Contratos de projeção OKF: origem, seleção, transformação, atualização e validação.
3. Critérios operacionais para criação de domínios de integração.
4. Estrutura exata, esquema de colunas e regras de sincronização dos índices em Drive/Sheets.
5. Estratégia de migração ou coexistência entre a arquitetura-alvo e o runtime anterior baseado em SQLite, materializações e superfícies REST/MCP.

## Relação com o repositório existente

Na leitura de 2026-10-30, `README.md`, `AGENTS.md` e `WORKSPACE_CONTRACT.md` ainda descrevem um produto local-first com SQLite canônico e especificações normativas em `system/00_specs/`. Esses documentos **não foram reescritos** por esta decisão. O presente registro documenta a decisão do proprietário para orientar a futura reconciliação arquitetural, sem alegar que a implementação anterior foi substituída, migrada ou homologada.

## Próxima etapa sugerida

Especificar um contrato mínimo federativo e demonstrar um caso real com dois domínios e uma relação entre eles. Comparar esse fluxo com as capacidades existentes antes de decidir migração, reaproveitamento ou descontinuação de componentes.

## Limites deste registro

Registro documental apenas. Não altera código, schemas, dados, execução, configuração, status de testes ou Control Plane.
