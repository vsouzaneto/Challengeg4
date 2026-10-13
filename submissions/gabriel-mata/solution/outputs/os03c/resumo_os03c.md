# OS-03c — Robustez da conclusão

Script: `solution/analysis/os03c_robustez.py`
Fonte: `datasets/social_media_dataset.csv` (52.214 posts, 25 meses: 2023-05 a 2025-05)
Saídas: `solution/outputs/os03c/` (7 arquivos .csv)

**Método mantido da OS-02:** `índice do post = valor / média da métrica na plataforma do post`; `lift do segmento` = média do índice dos posts do segmento. Exceção da OS: para a variável `platform`, índice = valor / média geral da base. Bootstrap percentil com 1.000 reamostragens, seed 42. Mesma divisão em duas metades da OS-02 (A = 26.107, B = 26.107). Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.

**Variáveis:** platform (5), content_type (4), content_category (3), faixa_seguidores (4), is_sponsored (2), audience_age_distribution (5), audience_gender_distribution (4), audience_location (8) — **35 segmentos**, × 3 métricas = **105 linhas segmento × métrica**.

| Arquivo | Conteúdo |
|---|---|
| `bloco1_equivalencia.csv` | lift, IC 95%, IC 90%, efeito máximo plausível e equivalência (105 linhas) |
| `bloco2_mde.csv` | menor efeito detectável por segmento e métrica (105 linhas) |
| `bloco3a_injecao_isolada.csv` | injeção em segmentos isolados (72 linhas) |
| `bloco3b_injecao_na_busca.csv` | injeção numa busca entre muitos segmentos (2 linhas) |
| `bloco4_cortes_plataforma.csv` | cortes de top 10%/1% e bottom 10% por plataforma e métrica (45 linhas) |
| `bloco4_caudas.csv` | % nas caudas com IC de Wilson e teste KS (105 linhas) |
| `bloco5_tendencia.csv` | médias mensais, tendências e primeiro × último ano (951 linhas) |

---

## 1. Bloco 1 — Limite máximo do efeito (equivalência)

**Efeito máximo plausível** = maior afastamento entre 1 e os limites do IC 95%, em %. **Equivalente a ±1% / ±2%** = IC 90% inteiro dentro de 0,99–1,01 / 0,98–1,02.

### Resumo por variável e métrica

| Variável | Métrica | Segmentos | Maior efeito máximo plausível | Equiv. ±1% | Equiv. ±2% |
|---|---|---|---|---|---|
| audience_age_distribution | comments_count | 5 | 0,3308% | 5/5 | 5/5 |
| audience_age_distribution | shares | 5 | 0,2560% | 5/5 | 5/5 |
| audience_age_distribution | taxa_engajamento | 5 | 0,1292% | 5/5 | 5/5 |
| audience_gender_distribution | comments_count | 4 | 0,2438% | 4/4 | 4/4 |
| audience_gender_distribution | shares | 4 | 0,1932% | 4/4 | 4/4 |
| audience_gender_distribution | taxa_engajamento | 4 | 0,0701% | 4/4 | 4/4 |
| audience_location | comments_count | 8 | 0,3121% | 8/8 | 8/8 |
| audience_location | shares | 8 | 0,2085% | 8/8 | 8/8 |
| audience_location | taxa_engajamento | 8 | 0,1151% | 8/8 | 8/8 |
| content_category | comments_count | 3 | 0,1509% | 3/3 | 3/3 |
| content_category | shares | 3 | 0,1186% | 3/3 | 3/3 |
| content_category | taxa_engajamento | 3 | 0,0706% | 3/3 | 3/3 |
| content_type | comments_count | 4 | 0,3636% | 4/4 | 4/4 |
| content_type | shares | 4 | 0,2438% | 4/4 | 4/4 |
| content_type | taxa_engajamento | 4 | 0,1106% | 4/4 | 4/4 |
| faixa_seguidores | comments_count | 4 | 0,3799% | 4/4 | 4/4 |
| faixa_seguidores | shares | 4 | 0,3447% | 4/4 | 4/4 |
| faixa_seguidores | taxa_engajamento | 4 | 0,1272% | 4/4 | 4/4 |
| is_sponsored | comments_count | 2 | 0,1079% | 2/2 | 2/2 |
| is_sponsored | shares | 2 | 0,0999% | 2/2 | 2/2 |
| is_sponsored | taxa_engajamento | 2 | 0,0350% | 2/2 | 2/2 |
| platform | comments_count | 5 | 0,2407% | 5/5 | 5/5 |
| platform | shares | 5 | 0,1745% | 5/5 | 5/5 |
| platform | taxa_engajamento | 5 | 0,0796% | 5/5 | 5/5 |

**105 de 105** linhas são equivalentes a ±1% e **105 de 105** a ±2%. O maior efeito máximo plausível da base inteira é **0,3799%** e o menor é 0,0350%.

### Os 10 segmentos com maior efeito máximo plausível

| Variável | Segmento | Métrica | n | Lift | IC95 inf. | IC95 sup. | IC90 inf. | IC90 sup. | Efeito máx. plausível |
|---|---|---|---|---|---|---|---|---|---|
| faixa_seguidores | ate 50K | comments_count | 2564 | 1,000996 | 0,998167 | 1,003799 | 0,998633 | 1,003344 | **0,3799%** |
| content_type | mixed | comments_count | 5213 | 1,001819 | 0,999929 | 1,003636 | 1,000257 | 1,003376 | **0,3636%** |
| faixa_seguidores | ate 50K | shares | 2564 | 0,998753 | 0,996553 | 1,000981 | 0,996843 | 1,000651 | **0,3447%** |
| audience_age_distribution | 50+ | comments_count | 2650 | 0,999266 | 0,996692 | 1,001925 | 0,997064 | 1,001442 | **0,3308%** |
| audience_location | India | comments_count | 6484 | 0,998628 | 0,996879 | 1,000431 | 0,997202 | 1,000024 | **0,3121%** |
| faixa_seguidores | 50-100K | comments_count | 2597 | 0,999848 | 0,997073 | 1,002419 | 0,997534 | 1,002028 | **0,2927%** |
| audience_location | Russia | comments_count | 6459 | 1,000781 | 0,999018 | 1,002569 | 0,999346 | 1,002201 | **0,2569%** |
| audience_age_distribution | 50+ | shares | 2650 | 1,000342 | 0,998073 | 1,002560 | 0,998568 | 1,002249 | **0,2560%** |
| audience_age_distribution | 36-50 | comments_count | 7736 | 0,998925 | 0,997517 | 1,000499 | 0,997652 | 1,000229 | **0,2483%** |
| content_type | text | shares | 5198 | 1,000991 | 0,999389 | 1,002438 | 0,999680 | 1,002257 | **0,2438%** |

