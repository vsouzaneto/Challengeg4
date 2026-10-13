# Resumo OS-06 — Lacunas finais: alcance e formato × audiência

Base: 52.214 posts (`datasets/social_media_dataset.csv`).
Script: `solution/analysis/os06_lacunas.py`. Saídas em `solution/outputs/os06/`.
Seed 42 em tudo. IC 95% por bootstrap percentil com 1.000 reamostragens.
Teste de repetição: a mesma divisão em duas metades da OS-02 (A = 26.107, B = 26.107).
Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
Volume por grupo: 22.314 posts patrocinados e 29.900 orgânicos.

---

# Parte 1 — Alcance: views patrocinado vs. orgânico

## 1a — Comparação simples

| item | n | valor | ic_inferior | ic_superior | mediana | ic_exclui_1 |
|---|---|---|---|---|---|---|
| patrocinado | 22.314 | 10.100,45 | 10.099,16 | 10.101,78 | 10.100,00 |  |
| organico | 29.900 | 10.100,16 | 10.098,96 | 10.101,24 | 10.100,00 |  |
| razao_medias_patrocinado_organico | 52.214 | 1,000029 | 0,999868 | 1,000195 | - | nao |

`valor` = média de views nas duas primeiras linhas e razão das médias na terceira.

## 1b — Comparação estratificada

Estratos: platform × content_category × content_type × faixa_seguidores.
Critério: pelo menos 30 posts patrocinados **e** 30 orgânicos por estrato.
Efeito = média das razões (média patrocinado / média orgânico) ponderada pelo tamanho do estrato.
IC 95% por bootstrap estratificado (reamostragem dentro de cada estrato e de cada grupo).

| campo | valor |
|---|---|
| metrica | views |
| estratos_existentes | 240 |
| estratos_usados | 141 |
| posts_usados | 49487 |
| posts_fora | 2727 |
| n_patrocinado_usado | 21174 |
| n_organico_usado | 28313 |
| efeito_geral | 1,000054 |
| ic_inferior | 0,999869 |
| ic_superior | 1,000208 |
| ic_exclui_1 | nao |
| efeito_metade_A | 1,000021 |
| efeito_metade_B | 1,000079 |
| pct_estratos_razao_maior_1 | 50,35 |
| razao_minimo | 0,996281 |
| razao_p5 | 0,998053 |
| razao_mediana | 1,000008 |
| razao_p95 | 1,002432 |
| razao_maximo | 1,003833 |
| comparacao_simples_sem_estratos | 1,000029 |

## 1c — Por faixa de seguidores

Estratos: platform × content_category, mínimo de 20 patrocinados e 20 orgânicos por estrato.

| faixa_seguidores | n_patrocinado | n_organico | estratos_existentes | estratos_usados | efeito | ic_inferior | ic_superior | ic_exclui_1 | efeito_metade_A | efeito_metade_B |
|---|---|---|---|---|---|---|---|---|---|---|
| ate 50K | 1.114 | 1.450 | 15 | 15 | 0,999723 | 0,999014 | 1,000533 | nao | 0,999497 | 1,000114 |
| 50-100K | 1.109 | 1.488 | 15 | 15 | 1,000154 | 0,999346 | 1,000951 | nao | 1,000051 | 1,000200 |
| 100-500K | 8.967 | 12.057 | 15 | 15 | 1,000071 | 0,999799 | 1,000336 | nao | 1,000163 | 0,999980 |
| 500K-1M | 11.124 | 14.905 | 15 | 15 | 1,000013 | 0,999761 | 1,000251 | nao | 0,999919 | 1,000111 |

## 1d — Mediana de views por faixa de seguidores × is_sponsored

| faixa_seguidores | is_sponsored | n | mediana_views | media_views |
|---|---|---|---|---|
| ate 50K | True | 1.114 | 10.098,00 | 10.097,73 |
| ate 50K | False | 1.450 | 10.097,00 | 10.100,69 |
| 50-100K | True | 1.109 | 10.097,00 | 10.099,23 |
| 50-100K | False | 1.488 | 10.100,00 | 10.097,58 |
| 100-500K | True | 8.967 | 10.100,00 | 10.100,09 |
| 100-500K | False | 12.057 | 10.100,00 | 10.099,38 |
| 500K-1M | True | 11.124 | 10.101,00 | 10.101,13 |
| 500K-1M | False | 14.905 | 10.101,00 | 10.101,00 |

