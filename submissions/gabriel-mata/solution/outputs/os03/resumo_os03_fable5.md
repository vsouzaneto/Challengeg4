# OS-03 — Patrocínio e validação geral

Script: `solution/analysis/os03_patrocinio_validacao.py`
Fonte: `datasets/social_media_dataset.csv` (52.214 posts; 22.314 patrocinados, 29.900 orgânicos)
Saídas: `solution/outputs/os03/` (8 arquivos .csv)

**Regras mantidas da OS-02:** faixas de seguidores (até 50K, 50–100K, 100–500K, 500K–1M); `n_hashtags` (nulo = 0), `periodo_dia` e `dia_semana` com a mesma construção; IC 95% por bootstrap percentil com 1.000 reamostragens; seed 42; a mesma divisão em duas metades (A = 26.107 / B = 26.107).

---

## Bloco 1 — Comparação justa (estratificada)

Estratos: platform × content_category × content_type × faixa_seguidores, mínimo de 30 patrocinados **e** 30 orgânicos por estrato (`bloco1_comparacao_estratificada.csv`).

**Cobertura (igual para as 3 métricas):** 240 estratos existentes, **141 usados**; 49.487 posts usados (21.174 patrocinados, 28.313 orgânicos) e **2.727 posts de fora** (5,2%).

| Métrica | Efeito geral | IC inferior | IC superior | IC exclui 1 | Metade A | Metade B | Simples (sem estratos) |
|---|---|---|---|---|---|---|---|
| taxa_engajamento | 0,999877 | 0,999429 | 1,000352 | não | 0,999728 | 1,000021 | 0,999946 |
| shares | 0,999520 | 0,998507 | 1,000535 | não | 0,999059 | 0,999958 | 0,999565 |
| comments_count | 1,000018 | 0,998796 | 1,001383 | não | 1,000150 | 0,999967 | 1,000184 |

Distribuição das razões (patrocinado / orgânico) nos 141 estratos:

| Métrica | % estratos com razão > 1 | Mínimo | p5 | Mediana | p95 | Máximo |
|---|---|---|---|---|---|---|
| taxa_engajamento | 53,19% | 0,988167 | 0,993916 | 1,000253 | 1,006637 | 1,010619 |
| shares | 46,81% | 0,979506 | 0,987602 | 0,999500 | 1,013298 | 1,029031 |
| comments_count | 46,10% | 0,970290 | 0,985417 | 0,999457 | 1,017395 | 1,037867 |

## Bloco 2 — Regressão com controles (OLS, erros robustos HC3)

n = 52.214, 46 parâmetros por modelo (`bloco2_regressao_controles.csv`).

| Métrica | Coef. is_sponsored | % da média | IC inferior | IC superior | p-valor | R² | R² ajustado | p do teste F | Nº de condição |
|---|---|---|---|---|---|---|---|---|---|
| taxa_engajamento | −0,000011 | −0,0057% | −0,000096 | 0,000073 | 0,791777 | 0,000775 | −0,000087 | 0,668108 | 17,41 |
| shares | −0,130211 | −0,0434% | −0,430394 | 0,169973 | 0,395228 | 0,000667 | −0,000195 | 0,867250 | 17,41 |
| comments_count | 0,038880 | 0,0194% | −0,205753 | 0,283513 | 0,755418 | 0,000659 | −0,000203 | 0,874329 | 17,41 |

Nenhum coeficiente de `is_sponsored` tem IC que exclua 0. R² ajustado é negativo nas 3 métricas e o teste F do modelo tem p entre 0,67 e 0,87.

## Bloco 3 — Patrocínio por faixa de seguidores

Estratos: platform × content_category (15 por faixa), mínimo de 20 patrocinados e 20 orgânicos. Em todas as 4 faixas os 15 estratos existem e os 15 foram usados (`bloco3_por_faixa_seguidores.csv`).

