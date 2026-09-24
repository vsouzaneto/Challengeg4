# Process Log — Pedro Pólido — Challenge 002

## 1. Resumo

Usei o **Claude Code** como agente principal (análise dos CSVs com código, pipeline, web app, testes e agentes de
verificação), o **Gemini** dentro do protótipo e num benchmark, e o **Claude Chat** para uma validação cruzada
independente. Foram **10 pedidos meus** nesta sessão, **14 commits** e **38 erros da IA** pegos por verificação: 21
antes de entrarem na entrega e 17 depois. O principal ponto de julgamento humano foi desconfiar da base. Questionei a contagem
do CSV de tickets e pedi uma revisão ponto a ponto só com o arquivo. Ela confirmou a contagem, explicou os "30 mil" e
derrubou o ROI que eu tinha: de "~91 h/mês" para ROI negativo com o volume do próprio CSV. No diferencial, pedi um
chat de atendimento, e a segunda opinião que trouxe de outra IA acrescentou dois pontos que a análise não tinha. No
fechamento, pedi uma validação final com portão de decisão antes do export e do fork: ela parou em 4 textos que não
batiam com os dados, e eu revisei os 40 casos da auditoria de rótulos.

## 2. Ferramentas e por quê

| Ferramenta | Papel no processo | Por que essa |
|---|---|---|
| Claude Code (Claude Opus; parte da validação final com o Claude Fable) | Leu o repositório, analisou os CSVs com código, escreveu 6 scripts de pipeline, o web app (com o chat) e os testes, e orquestrou agentes de verificação independentes | Executa código sobre os arquivos reais e deixa rastro (scripts, commits); nenhum número vem de memória |
| Claude Chat | Validação cruzada da análise do CSV, sem o contexto da sessão | Uma segunda IA para ver se chegava aos mesmos desvios. O texto da resposta e a verificação item a item estão em [`process-log/validacao-cruzada/`](process-log/validacao-cruzada/) `[PEDRO: confirmar que é a resposta do Claude Chat]` `[evidência: anexar print]` |
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
| 1 | "consegue visualizar esse projeto? se sim leia o readme e compreenda o que teremos que fazer" (22/09) | Resumo do repositório, das regras e dos 4 desafios | — | [print 01](process-log/chat-export/prints/01-primeiro-pedido.png) |
| 2 | "qual desafio acha que dá para fazer algo mais diferente que chame a atenção de forma eficiente?" | Recomendação do 002, com uma hipótese a verificar: a base de métricas seria sintética | Escolhi o 002 pela minha experiência; TRIA como base | [print 02](process-log/chat-export/prints/02-escolha-do-desafio.png) |
| 3 | Anexei os dois CSVs: "bora no 002" | Primeira verificação: 8.469 registros, `{product_purchased}` sem preencher em 100% das descrições, 49,3% dos tickets "resolvidos antes da 1ª resposta" | Decidi abrir com a auditoria, usar Gemini e fazer um web app | [print 03](process-log/chat-export/prints/03-decisoes-do-pedro.png); commit `376fc59` |
| 4 | Deixei a IA construir a v1 | Pipeline, detector de gargalos, classificador na base de TI, web app com simulador e triagem ao vivo | Analisei os CSVs por conta própria e conferi as afirmações `[evidência: anexar print/export]` | commits `d7eed68` a `90a8a38` |
| 5 | "coloquei a chave no .env, pode rodar o benchmark" | Benchmark Gemini × classificador; achou um modelo descontinuado | Chave fora do chat e do git | [print 04](process-log/chat-export/prints/04-benchmark.png); commits `680650c`, `7205e61`; `process-log/benchmark-llm/` |
| 6 | Reanexei o CSV ("deveria conter cerca de 30.000 tickets") e pedi uma revisão ponto a ponto, com FATO / INFERÊNCIA / PREMISSA e as respostas reestruturadas por tópico: automatizar, não automatizar, fluxo, ROI | Etapa 1: 8.469 registros confirmados. As 29.808 linhas físicas explicam os "30 mil". 5 agentes analistas + 5 verificadores | Revisei ponto a ponto contra o enunciado e fiz a validação cruzada no Claude Chat, que encontrou os mesmos desvios `[evidência: anexar print do Claude Chat]` | [print 05](process-log/chat-export/prints/05-revisao-dos-30-mil.png) |
| 7 | "suba o novo localhost atualizado" | Página de revisão (Etapas 1 a 3, fluxograma, ROI editável) + 2 auditores independentes: 35 problemas | Correções aplicadas e ROI refeito | commit `fc3222d` |
| 8 | Este process log, a partir da minha narrativa | Primeira versão deste arquivo | Marquei as evidências que faltam | [print 06](process-log/chat-export/prints/06-pedido-do-process-log.png); commit `4cded97` |
| 9 | "constrói o chat do diferencial", e colei a segunda opinião que pedi a outra IA | Chat de atendimento com política testada em 13 cenários e testado no navegador com o Gemini; script que recalcula as 19 afirmações da segunda opinião | O chat como diferencial, pela experiência com agentes de atendimento; trazer a segunda opinião | [print 07](process-log/chat-export/prints/07-chat-e-segunda-opiniao.png); commits `ef898b4` e `425a02e`; capturas 07 a 09 |
| 10 | Validação final com portão de decisão, depois prints, export da conversa, fork e teste do protótipo | Recálculo de 784 afirmações a partir dos CSVs: 4 textos não batiam, e a IA parou sem seguir. Depois: export revisado, fork e teste de ponta a ponta | Revisei os 40 casos de rótulo (concordei em todos) e propus o agente de verificação só de leitura | [prints 08 e 09](process-log/chat-export/prints/08-validacao-final.png); commits `1568a89` e `ba5a03b`; [`chat-export/`](process-log/chat-export/) |

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
| "0 registros repetidos" sem conferir o texto sozinho | A checagem comparava todas as colunas | A **segunda opinião que eu trouxe** apontou 392 duplicatas | Recalculado por script: 392 cópias exatas em 47 grupos, nenhum com o mesmo e-mail ou assunto | Entrou na revisão, com o outro ponto novo (3 tipos no brief, 5 no CSV) |
| Textos que não batiam com os dados: revisão humana marcada como feita, "errar quase metade" (são 55%), top-3 de precisão sem Internal Project, 3 modelos "nas três execuções" | Estavam na entrega | Na validação final que pedi, com portão de decisão | 784 afirmações recalculadas por 9 verificadores e 3 refutadores por divergência | Os 4 corrigidos; a revisão dos rótulos virou fato quando eu a fiz |
| Disse que nenhuma chave do Gemini aparecia na transcrição | A busca só conhecia o formato antigo da chave | Revisão independente do export | Varredura com os dois formatos | A chave está só no zip bruto, fora do repositório e do histórico; vou revogá-la |
| Rascunho do Gemini sem nenhum acento | 1 em 6 rascunhos no chat | Teste dos cenários no navegador | 6 chamadas repetidas com o mesmo ticket | A função pede de novo quando o rascunho vem sem acento: 8 de 8 depois |