---

# Parte 2 — Formato × audiência

Índice por post = valor / média da métrica na plataforma do post. Lift = média do índice no segmento.
Só segmentos com n ≥ 100.

## Cobertura dos segmentos

| variaveis | segmentos_existentes | segmentos_mantidos | segmentos_fora_por_n_menor_100 | posts_fora |
|---|---|---|---|---|
| content_type x audience_age_distribution | 20 | 20 | 0 | 0 |
| content_type x audience_gender_distribution | 16 | 16 | 0 | 0 |
| content_type x audience_location | 32 | 32 | 0 | 0 |

## Distribuição dos lifts por conjunto e métrica

| variaveis | metrica | segmentos | minimo | p5 | mediana | p95 | maximo | acima_1_03 | acima_1_05 | acima_1_10 | abaixo_0_97 | abaixo_0_95 | abaixo_0_90 | ic_exclui_1_sim | mesmo_lado_sim |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| content_type x audience_age_distribution | taxa_engajamento | 20 | 0,999271 | 0,999290 | 1,000199 | 1,001299 | 1,001334 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 8 |
| content_type x audience_age_distribution | shares | 20 | 0,997000 | 0,997250 | 1,000523 | 1,002688 | 1,004961 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 13 |
| content_type x audience_age_distribution | comments_count | 20 | 0,997046 | 0,998134 | 0,999779 | 1,004211 | 1,007754 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 8 |
| content_type x audience_gender_distribution | taxa_engajamento | 16 | 0,999554 | 0,999651 | 1,000171 | 1,000786 | 1,000800 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| content_type x audience_gender_distribution | shares | 16 | 0,996425 | 0,997770 | 1,000548 | 1,002193 | 1,003257 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| content_type x audience_gender_distribution | comments_count | 16 | 0,994353 | 0,995282 | 1,000846 | 1,003079 | 1,004368 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 11 |
| content_type x audience_location | taxa_engajamento | 32 | 0,998945 | 0,999241 | 1,000146 | 1,001522 | 1,002320 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 17 |
| content_type x audience_location | shares | 32 | 0,996803 | 0,997387 | 1,000282 | 1,002544 | 1,006007 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19 |
| content_type x audience_location | comments_count | 32 | 0,995016 | 0,997452 | 1,000126 | 1,003323 | 1,003940 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 |

## 5 maiores e 5 menores lifts de `taxa_engajamento` por conjunto

