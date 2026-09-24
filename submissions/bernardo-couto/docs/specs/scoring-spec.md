# Especificação do scoring — para o `machine-learning-engineer`

**Status:** proposta do data-scientist, 2026-09-23. Protótipo executável em `solution/pipeline/analysis/rules.py` (pandas); portar para `lead_scorer/scoring/` (Spark SQL / pandas no driver) com funções puras e testes. Evidência de cada decisão: `docs/figures/{01_eda,10_backtest,11_diagnostics,20_model_candidates}.md`.

## 0. Decisões que esta spec impõe (e a evidência)

| Decisão | Evidência |
|---|---|
| `p_win` = taxa de Won por produto (suavizada, a=20), **sem** ajustes por agente, agente×produto, setor, sobrevivência | AUC-ROC fora do tempo de cada ajuste 0,47–0,50; variante com ajustes piora Brier (0,243→0,251) e superestima 19 pp no bin alto. `10_backtest.md` "Variantes". |
| `account_*` **proibido como feature preditiva** (regras e modelo) | 100% dos deals com desfecho têm conta vs 32% dos ainda abertos (71% / 58% nos cortes): `account_known` codifica "já fechou". Confirmado por data-engineer e por H3 (taxa plana por idade, Spearman 0,025). Entra só em `confidence` e `reasons`. |
| Zumbi (`days_in_engaging` > 138) é **classe**, não ponto na curva | 0 de 679 zumbis-em-T fecharam depois; curva de sobrevivência tem n=0 para d ≥ 140. |
| Urgência = hazard de Won em 14 dias por idade | Único componente temporal derivável do histórico sem leakage; peso 40 é o mínimo que mantém Spearman(score, preço) < 0,9. |
| Razão `close_value/sales_price` por produto | Mediana 0,967–1,004: **quase não altera** o valor. Mantida por honestidade (é o estimador correto) e porque é barata; se simplificar, usar 1,0 e dizer. |
| Camada 2 (LR) em **modo sombra**, peso 0 no blend | Nenhum conjunto de features bate a taxa-base (AUC-ROC 0,45–0,51; Brier pior). `20_model_candidates.md`. |

## 1. Entradas (gold, particionadas por `as_of`)

Ler de `solution/data/gold/` (manifests `_manifest.json`). Colunas usadas pelo scoring:

| Tabela | Coluna | Uso |
|---|---|---|
| `opportunity_features/as_of=T` | `opportunity_id, sales_agent, manager, regional_office, product, account, sector, sales_price, deal_stage, days_in_engaging, account_known, open_load` | features + explicação. `days_in_engaging` = `T − engage_date`; nulo em Prospecting. `open_load` = deals abertos do agente em T. `revenue, employees, subsidiary_of` só para `reasons`. |
| `history_stats/as_of=T` | `p0`; `by_product(product, n, k)`; `by_agent`; `by_agent_product`; `by_sector`; `by_account`; `value_ratio(product, ratio)`; `survival(d, n_alive, won_alive)`; `hazard14(d, hazard)` | tudo com `close_date ≤ T`. Se `hazard14` não existir na gold, calcular no driver a partir dos fechados ≤ T (fórmula em §3.4) e pedir ao data-engineer para materializar. |
| `labels/as_of=T` | `opportunity_id, label, realized_value` | **só** em `train`/`evaluate`; nunca lido pelo `score`. |

**Lista fechada de features preditivas** (`ml/features.py`, testada): `product` (one-hot), `product_rate`, `log_days`, `is_zombie`, `log_price`, `open_load`, `survival_rate`. Proibidas: `account_known`, `sector`, `revenue`, `employees`, `subsidiary_of`, `account_*_rate`, `engage_month*`, `close_*`, `outcome_*`, `label`. Teste: `assert set(FEATURES) ∩ FORBIDDEN == ∅`.

## 2. Constantes (`scoring/weights.py`)

