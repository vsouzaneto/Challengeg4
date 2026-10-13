# OS-03b - Fit de patrocinio e audiencia

Base: 52214 posts. Patrocinados: 22314 (com fit: 7439; sem fit: 14875). Metades: A=26107, B=26107.

Metricas: `taxa_engajamento`, `shares`, `comments_count`. Indice por post = valor / media da metrica na plataforma do post. Lift = media do indice no segmento. IC 95% por bootstrap percentil (1000 reamostragens). Teste contra o acaso: 200 permutacoes. Seed 42.


## Parte A - Fit patrocinador x conteudo (so posts patrocinados)

### A1. Volume com e sem fit

| escopo | content_category | n_patrocinado | n_com_fit | n_sem_fit | pct_com_fit | pct_sem_fit |
|---|---|---|---|---|---|---|
| total | todas | 22314 | 7439 | 14875 | 33.3378 | 66.6622 |
| content_category | beauty | 8926 | 1503 | 7423 | 16.8384 | 83.1616 |
| content_category | lifestyle | 8891 | 4445 | 4446 | 49.9944 | 50.0056 |
| content_category | tech | 4497 | 1491 | 3006 | 33.1554 | 66.8446 |

### A2. Comparacao fit vs. sem fit (estratos platform x content_category x faixa_seguidores, minimo de 20 posts em cada grupo)

Efeito = media das razoes (media com fit / media sem fit) ponderada pelo tamanho do estrato.

| metrica | estratos_existentes | estratos_usados | estratos_fora | posts_base_patrocinados | posts_usados | posts_fora | n_com_fit_usado | n_sem_fit_usado | efeito_geral | ic_inferior | ic_superior | ic_exclui_1 | efeito_metade_A | efeito_metade_B | pct_estratos_razao_maior_1 | razao_minimo | razao_mediana | razao_maximo | comparacao_simples_sem_estratos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| taxa_engajamento | 60 | 42 | 18 | 22314 | 21035 | 1279 | 7182 | 13853 | 1.000339 | 0.99964 | 1.001107 | nao | 1.000439 | 1.000191 | 54.76 | 0.993729 | 1.000234 | 1.010336 | 1.000499 |
| shares | 60 | 42 | 18 | 22314 | 21035 | 1279 | 7182 | 13853 | 0.998367 | 0.996775 | 1.000232 | nao | 0.998514 | 0.99808 | 47.62 | 0.980394 | 0.999224 | 1.02155 | 0.998966 |
| comments_count | 60 | 42 | 18 | 22314 | 21035 | 1279 | 7182 | 13853 | 1.002017 | 0.999941 | 1.004237 | nao | 1.003411 | 1.000547 | 54.76 | 0.977977 | 1.001911 | 1.030423 | 1.00176 |

### A3. sponsor_category x content_category (18 combinacoes)

Lift com referencia na media dos posts patrocinados da plataforma.