| Faixa | Métrica | n patroc. | n orgân. | Estratos usados | Efeito | IC inferior | IC superior | Exclui 1 | Metade A | Metade B |
|---|---|---|---|---|---|---|---|---|---|---|
| até 50K | taxa_engajamento | 1.114 | 1.450 | 15 | 1,000678 | 0,998748 | 1,002710 | não | 1,000473 | 1,000511 |
| até 50K | shares | 1.114 | 1.450 | 15 | 0,999461 | 0,994622 | 1,004346 | não | 0,998470 | 1,000602 |
| até 50K | comments_count | 1.114 | 1.450 | 15 | 1,000885 | 0,995516 | 1,006709 | não | 0,999550 | 1,002758 |
| 50–100K | taxa_engajamento | 1.109 | 1.488 | 15 | 0,999652 | 0,997929 | 1,001637 | não | 0,999561 | 0,999859 |
| 50–100K | shares | 1.109 | 1.488 | 15 | 1,000716 | 0,996660 | 1,005108 | não | 1,000309 | 1,001316 |
| 50–100K | comments_count | 1.109 | 1.488 | 15 | 1,000554 | 0,995179 | 1,005857 | não | 0,997609 | 1,003926 |
| 100–500K | taxa_engajamento | 8.967 | 12.057 | 15 | 1,000235 | 0,999584 | 1,000893 | não | 0,999754 | 1,000697 |
| 100–500K | shares | 8.967 | 12.057 | 15 | 0,999895 | 0,998273 | 1,001438 | não | 0,999412 | 1,000334 |
| 100–500K | comments_count | 8.967 | 12.057 | 15 | 1,001194 | 0,999340 | 1,003029 | não | 1,000709 | 1,001687 |
| 500K–1M | taxa_engajamento | 11.124 | 14.905 | 15 | 0,999663 | 0,999104 | 1,000275 | não | 0,999758 | 0,999571 |
| 500K–1M | shares | 11.124 | 14.905 | 15 | 0,999233 | 0,997853 | 1,000625 | não | 0,998707 | 0,999790 |
| 500K–1M | comments_count | 11.124 | 14.905 | 15 | 0,999259 | 0,997638 | 1,001096 | não | 1,000152 | 0,998341 |

Nenhum dos 12 efeitos (4 faixas × 3 métricas) tem IC que exclua 1.

## Bloco 4 — Detalhes do patrocínio (só posts patrocinados)

Índice por post = valor / média dos **posts patrocinados** da plataforma. 17 segmentos × 3 métricas = 51 linhas (`bloco4_detalhes_patrocinio.csv`). Tabela completa para `taxa_engajamento`:

| Variáveis | Segmento | n | Lift | IC inferior | IC superior | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| disclosure_type | explicit | 11.784 | 1,000213 | 0,999770 | 1,000645 | não | 1,000341 | 1,000081 | sim |
| disclosure_type | implicit | 10.530 | 0,999762 | 0,999262 | 1,000267 | não | 0,999408 | 1,000107 | não |
| disclosure_location | caption | 8.944 | 0,999664 | 0,999166 | 1,000167 | não | 0,999494 | 0,999832 | sim |
| disclosure_location | hashtags | 6.124 | 1,000329 | 0,999700 | 1,000910 | não | 1,000519 | 1,000128 | sim |
| disclosure_location | video | 7.246 | 1,000136 | 0,999625 | 1,000676 | não | 0,999881 | 1,000385 | não |
| sponsor_category | cosmetics | 3.688 | 1,000546 | 0,999746 | 1,001359 | não | 1,000361 | 1,000741 | sim |
| sponsor_category | electronics | 3.750 | 1,000007 | 0,999229 | 1,000791 | não | 0,999224 | 1,000807 | não |
| sponsor_category | fashion | 3.710 | 0,999284 | 0,998493 | 1,000077 | não | 0,999314 | 0,999255 | sim |
| sponsor_category | food | 3.846 | 1,000307 | 0,999545 | 1,001140 | não | 1,000168 | 1,000446 | sim |
| sponsor_category | gaming | 3.687 | 0,999728 | 0,998912 | 1,000557 | não | 0,999778 | 0,999677 | sim |
| sponsor_category | travel | 3.633 | 1,000121 | 0,999298 | 1,000930 | não | 1,000620 | 0,999646 | não |
| disc_type × disc_location | explicit \| caption | 4.765 | 0,999768 | 0,999085 | 1,000473 | não | 0,999864 | 0,999671 | sim |
| disc_type × disc_location | explicit \| hashtags | 3.180 | 1,000711 | 0,999888 | 1,001601 | não | 1,001302 | 1,000039 | sim |
| disc_type × disc_location | explicit \| video | 3.839 | 1,000353 | 0,999600 | 1,001150 | não | 1,000083 | 1,000616 | sim |
| disc_type × disc_location | implicit \| caption | 4.179 | 0,999546 | 0,998792 | 1,000292 | não | 0,999065 | 1,000014 | não |
| disc_type × disc_location | implicit \| hashtags | 2.944 | 0,999917 | 0,999083 | 1,000754 | não | 0,999610 | 1,000217 | não |
| disc_type × disc_location | implicit \| video | 3.407 | 0,999892 | 0,999094 | 1,000715 | não | 0,999654 | 1,000125 | não |

