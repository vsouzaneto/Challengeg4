---
title: Implementar arquitetura de resposta executiva ao CEO
---

## Initial User Prompt

registre tudo isos que tratamos e vamos seguir com a arquitetura A que satisfaz a pergunta do CEO.

# Description

Entregar ao CEO uma resposta verificável à pergunta: “Estamos perdendo clientes e não sei por quê. Os números mostram que o churn subiu, mas o time de CS diz que a satisfação está ok. O time de produto diz que o uso da plataforma cresceu. Algo não bate. Preciso de alguém que olhe pra isso com olhos frescos e me diga o que está acontecendo de verdade.”

A arquitetura A aprovada apresenta a resposta primeiro e organiza a evidência em cinco blocos: o que mudou; onde a perda aparece; mecanismo sustentado, se houver; desconhecidos e limites; ações justificáveis. O valor central é esclarecer a aparente contradição e orientar decisões proporcionais à evidência. Qualidade e utilidade do conteúdo têm precedência sobre UI, integrações e LLM.

O diagnóstico deve preservar fatos descritivos úteis mesmo quando nenhuma hipótese explicativa passa pelos critérios de sustentação. A ausência de causa comprovada não impede responder quanto o churn mudou, qual exposição econômica foi observada e por que médias de satisfação e uso não representam necessariamente os clientes perdidos. Mecanismo sustentado continua sendo interpretação observacional; motivos declarados no cancelamento não equivalem a causas demonstradas.

**Scope Included:** resposta executiva comum ao relatório e dashboard existentes; comparação histórica com populações e denominadores explícitos; recortes de clientes/perdas; confronto das alegações de CS e Produto; classificação das afirmações pela escada de evidências; limites de qualidade, cronologia e cobertura; ações de validação ou intervenção compatíveis com a evidência; rastreabilidade e reprodução dos resultados.

**Scope Excluded:** redesenho visual amplo; novas integrações, APIs pagas ou geração via LLM; novo modelo preditivo como pré-requisito da resposta; prova causal inexistente nos dados; contato com clientes ou execução automática de intervenções; publicação/deploy ou mudanças nos CSVs brutos. Planejar esta feature não implementa código.

**User Scenarios:**

1. O CEO abre a entrega e entende a mudança observada, os recortes relevantes, os limites e a próxima decisão sem começar pela metodologia ou pelo status do modelo.
2. CS e Produto confrontam as alegações agregadas com cobertura e coortes; uma média geral crescente pode coexistir com deterioração entre futuros churners sem provar o mecanismo responsável.
3. Um analista inspeciona cada afirmação, reproduz o cálculo e distingue fato, mecanismo sustentado, hipótese plausível e afirmação rejeitada.
4. Todas as hipóteses explicativas ficam inconclusivas: a resposta conserva fatos e propõe validações delimitadas, sem inventar causa, fila acionável ou recuperação financeira.
5. Dados ausentes, cronologia inconsistente, denominador nulo ou artefatos inválidos impedem uma conclusão: a entrega exibe a limitação específica e evita apresentar zero, causalidade ou números desatualizados como resposta válida.

## Acceptance Criteria

**Checklist:**

Todas as perguntas são verificáveis com resposta sim/não; ausência da evidência exigida corresponde a não.

| ID | Question | Category | Importance |
|---|---|---|---|
| CK-1 | Relatório e dashboard abrem com resposta direta ao CEO e apresentam, nessa ordem, o que mudou, onde, mecanismo sustentado ou ausência dele, desconhecidos/limites e ações, antes do detalhamento metodológico? | principle | essential |
| CK-2 | A alegação “churn subiu” é calculada por mês e comparação de períodos, identifica clientes/eventos, população em risco, numerador, denominador, ponderação, calendário, exclusões e incerteza, sem confundir média mensal com probabilidade semestral? | hard_rule | essential |
| CK-3 | A exposição econômica informa moeda, período e regra de deduplicação/agregação, distinguindo MRR perdido observado, MRR exposto e eventual cenário de recuperação não estimado causalmente? | hard_rule | essential |
| CK-4 | A resposta “onde” compara segmentos elegíveis por volume, taxa e exposição financeira, declara base de comparação, amostra e incerteza, e evita chamar maior volume ou RR próximo de um de concentração de risco demonstrada? | hard_rule | essential |
| CK-5 | As alegações de satisfação e uso são confrontadas no agregado e nas coortes pertinentes com período, unidade, cobertura e exclusões, distinguindo satisfação de respondentes da base e leitura retrospectiva de seleção prospectiva? | hard_rule | essential |
| CK-6 | Cada afirmação material tem ID rastreável, fonte/cálculo, período, limitação e classificação explícita como fato confirmado, mecanismo sustentado, hipótese plausível ou afirmação rejeitada, com inconclusão preservada quando aplicável? | hard_rule | essential |
| CK-7 | O bloco de mecanismo exige temporalidade, comparação adequada, estabilidade observed/strict e corroboração pertinente, distingue motivos terminais de mecanismos e permite declarar que nenhum mecanismo foi suficientemente sustentado? | hard_rule | essential |
| CK-8 | Ausência de dados, cobertura insuficiente, baixa potência, intervalo amplo, falha de modelo e cronologia contraditória geram estados e explicações específicos, sem virar zero, efeito nulo ou refutação automática? | hard_rule | essential |
| CK-9 | Cada ação proposta liga-se a uma evidência ou lacuna identificada, nomeia responsável por função, prazo, população, métrica e condição de avançar/parar, mantendo validação separada de intervenção e sem prometer receita recuperável? | principle | essential |
| CK-10 | Relatório, dashboard, CSVs e manifesto apresentam a mesma conclusão, valores, períodos e IDs a partir da mesma execução, inclusive quando todos os mecanismos são inconclusivos e a fila acionável está vazia? | hard_rule | essential |
| CK-11 | Os cálculos novos ou alterados têm regressões determinísticas, casos de fronteira e comparação com os artefatos regenerados, preservando os checksums dos dados brutos e os gates existentes? | hard_rule | essential |
| CK-12 | A explicação executiva usa termos compreensíveis, mantém detalhe estatístico depois da resposta e permite ao leitor distinguir o que se sabe, o que falta e qual ação fazer em seguida? | principle | important |
| HR-1 | A entrega evita linguagem de causalidade comprovada a partir de associação, significância, motivos declarados, importância preditiva ou reprovação de um modelo? | hard_rule | pitfall |
| HR-2 | As alterações respeitam o escopo aprovado, preservam trabalho paralelo e dados originais e não acionam APIs pagas, contato externo, deploy ou gates proibidos no Mac sem autorização aplicável? | hard_rule | essential |
| HR-3 | Números de referência são confrontados com fontes e definições, com divergências registradas, sem codificar números esperados para forçar o resultado nem generalizar deterioração de uma coorte à base inteira? | hard_rule | pitfall |

**Regular Checks:**

Comandos descobertos no `Makefile`, `pyproject.toml` e testes atuais; executar na raiz da solução com Python 3.12 e dependências fixadas. O `make check` é o preflight canônico; os comandos direcionados abaixo ajudam a localizar falhas e não o substituem. Suíte completa/preflight pesado seguem o ambiente autorizado e `codespace-manager`; não executar no Mac sem autorização. Esta etapa de planejamento apenas especifica os checks.

- [ ] `.venv/bin/python -m pytest -q tests/test_diagnosis.py tests/test_panel.py` — conferir denominação, recortes, temporalidade e regressões analíticas; CK-2, CK-4–CK-8, CK-11, HR-1, HR-3.
- [ ] `.venv/bin/python -m pytest -q tests/test_publish.py tests/test_app.py` — conferir resposta publicada, consistência, estados vazios/erro e dashboard; CK-1, CK-3, CK-6, CK-8–CK-12.
- [ ] `make reproduce` — roda `make test` e regenera os artefatos canônicos depois de mudanças aprovadas; conferir manifesto, valores e CSVs, sem editar resultados manualmente; CK-2–CK-11, HR-3.
- [ ] `make check` — Ruff, formatação, pytest, reprodução temporária e comparação de artefatos; requisito final de código/artefatos da implementação; CK-10, CK-11, HR-2.
- [ ] `make app` — inspeção da primeira tela e dos cinco blocos com os artefatos validados; revisão manual da clareza, ações e limites em relatório/dashboard; CK-1, CK-9, CK-12, HR-1. Aplicativo rodando ou HTTP 200 isolados não comprovam conteúdo renderizado.

