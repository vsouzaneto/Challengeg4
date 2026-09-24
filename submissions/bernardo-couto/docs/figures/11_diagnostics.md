## Regras padrão vs simplificadas

| variante | T | AUC-PR p_win | Brier p_win | AUC-ROC score | receita top20% (score) | IC95 | Spearman(score,preço) |
|---|---|---|---|---|---|---|---|
| padrão (agente + agente×produto + sobrevivência) | 2017-06-30 | 0.651 | 0.235 | 0.461 | 0.377 | [0.321, 0.430] | 0.793 |
| padrão (agente + agente×produto + sobrevivência) | 2017-09-30 | 0.605 | 0.243 | 0.441 | 0.359 | [0.305, 0.398] | 0.772 |
| padrão (agente + agente×produto + sobrevivência) | snapshot |  |  |  |  |  | 0.461 |
| simplificado (p_win = taxa-base do produto; zumbi penalizado) | 2017-06-30 | 0.651 | 0.235 | 0.461 | 0.377 | [0.321, 0.430] | 0.793 |
| simplificado (p_win = taxa-base do produto; zumbi penalizado) | 2017-09-30 | 0.605 | 0.243 | 0.441 | 0.359 | [0.305, 0.398] | 0.772 |
| simplificado (p_win = taxa-base do produto; zumbi penalizado) | snapshot |  |  |  |  |  | 0.461 |
| simplificado + w_p reduzido (25/50/25) | 2017-06-30 | 0.651 | 0.235 | 0.472 | 0.414 | [0.360, 0.471] | 0.930 |
| simplificado + w_p reduzido (25/50/25) | 2017-09-30 | 0.605 | 0.243 | 0.460 | 0.439 | [0.385, 0.489] | 0.929 |
| simplificado + w_p reduzido (25/50/25) | snapshot |  |  |  |  |  | 0.509 |

## Efeito fim de trimestre (diagnóstico; mês de fechamento não é feature)

| T | n | fecham em mês de fim de trimestre (%) | win rate se fecha em fim de tri | IC | win rate se fecha em outro mês | IC  |
|---|---|---|---|---|---|---|
| 2017-04-30 | 1147 | 37.663 | 0.829 | [0.79, 0.86] | 0.561 | [0.52, 0.60] |
| 2017-05-31 | 930 | 65.054 | 0.825 | [0.79, 0.85] | 0.578 | [0.52, 0.63] |
| 2017-06-30 | 970 | 29.588 | 0.808 | [0.76, 0.85] | 0.552 | [0.51, 0.59] |
| 2017-07-31 | 1139 | 37.226 | 0.795 | [0.75, 0.83] | 0.566 | [0.53, 0.60] |
| 2017-08-31 | 893 | 68.645 | 0.803 | [0.77, 0.83] | 0.518 | [0.46, 0.58] |
| 2017-09-30 | 935 | 33.262 | 0.788 | [0.74, 0.83] | 0.503 | [0.46, 0.54] |
| 2017-10-31 | 1072 | 41.978 | 0.780 | [0.74, 0.82] | 0.529 | [0.49, 0.57] |

Entre todos os fechados: 49.0% dos Won e 20.1% dos Lost fecham em mês de fim de trimestre.

## Decomposição do baseline 'mais novo primeiro'

| T | abertos | vivos (≤138 d) | zumbis (>138 d) | zumbis com desfecho depois | vivos censurados (%) | AUC-ROC 'mais novo' entre vivos com desfecho | AUC-ROC 'mais novo' entre vivos, censurado=Lost |
|---|---|---|---|---|---|---|---|
| 2017-06-30 | 1686 | 1537 | 149 | 0 | 36.890 | 0.501 | 0.691 |
| 2017-09-30 | 2409 | 1879 | 530 | 0 | 50.239 | 0.495 | 0.766 |

## Grade de pesos (regras simplificadas)

| w_p/w_v/w_u | Spearman 2017-06-30 | receita top20% 2017-06-30 | P@10 agente 2017-06-30 | Spearman 2017-09-30 | receita top20% 2017-09-30 | P@10 agente 2017-09-30 | Spearman snapshot | tier A snapshot |
|---|---|---|---|---|---|---|---|---|
| 45/35/20 | 0.933 | 0.431 | 0.637 | 0.898 | 0.456 | 0.580 | 0.475 | 31 |
| 30/40/30 | 0.890 | 0.404 | 0.610 | 0.870 | 0.399 | 0.577 | 0.474 | 51 |
| 25/35/40 | 0.793 | 0.377 | 0.627 | 0.772 | 0.359 | 0.560 | 0.461 | 67 |
| 20/30/50 | 0.688 | 0.297 | 0.613 | 0.656 | 0.311 | 0.543 | 0.460 | 69 |
| 30/30/40 | 0.753 | 0.336 | 0.620 | 0.715 | 0.344 | 0.547 | 0.443 | 67 |

## Fila de zumbis no snapshot (valor nominal em risco)

| fila | n | valor nominal (preço × razão) | valor esperado (× p_win) | idade mediana | com conta (%) |
|---|---|---|---|---|---|
| zumbis (> 138 d) | 1291 | 3185056 | 998152 | 201 | 32 |
| Engaging vivos (≤ 138 d) | 298 | 692670 | 437246 | 104 | 30 |

Por manager:

| manager | n | valor_nominal | idade_mediana |
|---|---|---|---|
| Celia Rouche | 257 | 842070 | 256 |
| Summer Sewald | 305 | 717950 | 257 |
| Melvin Marxen | 213 | 534699 | 157 |
| Rocco Neubert | 157 | 436512 | 248 |
| Cara Losch | 169 | 372174 | 248 |
| Dustin Brinkmann | 190 | 281650 | 157 |

Por mês de engajamento:

| engage_month | n |
|---|---|
| 2016-11 | 13 |
| 2016-12 | 40 |
| 2017-01 | 65 |
| 2017-02 | 95 |
| 2017-03 | 137 |
| 2017-04 | 121 |
| 2017-05 | 134 |
| 2017-06 | 111 |
| 2017-07 | 402 |
| 2017-08 | 173 |

Dentro da fila o score ordena por valor (Spearman(score, valor nominal) = 1.000); a idade não entra (Spearman(score, idade) = 0.056). Proposta: desempate por idade crescente (zumbi mais novo primeiro), porque é o mais provável de ainda existir.
