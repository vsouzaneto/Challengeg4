# Resumo OS-03 — Patrocínio e validação geral

Base: 52.214 posts × 27 colunas originais (`datasets/social_media_dataset.csv`).
Script: `solution/analysis/os03_patrocinio_validacao.py`. Saídas: 8 .csv em `solution/outputs/os03/`.
Seed 42 em tudo. IC 95% por bootstrap percentil com 1.000 reamostragens.
Teste de repetição: a mesma divisão em duas metades da OS-02 (A = 26.107, B = 26.107).
Regras herdadas da OS-02: faixas de seguidores em 4 níveis (até 50K, 50–100K, 100–500K, 500K–1M),
`n_hashtags` (nulo = 0), `periodo_dia` e `dia_semana` com a mesma construção.

Volume por grupo: 22.314 posts patrocinados e 29.900 orgânicos.

---

## Bloco 1 — Comparação justa (estratificada)

Estratos: platform × content_category × content_type × faixa_seguidores.
Critério: pelo menos 30 posts patrocinados **e** 30 orgânicos por estrato.

| estratos_existentes | estratos_usados | posts_usados | posts_fora | n_patrocinado_usado | n_organico_usado |
|---|---|---|---|---|---|
| 240 | 141 | 49487 | 2727 | 21174 | 28313 |

Os 99 estratos descartados somam 2.727 posts (5,2% da base) e estão concentrados nas faixas
"até 50K" e "50–100K", que têm cerca de 2,5 mil posts cada.

Efeito geral = média das razões (média patrocinado / média orgânico) ponderada pelo tamanho do estrato.
IC 95% por bootstrap estratificado (reamostragem dentro de cada estrato e de cada grupo).

| metrica | efeito_geral | ic_inferior | ic_superior | ic_exclui_1 | efeito_metade_A | efeito_metade_B | comparacao_simples_sem_estratos |
|---|---|---|---|---|---|---|---|
| taxa_engajamento | 0.999877 | 0.999429 | 1.000352 | nao | 0.999728 | 1.000021 | 0.999946 |
| shares | 0.99952 | 0.998507 | 1.000535 | nao | 0.999059 | 0.999958 | 0.999565 |
| comments_count | 1.000018 | 0.998796 | 1.001383 | nao | 1.00015 | 0.999967 | 1.000184 |

Distribuição das 141 razões por métrica:

| metrica | pct_estratos_razao_maior_1 | razao_minimo | razao_p5 | razao_mediana | razao_p95 | razao_maximo |
|---|---|---|---|---|---|---|
| taxa_engajamento | 53.19 | 0.988167 | 0.993916 | 1.000253 | 1.006637 | 1.010619 |
| shares | 46.81 | 0.979506 | 0.987602 | 0.9995 | 1.013298 | 1.029031 |
| comments_count | 46.1 | 0.97029 | 0.985417 | 0.999457 | 1.017395 | 1.037867 |

## Bloco 2 — Regressão com controles (OLS, erros robustos HC3)

Modelo: `métrica ~ is_sponsored + platform + content_type + content_category + faixa_seguidores +
language + audience_age_distribution + audience_gender_distribution + audience_location +
n_hashtags + periodo_dia + dia_semana`. 46 parâmetros estimados, 52.214 observações.
`disclosure_type`, `disclosure_location`, `sponsor_category`, `sponsor_name` e `content_length`
não entraram, como pedido. `n_hashtags` entrou como variável categórica (6 níveis, 0 a 5),
junto com os demais controles categóricos.

| metrica | n | media_metrica | coef_is_sponsored | coef_pct_da_media | ic_inferior | ic_superior | ic_exclui_0 | p_valor | r2 | r2_ajustado | p_valor_teste_F | numero_de_condicao | n_parametros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| taxa_engajamento | 52214 | 0.199055 | -1.1e-05 | -0.0057 | -9.6e-05 | 7.3e-05 | nao | 0.791777 | 0.000775 | -8.7e-05 | 0.668108 | 17.41 | 46 |
| shares | 52214 | 300.018443 | -0.130211 | -0.0434 | -0.430394 | 0.169973 | nao | 0.395228 | 0.000667 | -0.000195 | 0.86725 | 17.41 | 46 |
| comments_count | 52214 | 200.015456 | 0.03888 | 0.0194 | -0.205753 | 0.283513 | nao | 0.755418 | 0.000659 | -0.000203 | 0.874329 | 17.41 | 46 |

