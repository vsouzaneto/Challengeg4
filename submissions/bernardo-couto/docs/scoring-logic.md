# Lógica de scoring — o que o número significa e o que ele não consegue fazer

**Para:** Head de Revenue Operations · **De:** data-scientist · **Data de referência dos dados:** 2017-12-31 · **Evidência:** `solution/pipeline/analysis/` (scripts reproduzíveis) e `docs/figures/` (tabelas e gráficos gerados por eles).

## Resumo em cinco linhas

1. Testamos 11 hipóteses registradas **antes** da análise (`analysis/00_hypotheses.md`). Sete foram refutadas — inclusive "vendedor bom fecha mais" e "conta grande fecha mais".
2. Entre deals abertos, **nada que sabemos sobre o deal prevê se ele vai fechar**: agente, produto, setor, conta, idade, carga — todos empatam com o aleatório no backtest (AUC-ROC entre 0,47 e 0,53 em dois cortes temporais). Isso está dito na tabela abaixo, com intervalos de confiança.
3. O que **é** previsível e útil: (a) **valor** — priorizar por valor esperado captura 2,4× mais receita realizada no top 20% que o aleatório; (b) **tempo** — nenhum deal na história fechou depois de 138 dias, e **81% do pipeline Engaging atual já passou disso**.
4. O score, portanto, é honesto sobre isso: `p_win` é a taxa-base do produto (60–65%), e a ordenação vem de **valor esperado × urgência**, com zumbis demovidos e razões escritas na voz do vendedor.
5. Não é "ordenar por preço disfarçado": correlação de Spearman entre score e preço = 0,46 no snapshot (limite do projeto: < 0,9). O que separa os dois é a urgência e a demoção de zumbis.

## Como o score é montado

```mermaid
flowchart LR
  subgraph entrada["Deal aberto em as_of"]
    P[produto]
    A[agente]
    C[conta? 68% sem]
    D[dias em Engaging<br/>nulo em Prospecting]
  end
  subgraph hist["Histórico até as_of<br/>(só close_date ≤ as_of)"]
    H1[taxa de Won por produto<br/>suavizada a=20]
    H2[razão mediana<br/>close_value / preço por produto]
    H3[curva de hazard:<br/>P(fecha Won nos próximos 14 d | aberto há d)]
  end
  P --> H1 --> PW["p_win<br/>0,60–0,65 · ×0,5 se zumbi"]
  P --> H2 --> EV["expected_value<br/>= preço × razão × p_win"]
  D --> H3 --> U["urgency 0–1<br/>zumbi 0,2 · Prospecting 0,5"]
  PW --> S["priority_score 0–100<br/>= 25·p̂ + 35·valor + 40·urgência"]
  EV --> S
  U --> S
  S --> T["tier A/B/C/D<br/>A exige confiança ≠ baixa<br/>zumbi nunca A"]
  A & C & D --> R["reason codes<br/>(voz do vendedor)"]
  C --> CF["confidence<br/>alta / média / baixa"]
```

### Componentes e pesos

| Componente | Como é calculado | Peso no score | Por quê esse peso |
|---|---|---|---|
| `p_win` | Taxa histórica de Won do produto, suavizada com prior bayesiano (a=20) para o global 63%. Multiplicada por 0,5 se o deal tem > 138 dias (zumbi). | 25 pontos (escala 0,30→0 · 0,80→1) | É o único estimador de probabilidade **calibrado** que temos (Brier 0,235 / 0,243, o melhor de 7 variantes testadas). Peso baixo porque varia pouco (60–65%): ele quase não separa deals, e fingir o contrário seria mentir. |
| valor | `log(1 + preço × razão_mediana)` normalizado pelo GTK 500 → 0,39 (MG Special) a 1,0 (GTK 500). A razão mediana `close_value/preço` dos Won é 0,967–1,004 em todos os produtos (IQR 0,13): o ajuste por histórico **quase não muda nada** — o preço de lista já é a estimativa. Mantemos a razão porque é o estimador correto e custa zero, não porque faça diferença. | 35 pontos | Valor é onde a priorização gera receita: top 20% por valor esperado captura 51% da receita realizada vs 20% do aleatório. Escala logarítmica para o GTK 500 (26.768) não engolir os outros seis produtos. |
| urgência | Hazard de 14 dias: entre deals que estavam abertos há `d` dias no histórico, a fração que virou Won nos 14 dias seguintes, normalizada pelo máximo. Zumbi (> 138 d) = 0,2. Prospecting (sem data) = 0,5 "desconhecida". | 40 pontos | É o que transforma "lista de valor" em "o que fazer esta semana". Também é o peso mínimo que mantém Spearman(score, preço) < 0,9 (grade de pesos em `docs/figures/11_diagnostics.md`); com 20 pontos o score vira ordenar por preço (0,93). |