| variaveis | segmento | metrica | tem_fit | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sponsor_category x content_category | cosmetics \| beauty | taxa_engajamento | sim | 1503 | 1.000362 | 0.999109 | 1.00165 | nao | 1.000449 | 1.000272 | sim |
| sponsor_category x content_category | cosmetics \| beauty | shares | sim | 1503 | 0.99562 | 0.992708 | 0.998549 | sim | 0.996255 | 0.994964 | sim |
| sponsor_category x content_category | cosmetics \| beauty | comments_count | sim | 1503 | 1.000987 | 0.997722 | 1.004551 | nao | 1.001622 | 1.000333 | sim |
| sponsor_category x content_category | cosmetics \| lifestyle | taxa_engajamento | nao | 1462 | 1.000291 | 0.998965 | 1.001587 | nao | 0.999545 | 1.001047 | nao |
| sponsor_category x content_category | cosmetics \| lifestyle | shares | nao | 1462 | 1.000896 | 0.998054 | 1.00366 | nao | 0.999466 | 1.002346 | nao |
| sponsor_category x content_category | cosmetics \| lifestyle | comments_count | nao | 1462 | 0.99835 | 0.994804 | 1.001813 | nao | 0.99858 | 0.998116 | sim |
| sponsor_category x content_category | cosmetics \| tech | taxa_engajamento | nao | 723 | 1.001446 | 0.999892 | 1.003349 | nao | 1.00172 | 1.001119 | sim |
| sponsor_category x content_category | cosmetics \| tech | shares | nao | 723 | 1.003791 | 0.999783 | 1.008176 | nao | 0.99979 | 1.008556 | nao |
| sponsor_category x content_category | cosmetics \| tech | comments_count | nao | 723 | 1.000278 | 0.994704 | 1.005738 | nao | 0.999325 | 1.001414 | nao |
| sponsor_category x content_category | electronics \| beauty | taxa_engajamento | nao | 1463 | 0.999017 | 0.997767 | 1.000273 | nao | 0.997438 | 1.000552 | nao |
| sponsor_category x content_category | electronics \| beauty | shares | nao | 1463 | 1.002633 | 0.999535 | 1.005723 | nao | 1.003064 | 1.002213 | sim |
| sponsor_category x content_category | electronics \| beauty | comments_count | nao | 1463 | 0.998505 | 0.994761 | 1.002142 | nao | 0.993292 | 1.003571 | nao |
| sponsor_category x content_category | electronics \| lifestyle | taxa_engajamento | nao | 1525 | 1.000814 | 0.999552 | 1.002064 | nao | 1.000396 | 1.001261 | sim |
| sponsor_category x content_category | electronics \| lifestyle | shares | nao | 1525 | 1.00081 | 0.997949 | 1.003812 | nao | 0.998619 | 1.003152 | nao |
| sponsor_category x content_category | electronics \| lifestyle | comments_count | nao | 1525 | 1.000496 | 0.997135 | 1.004216 | nao | 1.001457 | 0.999468 | nao |
| sponsor_category x content_category | electronics \| tech | taxa_engajamento | sim | 762 | 1.000292 | 0.99844 | 1.001973 | nao | 1.000168 | 1.000419 | sim |
| sponsor_category x content_category | electronics \| tech | shares | sim | 762 | 1.000397 | 0.996279 | 1.004766 | nao | 1.001503 | 0.999261 | nao |
| sponsor_category x content_category | electronics \| tech | comments_count | sim | 762 | 1.003724 | 0.998709 | 1.008891 | nao | 0.999806 | 1.007746 | nao |
| sponsor_category x content_category | fashion \| beauty | taxa_engajamento | nao | 1468 | 0.99858 | 0.997456 | 0.999863 | sim | 0.99856 | 0.9986 | sim |
| sponsor_category x content_category | fashion \| beauty | shares | nao | 1468 | 0.999105 | 0.996382 | 1.001982 | nao | 1.001662 | 0.996589 | nao |
| sponsor_category x content_category | fashion \| beauty | comments_count | nao | 1468 | 0.997909 | 0.994305 | 1.001262 | nao | 0.994949 | 1.000821 | nao |
| sponsor_category x content_category | fashion \| lifestyle | taxa_engajamento | sim | 1467 | 0.999806 | 0.998569 | 1.001109 | nao | 0.99886 | 1.000755 | nao |
| sponsor_category x content_category | fashion \| lifestyle | shares | sim | 1467 | 0.99931 | 0.996333 | 1.002192 | nao | 0.997474 | 1.001153 | nao |
| sponsor_category x content_category | fashion \| lifestyle | comments_count | sim | 1467 | 1.000098 | 0.996517 | 1.003659 | nao | 1.000264 | 0.99993 | nao |
| sponsor_category x content_category | fashion \| tech | taxa_engajamento | nao | 775 | 0.999629 | 0.997892 | 1.001249 | nao | 1.001653 | 0.997713 | nao |
| sponsor_category x content_category | fashion \| tech | shares | nao | 775 | 1.001981 | 0.997957 | 1.005682 | nao | 1.004317 | 0.999767 | nao |
| sponsor_category x content_category | fashion \| tech | comments_count | nao | 775 | 0.999008 | 0.994195 | 1.003828 | nao | 1.000716 | 0.997389 | nao |
| sponsor_category x content_category | food \| beauty | taxa_engajamento | nao | 1532 | 1.000353 | 0.999187 | 1.001544 | nao | 1.000404 | 1.000304 | sim |
| sponsor_category x content_category | food \| beauty | shares | nao | 1532 | 0.99958 | 0.996721 | 1.002535 | nao | 0.998807 | 1.000336 | nao |
| sponsor_category x content_category | food \| beauty | comments_count | nao | 1532 | 1.001428 | 0.99791 | 1.005093 | nao | 1.003184 | 0.999714 | nao |
| sponsor_category x content_category | food \| lifestyle | taxa_engajamento | sim | 1561 | 1.000636 | 0.999346 | 1.001848 | nao | 1.000634 | 1.000637 | sim |
| sponsor_category x content_category | food \| lifestyle | shares | sim | 1561 | 0.998813 | 0.996069 | 1.001855 | nao | 0.998983 | 0.998644 | sim |
| sponsor_category x content_category | food \| lifestyle | comments_count | sim | 1561 | 1.001422 | 0.998137 | 1.004601 | nao | 1.001593 | 1.001253 | sim |
| sponsor_category x content_category | food \| tech | taxa_engajamento | nao | 753 | 0.999533 | 0.99796 | 1.001355 | nao | 0.998759 | 1.00034 | nao |
| sponsor_category x content_category | food \| tech | shares | nao | 753 | 1.000235 | 0.996251 | 1.004433 | nao | 0.994163 | 1.006554 | nao |
| sponsor_category x content_category | food \| tech | comments_count | nao | 753 | 0.999744 | 0.995054 | 1.004503 | nao | 0.996865 | 1.002739 | nao |
| sponsor_category x content_category | gaming \| beauty | taxa_engajamento | nao | 1499 | 1.000026 | 0.998772 | 1.001258 | nao | 1.000076 | 0.999976 | nao |
| sponsor_category x content_category | gaming \| beauty | shares | nao | 1499 | 0.999079 | 0.995976 | 1.001764 | nao | 1.000166 | 0.997963 | nao |
| sponsor_category x content_category | gaming \| beauty | comments_count | nao | 1499 | 0.998569 | 0.994993 | 1.002366 | nao | 0.997217 | 0.999955 | sim |
| sponsor_category x content_category | gaming \| lifestyle | taxa_engajamento | nao | 1459 | 0.999414 | 0.998139 | 1.000693 | nao | 0.999118 | 0.999711 | sim |
| sponsor_category x content_category | gaming \| lifestyle | shares | nao | 1459 | 0.999302 | 0.996439 | 1.002106 | nao | 1.001329 | 0.997255 | nao |
| sponsor_category x content_category | gaming \| lifestyle | comments_count | nao | 1459 | 0.998327 | 0.994949 | 1.002247 | nao | 0.995222 | 1.001461 | nao |
| sponsor_category x content_category | gaming \| tech | taxa_engajamento | sim | 729 | 0.999743 | 0.997875 | 1.00145 | nao | 1.000491 | 0.999004 | nao |
| sponsor_category x content_category | gaming \| tech | shares | sim | 729 | 1.001607 | 0.997436 | 1.005761 | nao | 0.999954 | 1.003239 | nao |
| sponsor_category x content_category | gaming \| tech | comments_count | sim | 729 | 1.000713 | 0.995677 | 1.005694 | nao | 1.004415 | 0.997062 | nao |
| sponsor_category x content_category | travel \| beauty | taxa_engajamento | nao | 1461 | 0.999428 | 0.998166 | 1.000684 | nao | 0.999951 | 0.998941 | sim |
| sponsor_category x content_category | travel \| beauty | shares | nao | 1461 | 0.999475 | 0.996693 | 1.002215 | nao | 0.999302 | 0.999636 | sim |
| sponsor_category x content_category | travel \| beauty | comments_count | nao | 1461 | 1.001934 | 0.998326 | 1.005196 | nao | 1.002292 | 1.001599 | sim |
| sponsor_category x content_category | travel \| lifestyle | taxa_engajamento | sim | 1417 | 1.000853 | 0.999571 | 1.002074 | nao | 1.001783 | 0.999988 | nao |
| sponsor_category x content_category | travel \| lifestyle | shares | sim | 1417 | 1.002016 | 0.998995 | 1.00488 | nao | 1.001755 | 1.002259 | sim |
| sponsor_category x content_category | travel \| lifestyle | comments_count | sim | 1417 | 1.001084 | 0.997183 | 1.004771 | nao | 1.004756 | 0.997668 | nao |
| sponsor_category x content_category | travel \| tech | taxa_engajamento | nao | 755 | 1.000086 | 0.998183 | 1.001902 | nao | 0.999778 | 1.000403 | nao |
| sponsor_category x content_category | travel \| tech | shares | nao | 755 | 0.999198 | 0.995082 | 1.002912 | nao | 0.99882 | 0.999588 | sim |
| sponsor_category x content_category | travel \| tech | comments_count | nao | 755 | 0.998022 | 0.993066 | 1.00273 | nao | 0.995065 | 1.001066 | nao |

