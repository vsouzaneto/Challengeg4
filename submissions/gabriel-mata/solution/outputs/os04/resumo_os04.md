# OS-04 — Complementos

Script: `solution/analysis/os04_complementos.py`
Fonte: `datasets/social_media_dataset.csv` (52.214 posts)
Saídas: `solution/outputs/os04/` (4 arquivos .csv)

**Regras mantidas:** `engajamento` = likes + shares + comments_count; `taxa_engajamento` = engajamento / views; faixas de seguidores até 50K, 50–100K, 100–500K, 500K–1M; seed 42.

| Arquivo | Conteúdo |
|---|---|
| `item1_sanidade.csv` | os 27 indicadores de sanidade (indicador, valor) |
| `item2_hashtags.csv` | as 970 hashtags testadas × 2 métricas, com lift, p-valor e q-valor BH (1.940 linhas) |
| `item3_efeito_absoluto.csv` | efeito máximo plausível em % e em unidades absolutas (105 linhas) |
| `item4_tamanho_amostra.csv` | n por variante para 6 CV × 4 lifts (24 linhas) |

---

## 1. Tabela de sanidade

| indicador | valor |
|---|---|
| 1. mediana de views - faixa ate 50K (n=2564) | 10.097 |
| 1. mediana de views - faixa 50-100K (n=2597) | 10.099 |
| 1. mediana de views - faixa 100-500K (n=21024) | 10.100 |
| 1. mediana de views - faixa 500K-1M (n=26029) | 10.101 |
| 2. correlação de Pearson likes × views | 0,000761 |
| 2. correlação de Spearman likes × views | 0,001490 |
| 3. correlação de Pearson log10(follower_count) × log10(views) | 0,005644 |
| 4. variância ÷ média - views | 0,990585 |
| 4. variância ÷ média - likes | 1,002983 |
| 4. variância ÷ média - shares | 0,998600 |
| 4. variância ÷ média - comments_count | 0,993115 |
| 5. engajamento no percentil 1 ÷ mediana do engajamento | 0,948756 |
| 6. % de posts com engajamento < 10% da mediana | 0 |
| 7. mínimo de views | 9.676 |
| 7. máximo de views | 10.551 |
| 7. mínimo de engajamento | 1.833 |
| 7. máximo de engajamento | 2.189 |
| 8. % de creator_id em uma única plataforma (de 5000 creators) | 0 |
| 9. % de creator_id com o mesmo follower_count em todos os posts | 0 |
| 10. V de Cramér language × audience_location (5×8) | 0,011294 |
| 11. sponsor_name distintos entre os posts patrocinados | 18.005 |
| 11. total de posts patrocinados | 22.314 |
| 12. % de posts em Bilibili + RedNote | 40,219098 |
| 13. mediana de content_length - image (n=10303) | 173 |
| 13. mediana de content_length - mixed (n=5213) | 175 |
| 13. mediana de content_length - text (n=5198) | 174 |
| 13. mediana de content_length - video (n=31500) | 174 |

---

## 2. Hashtags com correção de testes múltiplos

**Universo:** 43.471 posts com `hashtags` preenchido (83,26% da base); 8.743 posts com nulo ficaram fora. 972 hashtags distintas, 970 com n ≥ 100. Comparação: posts com a hashtag × posts do universo sem a hashtag; teste t de Welch; correção de Benjamini-Hochberg com FDR de 5% aplicada separadamente por métrica.

### Resumo por métrica

| Métrica | Hashtags testadas | p < 0,05 sem correção | Esperadas por acaso | Significativas após BH | Menor lift | Maior lift |
|---|---|---|---|---|---|---|
| taxa_engajamento | 970 | 61 | 48,50 | 0 | 0,992744 | 1,006523 |
| shares | 970 | 57 | 48,50 | 0 | 0,984085 | 1,016026 |

### 10 hashtags de maior lift em cada métrica

