# Process Log — Challenge 003

## Ferramentas de IA usadas

| Ferramenta | Uso no trabalho |
| --- | --- |
| Codex | Exploração dos CSVs, formulação de hipóteses, implementação, revisão e testes do app. |
| Agente independente | Análise separada de mix de produtos por perfil de empresa, com validação por empresa. |
| Navegador automatizado | Verificação da interface Streamlit, filtros, seleção de linhas e estados de erro. |

## Histórico resumido da conversa

O registro integral, na ordem em que a conversa ocorreu, está preservado em [chat_history.txt](chat_history.txt). A tabela abaixo é uma síntese das decisões que mudaram a análise ou o produto entregue.

| Etapa | Pergunta ou decisão registrada | Resultado incorporado |
| --- | --- | --- |
| Escopo | Foi escolhido o dataset CRM Sales Predictive Analytics e o Challenge 003. As regras de entrega por Pull Request e o nome `gabriel-moreira-beltrami` foram definidos. | Estrutura de submissão criada em `submissions/gabriel-moreira-beltrami/`. |
| Exploração inicial | Foram pedidos histogramas de Won versus Lost, comparação de sucesso entre vendedores, produtos, receita e perfil das empresas. | A análise passou a distinguir taxa de conversão, valor de catálogo e receita do negócio fechado. |
| Qualidade da evidência | Surgiu a hipótese de clusters de receita. A imagem analisada era de `close_value`, registrado após o desfecho. | `close_value` foi marcado como vazamento e excluído de qualquer score de lead aberto. |
| Produto e esforço comercial | Foi perguntado se o produto “se vende” ou se o vendedor faz a diferença. | O CRM não contém contatos, atividades, tentativas ou último toque; essa hipótese ficou explicitamente sem conclusão. |
| Perfil da empresa | Foi investigada a combinação de receita da venda com tamanho e idade da empresa, inclusive por tipo de produto. | Não apareceu um ponto ótimo confiável nem ganho de previsão que justificasse priorizar porte ou idade após considerar o produto. |
| Momento do funil | Foi perguntado quais dados existem quando o lead entra e se seria possível identificar leads parados. | Foram separados os dados disponíveis na entrada dos dados posteriores; não há datas de criação, mudança de estágio ou atividades para medir espera. |
| Decisão operacional | A conversa distinguiu sugestões de prospecção das de negociação. | O app passou a oferecer duas filas: **Prospecção** (“quem abordar”) e **Em negociação** (“onde aumentar a atenção”). |
| Uso do app | Foi solicitado detalhe abaixo da tabela, interface em português e explicação rápida do action score. | A tabela permite selecionar um lead e exibe o detalhe abaixo; textos, ações e filtros foram traduzidos e a regra do score é explicada na interface. |
| Correção de UX | Um filtro por estágio deixava a fila vazia e uma troca de filtro causava `IndexError`. | O filtro agora escolhe a fila compatível e a seleção antiga é ignorada quando não pertence à tabela atual. |
| Preparação da entrega | Foi solicitado revisar a documentação de submissão e preparar a entrega; a abertura do PR foi posteriormente pausada. | Os arquivos de entrega foram preparados, sem commit, push ou Pull Request. |

## Workflow e iterações

1. Inspecionei as quatro tabelas do CRM e normalizei `GTXPro` para `GTX Pro` antes dos joins.
2. Separei os 6.711 negócios fechados dos 2.089 abertos; campos pós-desfecho ficaram fora do score.
3. Comparei produto, vendedor, resultado e perfil de empresa. Preço de catálogo e taxa de vitória por produto sustentaram a prioridade; porte e idade não trouxeram ganho útil depois de controlar por produto.
4. Fiz uma análise independente por empresa. O ganho fora da amostra foi pequeno e não justificou uma regra de roteamento por porte.
5. Transformei os achados em duas filas: Prospecção para primeiro contato e Em negociação para oportunidades de maior valor esperado.
6. Testei compilação, regras de pontuação, filtros de estágio, seleção da linha e detalhe do lead no navegador local.

## Onde a IA errou e como corrigi

- A primeira leitura interpretou que todos os prospects não tinham conta. A checagem corrigiu o dado: 163 dos 500 têm conta; 337 não têm.
- A primeira escala podia ultrapassar 100 e deixar oportunidades sem recomendação. Os componentes foram limitados e validados.
- Uma sugestão de prioridade por espera foi descartada porque não há criação do lead, transição de estágio, último contato nem snapshot.
- A seleção de linha mantinha um índice inválido depois da mudança de filtro. O app agora descarta a seleção fora da tabela atual e abre a fila compatível com o estágio escolhido.

## Julgamento aplicado

Separei “quem abordar” de “onde aumentar a atenção”. Um prospect sem conta conhecida não deve receber contato de alto esforço apenas porque o produto tem alto valor esperado; ele precisa de pesquisa. A explicação do score permanece em linguagem comercial: valor potencial, evidência histórica e contexto da conta.

## Evidências reprodutíveis

- Histórico integral da conversa: [chat_history.txt](chat_history.txt).
- Aplicação: `../solution/app.py`.
- Setup, lógica e limites: `../solution/README.md`.
- Estrutura dos dados e achados: `../solution/docs/analysis-summary.md`.
- Verificações: compilação de `app.py`, intervalo e recomendações do score, e fluxo no navegador local.
