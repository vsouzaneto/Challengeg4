# Model card — `2017-12-31-rules-v1`

**Data de referência dos dados:** 2017-12-31 · **Gerado pelo job** `train` (git `4aed364`, Spark 3.5.9) · **Duração:** 58.1 s

## 1. O que este artefato é

Duas camadas. **Camada 1 (regras)** produz o score que o vendedor vê: `priority_score = 25·p̂ + 35·valor + 40·urgência`, com `p_win` = taxa histórica de Won do produto (suavizada, prior a=20) × 0.5 se o deal passou de 138 dias em Engaging; valor = `log1p(preço × razão histórica)` normalizado; urgência = hazard empírico de Won nos próximos 14 dias dado a idade. **Camada 2 (modelo)** é uma regressão logística Spark ML treinada em frame temporal, em **modo sombra**: peso `0.0` no blend. Ela **não** altera nenhum score; suas métricas são registradas para decidir a promoção em versões futuras.

## 2. Dados e janela

- Fonte: CRM (snapshot 2017-12-31), tabelas gold `opportunity_features`, `history_stats` e `labels` particionadas por `as_of` (só informação conhecida em `as_of`).
- Frame de treino do modelo sombra final: meses 2017-03-31, 2017-04-30, 2017-05-31, 2017-06-30, 2017-07-31, 2017-08-31, 2017-09-30, 2017-10-31, 2017-11-30; 8066 linhas de treino, 548 no mês de calibração (2017-11-30); taxa de Won no treino 66%.
- Cortes de backtest: 2017-06-30, 2017-09-30 (walk-forward: histórico ≤ T, desfecho > T).
- Nenhum `randomSplit`/`CrossValidator`; nenhum `close_value`/`close_date` fora de história e avaliação; nenhum relógio real.

## 3. Features (lista fechada)

Camada 2: `product`, `product_rate`, `log_days`, `is_zombie`, `log_price`, `open_load`, `survival_rate`. Proibidas (e testadas): tudo da conta (`account_*`, setor, porte), `engage_month`, desfechos. Motivo: 100% dos deals fechados têm conta contra 32% dos abertos — `account_known` codifica "já fechou", não "vai fechar".

Coeficientes padronizados da LR final (contribuição = coef × valor padronizado):

| Feature | Coeficiente |
|---|---|
| `product=GTX Basic` | 0,007 |
| `product=MG Special` | 0,000 |
| `product=GTX Pro` | 0,000 |
| `product=MG Advanced` | 0,000 |
| `product=GTX Plus Basic` | -0,024 |
| `product=GTX Plus Pro` | 0,036 |
| `product=GTK 500` | 0,000 |
| `product=__unknown` | 0,000 |
| `product_rate` | -0,054 |
| `log_days` | 0,025 |
| `is_zombie` | 0,000 |
| `log_price` | 0,000 |
| `open_load` | -0,004 |
| `survival_rate` | 0,000 |
| `intercept` | 0,646 |

## 4. Resultado no snapshot

- 2089 deals abertos pontuados (500 em Prospecting); 1291 acima de 138 dias (R$ 3.185.048 nominais, fora do forecast).
- Conta conhecida em 32% dos deals.
- Tiers: A=67, B=516, C=771, D=735; confiança: alta=88, media=372, baixa=1629.
- Spearman(priority_score, preço) = 0,46 (limite do projeto: < 0,90 — não é "ordenar por preço").

## 5. Backtest temporal vs. baselines

Métricas probabilísticas (Brier, AUC-PR, calibração) usam `p_win`; métricas de ranking (P@10 por vendedor, receita capturada no top 20%) usam `priority_score`, que é o que o vendedor vê. Bootstrap pareado, 2.000 reamostras, semente fixa.

### Corte T = 2017-06-30

Abertos em T: 1686 · com desfecho até o snapshot: 970 (taxa-base 0,628) · censurados: 716 · parados (> 138 d) em T: 149, dos quais fecharam depois: **0** · Spearman(score, preço) = 0,54

