---
name: scoring-methodology
description: Metodologia de priorização de deals do Lead Scorer — decomposição probabilidade × valor × urgência, regras anti-leakage, protocolo de backtest temporal, baselines obrigatórios, contrato de explicabilidade (reason codes) e invariantes testáveis. Use ao desenhar, implementar, revisar ou documentar qualquer parte do scoring ou da UI que o exiba.
user-invocable: false
---

# Metodologia de scoring

## Decomposição

`priority_score (0–100) = f(p_win, expected_value, urgency)` com pesos nomeados e ajustáveis (`weights.py`). Cada componente é calculável para **qualquer** deal aberto no snapshot, com `confidence` explícita.

- **p_win**: taxa de Won por produto suavizada (α=20) × 0,5 se zumbi. Agente, agente×produto, setor, conta, sobrevivência e carga **não** entram em p_win (AUC-ROC ≈ 0,5 fora do tempo): viram reason codes informativos com peso 0. `account_*` é proibido como feature preditiva (artefato temporal). Camada 2 (LR) roda em modo sombra com peso 0 até provar AUC-PR ≥ taxa-base + 0,02 e Brier ≤ em ambos os cortes.
- **expected_value**: `sales_price × razão mediana close_value/sales_price dos Won daquele produto × p_win`. Nunca `close_value` do próprio deal.
- **urgency**: onde a ação do vendedor muda o desfecho. hazard empírico de Won nos próximos 14 dias dado a idade (`hazard14(d)`, materializado em `history_stats`); zumbi (> 138 dias) = 0,2 constante e fila separada "Decidir/limpar"; Prospecting = 0,5 com reason code próprio. Pesos default (spec): `priority_score = 25·p̂ + 35·log-valor + 40·urgência`; urgência ≥ 40 é o mínimo que mantém Spearman(score, preço) < 0,9.
- **tier**: A/B/C/D por quantis do `priority_score` dentro do recorte exibido (vendedor vê seus próprios quartis) e absoluto (para manager).

## Implementação

Camada 1 (regras) em expressões Spark SQL/pandas puras e testadas; camada 2 em Spark ML Pipeline (ver skill `spark-ml-practices`). O resultado final é o parquet `gold/scores/as_of=…` que a UI consome sem Spark.

## Regras anti-leakage (bloqueantes)

1. Nenhuma coluna `outcome_*`, `close_value`, `close_date` entra em features ou regras. Teste automatizado garante.
2. Estatísticas históricas usam apenas deals fechados com `close_date ≤ as_of`. Função única: `compute_history(closed_df, as_of)`.
3. Nada de `now()/today()`. Tempo = `SNAPSHOT_DATE` ou `as_of` do backtest.
4. Split temporal, nunca aleatório: `randomSplit`, `CrossValidator` e `TrainValidationSplit` são proibidos.

## Protocolo de backtest

Para `T ∈ {2017-06-30, 2017-09-30}` (mínimo):
1. `history = compute_history(closed[close_date ≤ T], as_of=T)`.
2. `open_T` = deals com `engage_date ≤ T` e (`close_date > T` ou aberto no snapshot). Para Prospecting não há data: reportar separadamente ou excluir do backtest, e dizer isso.
3. Pontuar `open_T`; avaliar com o desfecho real posterior.
4. Métricas: precision@10/@25 por agente, lift do top decil vs. taxa-base, receita real capturada no top 20% por score, Brier score e curva de calibração em 5 bins.
5. **Baselines obrigatórios**: aleatório, ordenar por `sales_price`, ordenar por idade (mais novo primeiro), taxa-base por produto. Se o scorer não bater todos com margem, dizer isso na documentação e simplificar.

## Contrato de explicabilidade

Saída por deal (`ScoredDeal`):
`opportunity_id, sales_agent, manager, regional_office, product, account, deal_stage, days_in_engaging, priority_score, tier, p_win, expected_value, urgency, confidence (alta/média/baixa), reasons: list[Reason], next_action`.
`Reason = {code, direction (+/−/i), weight, text_pt}`. Texto na voz do vendedor, com o número que o justifica: "78 dias em Engaging: acima da mediana de fechamento deste produto (57). Agir esta semana." Códigos mínimos: `PRODUCT_BASE_RATE, AGENT_TRACK_RECORD, AGENT_PRODUCT_FIT, SECTOR_FIT, ACCOUNT_SIZE, ACCOUNT_HISTORY, ACCOUNT_UNKNOWN, SURVIVAL_POSITIVE, ZOMBIE_RISK, HIGH_TICKET, LOW_TICKET, PROSPECTING_NO_TIMELINE, AGENT_OVERLOAD`.

## Invariantes (testar)

- Score monotônico não-decrescente em `sales_price`, tudo o mais constante.
- Deal com `days_in_engaging > 138` nunca no tier A; recebe `ZOMBIE_RISK`.
- `account_known = False` ⇒ `confidence != alta` e reason `ACCOUNT_UNKNOWN` presente.
- Nenhum deal aberto sem score; nenhum `NaN` em `priority_score`.
- Correlação de Spearman entre `priority_score` e `sales_price` < 0,9 (senão é "ordenar por valor" disfarçado).
- Determinismo: duas execuções ⇒ saídas idênticas.
