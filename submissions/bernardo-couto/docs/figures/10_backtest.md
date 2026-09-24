## Corte T = 2017-06-30

Abertos em T: 1686 · com desfecho até o snapshot: 970 (taxa-base 0.628) · censurados (ainda abertos em 2017-12-31): 716 · zumbis (> 138 d) em T: 149 · Spearman(priority_score, sales_price) = 0.540

| candidato | AUC-PR | AUC-PR IC95 | AUC-ROC | Brier | lift top decil | P@10/agente | P@25/agente | receita top 20% | receita IC95 |
|---|---|---|---|---|---|---|---|---|---|
| aleatório | 0.664 | [0.621, 0.706] | 0.530 |  | 1.149 | 0.660 | 0.634 | 0.204 | [0.169, 0.244] |
| sales_price | 0.634 | [0.593, 0.678] | 0.492 |  | 1.117 | 0.643 | 0.615 | 0.505 | [0.453, 0.550] |
| mais novo primeiro | 0.619 | [0.577, 0.661] | 0.501 |  | 0.936 | 0.603 | 0.619 | 0.175 | [0.143, 0.212] |
| mais antigo primeiro | 0.616 | [0.574, 0.662] | 0.499 |  | 0.920 | 0.627 | 0.625 | 0.160 | [0.130, 0.194] |
| taxa-base por produto | 0.651 | [0.612, 0.697] | 0.533 | 0.235 | 1.067 | 0.677 | 0.642 | 0.250 | [0.199, 0.303] |
| regras · p_win | 0.651 | [0.612, 0.697] | 0.533 | 0.235 | 1.067 | 0.677 | 0.642 | 0.250 | [0.199, 0.303] |
| regras · expected_value | 0.634 | [0.593, 0.678] | 0.492 |  | 1.117 | 0.643 | 0.615 | 0.505 | [0.453, 0.550] |
| regras · priority_score | 0.601 | [0.562, 0.645] | 0.461 |  | 0.936 | 0.627 | 0.602 | 0.377 | [0.321, 0.430] |

Calibração (5 bins) · regras p_win:

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 194.000 | 0.654 | 0.582 | -0.072 |
| 1.000 | 194.000 | 0.664 | 0.624 | -0.040 |
| 2.000 | 194.000 | 0.668 | 0.608 | -0.060 |
| 3.000 | 194.000 | 0.671 | 0.644 | -0.026 |
| 4.000 | 194.000 | 0.676 | 0.680 | 0.005 |

Calibração (5 bins) · taxa-base por produto:

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 194.000 | 0.654 | 0.582 | -0.072 |
| 1.000 | 194.000 | 0.664 | 0.624 | -0.040 |
| 2.000 | 194.000 | 0.668 | 0.608 | -0.060 |
| 3.000 | 194.000 | 0.671 | 0.644 | -0.026 |
| 4.000 | 194.000 | 0.676 | 0.680 | 0.005 |

Sensibilidade pessimista (censurados tratados como Lost):

| candidato | AUC-PR (censurado=Lost) | AUC-ROC |
|---|---|---|
| aleatório | 0.362 | 0.503 |
| sales_price | 0.324 | 0.484 |
| mais novo primeiro | 0.522 | 0.734 |
| mais antigo primeiro | 0.249 | 0.266 |
| taxa-base por produto | 0.342 | 0.526 |
| regras · p_win | 0.382 | 0.594 |
| regras · expected_value | 0.346 | 0.509 |
| regras · priority_score | 0.296 | 0.424 |

## Corte T = 2017-09-30

Abertos em T: 2409 · com desfecho até o snapshot: 935 (taxa-base 0.598) · censurados (ainda abertos em 2017-12-31): 1474 · zumbis (> 138 d) em T: 530 · Spearman(priority_score, sales_price) = 0.501