## Parte B - Audiencia (todos os posts)

### B1 e B2 - cobertura dos conjuntos

| variaveis | segmentos_existentes | segmentos_mantidos | segmentos_fora | posts_fora |
|---|---|---|---|---|
| audience_age_distribution x audience_gender_distribution x audience_location | 160 | 126 | 34 | 2157 |
| content_category x audience_age_distribution | 15 | 15 | 0 | 0 |
| content_category x audience_gender_distribution | 12 | 12 | 0 | 0 |
| content_category x audience_location | 24 | 24 | 0 | 0 |

Segmentos com n < 100 ficaram de fora.


### B1 e B2 - distribuicao dos lifts por conjunto e metrica

| conjunto | metrica | segmentos | minimo | p5 | mediana | p95 | maximo | acima_1_03 | acima_1_05 | acima_1_10 | abaixo_0_97 | abaixo_0_95 | abaixo_0_90 | ic_exclui_1_sim | mesmo_lado_sim |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 personas (idade x genero x local) | taxa_engajamento | 126 | 0.996523 | 0.997352 | 0.999882 | 1.002582 | 1.005435 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 59 |
| B1 personas (idade x genero x local) | shares | 126 | 0.989645 | 0.99382 | 0.999868 | 1.006039 | 1.01102 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 57 |
| B1 personas (idade x genero x local) | comments_count | 126 | 0.990042 | 0.993216 | 0.99965 | 1.006008 | 1.009605 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 52 |
| B2 content_category x audience_age_distribution | taxa_engajamento | 15 | 0.998769 | 0.999202 | 0.999956 | 1.00053 | 1.000661 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| B2 content_category x audience_age_distribution | shares | 15 | 0.998441 | 0.998755 | 1.000206 | 1.000958 | 1.001096 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| B2 content_category x audience_age_distribution | comments_count | 15 | 0.997251 | 0.997689 | 0.999808 | 1.001738 | 1.00256 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| B2 content_category x audience_gender_distribution | taxa_engajamento | 12 | 0.998909 | 0.999296 | 0.999972 | 1.000416 | 1.000567 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| B2 content_category x audience_gender_distribution | shares | 12 | 0.998888 | 0.999013 | 0.999974 | 1.001276 | 1.001831 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| B2 content_category x audience_gender_distribution | comments_count | 12 | 0.999027 | 0.999196 | 1.000121 | 1.001513 | 1.002054 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| B2 content_category x audience_location | taxa_engajamento | 24 | 0.998644 | 0.999174 | 0.999902 | 1.000827 | 1.00102 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 14 |
| B2 content_category x audience_location | shares | 24 | 0.998188 | 0.998352 | 1.000223 | 1.001715 | 1.001909 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 |
| B2 content_category x audience_location | comments_count | 24 | 0.997076 | 0.998431 | 1.000216 | 1.001634 | 1.002594 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 8 |