| Critério | AUC-PR [IC95] | AUC-ROC | Brier | Lift top 10% | P@10/vendedor [IC95] | Receita top 20% [IC95] |
|---|---|---|---|---|---|---|
| aleatório | 0,605 [0,565; 0,646] | 0,466 | — | 0,92 | 0,603 [0,547; 0,660] | 0,171 [0,141; 0,208] |
| maior preço primeiro | 0,641 [0,592; 0,679] | 0,492 | — | 1,08 | 0,657 [0,587; 0,697] | 0,497 [0,449; 0,546] |
| mais novo primeiro | 0,622 [0,577; 0,661] | 0,501 | — | 0,94 | 0,613 [0,559; 0,670] | 0,174 [0,143; 0,213] |
| mais antigo primeiro | 0,617 [0,575; 0,659] | 0,499 | — | 0,94 | 0,627 [0,569; 0,679] | 0,160 [0,128; 0,194] |
| taxa-base por produto | 0,661 [0,612; 0,700] | 0,533 | 0,235 | 1,07 | 0,680 [0,621; 0,730] | 0,250 [0,199; 0,304] |
| regras · p_win | 0,661 [0,612; 0,700] | 0,533 | 0,235 | 1,07 | 0,680 [0,621; 0,730] | 0,250 [0,199; 0,304] |
| regras · valor esperado | 0,641 [0,592; 0,679] | 0,492 | — | 1,08 | 0,657 [0,587; 0,697] | 0,497 [0,449; 0,546] |
| **regras · priority_score (o que o vendedor vê)** | 0,602 [0,561; 0,644] | 0,461 | — | 0,92 | 0,630 [0,557; 0,672] | 0,376 [0,320; 0,431] |
| modelo sombra · LR calibrada (peso 0 no score) | 0,628 [0,591; 0,675] | 0,507 | 0,273 | 1,00 | 0,660 [0,593; 0,700] | 0,307 [0,235; 0,318] |

Calibração de `p_win` (erro médio absoluto 0,041):

| Bin | n | p_win previsto | taxa real | gap |
|---|---|---|---|---|
| 0 | 194 | 0,654 | 0,567 | -0,087 |
| 1 | 194 | 0,664 | 0,639 | -0,025 |
| 2 | 194 | 0,668 | 0,634 | -0,034 |
| 3 | 194 | 0,671 | 0,619 | -0,052 |
| 4 | 194 | 0,676 | 0,680 | 0,005 |

### Corte T = 2017-09-30

Abertos em T: 2409 · com desfecho até o snapshot: 935 (taxa-base 0,598) · censurados: 1474 · parados (> 138 d) em T: 530, dos quais fecharam depois: **0** · Spearman(score, preço) = 0,50

| Critério | AUC-PR [IC95] | AUC-ROC | Brier | Lift top 10% | P@10/vendedor [IC95] | Receita top 20% [IC95] |
|---|---|---|---|---|---|---|
| aleatório | 0,592 [0,551; 0,637] | 0,504 | — | 0,89 | 0,600 [0,543; 0,653] | 0,203 [0,164; 0,243] |
| maior preço primeiro | 0,594 [0,548; 0,635] | 0,478 | — | 1,01 | 0,583 [0,533; 0,643] | 0,489 [0,432; 0,529] |
| mais novo primeiro | 0,584 [0,544; 0,628] | 0,495 | — | 0,98 | 0,550 [0,507; 0,620] | 0,194 [0,156; 0,235] |
| mais antigo primeiro | 0,580 [0,537; 0,623] | 0,505 | — | 0,87 | 0,543 [0,500; 0,618] | 0,180 [0,135; 0,211] |
| taxa-base por produto | 0,600 [0,563; 0,649] | 0,495 | 0,243 | 1,01 | 0,543 [0,503; 0,620] | 0,006 [0,005; 0,016] |
| regras · p_win | 0,600 [0,563; 0,649] | 0,495 | 0,243 | 1,01 | 0,543 [0,503; 0,620] | 0,006 [0,005; 0,016] |
| regras · valor esperado | 0,594 [0,548; 0,635] | 0,478 | — | 1,01 | 0,583 [0,533; 0,643] | 0,489 [0,432; 0,529] |
| **regras · priority_score (o que o vendedor vê)** | 0,566 [0,525; 0,610] | 0,441 | — | 0,98 | 0,560 [0,507; 0,617] | 0,359 [0,302; 0,400] |
| modelo sombra · LR calibrada (peso 0 no score) | 0,582 [0,548; 0,633] | 0,484 | 0,276 | 1,01 | 0,570 [0,543; 0,657] | 0,292 [0,222; 0,311] |

Calibração de `p_win` (erro médio absoluto 0,046):