## Bloco 3 — Patrocínio por faixa de seguidores

Método do Bloco 1 com estratos platform × content_category, mínimo de 20 patrocinados e
20 orgânicos por estrato. Os 15 estratos existentes foram usados nas 4 faixas.

| faixa_seguidores | metrica | n_patrocinado | n_organico | estratos_existentes | estratos_usados | efeito | ic_inferior | ic_superior | ic_exclui_1 | efeito_metade_A | efeito_metade_B |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ate 50K | taxa_engajamento | 1114 | 1450 | 15 | 15 | 1.000678 | 0.998748 | 1.00271 | nao | 1.000473 | 1.000511 |
| ate 50K | shares | 1114 | 1450 | 15 | 15 | 0.999461 | 0.994622 | 1.004346 | nao | 0.99847 | 1.000602 |
| ate 50K | comments_count | 1114 | 1450 | 15 | 15 | 1.000885 | 0.995516 | 1.006709 | nao | 0.99955 | 1.002758 |
| 50-100K | taxa_engajamento | 1109 | 1488 | 15 | 15 | 0.999652 | 0.997929 | 1.001637 | nao | 0.999561 | 0.999859 |
| 50-100K | shares | 1109 | 1488 | 15 | 15 | 1.000716 | 0.99666 | 1.005108 | nao | 1.000309 | 1.001316 |
| 50-100K | comments_count | 1109 | 1488 | 15 | 15 | 1.000554 | 0.995179 | 1.005857 | nao | 0.997609 | 1.003926 |
| 100-500K | taxa_engajamento | 8967 | 12057 | 15 | 15 | 1.000235 | 0.999584 | 1.000893 | nao | 0.999754 | 1.000697 |
| 100-500K | shares | 8967 | 12057 | 15 | 15 | 0.999895 | 0.998273 | 1.001438 | nao | 0.999412 | 1.000334 |
| 100-500K | comments_count | 8967 | 12057 | 15 | 15 | 1.001194 | 0.99934 | 1.003029 | nao | 1.000709 | 1.001687 |
| 500K-1M | taxa_engajamento | 11124 | 14905 | 15 | 15 | 0.999663 | 0.999104 | 1.000275 | nao | 0.999758 | 0.999571 |
| 500K-1M | shares | 11124 | 14905 | 15 | 15 | 0.999233 | 0.997853 | 1.000625 | nao | 0.998707 | 0.99979 |
| 500K-1M | comments_count | 11124 | 14905 | 15 | 15 | 0.999259 | 0.997638 | 1.001096 | nao | 1.000152 | 0.998341 |

Nenhum dos 12 IC exclui 1. Os efeitos ficam entre 0,999233 e 1,001194.

## Bloco 4 — Detalhes do patrocínio (só posts patrocinados)

Índice por post = valor / média da métrica entre os posts **patrocinados** da mesma plataforma.
Lift do segmento = média do índice no segmento.