```python
PRIOR_A = 20.0            # pseudo-contagem do prior bayesiano
ZOMBIE_DAYS = 138         # ciclo máximo observado (Won e Lost)
ZOMBIE_P_FACTOR = 0.5     # convenção, não estimativa (nunca houve fechamento > 138 d)
ZOMBIE_URGENCY = 0.2
ZOMBIE_SCORE_CAP = 49.0
PROSPECTING_URGENCY = 0.5 # "desconhecida", não zero
W_P, W_V, W_U = 25.0, 35.0, 40.0   # somam 100
P_SCALE_LO, P_SCALE_HI = 0.30, 0.80
MAX_LIST_PRICE = 26768.0  # GTK 500
HIGH_TICKET_PRICE, LOW_TICKET_PRICE = 4000.0, 600.0
MIN_GROUP_N = 30          # abaixo disso a evidência do grupo é "pequena"
OVERLOAD_QUANTILE = 0.75
TIER_A, TIER_B, TIER_C = 75.0, 55.0, 35.0
BLEND_MODEL_WEIGHT = 0.0  # camada 2 em sombra
```

## 3. Regras (funções puras; uma regra → um reason code)

Notação: `smooth(k, n, p0) = (k + PRIOR_A·p0) / (n + PRIOR_A)`; `logit`, `sigmoid` usuais.

### 3.1 `p_win_rules(product, days_in_engaging, hist) -> (p_win, reasons)`
```
p_prod = smooth(k_prod, n_prod, p0)              # PRODUCT_BASE_RATE (+), weight = W_P·p_scaled (pontos), n = n_prod
is_zombie = days_in_engaging is not null and days_in_engaging > ZOMBIE_DAYS
p_win = p_prod * (ZOMBIE_P_FACTOR if is_zombie else 1.0)
```
Reasons adicionais, **todos informativos (direção `i`, não alteram p_win)**, com o número e o `n` no texto:
- `AGENT_TRACK_RECORD`: `smooth(k_agent, n_agent, p0)` vs `p0`.
- `AGENT_PRODUCT_FIT`: `smooth(k_ap, n_ap, p0)` vs taxa do agente; texto avisa "amostra pequena" se `n_ap < MIN_GROUP_N`.
- `SECTOR_FIT` (só com conta), `ACCOUNT_SIZE` (só com conta), `ACCOUNT_HISTORY` (só com conta e `n_account ≥ 1`).
- `ACCOUNT_UNKNOWN` (sem conta).
- `SURVIVAL_POSITIVE` (vivo): `survival[d]` vs `p0`; se `d > 120`, texto acrescenta "faltam {138−d} dias para o ciclo máximo".
- `ZOMBIE_RISK` (direção `-`, weight = `(W_P / (P_SCALE_HI − P_SCALE_LO)) · (p_win − p_prod)` = `50·(p_win − p_prod)` pontos, ex. −15,4 para GTK 500; n = d).
- `URGENCY_WINDOW` (direção `+`, weight = `W_U · urgency` pontos: vivo 0–40, Prospecting 20, zumbi 8). **Código novo — estender o enum `ReasonCode`.**
- `PROSPECTING_NO_TIMELINE` (Prospecting).
- `AGENT_OVERLOAD` (i) se `open_load ≥ quantil 0,75 da carga em T`.

### 3.2 `expected_value(sales_price, product, p_win, hist) -> (ev, ev_gross, reason)`
```
ratio = value_ratio[product]  (fallback 1.0)
ev_gross = sales_price * ratio
ev = ev_gross * p_win
value_norm = log1p(ev_gross) / log1p(MAX_LIST_PRICE)      # 0,39 (MG Special) … 1,0 (GTK 500)
HIGH_TICKET (+) se sales_price ≥ 4000 ; LOW_TICKET (−) se ≤ 600 ; weight = W_V * value_norm (pontos)
```

### 3.3 `urgency(days_in_engaging, hist) -> (urgency, reason?)`
```
Prospecting        -> PROSPECTING_URGENCY
zumbi              -> ZOMBIE_URGENCY
vivo (d ≤ 138)     -> hazard14[d] / max(hazard14)
```
`hazard14[d] = #{fechados ≤ T : d < cycle ≤ d+14 e Won} / #{fechados ≤ T : cycle > d}`, definido para `n_alive ≥ 30`, forward-fill acima. É "a chance de este deal virar Won nas próximas duas semanas, dada a idade".

