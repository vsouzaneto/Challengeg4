# OS-02 — Benchmark por segmento

Script: `solution/analysis/os02_benchmark.py`
Fonte: `datasets/social_media_dataset.csv` (52.214 posts)
Saídas: `solution/outputs/os02/` (9 arquivos .csv)

**Método:** `indice = valor do post / média da métrica na plataforma do post`; `lift do segmento` = média do índice dos posts do segmento. IC 95% por bootstrap percentil (1.000 reamostragens). Teste de repetição: divisão única em duas metades aleatórias (seed 42, A = 26.107 / B = 26.107), a mesma para todos os segmentos. Teste contra o acaso: 200 permutações do índice dentro de cada plataforma.

Métricas: `taxa_engajamento`, `shares`, `comments_count`.
Ajustes desta OS: faixas de seguidores em 4 níveis (até 50K, 50–100K, 100–500K, 500K–1M); `content_length` não usado; variáveis novas `n_hashtags`, `periodo_dia`, `dia_semana`.

---

## 1. Plataforma

Média de cada métrica por plataforma vs. média geral, com IC 95% bootstrap (`plataforma.csv`).

| Plataforma | Métrica | n | Média | IC inferior | IC superior | Média geral | Razão | IC exclui a média geral |
|---|---|---|---|---|---|---|---|---|
| Bilibili | taxa_engajamento | 10.598 | 0,199085 | 0,198993 | 0,199179 | 0,199055 | 1,000153 | não |
| Instagram | taxa_engajamento | 10.423 | 0,198993 | 0,198896 | 0,199083 | 0,199055 | 0,999688 | não |
| RedNote | taxa_engajamento | 10.402 | 0,199098 | 0,199004 | 0,199190 | 0,199055 | 1,000216 | não |
| TikTok | taxa_engajamento | 10.296 | 0,199060 | 0,198969 | 0,199153 | 0,199055 | 1,000028 | não |
| YouTube | taxa_engajamento | 10.495 | 0,199037 | 0,198946 | 0,199133 | 0,199055 | 0,999913 | não |
| Bilibili | shares | 10.598 | 300,0924 | 299,7807 | 300,4241 | 300,0184 | 1,000246 | não |
| Instagram | shares | 10.423 | 300,1712 | 299,8340 | 300,5353 | 300,0184 | 1,000509 | não |
| RedNote | shares | 10.402 | 299,8177 | 299,4959 | 300,1449 | 300,0184 | 0,999331 | não |
| TikTok | shares | 10.296 | 299,8662 | 299,5333 | 300,1837 | 300,0184 | 0,999492 | não |
| YouTube | shares | 10.495 | 300,1404 | 299,8175 | 300,4637 | 300,0184 | 1,000407 | não |
| Bilibili | comments_count | 10.598 | 200,0405 | 199,7864 | 200,2970 | 200,0155 | 1,000125 | não |
| Instagram | comments_count | 10.423 | 199,9888 | 199,7199 | 200,2399 | 200,0155 | 0,999867 | não |
| RedNote | comments_count | 10.402 | 200,2146 | 199,9623 | 200,4971 | 200,0155 | 1,000996 | não |
| TikTok | comments_count | 10.296 | 199,9986 | 199,7354 | 200,2926 | 200,0155 | 0,999916 | não |
| YouTube | comments_count | 10.495 | 199,8358 | 199,5740 | 200,0880 | 200,0155 | 0,999102 | não |

Nenhuma das 15 combinações plataforma × métrica tem IC que exclua a média geral. A maior razão é 1,0010 (RedNote, comments_count) e a menor 0,9991 (YouTube, comments_count).

## 2. Distribuição dos lifts por nível e métrica

`distribuicao_lifts.csv`