| Métrica | Hashtag | n com | n sem | Lift | p-valor | q-valor (BH) |
|---|---|---|---|---|---|---|
| taxa_engajamento | range | 119 | 43.352 | 1,006523 | 0,002887 | 0,756957 |
| taxa_engajamento | stay | 154 | 43.317 | 1,006254 | 0,005036 | 0,756957 |
| taxa_engajamento | amount | 127 | 43.344 | 1,006145 | 0,004297 | 0,756957 |
| taxa_engajamento | Mrs | 122 | 43.349 | 1,005978 | 0,020576 | 0,756957 |
| taxa_engajamento | thus | 129 | 43.342 | 1,005841 | 0,009397 | 0,756957 |
| taxa_engajamento | rather | 125 | 43.346 | 1,005546 | 0,008734 | 0,756957 |
| taxa_engajamento | listen | 137 | 43.334 | 1,005446 | 0,012634 | 0,756957 |
| taxa_engajamento | hard | 142 | 43.329 | 1,005440 | 0,009580 | 0,756957 |
| taxa_engajamento | center | 135 | 43.336 | 1,005384 | 0,020196 | 0,756957 |
| taxa_engajamento | people | 134 | 43.337 | 1,005356 | 0,006043 | 0,756957 |
| shares | still | 136 | 43.335 | 1,016026 | 0,002613 | 0,422463 |
| shares | defense | 112 | 43.359 | 1,014588 | 0,004127 | 0,571895 |
| shares | process | 149 | 43.322 | 1,014260 | 0,002500 | 0,422463 |
| shares | common | 140 | 43.331 | 1,013893 | 0,002167 | 0,422463 |
| shares | cultural | 129 | 43.342 | 1,013558 | 0,002594 | 0,422463 |
| shares | stand | 125 | 43.346 | 1,012792 | 0,017805 | 0,684608 |
| shares | thus | 129 | 43.342 | 1,012210 | 0,022063 | 0,684608 |
| shares | six | 133 | 43.338 | 1,012066 | 0,015406 | 0,684608 |
| shares | important | 122 | 43.349 | 1,012041 | 0,020796 | 0,684608 |
| shares | range | 119 | 43.352 | 1,012038 | 0,019068 | 0,684608 |

---

## 3. Efeito máximo em valores absolutos

Entrada: `solution/outputs/os03c/bloco1_equivalencia.csv` (105 linhas). Conversão: efeito máximo plausível (%) ÷ 100 × média da base da métrica. Médias usadas: engajamento = 2.010,3084 interações por post; shares = 300,0184; comments_count = 200,0155.

### Resumo por variável (maior efeito de cada variável × métrica)

| Variável | Métrica | Segmento do maior efeito | n | Efeito máx. plausível (%) | Efeito máx. absoluto | Unidade |
|---|---|---|---|---|---|---|
| faixa_seguidores | comments_count | ate 50K | 2.564 | 0,3799 | 0,7599 | comentarios por post |
| content_type | comments_count | mixed | 5.213 | 0,3636 | 0,7273 | comentarios por post |
| audience_age_distribution | comments_count | 50+ | 2.650 | 0,3308 | 0,6617 | comentarios por post |
| audience_location | comments_count | India | 6.484 | 0,3121 | 0,6242 | comentarios por post |
| audience_gender_distribution | comments_count | unknown | 5.235 | 0,2438 | 0,4876 | comentarios por post |
| platform | comments_count | RedNote | 10.402 | 0,2407 | 0,4814 | comentarios por post |
| content_category | comments_count | tech | 10.430 | 0,1509 | 0,3018 | comentarios por post |
| is_sponsored | comments_count | True | 22.314 | 0,1079 | 0,2158 | comentarios por post |
| faixa_seguidores | shares | ate 50K | 2.564 | 0,3447 | 1,0342 | shares por post |
| audience_age_distribution | shares | 50+ | 2.650 | 0,2560 | 0,7680 | shares por post |
| content_type | shares | text | 5.198 | 0,2438 | 0,7314 | shares por post |
| audience_location | shares | China | 6.648 | 0,2085 | 0,6255 | shares por post |
| audience_gender_distribution | shares | unknown | 5.235 | 0,1932 | 0,5796 | shares por post |
| platform | shares | RedNote | 10.402 | 0,1745 | 0,5235 | shares por post |
| content_category | shares | tech | 10.430 | 0,1186 | 0,3558 | shares por post |
| is_sponsored | shares | True | 22.314 | 0,0999 | 0,2997 | shares por post |
| audience_age_distribution | taxa_engajamento | 50+ | 2.650 | 0,1292 | 2,5973 | interacoes por post |
| faixa_seguidores | taxa_engajamento | 50-100K | 2.597 | 0,1272 | 2,5571 | interacoes por post |
| audience_location | taxa_engajamento | India | 6.484 | 0,1151 | 2,3139 | interacoes por post |
| content_type | taxa_engajamento | text | 5.198 | 0,1106 | 2,2234 | interacoes por post |
| platform | taxa_engajamento | Instagram | 10.423 | 0,0796 | 1,6002 | interacoes por post |
| content_category | taxa_engajamento | tech | 10.430 | 0,0706 | 1,4193 | interacoes por post |
| audience_gender_distribution | taxa_engajamento | unknown | 5.235 | 0,0701 | 1,4092 | interacoes por post |
| is_sponsored | taxa_engajamento | True | 22.314 | 0,0350 | 0,7036 | interacoes por post |