### B1 personas (idade x genero x local) - 10 maiores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| 50+ \| male \| UK | 123 | 1.005435 | 1.000972 | 1.009954 | sim | 1.005413 | 1.005451 | sim |
| 26-35 \| non-binary \| China | 213 | 1.005216 | 1.001875 | 1.00875 | sim | 1.006189 | 1.00378 | sim |
| 26-35 \| non-binary \| UK | 189 | 1.003219 | 0.999591 | 1.007073 | nao | 1.002614 | 1.003991 | sim |
| 13-18 \| unknown \| Japan | 103 | 1.003126 | 0.998604 | 1.007704 | nao | 1.001799 | 1.004533 | sim |
| 26-35 \| unknown \| Germany | 205 | 1.003035 | 0.999637 | 1.006213 | nao | 1.005488 | 1.0007 | sim |
| 50+ \| female \| Russia | 128 | 1.002761 | 0.998931 | 1.006633 | nao | 1.00588 | 0.999641 | nao |
| 19-25 \| unknown \| Japan | 210 | 1.002584 | 0.999121 | 1.006466 | nao | 1.005382 | 0.999731 | nao |
| 26-35 \| non-binary \| Japan | 228 | 1.002577 | 0.999794 | 1.005751 | nao | 1.004952 | 0.999745 | nao |
| 36-50 \| male \| USA | 411 | 1.00248 | 1.000221 | 1.004908 | sim | 1.003552 | 1.00137 | sim |
| 19-25 \| female \| UK | 909 | 1.002139 | 1.000648 | 1.003734 | sim | 1.001157 | 1.003228 | sim |

### B1 personas (idade x genero x local) - 10 menores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| 19-25 \| unknown \| USA | 212 | 0.996523 | 0.993478 | 0.999802 | sim | 0.995963 | 0.997149 | sim |
| 50+ \| male \| Russia | 130 | 0.996722 | 0.992889 | 1.00068 | nao | 0.996318 | 0.997102 | sim |
| 50+ \| male \| USA | 114 | 0.996893 | 0.992931 | 1.001145 | nao | 0.997749 | 0.996149 | sim |
| 50+ \| female \| Japan | 114 | 0.996948 | 0.992111 | 1.00177 | nao | 0.995263 | 0.998692 | sim |
| 36-50 \| non-binary \| China | 107 | 0.997058 | 0.992261 | 1.001932 | nao | 0.994101 | 0.999557 | sim |
| 26-35 \| non-binary \| Brazil | 209 | 0.997213 | 0.994078 | 1.000399 | nao | 0.996111 | 0.998186 | sim |
| 26-35 \| unknown \| India | 192 | 0.99735 | 0.993839 | 1.000716 | nao | 0.998067 | 0.996676 | sim |
| 36-50 \| unknown \| Russia | 113 | 0.997358 | 0.992537 | 1.00234 | nao | 0.996995 | 0.997755 | sim |
| 50+ \| male \| Germany | 149 | 0.997397 | 0.993545 | 1.000691 | nao | 0.997896 | 0.997071 | sim |
| 13-18 \| non-binary \| Japan | 105 | 0.99754 | 0.993168 | 1.002032 | nao | 1.005526 | 0.989705 | nao |

### B2 content_category x audience_age_distribution - 10 maiores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| beauty \| 50+ | 1054 | 1.000661 | 0.999308 | 1.002075 | nao | 0.999935 | 1.001354 | nao |
| lifestyle \| 19-25 | 7250 | 1.000474 | 0.999919 | 1.00101 | nao | 1.000573 | 1.000375 | sim |
| beauty \| 36-50 | 3108 | 1.000259 | 0.999425 | 1.001052 | nao | 1.00042 | 1.00011 | sim |
| lifestyle \| 50+ | 1052 | 1.00019 | 0.998687 | 1.001583 | nao | 1.000546 | 0.999842 | nao |
| beauty \| 19-25 | 7399 | 1.000141 | 0.999559 | 1.000754 | nao | 1.000115 | 1.000167 | sim |
| tech \| 26-35 | 3117 | 1.0001 | 0.999205 | 1.000868 | nao | 1.001274 | 0.998933 | nao |
| lifestyle \| 13-18 | 3148 | 1.000085 | 0.999276 | 1.001003 | nao | 0.999223 | 1.00097 | nao |
| tech \| 19-25 | 3627 | 0.999956 | 0.999153 | 1.000745 | nao | 1.000299 | 0.999619 | nao |
| beauty \| 26-35 | 6343 | 0.999917 | 0.999372 | 1.000521 | nao | 0.999698 | 1.000137 | nao |
| tech \| 50+ | 544 | 0.999905 | 0.99795 | 1.001936 | nao | 0.998826 | 1.000938 | nao |