| Nível | Métrica | Segmentos | Mínimo | p5 | Mediana | p95 | Máximo |
|---|---|---|---|---|---|---|---|
| 1 | taxa_engajamento | 52 | 0,999430 | 0,999677 | 1,000008 | 1,000425 | 1,000495 |
| 1 | shares | 52 | 0,998753 | 0,999387 | 0,999998 | 1,000841 | 1,001267 |
| 1 | comments_count | 52 | 0,998392 | 0,998752 | 0,999960 | 1,000878 | 1,001819 |
| 2 | taxa_engajamento | 260 | 0,998500 | 0,999174 | 1,000017 | 1,000961 | 1,001844 |
| 2 | shares | 260 | 0,995899 | 0,997890 | 0,999956 | 1,002262 | 1,003250 |
| 2 | comments_count | 260 | 0,995154 | 0,997490 | 0,999966 | 1,002350 | 1,005802 |
| 3 | taxa_engajamento | 253 | 0,995435 | 0,998072 | 1,000029 | 1,002070 | 1,004139 |
| 3 | shares | 253 | 0,989311 | 0,995938 | 1,000082 | 1,004388 | 1,012901 |
| 3 | comments_count | 253 | 0,986097 | 0,994683 | 1,000172 | 1,006699 | 1,013706 |
| 4 | taxa_engajamento | 128 | 0,996816 | 0,998160 | 0,999993 | 1,003312 | 1,004772 |
| 4 | shares | 128 | 0,991731 | 0,995643 | 0,999992 | 1,005546 | 1,010496 |
| 4 | comments_count | 128 | 0,982784 | 0,994354 | 1,000550 | 1,009664 | 1,018423 |

Contagens por limiar — **todas zero**, em todos os níveis e métricas:

| Nível | Métrica | > 1,03 | > 1,05 | > 1,10 | < 0,97 | < 0,95 | < 0,90 |
|---|---|---|---|---|---|---|---|
| 1 | taxa_engajamento | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | shares | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | comments_count | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | taxa_engajamento | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | shares | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | comments_count | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | taxa_engajamento | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | shares | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | comments_count | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | taxa_engajamento | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | shares | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | comments_count | 0 | 0 | 0 | 0 | 0 | 0 |

Dos 693 segmentos avaliados (2.079 linhas segmento × métrica), o lift mais alto da base é 1,018423 (+1,84%) e o mais baixo 0,982784 (−1,72%), ambos em `comments_count` no Nível 4.

**Cobertura dos níveis com filtro** (`cobertura_niveis.csv`):

| Nível | Segmentos existentes | Mantidos (n ≥ 100) | Fora por n < 100 |
|---|---|---|---|
| 1 (sem filtro) | 52 | 52 | 0 |
| 2 | 260 | 260 | 0 |
| 3 | 275 | 253 | 22 |
| 4 | 240 | 128 | 112 |

No Nível 3, os 22 descartes vêm de `platform × content_type × faixa_seguidores` (21 de 80) e `platform × content_category × faixa_seguidores` (1 de 60); os outros dois conjuntos não perderam nenhum segmento. Detalhe por conjunto de variáveis em `cobertura_niveis.csv`.

## 3. Os 10 maiores e os 10 menores lifts de `taxa_engajamento`

`top_bottom_taxa_engajamento.csv`. Colunas: n, lift, IC 95%, se o IC exclui 1, lift em cada metade e se as duas metades ficaram do mesmo lado de 1.

### Nível 1 — maiores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| audience_location | UK | 6.570 | 1,000495 | 0,999907 | 1,001076 | não | 1,000252 | 1,000740 | sim |
| content_type | text | 5.198 | 1,000485 | 0,999831 | 1,001102 | não | 1,000614 | 1,000359 | sim |
| content_type | mixed | 5.213 | 1,000428 | 0,999775 | 1,001064 | não | 1,000267 | 1,000586 | sim |
| dia_semana | sexta | 7.495 | 1,000423 | 0,999927 | 1,001010 | não | 1,000543 | 1,000306 | sim |
| n_hashtags | 2 | 8.746 | 1,000395 | 0,999900 | 1,000879 | não | 1,000449 | 1,000340 | sim |
| faixa_seguidores | 50-100K | 2.597 | 1,000339 | 0,999397 | 1,001223 | não | 1,000225 | 1,000452 | sim |
| language | Spanish | 5.227 | 1,000335 | 0,999688 | 1,000975 | não | 1,000363 | 1,000305 | sim |
| audience_location | Brazil | 6.505 | 1,000320 | 0,999706 | 1,000894 | não | 1,000424 | 1,000216 | sim |
| audience_age_distribution | 50+ | 2.650 | 1,000319 | 0,999363 | 1,001274 | não | 0,999953 | 1,000672 | não |
| language | Japanese | 5.177 | 1,000306 | 0,999634 | 1,000947 | não | 1,000218 | 1,000394 | sim |