| candidato | AUC-PR | AUC-PR IC95 | AUC-ROC | Brier | lift top decil | P@10/agente | P@25/agente | receita top 20% | receita IC95 |
|---|---|---|---|---|---|---|---|---|---|
| aleatório | 0.619 | [0.577, 0.666] | 0.525 |  | 1.157 | 0.603 | 0.604 | 0.206 | [0.168, 0.247] |
| sales_price | 0.593 | [0.549, 0.637] | 0.478 |  | 0.996 | 0.577 | 0.590 | 0.459 | [0.434, 0.529] |
| mais novo primeiro | 0.581 | [0.544, 0.630] | 0.495 |  | 0.979 | 0.547 | 0.596 | 0.194 | [0.157, 0.233] |
| mais antigo primeiro | 0.579 | [0.541, 0.625] | 0.505 |  | 0.872 | 0.537 | 0.610 | 0.175 | [0.137, 0.211] |
| taxa-base por produto | 0.605 | [0.558, 0.649] | 0.495 | 0.243 | 1.139 | 0.557 | 0.585 | 0.006 | [0.005, 0.017] |
| regras · p_win | 0.605 | [0.558, 0.649] | 0.495 | 0.243 | 1.139 | 0.557 | 0.585 | 0.006 | [0.005, 0.017] |
| regras · expected_value | 0.593 | [0.549, 0.637] | 0.478 |  | 0.996 | 0.577 | 0.590 | 0.459 | [0.434, 0.529] |
| regras · priority_score | 0.565 | [0.525, 0.612] | 0.441 |  | 0.979 | 0.560 | 0.552 | 0.359 | [0.305, 0.398] |

Calibração (5 bins) · regras p_win:

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 187.000 | 0.619 | 0.561 | -0.058 |
| 1.000 | 187.000 | 0.642 | 0.642 | -0.001 |
| 2.000 | 187.000 | 0.645 | 0.615 | -0.030 |
| 3.000 | 187.000 | 0.655 | 0.535 | -0.120 |
| 4.000 | 187.000 | 0.658 | 0.636 | -0.022 |

Calibração (5 bins) · taxa-base por produto:

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 187.000 | 0.619 | 0.561 | -0.058 |
| 1.000 | 187.000 | 0.642 | 0.642 | -0.001 |
| 2.000 | 187.000 | 0.645 | 0.615 | -0.030 |
| 3.000 | 187.000 | 0.655 | 0.535 | -0.120 |
| 4.000 | 187.000 | 0.658 | 0.636 | -0.022 |

Sensibilidade pessimista (censurados tratados como Lost):

| candidato | AUC-PR (censurado=Lost) | AUC-ROC |
|---|---|---|
| aleatório | 0.234 | 0.508 |
| sales_price | 0.198 | 0.485 |
| mais novo primeiro | 0.488 | 0.833 |
| mais antigo primeiro | 0.140 | 0.167 |
| taxa-base por produto | 0.202 | 0.500 |
| regras · p_win | 0.261 | 0.637 |
| regras · expected_value | 0.230 | 0.526 |
| regras · priority_score | 0.216 | 0.517 |

## Variantes de pesos da camada de regras (p_win)

| variante | AUC-PR 2017-06-30 | Brier 2017-06-30 | AUC-PR 2017-09-30 | Brier 2017-09-30 |
|---|---|---|---|---|
| só produto (recomendado) | 0.651 | 0.235 | 0.605 | 0.243 |
| produto + sobrevivência | 0.646 | 0.240 | 0.602 | 0.249 |
| produto + agente | 0.652 | 0.235 | 0.587 | 0.244 |
| produto + agente + sobrevivência | 0.656 | 0.240 | 0.598 | 0.250 |
| produto + agente + agente×produto + sobrevivência | 0.621 | 0.243 | 0.605 | 0.251 |
| anterior + setor | 0.616 | 0.243 | 0.600 | 0.252 |
| sobrevivência ×2 | 0.624 | 0.250 | 0.612 | 0.260 |

## Cortes mensais (AUC-PR, estabilidade)