### B2 content_category x audience_age_distribution - 10 menores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| tech \| 36-50 | 1557 | 0.998769 | 0.997522 | 0.999988 | sim | 0.99924 | 0.998299 | sim |
| beauty \| 13-18 | 3119 | 0.999387 | 0.998565 | 1.000295 | nao | 0.999341 | 0.999432 | sim |
| tech \| 13-18 | 1585 | 0.999471 | 0.99826 | 1.000641 | nao | 1.000055 | 0.998887 | nao |
| lifestyle \| 26-35 | 6240 | 0.999834 | 0.999252 | 1.000483 | nao | 0.999609 | 1.000061 | nao |
| lifestyle \| 36-50 | 3071 | 0.999895 | 0.998994 | 1.000759 | nao | 0.999413 | 1.000384 | nao |
| tech \| 50+ | 544 | 0.999905 | 0.99795 | 1.001936 | nao | 0.998826 | 1.000938 | nao |
| beauty \| 26-35 | 6343 | 0.999917 | 0.999372 | 1.000521 | nao | 0.999698 | 1.000137 | nao |
| tech \| 19-25 | 3627 | 0.999956 | 0.999153 | 1.000745 | nao | 1.000299 | 0.999619 | nao |
| lifestyle \| 13-18 | 3148 | 1.000085 | 0.999276 | 1.001003 | nao | 0.999223 | 1.00097 | nao |
| tech \| 26-35 | 3117 | 1.0001 | 0.999205 | 1.000868 | nao | 1.001274 | 0.998933 | nao |

### B2 content_category x audience_gender_distribution - 10 maiores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| beauty \| unknown | 2117 | 1.000567 | 0.999584 | 1.001626 | nao | 1.000218 | 1.000907 | sim |
| lifestyle \| male | 8326 | 1.000292 | 0.999743 | 1.000806 | nao | 1.000018 | 1.000562 | sim |
| tech \| non-binary | 1003 | 1.000058 | 0.99854 | 1.00164 | nao | 1.000384 | 0.999724 | nao |
| lifestyle \| female | 8206 | 1.000029 | 0.999458 | 1.000545 | nao | 0.999827 | 1.000236 | nao |
| tech \| female | 4145 | 1.000013 | 0.999302 | 1.000782 | nao | 1.000428 | 0.999592 | nao |
| lifestyle \| unknown | 2100 | 0.999984 | 0.998839 | 1.001012 | nao | 1.000403 | 0.999585 | nao |
| lifestyle \| non-binary | 2129 | 0.999961 | 0.998874 | 1.000958 | nao | 0.99932 | 1.000687 | nao |
| beauty \| female | 8392 | 0.999957 | 0.999436 | 1.000447 | nao | 0.999833 | 1.000083 | nao |
| beauty \| non-binary | 2117 | 0.999954 | 0.998962 | 1.001043 | nao | 1.000703 | 0.999216 | nao |
| beauty \| male | 8397 | 0.999924 | 0.999408 | 1.000477 | nao | 0.999705 | 1.000138 | nao |

### B2 content_category x audience_gender_distribution - 10 menores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| tech \| unknown | 1018 | 0.998909 | 0.99733 | 1.000535 | nao | 0.99904 | 0.998789 | sim |
| tech \| male | 4264 | 0.999612 | 0.998883 | 1.000342 | nao | 1.000493 | 0.998754 | nao |
| beauty \| male | 8397 | 0.999924 | 0.999408 | 1.000477 | nao | 0.999705 | 1.000138 | nao |
| beauty \| non-binary | 2117 | 0.999954 | 0.998962 | 1.001043 | nao | 1.000703 | 0.999216 | nao |
| beauty \| female | 8392 | 0.999957 | 0.999436 | 1.000447 | nao | 0.999833 | 1.000083 | nao |
| lifestyle \| non-binary | 2129 | 0.999961 | 0.998874 | 1.000958 | nao | 0.99932 | 1.000687 | nao |
| lifestyle \| unknown | 2100 | 0.999984 | 0.998839 | 1.001012 | nao | 1.000403 | 0.999585 | nao |
| tech \| female | 4145 | 1.000013 | 0.999302 | 1.000782 | nao | 1.000428 | 0.999592 | nao |
| lifestyle \| female | 8206 | 1.000029 | 0.999458 | 1.000545 | nao | 0.999827 | 1.000236 | nao |
| tech \| non-binary | 1003 | 1.000058 | 0.99854 | 1.00164 | nao | 1.000384 | 0.999724 | nao |

### B2 content_category x audience_location - 10 maiores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| tech \| UK | 1247 | 1.00102 | 0.99976 | 1.002358 | nao | 1.001874 | 1.000132 | sim |
| beauty \| Russia | 2637 | 1.000834 | 0.999963 | 1.00168 | nao | 1.000954 | 1.000714 | sim |
| lifestyle \| UK | 2625 | 1.000784 | 0.999833 | 1.00167 | nao | 1.000108 | 1.00149 | sim |
| lifestyle \| Brazil | 2635 | 1.000702 | 0.999746 | 1.001649 | nao | 1.000461 | 1.000955 | sim |
| lifestyle \| USA | 2576 | 1.000532 | 0.999659 | 1.001526 | nao | 1.0005 | 1.000564 | sim |
| lifestyle \| Japan | 2616 | 1.00041 | 0.999522 | 1.001378 | nao | 1.000408 | 1.000411 | sim |
| beauty \| China | 2643 | 1.000381 | 0.999422 | 1.001242 | nao | 1.000204 | 1.000565 | sim |
| beauty \| Brazil | 2597 | 1.000066 | 0.99911 | 1.000947 | nao | 1.00032 | 0.999817 | nao |
| tech \| Brazil | 1273 | 1.000049 | 0.998557 | 1.001286 | nao | 1.000559 | 0.999547 | nao |
| beauty \| UK | 2698 | 0.999971 | 0.999031 | 1.000874 | nao | 0.999621 | 1.000309 | nao |

