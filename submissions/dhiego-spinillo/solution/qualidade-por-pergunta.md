# Qualidade por pergunta — universos utilizáveis e pontos de atenção

**15/09/2026 · continuação da análise de CX.** [Script](auditar_coortes.py) · [Resultados agregados](reports/coortes-qualidade.json) · [ADR 0003](../docs/decisions/0003-universos-analiticos-e-qualidade.md).

## 1. O que significa limpar neste case

Uma linha pode servir para contar volume por canal e não servir para calcular duração ou reconstruir a jornada do cliente. Por isso, a separação é por pergunta. Os arquivos originais permanecem intactos. As exclusões abaixo não são somáveis: um registro pode ter mais de um problema.

A [página original do Dataset 1](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) informa que o domínio de exemplo nos emails é intencional por privacidade e que satisfação é uma nota de 1 a 5 dos tickets fechados. A presença em Kaggle e essa explicação não comprovam autenticidade de todas as colunas, unicidade do email nem consistência dos eventos. Nos arquivos há indícios fortes de texto artificial; não identificamos o mecanismo completo de geração para afirmar como cada variável foi produzida.

## 2. O que sobra após cada verificação

| Pergunta | Universo observado | Separação / resultado | Uso permitido e limite |
|---|---|---|---|
| Quantos tickets e por canal? | 8.469 IDs únicos | Todos podem entrar na descrição do arquivo | Não confundir distribuição da amostra com demanda real por período. |
| Qual é a satisfação registrada? | 2.769 notas | Todas são inteiras entre 1 e 5; 5.700 ausências | Descrever os avaliados, todos fechados. Ausência não vira zero; sem inferir tendência de queda. |
| Houve reincidência do mesmo cliente? | 139 emails ambíguos, envolvendo 288 registros | Restam 8.181 registros e 8.181 emails distintos | Sem repetição restante nem identidade validada, não há jornada longitudinal demonstrável por email. |
| Qual é a duração/SLA? | 2.769 pares de eventos | 1.365 invertidos; 1.404 em ordem não negativa | Nenhum se torna apto a duração desde abertura: esse evento está ausente em toda a base. |
| O texto representa uma conversa natural validada? | 8.469 descrições | Todas contêm `{product_purchased}`; 54 grupos repetidos após normalização, envolvendo 457 registros | Leitura exploratória com ressalvas. Não remover artefato e declarar a semântica validada. |
| Dá para testar classificação no D2? | 47.837 registros | Todos têm texto e rótulo; oito classes; nenhuma duplicata exata normalizada | Candidatos à avaliação. Quase duplicatas e qualidade semântica dos rótulos ainda pendentes. |

Não usar descarte indiscriminado de linhas com qualquer campo vazio: isso excluiria 5.700 tickets e deixaria apenas fechados, eliminando justamente a visão de abertos e pendentes. Valores ausentes de resolução/satisfação nesses estados têm significado e não são, por si sós, sujeira.

### Identidade: precisão sobre o tamanho do problema

O máximo observado foi de **quatro nomes distintos por email**, não dezenas. A regra adotada separa os 288 registros dos 139 grupos para análises de identidade. Não tenta escolher um nome correto sem fonte de reconciliação e não remove esses tickets das estatísticas que independem de identidade.

### Rótulos: um achado adicional

Em 49 dos 54 grupos de descrições idênticas após normalizar caixa/espaços há mais de um `Ticket Type` (446 registros); em 49 há mais de uma prioridade (447 registros). Isso dificulta aprender rótulos confiáveis usando somente esse texto. Não significa que toda divergência seja erro: o mesmo texto pode exigir prioridade diferente por contrato ou contexto não representado.

## 3. Análise de sensibilidade: o que muda retirando identidade ambígua?

Esse exercício verifica estabilidade descritiva; identidade não é condição necessária para contar notas por ticket.

| Indicador | Todos os registros | Sem os 288 registros ambíguos |
|---|---:|---:|
| Notas disponíveis | 2.769 | 2.663 |
| Média da nota | 2,991 | 2,993 |
| Textos com `urgently` | 165 | 160 |
| Desses, prioridade Low/Medium | 78 (47,3%) | 75 (46,9%) |