Nas 51 linhas (3 métricas): **nenhum IC exclui 1**; os lifts vão de 0,997955 (`implicit | video`, comments_count) a 1,001770 (`explicit | hashtags`, comments_count); as duas metades ficam do mesmo lado de 1 em 28 de 51 linhas (54,9%).

## Bloco 5 — Engajamento entregue por faixa

`engajamento` absoluto por post, por faixa × is_sponsored (`bloco5_engajamento_por_faixa.csv`).

| Faixa | Patrocinado | n | Média | IC inferior | IC superior | Mediana | p10 | p90 | Mediana engaj./seguidor |
|---|---|---|---|---|---|---|---|---|---|
| até 50K | sim | 1.114 | 2.010,84 | 2.008,21 | 2.013,48 | 2.011,0 | 1.952,3 | 2.068,0 | 0,078271 |
| até 50K | não | 1.450 | 2.009,96 | 2.007,59 | 2.012,38 | 2.009,0 | 1.951,0 | 2.071,0 | 0,079037 |
| 50–100K | sim | 1.109 | 2.010,35 | 2.007,84 | 2.012,91 | 2.011,0 | 1.952,0 | 2.069,0 | 0,026380 |
| 50–100K | não | 1.488 | 2.010,78 | 2.008,64 | 2.013,13 | 2.009,0 | 1.952,0 | 2.069,0 | 0,026737 |
| 100–500K | sim | 8.967 | 2.010,63 | 2.009,73 | 2.011,57 | 2.011,0 | 1.953,0 | 2.067,0 | 0,006732 |
| 100–500K | não | 12.057 | 2.010,02 | 2.009,20 | 2.010,79 | 2.010,0 | 1.953,0 | 2.067,0 | 0,006678 |
| 500K–1M | sim | 11.124 | 2.009,92 | 2.009,07 | 2.010,66 | 2.009,0 | 1.952,0 | 2.068,0 | 0,002675 |
| 500K–1M | não | 14.905 | 2.010,58 | 2.009,87 | 2.011,24 | 2.010,0 | 1.954,0 | 2.068,0 | 0,002677 |

## Bloco 6 — Volume patrocinado

`bloco6_volume_patrocinado.csv`

| Variável | Segmento | n total | n patrocinado | % posts patrocinados | % do engajamento vindo de patrocinados |
|---|---|---|---|---|---|
| platform | Bilibili | 10.598 | 4.453 | 42,02% | 42,01% |
| platform | Instagram | 10.423 | 4.369 | 41,92% | 41,93% |
| platform | RedNote | 10.402 | 4.521 | 43,46% | 43,47% |
| platform | TikTok | 10.296 | 4.441 | 43,13% | 43,12% |
| platform | YouTube | 10.495 | 4.530 | 43,16% | 43,15% |
| content_category | beauty | 21.023 | 8.926 | 42,46% | 42,44% |
| content_category | lifestyle | 20.761 | 8.891 | 42,83% | 42,83% |
| content_category | tech | 10.430 | 4.497 | 43,12% | 43,13% |
| content_type | image | 10.303 | 4.416 | 42,86% | 42,86% |
| content_type | mixed | 5.213 | 2.224 | 42,66% | 42,67% |
| content_type | text | 5.198 | 2.205 | 42,42% | 42,42% |
| content_type | video | 31.500 | 13.469 | 42,76% | 42,75% |
| faixa_seguidores | até 50K | 2.564 | 1.114 | 43,45% | 43,46% |
| faixa_seguidores | 50–100K | 2.597 | 1.109 | 42,70% | 42,70% |
| faixa_seguidores | 100–500K | 21.024 | 8.967 | 42,65% | 42,66% |
| faixa_seguidores | 500K–1M | 26.029 | 11.124 | 42,74% | 42,73% |
| **base** | **total** | **52.214** | **22.314** | **42,74%** | **42,73%** |