**Rubric:**

| Criterion | Weight |
|---|---|
| Resposta executiva útil | 0.30 |
| Precisão e rastreabilidade quantitativa | 0.25 |
| Disciplina da escada de evidências | 0.25 |
| Consistência e reprodução da entrega | 0.15 |
| Project Guidelines Alignment | 0.05 |

**Rubric Score Definitions:**

### Resposta executiva útil

Avalia se a resposta esclarece a divergência e conduz a decisão proporcional à evidência. Abrange CK-1, CK-9 e CK-12; a qualidade da UI não compensa conteúdo omisso.

Anchors:

- `score_2`:
  ```text
  Ação: validar a queda de uso da coorte antes de intervir. Responsável: não definido. Prazo: 7 dias. Métrica: proporção de contas cujo sinal foi confirmado. Avançar: somente com evidência corroborada; caso contrário, revisar a hipótese.
  ```
- `score_4`:
  ```text
  Ação: validar a queda de uso da coorte antes de intervir. Responsável: Head de Produto. Prazo: 7 dias. Métrica: proporção de contas cujo sinal foi confirmado. Avançar: somente com evidência corroborada; caso contrário, revisar a hipótese.
  ```
- `contrast`: presença de responsável identificável para executar a ação.

### Precisão e rastreabilidade quantitativa

Avalia a interpretação de churn, perda econômica, segmentos, cobertura e coortes a partir de definições verificáveis. Abrange CK-2–CK-5 e HR-3; números fornecidos no contexto são referências a conferir, não resultados impostos.

Anchors:

- `score_2`:
  ```text
  A satisfação caiu de 4,50 para 3,67 entre junho e novembro de 2024. População: toda a base. Fonte: C-satisfaction-ok, cohort=churn_next_30d; cobertura média de respostas=65,85%.
  ```
- `score_4`:
  ```text
  A satisfação caiu de 4,50 para 3,67 entre junho e novembro de 2024. População: respondentes da coorte churn_next_30d. Fonte: C-satisfaction-ok, cohort=churn_next_30d; cobertura média de respostas=65,85%.
  ```
- `contrast`: identificação correta da população à qual o valor se refere.

### Disciplina da escada de evidências

Avalia a separação entre descrição, explicação observacional, hipótese e refutação, inclusive quando não existe mecanismo sustentado. Abrange CK-6–CK-8 e HR-1.

Anchors:

- `score_2`:
  ```text
  F-commercial-renewal: OR=1,097; IC95%=[0,411; 2,924]. Estado: hipótese rejeitada. O intervalo é amplo e inclui a ausência de associação.
  ```
- `score_4`:
  ```text
  F-commercial-renewal: OR=1,097; IC95%=[0,411; 2,924]. Estado: hipótese inconclusiva. O intervalo é amplo e inclui a ausência de associação.
  ```
- `contrast`: classificação da incerteza como inconclusão em vez de refutação.

### Consistência e reprodução da entrega

Avalia se as superfícies comunicam o mesmo resultado verificável e se mudanças de artefatos são detectadas. Abrange CK-10 e CK-11.

Anchors:

- `score_2`:
  ```text
  Relatório: nenhum mecanismo sustentado. Dashboard: mecanismo comercial sustentado. CSV: todos os mecanismos inconclusivos. Manifesto: execução R1.
  ```
- `score_4`:
  ```text
  Relatório: nenhum mecanismo sustentado. Dashboard: nenhum mecanismo sustentado. CSV: todos os mecanismos inconclusivos. Manifesto: execução R1.
  ```
- `contrast`: coerência do estado exibido pelo dashboard com os artefatos da execução.

### Project Guidelines Alignment

Avalia respeito ao escopo, aos dados, ao ambiente autorizado e à exigência de registrar a validação executada. Abrange HR-2 e CK-11.

Anchors:

- `score_2`:
  ```text
  Dados brutos: preservados. Integrações novas: nenhuma. APIs pagas: acionadas sem autorização. Contato externo: nenhum. Validação: make check no ambiente autorizado.
  ```
- `score_4`:
  ```text
  Dados brutos: preservados. Integrações novas: nenhuma. APIs pagas: não acionadas. Contato externo: nenhum. Validação: make check no ambiente autorizado.
  ```
- `contrast`: respeito à autorização necessária para chamadas pagas.

**Test Strategy:**

**Criticality:** alta para integridade analítica e comunicação executiva, pois uma falsa conclusão pode direcionar ações comerciais incorretas; baixa para infraestrutura, pois a entrega permanece local e somente leitura. Aplicável: cálculos, estados de evidência, publicação e leitura renderizada têm comportamento verificável. Reutilizar pytest, fixtures existentes e Streamlit AppTest; não criar nova infraestrutura de testes.

**Test Matrix:**

| Type | Size | Framework | Dependencies | Gate |
|---|---|---|---|---|
| unit | Casos mínimos calculáveis à mão | pytest | pandas e funções analíticas existentes | Denominadores, períodos, estados e fronteiras corretos |
| integration | Publicação de uma execução e casos de integridade | pytest | Pipeline, CSVs e manifesto locais | Superfícies coerentes e artefatos inválidos recusados |
| ui | Primeira tela e estados de leitura | Streamlit AppTest | Artefatos gerados por fixture | Cinco blocos e ausência de contradição |
| reproducibility | Dataset canônico completo | make check / CLI compare | Python 3.12, dependências fixadas e cinco CSVs | Execuções equivalentes; divergência material falha |
| manual | Leitura executiva e limites de escopo | Revisão humana + make app | Relatório, UI renderizada e evidência dos checks | Resposta compreensível e ações proporcionais |

**Test Cases to Cover:**

#### CK-1: Resposta primeiro

- [ui] A primeira seção responde à pergunta do CEO; os cinco blocos estão presentes na ordem aprovada, tanto com mecanismos sustentados quanto com todos inconclusivos.
- [integration] Relatório mantém a mesma resposta e ordem do dashboard; um modelo rejeitado não substitui a resposta executiva por mensagem genérica de falha.

#### CK-2: Mudança histórica

- [unit] Série pequena com denominadores mensais distintos confirma ponderação pela população em risco, e diferencia média ponderada de média simples e taxa semestral acumulada.
- [unit] Fronteiras de entrada/saída, múltiplas assinaturas/eventos, reativação, mês incompleto e denominador zero obedecem à regra documentada; sem exposição gera indisponível, não zero por conveniência.
- [reproducibility] Conferir referências do contexto: H2/2023 5,93% versus jun–nov/2024 13,83%, razão 2,33 e diferença +7,90 pp; novembro/2024 18,52%. Registrar qualquer divergência e a definição usada. Se publicado, p≈4,55e-9 acompanha teste, pressupostos e tratamento da repetição por conta; não mede causalidade.

#### CK-3: Exposição econômica

- [unit] Dois eventos da mesma conta/assinatura verificam a regra declarada contra dupla contagem; valor ausente não é receita zero.
- [reproducibility] Conferir MRR perdido de aproximadamente US$ 2,006 milhões em jun–nov/2024, distinguindo soma de MRR associado aos cancelamentos de receita acumulada efetivamente não recebida. MRR exposto e recuperação hipotética permanecem separados.

#### CK-4: Onde a perda aparece

- [unit] Segmento de maior tamanho com taxa semelhante não é declarado principal fator de risco; segmento pequeno exibe insuficiência de amostra.
- [reproducibility] Conferir a referência US com RR≈1,075 e identificar seu comparador. Esse RR isolado não comprova concentração relevante nem dispensa volume, intervalo e exposição econômica.