Nenhuma das 105 linhas tem IC 95% que exclua 1 (0/105). No IC 90%, 3 linhas excluem 1: `content_type = mixed` em comments_count (1,000257–1,003376), `audience_location = India` em taxa_engajamento (0,998918–0,999930) e `audience_location = UK` em taxa_engajamento (1,000010–1,001012) — as três continuam equivalentes a ±1%.

## 2. Bloco 2 — Menor efeito detectável

`MDE = (1,96 + 0,84) × desvio padrão do índice na base × raiz(1/n_segmento + 1/n_resto)`, poder 80% e significância 5% bicaudal. Desvio padrão do índice na base: 0,024461 (taxa_engajamento), 0,057691 (shares), 0,070462 (comments_count).

### Resumo por variável — MDE do segmento com menor n

| Variável | Segmento com menor n | n | MDE taxa_engajamento | MDE shares | MDE comments_count |
|---|---|---|---|---|---|
| platform | TikTok | 10.296 | 0,0753% | 0,1777% | 0,2170% |
| content_type | text | 5.198 | 0,1001% | 0,2361% | 0,2884% |
| content_category | tech | 10.430 | 0,0750% | 0,1768% | 0,2160% |
| faixa_seguidores | ate 50K | 2.564 | 0,1387% | 0,3271% | 0,3996% |
| is_sponsored | True | 22.314 | 0,0606% | 0,1429% | 0,1745% |
| audience_age_distribution | 50+ | 2.650 | 0,1366% | 0,3221% | 0,3934% |
| audience_gender_distribution | unknown | 5.235 | 0,0998% | 0,2354% | 0,2875% |
| audience_location | Russia | 6.459 | 0,0910% | 0,2147% | 0,2622% |

Faixa de MDE nas 105 linhas: de **0,0599%** (`faixa_seguidores = 500K-1M`, taxa_engajamento, n = 26.029) a **0,3996%** (`faixa_seguidores = ate 50K`, comments_count, n = 2.564). Por métrica: taxa_engajamento 0,0599%–0,1387%; shares 0,1414%–0,3271%; comments_count 0,1727%–0,3996%.

## 3. Bloco 3 — Controle positivo

Todas as injeções foram feitas em cópias dos dados; a base original não foi alterada. Após a injeção, o índice é recalculado (a média da plataforma — ou geral, no caso de `platform` — também muda).

### 3a. Injeção em segmentos isolados

Segmento de menor n de cada variável. **Detectado** = IC 95% exclui 1 **e** as duas metades acima de 1.

