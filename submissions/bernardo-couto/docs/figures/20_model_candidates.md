## Candidatos de modelo vs regras (AUC-PR nos deals abertos em T com desfecho)

| T | candidato | AUC-PR | IC95 | AUC-ROC | Brier |
|---|---|---|---|---|---|
| 2017-06-30 | regras · p_win | 0.651 | [0.612, 0.697] | 0.533 | 0.235 |
| 2017-06-30 | LR · só regras-features (agent, agent×prod, product, survival) | 0.607 | [0.567, 0.651] | 0.486 | 0.257 |
| 2017-06-30 | blend 0.5·regras + 0.5·(só regras-features () | 0.612 |  | 0.497 | 0.243 |
| 2017-06-30 | LR · + idade, preço, carga (sem conta) | 0.622 | [0.581, 0.666] | 0.497 | 0.254 |
| 2017-06-30 | blend 0.5·regras + 0.5·(+ idade, preço, carg) | 0.626 |  | 0.506 | 0.242 |
| 2017-06-30 | LR · + conta (PROIBIDO; só contraste) | 0.626 | [0.583, 0.671] | 0.500 | 0.254 |
| 2017-06-30 | blend 0.5·regras + 0.5·(+ conta (PROIBIDO; s) | 0.628 |  | 0.509 | 0.242 |
| 2017-06-30 | LR · + sazonalidade engage_month | 0.637 | [0.594, 0.680] | 0.509 | 0.283 |
| 2017-06-30 | blend 0.5·regras + 0.5·(+ sazonalidade engag) | 0.639 |  | 0.518 | 0.250 |
| 2017-06-30 | LR · só idade | 0.594 | [0.557, 0.640] | 0.451 | 0.256 |
| 2017-06-30 | blend 0.5·regras + 0.5·(só idade) | 0.621 |  | 0.490 | 0.242 |
| 2017-09-30 | regras · p_win | 0.605 | [0.558, 0.649] | 0.495 | 0.243 |
| 2017-09-30 | LR · só regras-features (agent, agent×prod, product, survival) | 0.589 | [0.549, 0.636] | 0.488 | 0.250 |
| 2017-09-30 | blend 0.5·regras + 0.5·(só regras-features () | 0.592 |  | 0.489 | 0.246 |
| 2017-09-30 | LR · + idade, preço, carga (sem conta) | 0.566 | [0.526, 0.610] | 0.463 | 0.249 |
| 2017-09-30 | blend 0.5·regras + 0.5·(+ idade, preço, carg) | 0.565 |  | 0.467 | 0.245 |
| 2017-09-30 | LR · + conta (PROIBIDO; só contraste) | 0.559 | [0.520, 0.602] | 0.453 | 0.250 |
| 2017-09-30 | blend 0.5·regras + 0.5·(+ conta (PROIBIDO; s) | 0.558 |  | 0.457 | 0.246 |
| 2017-09-30 | LR · + sazonalidade engage_month | 0.578 | [0.537, 0.622] | 0.480 | 0.261 |
| 2017-09-30 | blend 0.5·regras + 0.5·(+ sazonalidade engag) | 0.572 |  | 0.483 | 0.250 |
| 2017-09-30 | LR · só idade | 0.587 | [0.547, 0.633] | 0.499 | 0.250 |
| 2017-09-30 | blend 0.5·regras + 0.5·(só idade) | 0.600 |  | 0.505 | 0.246 |

## Coeficientes padronizados da LR (+ idade, preço, carga, sem conta)

| feature | 2017-06-30 | 2017-09-30 |
|---|---|---|
| agent_product_rate | -0.010 | -0.018 |
| agent_rate | -0.128 | -0.056 |
| is_zombie | 0.000 | 0.000 |
| log_days | 0.050 | 0.088 |
| log_price | 0.103 | 0.050 |
| open_load | -0.107 | -0.063 |
| product_rate | 0.008 | -0.003 |
| survival_rate | -0.299 | -0.118 |

## account_known entre deals com desfecho vs censurados (por que é proibido como feature)

| T | account_known · com desfecho | account_known · censurados |
|---|---|---|
| 2017-06-30 | 1.000 | 0.324 |
| 2017-09-30 | 1.000 | 0.316 |

## Calibração LR (+ idade, preço, carga, sem conta) · T=2017-06-30

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 194.000 | 0.718 | 0.624 | -0.094 |
| 1.000 | 194.000 | 0.748 | 0.639 | -0.109 |
| 2.000 | 194.000 | 0.767 | 0.629 | -0.138 |
| 3.000 | 194.000 | 0.787 | 0.603 | -0.184 |
| 4.000 | 194.000 | 0.812 | 0.644 | -0.168 |

## Calibração LR (+ idade, preço, carga, sem conta) · T=2017-09-30

| bin | n | p_mean | y_rate | gap |
|---|---|---|---|---|
| 0.000 | 187.000 | 0.651 | 0.615 | -0.037 |
| 1.000 | 187.000 | 0.672 | 0.631 | -0.041 |
| 2.000 | 187.000 | 0.684 | 0.610 | -0.074 |
| 3.000 | 187.000 | 0.696 | 0.620 | -0.075 |
| 4.000 | 187.000 | 0.715 | 0.513 | -0.202 |