| grupo | variaveis | segmento | n | lift | ic_inferior | ic_superior | ic_exclui_1 | lift_metade_A | lift_metade_B | mesmo_lado_nas_duas_metades |
|---|---|---|---|---|---|---|---|---|---|---|
| 5_maiores | content_type x audience_age_distribution | text \| 50+ | 254 | 1,001334 | 0,997859 | 1,004445 | nao | 0,999040 | 1,003294 | nao |
| 5_maiores | content_type x audience_age_distribution | mixed \| 19-25 | 1.791 | 1,001297 | 1,000188 | 1,002461 | sim | 1,001535 | 1,001056 | sim |
| 5_maiores | content_type x audience_age_distribution | text \| 36-50 | 774 | 1,001050 | 0,999356 | 1,002803 | nao | 1,000586 | 1,001496 | sim |
| 5_maiores | content_type x audience_age_distribution | text \| 26-35 | 1.533 | 1,000481 | 0,999177 | 1,001787 | nao | 0,999945 | 1,001000 | nao |
| 5_maiores | content_type x audience_age_distribution | image \| 13-18 | 1.488 | 1,000473 | 0,999240 | 1,001642 | nao | 0,999884 | 1,001062 | nao |
| 5_menores | content_type x audience_age_distribution | image \| 36-50 | 1.573 | 0,999271 | 0,998123 | 1,000472 | nao | 0,999623 | 0,998918 | sim |
| 5_menores | content_type x audience_age_distribution | video \| 13-18 | 4.836 | 0,999291 | 0,998618 | 0,999954 | sim | 0,999000 | 0,999588 | sim |
| 5_menores | content_type x audience_age_distribution | mixed \| 50+ | 275 | 0,999475 | 0,996824 | 1,002292 | nao | 1,000144 | 0,998876 | nao |
| 5_menores | content_type x audience_age_distribution | mixed \| 36-50 | 780 | 0,999601 | 0,998047 | 1,001343 | nao | 0,998243 | 1,000987 | nao |
| 5_menores | content_type x audience_age_distribution | video \| 26-35 | 9.494 | 0,999734 | 0,999247 | 1,000207 | nao | 0,999839 | 0,999627 | sim |
| 5_maiores | content_type x audience_gender_distribution | mixed \| non-binary | 530 | 1,000800 | 0,998817 | 1,003157 | nao | 1,001550 | 1,000034 | sim |
| 5_maiores | content_type x audience_gender_distribution | mixed \| female | 2.038 | 1,000781 | 0,999788 | 1,001869 | nao | 1,000105 | 1,001458 | sim |
| 5_maiores | content_type x audience_gender_distribution | text \| male | 2.144 | 1,000746 | 0,999763 | 1,001758 | nao | 1,001335 | 1,000203 | sim |
| 5_maiores | content_type x audience_gender_distribution | mixed \| unknown | 547 | 1,000699 | 0,998698 | 1,002714 | nao | 1,000874 | 1,000543 | sim |
| 5_maiores | content_type x audience_gender_distribution | text \| non-binary | 499 | 1,000674 | 0,998608 | 1,002668 | nao | 1,000571 | 1,000785 | sim |
| 5_menores | content_type x audience_gender_distribution | image \| non-binary | 1.046 | 0,999554 | 0,998112 | 1,001090 | nao | 1,000033 | 0,999039 | nao |
| 5_menores | content_type x audience_gender_distribution | image \| female | 4.183 | 0,999683 | 0,998986 | 1,000389 | nao | 0,999990 | 0,999372 | sim |
| 5_menores | content_type x audience_gender_distribution | video \| unknown | 3.167 | 0,999746 | 0,998920 | 1,000601 | nao | 0,999587 | 0,999896 | sim |
| 5_menores | content_type x audience_gender_distribution | video \| male | 12.674 | 0,999834 | 0,999417 | 1,000265 | nao | 0,999799 | 0,999868 | sim |
| 5_menores | content_type x audience_gender_distribution | video \| non-binary | 3.174 | 0,999869 | 0,999036 | 1,000782 | nao | 0,999744 | 1,000000 | nao |
| 5_maiores | content_type x audience_location | mixed \| Brazil | 636 | 1,002320 | 1,000274 | 1,004143 | sim | 1,003054 | 1,001638 | sim |
| 5_maiores | content_type x audience_location | text \| Russia | 642 | 1,001875 | 1,000060 | 1,003656 | sim | 1,002287 | 1,001476 | sim |
| 5_maiores | content_type x audience_location | mixed \| Russia | 621 | 1,001233 | 0,999093 | 1,003236 | nao | 1,001191 | 1,001274 | sim |
| 5_maiores | content_type x audience_location | text \| UK | 649 | 1,001134 | 0,999275 | 1,003043 | nao | 1,000234 | 1,002112 | sim |
| 5_maiores | content_type x audience_location | text \| Brazil | 660 | 1,000860 | 0,999031 | 1,002652 | nao | 1,001054 | 1,000663 | sim |
| 5_menores | content_type x audience_location | image \| Japan | 1.304 | 0,998945 | 0,997672 | 1,000306 | nao | 0,998935 | 0,998955 | sim |
| 5_menores | content_type x audience_location | video \| India | 3.877 | 0,999203 | 0,998458 | 1,000018 | nao | 0,998788 | 0,999624 | sim |
| 5_menores | content_type x audience_location | text \| Germany | 606 | 0,999272 | 0,997333 | 1,001135 | nao | 0,999415 | 0,999133 | sim |
| 5_menores | content_type x audience_location | mixed \| China | 655 | 0,999287 | 0,997489 | 1,000999 | nao | 1,000126 | 0,998336 | nao |
| 5_menores | content_type x audience_location | mixed \| India | 680 | 0,999361 | 0,997462 | 1,001143 | nao | 0,998588 | 1,000093 | nao |