#### CK-5: Aparente contradição

- [unit] Agregado de uso sobe enquanto a coorte de futuros churners cai; ambas as leituras são preservadas e identificadas como retrospectivas. Atribuição a composição só ocorre se houver decomposição/padronização que a sustente.
- [unit] Satisfação geral 3,959→4,021 e satisfação dos respondentes churn_next_30d 4,50→3,667 não produzem a frase “a satisfação de toda a base caiu”. Cobertura de tickets/respondentes não equivale automaticamente a cobertura de contas.
- [manual] Verificar HR-3: números citados como referência são rastreáveis; deterioração, crescimento e “ok” têm recortes e limitações explícitos.

#### CK-6: Classificação das afirmações

- [unit] Exemplos controlados cobrem fato reproduzível, mecanismo observacional corroborado, hipótese plausível inconclusiva e enunciado contradito por evidência; cada estado mantém fonte, período e limitação.
- [integration] Uma afirmação rejeitada contém o enunciado exato e a contraevidência; baixa potência ou modelo recusado não alimentam essa categoria automaticamente. Verificar HR-1.

#### CK-7: Mecanismo sustentado

- [unit] Corroboração fora da janela, vazamento de informação posterior, instabilidade observed/strict ou motivo terminal isolado não promovem hipótese a mecanismo sustentado.
- [integration] Com todos os mecanismos inconclusivos, fatos válidos continuam na abertura, o bloco de mecanismo declara o limite e a fila de intervenção permanece vazia; watchlist continua marcada apenas para validação.

#### CK-8: Limites e falhas

- [unit] Cobrir ausência de respostas, denominador zero, amostra pequena, intervalo amplo e falha de ajuste; cada condição conserva a razão de inconclusão em vez de inferir ausência de efeito.
- [integration] CSV ausente, checksum inválido ou manifesto incompatível impede leitura como análise válida; mensagem indica artefato/causa e reprodução necessária, sem resultado silenciosamente antigo.

#### CK-9: Ações justificáveis

- [manual] Cada proposta contém evidência/lacuna, função responsável, prazo, população, métrica e condição de avançar/parar; todos os mecanismos inconclusivos ainda permitem propor coleta/validação.
- [integration] Nenhuma conta entra na fila acionável só por pertencer a coorte retrospectiva ou watchlist; texto não promete recuperação financeira nem executa contato.

#### CK-10: Uma execução, uma resposta

- [integration] Comparar valores, IDs, períodos, conclusões e limites entre relatório, dashboard e tabelas canônicas; alterar um artefato invalida o conjunto pelo manifesto.
- [ui] Alterar filtro de cronologia preserva a identificação da leitura selecionada; nenhum filtro muda rótulo sem mudar o conteúdo correspondente.

#### CK-11: Regressão e reprodução

- [reproducibility] Regerar e comparar todos os artefatos com o comando canônico, permitindo apenas as variações já previstas pelo comparador, e conferir os checksums dos cinco CSVs de origem.
- [manual] Verificar HR-2: evidência do ambiente autorizado e do commit/diff validado, preservação de trabalho paralelo, ausência de bypass de gates e de ações externas fora do escopo.

#### CK-12: Leitura executiva

- [manual] Ler a abertura sem consultar metodologia: localizar a mudança, a divergência entre médias/coortes, o limite do mecanismo e a próxima ação. Confirmar que significância não é descrita como causalidade (HR-1).

**Definition of Done:**

1. CK-1–CK-12 e HR-1–HR-3 têm evidência verificável; a resposta em cinco blocos informa fatos úteis mesmo sem mecanismo sustentado.
2. Valores finais derivam dos dados e definições publicadas; divergências das referências foram resolvidas ou explicitadas; nenhuma inconclusão foi convertida em refutação ou causalidade.
3. Relatório, dashboard renderizado, tabelas e manifesto concordam; testes de regressão e `make check` passam no ambiente autorizado para o commit/diff entregue.
4. Ações têm responsável, prazo e critério de decisão, dentro do escopo; dados brutos e trabalho paralelo foram preservados; não houve execução externa não autorizada.
5. Alterações, decisões, validações executadas e limitações remanescentes ficam registradas de forma contemporânea no processo do projeto; revisão humana da SPEC antecede implementação, conforme o fluxo autorizado.

## Architecture Overview

**Decisão: arquitetura A, resposta canônica primeiro.** Aplicar a skill local [answer-first-churn](../../../.claude/skills/answer-first-churn/SKILL.md), especialmente a separação entre fato descritivo, mecanismo observacional, hipótese e refutação. A [análise de impacto](../../analysis/analysis-implement-ceo-answer-architecture.md) fundamenta os pontos de integração. Esta seção especifica a implementação futura; não a autoriza antes da revisão humana da SPEC.

O pipeline existente calcula as evidências; `publish.py` constrói uma resposta executiva uma única vez; relatório e dashboard renderizam essa mesma resposta. A resposta não depende da publicação do modelo preditivo nem da existência de mecanismo sustentado. Sem mecanismo, publica os fatos válidos, explicita o que falta e propõe validações delimitadas. Não criar serviço, camada de agentes, módulo analítico paralelo ou dependência nova.

```text
CSV bruto → contratos/QA → painéis e evidências → AnalysisResult
                                                  ↓
                           publish.py: _build_ceo_answer(result)
                                      ↙                   ↘
                              report.md              ceo_answer.json → app.py
                                      ↘                   ↙
                                  manifesto da mesma execução
```

### População, calendário e receita

`config.py` explicita `observation_end=2024-12-31`, série mensal de abril/2023 a novembro/2024, período de referência julho–dezembro/2023 e período recente junho–novembro/2024. São parâmetros versionados no manifesto, não valores de resultado. O fim observável não é inferido da maior data de um evento isolado. As taxas mensais usam `[primeiro dia, primeiro dia do mês seguinte)`, com datas na granularidade original; os labels atuais `(cutoff, cutoff+30 dias]` permanecem identificados como outra medida. Dezembro/2024 é corte de scoring sem label futuro, não um mês com churn futuro igual a zero.

A população principal é `registered_at_start`: contas com cadastro válido em ou antes do primeiro dia do mês e sem primeiro churn terminal válido anterior a esse dia. Inclui trials/contas sem assinatura, que ficam identificados nos recortes; não será chamada de retenção paga. O numerador contém somente primeiros churns válidos dessas mesmas contas dentro do mês. Contas cadastradas depois do começo do mês e seus churns são informados separadamente (`new_accounts`, `entrant_churns`), sem entrar silenciosamente na taxa principal. Um evento no primeiro dia pertence ao mês e a conta integra o denominador se já cadastrada nessa data. Não construir uma segunda população paga nesta feature; MRR e presença de assinatura explicitam a exposição financeira dentro da população declarada.

Uma seleção compartilhada em `panel.py` filtra os eventos **antes** de escolher o primeiro por conta: conta existente, `signup_date` e `churn_date` conhecidas, `churn_date >= signup_date`, data dentro do limite observável e `is_reactivation == False`. Flag de reativação ausente é indeterminada, não terminal por conveniência. Ordenar por `account_id`, `churn_date`, `churn_event_id` resolve empates de forma determinística. Retornar o primeiro registro válido e uma tabela interna de exclusões por evento/razão. `first_terminal_churn` preserva a saída Series de datas, recebe também accounts/limite e delega a essa seleção; painel, histórico, motivos e corroboração usam a mesma seleção. Exemplo obrigatório: evento anterior ao signup seguido de evento válido mantém a conta em risco até o evento válido e usa o motivo deste; não descarta a conta inteira nem revive o evento inválido. Reativação não abre um segundo episódio de risco neste escopo.