### Regras duras (não são pesos, são portas)

- **Zumbi** (`days_in_engaging` > 138): `p_win` × 0,5, urgência 0,2, score ≤ 49, nunca tier A. Justificativa: em 6.711 deals fechados, nenhum ciclo passou de 138 dias; dos 679 deals que já tinham > 138 d nos cortes de backtest, **zero** fecharam depois.
- **Tier A exige confiança ≠ baixa**: deal sem conta e sem timeline (Prospecting) ou zumbi não pode ser a primeira ligação da semana.
- **Conta desconhecida** ⇒ confiança nunca `alta` + reason code pedindo para completar o CRM. E uma proibição: **nada da conta entra como preditor**. Motivo (verificado por data-engineer e por nós): 100% dos deals que fecharam têm conta; só 32% dos que continuam abertos têm (71% em 2017-06-30, 58% em 2017-09-30). Ou seja, "ter conta" prevê "já fechou", não "vai fechar" — qualquer modelo que use isso parece ótimo no treino e não serve para nada na segunda-feira. Setor, tamanho e histórico da conta aparecem como contexto nas razões, com peso zero.

## Reason codes (o que o vendedor lê)

Códigos do contrato `ReasonCode`. Direção `+` sobe o score, `-` desce, `i` é informativo (mostra o número, mas não mexe no score — porque o backtest provou que não prevê). **Unidade do peso: pontos de `priority_score` (0–100)**, para todo código, como o pipeline implementou (`docs/ml-pipeline.md` §2.3): `HIGH_TICKET = 35·valor_norm`; `LOW_TICKET = −(35 − 35·valor_norm)`; `ZOMBIE_RISK = 50·(p_win − p_prod)` (efeito de cortar `p_win` pela metade no componente de probabilidade); `PRODUCT_BASE_RATE = 25·p̂` (os pontos que o componente de probabilidade entrega); `URGENCY_WINDOW = 40·urgência` (novo código, os pontos do componente de urgência); informativos = 0. A soma dos pesos com sinal reproduz o score, e a API expõe isso em `score_breakdown` (probabilidade / valor / urgência em pontos).