| variaveis | segmento | metrica | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|---|---|
| disclosure_type | explicit | taxa_engajamento | 11784 | 1.000213 | 0.99977 | 1.000645 | nao | 1.000341 | 1.000081 | sim |
| disclosure_type | explicit | shares | 11784 | 1.000574 | 0.999618 | 1.001605 | nao | 1.000425 | 1.000727 | sim |
| disclosure_type | explicit | comments_count | 11784 | 1.00014 | 0.998838 | 1.001374 | nao | 0.999163 | 1.001145 | nao |
| disclosure_type | implicit | taxa_engajamento | 10530 | 0.999762 | 0.999262 | 1.000267 | nao | 0.999408 | 1.000107 | nao |
| disclosure_type | implicit | shares | 10530 | 0.999357 | 0.99823 | 1.000456 | nao | 0.998886 | 0.999817 | sim |
| disclosure_type | implicit | comments_count | 10530 | 0.999843 | 0.998481 | 1.001257 | nao | 0.999876 | 0.999811 | sim |
| disclosure_location | caption | taxa_engajamento | 8944 | 0.999664 | 0.999166 | 1.000167 | nao | 0.999494 | 0.999832 | sim |
| disclosure_location | caption | shares | 8944 | 0.999445 | 0.998236 | 1.000571 | nao | 0.999952 | 0.998945 | sim |
| disclosure_location | caption | comments_count | 8944 | 1.000725 | 0.999267 | 1.002186 | nao | 1.000075 | 1.001367 | sim |
| disclosure_location | hashtags | taxa_engajamento | 6124 | 1.000329 | 0.9997 | 1.00091 | nao | 1.000519 | 1.000128 | sim |
| disclosure_location | hashtags | shares | 6124 | 1.000385 | 0.998874 | 1.001657 | nao | 0.999461 | 1.001363 | nao |
| disclosure_location | hashtags | comments_count | 6124 | 1.000588 | 0.998867 | 1.002272 | nao | 1.000884 | 1.000274 | sim |
| disclosure_location | video | taxa_engajamento | 7246 | 1.000136 | 0.999625 | 1.000676 | nao | 0.999881 | 1.000385 | nao |
| disclosure_location | video | shares | 7246 | 1.000359 | 0.999026 | 1.001705 | nao | 0.999626 | 1.001074 | nao |
| disclosure_location | video | comments_count | 7246 | 0.998609 | 0.996994 | 1.000161 | nao | 0.99755 | 0.99964 | sim |
| sponsor_category | cosmetics | taxa_engajamento | 3688 | 1.000546 | 0.999746 | 1.001359 | nao | 1.000361 | 1.000741 | sim |
| sponsor_category | cosmetics | shares | 3688 | 0.999313 | 0.997351 | 1.001088 | nao | 0.998238 | 1.000446 | nao |
| sponsor_category | cosmetics | comments_count | 3688 | 0.999803 | 0.997629 | 1.002008 | nao | 0.999961 | 0.999636 | sim |
| sponsor_category | electronics | taxa_engajamento | 3750 | 1.000007 | 0.999229 | 1.000791 | nao | 0.999224 | 1.000807 | nao |
| sponsor_category | electronics | shares | 3750 | 1.001437 | 0.999639 | 1.003444 | nao | 1.000898 | 1.001988 | sim |
| sponsor_category | electronics | comments_count | 3750 | 1.000375 | 0.998237 | 1.002578 | nao | 0.998014 | 1.002787 | nao |
| sponsor_category | fashion | taxa_engajamento | 3710 | 0.999284 | 0.998493 | 1.000077 | nao | 0.999314 | 0.999255 | sim |
| sponsor_category | fashion | shares | 3710 | 0.999786 | 0.997872 | 1.00164 | nao | 1.000533 | 0.999052 | nao |
| sponsor_category | fashion | comments_count | 3710 | 0.999004 | 0.996885 | 1.001291 | nao | 0.998254 | 0.999742 | sim |
| sponsor_category | food | taxa_engajamento | 3846 | 1.000307 | 0.999545 | 1.00114 | nao | 1.000168 | 1.000446 | sim |
| sponsor_category | food | shares | 3846 | 0.999397 | 0.997555 | 1.001221 | nao | 0.997949 | 1.00084 | nao |
| sponsor_category | food | comments_count | 3846 | 1.001096 | 0.998843 | 1.003266 | nao | 1.001275 | 1.000918 | sim |
| sponsor_category | gaming | taxa_engajamento | 3687 | 0.999728 | 0.998912 | 1.000557 | nao | 0.999778 | 0.999677 | sim |
| sponsor_category | gaming | shares | 3687 | 0.999667 | 0.997765 | 1.00151 | nao | 1.000584 | 0.998739 | nao |
| sponsor_category | gaming | comments_count | 3687 | 0.998897 | 0.996479 | 1.001088 | nao | 0.997834 | 0.999972 | sim |
| sponsor_category | travel | taxa_engajamento | 3633 | 1.000121 | 0.999298 | 1.00093 | nao | 1.00062 | 0.999646 | nao |
| sponsor_category | travel | shares | 3633 | 1.000408 | 0.998499 | 1.002353 | nao | 1.000143 | 1.00066 | sim |
| sponsor_category | travel | comments_count | 3633 | 1.000789 | 0.998628 | 1.002901 | nao | 1.001679 | 0.999943 | nao |
| disclosure_type x disclosure_location | explicit \| caption | taxa_engajamento | 4765 | 0.999768 | 0.999085 | 1.000473 | nao | 0.999864 | 0.999671 | sim |
| disclosure_type x disclosure_location | explicit \| caption | shares | 4765 | 1.000277 | 0.998704 | 1.002004 | nao | 1.000635 | 0.999918 | nao |
| disclosure_type x disclosure_location | explicit \| caption | comments_count | 4765 | 0.999818 | 0.997819 | 1.001803 | nao | 0.999416 | 1.000222 | nao |
| disclosure_type x disclosure_location | explicit \| hashtags | taxa_engajamento | 3180 | 1.000711 | 0.999888 | 1.001601 | nao | 1.001302 | 1.000039 | sim |
| disclosure_type x disclosure_location | explicit \| hashtags | shares | 3180 | 1.000506 | 0.998526 | 1.002435 | nao | 0.999938 | 1.001153 | nao |
| disclosure_type x disclosure_location | explicit \| hashtags | comments_count | 3180 | 1.00177 | 0.999505 | 1.004234 | nao | 1.001303 | 1.002302 | sim |
| disclosure_type x disclosure_location | explicit \| video | taxa_engajamento | 3839 | 1.000353 | 0.9996 | 1.00115 | nao | 1.000083 | 1.000616 | sim |
| disclosure_type x disclosure_location | explicit \| video | shares | 3839 | 1.001 | 0.999099 | 1.002902 | nao | 1.000597 | 1.001393 | sim |
| disclosure_type x disclosure_location | explicit \| video | comments_count | 3839 | 0.999189 | 0.996784 | 1.001589 | nao | 0.996934 | 1.00139 | nao |
| disclosure_type x disclosure_location | implicit \| caption | taxa_engajamento | 4179 | 0.999546 | 0.998792 | 1.000292 | nao | 0.999065 | 1.000014 | nao |
| disclosure_type x disclosure_location | implicit \| caption | shares | 4179 | 0.998497 | 0.996732 | 1.000145 | nao | 0.999161 | 0.997851 | sim |
| disclosure_type x disclosure_location | implicit \| caption | comments_count | 4179 | 1.001758 | 0.999624 | 1.004016 | nao | 1.000838 | 1.002654 | sim |
| disclosure_type x disclosure_location | implicit \| hashtags | taxa_engajamento | 2944 | 0.999917 | 0.999083 | 1.000754 | nao | 0.99961 | 1.000217 | nao |
| disclosure_type x disclosure_location | implicit \| hashtags | shares | 2944 | 1.000255 | 0.998199 | 1.002162 | nao | 0.998908 | 1.001574 | nao |
| disclosure_type x disclosure_location | implicit \| hashtags | comments_count | 2944 | 0.99931 | 0.996883 | 1.001758 | nao | 1.000397 | 0.998245 | nao |
| disclosure_type x disclosure_location | implicit \| video | taxa_engajamento | 3407 | 0.999892 | 0.999094 | 1.000715 | nao | 0.999654 | 1.000125 | nao |
| disclosure_type x disclosure_location | implicit \| video | shares | 3407 | 0.999637 | 0.997688 | 1.001514 | nao | 0.998529 | 1.000714 | nao |
| disclosure_type x disclosure_location | implicit \| video | comments_count | 3407 | 0.997955 | 0.995579 | 1.000125 | nao | 0.998246 | 0.997672 | sim |

