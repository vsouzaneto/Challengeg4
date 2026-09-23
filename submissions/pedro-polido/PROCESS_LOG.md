# Process Log — Pedro Pólido — Challenge 002

## 1. Resumo

Usei o **Claude Code** como agente principal (análise dos CSVs com código, pipeline, web app, testes e agentes de
verificação), o **Gemini** dentro do protótipo e num benchmark, e o **Claude Chat** para uma validação cruzada
independente. Foram **8 pedidos meus** nesta sessão, **8 commits** de solução (este log entra no 9º) e **22 erros da
IA** pegos por verificação: 13 antes
de entrarem na entrega e 9 depois. O principal ponto de julgamento humano foi desconfiar da base. Questionei a contagem
do CSV de tickets e pedi uma revisão ponto a ponto só com o arquivo. Ela confirmou a contagem, explicou os "30 mil" e
derrubou o ROI que eu tinha: de "~91 h/mês" para ROI negativo com o volume do próprio CSV.

## 2. Ferramentas e por quê

| Ferramenta | Papel no processo | Por que essa |
|---|---|---|
| Claude Code (Claude Opus, no terminal) | Leu o repositório, analisou os CSVs com código, escreveu 5 scripts de pipeline, o web app e os testes, e orquestrou agentes de verificação independentes | Executa código sobre os arquivos reais e deixa rastro (scripts, commits); nenhum número vem de memória |
| Claude Chat | Validação cruzada da análise do CSV, sem o contexto da sessão | Uma segunda IA para ver se chegava aos mesmos desvios `[evidência: anexar print/export]` |
| Gemini 3.5 Flash-Lite | No protótipo: traduz tickets em português e redige rascunhos de resposta. No benchmark: comparado ao classificador | Chave que eu já tinha. Medido nos mesmos 234 tickets, classifica pior (42–64% contra 85,9%), então ficou só onde agrega |
| TRIA (meu assistente de recrutamento e seleção) | Base de arquitetura: IA tria e encaminha, humano decide nos casos sensíveis | Já opero triagem automatizada em produção `[evidência: anexar print/export]` |

## 3. Decomposição do problema

**Escolha do challenge.** Pedi ao Claude Code que lesse o README do repositório e o do desafio como prompt inicial e
me dissesse qual dos 4 teria mais efetividade para mim. Com o contexto de quem sou e do que já construí, fomos no
**002**, pela minha bagagem em automação de suporte. Pedi que usasse a TRIA como base `[evidência: anexar print/export]`.

**Divisão antes de construir**, seguindo as perguntas do Diretor de Operações:
1. **Os dados sustentam um diagnóstico?** Verificar a base antes de analisar.
2. **O que automatizar e o que não?** Medir onde a IA acerta, e deixar humano o que é sensível ou incerto.
3. **Mostrar funcionando:** um protótipo que o avaliador abre e usa.
4. **ROI:** fórmula explícita, com premissas visíveis e editáveis.

**Três decisões minhas antes da construção:** abrir a entrega pela auditoria dos dados; usar o Gemini, com a chave num
`.env` fora do git; e publicar um web app em vez de Streamlit.

## 4. Linha do tempo das iterações

