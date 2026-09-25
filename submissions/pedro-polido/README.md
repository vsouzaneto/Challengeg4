# Submissão — Pedro Pólido — Challenge 002

## Sobre mim

- **Nome:** Pedro Henrique Pólido Martins
- **LinkedIn:** [linkedin.com/in/pedro-pólido](https://www.linkedin.com/in/pedro-p%C3%B3lido)
- **Challenge escolhido:** 002 — Redesign de Suporte

**Protótipo no ar:** [triagem-suporte-ia.vercel.app](https://triagem-suporte-ia.vercel.app) · [revisão só com o CSV](https://triagem-suporte-ia.vercel.app/revisao.html) · [chat de atendimento](https://triagem-suporte-ia.vercel.app/chat.html) · **Rodar local:** [instruções](#como-rodar)

---

## Executive Summary

O dataset de métricas de suporte tem **todas as marcas de dado gerado** (a confirmar com a empresa): 49,3% dos tickets fechados foram "resolvidos antes
da primeira resposta", 100% das descrições têm variáveis de template sem preencher, e um modelo com todas as colunas
prevê a nota de satisfação no nível do chute (20,9%). Qualquer gargalo ou fator de satisfação tirado dali é ruído, e é
exatamente isso que uma IA entrega quando recebe o brief sozinha. Por isso entreguei três coisas:

1. um **detector de gargalos validado**, que não inventa padrão (0 gargalos nos dados atuais) e encontra quando existe
   (+3 h num segmento canal × prioridade é detectado em 82% das simulações);
2. a **automação medida onde o texto é real**, na outra base (47.837 tickets de TI, não o CSV): 60% dos tickets roteados
   sem humano com 97,2% de acerto, 32% com 2 sugestões para o atendente, 8% sempre humanos;
3. um **protótipo rodando** com essa política, o simulador de ROI, a triagem ao vivo e um **chat de atendimento**, com o
   LLM (Gemini) só onde ele ganha. Medido nos mesmos tickets, ele classifica pior (42–64% contra 85,9%), mas traduz e redige bem.

**Recomendação principal:** instrumentar o suporte para medir tempo e volume de verdade. Com dados como os do CSV, começar
pelas automações de fluxo que ele sustenta (acuse de recebimento, lembrete, pedido da mensagem de erro que faltou); a
triagem automática, medida na base de TI, entra em modo sombra. O ganho depende do volume, que o CSV não informa: com
2.500 tickets/mês (premissa do brief), ~91 h/mês de triagem liberadas; com o proxy do CSV (~353/mês), ~13 h/mês.

**Revisão ponto a ponto usando só o CSV:** [`solution/app/revisao.html`](solution/app/revisao.html), gerada por
[`05_revisao_csv.py`](solution/pipeline/05_revisao_csv.py): verificação do arquivo (8.469 registros; os "~30 mil" batem
com as 29.808 linhas físicas), o que automatizar e o que não, fluxo e ROI com premissas editáveis.

**Chat de atendimento (diferencial):** [`solution/app/chat.html`](solution/app/chat.html) mostra o fluxo numa conversa,
com o avaliador no papel do cliente e do atendente. A IA confirma o recebimento na hora e aplica as regras de risco
(reembolso, perda de dados, invasão, tema sensível) antes de qualquer modelo. Ela também pede o que falta, roteia quando
tem confiança e passa para uma pessoa quando não deve decidir. O Gemini traduz e redige, mas nada do que ele escreve
chega ao cliente sem o clique do atendente. Cada um dos 7 cenários abre direto por link (`chat.html?cenario=1` a `7`).

**Validação cruzada:** o Claude Chat analisou o mesmo CSV sem ver os achados desta entrega, e cada afirmação dele foi recalculada
por script ([`process-log/validacao-cruzada/`](process-log/validacao-cruzada/)). Das 19 afirmações, 16 se confirmam,
2 divergem e 1 não é verificável. Duas eram novas e entraram na revisão.

---

## Solução

### Abordagem

| Etapa | Pergunta | Onde está |
|---|---|---|
| 1. Auditoria | Os dados operacionais sustentam um diagnóstico? | [`01_auditoria_dataset1.py`](solution/pipeline/01_auditoria_dataset1.py) |
| 2. Detector | Como achar gargalo sem cair em ruído? | [`02_diagnostico_gargalos.py`](solution/pipeline/02_diagnostico_gargalos.py) |
| 3. Triagem | Quanto da triagem a IA assume, com que acerto, e o que fica humano? | [`03_triagem_dataset2.py`](solution/pipeline/03_triagem_dataset2.py) |
| 4. LLM | Vale usar LLM para classificar? Onde ele agrega? | [`04_benchmark_llm.py`](solution/pipeline/04_benchmark_llm.py) |
| 5. Protótipo | Funciona com dados reais, na mão de quem usa? | [`solution/app`](solution/app) |
| 6. Revisão | O que o CSV sozinho sustenta? | [`05_revisao_csv.py`](solution/pipeline/05_revisao_csv.py) → [`revisao.html`](solution/app/revisao.html) |
| 7. Chat | Como o fluxo fica numa conversa, com o atendente aprovando o que a IA escreve? | [`chat.html`](solution/app/chat.html) + [`chat-policy.js`](solution/app/js/chat-policy.js) |
| 8. Validação cruzada | Outra IA (Claude Chat) chega aos mesmos desvios? | [`06_validacao_cruzada.py`](solution/pipeline/06_validacao_cruzada.py) → [`validacao-cruzada/`](process-log/validacao-cruzada/) |

Princípio em todas as etapas: tentar derrubar cada achado antes de reportá-lo. Os limiares da política foram escolhidos em
validação cruzada **no treino**, e o conjunto de teste (9.568 tickets) só foi usado para medir.

### Resultados

**1. O Dataset 1 não sobrevive à auditoria** (9 verificações reproduzíveis)

| Verificação | Resultado |
|---|---|
| Registros no arquivo | 8.469, em 29.808 linhas físicas: os ~30.000 do brief batem com as linhas (21.338 quebras ficam dentro das descrições) |
| Descrições com `{product_purchased}` sem preencher | 100% |
| Tickets "resolvidos antes da 1ª resposta" | 49,3%: a diferença é um triângulo simétrico em zero, a assinatura de dois horários sorteados de forma independente |
| Janela de todas as respostas e resoluções | 27 horas, para compras de 2020 a 2021 |
| Resoluções que descrevem alguma ação técnica | 0 de 2.769 (são frases aleatórias do Faker) |
| Tipo do ticket × assunto | sem associação detectável (p = 0,98) |
| Texto do ticket × assunto | sem associação detectável (p = 0,91) |
| Prever a nota de satisfação com todas as variáveis | 20,9% de acerto = chutar a nota mais comum |

A validação cruzada acrescentou dois pontos: **392 descrições são cópia exata de outra** (47 grupos, nenhum com o mesmo
e-mail ou assunto: é texto de template reaproveitado), e **o brief cita 3 tipos de ticket, mas o CSV tem 5**. Os 2 que
faltam no brief, reembolso e cancelamento, somam 40,7% dos tickets.

O que uma análise ingênua reportaria, e o teste que derruba: a "pior combinação" (Email × Medium × Product inquiry,
+3,4 h) aparece com os tempos embaralhados em 78% das simulações.

**2. Detector de gargalos:** 149 segmentos testados com correção para comparações múltiplas. Resultado: **0 gargalos**
de tempo e 0 de satisfação. Em ruído puro, 8% das rodadas têm algum alarme falso; a análise por "pior média" erra em
100%. Com os 2.769 tickets fechados do CSV (cerca de um mês no volume do brief; o CSV não informa o volume), ele detecta
+2 h num canal inteiro (92%) e +3 h em canal × prioridade (82%).

**3. Onde o tempo se perde, no texto real** (Dataset 2)

- **17% dos tickets chegam como cadeia de e-mails** (30% em Administrative rights, 1% em Purchase). O modelo acerta igual
  com 1 ou com várias mensagens, então ler a cadeia deixa de ser trabalho humano.
- **Hardware é o "ralo":** recebe 28% do volume, mas 38% dos tickets mal roteados.
- **Vício de rótulo:** 61% dos pedidos sem conteúdo ("access hello please provide kind regards") estão rotulados como
  HR Support. O modelo aprendeu o vício e "acerta" 93% deles. Na política, pedido vazio nunca é roteado.
- **Auditoria de rótulos:** dos 40 "erros" com confiança ≥ 90% revisados um a um (pela IA e depois por mim, sem
  discordância), **15 são erros do rótulo**, 13 do
  modelo e 12 ambíguos. O acerto real da faixa automática é maior que o medido.

**4. Classificador e política** (TF-IDF + regressão logística, 85,7% de acerto, 96,1% com a fila certa entre as 2
primeiras, calibrado: ECE 0,012)

| Faixa | Regra | Volume | Acerto |
|---|---|---|---|
| Roteamento automático | confiança ≥ 88,5% | 59,9% | 97,2% |
| Assistido (2 sugestões) | 48% a 88,5% | 31,8% | 93,5% (fila certa entre as 2) |
| Triagem humana | < 48%, tema sensível, ou texto fora do padrão | 7,7% | — |
| Pedir detalhes | pedido sem conteúdo | 0,6% | — |

**5. LLM × classificador** (mesmos 234 tickets de teste, [`04_benchmark_llm.py`](solution/pipeline/04_benchmark_llm.py),
logs brutos em [`process-log/benchmark-llm/`](process-log/benchmark-llm/))

| Abordagem | Acerto | Tokens por ticket |
|---|---|---|
| **Classificador linear (o do app)** | **85,9%** | 0 |
| Gemini 3.5 Flash-Lite, só os nomes das filas | 42–44% | 48 |
| + descrição de cada fila | 58–59% | 53 |
| + 24 exemplos rotulados (few-shot) | 62–64% | 89 |

As faixas vêm de duas execuções com temperatura 0 (o LLM não é determinístico). Todas as diferenças para o linear têm
McNemar p < 0,001. A perda se concentra nas **filas da casa**: Hardware 47% contra 89%, Miscellaneous 50% contra 76%, HR
Support 64% contra 87%. Nas filas de nome autoexplicativo (Access, Storage, Internal Project), o LLM com exemplos fica
perto do linear. Conclusão: classificar é trabalho do modelo treinado com os rótulos da casa; o LLM entra na tradução e
no rascunho, testados de ponta a ponta no app.

Na auditoria de rótulos, o Gemini foi uma checagem independente: nos 15 casos em que a IA julgou o rótulo errado, ele
(sem ver rótulo nem previsão) **nunca** escolheu o rótulo e ficou com a fila do modelo em 10.

**6. ROI** (premissas editáveis no simulador: 3 min de triagem manual, 1 min assistida, 15 min de retrabalho por erro,
R$ 40/h). O volume decide o resultado, e o CSV não o informa: com **2.500 tickets/mês** (30 mil/ano do brief), ~91 h/mês
liberadas, ~R$ 44 mil/ano e 42 tickets/mês na fila errada; com o **proxy do CSV** (8.469 registros ÷ 24 meses de datas de
compra ≈ 353/mês, também premissa), ~13 h/mês e ~R$ 6 mil/ano. Nas automações que o CSV sozinho sustenta, o ROI de 12
meses é negativo nos cenários conservador e provável e positivo só no otimista; o provável se paga a partir de ~1.000
tickets/mês ([revisão, Etapa 3](solution/app/revisao.html)). O ganho provável maior é o tempo de espera na fila de
triagem, que estes dados não permitem medir.

### Recomendações (em ordem)

1. **Instrumentar antes de otimizar (semana 1).** Registrar eventos com horário e responsável (criação, 1ª resposta,
   cada transferência, reabertura, resolução) e a taxa de resposta do CSAT. Sem isso, nenhum diagnóstico de tempo é
   possível, e o detector já está pronto para rodar.
2. **Triagem em modo sombra (semanas 1–2):** o modelo sugere e as pessoas roteiam como hoje. Avança se a faixa
   automática acertar ≥ 97% nos tickets reais.
3. **Roteamento automático nas filas fortes (semanas 3–4), se a operação tiver filas como as da base de TI:** Purchase,
   Storage, Internal Project e Access (precisão de 89% a 95%), com a faixa assistida em todas. Com dados como os do CSV (sem coluna de
   fila e sem rótulo confiável), a triagem segue humana até existirem rótulos novos.
4. **Arrumar a taxonomia:** HR Support absorve pedido vazio e pedido de acesso, e Hardware é o ralo dos erros. As
   correções dos atendentes no modo sombra viram os novos rótulos.
5. **LLM onde ele agrega:** traduzir tickets em português e redigir rascunhos que o atendente aprova. A métrica é a taxa
   de edição dos rascunhos.
6. **Verificar antes de rotear (próxima evolução):** na auditoria de rótulos, boa parte dos casos ambíguos só se resolve
   consultando outro sistema (conta bloqueada, chamado aberto do equipamento, pedido de compra existente). A proposta é
   um agente com acesso **só de leitura** a esses sistemas, que verifica antes de rotear e nunca executa nada. Entra no
   modo sombra, e a métrica é quantos ambíguos passam a ser resolvidos com verificação.

### O que NÃO automatizar

- **Temas sensíveis** (1,8%: maternidade, salário, desligamento): dado pessoal sensível e conversa que pede empatia. O
  filtro prefere errar para o lado humano.
- **Confiança abaixo de 48%** (5,9%): a 1ª sugestão acerta só 45%.
- **Texto fora do padrão de treino:** um ticket em português saía como "Administrative rights" com **100% de
  confiança**. Hoje, se o modelo reconhece menos de 50% das palavras, o ticket vai para uma pessoa ou é traduzido antes.
- **Conceder acesso ou direito de administrador:** a IA roteia, a pessoa aprova.
- **Reclamação, cancelamento e reembolso:** a IA redige, a pessoa envia. No CSV, pelo rótulo, reembolso é 26,1% e
  cancelamento 24,5% dos tickets (revisão, 2.2); como o texto não confirma o rótulo, a regra é de política.

### Limitações

- **Os tempos e o CSAT do CSV não são utilizáveis** (e o CSV não informa o volume), então o ROI depende de premissas
  (editáveis no simulador e na revisão) e não de medição.
- **O Dataset 2 é de outra operação** (TI interna, texto pré-processado, em inglês) e tem rótulos ruidosos. A política
  precisa ser recalibrada com os tickets reais no modo sombra.
- **O sinal de urgência é uma heurística não validada:** não existe prioridade real confiável nos dados.
- **Português depende do LLM** (tradução antes do classificador). Um modelo treinado com tickets em português seria o
  passo seguinte.
- **O limite de uso da função do Gemini é por instância** (melhor esforço). Em produção, seria preciso um gateway com cota.
- **O chat é uma demonstração:** o protocolo e o link do portal são fictícios, a conversa não é gravada e a escolha de fila
  no modo assistido não volta para o treino. As regras de risco são listas de palavras (preferem pegar demais).
- **O benchmark de LLM usou o Flash-Lite.** Os modelos maiores (`gemini-3.5-flash`, `3.6-flash`, `flash-latest`) estavam
  indisponíveis por cota ou demanda (429/503) na hora do teste. Um modelo maior pode reduzir a diferença, e o script já
  tenta rodá-los sozinho.

---

## Process Log — Como usei IA

> **Process log principal:** [`PROCESS_LOG.md`](PROCESS_LOG.md) (iterações, verificações e o que eu decidi). O log técnico,
> com os 38 erros da IA e como cada um foi pego, está em [`process-log/README.md`](process-log/README.md). A conversa
> inteira com o Claude Code está em [`process-log/chat-export/`](process-log/chat-export/).

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| Claude Code (Claude Opus) | Agente principal: exploração dos dados, testes estatísticos, pipeline em Python, web app, revisão visual |
| Gemini | Dentro do produto: tradução e rascunho de resposta. No benchmark: LLM × classificador linear |
| Edge headless | Capturas de tela da página inteira para revisar o visual (o painel do navegador estava oculto) |
| Claude Chat (segunda opinião) | Análise independente do mesmo CSV; cada afirmação dele foi recalculada por script |

### Workflow

1. Li o desafio com a IA e escolhi o 002 com uma **hipótese a verificar** (Dataset 1 sintético) antes de ter os dados.
2. **Tentei derrubar a hipótese primeiro.** Ela sobreviveu a 9 testes, e isso definiu a entrega.
3. Decidi abrir com a auditoria, usar o Gemini e publicar um web app (decisões minhas, registradas no log).
4. Pipeline em 6 scripts (o 5º, `05_revisao_csv.py`, refaz a análise usando só o CSV e alimenta `revisao.html`; o 6º
   recalcula as afirmações da segunda opinião); cada afirmação da entrega sai de um número calculado, não digitado.
5. Protótipo com o mesmo modelo, com paridade Python × navegador verificada em 308 textos.
6. Revisão visual por captura de tela, que pegou erros de conteúdo, não só de layout.
7. Auditoria de rótulos: a IA deu o primeiro veredito em 40 casos; revisei os 40 e concordei em todos (coluna
   `veredito_pedro`).
8. Chat de atendimento: a política é uma função pura testada em 13 cenários, e a tela foi testada no navegador com o
   Gemini ativo (7 cenários, aprovação, passagem para uma pessoa, HTML escapado, 375 px).
9. Validação cruzada com o Claude Chat, conferida número a número.

### Onde a IA errou, e como a verificação pegou (seleção; lista completa no log)

- **Afirmou mais do que os dados sustentam:** "todos os campos são uniformes" (gênero não é, p = 0,007); o histograma
  do tempo de resolução descrito como "plano" (é um triângulo). E a segunda explicação, "diferença de uniformes na janela
  de 27 h", foi rejeitada pelo teste KS. A versão final foi medida.
- **Validação com defeito:** a primeira curva de poder do detector dizia que um gargalo de +12 h nunca era detectado.
  O problema era a resolução da permutação (500 sorteios) contra a correção de 149 testes. Troquei por Welch + BH.
- **Regras com falso positivo:** a regex de tema sensível pegava "discipline" 2.273 vezes (no dataset, é cargo).
- **Métrica boa, comportamento ruim:** 92,7% de acerto nos pedidos vazios era o modelo aprendendo um vício do rótulo.
- **Bug de segurança pego no teste:** texto em português saía com 100% de confiança e era roteado sozinho. Criei a
  regra de cobertura de vocabulário.

### O que eu adicionei que a IA sozinha não faria

- **A escolha do desafio pelo diferencial.** Perguntei à IA onde dava para fazer algo diferente de forma eficiente; ela
  levantou a hipótese do dataset sintético e eu decidi apostar no 002.
- **Abrir a entrega com a auditoria**, assumindo o risco de dizer ao avaliador que os dados não sustentam o diagnóstico,
  e compensar com ferramentas validadas em vez de só apontar o problema.
- **Um web app publicado em vez de Streamlit**, para o avaliador abrir um link e usar em 30 segundos, com o Gemini
  (chave minha, fora do chat e do git) só onde agrega.
- **O chat como diferencial**, pela minha experiência com agentes de atendimento.
- **Uma segunda opinião do Claude Chat** sobre o mesmo CSV, que trouxe dois pontos que a análise principal não tinha.
- **A revisão dos 40 casos da auditoria de rótulos.** Concordei com o veredito da IA em todos. O que a revisão me
  mostrou foi outra coisa: boa parte dos casos ambíguos não se resolve lendo o ticket de novo, e sim consultando outro
  sistema (se a conta está bloqueada, se o equipamento tem chamado, se já existe pedido de compra). Por isso a próxima
  evolução que proponho é um agente com acesso só de leitura a esses sistemas, que verifica antes de rotear e nunca
  executa nada. Ele entra no modo sombra, medindo quantos ambíguos passam a ser resolvidos com verificação.
- **A TRIA como base.** A TRIA, o assistente de recrutamento que construí, já triou mais de 10 mil candidatos em
  operação real, dentro do WhatsApp: a conversa é a triagem, as perguntas seguem os critérios da vaga definidos pelo RH,
  e o recrutador recebe o resultado já filtrado, no sistema que já usa ([portfólio](https://pedro-polido.vercel.app/)). A proposta segue esse
  desenho: a IA atende no canal onde o cliente já está, confirma o recebimento, pede o que falta e entrega o ticket
  organizado na fila certa, e a pessoa decide onde há julgamento (tema sensível, reembolso, perda de dados). O uso do
  LLM segue o mesmo critério que defendo no portfólio: modelo determinístico primeiro, LLM só onde ele agrega.

---

## Como rodar

```bash
# 1. Dados: baixe os dois CSVs do Kaggle para ai-master-challenge/datasets/
#    customer_support_tickets.csv · all_tickets_processed_improved_v3.csv
python -m venv .venv && .venv/Scripts/pip install -r submissions/pedro-polido/solution/pipeline/requirements.txt
cd submissions/pedro-polido/solution/pipeline
python 01_auditoria_dataset1.py && python 02_diagnostico_gargalos.py && python 03_triagem_dataset2.py
python 04_benchmark_llm.py        # opcional, requer GEMINI_API_KEY no .env da raiz
python 05_revisao_csv.py          # revisão usando só o CSV (página revisao.html)
python 06_validacao_cruzada.py    # recalcula as afirmações da segunda opinião

# 2. Protótipo (Node 18+). Sem dependências npm.
cd ../app && node tests/parity.mjs && node tests/chat.mjs && node tests/roi.mjs
node dev-server.mjs               # http://localhost:5173 (chat em /chat.html)
```

Os JSONs gerados pelo pipeline já estão versionados em `solution/app/data/`, então o protótipo roda sem precisar
reprocessar nada. Para as funções do Gemini, defina `GEMINI_API_KEY` (e opcionalmente `GEMINI_MODEL`) no `.env` local
ou nas variáveis de ambiente da Vercel.

## Evidências

- [x] Git history: um commit por etapa, com o motivo das correções
- [x] Narrativa escrita: [`PROCESS_LOG.md`](PROCESS_LOG.md) e o log técnico [`process-log/README.md`](process-log/README.md)
- [x] Revisão humana da auditoria de rótulos: 40 de 40 casos, coluna `veredito_pedro` em
  [`process-log/auditoria-rotulos/`](process-log/auditoria-rotulos/)
- [x] Screenshots: [`process-log/screenshots/`](process-log/screenshots/) (07 a 09: chat de atendimento)
- [x] Validação cruzada: texto da segunda opinião e verificação item a item em
  [`process-log/validacao-cruzada/`](process-log/validacao-cruzada/)
- [x] Chat export da sessão com o Claude Code, revisado e sem dados pessoais, com 9 prints:
  [`process-log/chat-export/`](process-log/chat-export/)
- [x] Prints da conversa com o Claude Chat: [`process-log/validacao-cruzada/prints/`](process-log/validacao-cruzada/prints/)
  e [a proposta do agente de verificação](process-log/auditoria-rotulos/claude-chat-agente-de-verificacao.png)
- [x] Prints da minha leitura dos dois datasets no Excel: [`process-log/analise-manual/`](process-log/analise-manual/)

---

_Submissão enviada em: 25/09/2026_