| Variável | Segmento | n | Métrica | Efeito injetado | Lift medido | IC inf. | IC sup. | Metade A | Metade B | Detectado |
|---|---|---|---|---|---|---|---|---|---|---|
| platform | TikTok | 10296 | taxa_engajamento | +1% | 1,008041 | 1,007621 | 1,008518 | 1,007914 | 1,008168 | sim |
| platform | TikTok | 10296 | taxa_engajamento | +2% | 1,016022 | 1,015553 | 1,016517 | 1,015894 | 1,016150 | sim |
| platform | TikTok | 10296 | taxa_engajamento | +5% | 1,039778 | 1,039304 | 1,040203 | 1,039647 | 1,039909 | sim |
| platform | TikTok | 10296 | shares | +1% | 1,006197 | 1,004996 | 1,007373 | 1,006216 | 1,006177 | sim |
| platform | TikTok | 10296 | shares | +2% | 1,014186 | 1,013082 | 1,015255 | 1,014208 | 1,014164 | sim |
| platform | TikTok | 10296 | shares | +5% | 1,037978 | 1,036830 | 1,039126 | 1,038001 | 1,037955 | sim |
| platform | TikTok | 10296 | comments_count | +1% | 1,005984 | 1,004625 | 1,007337 | 1,005136 | 1,006831 | sim |
| platform | TikTok | 10296 | comments_count | +2% | 1,013973 | 1,012646 | 1,015331 | 1,013126 | 1,014819 | sim |
| platform | TikTok | 10296 | comments_count | +5% | 1,037805 | 1,036374 | 1,039280 | 1,036949 | 1,038660 | sim |
| content_type | text | 5198 | taxa_engajamento | +1% | 1,009483 | 1,008818 | 1,010114 | 1,009614 | 1,009355 | sim |
| content_type | text | 5198 | taxa_engajamento | +2% | 1,018463 | 1,017784 | 1,019131 | 1,018596 | 1,018332 | sim |
| content_type | text | 5198 | taxa_engajamento | +5% | 1,045295 | 1,044599 | 1,046027 | 1,045436 | 1,045157 | sim |
| content_type | text | 5198 | shares | +1% | 1,008534 | 1,006930 | 1,010112 | 1,008916 | 1,008159 | sim |
| content_type | text | 5198 | shares | +2% | 1,017515 | 1,015858 | 1,019236 | 1,017898 | 1,017140 | sim |
| content_type | text | 5198 | shares | +5% | 1,044415 | 1,042811 | 1,046082 | 1,044830 | 1,044009 | sim |
| content_type | text | 5198 | comments_count | +1% | 1,006571 | 1,004612 | 1,008356 | 1,006402 | 1,006737 | sim |
| content_type | text | 5198 | comments_count | +2% | 1,015554 | 1,013638 | 1,017422 | 1,015387 | 1,015717 | sim |
| content_type | text | 5198 | comments_count | +5% | 1,042456 | 1,040469 | 1,044360 | 1,042243 | 1,042664 | sim |
| content_category | tech | 10430 | taxa_engajamento | +1% | 1,007730 | 1,007241 | 1,008197 | 1,008309 | 1,007157 | sim |
| content_category | tech | 10430 | taxa_engajamento | +2% | 1,015682 | 1,015185 | 1,016151 | 1,016266 | 1,015105 | sim |
| content_category | tech | 10430 | taxa_engajamento | +5% | 1,039351 | 1,038880 | 1,039833 | 1,039949 | 1,038760 | sim |
| content_category | tech | 10430 | shares | +1% | 1,006810 | 1,005606 | 1,007936 | 1,006561 | 1,007057 | sim |
| content_category | tech | 10430 | shares | +2% | 1,014773 | 1,013672 | 1,015937 | 1,014525 | 1,015018 | sim |
| content_category | tech | 10430 | shares | +5% | 1,038513 | 1,037335 | 1,039611 | 1,038276 | 1,038747 | sim |
| content_category | tech | 10430 | comments_count | +1% | 1,006269 | 1,004848 | 1,007589 | 1,005529 | 1,007001 | sim |
| content_category | tech | 10430 | comments_count | +2% | 1,014231 | 1,012798 | 1,015854 | 1,013491 | 1,014962 | sim |
| content_category | tech | 10430 | comments_count | +5% | 1,037979 | 1,036662 | 1,039379 | 1,037234 | 1,038716 | sim |
| faixa_seguidores | ate 50K | 2564 | taxa_engajamento | +1% | 1,009611 | 1,008615 | 1,010602 | 1,010465 | 1,008691 | sim |
| faixa_seguidores | ate 50K | 2564 | taxa_engajamento | +2% | 1,019106 | 1,018150 | 1,020142 | 1,019968 | 1,018178 | sim |
| faixa_seguidores | ate 50K | 2564 | taxa_engajamento | +5% | 1,047537 | 1,046571 | 1,048489 | 1,048422 | 1,046582 | sim |
| faixa_seguidores | ate 50K | 2564 | shares | +1% | 1,006656 | 1,004353 | 1,008959 | 1,006626 | 1,006689 | sim |
| faixa_seguidores | ate 50K | 2564 | shares | +2% | 1,016159 | 1,013844 | 1,018381 | 1,016131 | 1,016188 | sim |
| faixa_seguidores | ate 50K | 2564 | shares | +5% | 1,044622 | 1,042280 | 1,047147 | 1,044622 | 1,044621 | sim |
| faixa_seguidores | ate 50K | 2564 | comments_count | +1% | 1,008196 | 1,005313 | 1,010999 | 1,009478 | 1,006814 | sim |
| faixa_seguidores | ate 50K | 2564 | comments_count | +2% | 1,017689 | 1,014820 | 1,020724 | 1,018969 | 1,016311 | sim |
| faixa_seguidores | ate 50K | 2564 | comments_count | +5% | 1,046204 | 1,043496 | 1,048974 | 1,047501 | 1,044807 | sim |
| is_sponsored | True | 22314 | taxa_engajamento | +1% | 1,005669 | 1,005350 | 1,005962 | 1,005576 | 1,005762 | sim |
| is_sponsored | True | 22314 | taxa_engajamento | +2% | 1,011322 | 1,010989 | 1,011633 | 1,011228 | 1,011415 | sim |
| is_sponsored | True | 22314 | taxa_engajamento | +5% | 1,027996 | 1,027676 | 1,028333 | 1,027902 | 1,028090 | sim |
| is_sponsored | True | 22314 | shares | +1% | 1,004524 | 1,003795 | 1,005286 | 1,004242 | 1,004807 | sim |
| is_sponsored | True | 22314 | shares | +2% | 1,010188 | 1,009406 | 1,010948 | 1,009907 | 1,010470 | sim |
| is_sponsored | True | 22314 | shares | +5% | 1,026915 | 1,026198 | 1,027694 | 1,026626 | 1,027205 | sim |
| is_sponsored | True | 22314 | comments_count | +1% | 1,004418 | 1,003474 | 1,005305 | 1,003898 | 1,004939 | sim |
| is_sponsored | True | 22314 | comments_count | +2% | 1,010082 | 1,009152 | 1,010982 | 1,009565 | 1,010601 | sim |
| is_sponsored | True | 22314 | comments_count | +5% | 1,026823 | 1,025928 | 1,027763 | 1,026310 | 1,027338 | sim |
| audience_age_distribution | 50+ | 2650 | taxa_engajamento | +1% | 1,009809 | 1,008838 | 1,010747 | 1,009439 | 1,010165 | sim |
| audience_age_distribution | 50+ | 2650 | taxa_engajamento | +2% | 1,019289 | 1,018387 | 1,020210 | 1,018917 | 1,019648 | sim |
| audience_age_distribution | 50+ | 2650 | taxa_engajamento | +5% | 1,047672 | 1,046676 | 1,048586 | 1,047291 | 1,048040 | sim |
| audience_age_distribution | 50+ | 2650 | shares | +1% | 1,008278 | 1,005981 | 1,010349 | 1,007985 | 1,008559 | sim |
| audience_age_distribution | 50+ | 2650 | shares | +2% | 1,017756 | 1,015486 | 1,019970 | 1,017464 | 1,018037 | sim |
| audience_age_distribution | 50+ | 2650 | shares | +5% | 1,046190 | 1,044085 | 1,048476 | 1,045922 | 1,046448 | sim |
| audience_age_distribution | 50+ | 2650 | comments_count | +1% | 1,006428 | 1,003765 | 1,009082 | 1,007039 | 1,005839 | sim |
| audience_age_distribution | 50+ | 2650 | comments_count | +2% | 1,015913 | 1,013156 | 1,018749 | 1,016530 | 1,015319 | sim |
| audience_age_distribution | 50+ | 2650 | comments_count | +5% | 1,044348 | 1,041674 | 1,047184 | 1,045011 | 1,043708 | sim |
| audience_gender_distribution | unknown | 5235 | taxa_engajamento | +1% | 1,008998 | 1,008298 | 1,009631 | 1,009055 | 1,008944 | sim |
| audience_gender_distribution | unknown | 5235 | taxa_engajamento | +2% | 1,017968 | 1,017323 | 1,018702 | 1,018024 | 1,017914 | sim |
| audience_gender_distribution | unknown | 5235 | taxa_engajamento | +5% | 1,044769 | 1,044041 | 1,045423 | 1,044824 | 1,044716 | sim |
| audience_gender_distribution | unknown | 5235 | shares | +1% | 1,007134 | 1,005532 | 1,008730 | 1,007010 | 1,007252 | sim |
| audience_gender_distribution | unknown | 5235 | shares | +2% | 1,016106 | 1,014561 | 1,017697 | 1,015983 | 1,016223 | sim |
| audience_gender_distribution | unknown | 5235 | shares | +5% | 1,042947 | 1,041257 | 1,044615 | 1,042788 | 1,043098 | sim |
| audience_gender_distribution | unknown | 5235 | comments_count | +1% | 1,007446 | 1,005517 | 1,009373 | 1,006453 | 1,008394 | sim |
| audience_gender_distribution | unknown | 5235 | comments_count | +2% | 1,016420 | 1,014304 | 1,018500 | 1,015427 | 1,017368 | sim |
| audience_gender_distribution | unknown | 5235 | comments_count | +5% | 1,043303 | 1,041179 | 1,045230 | 1,042285 | 1,044276 | sim |
| audience_location | Russia | 6459 | taxa_engajamento | +1% | 1,008733 | 1,008135 | 1,009277 | 1,008749 | 1,008717 | sim |
| audience_location | Russia | 6459 | taxa_engajamento | +2% | 1,017461 | 1,016797 | 1,018069 | 1,017478 | 1,017445 | sim |
| audience_location | Russia | 6459 | taxa_engajamento | +5% | 1,043519 | 1,042926 | 1,044107 | 1,043536 | 1,043502 | sim |
| audience_location | Russia | 6459 | shares | +1% | 1,006637 | 1,005132 | 1,007967 | 1,006217 | 1,007051 | sim |
| audience_location | Russia | 6459 | shares | +2% | 1,015372 | 1,013854 | 1,016863 | 1,014955 | 1,015784 | sim |
| audience_location | Russia | 6459 | shares | +5% | 1,041476 | 1,039969 | 1,042990 | 1,041049 | 1,041897 | sim |
| audience_location | Russia | 6459 | comments_count | +1% | 1,007392 | 1,005651 | 1,009175 | 1,006746 | 1,008029 | sim |
| audience_location | Russia | 6459 | comments_count | +2% | 1,016124 | 1,014442 | 1,017821 | 1,015480 | 1,016761 | sim |
| audience_location | Russia | 6459 | comments_count | +5% | 1,042276 | 1,040665 | 1,044036 | 1,041615 | 1,042929 | sim |