| # | O que pedi (resumo) | O que a IA entregou | Minha decisão / ajuste | Evidência |
|---|---|---|---|---|
| 1 | "consegue visualizar esse projeto? se sim leia o readme e compreenda o que teremos que fazer" (22/09) | Resumo do repositório, das regras e dos 4 desafios | — | export da conversa |
| 2 | "qual desafio acha que dá para fazer algo mais diferente que chame a atenção de forma eficiente?" | Recomendação do 002, com uma hipótese a verificar: a base de métricas seria sintética | Escolhi o 002 pela minha experiência; TRIA como base | export da conversa |
| 3 | Anexei os dois CSVs: "bora no 002" | Primeira verificação: 8.469 registros, `{product_purchased}` sem preencher em 100% das descrições, 49,3% dos tickets "resolvidos antes da 1ª resposta" | Decidi abrir com a auditoria, usar Gemini e fazer um web app | export; commit `376fc59` |
| 4 | Deixei a IA construir a v1 | Pipeline, detector de gargalos, classificador na base de TI, web app com simulador e triagem ao vivo | Analisei os CSVs por conta própria e conferi as afirmações `[evidência: anexar print/export]` | commits `d7eed68` a `90a8a38` |
| 5 | "coloquei a chave no .env, pode rodar o benchmark" | Benchmark Gemini × classificador; achou um modelo descontinuado | Chave fora do chat e do git | commits `680650c`, `7205e61`; `process-log/benchmark-llm/` |
| 6 | Reanexei o CSV ("deveria conter cerca de 30.000 tickets") e pedi uma revisão ponto a ponto, com FATO / INFERÊNCIA / PREMISSA e as respostas reestruturadas por tópico: automatizar, não automatizar, fluxo, ROI | Etapa 1: 8.469 registros confirmados. As 29.808 linhas físicas explicam os "30 mil". 5 agentes analistas + 5 verificadores | Revisei ponto a ponto contra o enunciado e fiz a validação cruzada no Claude Chat, que encontrou os mesmos desvios `[evidência: anexar print/export]` | export da conversa |
| 7 | "suba o novo localhost atualizado" | Página de revisão (Etapas 1 a 3, fluxograma, ROI editável) + 2 auditores independentes: 35 problemas | Correções aplicadas e ROI refeito | commit `fc3222d` |
| 8 | No diferencial, pedi um chat | `[evidência: anexar print/export]` | — | — |
| 9 | Este process log | — | — | este arquivo |

## 5. Onde a IA errou e como corrigi

| Erro da IA | Sintoma | Como detectei | Como verifiquei | Resultado |
|---|---|---|---|---|
| Chamou a base de "o de 30 mil tickets" antes de medir | O brief fala em ~30.000; a análise usava 8.469 | **Desconfiei da contagem** e pedi uma reanálise, porque toda a solução depende dessa base | 4 leituras diferentes do arquivo (leitor CSV do Python, pandas com os dois motores, `on_bad_lines="warn"`): 8.469 em todas, 0 linhas descartadas, IDs de 1 a 8.469 sem buracos, mesmo SHA-256. Validação cruzada no Claude Chat `[evidência: anexar print/export]` | A contagem estava certa. **1 cabeçalho + 8.469 registros + 21.338 quebras de linha dentro das descrições = 29.808 linhas físicas**, e são elas que batem com os "~30 mil" |
| ROI de "~91 h/mês com premissas conservadoras" | O volume de 2.500/mês vinha do brief, não do CSV | Na revisão ponto a ponto | Fórmula explícita, 3 cenários, sensibilidade por premissa | Com o proxy do CSV (~353/mês): ~13 h/mês. Nas automações que o CSV sustenta, ROI de 12 meses provável de **−65,0%**, que se paga a partir de ~1.000 tickets/mês |
| Percentuais de automação (60/32/8) apresentados sem dizer a base | Eram da base de TI (47.837 tickets), não do CSV | Na revisão ponto a ponto | Conferência das fontes de cada número | Marcados como "base de TI" no app e no README |
| "Pedir detalhes" para 5.868 descrições "genéricas" | A frase genérica é só a abertura | Um agente auditor independente | Recontagem: nenhuma descrição termina na frase genérica (mediana de 38 palavras depois dela) | O único sinal medido é o `{error_message}` vazio: pelo fluxo, **126 tickets**, não 6.023 |
| Texto em português roteado sozinho com **100% de confiança** | O modelo reconhecia 3 de 14 palavras | Teste manual com frase em português | Cobertura de vocabulário: mediana de 100% nos tickets reais, 8% a 30% em português e espanhol | Nova regra: abaixo de 50%, o ticket vai para uma pessoa ou é traduzido |
| Modelo padrão do Gemini já descontinuado | Erro 404 com o `gemini-2.5-flash` | Teste com 7 modelos antes do benchmark | O protótipo teria quebrado no deploy | Troca para o `gemini-3.5-flash-lite` (~1 s por chamada) |
| "Tempo de resolução" descrito como uniforme | O gráfico mostrava um triângulo | Revisão visual das telas | Teste KS (p < 0,001) e forma medida: desvio de 9,6 h contra 9,8 h teóricos | Texto corrigido na página e no script |

A lista completa, com os 22 erros, está em [`process-log/README.md`](process-log/README.md).