| Código | Direção | Texto em pt-BR (modelo; números vêm do histórico até `as_of`) |
|---|---|---|
| `PRODUCT_BASE_RATE` | + | "GTX Plus Pro fecha em 64% dos casos (745 deals no histórico; média geral 63%)." Peso = 25·p̂ (ex.: +17,1 pts para 64%). |
| `URGENCY_WINDOW` | + | "127 dias em Engaging: nesta idade, 1 em cada X deals vira Won nas próximas duas semanas." Peso = 40·urgência (ex.: +39,2 pts; Prospecting +20; zumbi +8). |
| `HIGH_TICKET` | + | "Ticket alto: valor esperado de R$ 3.537 (preço 5.482 × 1,00 de razão histórica × 64%)." |
| `LOW_TICKET` | - | "Ticket baixo: MG Special vale R$ 55; feche rápido ou não gaste a semana nele." |
| `SURVIVAL_POSITIVE` | i | "127 dias em Engaging: deals que chegam aqui fecharam em 79% dos casos — mas atenção: faltam 11 dias para o ciclo máximo já visto (138)." |
| `ZOMBIE_RISK` | - | "150 dias em Engaging: nenhum deal na história fechou depois de 138. Confirme se ainda existe; se não, marque como Lost." |
| `PROSPECTING_NO_TIMELINE` | i | "Sem data de engajamento: não dá para medir urgência. Registre o primeiro contato no CRM." |
| `ACCOUNT_UNKNOWN` | i | "Sem conta no CRM: não sabemos setor nem tamanho. Complete o cadastro para o score ganhar confiança." |
| `AGENT_TRACK_RECORD` | i | "Você fecha 64% dos seus deals (272 fechados; time 63%). No backtest isso não previu o futuro, por isso não altera o score." |
| `AGENT_PRODUCT_FIT` | i | "Você fecha 73% dos GTX Plus Pro (18 deals — amostra pequena)." |
| `SECTOR_FIT` | i | "Setor retail: 62% de fechamento (950 deals). Igual à média." |
| `ACCOUNT_SIZE` | i | "Conta com receita de US$ 1,1 bi e 2.822 funcionários. Tamanho não previu fechamento no backtest." |
| `ACCOUNT_HISTORY` | i | "Esta conta já fechou 12 de 18 com a gente (67%)." |
| `AGENT_OVERLOAD` | i | "Você tem 96 deals abertos (quartil superior do time). Sugestão para o manager: redistribuir." |
| `MODEL_CONTRIBUTION` | ± | Reservado para a camada 2 (modelo). **Hoje peso zero** — ver "Modelo". |

## Backtest: o que bate o quê

Protocolo: em cada corte `T`, refazemos o pipeline aberto em `T` (engajado até `T`, não fechado até `T`), calculamos o histórico **só com fechamentos ≤ T**, pontuamos, e conferimos o que aconteceu depois. Deals ainda abertos no snapshot são "censurados" e reportados à parte. Intervalos de 95% por bootstrap (2.000 reamostras). Tabela completa em `docs/figures/10_backtest.md`.

**Fonte oficial dos números: `solution/models/latest/metrics.json`** (gerado pelo job Spark, exibido na tela "Qualidade"). As tabelas abaixo vêm do protótipo pandas e diferem na 2ª–3ª casa decimal por semente do bootstrap e ordem de desempate (`p_win` tem muitos empates por produto); os pontos do scorer coincidem (Brier 0,235 / 0,243; receita 0,376 / 0,359). O pipeline acrescenta um baseline que o protótipo não tinha — **"preço excluindo > 138 d"** (ordenar por preço só entre deals vivos) — para separar quanto do ganho de "ordenar por preço" sobrevive quando os parados saem da conta.

**Corte 2017-06-30** — 1.686 abertos, 970 com desfecho (taxa-base 62,8%), 716 censurados, 149 zumbis em T.

| Candidato | AUC-PR [IC 95%] | AUC-ROC | Brier | P@10 por vendedor | Receita realizada no top 20% [IC 95%] |
|---|---|---|---|---|---|
| Aleatório | 0,664 [0,621; 0,706] | 0,530 | — | 0,660 | 0,204 [0,169; 0,244] |
| Ordenar por preço | 0,634 [0,593; 0,678] | 0,492 | — | 0,643 | 0,505 [0,453; 0,550] |
| Mais novo primeiro | 0,619 [0,577; 0,661] | 0,501 | — | 0,603 | 0,175 [0,143; 0,212] |
| Mais antigo primeiro | 0,616 [0,574; 0,662] | 0,499 | — | 0,627 | 0,160 [0,130; 0,194] |
| Taxa-base por produto (= `p_win`) | 0,651 [0,612; 0,697] | 0,533 | 0,235 | 0,677 | 0,250 [0,199; 0,303] |
| `expected_value` | 0,634 [0,593; 0,678] | 0,492 | — | 0,643 | 0,505 [0,453; 0,550] |
| **`priority_score`** | 0,601 [0,562; 0,645] | 0,461 | — | 0,627 | **0,377 [0,321; 0,430]** |