### Nível 1 — menores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| audience_location | India | 6.484 | 0,999430 | 0,998852 | 1,000042 | não | 0,999327 | 0,999534 | sim |
| n_hashtags | 0 | 8.743 | 0,999605 | 0,999068 | 1,000118 | não | 0,999326 | 0,999892 | sim |
| audience_location | Germany | 6.497 | 0,999668 | 0,999098 | 1,000243 | não | 0,999923 | 0,999418 | sim |
| audience_age_distribution | 13-18 | 7.852 | 0,999684 | 0,999147 | 1,000195 | não | 0,999437 | 0,999933 | sim |
| dia_semana | quarta | 7.343 | 0,999689 | 0,999091 | 1,000244 | não | 0,999735 | 0,999643 | sim |
| content_category | tech | 10.430 | 0,999745 | 0,999292 | 1,000239 | não | 1,000320 | 0,999178 | não |
| periodo_dia | madrugada | 13.154 | 0,999788 | 0,999370 | 1,000196 | não | 0,999663 | 0,999912 | sim |
| language | English | 26.110 | 0,999797 | 0,999513 | 1,000079 | não | 0,999797 | 0,999797 | sim |
| audience_age_distribution | 36-50 | 7.736 | 0,999815 | 0,999264 | 1,000378 | não | 0,999773 | 0,999856 | sim |
| n_hashtags | 1 | 8.738 | 0,999818 | 0,999327 | 1,000342 | não | 0,999758 | 0,999878 | sim |

Nenhum dos 20 extremos do Nível 1 tem IC que exclua 1. A amplitude total do nível é de 0,99943 a 1,00050 (−0,06% a +0,05%).

### Nível 2 — maiores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| platform × audience_location | Bilibili \| UK | 1.341 | 1,001844 | 1,000523 | 1,003102 | **sim** | 1,002581 | 1,001149 | sim |
| platform × audience_location | Instagram \| Brazil | 1.288 | 1,001754 | 1,000415 | 1,003029 | **sim** | 1,002326 | 1,001231 | sim |
| platform × faixa_seguidores | TikTok \| 50-100K | 504 | 1,001444 | 0,999222 | 1,003602 | não | 1,001575 | 1,001313 | sim |
| platform × audience_age_distribution | Bilibili \| 50+ | 516 | 1,001238 | 0,999027 | 1,003407 | não | 0,999819 | 1,002771 | não |
| platform × audience_location | YouTube \| UK | 1.336 | 1,001190 | 0,999886 | 1,002597 | não | 1,000161 | 1,002263 | sim |
| platform × dia_semana | RedNote \| sexta | 1.468 | 1,001181 | 0,999867 | 1,002427 | não | 1,001217 | 1,001149 | sim |
| platform × faixa_seguidores | Bilibili \| ate 50K | 542 | 1,001161 | 0,999009 | 1,003305 | não | 1,004225 | 0,997788 | não |
| platform × n_hashtags | RedNote \| 2 | 1.767 | 1,001156 | 0,999963 | 1,002232 | não | 1,001106 | 1,001205 | sim |
| platform × content_type | YouTube \| text | 1.052 | 1,001138 | 0,999578 | 1,002578 | não | 1,001129 | 1,001147 | sim |
| platform × language | TikTok \| Spanish | 1.050 | 1,001120 | 0,999583 | 1,002674 | não | 1,001107 | 1,001135 | sim |