Dos 51 segmentos × métrica, **0 têm IC que exclui 1**. O teste de repetição aponta o mesmo lado
nas duas metades em 28 de 51 casos (54,9%). Os lifts ficam entre 0,997955 e 1,001770.

## Bloco 5 — Engajamento entregue por faixa

`engajamento` = likes + shares + comments_count (valor absoluto por post).

| faixa_seguidores | is_sponsored | n | media_engajamento | ic_inferior | ic_superior | mediana_engajamento | p10_engajamento | p90_engajamento | mediana_engajamento_por_seguidor |
|---|---|---|---|---|---|---|---|---|---|
| ate 50K | True | 1114 | 2010.843806 | 2008.213375 | 2013.48456 | 2011.0 | 1952.3 | 2068.0 | 0.078270687 |
| ate 50K | False | 1450 | 2009.95931 | 2007.588621 | 2012.378224 | 2009.0 | 1951.0 | 2071.0 | 0.079036932 |
| 50-100K | True | 1109 | 2010.346258 | 2007.837669 | 2012.914022 | 2011.0 | 1952.0 | 2069.0 | 0.026379656 |
| 50-100K | False | 1488 | 2010.782258 | 2008.637601 | 2013.126546 | 2009.0 | 1952.0 | 2069.0 | 0.026736727 |
| 100-500K | True | 8967 | 2010.633657 | 2009.730141 | 2011.565992 | 2011.0 | 1953.0 | 2067.0 | 0.006731932 |
| 100-500K | False | 12057 | 2010.021232 | 2009.195975 | 2010.7899 | 2010.0 | 1953.0 | 2067.0 | 0.006677936 |
| 500K-1M | True | 11124 | 2009.918105 | 2009.07304 | 2010.6595 | 2009.0 | 1952.0 | 2068.0 | 0.00267522 |
| 500K-1M | False | 14905 | 2010.580074 | 2009.87163 | 2011.244291 | 2010.0 | 1954.0 | 2068.0 | 0.002677199 |