`quality.py` também usa essa seleção compartilhada para `accounts_flag_vs_terminal_event` e `subscription_accounts_flag_vs_terminal_event`, eliminando sua seleção independente baseada apenas em reativação. `quality_report.json.label_policy` passa a `first_valid_non_reactivation_event`; o manifesto copia essa política, com o mesmo limite observável. Contagens de problemas brutos, como `events_before_signup`, continuam medindo as linhas originais excluídas. A regressão em `tests/test_quality.py` cobre uma conta com flag de churn e somente evento inválido (há divergência), seguida da inclusão de evento válido (divergência resolvida, data válida escolhida); confirma também flag de reativação ausente excluída e igualdade da política entre QA, painel e manifesto. Contagens canônicas de divergência são regeneradas sob essa regra, sem preservar por conveniência os valores da política antiga.

MRR perdido é a soma, uma vez por conta terminal, de assinaturas distintas ativas no dia anterior ao churn (`start <= dia_anterior < end`, com end aberto). Reutilizar `mrr_lost_at_churn`. A moeda é `USD`; somar MRR associado a cancelamentos em seis meses não equivale a receita acumulada não recebida. Ausência de histórico de assinatura ou valor ativo desconhecido gera MRR desconhecido para aquela conta; histórico conhecido sem assinatura ativa permite zero. Publicar soma conhecida, número de contas com MRR conhecido/desconhecido e estado parcial; não preencher ausências com zero. MRR exposto é o estoque ativo no começo do mês ou no cutoff indicado, deduplicado por assinatura e conta; não somar estoques mensais nem dimensões sobrepostas como se fossem perda adicional. Recuperação financeira permanece `null`, com razão `not_estimated`.

Taxa agregada de período = soma dos churns elegíveis / soma das contas em risco nos meses completos, rotulada **taxa mensal ponderada por exposição conta-mês**. Não equivale à probabilidade semestral. Cada mês permite IC95% de Wilson com `statsmodels.stats.proportion.proportion_confint`, pois a conta aparece uma vez nesse mês. Comparação entre períodos, diferenças, razões e recortes com exposições repetidas usa bootstrap por conta, mantendo todos os meses da conta juntos e o mesmo sorteio nos dois períodos: seed existente 42, 2.000 réplicas, percentis 2,5/97,5. Denominador zero, amostra de menos de duas contas distintas ou menos de 95% de réplicas válidas deixa o intervalo/razão indisponível e registra a causa. Não calcular p-valor tratando conta-mês como independente. Contagens e valores financeiros observados são totais do dataset, com incerteza de cobertura/qualidade explícita, sem IC estatístico inventado.

O bloco “onde” usa o mesmo histórico por dimensão/segmento, além da fotografia existente claramente rotulada. Reutilizar dimensões de `_segment_metrics`; atributos contratuais vêm das assinaturas ativas no começo do mês, com `mixed` e `unknown` explícitos. Comparador histórico de um segmento = **demais contas da mesma dimensão**, disjunto; o RR legado de `segment_metrics.csv` continua identificado como segmento versus toda a base naquele snapshot. Publicar volume, taxa, MRR, base do comparador e intervalo. Só destacar excesso de risco se ambos os lados passam 30 contas distintas/10 churns e o IC da razão fica acima de 1; ordenar volume financeiro separadamente. Maior volume, RR pontual próximo de 1 ou recorte insuficiente não demonstra concentração. Não afirmar que a mudança foi ampla sem os recortes históricos calculados.

### Cronologia e coortes relativas ao churn

`observed` mantém os eventos registrados mesmo quando uso/tickets contradizem o ciclo de vida, mas sempre corta informação posterior ao cutoff. `strict` aplica os filtros atuais: uso em/apos signup e início da assinatura, não posterior ao end registrado; ticket em/apos signup; respostas, encerramento, escalada e satisfação somente quando conhecidos no cutoff. Preservar a convenção atual de `usage_date <= end_date` e a convenção distinta de estoque ativo `cutoff < end_date`, documentando a granularidade diária. Ambas as leituras usam o **mesmo primeiro churn válido** e as mesmas âncoras/populações; observed não reintroduz labels impossíveis. Strict é a leitura executiva principal, observed é a análise de sensibilidade identificada por campos e rótulos.

`build_event_aligned_panel` gera âncoras retrospectivas no primeiro churn válido `t` em junho–novembro/2024 e cutoffs `t−1`, `t−31`, `t−61` dias. A mesma função produz um recorte separado para a janela de desfechos do snapshot diagnóstico, necessário ao gate temporal; não usar meses diferentes como corroboração contemporânea. Se o horizonte dos controles desse recorte exceder a observação disponível, o gate fica indisponível e essa limitação é publicada, sem relaxar a seleção. Reutiliza janelas existentes de 30 dias para medidas não sobrepostas: dias relativos `[-30,-1]`, `[-60,-31]`, `[-90,-61]`. Para sinais já definidos em 90 dias, reutiliza a feature de 90 dias no cutoff `t−1` e rotula essa janela adicional, sem chamar sobreposição de observação independente. Features de casos nunca incluem o dia do churn. Casos precisam estar cadastrados, sem churn anterior e com assinatura ativa no cutoff; exclusões ficam contadas.

Controles são contas elegíveis no mesmo cutoff `t−1`, com observação até `t+29` e sem primeiro churn válido até essa data. Podem churnar depois desse horizonte; não exigir sobrevivência até o fim do dataset. As mesmas contas de cada conjunto de âncora são acompanhadas nas três janelas, conservando ausências quando ainda não há cobertura. A análise é retrospectiva e não alimenta features preditivas, scoring ou seleção de intervenção.

Uma conta pode reaparecer como controle em âncoras distintas ou como caso posterior. Publicar `unique_accounts`, `account_anchor_rows` e `reused_control_accounts`; não apresentar as linhas como pessoas independentes. Por data de âncora, uso é a média por conta coberta em cada coorte. Para satisfação, em cada coorte/âncora/janela, calcular `sum(media_da_conta × respostas_da_conta) / sum(respostas_da_conta)`, usando apenas satisfação conhecida e respostas positivas de tickets encerrados; não usar média simples de médias por conta. Depois, para ambas as coortes, ponderar as médias das âncoras pela quantidade de casos elegíveis naquela data: `sum(media_da_ancora × casos_elegiveis_da_ancora) / sum(casos_elegiveis_da_ancora)`. A comparação usa o mesmo conjunto de âncoras com valor disponível nos dois lados; âncora sem respostas fica nula, com exclusão/cobertura informada, nunca zero. Registrar `weighting=responses_within_anchor;eligible_cases_between_anchors` para satisfação. ICs e diferenças usam reamostragem por conta, preservando todas as participações e recalculando os dois níveis de ponderação em cada réplica. Comparação é com o conjunto em risco contemporâneo, sem afirmar pareamento por plano/tenure ou ausência de confundimento. Diferenças de composição permanecem limitação; só atribuir mudança à composição se uma decomposição/padronização for efetivamente calculada.

Reutilizar `build_account_panel`, `_add_usage_window`, `_add_support_window` e `_add_trends` para os pares conta/cutoff necessários. A construção de linha pode ser extraída dentro de `panel.py` se necessária para evitar produto cartesiano inútil; nenhuma segunda implementação das fórmulas. Labels de âncoras cujo horizonte ultrapasse `observation_end` são nulos independentemente de coincidirem com `SCORING_CUTOFF`.

Para a alegação de Produto, distinguir total de eventos de uso, uso diário por conta com cobertura e proporção de contas cobertas. Para CS, publicar média ponderada por respostas de tickets encerrados, respostas/tickets e contas respondentes/contas elegíveis separadamente. As coortes `overall`, `retained`, `churn_next_30d` de `claim_checks.csv` mantêm seus significados; “retained” significa apenas sem churn no horizonte de 30 dias. A skill proíbe generalizar satisfação dos respondentes à base ou deterioração retrospectiva a todo cliente. “Ok” conserva o limiar descritivo existente, acompanhado de cobertura, e não vira evidência causal.