**Corte 2017-09-30** — 2.409 abertos, 935 com desfecho (taxa-base 59,8%), 1.474 censurados, 530 zumbis em T.

| Candidato | AUC-PR [IC 95%] | AUC-ROC | Brier | P@10 por vendedor | Receita realizada no top 20% [IC 95%] |
|---|---|---|---|---|---|
| Aleatório | 0,619 [0,577; 0,666] | 0,525 | — | 0,603 | 0,206 [0,168; 0,247] |
| Ordenar por preço | 0,593 [0,549; 0,637] | 0,478 | — | 0,577 | 0,459 [0,434; 0,529] |
| Mais novo primeiro | 0,581 [0,544; 0,630] | 0,495 | — | 0,547 | 0,194 [0,157; 0,233] |
| Mais antigo primeiro | 0,579 [0,541; 0,625] | 0,505 | — | 0,537 | 0,175 [0,137; 0,211] |
| Taxa-base por produto (= `p_win`) | 0,605 [0,558; 0,649] | 0,495 | 0,243 | 0,557 | 0,006 [0,005; 0,017] |
| `expected_value` | 0,593 [0,549; 0,637] | 0,478 | — | 0,577 | 0,459 [0,441; 0,542] |
| **`priority_score`** | 0,565 [0,525; 0,612] | 0,441 | — | 0,560 | **0,359 [0,305; 0,398]** |

Leitura sem eufemismo:

- **Em probabilidade de fechar, ninguém bate o aleatório.** Todos os ICs de AUC-PR se sobrepõem ao do aleatório; AUC-ROC de 0,44 a 0,53. O `priority_score` fica **abaixo** de 0,5 em AUC-ROC porque produtos caros fecham marginalmente menos (GTK 500: 60%) — ao priorizar valor, pagamos ~2 pp em taxa de acerto. Escolha consciente: receita.
- **Em receita, o score entrega 1,8× o aleatório** (0,377 e 0,359 vs 0,204 e 0,206) e fica abaixo de "ordenar por preço" (0,505 / 0,459). A diferença é o preço que pagamos pela urgência e pela demoção de zumbis — que não aparecem nesta métrica (deals com desfecho realizado, por definição, não eram zumbis mortos). Quem quiser só receita, ordena por preço; a ferramenta existe para dizer **quando** agir e **o que está morto**.
- **"Mais novo primeiro" não é o baseline forte que se supunha.** Entre deals vivos com desfecho, AUC-ROC 0,50. Ele só parece forte (AUC-ROC 0,73–0,83) quando os censurados são contados como Lost — e aí o que ele está capturando é exatamente o efeito zumbi, que já é uma regra dura do score. Detalhe em `docs/figures/11_diagnostics.md`.
- **Calibração**: `p_win` (taxa-base do produto) tem erro por bin de 1–6 pp; a variante com ajustes por agente e sobrevivência superestimava em até 19 pp no bin mais alto — por isso foi descartada.
- **Cortes mensais** (abr–out/2017, `backtest_monthly_aucpr.png`): mesma história em todos os sete meses — nenhum critério se separa do aleatório de forma estável. O padrão de calendário que apareceu nos diagnósticos (win rate mensal mais alto em mar/jun/set/dez) foi examinado pela revisão de RevOps (`docs/revops-review.md` §3b) e descartado como sinal: o Won é plano ao longo do mês; o que varia é o **registro de Lost** (concentrado em abr/jul/out, com ciclo mediano de 7 dias). É artefato de como o CRM foi preenchido, não comportamento de compra.

## O que o vendedor vê no snapshot (2017-12-31)

| Grupo | n | `p_win` médio | score médio | Valor esperado somado |
|---|---|---|---|---|
| Engaging vivo (≤ 138 d) | 298 | 0,63 | 62,5 | R$ 437 mil |
| Engaging zumbi (> 138 d) | 1.291 | 0,32 | 32,5 | R$ 998 mil (nominal; provavelmente irrecuperável) |
| Prospecting | 500 | 0,63 | 59,7 | R$ 674 mil |

### A fila de zumbis, em dinheiro