### B2 content_category x audience_location - 10 menores lifts de taxa_engajamento

| segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|
| tech \| India | 1283 | 0.998644 | 0.997285 | 1.000106 | nao | 0.998702 | 0.998585 | sim |
| lifestyle \| Russia | 2548 | 0.999139 | 0.998166 | 1.000109 | nao | 0.998798 | 0.999489 | sim |
| beauty \| India | 2584 | 0.99937 | 0.998411 | 1.000318 | nao | 0.999526 | 0.999205 | sim |
| tech \| Japan | 1323 | 0.999386 | 0.998093 | 1.000663 | nao | 0.999075 | 0.999696 | sim |
| lifestyle \| Germany | 2523 | 0.99955 | 0.99858 | 1.000536 | nao | 0.999509 | 0.999591 | sim |
| tech \| Germany | 1335 | 0.999598 | 0.998215 | 1.00089 | nao | 1.001511 | 0.997698 | nao |
| tech \| China | 1384 | 0.999678 | 0.99832 | 1.000945 | nao | 1.000443 | 0.998923 | nao |
| beauty \| USA | 2611 | 0.999686 | 0.998769 | 1.000679 | nao | 0.998869 | 1.00049 | nao |
| tech \| USA | 1311 | 0.999744 | 0.998352 | 1.001118 | nao | 0.99996 | 0.99953 | sim |
| beauty \| Germany | 2639 | 0.999817 | 0.998952 | 1.000826 | nao | 0.999509 | 1.000114 | nao |

### B3. Audiencia x patrocinio (estratos platform x content_category, minimo de 20 patrocinados e 20 organicos)

Efeito = media das razoes (media patrocinado / media organico) ponderada pelo tamanho do estrato.