### Gates e escada de evidência

Os seis candidatos e seus limiares em `CANDIDATES` permanecem. Cada critério registra `pass`, `fail` ou `unavailable`, com razão e referências; não reduzir tudo ao primeiro erro. `fail` significa que o critério de sustentação não passou, não que o mecanismo foi refutado. Acrescentar os resultados separados a `findings.csv`; `failure_reason` legado pode conservar uma razão principal por compatibilidade.

| Gate | Condição necessária para sustentar o mecanismo |
|---|---|
| Temporalidade e comparação | Feature conhecida antes do desfecho, label completamente observado e mesma população/cutoff; coorte relativa pertinente com sinal na direção esperada em strict e observed e comparação contemporânea identificada. Persistência do sinal pré-evento permite sustentação; tendência de agravamento só é afirmada se as janelas a mostrarem. |
| Amostra e cobertura | Preservar pelo menos 30 contas expostas, 10 churns expostos e cobertura da feature de 70% no snapshot. Na comparação relativa, pelo menos 30 casos e 30 controles distintos, cobertura de 70% em cada lado/janela usada. Ausência de observação não é zero. |
| Associação ajustada | Preservar GLM e controles existentes, convergência e estimativas finitas; sinal esperado e IC95% inteiramente do lado esperado de OR=1. Registrar tamanho amostral efetivo, controles e perdas por complete-case. Corrigir os seis testes da família por Holm com statsmodels, alpha=0,05; a correção só pode restringir a aceitação existente. Não tratar controles possivelmente mediadores ou snapshots observacionais como identificação causal. |
| Robustez cronológica | Fits observed/strict disponíveis, mesmo sinal e `abs(beta_strict−beta_observed)/max(abs(beta_observed),1e−9) <= 0,25`, como hoje; diferenças de cobertura e exclusões publicadas. Se uma leitura falha, gate indisponível. |
| Corroboração pertinente | Motivos do primeiro churn válido somente das contas/horizonte do snapshot `(cutoff, cutoff+30 dias]`; pelo menos 10 eventos elegíveis e share do grupo de motivos entre expostos pelo menos 1,25× o share geral nessa janela, com denominadores/unknown explícitos. Reutilizar o mapeamento de motivos existente. Motivo terminal corrobora, nunca substitui a evidência pré-evento. |

O enum fechado de `evidence_level` é `confirmed_fact`, `supported_mechanism`, `plausible_hypothesis` ou `rejected_claim`; não publicar abreviações ou sinônimos. `supported_mechanism` exige todos esses critérios e continua interpretação observacional, sujeita a confundimento e qualidade de origem. `confirmed_fact` é um enunciado descritivo reproduzível no recorte declarado, mesmo quando seus mecanismos falham. `plausible_hypothesis` registra a explicação compatível, os critérios faltantes e o teste discriminante. `rejected_claim` exige o enunciado exato e contraevidência demonstrada, ou rejeita especificamente uma extrapolação indevida (por exemplo, “associação prova causa”), sem declarar o efeito inexistente. Baixa potência, intervalo amplo que inclui 1, falta de cobertura, não convergência ou modelo preditivo recusado produzem inconclusão/indisponibilidade, nunca rejeição automática.

Separar `evidence_level` de `status` e de `confidence`. Atualizar a confiança operacional final para `accepted` somente quando os gates anteriores **e** os critérios acima passam; os demais permanecem `inconclusive`. Isso restringe a fila e não cria nova autorização de contato. `rank_findings` e `_build_queue` continuam operando exclusivamente sobre accepted; nenhum rank de intervenção é dado a hipóteses. O scorecard não usa soma ponderada arbitrária nem MRR para graduar força da evidência. Se vários mecanismos são sustentados sem critério que distinga sua força, declarar empate; se nenhum passa, `selected_mechanism_id=null`, preservando todos os fatos válidos e uma fila vazia.

### Contratos concretos de saída

Notação: `str`, `int`, `float`, `bool`, `date` (ISO `YYYY-MM-DD`); `?` significa nullable. Todos os campos listados são obrigatórios, salvo indicação; JSON usa `null`, CSV campo vazio. Floats válidos são finitos; razões e intervalos não calculáveis não viram NaN/Infinity, zero ou texto numérico. IDs são strings determinísticas construídas da chave natural, nunca da posição da linha. Toda tabela mantém cabeçalhos mesmo vazia.

Campos comuns às quatro tabelas novas: `evidence_id:str` único, `period_start:date`, `period_end:date` inclusivo, `population:str`, `chronology:str` (`strict`, `observed` ou `shared` para labels), `status:str` (`available`, `partial`, `inconclusive`, `unavailable`), `limitation:str`, `source_refs:str` (IDs separados por `|`) e `calculation:str` (função e definição versionada). Nulos nos cálculos exigem causa em `limitation`. Contagens sem observações são zero somente se o universo foi observado e está vazio.

| Artefato / chave natural | Campos específicos e semântica |
|---|---|
| `monthly_churn.csv` / período, população, dimensão, segmento | `period_kind:str` (`month`/`comparison_period`), `dimension:str`, `segment:str`, `at_risk_accounts:int` (soma de exposições nas linhas de período), `unique_accounts:int`, `terminal_churns:int`, `new_accounts:int`, `entrant_churns:int`, `excluded_events:int`, `observation_complete:bool`, `churn_rate:float?`, `rate_unit:str=account_churn/account_month`, `ci_low:float?`, `ci_high:float?`, `ci_level:float=0.95`, `ci_method:str`, `comparator_id:str?`, `comparator_rate:float?`, `relative_risk:float?`, `rr_ci_low:float?`, `rr_ci_high:float?`, `rate_difference:float?` (fração, exibição em pp), `difference_ci_low:float?`, `difference_ci_high:float?`, `mrr_lost:float?`, `mrr_known_accounts:int`, `mrr_unknown_accounts:int`, `mrr_exposed:float?`, `mrr_exposed_as_of:date?`, `currency:str=USD`, `financial_unit:str=monthly_recurring_revenue`. Totais usam `dimension=all, segment=all`; comparador de segmento é complemento, de período recente é período de referência da mesma população/recorte. As referências distinguem esses dois contrastes; quando ambos são necessários, emitir linhas com `comparison_kind:str` (`segment_complement`/`previous_period`/`none`) incluído na chave. Estoque agregado de vários meses fica null, sem somá-lo. |
| `reason_distribution.csv` / período, população, razão | `reason_code:str` (inclui `unknown`), `terminal_accounts:int`, `eligible_events:int` (denominador da janela/população), `excluded_events:int`, `share:float?`, `unit:str=share_of_first_valid_terminal_accounts`, `ci_low:float?`, `ci_high:float?`, `ci_method:str=wilson`, `ci_level:float=0.95`, `comparator_id:str?`, `mrr_lost:float?`, `mrr_known_accounts:int`, `mrr_unknown_accounts:int`, `currency:str=USD`. Publicar distribuição de cancelamentos do período e, separadamente por `population`, eventos da população principal e do horizonte diagnóstico; nunca usar todos os eventos para corroborar o último snapshot. |
| `event_cohort_metrics.csv` / métrica, cronologia, coorte, janela, período de âncoras | `metric:str`, `cohort:str` (`terminal_cases`/`contemporaneous_controls`), `relative_window_start:int`, `relative_window_end:int`, `anchor_period_start:date`, `anchor_period_end:date`, `eligible_accounts:int`, `observed_accounts:int`, `unique_accounts:int`, `account_anchor_rows:int`, `eligible_account_anchors:int`, `observed_account_anchors:int`, `reused_control_accounts:int`, `coverage:float?` (observed_account_anchors/eligible_account_anchors), `coverage_unit:str=covered_account_anchors/eligible_account_anchors`, `response_count:int?`, `ticket_count:int?`, `respondent_accounts:int?`, `value:float?`, `unit:str` (p.ex. `usage_events/account/day`, `satisfaction_points/response`), `weighting:str`, `comparator_id:str?`, `difference:float?`, `ci_low:float?`, `ci_high:float?`, `difference_ci_low:float?`, `difference_ci_high:float?`, `ci_method:str`, `ci_level:float=0.95`. Contas distintas e pares não são intercambiáveis; cobertura de respostas também é informada, sem reaproveitar cobertura de contas. |
| `mechanism_scorecard.csv` / mecanismo | `mechanism_id:str`, `finding_id:str`, `claim:str`, `evidence_level:str?`, `temporal_support:str`, `comparison_support:str`, `sample_support:str`, `association_support:str`, `chronology_support:str`, `cross_table_support:str` (enum de gate), `gate_reasons:str` (objeto JSON com gate→razão), `effect:float?`, `effect_unit:str=adjusted_odds_ratio`, `comparator_id:str`, `ci_low:float?`, `ci_high:float?`, `ci_level:float=0.95`, `ci_method:str`, `p_adjusted:float?`, `observed_coverage:float?`, `strict_coverage:float?`, `counterevidence:str?`, `rejected_statement:str?`, `recommended_validation:str`. Nível null significa nenhuma proposição classificável por dados; `status=unavailable`. Hipótese compatível porém não sustentada mantém `evidence_level=plausible_hypothesis` e `status=inconclusive`. |