### Nível 2 — menores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| platform × audience_location | RedNote \| India | 1.321 | 0,998500 | 0,997287 | 0,999819 | **sim** | 0,998771 | 0,998220 | sim |
| platform × audience_location | TikTok \| Germany | 1.277 | 0,998664 | 0,997424 | 0,999964 | **sim** | 0,999006 | 0,998313 | sim |
| platform × n_hashtags | RedNote \| 0 | 1.751 | 0,998780 | 0,997688 | 0,999853 | **sim** | 0,998437 | 0,999123 | sim |
| platform × dia_semana | RedNote \| sabado | 1.448 | 0,998826 | 0,997622 | 1,000023 | não | 0,999351 | 0,998300 | sim |
| platform × faixa_seguidores | YouTube \| ate 50K | 514 | 0,998908 | 0,996612 | 1,001164 | não | 1,000458 | 0,997270 | não |
| platform × audience_location | Bilibili \| India | 1.304 | 0,998924 | 0,997560 | 1,000270 | não | 0,999235 | 0,998622 | sim |
| platform × faixa_seguidores | Instagram \| 50-100K | 506 | 0,998937 | 0,996948 | 1,001003 | não | 0,997989 | 0,999923 | sim |
| platform × audience_age_distribution | Instagram \| 36-50 | 1.507 | 0,998968 | 0,997739 | 1,000234 | não | 0,998090 | 0,999807 | sim |
| platform × audience_location | Instagram \| Russia | 1.328 | 0,998977 | 0,997702 | 1,000343 | não | 0,998794 | 0,999175 | sim |
| platform × content_category | YouTube \| tech | 2.060 | 0,999076 | 0,997938 | 1,000141 | não | 0,999004 | 0,999147 | sim |

### Nível 3 — maiores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| platform × content_category × audience_age | Bilibili \| tech \| 50+ | 113 | 1,004139 | 0,999727 | 1,008597 | não | 1,004775 | 1,003596 | sim |
| platform × content_type × faixa_seguidores | Bilibili \| video \| ate 50K | 326 | 1,003250 | 1,000451 | 1,006059 | **sim** | 1,006746 | 0,999346 | não |
| platform × content_category × faixa_seguidores | Instagram \| beauty \| ate 50K | 188 | 1,003075 | 0,999498 | 1,006432 | não | 1,003053 | 1,003098 | sim |
| platform × content_category × faixa_seguidores | TikTok \| lifestyle \| ate 50K | 184 | 1,003020 | 0,999382 | 1,006934 | não | 1,003760 | 1,002139 | sim |
| platform × content_type × content_category | YouTube \| text \| tech | 207 | 1,002838 | 0,999696 | 1,006250 | não | 1,001664 | 1,003936 | sim |
| platform × content_category × faixa_seguidores | RedNote \| tech \| 50-100K | 105 | 1,002508 | 0,998038 | 1,006930 | não | 1,002520 | 1,002497 | sim |
| platform × content_type × content_category | Instagram \| mixed \| tech | 206 | 1,002382 | 0,999122 | 1,005669 | não | 1,001073 | 1,003569 | sim |
| platform × content_category × audience_age | Instagram \| tech \| 26-35 | 602 | 1,002299 | 1,000409 | 1,004166 | **sim** | 1,003301 | 1,001362 | sim |
| platform × content_category × faixa_seguidores | TikTok \| beauty \| 50-100K | 207 | 1,002243 | 0,998818 | 1,005391 | não | 1,001460 | 1,002974 | sim |
| platform × content_type × faixa_seguidores | TikTok \| video \| 50-100K | 302 | 1,002138 | 0,999372 | 1,004996 | não | 1,002349 | 1,001925 | sim |

### Nível 3 — menores