**Detectado em 72 de 72 linhas** (24/24 em cada nível de injeção: +1%, +2% e +5%).

### 3b. Injeção numa busca entre muitos segmentos (`taxa_engajamento`)

Combinações `platform × content_type × content_category × faixa_seguidores` com n entre 100 e 150: **29 candidatas**. Sorteada (seed 42): `Bilibili | video | beauty | 50-100K`, n = 137. Busca refeita com filtro n ≥ 100 (**128 de 240** combinações), com teste contra o acaso de 200 permutações do índice dentro da plataforma.

| Cenário | Efeito injetado | Segmento sorteado | n | Lift medido | IC inf. | IC sup. | IC exclui 1 | Posição no ranking | Maior lift por acaso (p95) | Supera o acaso |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +5% | Bilibili \| video \| beauty \| 50-100K | 137 | 1,045982 | 1,041436 | 1,050154 | sim | 1 de 128 | 1,006481 | sim |
| 2 | +10% | Bilibili \| video \| beauty \| 50-100K | 137 | 1,095086 | 1,090902 | 1,100069 | sim | 1 de 128 | 1,007255 | sim |

Nos dois cenários o segmento injetado sai em **1º lugar entre os 128** segmentos da busca e fica acima do p95 do acaso. Sem injeção, esse mesmo segmento tinha o lift mais baixo do Nível 4 da OS-02 (0,996816).

## 4. Bloco 4 — Caudas da distribuição

Cortes por plataforma e métrica em `bloco4_cortes_plataforma.csv`. Para cada segmento, % de posts no top 10%, top 1% e bottom 10% da sua plataforma (esperado 10%, 1% e 10%), com IC 95% de Wilson, mais o teste KS do índice do segmento contra o resto da base.

### Resumo

| Cauda | Esperado | IC exclui o esperado | taxa_engajamento | shares | comments_count | Faixa de % observada |
|---|---|---|---|---|---|---|
| top 10% | 10% | 32/105 | 0/35 | 12/35 | 20/35 | 9,4340% – 11,3175% |
| top 1% | 1% | 14/105 | 1/35 | 3/35 | 10/35 | 0,7316% – 1,5211% |
| bottom 10% | 10% | 42/105 | 1/35 | 22/35 | 19/35 | 9,0563% – 11,5361% |

**88 de 315** testes de Wilson excluem o valor esperado nominal (10%/1%/10%). **86 dos 88 estão em `shares` e `comments_count`**, que são inteiros: o corte por quantil nessas métricas não realiza 10%/1% exatos por causa dos empates no valor do corte — realiza de 10,15% a 11,19% (top 10%), 1,06% a 1,16% (top 1%) e 10,17% a 11,19% (bottom 10%), conforme `bloco4_cortes_plataforma.csv`. Comparando cada IC de Wilson com a taxa que o corte **de fato** realiza nas plataformas do segmento (coluna `*_exclui_taxa_base`), sobram **6 de 315** exclusões:

| Variável | Segmento | Métrica | n | Cauda | % observada | IC 95% Wilson | Taxa realizada pelo corte |
|---|---|---|---|---|---|---|---|
| faixa_seguidores | 50-100K | comments_count | 2597 | top 10% | 9,4340% | 8,3689% – 10,6189% | 10,6307% |
| content_type | image | shares | 10303 | top 1% | 1,3006% | 1,0993% – 1,5382% | 1,0805% |
| faixa_seguidores | ate 50K | taxa_engajamento | 2564 | top 1% | 1,5211% | 1,1147% – 2,0725% | 1,0035% |
| audience_location | USA | comments_count | 6498 | top 1% | 0,8310% | 0,6375% – 1,0826% | 1,1263% |
| audience_location | India | comments_count | 6484 | bottom 10% | 11,5361% | 10,7812% – 12,3366% | 10,6520% |
| audience_location | UK | taxa_engajamento | 6570 | bottom 10% | 9,0563% | 8,3861% – 9,7744% | 10,0050% |

**Teste KS:** 4 de 105 segmentos × métrica com p < 0,05 (3,8%), contra ~5% esperados por acaso.

| Variável | Segmento | Métrica | n | Estatística KS | p-valor |
|---|---|---|---|---|---|
| platform | Instagram | taxa_engajamento | 10423 | 0,017108 | 0,014970 |
| faixa_seguidores | 500K-1M | taxa_engajamento | 26029 | 0,013246 | 0,020323 |
| platform | RedNote | comments_count | 10402 | 0,016451 | 0,021777 |
| faixa_seguidores | 100-500K | taxa_engajamento | 21024 | 0,013039 | 0,027713 |

### Lista completa dos segmentos com IC de Wilson que exclui o esperado (88 linhas)

A última coluna é a taxa que o corte realmente realiza nas plataformas do segmento; quando ela está dentro do IC, a exclusão vem do empate no corte e não do segmento.