`ceo_answer.json` tem `schema_version:int=1`, `analysis_id:str`, `parameters:object`, `headline:str`, `headline_claim_ids:list[str]`, `selected_mechanism_id:str?`, `mechanism_status:str` (`supported`, `tied`, `inconclusive`, `unavailable`), `blocks:list[Block]` e `evidence_refs:dict[str, EvidenceRef]`. `analysis_id` é SHA-256 determinístico dos checksums de entrada, parâmetros e checksums das tabelas/JSONs de evidência já serializados, antes do relatório e da própria resposta; também consta no manifesto. Assim não há autorreferência e o comparador conserva a exceção atual apenas para timestamp/SHA do Git.

`Block` contém `id:str`, `title:str`, `summary:str`, `claims:list[Claim]`, `actions:list[Action]`; ordem exata: `what_changed`, `where`, `strongest_mechanism`, `unknowns`, `next_actions`. Arrays vazios são permitidos, bloco ausente não. `Claim` contém `id:str`, `statement:str`, `evidence_level:str?`, `status:str`, `value:float?`, `unit:str`, `numerator:float?`, `denominator:float?`, `population:str`, `period_start:date`, `period_end:date`, `comparator_id:str?`, `uncertainty:{method:str,level:float?,low:float?,high:float?,reason:str?}`, `evidence_ids:list[str]`, `limitation:str`, `counterevidence:str?`. Comparações podem ter claims próprios para valor inicial/final/diferença, evitando campos numéricos escondidos na prosa.

`EvidenceRef` contém `artifact:str` (nome permitido do manifesto ou fonte bruta com checksum validado), `row_key:dict[str,str|int|bool]`, `columns:list[str]`, `calculation:str`, `source_tables:list[str]`, `period_start:date`, `period_end:date`, `population:str` e `unit:str`. Não aceitar referências vagas a “todas as tabelas”: cada ID resolve para uma linha única e colunas existentes; referências a dados brutos usam PKs, ou filtro de cálculo declarado quando agregado. Comparadores apontam para outra evidência/claim existente, sem ciclos autorreferentes. Claims de limitação referenciam QA/gates/exclusões que a demonstram.

`Action` contém `id:str`, `kind:str` (`data_audit`, `validation`, `intervention_proposal`), `description:str`, `evidence_ids:list[str]`, `owner_role:str`, `deadline_days:int`, `population:str`, `success_metric:str`, `advance_if:str`, `stop_if:str`, `limitation:str`. Toda ação tem evidência ou lacuna rastreável; 7 dias para uma validação delimitada ou 30–90 dias para piloto/instrumentação são prazos propostos, sem execução automática. Intervenção proposta exige mecanismo sustentado e teste prospectivo; nenhuma ação promete receita recuperável.

Exemplo **ilustrativo de formato**, com dados sintéticos que não são resultados esperados nem golden values:

```text
Churn mensal ponderado passou de 2/100 (2%) para 6/100 (6%) nas exposições
observadas dos períodos comparados. MRR associado aos cancelamentos recentes:
US$ 600/mês, com cobertura financeira de 6/6 contas. [C-change, C-mrr]

1. O que mudou — +4 pp; períodos e IC do bootstrap por conta nas evidências.
2. Onde — o maior volume está no segmento A; seu intervalo não demonstra
   excesso de risco em relação às demais contas. [C-where]
3. Mecanismo — nenhum suficientemente sustentado. Queda prévia de uso é
   hipótese plausível; cobertura de 12/30 casos impede sustentação. [M-usage]
4. Limites — satisfação descreve tickets respondidos; médias agregadas e
   coortes retrospectivas medem populações diferentes. [C-coverage]
5. Ação — Head de Produto, 7 dias: auditar os 18 casos sem cobertura;
   avançar se o sinal temporal se mantiver com cobertura >=70%; parar e
   revisar a hipótese se a auditoria contradizer o sinal. [A-validate-usage]
```

O exemplo orienta formato e níveis; na entrega real, referências, períodos, intervalos e população são preenchidos pelo pipeline, inclusive quando a tendência for flat/down ou não calculável. Relatório e app recebem o mesmo headline, claims, ações e limitações; somente formatação visual difere.

### Integração, publicação e falhas

`AnalysisResult` recebe quatro DataFrames adicionais: `monthly_churn`, `reason_distribution`, `event_cohort_metrics`, `mechanism_scorecard`. `cli.reproduce` preserva a sequência única: contratos/QA → seleção comum de eventos/painéis → histórico/motivos/coortes → candidatos com gates completos → scorecard → claims/modelo existentes → `AnalysisResult` → publicação/validação. Nenhum cálculo analítico é disparado pelo app. O scorecard consome os gates finalizados dos findings; não altera confiança depois de uma fila já construída.

`publish_artifacts` serializa as evidências, constrói `_build_ceo_answer(result)` uma vez e passa o mesmo objeto a `_build_report(result, queue, watchlist, answer)`. O JSON persistido é lido pelo app somente após validação. A primeira área útil apresenta headline e cinco blocos; modelo, metodologia e tabelas de auditoria vêm depois. Manter as três abas, componentes, filtros e downloads atuais; filtro de cronologia da aba Evidências exibe os valores correspondentes, sem rebatizar a resposta strict como observed. Corrigir estados `flat`, `insufficient`, razão com início zero/nulo e watchlist vazia no caminho compartilhado/apresentação pertinente.

**Premissa de publicação: um escritor e nenhum leitor concorrente do diretório de destino.** Gerar/reproduzir offline, com app parado; finalizar escrita e validar antes de abrir o app. O `make check` já usa diretório temporário exclusivo. Manter replace atômico por arquivo e manifesto por último; isto não é transação de diretório e a validação prévia não elimina TOCTOU com publicações simultâneas. Documentar a premissa no README e não implementar hot reload/publicação concorrente nesta feature. Caso esse uso se torne necessário, exigirá snapshot imutável ou leitura validada dos mesmos bytes, em mudança separada.

O conjunto obrigatório passa de nove para 14 payloads mais `run_manifest.json`. Manifesto registra schema, `analysis_id`, parâmetros, unidades, políticas de calendário/população/exclusão, seed/reamostragens e hashes. Validação exige nomes exatos, checksums, cinco blocos em ordem, IDs únicos, referências resolvidas, tipos/nulabilidade, unidades/comparadores presentes e ausência de números não finitos. Normalizar ausência legítima para null; erro de cálculo não finito tem estado explícito ou bloqueia a publicação, nunca vira fato. Hash válido sozinho não valida a semântica. Falha mostra artefato/causa e instrução de reprodução; o app para sem fallback para resultado antigo.

## Expected Changes