| Variáveis | Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|---|
| platform × content_category × faixa_seguidores | YouTube \| tech \| ate 50K | 106 | 0,995435 | 0,990492 | 1,000025 | não | 0,996475 | 0,994394 | sim |
| platform × content_type × faixa_seguidores | YouTube \| image \| ate 50K | 107 | 0,995486 | 0,990754 | 0,999900 | **sim** | 0,997844 | 0,992587 | sim |
| platform × content_category × faixa_seguidores | Instagram \| lifestyle \| 50-100K | 197 | 0,996066 | 0,993011 | 0,999088 | **sim** | 0,996547 | 0,995589 | sim |
| platform × content_type × faixa_seguidores | Instagram \| image \| 50-100K | 100 | 0,996291 | 0,991629 | 1,000451 | não | 0,994970 | 0,997511 | sim |
| platform × content_type × faixa_seguidores | RedNote \| image \| ate 50K | 101 | 0,996824 | 0,991306 | 1,002306 | não | 0,996151 | 0,997662 | sim |
| platform × content_category × audience_age | RedNote \| tech \| 50+ | 103 | 0,997277 | 0,992596 | 1,001995 | não | 0,993624 | 1,001148 | não |
| platform × content_type × faixa_seguidores | Bilibili \| image \| ate 50K | 107 | 0,997287 | 0,992878 | 1,001738 | não | 0,998727 | 0,995301 | sim |
| platform × content_category × faixa_seguidores | RedNote \| tech \| ate 50K | 114 | 0,997374 | 0,992960 | 1,001895 | não | 0,993338 | 1,002924 | não |
| platform × content_category × audience_age | YouTube \| tech \| 36-50 | 288 | 0,997434 | 0,994675 | 1,000261 | não | 0,997696 | 0,997088 | sim |
| platform × content_category × faixa_seguidores | Instagram \| tech \| ate 50K | 120 | 0,997532 | 0,992971 | 1,001641 | não | 0,997678 | 0,997387 | sim |

### Nível 4 — maiores

Variáveis: `platform × content_type × content_category × faixa_seguidores` em todas as linhas.

| Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|
| Instagram \| text \| beauty \| 100-500K | 151 | 1,004772 | 1,001009 | 1,008748 | **sim** | 1,003171 | 1,006231 | sim |
| Bilibili \| video \| lifestyle \| ate 50K | 124 | 1,004315 | 0,999761 | 1,008488 | não | 1,005878 | 1,001923 | sim |
| TikTok \| video \| beauty \| 50-100K | 120 | 1,003906 | 0,999183 | 1,008319 | não | 1,003876 | 1,003935 | sim |
| Instagram \| video \| beauty \| ate 50K | 105 | 1,003518 | 0,998379 | 1,008428 | não | 1,002947 | 1,004058 | sim |
| TikTok \| text \| lifestyle \| 500K-1M | 202 | 1,003468 | 1,000171 | 1,007040 | **sim** | 1,004611 | 1,002278 | sim |
| TikTok \| mixed \| beauty \| 500K-1M | 196 | 1,003454 | 1,000090 | 1,006410 | **sim** | 0,999147 | 1,008850 | não |
| Bilibili \| video \| beauty \| ate 50K | 132 | 1,003369 | 0,998792 | 1,008025 | não | 1,004950 | 1,001835 | sim |
| Instagram \| mixed \| beauty \| 100-500K | 172 | 1,003207 | 0,999071 | 1,006914 | não | 1,002718 | 1,003782 | sim |
| RedNote \| image \| lifestyle \| 500K-1M | 449 | 1,003166 | 1,000939 | 1,005686 | **sim** | 1,001947 | 1,004306 | sim |
| Bilibili \| text \| beauty \| 100-500K | 197 | 1,003092 | 0,999743 | 1,006593 | não | 1,004341 | 1,001855 | sim |

### Nível 4 — menores

