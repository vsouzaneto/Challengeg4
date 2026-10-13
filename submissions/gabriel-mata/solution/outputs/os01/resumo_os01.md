# OS-01 — Base amostral

Script: `solution/analysis/os01_base_amostral.py`
Fonte: `datasets/social_media_dataset.csv`
Saídas: `solution/outputs/os01/` (17 arquivos .csv)

Definições usadas: `engajamento` = likes + shares + comments_count; `taxa_engajamento` = engajamento / views.
A faixa de duração foi construída sobre `content_length` (único campo candidato a duração), restrita a `content_type = video`.

---

## 1. Visão geral

| Indicador | Valor |
|---|---|
| Linhas | 52.214 |
| Colunas | 27 |
| Duplicatas em `id` | 0 |
| Duplicatas em `content_id` | 0 |
| `creator_id` únicos | 5.000 |
| `post_date` mínima | 2023-05-29 00:15 |
| `post_date` máxima | 2025-05-28 11:08 |
| Posts com engajamento = 0 | 0 |
| Posts com views = 0 | 0 |

Nulos: apenas duas colunas têm nulos — `hashtags` (8.743 / 16,74%) e `comments_text` (8.688 / 16,64%). As outras 25 colunas têm 0 nulos.

Tipos: 7 colunas inteiras (`id`, `content_length`, `views`, `likes`, `shares`, `comments_count`, `follower_count`), 1 booleana (`is_sponsored`), 1 data (`post_date`, convertida na leitura a partir de texto no formato `M/D/AA HH:MM AM/PM`) e 18 de texto. Detalhe em `01_tipos_colunas.csv`.

## 2. Distribuição das métricas

| Métrica | Mínimo | p1 | p25 | Mediana | p75 | p99 | Máximo | Média | Desvio | CV |
|---|---|---|---|---|---|---|---|---|---|---|
| views | 9.676 | 9.867 | 10.032 | 10.100 | 10.168 | 10.335 | 10.551 | 10.100,3 | 100,0 | **0,0099** |
| likes | 1.354 | 1.420 | 1.484 | 1.510 | 1.536 | 1.602 | 1.668 | 1.510,3 | 38,9 | **0,0258** |
| shares | 227 | 260 | 288 | 300 | 312 | 341 | 380 | 300,0 | 17,3 | **0,0577** |
| comments_count | 140 | 168 | 190 | 200 | 210 | 233 | 258 | 200,0 | 14,1 | **0,0705** |
| follower_count | 1.013 | 11.290 | 250.818 | 498.490 | 749.819 | 989.656 | 999.998 | 499.884,5 | 288.044,6 | 0,5762 |
| engajamento | 1.833 | 1.907 | 1.980 | 2.010 | 2.041 | 2.116 | 2.189 | 2.010,3 | 44,9 | **0,0223** |
| taxa_engajamento | 0,1788 | 0,1879 | 0,1958 | 0,1990 | 0,2023 | 0,2105 | 0,2223 | 0,1991 | 0,0049 | **0,0245** |

Posts com engajamento igual a zero: **0**.

## 3. Volume por segmento

Todas as 59 linhas estão em `03_volume_por_segmento.csv`. Resumo:

- **platform** (5): Bilibili 10.598 (20,30%), YouTube 10.495 (20,10%), Instagram 10.423 (19,96%), RedNote 10.402 (19,92%), TikTok 10.296 (19,72%).
- **content_type** (4): video 31.500 (60,33%), image 10.303 (19,73%), mixed 5.213 (9,98%), text 5.198 (9,96%).
- **content_category** (3): beauty 21.023 (40,26%), lifestyle 20.761 (39,76%), tech 10.430 (19,98%).
- **language** (5): English 26.110 (50,01%), Chinese 10.428 (19,97%), Hindi 5.272 (10,10%), Spanish 5.227 (10,01%), Japanese 5.177 (9,92%).
- **is_sponsored**: False 29.900 (57,26%), True 22.314 (42,74%).
- **disclosure_type**: none 29.900 (57,26%), explicit 11.784 (22,57%), implicit 10.530 (20,17%).
- **disclosure_location**: none 29.900 (57,26%), caption 8.944 (17,13%), video 7.246 (13,88%), hashtags 6.124 (11,73%).
- **sponsor_category**: Not sponsors 29.900 (57,26%); food 3.846, electronics 3.750, fashion 3.710, cosmetics 3.688, gaming 3.687, travel 3.633 (6,96%–7,37% cada).
- **audience_age_distribution**: 19-25 18.276 (35,00%), 26-35 15.700 (30,07%), 13-18 7.852 (15,04%), 36-50 7.736 (14,82%), 50+ 2.650 (5,08%).
- **audience_gender_distribution**: male 20.987 (40,19%), female 20.743 (39,73%), non-binary 5.249 (10,05%), unknown 5.235 (10,03%).
- **audience_location** (8 países): de Russia 6.459 (12,37%) a China 6.648 (12,73%) — praticamente uniforme.