| Fila | Deals | Valor nominal (preço × razão) | Idade mediana | Com conta |
|---|---|---|---|---|
| Zumbis (> 138 d) — "Decidir / limpar" | 1.291 | **R$ 3,19 mi** | 201 d | 32% |
| Engaging vivos (≤ 138 d) — "Trabalhar" | 298 | R$ 0,69 mi | 104 d | 30% |

A fila morta carrega **4,6× mais valor nominal** que o pipeline vivo. Por manager: Celia Rouche R$ 842 mil (257 deals), Summer Sewald R$ 718 mil (305), Melvin Marxen R$ 535 mil (213), Rocco Neubert R$ 437 mil (157), Cara Losch R$ 372 mil (169), Dustin Brinkmann R$ 282 mil (190). 402 desses deals foram engajados em julho/2017 e 173 em agosto — um lote que ninguém atualizou no CRM. Esse dinheiro **não entra no forecast**; entra numa fila separada na UI, ordenada por valor e, em empate, pelo zumbi mais novo (mais chance de ainda existir), com um botão "confirmar ou marcar Lost". A urgência desses deals é constante (0,2): é trabalho administrativo, não comercial. Se a Head quiser, o feedback dessa fila calibra no futuro o fator 0,5 que hoje é convenção.

Tiers absolutos: **A = 67** (todos Engaging vivos com conta ou histórico suficiente), B = 516 (380 Prospecting), C = 771 (563 zumbis), D = 735 (728 zumbis). Confiança: alta 88 · média 372 · baixa 1.629 (zumbis + sem conta). Nenhum deal sem score.

### Três deals de exemplo

**`059K86LU` — Kami Bicknell · GTX Plus Pro · Labdrill · Engaging há 127 dias → score 85,9 · tier A · confiança alta**
`p_win` 0,64 · valor esperado R$ 3.537 · urgência 0,98.
- URGENCY_WINDOW (+39,2 pts): "127 dias em Engaging: nesta idade os deals que vão fechar estão fechando — janela de duas semanas."
- HIGH_TICKET (+29,6 pts): "Ticket alto: valor esperado de R$ 3.537."
- PRODUCT_BASE_RATE (+17,1 pts): "GTX Plus Pro fecha em 64% dos casos (745 deals)."
- SURVIVAL_POSITIVE (i): "127 dias em Engaging: deals que chegam aqui fecharam em 79% dos casos — faltam 11 dias para o ciclo máximo já visto (138)."
- AGENT_PRODUCT_FIT (i): "Você fecha 73% dos GTX Plus Pro (18 deals — amostra pequena)."
- SECTOR_FIT (i): "Setor da Labdrill: 62% (950 deals), igual à média."
- Próxima ação: "Ligar esta semana e propor data de fechamento antes de 11 dias."

**`A04V2WB3` — Elease Gluck · GTK 500 · sem conta · Engaging há 150 dias → score 43,2 · tier C · confiança baixa**
`p_win` 0,31 (0,61 × 0,5) · valor esperado R$ 7.950 · urgência 0,2.
- HIGH_TICKET (+34,9 pts): "Se existir, é o maior ticket do catálogo (R$ 25.897 de valor bruto esperado)."
- ZOMBIE_RISK (−15,4 pts = 50·(0,31 − 0,61)): "150 dias em Engaging: nenhum deal na história fechou depois de 138. Confirme se ainda existe."
- URGENCY_WINDOW (+8,0 pts): "Urgência administrativa, não comercial: confirmar ou encerrar."
- PRODUCT_BASE_RATE (+0,4 pts): "GTK 500 fecha em 61% — mas só 25 deals no histórico; com a metade aplicada, quase nada sobra."
- ACCOUNT_UNKNOWN (i): "Sem conta no CRM."
- Próxima ação: "Confirmar com o cliente se a oportunidade existe; se não, marcar Lost e limpar o pipeline."