Quinze arquivos existentes de código/testes/documentação, cinco novos artefatos e regeneração dos dez arquivos canônicos existentes. Nenhum módulo, pacote, API, banco ou exclusão de arquivo. A quantidade final de arquivos modificados depende da reprodução: a correção do primeiro churn pode alterar painel, claims, fila e modelo; preservar esses contratos não significa congelar valores incorretos.

| Arquivo relativo à solução | Mudança esperada |
|---|---|
| `src/ravenstack_churn/config.py` | Períodos, limite observável, parâmetros de comparação e reamostragem centralizados; registrar no manifesto. |
| `src/ravenstack_churn/panel.py` | Seleção compartilhada do primeiro terminal válido antes da deduplicação; adaptar todos os callers; MRR nullable quando desconhecido; painel relativo reutilizando features, com horizonte observado e contagem de exclusões. |
| `src/ravenstack_churn/quality.py` | Usar a seleção terminal válida compartilhada nas divergências de flags; atualizar `label_policy` e preservar contagens de anomalias brutas. |
| `src/ravenstack_churn/diagnosis.py` | `build_monthly_churn`, `build_reason_distribution`, `build_event_cohort_metrics`, `build_mechanism_scorecard`; enriquecer `evaluate_candidates` com gates individuais, corroboração no horizonte e evidência temporal. `build_claim_checks` mantém contrato, com metadados de cobertura derivados para a resposta. Usar pandas, scipy/numpy e statsmodels já instalados. |
| `src/ravenstack_churn/cli.py` | Orquestrar análises e seleção de eventos uma vez; estender montagem de `AnalysisResult`; levar exclusões ao QA existente. |
| `src/ravenstack_churn/publish.py` | Estender dataclass; montar resposta canônica, relatório e ações derivados; serialização sem NaN/Infinity; conjunto exato, schema, referências e manifesto validados. Preservar fila accepted e watchlist de validação. |
| `app.py` | Renderizar JSON nos cinco blocos antes de metodologia/modelo; ler novas evidências, eliminar narrativa/cálculo decisório duplicados e tratar estados vazios/nulos, mantendo componentes e fluxo de leitura existentes. |
| `tests/test_panel.py` | Primeiro inválido seguido de válido, empate, reativação/flag desconhecida, fronteiras de signup, cutoff/label incompleto, âncoras/controles, MRR desconhecido versus zero e ausência de vazamento. |
| `tests/test_quality.py` | Regressão invalid-only→valid para divergências de flags e primeiro evento; flag de reativação ausente; política igual entre QA/painel/manifesto e contagens canônicas reconciliadas. |
| `tests/test_diagnosis.py` | Fixtures manuais para meses/entrantes/deduplicação, exposição repetida, segmentos versus complemento, motivos no horizonte, cobertura/coortes, cada gate/estado, multiplicidade e empate; baixa potência nunca rejected. Para satisfação, fixture com 9 respostas de média 1 e uma de média 5 na primeira âncora (1,4), média 4 na segunda e pesos de casos 1:3 confirma 3,35; distingue média de médias e pooling global de respostas, incluindo âncora sem respostas. |
| `tests/test_publish.py` | Resposta/relatório idênticos em conclusões/IDs; filas coerentes; no-data/flat/down/accepted/inconclusive; schema/referências inválidos mesmo com hash atualizado, ausência/tamper, nulos e reprodução determinística. |
| `tests/test_app.py` | AppTest dos cinco blocos e valores canônicos, filtros strict/observed, sem chamada analítica durante renderização, watchlist vazia e bloqueio por artefatos inválidos. |
| `tests/conftest.py` | Fixtures pequenas completas segundo os contratos, com populações e períodos reproduzíveis; não mascarar campos faltantes com defaults permissivos. |
| `README.md` | Definições, cinco blocos, artefatos, gates/limites, publicação sem concorrência e comandos; reconciliar alegações atuais com saídas regeneradas. |
| `Makefile` | Manter comandos; tornar a reprodução de `check` fail-fast antes de compare para não mascarar retorno de erro. |

Criar somente `artifacts/monthly_churn.csv`, `artifacts/reason_distribution.csv`, `artifacts/event_cohort_metrics.csv`, `artifacts/mechanism_scorecard.csv`, `artifacts/ceo_answer.json`. Regenerar todos os existentes via `make reproduce`; `findings.csv`, `report.md` e `run_manifest.json` necessariamente mudam. Os demais entram no diff somente se o cálculo legítimo mudar; nenhum artefato é editado manualmente. `pyproject.toml`, `requirements.txt`, CSVs brutos e pipeline/modelo preditivo permanecem sem expansão de escopo.

As verificações são as de Acceptance Criteria, no ambiente autorizado: regressões determinísticas focadas durante a implementação, depois `make reproduce` e `make check` no mesmo commit/diff, preservando hashes de origem. Registrar especificamente a migração invalid→valid, os deltas em artefatos antigos e a diferença em relação aos números exploratórios, sem forçar resultados. Revisão renderizada confirma a mesma resposta no app e no relatório, inclusive com todos os mecanismos inconclusivos. Esta fase não executa esses checks nem implementa os arquivos descritos.

## Implementation Process

> **Para agentes de implementação:** ler esta SPEC e o respectivo Sub-Task File antes de editar; trabalhar em TDD (`RED → GREEN → REFACTOR`), executar o menor teste direcionado após cada mudança e só então fechar o gate da fase. Não implementar um step futuro por conveniência.

**Goal:** produzir uma resposta executiva canônica, rastreável e útil à pergunta do CEO, mesmo quando nenhum mecanismo for sustentado.

**Architecture:** o pipeline calcula evidências uma vez, `publish.py` constrói `ceo_answer.json` e o mesmo objeto alimenta relatório e dashboard. A escada de evidência preserva fatos descritivos sem promover associação a causalidade.

**Tech Stack:** Python 3.12, pandas, NumPy, SciPy, statsmodels, pytest e Streamlit já instalados; zero dependência nova.

**Spec:** este arquivo, `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md`.

### Global Constraints

- Preservar CSVs brutos, seus cinco checksums e todo trabalho paralelo; nenhuma edição manual de artefato gerado.
- Não adicionar dependência, API paga, LLM, contato externo ou deploy.
- `strict` é a leitura executiva; `observed` é sensibilidade. Inconclusão nunca equivale a rejeição.
- Gates pesados rodam no ambiente autorizado via `codespace-manager`; nenhum bypass de teste, CI ou reprodução.
- Relatório e dashboard devem consumir a mesma resposta canônica; renderizadores não recalculam decisão.

### Review Focus

1. **Evento inválido seguido de válido:** a seleção conserva a conta em risco e escolhe o primeiro terminal válido; coberto no Step 01.
2. **Exposição repetida por conta:** bootstrap mantém todos os meses/âncoras da conta juntos e materializa cada ocorrência quando a mesma conta é sorteada mais de uma vez; coberto nos Steps 02 e 04.
3. **Ausência versus zero:** MRR, denominadores, cobertura e números não finitos mantêm nulabilidade e causa; coberto nos Steps 01, 02 e 05.
4. **Todos os mecanismos inconclusivos:** fatos continuam na abertura, fila fica vazia e ações viram validação; coberto nos Steps 04–06.
5. **Conjunto misturado ou semanticamente inválido:** checksum válido não basta; referências, tipos e IDs são verificados e o app bloqueia fallback; coberto nos Steps 05 e 06.

Após a revisão humana da SPEC, lançar **um agente distinto por step**, usando exatamente seu `Model` e `Agent`, passando o caminho desta task e o caminho do respectivo Sub-Task File. Cada agente implementa somente seu step e escreve suas regressões. Agentes não alteram o índice Git nem criam commits; o orquestrador faz isso depois do teste/review de step sequencial ou da sincronização integral do grupo paralelo. Lançar steps indicados como paralelos simultaneamente, respeitando dependências e ownership de arquivos. Metadados de modelo não autorizam chamadas pagas nem troca de provider. Ao concluir todos os steps de cada fase, executar **uma revisão de código por fase**, no `Reviewer model` indicado, sobre o diff integrado e suas evidências; não criar revisão por step. Não iniciar a próxima fase com falhas pendentes.