| variavel | valor | metrica | n_patrocinado | n_organico | estratos_usados | efeito | ic_inferior | ic_superior | ic_exclui_1 | efeito_metade_A | efeito_metade_B |
|---|---|---|---|---|---|---|---|---|---|---|---|
| audience_age_distribution | 13-18 | taxa_engajamento | 3295 | 4557 | 15 | 1.000024 | 0.998942 | 1.001147 | nao | 0.999747 | 1.000313 |
| audience_age_distribution | 13-18 | shares | 3295 | 4557 | 15 | 0.998382 | 0.995901 | 1.001004 | nao | 0.997387 | 0.999431 |
| audience_age_distribution | 13-18 | comments_count | 3295 | 4557 | 15 | 0.998979 | 0.995865 | 1.002393 | nao | 0.997451 | 1.000489 |
| audience_age_distribution | 19-25 | taxa_engajamento | 7858 | 10418 | 15 | 1.000313 | 0.999543 | 1.001013 | nao | 0.999935 | 1.000685 |
| audience_age_distribution | 19-25 | shares | 7858 | 10418 | 15 | 1.000298 | 0.998704 | 1.002089 | nao | 1.000297 | 1.000313 |
| audience_age_distribution | 19-25 | comments_count | 7858 | 10418 | 15 | 1.000493 | 0.998476 | 1.002435 | nao | 1.001397 | 0.999607 |
| audience_age_distribution | 26-35 | taxa_engajamento | 6680 | 9020 | 15 | 0.999853 | 0.999104 | 1.000605 | nao | 0.999733 | 0.999896 |
| audience_age_distribution | 26-35 | shares | 6680 | 9020 | 15 | 0.999343 | 0.997587 | 1.00109 | nao | 0.999762 | 0.998925 |
| audience_age_distribution | 26-35 | comments_count | 6680 | 9020 | 15 | 1.001705 | 0.999496 | 1.003841 | nao | 1.001432 | 1.001944 |
| audience_age_distribution | 36-50 | taxa_engajamento | 3353 | 4383 | 15 | 0.998952 | 0.997871 | 0.999977 | sim | 0.99926 | 0.998598 |
| audience_age_distribution | 36-50 | shares | 3353 | 4383 | 15 | 0.999465 | 0.99698 | 1.001916 | nao | 0.996563 | 1.002422 |
| audience_age_distribution | 36-50 | comments_count | 3353 | 4383 | 15 | 0.998079 | 0.995052 | 1.001164 | nao | 0.997294 | 0.998992 |
| audience_age_distribution | 50+ | taxa_engajamento | 1128 | 1522 | 15 | 1.000529 | 0.99864 | 1.002407 | nao | 1.000725 | 1.000667 |
| audience_age_distribution | 50+ | shares | 1128 | 1522 | 15 | 0.999421 | 0.995329 | 1.00394 | nao | 1.000288 | 0.999659 |
| audience_age_distribution | 50+ | comments_count | 1128 | 1522 | 15 | 0.99853 | 0.993311 | 1.003975 | nao | 1.000441 | 0.996678 |
| audience_gender_distribution | female | taxa_engajamento | 8868 | 11875 | 15 | 0.999757 | 0.999052 | 1.000382 | nao | 0.999793 | 0.999704 |
| audience_gender_distribution | female | shares | 8868 | 11875 | 15 | 0.999094 | 0.997478 | 1.000687 | nao | 0.998652 | 0.999511 |
| audience_gender_distribution | female | comments_count | 8868 | 11875 | 15 | 1.00033 | 0.998243 | 1.002198 | nao | 1.000544 | 1.00017 |
| audience_gender_distribution | male | taxa_engajamento | 8988 | 11999 | 15 | 0.99982 | 0.999186 | 1.000515 | nao | 0.999533 | 1.000091 |
| audience_gender_distribution | male | shares | 8988 | 11999 | 15 | 1.000006 | 0.998459 | 1.001546 | nao | 0.999514 | 1.000553 |
| audience_gender_distribution | male | comments_count | 8988 | 11999 | 15 | 1.00031 | 0.998501 | 1.002215 | nao | 0.999571 | 1.001048 |
| audience_gender_distribution | non-binary | taxa_engajamento | 2254 | 2995 | 15 | 0.99967 | 0.998242 | 1.000998 | nao | 0.999271 | 1.000034 |
| audience_gender_distribution | non-binary | shares | 2254 | 2995 | 15 | 0.99653 | 0.993276 | 0.999933 | sim | 0.994391 | 0.99853 |
| audience_gender_distribution | non-binary | comments_count | 2254 | 2995 | 15 | 1.000632 | 0.996668 | 1.004446 | nao | 1.001097 | 1.000311 |
| audience_gender_distribution | unknown | taxa_engajamento | 2204 | 3031 | 15 | 1.001414 | 1.000091 | 1.002753 | sim | 1.001295 | 1.001522 |
| audience_gender_distribution | unknown | shares | 2204 | 3031 | 15 | 1.002848 | 0.999966 | 1.005917 | nao | 1.004079 | 1.001669 |
| audience_gender_distribution | unknown | comments_count | 2204 | 3031 | 15 | 0.998665 | 0.994805 | 1.002944 | nao | 1.000591 | 0.997084 |
| audience_location | Brazil | taxa_engajamento | 2769 | 3736 | 15 | 0.999607 | 0.998433 | 1.000842 | nao | 0.9994 | 0.999782 |
| audience_location | Brazil | shares | 2769 | 3736 | 15 | 1.000407 | 0.997676 | 1.003141 | nao | 1.000735 | 1.000071 |
| audience_location | Brazil | comments_count | 2769 | 3736 | 15 | 0.999531 | 0.996046 | 1.003062 | nao | 0.998191 | 1.000847 |
| audience_location | China | taxa_engajamento | 2789 | 3859 | 15 | 1.000277 | 0.998997 | 1.001477 | nao | 0.999555 | 1.000965 |
| audience_location | China | shares | 2789 | 3859 | 15 | 0.998889 | 0.995967 | 1.001506 | nao | 1.00108 | 0.996749 |
| audience_location | China | comments_count | 2789 | 3859 | 15 | 1.001842 | 0.998421 | 1.005278 | nao | 1.002169 | 1.001239 |
| audience_location | Germany | taxa_engajamento | 2791 | 3706 | 15 | 0.998999 | 0.997767 | 1.000198 | nao | 0.998644 | 0.999389 |
| audience_location | Germany | shares | 2791 | 3706 | 15 | 0.999282 | 0.996577 | 1.002148 | nao | 0.997097 | 1.001365 |
| audience_location | Germany | comments_count | 2791 | 3706 | 15 | 0.998408 | 0.994967 | 1.001586 | nao | 0.995906 | 1.000786 |
| audience_location | India | taxa_engajamento | 2815 | 3669 | 15 | 1.000235 | 0.998956 | 1.001453 | nao | 1.000099 | 1.000326 |
| audience_location | India | shares | 2815 | 3669 | 15 | 0.998127 | 0.99536 | 1.000876 | nao | 0.998077 | 0.998191 |
| audience_location | India | comments_count | 2815 | 3669 | 15 | 1.000751 | 0.996971 | 1.004388 | nao | 1.001531 | 0.999985 |
| audience_location | Japan | taxa_engajamento | 2753 | 3800 | 15 | 1.000244 | 0.999013 | 1.001397 | nao | 1.000856 | 0.999549 |
| audience_location | Japan | shares | 2753 | 3800 | 15 | 0.99846 | 0.995508 | 1.001227 | nao | 0.997285 | 0.999615 |
| audience_location | Japan | comments_count | 2753 | 3800 | 15 | 1.000927 | 0.997503 | 1.004179 | nao | 1.000338 | 1.001099 |
| audience_location | Russia | taxa_engajamento | 2734 | 3725 | 15 | 1.000555 | 0.999318 | 1.00179 | nao | 1.000502 | 1.00059 |
| audience_location | Russia | shares | 2734 | 3725 | 15 | 1.001863 | 0.999012 | 1.004535 | nao | 1.000796 | 1.002909 |
| audience_location | Russia | comments_count | 2734 | 3725 | 15 | 0.997822 | 0.994263 | 1.001239 | nao | 0.998769 | 0.996779 |
| audience_location | UK | taxa_engajamento | 2885 | 3685 | 15 | 0.999427 | 0.998321 | 1.000588 | nao | 0.998977 | 0.99993 |
| audience_location | UK | shares | 2885 | 3685 | 15 | 1.000121 | 0.997185 | 1.003061 | nao | 0.999702 | 1.000828 |
| audience_location | UK | comments_count | 2885 | 3685 | 15 | 1.000892 | 0.997399 | 1.00425 | nao | 1.00079 | 1.000848 |
| audience_location | USA | taxa_engajamento | 2778 | 3720 | 15 | 1.000347 | 0.99911 | 1.001572 | nao | 1.000368 | 1.000265 |
| audience_location | USA | shares | 2778 | 3720 | 15 | 0.999557 | 0.996346 | 1.002224 | nao | 0.998226 | 1.000897 |
| audience_location | USA | comments_count | 2778 | 3720 | 15 | 1.001669 | 0.99847 | 1.005301 | nao | 1.003386 | 0.999734 |