| Bin | n | p_win previsto | taxa real | gap |
|---|---|---|---|---|
| 0 | 187 | 0,619 | 0,594 | -0,026 |
| 1 | 187 | 0,642 | 0,642 | -0,001 |
| 2 | 187 | 0,645 | 0,594 | -0,052 |
| 3 | 187 | 0,655 | 0,529 | -0,126 |
| 4 | 187 | 0,658 | 0,631 | -0,027 |

**Leitura honesta.** Nenhum critério — nem as regras, nem o modelo — acerta *quem* vai fechar melhor que o acaso (AUC-ROC ≈ 0,5, IC95 do AUC-PR sobreposto ao aleatório). O ganho está em **valor** (receita capturada no top 20% ≈ 1,7–1,8× o aleatório), em **momento** (hazard por idade) e na **limpeza** dos deals parados, que nunca fecharam.

Sensibilidade pessimista (censurados tratados como Lost): "mais novo primeiro" sobe para AUC-ROC 0,73, 0,83 **por causa dos zumbis** (deal antigo e ainda aberto = nunca fechou), não por prever fechamento.

## 6. Modelo sombra e regra de promoção

Regra: promote only if, in every cut, AUC-PR(model) >= AUC-PR(base rate) + 0.02 and Brier(model) <= Brier(base rate) after calibration.

| Corte | AUC-PR modelo | AUC-PR taxa-base | Brier modelo | Brier taxa-base | Passou |
|---|---|---|---|---|---|
| 2017-06-30 | 0,628 | 0,661 | 0,273 | 0,235 | não |
| 2017-09-30 | 0,582 | 0,600 | 0,276 | 0,243 | não |

**Decisão:** mantido em sombra (`blend_model_weight = 0.0`).

Viés conhecido do frame: meses recentes só têm deals que fecharam rápido, logo a taxa de Won do treino é maior que a fora do tempo; a calibração isotônica no último mês do frame corrige parte disso. Reponderação temporal fica como questão aberta.

## 7. Aceite (spec §7)

| Verificação | Corte | Valor | Passou |
|---|---|---|---|
| brier_p_win <= 0.245 | 2017-06-30 | 0.2348 | sim |
| mean_calibration_error <= 0.06 | 2017-06-30 | 0.0405 | sim |
| revenue_top20 >= 1.5 x random and CI low > random | 2017-06-30 | [0.3761, 0.1713] | sim |
| spearman(priority_score, sales_price) < 0.9 | 2017-06-30 | 0.54 | sim |
| zombies at cut that closed after (report; expected 0) | 2017-06-30 | 0 | sim |
| brier_p_win <= 0.245 | 2017-09-30 | 0.2428 | sim |
| mean_calibration_error <= 0.06 | 2017-09-30 | 0.0462 | sim |
| revenue_top20 >= 1.5 x random and CI low > random | 2017-09-30 | [0.3591, 0.203] | sim |
| spearman(priority_score, sales_price) < 0.9 | 2017-09-30 | 0.5011 | sim |
| zombies at cut that closed after (report; expected 0) | 2017-09-30 | 0 | sim |

**Resultado:** todos os limiares atendidos.

## 8. Monitoramento

- O job `score` grava no `_manifest.json` da partição o PSI de cada feature contra a distribuição do frame de treino (referência em `training_manifest.json`) e alerta se PSI > 0,2. Esperar alarme em `account_known` se alguém o incluir: é o sintoma do vazamento descrito em §3, não drift real.
- Cobertura de conta (`account_known_rate`) e distribuição de tiers/confiança por lote.
- Feedback do vendedor (`POST /api/v1/feedback`) alimenta `data/feedback/actions` para, num ciclo futuro, calibrar o fator 0.5 dos deals parados.

## 9. Limitações e uso pretendido

- **Uso:** ordenar a fila semanal de um vendedor e separar a fila "confirmar ou encerrar". **Não** é previsão individual de fechamento, **não** avalia vendedores e **não** decide encerrar deal.
- `p_win` é a taxa do produto (60–65%): igual para todo deal do mesmo produto; em deals parados o fator 0.5 é convenção declarada, não estimativa.
- 68% dos deals abertos não têm conta: setor, porte e histórico aparecem só como contexto (peso 0) e a confiança cai.
- Toda idade é contada até `as_of` (snapshot 2017-12-31), nunca até hoje.
- Dataset possivelmente sintético (Kaggle): padrões de calendário (fim de trimestre) foram avaliados e **não** entram no score.