| Segmento | n | Lift | IC inf. | IC sup. | Exclui 1 | Metade A | Metade B | Mesmo lado |
|---|---|---|---|---|---|---|---|---|
| Bilibili \| video \| beauty \| 50-100K | 137 | 0,996816 | 0,992621 | 1,000962 | não | 0,997836 | 0,995780 | sim |
| TikTok \| mixed \| lifestyle \| 100-500K | 171 | 0,997221 | 0,993035 | 1,001153 | não | 0,997024 | 0,997434 | sim |
| YouTube \| image \| beauty \| 500K-1M | 420 | 0,997441 | 0,995257 | 0,999585 | **sim** | 0,997175 | 0,997701 | sim |
| TikTok \| text \| tech \| 500K-1M | 106 | 0,997898 | 0,992976 | 1,002673 | não | 0,998593 | 0,997148 | sim |
| Bilibili \| image \| lifestyle \| 100-500K | 322 | 0,997933 | 0,995394 | 1,000381 | não | 0,996905 | 0,999083 | sim |
| TikTok \| image \| lifestyle \| 500K-1M | 404 | 0,998040 | 0,995652 | 1,000399 | não | 1,000157 | 0,995679 | não |
| Instagram \| text \| lifestyle \| 100-500K | 174 | 0,998102 | 0,994312 | 1,001587 | não | 0,995263 | 1,000106 | não |
| TikTok \| image \| tech \| 100-500K | 166 | 0,998268 | 0,994764 | 1,002017 | não | 0,999610 | 0,997079 | sim |
| TikTok \| mixed \| lifestyle \| 500K-1M | 173 | 0,998388 | 0,994727 | 1,002318 | não | 0,997361 | 0,999428 | sim |
| Instagram \| text \| tech \| 500K-1M | 108 | 0,998396 | 0,993673 | 1,003350 | não | 0,997001 | 0,999645 | sim |

## 4. Teste contra o acaso

200 permutações do índice dentro de cada plataforma, por nível e métrica (`teste_acaso.csv`). "Observado" é o maior/menor lift entre os segmentos do nível; "acaso" é o p95 dos maiores e o p5 dos menores sob permutação.

| Nível | Métrica | Segmentos | Maior observado | Acaso p95 dos maiores | Observado > acaso | Menor observado | Acaso p5 dos menores | Observado < acaso |
|---|---|---|---|---|---|---|---|---|
| 1 | taxa_engajamento | 52 | 1,000495 | 1,000995 | não | 0,999430 | 0,998897 | não |
| 1 | shares | 52 | 1,001267 | 1,002165 | não | 0,998753 | 0,997590 | não |
| 1 | comments_count | 52 | 1,001819 | 1,002808 | não | 0,998392 | 0,997098 | não |
| 2 | taxa_engajamento | 260 | 1,001844 | 1,002667 | não | 0,998500 | 0,997174 | não |
| 2 | shares | 260 | 1,003250 | 1,006547 | não | 0,995899 | 0,993808 | não |
| 2 | comments_count | 260 | 1,005802 | 1,008290 | não | 0,995154 | 0,991721 | não |
| 3 | taxa_engajamento | 253 | 1,004139 | 1,006826 | não | 0,995435 | 0,993074 | não |
| 3 | shares | 253 | 1,012901 | 1,016277 | não | 0,989311 | 0,984889 | não |
| 3 | comments_count | 253 | 1,013706 | 1,019119 | não | 0,986097 | 0,980198 | não |
| 4 | taxa_engajamento | 128 | 1,004772 | 1,006406 | não | 0,996816 | 0,993086 | não |
| 4 | shares | 128 | 1,010496 | 1,015699 | não | 0,991731 | 0,984029 | não |
| 4 | comments_count | 128 | 1,018423 | 1,019989 | não | 0,982784 | 0,979604 | não |

Em **24 de 24 comparações** (12 maiores + 12 menores), o extremo observado está dentro do intervalo que a permutação produz. Nenhum nível, em nenhuma métrica, tem extremo acima do p95 dos maiores ou abaixo do p5 dos menores.

---

## Pontos suspeitos ou problemas encontrados

1. **Todos os 693 segmentos têm lift entre 0,98 e 1,02.** Em nenhum dos 4 níveis, para nenhuma das 3 métricas, existe um único segmento acima de 1,03 ou abaixo de 0,97 — as 72 contagens de limiar da seção 2 são todas zero. O lift mais extremo da base inteira é 1,018423 (+1,84%, `comments_count`, Nível 4, 128 segmentos) e o mais baixo 0,982784 (−1,72%). Isso é coerente com o ponto 1 da OS-01: `taxa_engajamento` tem CV de 0,0245 e varia de 0,1788 a 0,2223 na base toda, então nenhum agrupamento de posts pode se afastar muito da média.