## Testes contra o acaso

| conjunto | metrica | segmentos_existentes | segmentos_avaliados | segmentos_fora_por_n_minimo | posts_fora_por_n_minimo | maior_lift_observado | acaso_p95_dos_maiores | maior_observado_acima_do_acaso | menor_lift_observado | acaso_p5_dos_menores | menor_observado_abaixo_do_acaso |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A3 sponsor_category x content_category (so patrocinados) | taxa_engajamento | 18 | 18 | 0 | 0 | 1.001446 | 1.002177 | nao | 0.99858 | 0.997784 | nao |
| A3 sponsor_category x content_category (so patrocinados) | shares | 18 | 18 | 0 | 0 | 1.003791 | 1.004769 | nao | 0.99562 | 0.99489 | nao |
| A3 sponsor_category x content_category (so patrocinados) | comments_count | 18 | 18 | 0 | 0 | 1.003724 | 1.005993 | nao | 0.997909 | 0.993925 | nao |
| B1 personas (idade x genero x local) | taxa_engajamento | 160 | 126 | 34 | 2157 | 1.005435 | 1.00645 | nao | 0.996523 | 0.993089 | nao |
| B1 personas (idade x genero x local) | shares | 160 | 126 | 34 | 2157 | 1.01102 | 1.015717 | nao | 0.989645 | 0.984331 | nao |
| B1 personas (idade x genero x local) | comments_count | 160 | 126 | 34 | 2157 | 1.009605 | 1.019881 | nao | 0.990042 | 0.98014 | nao |
| B2 content_category x audience_age_distribution | taxa_engajamento | 15 | 15 | 0 | 0 | 1.000661 | 1.001871 | nao | 0.998769 | 0.998276 | nao |
| B2 content_category x audience_age_distribution | shares | 15 | 15 | 0 | 0 | 1.001096 | 1.004931 | nao | 0.998441 | 0.995676 | nao |
| B2 content_category x audience_age_distribution | comments_count | 15 | 15 | 0 | 0 | 1.00256 | 1.005547 | nao | 0.997251 | 0.994942 | nao |
| B2 content_category x audience_gender_distribution | taxa_engajamento | 12 | 12 | 0 | 0 | 1.000567 | 1.001539 | nao | 0.998909 | 0.99848 | nao |
| B2 content_category x audience_gender_distribution | shares | 12 | 12 | 0 | 0 | 1.001831 | 1.00381 | nao | 0.998888 | 0.996611 | nao |
| B2 content_category x audience_gender_distribution | comments_count | 12 | 12 | 0 | 0 | 1.002054 | 1.004256 | nao | 0.999027 | 0.995646 | nao |
| B2 content_category x audience_location | taxa_engajamento | 24 | 24 | 0 | 0 | 1.00102 | 1.001757 | nao | 0.998644 | 0.998253 | nao |
| B2 content_category x audience_location | shares | 24 | 24 | 0 | 0 | 1.001909 | 1.003917 | nao | 0.998188 | 0.996117 | nao |
| B2 content_category x audience_location | comments_count | 24 | 24 | 0 | 0 | 1.002594 | 1.004944 | nao | 0.997076 | 0.995429 | nao |

## Pontos suspeitos ou problemas encontrados

- `sponsor_category` esta praticamente uniforme dentro de cada `content_category`, entao a proporcao de posts com fit e definida pela regra da tabela de fit, nao pelos dados: beauty 16.8384%; lifestyle 49.9944%; tech 33.1554%.
- A2 deixou 18 de 60 estratos de fora (1279 posts patrocinados, 5.73%) por nao atingirem 20 posts em um dos grupos; as faixas 'ate 50K' e '50-100K' tem poucos posts.
- Conjuntos de B com segmentos abaixo do n minimo: audience_age_distribution x audience_gender_distribution x audience_location (34 de 160, 2157 posts).
- Nenhum extremo observado ficou fora da faixa do acaso em nenhum conjunto.
- Conjuntos com menos de 20 segmentos: as listas dos 10 maiores e dos 10 menores lifts se sobrepoem (B2 content_category x audience_age_distribution; B2 content_category x audience_gender_distribution).
- Linhas com IC que exclui 1 nas tabelas de segmentos (A3, B1, B2): 18 de 585.