As 8 médias ficam entre 2.009,92 e 2.010,84. A mediana de `engajamento / follower_count` cai
com a faixa de seguidores (0,078 na faixa até 50K contra 0,0027 na faixa 500K–1M) e é
praticamente igual entre patrocinado e orgânico dentro de cada faixa.

## Bloco 6 — Volume patrocinado

| variavel | segmento | n_total | n_patrocinado | n_organico | pct_patrocinado | engajamento_total | engajamento_patrocinado | pct_engajamento_patrocinado |
|---|---|---|---|---|---|---|---|---|
| platform | Bilibili | 10598 | 4453 | 6145 | 42.0174 | 21307767.0 | 8951580.0 | 42.0109 |
| platform | Instagram | 10423 | 4369 | 6054 | 41.9169 | 20946950.0 | 8782394.0 | 41.9268 |
| platform | RedNote | 10402 | 4521 | 5881 | 43.4628 | 20916853.0 | 9093334.0 | 43.4737 |
| platform | TikTok | 10296 | 4441 | 5855 | 43.1333 | 20699400.0 | 8926472.0 | 43.1243 |
| platform | YouTube | 10495 | 4530 | 5965 | 43.1634 | 21095272.0 | 9103455.0 | 43.154 |
| content_category | beauty | 21023 | 8926 | 12097 | 42.4583 | 42261477.0 | 17936938.0 | 42.4428 |
| content_category | lifestyle | 20761 | 8891 | 11870 | 42.8255 | 41740052.0 | 17878595.0 | 42.8332 |
| content_category | tech | 10430 | 4497 | 5933 | 43.116 | 20964713.0 | 9041702.0 | 43.1282 |
| content_type | image | 10303 | 4416 | 5887 | 42.8613 | 20712300.0 | 8878250.0 | 42.8646 |
| content_type | mixed | 5213 | 2224 | 2989 | 42.6626 | 10484160.0 | 4473848.0 | 42.6725 |
| content_type | text | 5198 | 2205 | 2993 | 42.4202 | 10452520.0 | 4434333.0 | 42.4236 |
| content_type | video | 31500 | 13469 | 18031 | 42.7587 | 63317262.0 | 27070804.0 | 42.7542 |
| faixa_seguidores | 100-500K | 21024 | 8967 | 12057 | 42.6513 | 42264178.0 | 18029352.0 | 42.6587 |
| faixa_seguidores | 50-100K | 2597 | 1109 | 1488 | 42.7031 | 5221518.0 | 2229474.0 | 42.6978 |
| faixa_seguidores | 500K-1M | 26029 | 11124 | 14905 | 42.7369 | 52326025.0 | 22358329.0 | 42.7289 |
| faixa_seguidores | ate 50K | 2564 | 1114 | 1450 | 43.4477 | 5154521.0 | 2240080.0 | 43.4585 |
| base | todos | 52214 | 22314 | 29900 | 42.7357 | 104966242.0 | 44857235.0 | 42.7349 |

Na base inteira: 42,7357% dos posts são patrocinados e esses posts respondem por
42,7349% do engajamento total — uma diferença de 0,0008 ponto percentual.

## Bloco 7 — Validação geral (modelo preditivo)