### Maior valor da base inteira, por métrica

| Métrica | Variável | Segmento | n | Efeito máx. plausível (%) | Efeito máx. absoluto | Unidade |
|---|---|---|---|---|---|---|
| comments_count | faixa_seguidores | ate 50K | 2.564 | 0,3799 | 0,7599 | comentarios por post |
| shares | faixa_seguidores | ate 50K | 2.564 | 0,3447 | 1,0342 | shares por post |
| taxa_engajamento | audience_age_distribution | 50+ | 2.650 | 0,1292 | 2,5973 | interacoes por post |

---

## 4. Tamanho de amostra para testes futuros

Fórmula da OS: `n por variante = 2 × (1,96 + 0,84)² × CV² ÷ lift²` (poder 80%, significância 5% bicaudal, duas variantes). Arredondado para cima.

| CV (rótulo) | CV (valor) | lift 5% | lift 10% | lift 20% | lift 40% |
|---|---|---|---|---|---|
| CV da base - comments_count | 0,070464 | 32 | 8 | 2 | 1 |
| CV da base - engajamento | 0,022329 | 4 | 1 | 1 | 1 |
| CV da base - shares | 0,057693 | 21 | 6 | 2 | 1 |
| cenário fixo CV = 0,5 | 0,500000 | 1.568 | 392 | 98 | 25 |
| cenário fixo CV = 0,7 | 0,700000 | 3.074 | 769 | 193 | 49 |
| cenário fixo CV = 1,0 | 1,000000 | 6.272 | 1.568 | 392 | 98 |

---

## Pontos suspeitos ou problemas encontrados

1. **Views e engajamento quase constantes.** Views vão de 9.676 a 10.551 (amplitude de 875 em torno de uma média de 10.100,3) e o engajamento de 1.833 a 2.189. O engajamento no percentil 1 é 0,948756 da mediana e **0,0000%** dos posts ficam abaixo de 10% da mediana.
2. **Variância ÷ média colada em 1 nas quatro métricas** (views 0,990585; likes 1,002983; shares 0,998600; comments_count 0,993115 — todas entre 0,9906 e 1,0030). O valor 1 é o de uma Poisson; em métricas de redes sociais esse índice costuma ser muito maior que 1.
3. **Likes e views sem correlação** (Pearson 0,000761, Spearman 0,001490); **log10(follower_count) e log10(views) também** (0,005644). As medianas de views nas quatro faixas de seguidores são praticamente iguais.
4. **`sponsor_name` tem 18.005 valores distintos em 22.314 posts patrocinados** — quase um patrocinador por post.
5. **Hashtags: 118 resultados com p < 0,05 sem correção em 1.940 testes, contra 97,0 esperados por acaso; após a correção BH sobram 0.** Os lifts extremos ficam entre 0,984085 e 1,016026.
6. **Efeito máximo plausível em unidades absolutas, no pior caso de cada métrica:** comments_count = 0,7599 comentarios por post sobre uma média de 200,0155; shares = 1,0342 shares por post sobre uma média de 300,0184; taxa_engajamento = 2,5973 interacoes por post sobre uma média de 2.010,3084.
7. **Os CV da base são muito baixos** (0,022329 para engajamento; 0,057693 para shares; 0,070464 para comments_count), então o n por variante do item 4 fica em poucas unidades com esses CV, contra centenas ou milhares nos cenários fixos de 0,5 a 1,0.
8. **Faixas de seguidores desbalanceadas:** 50–100K e até 50K têm 2.597 e 2.564 posts, contra 26.029 em 500K–1M.
9. **Indicadores 8 e 9 dão exatamente 0,0000% e 0,0000%** sobre 5.000 creators: nenhum creator está restrito a uma plataforma e nenhum tem `follower_count` constante. Todos os 5.000 creators têm mais de 1 post (10 a 11 posts), aparecem em 2 a 5 plataformas e têm 10 a 11 valores distintos de `follower_count`.