## 6. O que eu adicionei que a IA sozinha não faria

- **A escolha do challenge pela minha experiência** em automação de suporte, e não pelo que parecia mais fácil.
- **A TRIA como base:** IA que tria, humano que decide no que é sensível `[evidência: anexar print/export]`.
- **A desconfiança e a checagem manual dos dados** `[evidência: anexar print/export]`. Foi a minha dúvida sobre a contagem
  que disparou a revisão, e foi a revisão que derrubou o ROI de "~91 h/mês".
- **As regras da revisão:** nenhum número de memória, separação entre FATO / INFERÊNCIA / PREMISSA, exemplo real com ID
  do ticket, e nenhuma etapa antes de fechar a anterior.
- **A validação numa segunda IA** (Claude Chat), sem o contexto da sessão `[evidência: anexar print/export]`.
- **As decisões de produto:** abrir a entrega pela auditoria, usar o Gemini só onde ele ganha (tradução e rascunho) e
  publicar um web app.
- **A escolha do diferencial:** pedi um chat, porque é onde temos mais experiência pelo histórico de agentes já
  construídos `[evidência: anexar print/export]`.

## 7. Contagem de iterações

| Fase | Pedidos meus | O que rodou | Correções |
|---|---|---|---|
| Entendimento e escolha | 2 | Leitura do repositório e dos 4 desafios | — |
| Construção da v1 | 2 (dados + 3 decisões) | 5 commits, paridade Python × navegador em 308 textos | 11 erros da IA pegos antes da entrega |
| Benchmark do LLM | 1 | 3 execuções (2 interrompidas por 429/503), 2 commits | 2 erros da IA: modelo descontinuado; resultados só gravados no fim |
| Revisão ponto a ponto | 1 | 10 agentes (5 análise + 5 verificação), 199 fatos checados, 71 exemplos conferidos | 4 erros da IA que já estavam na entrega (30 mil, 2.500/mês, 60/32/8, "independentes") + 7 divergências de formulação |
| Página de revisão | 1 | 2 auditores independentes, 1 commit | 35 problemas; 5 erros da IA corrigidos, 3 deles na própria resposta da revisão |
| Process log | 1 | — | — |
| **Total** | **8 nesta sessão**, mais a validação no Claude Chat e o pedido do chat | **8 commits** de solução | **22 erros da IA corrigidos** (11 + 2 + 4 + 5) |

## 8. Evidências anexas

- **Commits** da branch `submission/pedro-polido`, todos em 23/09: `376fc59` 00:13 auditoria · `d7eed68` 00:15 detector
  · `6b35e41` 00:23 triagem · `de2a8e8` 00:41 web app · `90a8a38` 00:47 README e log · `680650c` 00:59 correção do
  Gemini · `7205e61` 01:46 benchmark · `fc3222d` 15:48 revisão só com o CSV.
- [`process-log/README.md`](process-log/README.md): log técnico, com decisões, hipóteses refutadas e os 22 erros.
- [`process-log/benchmark-llm/`](process-log/benchmark-llm/): logs brutos das 3 execuções do benchmark.
- [`process-log/auditoria-rotulos/candidatos.csv`](process-log/auditoria-rotulos/candidatos.csv): 40 casos, com o
  veredito da IA e o do Gemini.
- [`process-log/screenshots/`](process-log/screenshots/): 6 capturas do protótipo.
- [`solution/app/revisao.html`](solution/app/revisao.html) e
  [`05_revisao_csv.py`](solution/pipeline/05_revisao_csv.py): a revisão ponto a ponto.

## O que falta eu anexar

- [ ] Export desta conversa com o Claude Code em `process-log/chat-export/`. **Antes, revisar:** a conversa tem dados
      pessoais meus (telefone e e-mail) lidos da memória do assistente.
- [ ] Prints ou export da validação cruzada no Claude Chat.
- [ ] Print do pedido para usar a TRIA como base.
- [ ] Prints da minha análise manual dos CSVs.
- [ ] Evidência do pedido do chat no diferencial, e alinhar o texto com o protótipo entregue.
- [ ] Minha revisão dos 40 casos de rótulo (coluna `veredito_pedro`, hoje vazia) e os 2 trechos `[PEDRO: ...]` do README.