`HistGradientBoostingRegressor` com parâmetros padrão e `random_state=42`.
Entradas: platform, content_type, content_category, language, is_sponsored,
audience_age_distribution, audience_gender_distribution, audience_location, follower_count,
n_hashtags, content_length, hora do post e dia_semana (13 variáveis).
Nenhuma métrica de resultado entrou como entrada.
Validação cruzada de 5 partes, embaralhada, seed 42. Comparação com `DummyRegressor` (média).

| alvo | r2_medio | r2_desvio | mae_modelo | mae_modelo_da_media | dif_pct_mae_vs_media | r2_medio_modelo_da_media |
|---|---|---|---|---|---|---|
| taxa_engajamento | -0.001162 | 0.000598 | 0.003882 | 0.00388 | 0.0473 | -0.000122 |
| shares | -0.001241 | 0.000942 | 13.834531 | 13.824963 | 0.0692 | -0.000135 |
| comments_count | -0.000807 | 0.000492 | 11.271032 | 11.265099 | 0.0527 | -0.000159 |
| engajamento | -0.001308 | 0.00049 | 35.851408 | 35.831213 | 0.0564 | -9.6e-05 |

`dif_pct_mae_vs_media` positivo significa MAE do modelo **maior** (pior) que o do modelo da média.

Importância por permutação (80% treino / 20% teste, seed 42; 10 repetições; queda de R²):

| alvo | posicao | variavel | queda_r2_media | queda_r2_desvio |
|---|---|---|---|---|
| taxa_engajamento | 1 | dia_semana | 0.000529 | 0.000512 |
| taxa_engajamento | 2 | audience_age_distribution | 0.00031 | 0.000221 |
| taxa_engajamento | 3 | hora | 0.000255 | 0.000239 |
| taxa_engajamento | 4 | content_category | 0.000136 | 9.7e-05 |
| taxa_engajamento | 5 | follower_count | 0.000114 | 0.000214 |
| taxa_engajamento | 6 | language | 9.9e-05 | 0.000119 |
| taxa_engajamento | 7 | is_sponsored_num | 3.8e-05 | 6.8e-05 |
| taxa_engajamento | 8 | n_hashtags | -1.1e-05 | 9.4e-05 |
| taxa_engajamento | 9 | content_type | -4.4e-05 | 0.000191 |
| taxa_engajamento | 10 | audience_gender_distribution | -0.000107 | 0.000174 |
| shares | 1 | platform | 0.000541 | 0.000417 |
| shares | 2 | hora | 0.000379 | 0.000326 |
| shares | 3 | content_type | 0.000212 | 0.000483 |
| shares | 4 | n_hashtags | 4.5e-05 | 0.000219 |
| shares | 5 | audience_age_distribution | 1.2e-05 | 0.000258 |
| shares | 6 | language | -7.3e-05 | 0.000215 |
| shares | 7 | is_sponsored_num | -0.000114 | 0.000176 |
| shares | 8 | content_length | -0.000118 | 0.00038 |
| shares | 9 | content_category | -0.000125 | 0.000117 |
| shares | 10 | audience_gender_distribution | -0.000167 | 0.000285 |
| comments_count | 1 | hora | 0.000507 | 0.000364 |
| comments_count | 2 | audience_location | 0.000507 | 0.000291 |
| comments_count | 3 | dia_semana | 0.000199 | 0.000316 |
| comments_count | 4 | content_type | 0.000168 | 0.000156 |
| comments_count | 5 | audience_gender_distribution | 8.3e-05 | 0.00012 |
| comments_count | 6 | platform | 7.7e-05 | 0.000221 |
| comments_count | 7 | is_sponsored_num | 5.4e-05 | 0.0001 |
| comments_count | 8 | follower_count | 1.6e-05 | 0.000223 |
| comments_count | 9 | n_hashtags | -1.1e-05 | 0.000111 |
| comments_count | 10 | content_category | -2.1e-05 | 0.000205 |
| engajamento | 1 | n_hashtags | 0.000186 | 0.000128 |
| engajamento | 2 | content_type | 9.6e-05 | 0.000247 |
| engajamento | 3 | dia_semana | 9.4e-05 | 0.000504 |
| engajamento | 4 | follower_count | 5.7e-05 | 0.000304 |
| engajamento | 5 | audience_age_distribution | 3.5e-05 | 0.000314 |
| engajamento | 6 | content_length | 9e-06 | 0.0002 |
| engajamento | 7 | audience_gender_distribution | -1.2e-05 | 0.000132 |
| engajamento | 8 | is_sponsored_num | -3e-05 | 3.3e-05 |
| engajamento | 9 | hora | -3.2e-05 | 0.000254 |
| engajamento | 10 | content_category | -3.8e-05 | 0.000189 |