### 3.4 `priority_score(p_win, value_norm, urgency, is_zombie) -> float`
```
p_scaled = clip((p_win − 0.30) / 0.50, 0, 1)
score = W_P·p_scaled + W_V·value_norm + W_U·urgency
if is_zombie: score = min(score, ZOMBIE_SCORE_CAP)
score = clip(score, 0, 100)
```
**Unidade única de `Reason.weight`: pontos de `priority_score` (0–100), para todo código** (`docs/ml-pipeline.md` §2.3). `HIGH_TICKET = 35·value_norm`; `LOW_TICKET = −(35 − 35·value_norm)`; `PRODUCT_BASE_RATE = 25·p_scaled`; `URGENCY_WINDOW = 40·urgency`; `ZOMBIE_RISK = 50·(p_win − p_prod)`; informativos = 0 com direção `i`. Invariante: `PRODUCT_BASE_RATE + ZOMBIE_RISK + HIGH/LOW_TICKET (ou 35·value_norm) + URGENCY_WINDOW ≈ priority_score` antes do cap de zumbi. A saída também carrega `score_breakdown = {probability: 25·p_scaled, value: 35·value_norm, urgency: 40·urgency, cap_applied: bool}` para a UI mostrar a composição sem recomputar. A UI exibe o peso bruto com sinal — nunca multiplica por 100.

### 3.5 `confidence(account_known, deal_stage, is_zombie, n_agent, n_prod) -> alta|media|baixa`
```
baixa  se is_zombie or (deal_stage == Prospecting and not account_known) or n_agent < 30 or n_prod < 30
media  se not account_known or deal_stage == Prospecting
alta   caso contrário
```

### 3.6 `tier(score, confidence)` (absoluto; a UI também mostra quartis do recorte)
```
A ≥ 75, B ≥ 55, C ≥ 35, senão D ; A com confidence == baixa → B
```

### 3.7 `next_action` (template por situação)
| Situação | Texto |
|---|---|
| vivo, d ≤ 120, tier A/B | "Ligar esta semana e propor data de fechamento." |
| vivo, 120 < d ≤ 138 | "Faltam {138−d} dias para o ciclo máximo já visto: fechar ou desistir esta semana." |
| zumbi | "Confirmar com o cliente se a oportunidade existe; se não, marcar Lost e limpar o pipeline." |
| Prospecting sem conta | "Registrar conta e data de engajamento no CRM antes de priorizar." |
| Prospecting com conta | "Agendar primeiro contato e registrar engage_date." |

## 4. Fila de zumbis ("Decidir / limpar")

No snapshot: **1.291 deals, R$ 3.185.056 de valor nominal** (preço × razão), R$ 998 mil "esperado" com o fator 0,5 — número que **não** deve ser somado ao forecast. Comparação: os 298 Engaging vivos somam R$ 692.670 nominais. Por manager: Celia Rouche R$ 842 mil (257), Summer Sewald R$ 718 mil (305), Melvin Marxen R$ 535 mil (213), Rocco Neubert R$ 437 mil (157), Cara Losch R$ 372 mil (169), Dustin Brinkmann R$ 282 mil (190). Picos de `engage_month` 2017-07 (402) e 2017-08 (173): lote nunca atualizado.

Comportamento especificado:
- `ZOMBIE_RISK` sempre presente; `urgency = 0,2` constante (a urgência de um zumbi é administrativa, não comercial); `score ≤ 49` → tiers C/D.
- **Dentro da fila** o score já ordena por valor nominal (Spearman = 1,0). Desempate obrigatório: `days_in_engaging` **crescente** (zumbi mais novo primeiro — mais provável de ainda existir). Implementar como `ORDER BY priority_score DESC, days_in_engaging ASC`.
- A UI exibe a fila separada do "pipeline vivo", com o valor nominal em risco por manager, e um CTA "confirmar ou marcar Lost". Feedback do vendedor (`POST /feedback`) alimenta `data/feedback/actions` para, num ciclo futuro, calibrar `ZOMBIE_P_FACTOR` com dados reais.
- Alternativa avaliada e rejeitada: decaimento contínuo de `p_win` com a idade acima de 138 d — não há dados para ajustar a forma; um fator fixo declarado como convenção é mais honesto.

## 5. Camada 2 — LogisticRegression em sombra