| T | n | taxa-base | regras p_win | mais novo | mais antigo | produto | preço |
|---|---|---|---|---|---|---|---|
| 2017-04-30 | 1147 | 0.662 | 0.637 | 0.675 | 0.646 | 0.637 | 0.687 |
| 2017-05-31 | 930 | 0.739 | 0.750 | 0.712 | 0.791 | 0.750 | 0.757 |
| 2017-06-30 | 970 | 0.628 | 0.651 | 0.619 | 0.616 | 0.651 | 0.634 |
| 2017-07-31 | 1139 | 0.651 | 0.652 | 0.659 | 0.626 | 0.652 | 0.661 |
| 2017-08-31 | 893 | 0.713 | 0.712 | 0.694 | 0.757 | 0.712 | 0.732 |
| 2017-09-30 | 935 | 0.598 | 0.605 | 0.581 | 0.579 | 0.605 | 0.593 |
| 2017-10-31 | 1072 | 0.634 | 0.633 | 0.658 | 0.592 | 0.633 | 0.619 |

## Snapshot 2017-12-31 · o que o vendedor veria

| deal_stage | is_zombie | n | p_win_mean | score_mean | ev_sum |
|---|---|---|---|---|---|
| Engaging | False | 298 | 0.63 | 62.51 | 437245.55 |
| Engaging | True | 1291 | 0.32 | 32.48 | 998152.00 |
| Prospecting | False | 500 | 0.63 | 59.73 | 673820.71 |

Tiers absolutos (A ≥ 75, B ≥ 55, C ≥ 35):

| tier | n | score_min | score_max | zombies | prospecting |
|---|---|---|---|---|---|
| A | 67 | 75.6 | 85.9 | 0 | 0 |
| B | 516 | 55.2 | 74.7 | 0 | 380 |
| C | 771 | 35.9 | 54.8 | 563 | 120 |
| D | 735 | 23.0 | 34.8 | 728 | 0 |

Confiança:

| confidence | n |
|---|---|
| baixa | 1629 |
| media | 372 |
| alta | 88 |

Spearman(priority_score, sales_price) = 0.461; scores NaN: 0.

## Deals-exemplo (snapshot)

| opportunity_id | sales_agent | product | account | deal_stage | days_in_engaging | p_win | expected_value | urgency | priority_score | tier | confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 059K86LU | Kami Bicknell | GTX Plus Pro | Labdrill | Engaging | 127.00 | 0.64 | 3536.52 | 0.98 | 85.93 | A | alta |
| A04V2WB3 | Elease Gluck | GTK 500 |  | Engaging | 150.00 | 0.31 | 7950.38 | 0.20 | 43.24 | C | baixa |
| 73CWPT9H | Gladys Colclough | GTX Plus Pro |  | Prospecting |  | 0.64 | 3536.52 | 0.50 | 66.70 | B | baixa |

- `059K86LU`: PRODUCT_BASE_RATE(i, w=0.011, n=745, v=0.643); AGENT_TRACK_RECORD(i, w=0.008, n=272, v=0.639); AGENT_PRODUCT_FIT(i, w=0.088, n=18, v=0.727); SECTOR_FIT(i, w=-0.000, n=950, v=0.623); SURVIVAL_POSITIVE(i, w=0.153, n=127, v=0.785); HIGH_TICKET(+, w=29.570, n=0, v=5503.0)
- `A04V2WB3`: PRODUCT_BASE_RATE(i, w=-0.018, n=25, v=0.614); AGENT_TRACK_RECORD(i, w=0.003, n=126, v=0.634); AGENT_PRODUCT_FIT(i, w=-0.021, n=12, v=0.613); ACCOUNT_UNKNOWN(i, w=0.000, n=0, v=); ZOMBIE_RISK(-, w=-0.307, n=150, v=150.0); HIGH_TICKET(+, w=34.886, n=0, v=25897.0)
- `73CWPT9H`: PRODUCT_BASE_RATE(i, w=0.011, n=745, v=0.643); AGENT_TRACK_RECORD(i, w=-0.046, n=232, v=0.586); AGENT_PRODUCT_FIT(i, w=0.006, n=25, v=0.592); ACCOUNT_UNKNOWN(i, w=0.000, n=0, v=); PROSPECTING_NO_TIMELINE(i, w=0.000, n=0, v=); HIGH_TICKET(+, w=29.570, n=0, v=5503.0)