---

## Pontos suspeitos ou problemas encontrados

1. **Nenhum efeito de patrocínio em nenhum dos três métodos.** Bloco 1: efeito geral entre
   0,99952 e 1,000018, com os 3 IC incluindo 1; a maior razão de estrato individual é 1,037867 e a
   menor 0,97029, em 141 estratos. Bloco 2: coeficiente de `is_sponsored` com p-valor 0,40 a 0,79 e
   magnitude de -0,04% a +0,02% da média da métrica. Bloco 3: 0 de 12 IC excluem 1. Bloco 4:
   0 de 51 IC excluem 1. Os números estão reportados; não houve alteração de método.

2. **A regressão com 45 controles não explica nada.** R² entre 0,000659 e 0,000775, R² ajustado
   **negativo** nas três métricas (-0,000087 a -0,000203) e p-valor do teste F do modelo entre
   0,668 e 0,874. Ou seja, o conjunto completo de controles não se distingue de ruído. O número de
   condição é baixo (17,41), então não é colinearidade: é ausência de sinal.

3. **O modelo preditivo é pior que prever a média.** R² médio negativo nos 4 alvos
   (-0,000807 a -0,001308) e MAE 0,05% a 0,07% **acima** do `DummyRegressor`. Na importância por
   permutação, 14 das 40 linhas do top 10 têm queda de R² **negativa** e 29 das 40 têm
   |média| menor que o próprio desvio-padrão — o ranking de variáveis não se distingue de ruído.
   A maior queda de R² observada em toda a tabela é 0,000541.

4. **O teste de repetição se comporta como sorteio.** No Bloco 4, 28 de 51 casos (54,9%) apontam o
   mesmo lado nas duas metades, contra 50% esperados por acaso. Mesmo padrão já registrado na OS-02.

5. **Métricas com dispersão implausível para dados reais** (já apontado na OS-01 e OS-02). O
   engajamento médio por post é praticamente constante em todos os cortes: no Bloco 5, as 8 células
   de faixa × patrocínio ficam entre 2.009,92 e 2.010,84 (variação de 0,05%), com p10 ~1.952 e
   p90 ~2.068 em todas elas. No Bloco 6, o % de engajamento que vem de posts patrocinados coincide
   com o % de posts patrocinados até a terceira casa decimal, em todos os cortes. É o
   comportamento esperado de métricas sorteadas em torno de uma média fixa, sem relação com
   nenhuma variável da base.

6. **Cobertura do Bloco 1.** O critério de 30 + 30 descartou 99 dos 240 estratos, mas só 5,2% dos
   posts (2.727). O descarte é quase todo nas faixas "até 50K" e "50–100K", que juntas têm 5.161
   posts contra 47.053 nas outras duas faixas. O efeito geral do Bloco 1 fica, portanto,
   dominado pelas faixas 100–500K e 500K–1M.

7. **As colunas de patrocínio são 100% determinadas por `is_sponsored`** (confirmado: todos os
   orgânicos têm `disclosure_type='none'`, `disclosure_location='none'` e
   `sponsor_category='Not sponsors'`; nenhum patrocinado tem `'none'`). Por isso o Bloco 4 não tem
   segmento "none" e a exclusão dessas colunas no Bloco 2 era necessária.

8. **Aviso do numpy no Bloco 2 (não é erro de resultado).** O cálculo do p-valor do teste F com
   covariância HC3 dispara `RuntimeWarning: divide by zero / overflow / invalid value encountered
   in matmul`, vindo do `np.linalg.pinv` chamado por `statsmodels` dentro do Wald F robusto. A causa
   é a escala minúscula das entradas da matriz HC3 (da ordem de 1e-18 para `taxa_engajamento`), não
   um erro de especificação. Conferi os três p-valores do teste F contra o F clássico calculado à
   mão a partir do R² e dos graus de liberdade (0,67 / 0,87 / 0,87): conferem. O aviso ficou
   registrado em vez de ser silenciado.