---

# Teste contra o acaso

Índice embaralhado dentro de cada plataforma, 200 repetições. Em cada repetição são recalculados
todos os segmentos do conjunto e guardados o maior e o menor lift.

| variaveis | metrica | segmentos_avaliados | maior_lift_observado | acaso_p95_dos_maiores | maior_observado_acima_do_acaso | menor_lift_observado | acaso_p5_dos_menores | menor_observado_abaixo_do_acaso |
|---|---|---|---|---|---|---|---|---|
| content_type x audience_age_distribution | taxa_engajamento | 20 | 1,001334 | 1,002930 | nao | 0,999271 | 0,997124 | nao |
| content_type x audience_age_distribution | shares | 20 | 1,004961 | 1,007056 | nao | 0,997000 | 0,992664 | nao |
| content_type x audience_age_distribution | comments_count | 20 | 1,007754 | 1,007570 | sim | 0,997046 | 0,991618 | nao |
| content_type x audience_gender_distribution | taxa_engajamento | 16 | 1,000800 | 1,002199 | nao | 0,999554 | 0,997621 | nao |
| content_type x audience_gender_distribution | shares | 16 | 1,003257 | 1,005578 | nao | 0,996425 | 0,994712 | nao |
| content_type x audience_gender_distribution | comments_count | 16 | 1,004368 | 1,006525 | nao | 0,994353 | 0,992643 | nao |
| content_type x audience_location | taxa_engajamento | 32 | 1,002320 | 1,002709 | nao | 0,998945 | 0,997410 | nao |
| content_type x audience_location | shares | 32 | 1,006007 | 1,006172 | nao | 0,996803 | 0,993968 | nao |
| content_type x audience_location | comments_count | 32 | 1,003940 | 1,007371 | nao | 0,995016 | 0,992656 | nao |

---

# Pontos suspeitos ou problemas encontrados

1. **Views de patrocinado e orgânico são praticamente iguais.** A razão das médias é
   1,000029 com IC 95% [0,999868; 1,000195], que
   inclui 1. As médias são 10.100,45
   (patrocinado) e 10.100,16 (orgânico), diferença de
   0,29 views por post.
2. **A estratificação não muda nada.** O efeito estratificado de 1b é 1,000054
   (IC [0,999869; 1,000208], inclui 1)
   contra 1,000029 na comparação simples. As 141
   razões por estrato ficam entre 0,996281 e 1,003833, e
   50,35% delas estão acima de 1 — próximo dos 50% de um sorteio.
3. **1b descarta 99 dos 240 estratos**
   pelo mínimo de 30+30, o que deixa 2.727 posts
   (5,22% da base) fora do cálculo.
4. **Nenhuma faixa de seguidores se destaca em 1c:** 0 de
   4 IC excluem 1, e 1 de 4 faixas têm as duas
   metades do mesmo lado de 1. Os efeitos ficam entre 0,999723 e
   1,000154.
5. **As 8 células de 1d têm medianas quase idênticas.** A maior diferença absoluta entre
   patrocinado e orgânico dentro de uma faixa é de 3,00 views
   (faixa "50-100K"), sobre medianas da ordem de 10.099 views.
6. **Os lifts da Parte 2 são todos planos:** 204 linhas segmento × métrica com lift
   entre 0,994353 e 1,007754. As 54 contagens de
   limiar (>1,03 / >1,05 / >1,10 e <0,97 / <0,95 / <0,90) somam 0.
7. **Quase nenhum IC da Parte 2 exclui 1:** 11 de 204.
8. **O teste de repetição acerta o lado em 109 de 204 casos**
   (53,4%), contra 50% esperados por sorteio.
9. **Teste contra o acaso: 1 de 18 comparações ficam fora do
   acaso.** Fora do acaso: maior lift de `comments_count` em content_type x audience_age_distribution (1,007754 contra p95 do acaso 1,007570). Nas outras 17 comparações os
   extremos observados são menos extremos que os das permutações, o mesmo padrão já registrado na
   OS-02 e na OS-03b.
10. O padrão geral repete o das OS anteriores: as variáveis da base não separam desempenho nem
    em alcance (Parte 1) nem em formato × audiência (Parte 2). Nenhum número foi alterado.