**Faixa de seguidores** (base: 52.214):

| Faixa | n | % |
|---|---|---|
| 1–10K | 454 | 0,87% |
| 10–50K | 2.110 | 4,04% |
| 50–100K | 2.597 | 4,97% |
| 100–500K | 21.024 | 40,27% |
| 500K–1M | 26.029 | 49,85% |

**Faixa de duração** (base: 31.500 posts de vídeo):

| Faixa | n | % |
|---|---|---|
| <30 | 1.459 | 4,63% |
| 30–60 | 2.997 | 9,51% |
| 60–180 | 11.957 | 37,96% |
| >180 | 15.087 | 47,90% |

## 4. Tamanho dos cruzamentos

| Cruzamento | Combinações | n ≥ 100 | n 30–99 | n < 30 | n mín | n mediano | n máx |
|---|---|---|---|---|---|---|---|
| platform × content_type × content_category × faixa_seguidores | 299 | 123 | 45 | 131 | 1 | 49,0 | 1.344 |
| platform × content_category × faixa_seguidores × is_sponsored | 150 | 73 | 48 | 29 | 5 | 96,0 | 1.270 |

Detalhe célula por célula em `04_cruzamento_A_detalhe.csv` e `04_cruzamento_B_detalhe.csv`.

## 5. Consistência

**Patrocínio** — nenhuma inconsistência:

| Indicador | Valor |
|---|---|
| Não patrocinados (total) | 29.900 |
| Não patrocinados com `disclosure_type` ≠ none | 0 |
| Não patrocinados com `sponsor_category` ≠ "Not sponsors" | 0 |
| Patrocinados (total) | 22.314 |
| Patrocinados com `disclosure_type` = none | 0 |

**Por `creator_id`** (5.000 creators):

Plataformas distintas por creator: 5 plataformas → 2.813 creators; 4 → 1.974; 3 → 211; 2 → 2. Nenhum creator aparece em só 1 plataforma.

Variação de `follower_count` dentro do mesmo creator:

| Indicador | Valor |
|---|---|
| Creators com `follower_count` variável | 5.000 de 5.000 (100%) |
| Diferença (máx − mín) mínima | 246.977 |
| Diferença mediana | 842.331,5 |
| Diferença máxima | 996.601 |

**`comments_count` vs. comentários em `comments_text`** (contagem por frases):

| Indicador | Mediana |
|---|---|
| `comments_count` (todas as linhas) | 200 |
| Comentários em `comments_text` (todas as linhas) | 3 |
| `comments_count` (só texto não nulo) | 200 |
| Comentários em `comments_text` (só texto não nulo) | 3 |

## 6. Relação entre métricas

Correlação de Spearman:

| | follower_count | views | likes | shares | comments_count | engajamento |
|---|---|---|---|---|---|---|
| **follower_count** | 1,0000 | 0,0046 | −0,0039 | 0,0067 | 0,0022 | −0,0004 |
| **views** | 0,0046 | 1,0000 | 0,0015 | −0,0075 | −0,0044 | −0,0032 |
| **likes** | −0,0039 | 0,0015 | 1,0000 | 0,0069 | −0,0033 | 0,8570 |
| **shares** | 0,0067 | −0,0075 | 0,0069 | 1,0000 | −0,0022 | 0,3756 |
| **comments_count** | 0,0022 | −0,0044 | −0,0033 | −0,0022 | 1,0000 | 0,2984 |
| **engajamento** | −0,0004 | −0,0032 | 0,8570 | 0,3756 | 0,2984 | 1,0000 |

Medianas por faixa de seguidores:

| Faixa | n | Mediana views | Mediana engajamento |
|---|---|---|---|
| 1–10K | 454 | 10.090,5 | 2.006,5 |
| 10–50K | 2.110 | 10.100,0 | 2.011,0 |
| 50–100K | 2.597 | 10.099,0 | 2.010,0 |
| 100–500K | 21.024 | 10.100,0 | 2.010,0 |
| 500K–1M | 26.029 | 10.101,0 | 2.010,0 |