Total: 22.314 patrocinados e 29.900 orgânicos. Na base toda, 42,74% dos posts são patrocinados e respondem por 42,73% do engajamento total.

## Bloco 7 — Validação geral (modelo preditivo)

`HistGradientBoostingRegressor` (parâmetros padrão, random_state=42), validação cruzada de 5 partes (embaralhada, seed 42), comparado com `DummyRegressor` que prevê a média (`bloco7a_desempenho_modelo.csv`).

| Alvo | R² médio | R² desvio | MAE modelo | MAE modelo da média | Diferença % (MAE) |
|---|---|---|---|---|---|
| taxa_engajamento | −0,001162 | 0,000598 | 0,003882 | 0,003880 | +0,0473% |
| shares | −0,001241 | 0,000942 | 13,834531 | 13,824963 | +0,0692% |
| comments_count | −0,000807 | 0,000492 | 11,271032 | 11,265099 | +0,0527% |
| engajamento | −0,001308 | 0,000490 | 35,851408 | 35,831213 | +0,0564% |

O R² médio é negativo nos 4 alvos e o MAE do modelo é **maior** que o do modelo que sempre prevê a média, em todos os alvos (diferença de +0,05% a +0,07%).

**Importância por permutação** (teste de 20%, seed 42, 10 repetições; queda de R² ao permutar a variável — `bloco7b_importancia_permutacao.csv`). As 10 variáveis mais importantes por alvo:

| Alvo | Pos. | Variável | Queda R² média | Desvio |
|---|---|---|---|---|
| taxa_engajamento | 1 | dia_semana | 0,000529 | 0,000512 |
| taxa_engajamento | 2 | audience_age_distribution | 0,000310 | 0,000221 |
| taxa_engajamento | 3 | hora | 0,000255 | 0,000239 |
| taxa_engajamento | 4 | content_category | 0,000136 | 0,000097 |
| taxa_engajamento | 5 | follower_count | 0,000114 | 0,000214 |
| taxa_engajamento | 6 | language | 0,000099 | 0,000119 |
| taxa_engajamento | 7 | is_sponsored | 0,000038 | 0,000068 |
| taxa_engajamento | 8 | n_hashtags | −0,000011 | 0,000094 |
| taxa_engajamento | 9 | content_type | −0,000044 | 0,000191 |
| taxa_engajamento | 10 | audience_gender_distribution | −0,000107 | 0,000174 |
| shares | 1 | platform | 0,000541 | 0,000417 |
| shares | 2 | hora | 0,000379 | 0,000326 |
| shares | 3 | content_type | 0,000212 | 0,000483 |
| shares | 4 | n_hashtags | 0,000045 | 0,000219 |
| shares | 5 | audience_age_distribution | 0,000012 | 0,000258 |
| shares | 6 | language | −0,000073 | 0,000215 |
| shares | 7 | is_sponsored | −0,000114 | 0,000176 |
| shares | 8 | content_length | −0,000118 | 0,000380 |
| shares | 9 | content_category | −0,000125 | 0,000117 |
| shares | 10 | audience_gender_distribution | −0,000167 | 0,000285 |
| comments_count | 1 | hora | 0,000507 | 0,000364 |
| comments_count | 2 | audience_location | 0,000507 | 0,000291 |
| comments_count | 3 | dia_semana | 0,000199 | 0,000316 |
| comments_count | 4 | content_type | 0,000168 | 0,000156 |
| comments_count | 5 | audience_gender_distribution | 0,000083 | 0,000120 |
| comments_count | 6 | platform | 0,000077 | 0,000221 |
| comments_count | 7 | is_sponsored | 0,000054 | 0,000100 |
| comments_count | 8 | follower_count | 0,000016 | 0,000223 |
| comments_count | 9 | n_hashtags | −0,000011 | 0,000111 |
| comments_count | 10 | content_category | −0,000021 | 0,000205 |
| engajamento | 1 | n_hashtags | 0,000186 | 0,000128 |
| engajamento | 2 | content_type | 0,000096 | 0,000247 |
| engajamento | 3 | dia_semana | 0,000094 | 0,000504 |
| engajamento | 4 | follower_count | 0,000057 | 0,000304 |
| engajamento | 5 | audience_age_distribution | 0,000035 | 0,000314 |
| engajamento | 6 | content_length | 0,000009 | 0,000200 |
| engajamento | 7 | audience_gender_distribution | −0,000012 | 0,000132 |
| engajamento | 8 | is_sponsored | −0,000030 | 0,000033 |
| engajamento | 9 | hora | −0,000032 | 0,000254 |
| engajamento | 10 | content_category | −0,000038 | 0,000189 |