| Variável | Segmento | Métrica | n | Cauda | % observada | IC 95% Wilson | Taxa realizada |
|---|---|---|---|---|---|---|---|
| platform | Bilibili | shares | 10598 | top 10% | 10,7096% | 10,1350% – 11,3126% | 10,7096% |
| platform | Bilibili | comments_count | 10598 | bottom 10% | 10,8039% | 10,2270% – 11,4092% | 10,8039% |
| platform | Instagram | shares | 10423 | top 10% | 10,6687% | 10,0905% – 11,2759% | 10,6687% |
| platform | Instagram | shares | 10423 | bottom 10% | 11,1868% | 10,5959% – 11,8063% | 11,1868% |
| platform | Instagram | comments_count | 10423 | top 10% | 10,8126% | 10,2308% – 11,4233% | 10,8126% |
| platform | Instagram | comments_count | 10423 | bottom 10% | 10,9086% | 10,3244% – 11,5215% | 10,9086% |
| platform | RedNote | shares | 10402 | bottom 10% | 10,8248% | 10,2422% – 11,4364% | 10,8248% |
| platform | RedNote | comments_count | 10402 | top 10% | 10,9402% | 10,3547% – 11,5545% | 10,9402% |
| platform | TikTok | shares | 10296 | bottom 10% | 10,7615% | 10,1774% – 11,3748% | 10,7615% |
| platform | TikTok | comments_count | 10296 | top 10% | 10,7323% | 10,1490% – 11,3449% | 10,7323% |
| platform | YouTube | shares | 10495 | top 10% | 10,5860% | 10,0117% – 11,1891% | 10,5860% |
| platform | YouTube | comments_count | 10495 | top 10% | 10,6146% | 10,0396% – 11,2184% | 10,6146% |
| platform | YouTube | comments_count | 10495 | bottom 10% | 11,0148% | 10,4300% – 11,6281% | 11,0148% |
| content_type | image | shares | 10303 | top 10% | 11,0453% | 10,4545% – 11,6652% | 10,4638% |
| content_type | image | shares | 10303 | top 1% | 1,3006% | 1,0993% – 1,5382% | 1,0805% |
| content_type | image | shares | 10303 | bottom 10% | 11,1133% | 10,5208% – 11,7347% | 10,7206% |
| content_type | mixed | comments_count | 5213 | top 10% | 11,0109% | 10,1897% – 11,8896% | 10,6392% |
| content_type | mixed | comments_count | 5213 | top 1% | 1,3812% | 1,0982% – 1,7357% | 1,1254% |
| content_type | text | shares | 5198 | top 10% | 10,8503% | 10,0335% – 11,7249% | 10,4674% |
| content_type | video | shares | 31500 | bottom 10% | 10,6190% | 10,2836% – 10,9641% | 10,7242% |
| content_type | video | comments_count | 31500 | top 10% | 10,6508% | 10,3149% – 10,9963% | 10,6344% |
| content_type | video | comments_count | 31500 | top 1% | 1,1333% | 1,0223% – 1,2563% | 1,1262% |
| content_type | video | comments_count | 31500 | bottom 10% | 10,7714% | 10,4338% – 11,1186% | 10,6557% |
| content_category | beauty | shares | 21023 | top 10% | 10,6931% | 10,2825% – 11,1180% | 10,4641% |
| content_category | beauty | shares | 21023 | bottom 10% | 11,0593% | 10,6425% – 11,4904% | 10,7235% |
| content_category | beauty | comments_count | 21023 | top 10% | 10,5741% | 10,1656% – 10,9970% | 10,6359% |
| content_category | beauty | comments_count | 21023 | bottom 10% | 10,5456% | 10,1376% – 10,9680% | 10,6555% |
| content_category | lifestyle | shares | 20761 | bottom 10% | 10,4956% | 10,0860% – 10,9199% | 10,7230% |
| content_category | lifestyle | comments_count | 20761 | top 10% | 10,7509% | 10,3368% – 11,1796% | 10,6364% |
| content_category | lifestyle | comments_count | 20761 | top 1% | 1,2234% | 1,0827% – 1,3823% | 1,1263% |
| content_category | lifestyle | comments_count | 20761 | bottom 10% | 10,8328% | 10,4173% – 11,2629% | 10,6561% |
| faixa_seguidores | 100-500K | shares | 21024 | top 10% | 10,4880% | 10,0810% – 10,9094% | 10,4647% |
| faixa_seguidores | 100-500K | shares | 21024 | bottom 10% | 10,8876% | 10,4736% – 11,3158% | 10,7231% |
| faixa_seguidores | 100-500K | comments_count | 21024 | top 10% | 10,5070% | 10,0997% – 10,9288% | 10,6352% |
| faixa_seguidores | 100-500K | comments_count | 21024 | top 1% | 1,1986% | 1,0602% – 1,3549% | 1,1264% |
| faixa_seguidores | 100-500K | comments_count | 21024 | bottom 10% | 10,5784% | 10,1698% – 11,0014% | 10,6570% |
| faixa_seguidores | 500K-1M | shares | 26029 | top 10% | 10,5421% | 10,1748% – 10,9210% | 10,4648% |
| faixa_seguidores | 500K-1M | shares | 26029 | bottom 10% | 10,5459% | 10,1786% – 10,9249% | 10,7241% |
| faixa_seguidores | 500K-1M | comments_count | 26029 | top 10% | 10,8264% | 10,4547% – 11,2097% | 10,6360% |
| faixa_seguidores | 500K-1M | comments_count | 26029 | bottom 10% | 10,7880% | 10,4169% – 11,1707% | 10,6562% |
| faixa_seguidores | ate 50K | taxa_engajamento | 2564 | top 1% | 1,5211% | 1,1147% – 2,0725% | 1,0035% |
| is_sponsored | False | shares | 29900 | top 10% | 10,5619% | 10,2185% – 10,9153% | 10,4668% |
| is_sponsored | False | shares | 29900 | bottom 10% | 10,7191% | 10,3734% – 11,0748% | 10,7241% |
| is_sponsored | False | comments_count | 29900 | top 10% | 10,6054% | 10,2614% – 10,9594% | 10,6333% |
| is_sponsored | False | comments_count | 29900 | top 1% | 1,1505% | 1,0357% – 1,2778% | 1,1263% |
| is_sponsored | False | comments_count | 29900 | bottom 10% | 10,6355% | 10,2910% – 10,9900% | 10,6583% |
| is_sponsored | True | shares | 22314 | bottom 10% | 10,7287% | 10,3294% – 11,1415% | 10,7220% |
| is_sponsored | True | comments_count | 22314 | top 10% | 10,6749% | 10,2765% – 11,0869% | 10,6374% |
| is_sponsored | True | comments_count | 22314 | bottom 10% | 10,6839% | 10,2853% – 11,0960% | 10,6532% |
| audience_age_distribution | 13-18 | shares | 7852 | top 1% | 1,2481% | 1,0253% – 1,5186% | 1,0801% |
| audience_age_distribution | 13-18 | shares | 7852 | bottom 10% | 11,1437% | 10,4665% – 11,8588% | 10,7242% |
| audience_age_distribution | 13-18 | comments_count | 7852 | top 10% | 10,7489% | 10,0828% – 11,4532% | 10,6340% |
| audience_age_distribution | 13-18 | comments_count | 7852 | bottom 10% | 10,8635% | 10,1942% – 11,5710% | 10,6544% |
| audience_age_distribution | 19-25 | shares | 18276 | top 10% | 10,7627% | 10,3217% – 11,2203% | 10,4636% |
| audience_age_distribution | 19-25 | shares | 18276 | bottom 10% | 10,7135% | 10,2733% – 11,1702% | 10,7247% |
| audience_age_distribution | 19-25 | comments_count | 18276 | top 10% | 10,7190% | 10,2787% – 11,1758% | 10,6357% |
| audience_age_distribution | 19-25 | comments_count | 18276 | bottom 10% | 10,4837% | 10,0478% – 10,9362% | 10,6548% |
| audience_age_distribution | 26-35 | shares | 15700 | bottom 10% | 10,9554% | 10,4764% – 11,4536% | 10,7224% |
| audience_age_distribution | 26-35 | comments_count | 15700 | top 10% | 10,7707% | 10,2953% – 11,2653% | 10,6362% |
| audience_age_distribution | 26-35 | comments_count | 15700 | top 1% | 1,1975% | 1,0388% – 1,3799% | 1,1262% |
| audience_age_distribution | 26-35 | comments_count | 15700 | bottom 10% | 10,5987% | 10,1268% – 11,0899% | 10,6593% |
| audience_age_distribution | 36-50 | comments_count | 7736 | bottom 10% | 10,8713% | 10,1969% – 11,5844% | 10,6538% |
| audience_gender_distribution | female | shares | 20743 | top 10% | 10,4373% | 10,0285% – 10,8607% | 10,4632% |
| audience_gender_distribution | female | shares | 20743 | bottom 10% | 10,4373% | 10,0285% – 10,8607% | 10,7237% |
| audience_gender_distribution | female | comments_count | 20743 | bottom 10% | 10,4758% | 10,0664% – 10,8999% | 10,6550% |
| audience_gender_distribution | male | shares | 20987 | top 10% | 10,5589% | 10,1503% – 10,9819% | 10,4651% |
| audience_gender_distribution | male | shares | 20987 | bottom 10% | 10,9020% | 10,4875% – 11,3308% | 10,7217% |
| audience_gender_distribution | male | comments_count | 20987 | top 10% | 10,6923% | 10,2814% – 11,1176% | 10,6341% |
| audience_gender_distribution | male | comments_count | 20987 | bottom 10% | 10,8210% | 10,4078% – 11,2485% | 10,6572% |
| audience_gender_distribution | non-binary | shares | 5249 | top 1% | 1,2955% | 1,0232% – 1,6390% | 1,0799% |
| audience_gender_distribution | non-binary | shares | 5249 | bottom 10% | 11,0878% | 10,2667% – 11,9659% | 10,7214% |
| audience_gender_distribution | non-binary | comments_count | 5249 | top 10% | 11,2212% | 10,3955% – 12,1036% | 10,6293% |
| audience_gender_distribution | non-binary | comments_count | 5249 | top 1% | 1,3526% | 1,0738% – 1,7026% | 1,1262% |
| audience_gender_distribution | unknown | comments_count | 5235 | top 10% | 11,0793% | 10,2574% – 11,9582% | 10,6348% |
| audience_location | Brazil | shares | 6505 | bottom 10% | 10,7456% | 10,0160% – 11,5215% | 10,7220% |
| audience_location | Brazil | comments_count | 6505 | top 1% | 1,3067% | 1,0580% – 1,6128% | 1,1262% |
| audience_location | Germany | shares | 6497 | bottom 10% | 10,7434% | 10,0135% – 11,5197% | 10,7274% |
| audience_location | Germany | comments_count | 6497 | top 10% | 10,7896% | 10,0582% – 11,5673% | 10,6429% |
| audience_location | Germany | comments_count | 6497 | top 1% | 1,2467% | 1,0043% – 1,5468% | 1,1259% |
| audience_location | India | comments_count | 6484 | bottom 10% | 11,5361% | 10,7812% – 12,3366% | 10,6520% |
| audience_location | Japan | shares | 6553 | bottom 10% | 10,8042% | 10,0754% – 11,5789% | 10,7207% |
| audience_location | Japan | comments_count | 6553 | bottom 10% | 10,7584% | 10,0311% – 11,5318% | 10,6468% |
| audience_location | Russia | shares | 6459 | bottom 10% | 10,8531% | 10,1176% – 11,6351% | 10,7249% |
| audience_location | Russia | comments_count | 6459 | top 10% | 11,3175% | 10,5678% – 12,1133% | 10,6279% |
| audience_location | Russia | comments_count | 6459 | top 1% | 1,2695% | 1,0240% – 1,5730% | 1,1265% |
| audience_location | UK | taxa_engajamento | 6570 | bottom 10% | 9,0563% | 8,3861% – 9,7744% | 10,0050% |
| audience_location | UK | comments_count | 6570 | bottom 10% | 10,7763% | 10,0492% – 11,5491% | 10,6611% |
| audience_location | USA | shares | 6498 | bottom 10% | 10,7572% | 10,0268% – 11,5338% | 10,7252% |