A lista completa, com os 38 erros, está em [`process-log/README.md`](process-log/README.md).

## 6. O que eu adicionei que a IA sozinha não faria

- **A escolha do challenge pela minha experiência** em automação de suporte, e não pelo que parecia mais fácil.
- **A TRIA como base:** IA que tria, humano que decide no que é sensível `[evidência: anexar print/export]`.
- **A desconfiança e a checagem manual dos dados** `[evidência: anexar print/export]`. Foi a minha dúvida sobre a contagem
  que disparou a revisão, e foi a revisão que derrubou o ROI de "~91 h/mês".
- **As regras da revisão:** nenhum número de memória, separação entre FATO / INFERÊNCIA / PREMISSA, exemplo real com ID
  do ticket, e nenhuma etapa antes de fechar a anterior.
- **A validação numa segunda IA** (Claude Chat), sem o contexto da sessão. Ela trouxe dois pontos que a análise não
  tinha, e cada afirmação dela foi recalculada ([`validacao-cruzada/`](process-log/validacao-cruzada/)) `[evidência: anexar print]`.
- **As decisões de produto:** abrir a entrega pela auditoria, usar o Gemini só onde ele ganha (tradução e rascunho) e
  publicar um web app.
- **A revisão dos 40 casos da auditoria de rótulos:** concordei com a IA em todos, mas vi que boa parte dos ambíguos
  só se resolve consultando outro sistema (conta, chamado, pedido de compra). Daí a proposta de um agente de
  verificação só de leitura, avaliado no modo sombra (recomendação 6 do README).
- **A escolha do diferencial:** pedi um chat, porque é onde temos mais experiência pelo histórico de agentes já
  construídos. Ele está em [`solution/app/chat.html`](solution/app/chat.html).

## 7. Contagem de iterações

