# Submissão — Pedro Pólido — Challenge 002

## Sobre mim

- **Nome:** Pedro Henrique Pólido Martins
- **LinkedIn:** [linkedin.com/in/pedro-pólido](https://www.linkedin.com/in/pedro-p%C3%B3lido)
- **Challenge escolhido:** 002 — Redesign de Suporte

**Protótipo no ar:** _URL_DO_DEPLOY_ · **Rodar local:** [instruções](#como-rodar)

---

## Executive Summary

O dataset de métricas de suporte é **sintético**, e dá para provar: 49,3% dos tickets fechados foram "resolvidos antes
da primeira resposta", 100% das descrições têm variáveis de template sem preencher, e um modelo com todas as colunas
prevê a nota de satisfação no nível do chute (20,9%). Qualquer gargalo ou fator de satisfação tirado dali é ruído, e é
exatamente isso que uma IA entrega quando recebe o brief sozinha. Por isso entreguei três coisas:

1. um **detector de gargalos validado**, que não inventa padrão (0 gargalos nos dados atuais) e encontra quando existe
   (+3 h num segmento canal × prioridade é detectado em 82% das simulações);
2. a **automação medida onde o texto é real** (47.837 tickets de TI): 60% dos tickets roteados sem humano com 97,2% de
   acerto, 32% com 2 sugestões para o atendente, 8% sempre humanos;
3. um **protótipo rodando** com essa política, o simulador de ROI e a triagem ao vivo.

**Recomendação principal:** instrumentar o suporte para medir tempo de verdade e começar pela triagem, em modo sombra.
Com premissas conservadoras, são ~90 h/mês de triagem liberadas.

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

Princípio em todas as etapas: tentar derrubar cada achado antes de reportá-lo. Os limiares da política foram escolhidos em
validação cruzada **no treino**, e o conjunto de teste (9.568 tickets) só foi usado para medir.

### Resultados

**1. O Dataset 1 não sobrevive à auditoria** (9 verificações reproduzíveis)

| Verificação | Resultado |
|---|---|
| Linhas no arquivo | 8.469 (o brief fala em ~30.000) |
| Descrições com `{product_purchased}` sem preencher | 100% |
| Tickets "resolvidos antes da 1ª resposta" | 49,3%: a diferença é um triângulo simétrico em zero, a assinatura de dois horários sorteados de forma independente |
| Janela de todas as respostas e resoluções | 27 horas, para compras de 2020 a 2021 |
| Resoluções que descrevem alguma ação técnica | 0 de 2.769 (são frases aleatórias do Faker) |
| Tipo do ticket × assunto | independentes (p = 0,98) |
| Texto do ticket × assunto | independentes (p = 0,91) |
| Prever a nota de satisfação com todas as variáveis | 20,9% de acerto = chutar a nota mais comum |

O que uma análise ingênua reportaria, e o teste que derruba: a "pior combinação" (Email × Medium × Product inquiry,
+3,4 h) aparece com os tempos embaralhados em 78% das simulações.

**2. Detector de gargalos:** 149 segmentos testados com correção para comparações múltiplas. Resultado: **0 gargalos**
de tempo e 0 de satisfação. Em ruído puro, 8% das rodadas têm algum alarme falso; a análise por "pior média" erra em
100%. Com um mês de volume, ele detecta +2 h num canal inteiro (92%) e +3 h em canal × prioridade (82%).

**3. Onde o tempo se perde, no texto real** (Dataset 2)

- **17% dos tickets chegam como cadeia de e-mails** (30% em Administrative rights, 1% em Purchase). O modelo acerta igual
  com 1 ou com várias mensagens, então ler a cadeia deixa de ser trabalho humano.
- **Hardware é o "ralo":** recebe 28% do volume, mas 38% dos tickets mal roteados.
- **Vício de rótulo:** 61% dos pedidos sem conteúdo ("access hello please provide kind regards") estão rotulados como
  HR Support. O modelo aprendeu o vício e "acerta" 93% deles. Na política, pedido vazio nunca é roteado.
- **Auditoria de rótulos:** dos 40 "erros" com confiança ≥ 90% revisados um a um, **15 são erros do rótulo**, 13 do
  modelo e 12 ambíguos. O acerto real da faixa automática é maior que o medido.

**4. Classificador e política** (TF-IDF + regressão logística, 85,7% de acerto, 96,1% com a fila certa entre as 2
primeiras, calibrado: ECE 0,012)

| Faixa | Regra | Volume | Acerto |
|---|---|---|---|
| Roteamento automático | confiança ≥ 88,5% | 59,9% | 97,2% |
| Assistido (2 sugestões) | 48% a 88,5% | 31,8% | 93,5% (fila certa entre as 2) |
| Triagem humana | < 48%, tema sensível, ou texto fora do padrão | 7,7% | — |
| Pedir detalhes | pedido sem conteúdo | 0,6% | — |

**5. LLM:** _RESULTADO_DO_BENCHMARK_

**6. ROI** (premissas editáveis no simulador: 2.500 tickets/mês, 3 min de triagem manual, 1 min assistida, 15 min de
retrabalho por erro, R$ 40/h): **~91 h/mês liberadas, ~R$ 44 mil/ano, 42 tickets/mês na fila errada**. É um ganho
modesto em reais. O ganho provável maior é o tempo de espera na fila de triagem, que estes dados não permitem medir.

### Recomendações (em ordem)

1. **Instrumentar antes de otimizar (semana 1).** Registrar eventos com horário e responsável (criação, 1ª resposta,
   cada transferência, reabertura, resolução) e a taxa de resposta do CSAT. Sem isso, nenhum diagnóstico de tempo é
   possível, e o detector já está pronto para rodar.
2. **Triagem em modo sombra (semanas 1–2):** o modelo sugere e as pessoas roteiam como hoje. Avança se a faixa
   automática acertar ≥ 97% nos tickets reais.
3. **Roteamento automático nas filas fortes (semanas 3–4):** Purchase, Storage e Access (precisão de 89% a 95%), com a
   faixa assistida em todas.
4. **Arrumar a taxonomia:** HR Support absorve pedido vazio e pedido de acesso, e Hardware é o ralo dos erros. As
   correções dos atendentes no modo sombra viram os novos rótulos.
5. **LLM onde ele agrega:** traduzir tickets em português e redigir rascunhos que o atendente aprova. A métrica é a taxa
   de edição dos rascunhos.

### O que NÃO automatizar

- **Temas sensíveis** (1,8%: maternidade, salário, desligamento): dado pessoal sensível e conversa que pede empatia. O
  filtro prefere errar para o lado humano.
- **Confiança abaixo de 48%** (5,9%): a 1ª sugestão acerta só 45%.
- **Texto fora do padrão de treino:** um ticket em português saía como "Administrative rights" com **100% de
  confiança**. Hoje, se o modelo reconhece menos de 50% das palavras, o ticket vai para uma pessoa ou é traduzido antes.
- **Conceder acesso ou direito de administrador:** a IA roteia, a pessoa aprova.
- **Reclamação, cancelamento e reembolso:** a IA redige, a pessoa envia. Como esses dados são sintéticos, é regra de
  política, não número.

### Limitações

- **Os tempos e o CSAT são sintéticos**, então o ROI depende de premissas (editáveis no simulador) e não de medição.
- **O Dataset 2 é de outra operação** (TI interna, texto pré-processado, em inglês) e tem rótulos ruidosos. A política
  precisa ser recalibrada com os tickets reais no modo sombra.
- **O sinal de urgência é uma heurística não validada:** não existe prioridade real confiável nos dados.
- **Português depende do LLM** (tradução antes do classificador). Um modelo treinado com tickets em português seria o
  passo seguinte.
- **O limite de uso da função do Gemini é por instância** (melhor esforço). Em produção, seria preciso um gateway com cota.

---

## Process Log — Como usei IA

> O log completo, com a linha do tempo, as decisões e os erros da IA, está em [`process-log/README.md`](process-log/README.md).

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| Claude Code (Claude Opus) | Agente principal: exploração dos dados, testes estatísticos, pipeline em Python, web app, revisão visual |
| Gemini | Dentro do produto: tradução e rascunho de resposta. No benchmark: LLM × classificador linear |
| Edge headless | Capturas de tela da página inteira para revisar o visual (o painel do navegador estava oculto) |

### Workflow

1. Li o desafio com a IA e escolhi o 002 com uma **hipótese a verificar** (Dataset 1 sintético) antes de ter os dados.
2. **Tentei derrubar a hipótese primeiro.** Ela sobreviveu a 9 testes, e isso definiu a entrega.
3. Decidi abrir com a auditoria, usar o Gemini e publicar um web app (decisões minhas, registradas no log).
4. Pipeline em 4 scripts; cada afirmação da entrega sai de um número calculado, não digitado.
5. Protótipo com o mesmo modelo, com paridade Python × navegador verificada em 308 textos.
6. Revisão visual por captura de tela, que pegou erros de conteúdo, não só de layout.
7. Auditoria de rótulos: a IA deu o primeiro veredito em 40 casos; a revisão humana está na coluna `veredito_pedro`.

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
- _[PEDRO: resultado da sua revisão da auditoria de rótulos: em quantos casos você discordou do veredito da IA e por quê]_
- _[PEDRO: o que a sua experiência operando triagem em produção (Tria) mudou na proposta, com as suas palavras]_

---

## Como rodar

```bash
# 1. Dados: baixe os dois CSVs do Kaggle para ai-master-challenge/datasets/
#    customer_support_tickets.csv · all_tickets_processed_improved_v3.csv
python -m venv .venv && .venv/Scripts/pip install -r submissions/pedro-polido/solution/pipeline/requirements.txt
cd submissions/pedro-polido/solution/pipeline
python 01_auditoria_dataset1.py && python 02_diagnostico_gargalos.py && python 03_triagem_dataset2.py
python 04_benchmark_llm.py        # opcional, requer GEMINI_API_KEY no .env da raiz

# 2. Protótipo (Node 18+). Sem dependências npm.
cd ../app && node tests/parity.mjs && node dev-server.mjs   # http://localhost:5173
```

Os JSONs gerados pelo pipeline já estão versionados em `solution/app/data/`, então o protótipo roda sem precisar
reprocessar nada. Para as funções do Gemini, defina `GEMINI_API_KEY` (e opcionalmente `GEMINI_MODEL`) no `.env` local
ou nas variáveis de ambiente da Vercel.

## Evidências

- [x] Git history: um commit por etapa, com o motivo das correções
- [x] Narrativa escrita: [`process-log/README.md`](process-log/README.md)
- [x] Revisão humana da auditoria de rótulos: [`process-log/auditoria-rotulos/`](process-log/auditoria-rotulos/)
- [x] Screenshots: [`process-log/screenshots/`](process-log/screenshots/)
- [x] Chat export da sessão com o Claude Code: [`process-log/chat-export/`](process-log/chat-export/)

---

_Submissão enviada em: DATA_DO_PR_