## 5. Bloco 5 — Tendência no tempo

Médias mensais (geral, por platform, por content_type e por is_sponsored) em `bloco5_tendencia.csv` (`tabela = media_mensal`, 25 meses × 3 métricas × 12 escopos). Amplitude das médias mensais da base inteira: taxa_engajamento 0,198878–0,199169 (0,146% da média), shares 298,845745–300,571224 (0,575%), comments_count 199,416123–200,873441 (0,728%).

### Tendência — regressão no nível do post, `métrica ~ número do mês` (1 a 25), erros HC3

Inclinação convertida em % da média por ano.

| Escopo | Métrica | n | % da média por ano | IC 95% | p-valor |
|---|---|---|---|---|---|
| base inteira | taxa_engajamento | 52214 | -0,0034% | -0,0399% – 0,0330% | 0,8535 |
| base inteira | shares | 52214 | 0,0488% | -0,0370% – 0,1346% | 0,2646 |
| base inteira | comments_count | 52214 | 0,0064% | -0,0989% – 0,1117% | 0,9050 |
| platform = Bilibili | taxa_engajamento | 10598 | -0,0308% | -0,1119% – 0,0503% | 0,4571 |
| platform = Bilibili | shares | 10598 | -0,0356% | -0,2255% – 0,1543% | 0,7136 |
| platform = Bilibili | comments_count | 10598 | -0,0994% | -0,3342% – 0,1353% | 0,4064 |
| platform = Instagram | taxa_engajamento | 10423 | 0,0269% | -0,0550% – 0,1089% | 0,5192 |
| platform = Instagram | shares | 10423 | 0,1293% | -0,0633% – 0,3218% | 0,1882 |
| platform = Instagram | comments_count | 10423 | 0,1191% | -0,1180% – 0,3562% | 0,3248 |
| platform = RedNote | taxa_engajamento | 10402 | 0,0426% | -0,0397% – 0,1250% | 0,3104 |
| platform = RedNote | shares | 10402 | 0,0373% | -0,1590% – 0,2336% | 0,7094 |
| platform = RedNote | comments_count | 10402 | 0,0490% | -0,1854% – 0,2834% | 0,6819 |
| platform = TikTok | taxa_engajamento | 10296 | -0,0748% | -0,1572% – 0,0075% | 0,0748 |
| platform = TikTok | shares | 10296 | -0,0848% | -0,2774% – 0,1079% | 0,3884 |
| platform = TikTok | comments_count | 10296 | -0,0005% | -0,2358% – 0,2347% | 0,9966 |
| platform = YouTube | taxa_engajamento | 10495 | 0,0181% | -0,0618% – 0,0980% | 0,6571 |
| platform = YouTube | shares | 10495 | **0,1975%** | 0,0093% – 0,3857% | **0,0397** |
| platform = YouTube | comments_count | 10495 | -0,0295% | -0,2652% – 0,2061% | 0,8059 |
| content_type = image | taxa_engajamento | 10303 | -0,0275% | -0,1097% – 0,0548% | 0,5126 |
| content_type = image | shares | 10303 | 0,0591% | -0,1395% – 0,2577% | 0,5596 |
| content_type = image | comments_count | 10303 | 0,0473% | -0,1887% – 0,2833% | 0,6946 |
| content_type = mixed | taxa_engajamento | 5213 | -0,0367% | -0,1516% – 0,0782% | 0,5318 |
| content_type = mixed | shares | 5213 | -0,0298% | -0,2997% – 0,2401% | 0,8286 |
| content_type = mixed | comments_count | 5213 | -0,2150% | -0,5527% – 0,1227% | 0,2121 |
| content_type = text | taxa_engajamento | 5198 | 0,0294% | -0,0862% – 0,1450% | 0,6183 |
| content_type = text | shares | 5198 | 0,0843% | -0,1891% – 0,3577% | 0,5455 |
| content_type = text | comments_count | 5198 | -0,1637% | -0,4966% – 0,1691% | 0,3350 |
| content_type = video | taxa_engajamento | 31500 | 0,0047% | -0,0422% – 0,0517% | 0,8433 |
| content_type = video | shares | 31500 | 0,0516% | -0,0579% – 0,1611% | 0,3555 |
| content_type = video | comments_count | 31500 | 0,0574% | -0,0781% – 0,1929% | 0,4065 |
| is_sponsored = False | taxa_engajamento | 29900 | -0,0079% | -0,0559% – 0,0400% | 0,7452 |
| is_sponsored = False | shares | 29900 | 0,0594% | -0,0539% – 0,1726% | 0,3042 |
| is_sponsored = False | comments_count | 29900 | -0,0147% | -0,1541% – 0,1247% | 0,8363 |
| is_sponsored = True | taxa_engajamento | 22314 | 0,0026% | -0,0536% – 0,0587% | 0,9279 |
| is_sponsored = True | shares | 22314 | 0,0352% | -0,0962% – 0,1667% | 0,5996 |
| is_sponsored = True | comments_count | 22314 | 0,0342% | -0,1264% – 0,1949% | 0,6761 |

