# Contrato de entrega — Challenge 003

> **Registro de planejamento.** Este documento descreve o plano inicial, com interface em Streamlit. A entrega final é o Lead Kanban: servidor em Python e interface web em [`solution/`](../solution/README.md), com a regra descrita no [doc 09](09-g3-revisao-fila-foco.md). Ver o [índice](README.md).

**Fonte de verdade:** [README do Challenge 003](../../../challenges/build-003-lead-scorer/README.md), [Guia de Submissão](../../../submission-guide.md), [template](../../../templates/submission-template.md) e [regras do PR](../../../CONTRIBUTING.md). Este documento preserva os tópicos do brief para consulta durante a implementação. O [plano de execução](06-plano-execucao.md) diz como atendê-los.

## Problema e resultado desejado

A Head de RevOps quer que o vendedor abra uma ferramenta, veja sua carteira e saiba **onde focar**. O ponto de partida do case é priorização por intuição em uma equipe de 35 vendedores. O resultado esperado é uma decisão comercial útil, explicada e executável, não apenas uma previsão estatística.

## Deliverables obrigatórios e aceite

| ID | Exigência do brief | Critério verificável na entrega | Evidência prevista |
|---|---|---|---|
| F1 | Solução funcional | Outra pessoa instala, executa e abre o sistema seguindo o README; a tela não é mockup. | Comandos de setup, teste de inicialização e demonstração. |
| F2 | Dados reais do challenge | As quatro tabelas públicas alimentam a preparação; a carteira exibida contém oportunidades reais `Prospecting`/`Engaging`. | Fonte, SHA-256, verificações de chaves e contagens reproduzíveis. |
| F3 | Scoring/priorização além de valor | A ordem usa critérios comerciais documentados; um teste mostra que não equivale a ordenar apenas por preço/valor. | Contrato de variáveis, referência simples, avaliação do método escolhido. |
| F4 | Explicação por negócio | Ao abrir uma oportunidade, o vendedor vê os principais fatores que elevaram ou reduziram sua prioridade e os dados ausentes relevantes. | Tela de detalhe e exemplos verificados. |
| D1 | Setup mínimo | Dependências, versão de Python, download dos dados, comandos e URL local estão documentados. | `solution/README.md` final, executado do zero. |
| D2 | Lógica mínima | Alvo, variáveis, método de potencial, regras de prioridade e motivo das escolhas estão descritos em linguagem clara. | README, documentação técnica curta e código. |
| D3 | Limitações mínimas | Restrições dos dados, validade temporal, uso de campos ausentes e condições para escalar estão explícitos. | Seção de limitações e alertas na interface quando cabíveis. |
| P1 | Process log obrigatório | Há narrativa cronológica de como a IA foi usada, iterações, checagens, erros reais, correções e contribuição do candidato. | `process-log/`, com referências aos artefatos e commits quando existirem. |

**Regra decisiva:** sem process log, o guia informa desclassificação. A solução e o process log devem ficar dentro desta pasta de submissão; o README segue o template oficial.

## Exemplos de soluções aceitas pelo G4

O brief aceita **aplicação web** (Streamlit, React, HTML+JS), **dashboard interativo**, **CLI/relatório priorizado**, **API de score com explicação**, **planilha inteligente** ou **bot de prioridades**. Escolhemos uma **aplicação web local**, pois mostra a decisão na rotina do vendedor e permite uma demonstração direta. Um notebook apoiará a análise, mas não será o produto principal. O plano inicial de tecnologia está em [06-plano-execucao.md](06-plano-execucao.md).

## Critérios de qualidade convertidos em revisão

| Pergunta do avaliador | Nossa checagem antes de considerar pronto |
|---|---|
| Funciona de verdade e o setup é reproduzível? | Executar instalação e fluxo principal do início ao fim em ambiente limpo. |
| O score faz sentido e usa as variáveis certas? | Comparar com referência simples, verificar disponibilidade das variáveis no instante da decisão e inspecionar casos. |
| Um vendedor não técnico entende? | Mostrar prioridade, motivo e próxima ação em linguagem comercial; termos estatísticos ficam em ajuda contextual. |
| A interface ajuda a decidir? | O padrão é uma lista curta de trabalho por vendedor, com filtros e sinalização de dados ausentes. |
| Outro dev consegue manter? | Separar ingestão, preparação, modelo, priorização, explicação e interface; nomes e testes focados em comportamentos críticos. |

## Dicas do brief traduzidas em decisões

- **Utilidade antes de sofisticação.** Um método simples e explicável permanece como referência; modelo complexo só entra se melhorar a decisão.
- **Examinar as variáveis, não presumir sua qualidade.** Etapa, tempo, conta, produto e vendedor são candidatos, mas a auditoria define o que existe antes do resultado. No histórico concluído, `deal_stage` é o desfecho final, portanto não entra como variável de treino.
- **Explicabilidade na experiência.** O vendedor deve saber por que uma oportunidade subiu ou desceu, não receber um número isolado.
- **Uso na segunda-feira.** Ao escolher seu nome, o vendedor vê onde atuar primeiro; manager e regional podem filtrar a carteira.
- **Limite de escopo.** O case não exige CRM ao vivo, autenticação, disparo automático de mensagens, hospedagem pública ou ML sofisticado. Essas possibilidades não podem atrasar F1–P1.

## Process log: conteúdo e formatos

O guia aceita capturas, vídeo, export da conversa, narrativa escrita, histórico de commits e notebook comentado; basta um formato ou uma combinação. Nosso formato principal será **narrativa escrita verificável**, apoiada pelo notebook, pelos ajustes no código e, se útil, por capturas da interface. Cada entrada deve registrar: objetivo, uso da IA, validação humana, erro ou limite encontrado, correção, iteração e decisão final. Não inventaremos erro para preencher um campo.

## Regras de conteúdo

Os dados da solução virão do dataset público do challenge. Projetos da Área de Trabalho podem orientar organização, fluxos comerciais, padrões de interface e decisões técnicas. Nenhum dado, segredo, credencial ou informação confidencial desses projetos pode entrar aqui. Se algum componente genérico vier a ser aproveitado, sua origem, dependências e conteúdo serão revisados antes da inclusão; nenhuma cópia de código é necessária nesta fase.