| Fase | Pedidos meus | O que rodou | Correções |
|---|---|---|---|
| Entendimento e escolha | 2 | Leitura do repositório e dos 4 desafios | — |
| Construção da v1 | 2 (dados + 3 decisões) | 5 commits, paridade Python × navegador em 308 textos | 11 erros da IA pegos antes da entrega |
| Benchmark do LLM | 1 | 3 execuções (2 interrompidas por 429/503), 2 commits | 2 erros da IA: modelo descontinuado; resultados só gravados no fim |
| Revisão ponto a ponto | 1 | 10 agentes (5 análise + 5 verificação), 199 fatos checados, 71 exemplos conferidos | 4 erros da IA que já estavam na entrega (30 mil, 2.500/mês, 60/32/8, "independentes") + 7 divergências de formulação |
| Página de revisão | 1 | 2 auditores independentes, 1 commit | 35 problemas; 5 erros da IA corrigidos, 3 deles na própria resposta da revisão |
| Process log | 1 | 1 commit | — |
| Chat e validação cruzada | 1, com a segunda opinião colada | 13 cenários em Node, 7 no navegador com o Gemini, 19 afirmações recalculadas, 2 commits | 9 erros da IA: 7 da construção, 2 apontados pela segunda opinião |
| Validação final, export e fork | 1, mais a minha revisão dos 40 rótulos | 42 agentes na validação, 63 na revisão do export, teste de ponta a ponta, 3 commits | 7 erros da IA: 4 textos, a afirmação sobre a chave e 2 no gerador do export |
| **Total** | **10 nesta sessão**, mais a validação no Claude Chat | **14 commits** | **38 erros da IA corrigidos** (11 + 2 + 4 + 5 + 9 + 7) |

## 8. Evidências anexas

- **Commits** da branch `submission/pedro-polido`, todos em 23/09: `376fc59` 00:13 auditoria · `d7eed68` 00:15 detector
  · `6b35e41` 00:23 triagem · `de2a8e8` 00:41 web app · `90a8a38` 00:47 README e log · `680650c` 00:59 correção do
  Gemini · `7205e61` 01:46 benchmark · `fc3222d` 15:48 revisão só com o CSV · `4cded97` 15:51 este log ·
  `ef898b4` chat de atendimento · `425a02e` validação cruzada; em 24/09: `1568a89` validação final e revisão dos
  rótulos · `ba5a03b` export da conversa · e o commit deste fechamento.
- [`process-log/chat-export/`](process-log/chat-export/): a conversa inteira com o Claude Code, conferida contra o
  export bruto, com 9 prints dos momentos da linha do tempo acima.
- **Fork:** [github.com/P0lid0/ai-master-challenge](https://github.com/P0lid0/ai-master-challenge).
- [`process-log/README.md`](process-log/README.md): log técnico, com decisões, hipóteses refutadas e os 31 erros.
- [`process-log/benchmark-llm/`](process-log/benchmark-llm/): logs brutos das 3 execuções do benchmark.
- [`process-log/auditoria-rotulos/candidatos.csv`](process-log/auditoria-rotulos/candidatos.csv): 40 casos, com o
  veredito da IA, o do Gemini e o meu.
- [`process-log/screenshots/`](process-log/screenshots/): 9 capturas do protótipo (07 a 09 são do chat).
- [`process-log/validacao-cruzada/`](process-log/validacao-cruzada/): o texto da segunda opinião, sem edição, e cada
  afirmação recalculada por [`06_validacao_cruzada.py`](solution/pipeline/06_validacao_cruzada.py).
- [`solution/app/chat.html`](solution/app/chat.html): o chat do diferencial; a política está em
  [`js/chat-policy.js`](solution/app/js/chat-policy.js) e os testes em [`tests/chat.mjs`](solution/app/tests/chat.mjs).
- [`solution/app/revisao.html`](solution/app/revisao.html) e
  [`05_revisao_csv.py`](solution/pipeline/05_revisao_csv.py): a revisão ponto a ponto.

## O que falta eu anexar

- [ ] Revogar a chave do Gemini que ficou no zip bruto do export, e cadastrar uma nova na Vercel no deploy.
- [ ] Enviar a branch para o fork, publicar na Vercel e abrir o PR.
- [ ] Print da conversa da validação cruzada (o texto já está em `process-log/validacao-cruzada/`), e confirmar que é a do Claude Chat.
- [ ] Print do pedido para usar a TRIA como base.
- [ ] Prints da minha análise manual dos CSVs.
- [ ] O trecho `[PEDRO: ...]` do README sobre o que a Tria mudou na proposta.