A separação quase não altera esses dois retratos. Isso não prova autenticidade ou validade semântica; apenas mostra que a ambiguidade de email não explica, sozinha, os sinais observados.

## 4. O pedido urgente com prioridade baixa

Dhiego interpretou o caso de recuperação urgente de arquivos como suspeita relevante de classificação inadequada. A análise registra esse caso como **candidato à revisão humana**, preservando o rótulo original. O texto contém urgência declarada, mas faltam prazo confirmado, impacto, alternativas e regra de prioridade.

Não estabelecer uma janela universal de recuperação de arquivos com base no ticket. O ponto verificável aqui é a necessidade de esclarecer prazo e consequência da demora. Limpar esse caso apagando a divergência esconderia uma hipótese operacional que merece investigação.

## 5. Atendentes: pergunta válida, informação ausente

Nenhum dos dois arquivos contém identificação de atendente, carteira atribuída, eventos de transferência, N1/N2/N3 ou sequência de reabertura. `Customer Name` identifica o cliente, não o atendente. Não é possível comparar volume, qualidade ou recorrência por profissional.

Para essa análise futura: `agent_id`, eventos de atribuição, tempo disponível/escala, tempo ativo quando mensurável, categoria/complexidade, reabertura, motivo, resolução confirmada e satisfação com data. Comparar apenas contagem ou nota bruta pode confundir desempenho com carga, complexidade ou especialização; pessoas que recebem escalonamentos lidam com uma seleção diferente de casos.

## 6. Satisfação: o que existe de fato

- `Customer Satisfaction Rating`, escala 1–5 conforme o dicionário da fonte.
- 2.769 notas disponíveis, cobrindo 32,7% dos tickets, todas entre fechados.
- Distribuição: nota 1 = 553; 2 = 549; 3 = 580; 4 = 543; 5 = 544.
- Média 2,991. Agrupamento exploratório de notas 1–2: 1.102/2.769 = 39,8%.
- Não há campo NPS, pergunta de recomendação, momento da resposta ou identidade de atendente.

Podemos descrever essas notas; não convertê-las em NPS, assumir uma definição oficial de CSAT percentual ou demonstrar queda ao longo do tempo. A queda é parte do cenário do desafio, não uma tendência comprovada pelo CSV.

## 7. Aguardando cliente: incorporar a distinção de Dhiego

| Situação | Exemplo operacional de Dhiego | Dados para distinguir |
|---|---|---|
| Informação necessária | Qual guia o cliente precisa, dentre várias? | Item faltante, alternativas oferecidas, pergunta e mensagem que originou a dúvida. |
| Documento/evidência necessária | Falta arquivo ou comprovante para prosseguir | Documento solicitado, responsável, prazo e recebimento. |
| Confirmação da solução | Cadastro corrigido; cliente precisa validar se ficou correto | Ação realizada, evidência, pedido de confirmação e aceite/rejeição. |
| Nova pergunta / possível retrabalho | Informação já enviada é solicitada novamente | Sequência completa e vínculo entre dado original e pergunta repetida. |

Os exemplos são ilustrações do usuário, não registros observados no CSV. Os 2.881 pendentes não podem ser distribuídos entre essas situações com as colunas disponíveis. Prazo, responsável e eventual pausa de SLA dependem da política aplicável; não presumir que todo status pendente interrompe todo compromisso.

## 8. Onde IA poderia ajudar — hipótese ainda em análise

Ajudar o atendente a separar: pedido do cliente, fatos já informados, ambiguidades, itens faltantes e itens atendidos/pendentes. A saída deveria mostrar evidência textual e sugerir uma pergunta objetiva, sem repetir o que já foi respondido nem preencher lacunas com suposições.

Essa tarefa é diferente de prever categoria ou sentimento. Para avaliar se respondeu A quando o cliente pediu B, seriam necessárias conversas adequadas e revisão humana de compreensão e cobertura. O D1 atual não sustenta essa validação; nenhuma funcionalidade foi adicionada ao escopo automaticamente. Prioridade e ação continuam sujeitas à política determinística do ADR 0001.