2. **O teste contra o acaso não separa nada: 24 de 24 comparações ficam dentro do acaso.** Os extremos observados são sistematicamente *menos* extremos que os produzidos por permutação (ex.: Nível 3 `shares`, maior observado 1,012901 contra p95 do acaso de 1,016277). Ou seja, embaralhar o índice dentro de cada plataforma gera lifts tão ou mais extremos que os reais, em todos os níveis e métricas.

3. **O teste de repetição se comporta como cara ou coroa.** Proporção de linhas com as duas metades do mesmo lado de 1: Nível 1 71/156 (45,5%), Nível 2 322/780 (41,3%), Nível 3 361/759 (47,6%), Nível 4 186/384 (48,4%). O esperado por sorteio é 50%. Nenhum nível se afasta disso de forma relevante — inclusive os níveis mais granulares, que deveriam ser mais ruidosos, ficam mais perto de 50% que o Nível 1.

4. **Quase nenhum IC exclui 1, e menos do que o esperado por acaso.** `ic_exclui_1 = sim` em 1/156 linhas no Nível 1 (0,6%), 13/780 no Nível 2 (1,7%), 27/759 no Nível 3 (3,6%) e 14/384 no Nível 4 (3,6%). Um IC de 95% aplicado a segmentos sem efeito real produziria ~5%. As taxas observadas estão todas abaixo disso.

5. **O único segmento do Nível 1 com IC que exclui 1 é `dia_semana = terça` em `comments_count`** (n = 7.510, lift 0,998392, IC 0,996913–0,999996). O limite superior do IC é 0,999996 — a 4 casas decimais de conter 1. Reporto como achado de fronteira, não como efeito.

6. **Nenhuma plataforma se distingue da média geral.** As 15 combinações plataforma × métrica têm razão entre 0,9991 e 1,0010 e nenhum IC exclui a média geral. Como consequência, a normalização por plataforma pedida no método é praticamente inócua: dividir pelo valor da plataforma ou pela média geral dá quase o mesmo índice.

7. **Faixa `até 50K` é pequena e domina os extremos negativos.** A faixa agregada tem 2.564 posts (454 da faixa 1–10K + 2.110 da 10–50K da OS-01), contra 26.029 em 500K–1M. Nos 10 menores lifts do Nível 3, 6 envolvem `ate 50K` e 2 envolvem `50-100K`; os ICs desses segmentos são os mais largos do nível (ex.: `YouTube | tech | ate 50K`, n = 106, IC de 0,990492 a 1,000025, amplitude de ~0,95 ponto percentual). Os extremos dos níveis granulares estão onde o n é menor, o que é o padrão esperado de ruído amostral.

8. **Perda grande de segmentos no Nível 4 pelo filtro de n.** 112 das 240 combinações ficam de fora por n < 100 (46,7%), restando 128. No Nível 3, `platform × content_type × faixa_seguidores` perde 21 de 80 (26,3%). Os dois conjuntos do Nível 3 que não usam `faixa_seguidores` não perdem nenhum segmento — a perda vem toda do desbalanceamento das faixas de seguidores apontado na OS-01.

9. **`n_hashtags = 0` é exatamente o conjunto de nulos.** Os 8.743 posts com `n_hashtags = 0` são as mesmas 8.743 linhas com `hashtags` nulo; nenhum post tem `hashtags` preenchido com lista vazia. A regra "nulo = 0" da OS foi aplicada, mas o segmento `0` é, na prática, "hashtags não informadas", não "post sem hashtag". As outras cinco categorias têm entre 8.586 e 8.746 posts cada — distribuição uniforme.

10. **Não há concentração de horário nem de dia de publicação.** As quatro faixas de `periodo_dia` ficam entre 12.953 (manhã) e 13.154 (madrugada) posts, e cada uma das 24 horas tem entre 2.097 e 2.267 posts. `dia_semana` segue o mesmo padrão: de 7.343 (quarta) a 7.537 (quinta), contra 7.459 esperados numa divisão perfeitamente uniforme. As duas variáveis novas derivadas de `post_date` dividem a base em partes praticamente iguais, sem nenhum horário ou dia predominante.