Os caminhos dos sub-tasks abaixo são relativos à raiz da solução. A pasta dos sub-tasks não se move quando esta task for promovida; atualizar/localizar referências pelo mesmo basename. Todo comando automatizado de teste/reprodução roda no Codespace do repositório, no commit/diff exato, via `codespace-manager list` e `codespace-manager run <nome> -- '<comando remoto>'`; não executar esses gates diretamente no Mac. Manter diário contemporâneo e hashes brutos; não publicar/deployar, contatar clientes nem alterar dados de origem.

### Parallelization Overview

```text
FASE 1 — motor analítico + aplicação existente executáveis
                         [01 opus]
                         /       \
                        v         v
                 [02 opus]     [03 opus]
                 histórico     painel relativo
                        \         /
                         v       v
                         [04 opus]
                   métricas/gates + reprodução
                              |
                    revisão da fase: opus
==============================|================================
FASE 2 — resposta canônica + superfícies verificadas
                              v
                         [05 opus]
                    publicação + relatório
                         /       \
                        v         v
                [06 sonnet]   [07 sonnet]
                 dashboard    README + gate
                        \         /
                         v       v
              revisão da fase: opus + check integrado
```

| Step | Phase | Model | Agent | Depends on | Parallel with | Sub-Task File |
|---|---|---|---|---|---|---|
| 01 — Seleção terminal, QA e MRR | 1 | opus | general:opus | None | None | [.specs/sub-tasks/implement-ceo-answer-architecture/01-unify-terminal-selection.md](../../sub-tasks/implement-ceo-answer-architecture/01-unify-terminal-selection.md) |
| 02 — Histórico, segmentos e motivos | 1 | opus | general:opus | 01 | 03 | [.specs/sub-tasks/implement-ceo-answer-architecture/02-build-historical-evidence.md](../../sub-tasks/implement-ceo-answer-architecture/02-build-historical-evidence.md) |
| 03 — Painel relativo ao churn | 1 | opus | general:opus | 01 | 02 | [.specs/sub-tasks/implement-ceo-answer-architecture/03-build-event-aligned-panel.md](../../sub-tasks/implement-ceo-answer-architecture/03-build-event-aligned-panel.md) |
| 04 — Coortes, gates e integração analítica | 1 | opus | general:opus | 02, 03 | None | [.specs/sub-tasks/implement-ceo-answer-architecture/04-integrate-evidence-gates.md](../../sub-tasks/implement-ceo-answer-architecture/04-integrate-evidence-gates.md) |
| 05 — Contrato, publicação e resposta | 2 | opus | general:opus | 04 | None | [.specs/sub-tasks/implement-ceo-answer-architecture/05-publish-canonical-ceo-answer.md](../../sub-tasks/implement-ceo-answer-architecture/05-publish-canonical-ceo-answer.md) |
| 06 — Dashboard | 2 | sonnet | general:sonnet | 05 | 07 | [.specs/sub-tasks/implement-ceo-answer-architecture/06-render-ceo-answer.md](../../sub-tasks/implement-ceo-answer-architecture/06-render-ceo-answer.md) |
| 07 — Documentação e gate de reprodução | 2 | sonnet | general:sonnet | 05 | 06 | [.specs/sub-tasks/implement-ceo-answer-architecture/07-document-and-close-reproduction-gate.md](../../sub-tasks/implement-ceo-answer-architecture/07-document-and-close-reproduction-gate.md) |

Sete steps e 35 subtasks, dois grupos paralelos e largura máxima **2**. Caminho crítico estrutural: `01 → (02 e 03 concluídos) → 04 → 05 → (06 e 07 concluídos)`; cinco steps em qualquer caminho mais longo, sem estimativa temporal presumida. Distribuição: cinco `general:opus`, dois `general:sonnet`, zero haiku. Opus é exigido nos Steps 01–05 por integridade analítica/contrato compartilhado; 06/07 consomem contratos fechados e têm decisões locais. Reviewer opus nas duas fases: teto disponível e nunca inferior ao maior tier. Combinar seleção/callers, contrato/publicação e documentação/gate evita três handoffs; não paralelizar edições de diagnosis/test_diagnosis entre 02 e 04.

### Phase Overview

#### Phase 1 — Base analítica verificável

**Steps:** 01, 02, 03, 04.

**Reviewer model:** opus (`general:opus`), teto disponível para revisão de integridade analítica.

**Acceptance Criteria that should be fulfiled:** o motor analítico calcula fatos históricos e coortes com testes determinísticos; QA/painel/diagnóstico usam o mesmo primeiro terminal válido, gates precedem confiança/fila e a aplicação existente continua executável. Step 04 fecha o conjunto canônico vigente com `make reproduce` e `make check`, hashes brutos preservados e deltas explicados. Não declarar concluída a resposta executiva: os contratos novos de publicação e sua apresentação vencem na fase 2.

**Checklist items:**

- CK-2, CK-3, CK-4 — componente de cálculo e DataFrames verificáveis: calendário, população, receita e comparadores corretos; publicação final pendente da fase 2.
- CK-5, CK-6 — métricas/coortes, cobertura, IDs e estados analíticos reproduzíveis; narrativa executiva pendente da fase 2.
- CK-7, CK-8 — gates completos, ausência de causalidade inferida, limites específicos e confiança/fila coerentes no pipeline existente.
- CK-11, HR-2 — regressões, reprodução e aplicação legada executáveis no ambiente autorizado, trabalho paralelo/dados preservados.
- HR-1, HR-3 — motivos/associação não viram causa, inconclusão não vira rejeição e referências quantitativas são conferidas sem impor resultado.

**Rubrics:**

- Precisão e rastreabilidade quantitativa.
- Disciplina da escada de evidências.
- Consistência e reprodução da entrega — escopo analítico e conjunto vigente ao final desta fase.
- Project Guidelines Alignment.

#### Phase 2 — Resposta executiva consistente

**Steps:** 05, 06, 07.

**Reviewer model:** opus (`general:opus`), teto disponível para revisar contrato compartilhado e superfícies.

**Acceptance Criteria that should be fulfiled:** JSON, relatório, dashboard renderizado, CSVs e manifesto compartilham a mesma execução e conclusão; todos os cinco blocos aparecem antes de metodologia/modelo, inclusive sem mecanismo sustentado. Após união de 06/07, a revisão executa `make check` no diff exato, confere hashes, semântica/referências, primeiro conteúdo renderizado e README. `make reproduce` já gerou os canônicos no Step 05; se correção alterar resultados, regenerar pelo comando e repetir o gate. Uma falha bloqueia fechamento; HTTP 200 ou manifesto escrito isoladamente não comprovam entrega.

**Checklist items:**

- CK-1, CK-9, CK-12 — resposta primeiro, ações completas e leitura executiva útil, com modelo/metodologia depois.
- CK-2, CK-3, CK-4, CK-5 — conferir os cálculos da fase 1 agora publicados com populações, comparadores, cobertura, receita e incerteza explícitos.
- CK-6, CK-7, CK-8 — IDs resolvidos, nível/estado separado, gates e limitações preservados em todas as superfícies, inclusive erro ou ausência de dados.
- CK-10, CK-11 — conjunto exato de 14 payloads mais manifesto, equality de análise/conclusão, AppTest, testes de corrupção e `make check` no mesmo diff.
- HR-1, HR-2, HR-3 — sem causalidade/recuperação prometida, APIs pagas/contato/deploy, resultados forçados, perda de dados ou bypass de gates.

**Rubrics:**

- Resposta executiva útil.
- Precisão e rastreabilidade quantitativa.
- Disciplina da escada de evidências.
- Consistência e reprodução da entrega.
- Project Guidelines Alignment.