---

## Pontos suspeitos ou problemas encontrados

1. **Nenhum dos três métodos detecta efeito de patrocínio.** O efeito estratificado geral fica entre 0,99952 e 1,00002 (Bloco 1), o coeficiente de `is_sponsored` na regressão fica entre −0,04% e +0,02% da média da métrica com p-valores de 0,40 a 0,79 (Bloco 2), e nenhuma das 4 faixas de seguidores tem efeito com IC fora de 1 (Bloco 3). Nenhum dos 3 + 3 + 12 intervalos exclui o valor nulo.

2. **A estratificação não muda nada.** A comparação simples (sem estratos) difere do efeito estratificado só a partir da 4ª casa decimal (ex.: taxa_engajamento 0,999946 simples vs. 0,999877 estratificado). Controlar por plataforma, categoria, tipo e faixa não altera o resultado — coerente com a OS-02, onde nenhum desses segmentos tinha lift relevante.

3. **A regressão inteira não explica nada.** R² entre 0,00066 e 0,00078, R² ajustado **negativo** nas 3 métricas e teste F do modelo com p de 0,67 a 0,87 — o conjunto completo de 46 parâmetros não supera um modelo só com intercepto.

4. **O modelo preditivo perde para a média (Bloco 7).** R² médio negativo nos 4 alvos (−0,0008 a −0,0013) e MAE do modelo *pior* que o do `DummyRegressor` em todos (+0,05% a +0,07%). Nenhuma combinação das 13 variáveis de entrada prevê qualquer um dos 4 alvos melhor que prever sempre a média.

5. **Nenhuma variável tem importância real.** A maior queda de R² por permutação da base inteira é 0,000541 (platform, shares), da mesma ordem do próprio desvio entre repetições; 14 das 40 linhas do top-10 têm queda negativa. `is_sponsored` nunca passa de 0,000054.

6. **Engajamento entregue é constante.** As 8 células faixa × patrocínio do Bloco 5 têm média entre 2.009,92 e 2.010,84 (amplitude de 0,9 em ~2.010) e mediana 2.009–2.011. A mediana de engajamento/seguidor cai ~29× da faixa até 50K (0,0783) para 500K–1M (0,0027) apenas porque o denominador cresce — o numerador não varia (consistente com os pontos 1 e 2 da OS-01).

7. **% do engajamento = % dos posts em todos os cortes.** Na base, patrocinados são 42,74% dos posts e geram 42,73% do engajamento; em todos os 16 segmentos do Bloco 6 as duas porcentagens diferem só na 2ª casa decimal. Consequência direta do engajamento por post quase constante.

8. **Teste de repetição segue parecendo sorteio.** No Bloco 1, as metades de `taxa_engajamento` caem em lados opostos de 1 (A = 0,999728, B = 1,000021); no Bloco 4, só 28 de 51 linhas (54,9%) têm as duas metades do mesmo lado — próximo dos 50% esperados ao acaso, como na OS-02.

9. **Cobertura do Bloco 1:** 99 dos 240 estratos caem por não ter 30 patrocinados e 30 orgânicos, deixando 2.727 posts (5,2%) fora da comparação estratificada — reflexo do desbalanceamento das faixas de seguidores apontado na OS-01.

10. **Entrega do Bloco 7 em dois .csv.** O bloco tem duas tabelas de natureza diferente (desempenho por alvo e importância por variável), então saiu em `bloco7a_desempenho_modelo.csv` e `bloco7b_importancia_permutacao.csv` em vez de um único arquivo.