**1 de 36** tendências tem p < 0,05 (YouTube, shares). Todas as inclinações ficam entre −0,2150% e +0,1975% da média por ano.

### Primeiro ano vs. último ano, por plataforma

Razão entre a média dos meses 14–25 e a dos meses 1–12, com IC 95% bootstrap. A base tem 25 meses, então o mês 13 fica fora da comparação.

| Plataforma | Métrica | n | Razão | IC 95% | Exclui 1 |
|---|---|---|---|---|---|
| Bilibili | taxa_engajamento | 10141 | 0,999770 | 0,998862 – 1,000717 | não |
| Bilibili | shares | 10141 | 0,999714 | 0,997596 – 1,001987 | não |
| Bilibili | comments_count | 10141 | 0,999396 | 0,996616 – 1,002211 | não |
| Instagram | taxa_engajamento | 10004 | 1,000095 | 0,999107 – 1,001048 | não |
| Instagram | shares | 10004 | 1,001186 | 0,998985 – 1,003443 | não |
| Instagram | comments_count | 10004 | 1,002945 | 1,000142 – 1,005613 | **sim** |
| RedNote | taxa_engajamento | 9961 | 1,000473 | 0,999547 – 1,001481 | não |
| RedNote | shares | 9961 | 1,000692 | 0,998338 – 1,003080 | não |
| RedNote | comments_count | 9961 | 1,000039 | 0,997199 – 1,002956 | não |
| TikTok | taxa_engajamento | 9867 | 0,999485 | 0,998531 – 1,000433 | não |
| TikTok | shares | 9867 | 0,999030 | 0,996619 – 1,001267 | não |
| TikTok | comments_count | 9867 | 1,000483 | 0,997593 – 1,003135 | não |
| YouTube | taxa_engajamento | 10046 | 1,000193 | 0,999185 – 1,001116 | não |
| YouTube | shares | 10046 | 1,001634 | 0,999277 – 1,003752 | não |
| YouTube | comments_count | 10046 | 1,000379 | 0,997853 – 1,003373 | não |