- **Frame de treino temporal** (não `randomSplit`): para cada fim de mês `m` de 2017-03-31 até `T − 1 mês`, linhas = deals abertos em `m` cujo desfecho é conhecido até `T`; features com `history_stats/as_of=m`; label de `labels/as_of=m` filtrado por `close_date ≤ T`. Viés conhecido: cortes recentes só têm deals rápidos (taxa de Won do treino 0,68 vs 0,60–0,63 no teste) → calibrar por `IsotonicRegression` no corte de validação **ou** reponderar por mês; documentar no model card.
- **Pipeline Spark ML**: `StringIndexer(product, handleInvalid="keep") → OneHotEncoder → VectorAssembler(FEATURES) → StandardScaler → LogisticRegression(elasticNetParam=0.5, regParam=0.1, maxIter=200)`; seed fixa.
- **Blend**: `p_win = (1 − BLEND_MODEL_WEIGHT)·p_rules + BLEND_MODEL_WEIGHT·p_model`, com `BLEND_MODEL_WEIGHT = 0.0`. Promoção só se, em **ambos** os cortes, `AUC-PR(model) ≥ AUC-PR(taxa-base) + 0,02` **e** `Brier(model) ≤ Brier(taxa-base)` após calibração. Aí `MODEL_CONTRIBUTION` entra em `reasons` com `coef × valor padronizado` (exato).
- **GBT**: não testado (sem biblioteca aqui). Plano: `GBTClassifier(maxDepth=3, maxIter=50, seed)` + isotônica; mesma regra de promoção **e** margem > 0,02 sobre a LR. Expectativa declarada: não vai passar — as features não carregam sinal.
- **PSI** por feature (treino vs lote) no manifesto; alarme > 0,2. **Esperar alarme em `account_known`** se alguém o incluir — é o sintoma do vazamento descrito em §0, não um drift real.

## 6. Invariantes (testes obrigatórios em `tests/test_scoring_rules.py`)

1. `priority_score` não-decrescente em `sales_price`, tudo o mais constante (inclui zumbis dentro do cap).
2. `days_in_engaging > 138` ⇒ `ZOMBIE_RISK ∈ reasons`, `tier ∈ {C, D}`, `urgency == 0.2`, `p_win == p_prod × 0.5`.
3. `account_known == False` ⇒ `confidence != "alta"` e `ACCOUNT_UNKNOWN ∈ reasons`.
4. `deal_stage == Prospecting` ⇒ `days_in_engaging is None`, `urgency == 0.5`, `PROSPECTING_NO_TIMELINE ∈ reasons`; sem conta ⇒ `tier != A`.
5. Nenhum deal aberto sem linha em `scores`; nenhum `NaN`; `0 ≤ score ≤ 100`; `0 ≤ p_win ≤ 1`; `len(reasons) ≥ 1`.
6. `Spearman(priority_score, sales_price) < 0,9` no lote pontuado (snapshot: 0,46; frames de backtest: 0,54 / 0,50).
7. Determinismo: duas execuções ⇒ parquet idêntico (hash).
8. Point-in-time: `score(as_of=T)` só lê partições `as_of=T`; teste que injeta um fechamento com `close_date > T` no histórico e verifica que a saída não muda.
9. `set(FEATURES) ∩ FORBIDDEN == ∅`; `account_known` nunca no vetor do modelo.
10. `p_win` de um produto com `n=0` no histórico = `p0` (prior puro).
11. Todos os `code` em `reasons` pertencem ao enum `ReasonCode`; `text_pt` contém pelo menos um dígito (o número que justifica).

## 7. Avaliação e aceite (`jobs/evaluate --as-of T`, T ∈ {2017-06-30, 2017-09-30})

Reproduzir a tabela de `10_backtest.md` com bootstrap (2.000 reamostras, seed fixa). Limiares de aceite — o pipeline **falha** se qualquer um não for atendido:

| Métrica (deals abertos em T com desfecho) | Aceite | Referência obtida |
|---|---|---|
| Brier(`p_win`) | ≤ 0,245 em ambos os cortes | 0,235 / 0,243 |
| Erro médio absoluto de calibração (5 bins) | ≤ 0,06 | 0,01–0,06 |
| Receita realizada no top 20% por `priority_score` | ≥ 1,5× aleatório (IC inferior > aleatório) | 0,377 / 0,359 vs 0,204 / 0,206 |
| Spearman(`priority_score`, `sales_price`) | < 0,9 | 0,54 / 0,50 |
| Zumbis-em-T que fecharam depois | reportar; esperado 0 | 0 / 0 |
| AUC-PR(`p_win`) vs aleatório | **não há aceite** — reportar com IC e dizer que empata | 0,651 / 0,605 vs 0,664 / 0,619 |