**`73CWPT9H` — Gladys Colclough · GTX Plus Pro · sem conta · Prospecting → score 66,7 · tier B (barrado de A por confiança baixa)**
`p_win` 0,64 · valor esperado R$ 3.537 · urgência 0,5 (desconhecida).
- HIGH_TICKET (+29,6 pts).
- URGENCY_WINDOW (+20,0 pts): "Sem data de engajamento: urgência desconhecida, contada como neutra."
- PRODUCT_BASE_RATE (+17,1 pts).
- PROSPECTING_NO_TIMELINE (i): "Sem data de engajamento: não dá para medir urgência."
- ACCOUNT_UNKNOWN (i): "Sem conta: complete o cadastro."
- AGENT_TRACK_RECORD (i): "Você fecha 59% (232 deals; time 63%). Não altera o score."
- Próxima ação: "Registrar conta e data de engajamento no CRM; só então priorizar."

## Modelo (camada 2)

Testamos regressão logística em frame temporal (features calculadas com histórico até cada mês, rótulo conhecido até T) — quatro conjuntos de features, dois cortes. Nenhum bate a taxa-base do produto: AUC-ROC 0,45–0,51, Brier pior (0,250–0,283) e calibração pior (superestima em 9–20 pp). Tabela em `docs/figures/20_model_candidates.md`. **Decisão:** camada 2 entra em produção com **peso zero** no blend (modo sombra: treinada, versionada, monitorada, não altera o score) até que um backtest mostre AUC-PR > taxa-base + 0,02 em ambos os cortes. GBT não foi testado (sem biblioteca de árvores aqui) e só será cogitado se a LR sombra mostrar sinal.

## Limitações — sem eufemismo

1. **O score não prevê quem vai fechar.** Ele ordena por valor e tempo. Se alguém apresentar este produto como "IA que prevê fechamento", está errado. Os dados do CRM não contêm o que decide um deal (interações, proposta, concorrência, decisor).
2. **81% do pipeline Engaging está morto pelo critério histórico.** A primeira semana de uso é limpeza de CRM, não venda. A ferramenta deixa isso explícito; não maquia.
3. **68% dos deals abertos não têm conta**, e isso não é preenchimento tardio (é constante em toda faixa de idade). Setor, tamanho e histórico da conta não têm sinal preditivo mesmo quando existem — então a perda prática é de contexto, não de acurácia.
4. **Prospecting não tem data.** Urgência é "desconhecida" (0,5), não zero; o score desses 500 deals é essencialmente valor. Barrados de tier A sem conta.
5. **Um ano de dados, e com truncamento:** `close_date` começa em 2017-03-01, então deals rápidos engajados antes de março não existem — isso infla o win rate de dez/2016–fev/2017 e é o motivo de não usarmos mês de engajamento.
6. **O único padrão temporal forte do dataset — win rate mensal mais alto em mar/jun/set/dez — é artefato de registro de Lost, não comportamento de compra** (`docs/revops-review.md` §3b). Foi descartado; nenhuma regra de calendário entra no score.
7. **Zumbi = 0,5 × p_win é convenção, não estimativa.** Não há dados para calibrar a probabilidade de um deal com 200 dias — nunca aconteceu um fechar.
8. **O `priority_score` fica abaixo de "ordenar por preço" em receita capturada** (0,38 vs 0,51). Se a Head preferir maximizar receita bruta e aceitar ignorar urgência e zumbis, o peso do valor sobe para 50 e o de urgência cai para 25 — mas Spearman com preço passa de 0,9 e a ferramenta vira uma lista de preços.

## Reproduzir

```bash
cd solution/pipeline
uv run python analysis/01_eda.py            # H1–H8, H10, H11 → docs/figures/01_eda.md + eda_*.png
uv run python analysis/10_backtest.py       # H9, baselines, calibração, snapshot → 10_backtest.md, backtest_*.png
uv run python analysis/11_diagnostics.py    # regras simplificadas, diagnóstico de calendário (descartado, revops-review §3b), grade de pesos, fila de zumbis → 11_diagnostics.md
uv run python analysis/20_model_candidates.py  # LR numpy vs regras → 20_model_candidates.md
```