**1 de 15** razões tem IC que exclui 1. As 15 razões ficam entre 0,999030 e 1,002945 (−0,10% a +0,29%).

---

## Pontos suspeitos ou problemas encontrados

1. **Todos os 105 segmentos × métrica são equivalentes a ±1%, e o teto do efeito é 0,38%.** O maior efeito máximo plausível da base inteira é 0,3799% (`faixa_seguidores = ate 50K`, comments_count, n = 2.564) e o menor 0,0350% (`is_sponsored`, taxa_engajamento). Nenhuma das 105 linhas tem IC 95% que exclua 1 (0/105) — na OS-02, com os mesmos segmentos agregados, a taxa de exclusão também ficava abaixo dos 5% esperados por acaso.

2. **O menor efeito detectável é muito menor que o limite de equivalência, em todas as linhas.** O MDE vai de 0,0599% a 0,3996%, com o pior caso (0,3996%) ainda ~2,5× menor que 1%. Para `taxa_engajamento` o MDE nunca passa de 0,1387%. Ou seja: a base teria poder de 80% para detectar efeitos de 0,06% a 0,40%, e não detectou nenhum. Falta de poder não explica o resultado nulo nos agregados do Bloco 1.

3. **O controle positivo funciona em 100% dos casos: 72/72 no 3a e 2/2 no 3b.** Mesmo a injeção mais fraca (+1%) é detectada em 24 de 24 combinações variável × métrica, com IC 95% excluindo 1 e as duas metades acima de 1. No 3b, o segmento com +5% e com +10% salta para o 1º lugar entre 128 segmentos e supera o p95 do acaso. O método não é cego a efeitos reais do tamanho dos que se procuram.

4. **O lift medido é sistematicamente menor que o efeito injetado — efeito de diluição do denominador.** Como o índice divide pela média da própria plataforma (ou pela média geral, no caso de `platform`), os posts do segmento entram no denominador e o lift medido fica em `efeito / (1 + efeito × participação do segmento)`. Exemplos: `is_sponsored = True` (42,74% da base) com +5% mede 1,027996 em vez de 1,05 (previsto pela fórmula: 1,028033); `platform = TikTok` (19,72%) com +1% mede 1,008041. Quanto maior o segmento, maior a perda — o segmento de menor n de `is_sponsored` ocupa quase metade da base, então é o caso mais afetado. Isto não é erro de cálculo, mas significa que o lift do método subestima efeitos de segmentos grandes.

5. **No Bloco 4, 88 de 315 testes de Wilson excluem o esperado nominal, mas 86 deles vêm de empates no corte, não dos segmentos.** `shares` e `comments_count` são inteiros e os cortes de quantil caem em valores repetidos, então o corte realiza de 10,15% a 11,19% dos posts no "top 10%" e de 1,06% a 1,16% no "top 1%", em vez de 10% e 1% (ver `bloco4_cortes_plataforma.csv`). Com a variável `platform`, onde o segmento é a própria plataforma, a % observada é **idêntica** à taxa realizada pelo corte (ex.: Bilibili/shares, 10,7096% nos dois) — ou seja, a exclusão é 100% artefato. Comparando o IC de Wilson com a taxa que o corte de fato realiza, sobram 6 de 315 exclusões (1,9%, abaixo dos 5% de acaso). Em `taxa_engajamento`, que é contínua, o corte realiza 10,0019%–10,0077% e só 2 das 105 linhas excluem o nominal.

6. **As duas exclusões de cauda em `taxa_engajamento` são as únicas que sobrevivem ao ajuste de empate nessa métrica.** `faixa_seguidores = ate 50K` tem 1,5211% dos posts no top 1% da plataforma (39 de 2.564, contra 25,6 esperados; IC 1,1147%–2,0725%) e `audience_location = UK` tem 9,0563% no bottom 10% (595 de 6.570, contra 657 esperados; IC 8,3861%–9,7744%). Registro como achado isolado de cauda: os mesmos dois segmentos têm lift agregado dentro de ±0,13% de 1 no Bloco 1.

7. **O teste KS não separa nada: 4 de 105 com p < 0,05 (3,8%), abaixo dos ~5% de acaso.** O menor p-valor da base inteira é 0,014970 (`platform = Instagram`, taxa_engajamento) e a maior estatística KS é 0,017108 — distâncias de distribuição da ordem de 1,7 ponto percentual.

8. **Nenhuma tendência temporal: 1 de 36 inclinações com p < 0,05, contra ~1,8 esperadas por acaso.** A única é YouTube/shares, +0,1975% da média por ano (IC 0,0093%–0,3857%, p = 0,0397), com limite inferior a 0,009 ponto de zero. As 36 inclinações ficam todas entre −0,2150% e +0,1975% por ano; em 25 meses isso acumula no máximo ~0,45%. As médias mensais da base inteira variam 0,146% (taxa_engajamento), 0,575% (shares) e 0,728% (comments_count) entre o menor e o maior mês.

9. **Primeiro ano vs. último ano: 1 de 15 razões exclui 1, por margem mínima.** Instagram/comments_count, razão 1,002945 com IC 1,000142–1,005613 — o limite inferior está a 0,014% de conter 1. As outras 14 razões têm IC contendo 1.

10. **Os meses das pontas são parciais e desiguais.** O mês 1 (2023-05) tem 188 posts (só 29–31 de maio de 2023) e o mês 25 (2025-05) tem 1.974 (até 28 de maio de 2025); os 23 meses do meio têm de 1.914 a 2.347. A regressão no nível do post pondera cada mês pelo seu volume, então o mês 1 pesa ~1/12 de um mês normal. Na comparação primeiro × último ano, o mês 13 fica de fora (25 meses no total).

11. **Desvio de entrega registrado.** A OS pede um .csv por bloco; o Bloco 4 saiu em dois arquivos porque a OS também pede explicitamente o cálculo dos cortes por plataforma e métrica, que não cabe na tabela por segmento (`bloco4_cortes_plataforma.csv`, 45 linhas). Pelo mesmo motivo, `bloco4_caudas.csv` tem duas colunas por cauda além das pedidas (`*_taxa_base_plataformas_pct` e `*_exclui_taxa_base`), que são a base do ponto 5 acima. O Bloco 5 saiu em um único .csv em formato longo (coluna `tabela` separa médias mensais, tendências e primeiro × último ano).