---

## Pontos suspeitos ou problemas encontrados

1. **As métricas de performance têm dispersão quase nula.** `views` varia de 9.676 a 10.551 em 52.214 posts (CV = 0,0099); `engajamento` de 1.833 a 2.189 (CV = 0,0223); `taxa_engajamento` de 0,1788 a 0,2223 (CV = 0,0245). Cada métrica se concentra em torno de um valor fixo (views ≈ 10.100, likes ≈ 1.510, shares ≈ 300, comments_count ≈ 200), com p1 e p99 a menos de 3% da mediana. Não há cauda longa nem posts virais.

2. **`follower_count` não tem relação com nenhuma métrica.** Spearman de `follower_count` contra views, likes, shares, comments_count e engajamento fica entre −0,0039 e +0,0067. A mediana de views vai de 10.090,5 (faixa 1–10K) a 10.101,0 (faixa 500K–1M) — diferença de ~10 views entre creators com 1 mil e 1 milhão de seguidores. O mesmo para engajamento (2.006,5 a 2.011,0).

3. **`follower_count` varia dentro do mesmo creator.** Todos os 5.000 creators têm `follower_count` variável, com diferença mediana de 842.331,5 entre o post de maior e o de menor valor. O campo se comporta como valor sorteado por linha, não como atributo do creator.

4. **`views` também não se relaciona com likes, shares nem comments_count** (Spearman entre −0,0075 e +0,0015). As correlações de likes (0,8570), shares (0,3756) e comments_count (0,2984) com `engajamento` refletem apenas a composição da soma — likes representa ~75% do total.

5. **`content_length` não parece ser duração.** A distribuição é praticamente idêntica nos quatro `content_type`, incluindo `text` e `image` (`03_content_length_por_content_type.csv`):

   | content_type | n | mín | p25 | mediana | p75 | máx | média |
   |---|---|---|---|---|---|---|---|
   | image | 10.303 | 10 | 94,0 | 173,0 | 359,0 | 599 | 229,00 |
   | mixed | 5.213 | 10 | 95,0 | 175,0 | 359,0 | 599 | 228,65 |
   | text | 5.198 | 10 | 95,0 | 174,0 | 358,0 | 599 | 228,96 |
   | video | 31.500 | 10 | 95,0 | 174,0 | 361,0 | 599 | 229,96 |

   Se fosse duração de vídeo em segundos, não deveria existir com a mesma distribuição para post de texto e imagem. As faixas de duração da seção 3 foram calculadas sobre esse campo e herdam essa ressalva.

6. **`comments_count` é incompatível com `comments_text`.** Mediana de 200 em `comments_count` contra 3 frases em `comments_text`. Além disso, `comments_text` traz um texto corrido sem separador: nas 43.526 linhas com texto, 0 contêm `|`, `;`, quebra de linha ou tab (`05_comments_text_separadores.csv`). Não há como recuperar comentários individuais — a contagem de 3 é por frase, separando em `.`, `!` e `?`.

7. **Células pequenas no cruzamento A.** Em platform × content_type × content_category × faixa_seguidores, 131 das 299 combinações têm n < 30 e o n mínimo é 1. O cruzamento B é mais robusto (29 de 150 com n < 30, mínimo 5).

8. **Faixas de seguidores muito desbalanceadas.** 90,1% dos posts caem em 100–500K e 500K–1M, contra 0,87% em 1–10K (454 posts). Isso decorre da largura desigual das faixas aplicada a um `follower_count` espalhado de 1.013 a 999.998.

9. **`hashtags` e `comments_text` têm ~16,7% de nulos** (8.743 e 8.688 linhas). Nenhuma outra coluna tem nulo.

10. **Campos de patrocínio perfeitamente consistentes.** As quatro colunas (`is_sponsored`, `disclosure_type`, `sponsor_category`, `disclosure_location`) concordam em 100% das 52.214 linhas: os 29.900 não patrocinados têm exatamente `none`/`Not sponsors`/`none` e nenhum dos 22.314 patrocinados tem `disclosure_type = none`. Zero ruído.

11. **`creator_id` atravessa plataformas.** 4.787 dos 5.000 creators aparecem em 4 ou 5 plataformas distintas e nenhum aparece em apenas 1, com o mesmo `creator_id` e `creator_name`.
