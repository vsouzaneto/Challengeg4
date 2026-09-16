# Process log — análise inicial

**Registro organizado em 15/09/2026 a partir da conversa já ocorrida.** É uma síntese retrospectiva; não é uma gravação integral nem um diário com horários exatos. Novas decisões serão acrescentadas conforme acontecerem.

## Ferramentas e papéis

Claude produziu o plano inicial. Codex revisou esse plano, inspecionou os dados, escreveu/executou a auditoria e ajudou a estruturar as alternativas. Dhiego orientou a investigação e introduziu/restringiu decisões de produto. A revisão considerou experiência profissional e projetos anteriores como contexto; o pacote não inclui código ou dados privados desses sistemas.

## Decomposição

Entender a solicitação do diretor → conferir a evidência → identificar lacunas → escolher intervenção → avaliar → comunicar. Hoje a atividade permanece nas etapas de análise e definição; construção prevista para amanhã.

## Iterações documentadas

Os nove marcos abaixo são agrupamentos temáticos retrospectivos, não contagem de prompts ou sessões.

| Marco | Intervenção / evidência | Mudança |
|---|---|---|
| 1 | Dhiego pediu crítica do plano de Claude | A proposta inicial passou a ser hipótese revisável. |
| 2 | Auditoria por Codex encontrou ausência de abertura, ordem temporal inválida e cobertura limitada de satisfação | Abandonar duração inventada e separar cenário de economia medida. |
| 3 | Dhiego trouxe feedbacks públicos e questionou a prioridade do protótipo | Interface funcional passou ao escopo principal. |
| 4 | Discussão das 4–6h e do process log | Contar preparação no esforço total; documentar processo real. |
| 5 | Dhiego encerrou a comparação com candidatos e priorizou entender o problema | Nenhuma nova investigação de soluções concorrentes desde essa decisão. |
| 6 | Dhiego propôs aplicação própria, OpenRouter e n8n | Opções registradas; stack e utilidade do LLM ainda abertas. |
| 7 | Dhiego questionou colocar IA em tudo | ADR 0001: separar regras, inferência e decisão humana. |
| 8 | Dhiego trouxe flags e acompanhamento; em seguida decidiu reservá-los para o futuro | ADR 0002 e mapa de dados necessários, sem ampliar o protótipo atual. |
| 9 | Dhiego definiu hoje como análise e amanhã como implementação | Roadmap, status e pacote inicial para versionamento. |

## Erros e revisões da IA

- O plano de Claude repetiu o volume aproximado do brief e propôs analisar tempos sem verificar a semântica dos campos. A auditoria de Codex verificou contagens e limites.
- O plano inicial sugeriu volume multiplicado por tempo médio como desperdício; a revisão distinguiu espera/tempo decorrido de esforço ativo.
- Codex inicialmente tratou interface como opcional; a discussão com Dhiego mudou a prioridade.
- A sugestão de Codex de mostrar flags avançadas em cenários simulados foi retirada após Dhiego restringir essas ideias a propostas futuras.
- A preparação não pode desaparecer da contabilização de esforço. Nenhum total de horas foi medido até aqui.

## Contribuição do candidato

Escolheu conduzir entendimento antes da implementação; exigiu fronteira determinística; trouxe experiência de operação para discutir prioridades; definiu dados necessários como condição de evolução; delimitou o escopo. As descobertas computacionais produzidas por Codex permanecem atribuídas a essa revisão.

## Evidências e limites

- [Trechos literais selecionados da conversa](evidencias/trechos-da-conversa.md).
- [Trechos do plano inicial](evidencias/plano-inicial.md).
- [Auditoria](../solution/auditar_datasets.py) e [resultado](../solution/reports/auditoria-datasets.json).
- [ADR 0001](../docs/decisions/0001-fronteira-entre-regras-e-ia.md) e [ADR 0002](../docs/decisions/0002-flags-priorizacao-e-acompanhamento.md).

A consulta anterior a avaliações públicas serviu para entender expectativas de entrega; os aplicativos dos candidatos não foram reproduzidos. A auditoria dos nossos CSVs ocorreu antes dessa comparação. Não há captura de aplicativo funcionando, modelo treinado ou resultado de integração a apresentar nesta etapa.

O primeiro registro Git reúne o trabalho de análise já ocorrido. Não foi reconstruída uma sequência fictícia de commits anteriores. O cronômetro das atividades anteriores não foi registrado; duração permanece não apurada, incluindo preparação e pesquisa.

## Continuação — perguntas de CX e exploração preliminar

Dhiego pediu exploração dos números à luz de sua experiência em atendimento e distinguiu urgência de criticidade. Acrescentou hipóteses de penalização recorrente do cliente, repetição de informação, respostas parciais e dificuldade de compreensão pelo atendente. Também autorizou commits que demonstrem progresso. O primeiro commit local registra o pacote de análise inicial; esta continuação corresponde ao aprofundamento posterior.

Codex executou nova exploração integral: distribuição por canal/tipo/prioridade, notas baixas entre avaliados, busca literal de sinais, consistência de identidade para emails repetidos e tamanho das resoluções. Inspecionou uma amostra de 20 resoluções (seed 42), exemplos de termos de urgência e trechos que revelaram falsos positivos de palavra-chave. Produziu [script](../solution/explorar_cx.py), [resultados](../solution/reports/exploracao-cx.json) e [análise para discussão](../solution/analise-preliminar-cx.md).

Achados adicionais incluem 78 de 165 textos com `urgently` marcados Low/Medium, identidade não reconciliada em emails repetidos, 2.881 casos aguardando cliente e resoluções de 3–8 palavras. A interpretação separa contagens do arquivo de hipóteses sobre a operação: não conclui que houve violação de SLA, reincidência real, atendimento inadequado ou churn. Não houve implementação de produto nem mudança automática do escopo.