Baselines obrigatórios na tabela: aleatório, `sales_price`, **`sales_price` excluindo > 138 d** (preço só entre deals vivos — isola quanto do ganho de "ordenar por preço" depende de ignorar os parados), mais novo primeiro, mais antigo primeiro, taxa-base por produto. Sensibilidade: censurados = Lost (reportar à parte; ali "mais novo primeiro" sobe para AUC-ROC 0,73–0,83 **por causa dos zumbis** — dizer isso).

## 8. `models/<version>/metrics.json` (contrato para a UI "Qualidade do modelo")

```json
{
  "model_version": "2017-12-31-rules-v1",
  "as_of": "2017-12-31",
  "cuts": ["2017-06-30", "2017-09-30"],
  "summary": {
    "coverage": 2089, "prospecting_count": 500, "zombie_count": 1291,
    "account_known_rate": 0.32,
    "mean_calibration_error": 0.04,
    "spearman_score_price": 0.46
  },
  "backtest": {
    "2017-09-30": {
      "n_open": 2409, "n_labeled": 935, "n_censored": 1474, "base_rate": 0.598,
      "brier": 0.243, "auc_pr": 0.605, "auc_pr_ci": [0.558, 0.649], "auc_roc": 0.495,
      "lift_top_decile": 1.14,
      "precision_at_10": 0.560, "precision_at_10_ci": [0.51, 0.61],
      "precision_at_25": 0.552,
      "revenue_capture_top20": 0.359, "revenue_capture_top20_ci": [0.305, 0.398],
      "calibration_bins": [
        {"bin": 0, "p_low": 0.60, "p_high": 0.62, "predicted": 0.612, "actual": 0.588, "count": 187}
      ]
    }
  },
  "baselines": {
    "random":    {"2017-09-30": {"precision_at_10": 0.603, "precision_at_10_ci": [0.55, 0.65], "auc_pr": 0.619, "revenue_capture_top20": 0.206, "lift_top_decile": 1.16}},
    "newest":    {"2017-09-30": {"precision_at_10": 0.547, "precision_at_10_ci": [0.50, 0.60], "auc_pr": 0.581, "revenue_capture_top20": 0.194}},
    "price":     {"2017-09-30": {"precision_at_10": 0.577, "precision_at_10_ci": [0.53, 0.63], "auc_pr": 0.593, "revenue_capture_top20": 0.459}},
    "base_rate": {"2017-09-30": {"precision_at_10": 0.557, "precision_at_10_ci": [0.51, 0.61], "auc_pr": 0.605, "revenue_capture_top20": 0.006}}
  }
}
```
Chaves por corte sob `backtest[cut]` (scorer) e `baselines[name][cut]`; ICs como `*_ci: [lo, hi]`. `precision_at_10` é a média por vendedor com ≥ 10 deals abertos em T. Os números acima são os do protótipo pandas (`docs/figures/10_backtest.md`) e **diferem na 2ª–3ª casa** dos de `solution/models/latest/metrics.json` por semente do bootstrap e ordem de desempate (as linhas no Spark são ordenadas por `opportunity_id`; `p_win` tem muitos empates por produto). **A fonte oficial é `metrics.json`**; a doc para a Head e a tela "Qualidade" leem dele, não deste exemplo. Chaves adicionais que o pipeline grava e a UI pode usar: `baselines.price_excl_zombies[cut]`, `by_signal`, `shadow_model`, `pessimistic`, `promotion`, `acceptance`, `summary.blend_model_weight`.

## 9. Fora de escopo desta versão (registrar como questão aberta)

- ~~`QUARTER_END_WINDOW`~~ — **vetado** (`docs/revops-review.md` §3b): o Won é plano ao longo do mês; o que varia é o registro de Lost. Nenhuma regra de calendário entra no score.
- Calibração de `ZOMBIE_P_FACTOR` com feedback real (`data/feedback/actions`).
- Reponderação temporal do frame de treino da LR.
