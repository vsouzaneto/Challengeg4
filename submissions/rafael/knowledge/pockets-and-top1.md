# Bolsões de desempenho e top 1% — insights exploratórios e como usar

Fonte: `solution/src/social_insights/discovery.py` · notebook: `solution/notebooks/10_bolsoes_e_top1.ipynb` · 2026-10-19 · 52.214 posts.
Pedido: tratar variações como a de "vídeos > 480 s" como **insights** e buscar mais, além de achar semelhanças pré-postagem entre os top 1%.

## Como os insights são classificados
| Evidência | Critério | Uso |
|---|---|---|
| **robusta** | sobrevive à correção de todos os testes (FDR) | decisão |
| **replicada** | p < 0,05 na 1ª metade do período e mesma direção com p < 0,05 na 2ª | hipótese forte: teste A/B |
| **exploratória** | p < 0,05 nos dados completos | hipótese: monitorar |

**Bolsão** = valor de atributo, janela numérica (decis contíguos de duração, seguidores, hora e palavras da legenda) ou par de valores. Métrica: % do bolsão no top 5%. São 1.569 bolsões por métrica (views, likes, comentários).

## Panorama (honestidade para o site)
| Métrica | p < 0,05 | esperado por acaso | replicados | taxa de replicação | robustos |
|---|---|---|---|---|---|
| views | 84 | 78 | 6 | 6,4% | 0 |
| likes | 62 | 78 | 5 | 6,0% | 0 |
| comentários | 91 | 78 | 2 | 3,1% | 0 |
- A taxa de replicação esperada por acaso é ~5%. **No conjunto**, os padrões não persistem acima do acaso (ρ entre metades ≈ 0). Por isso cada bolsão é uma **hipótese priorizada**, não um efeito provado.

## ⭐ Insight mais forte: horário × comentários (top 1%)
- Os posts do **top 1% de comentários** saem mais cedo: hora mediana **10h** vs. 12h no resto.
- Sobrevive à correção entre os 12 testes numéricos do top 1% (q ≈ 0,02) e **se repete nas duas metades** (p = 0,013 e 0,047).
- Taxa de entrada no top 1% de comentários: **madrugada 1,33% · manhã 1,20% · tarde 0,96% · noite 1,01%**. Por hora, de 0h a 8h fica acima de 1% e entre 15h e 20h fica abaixo.
- Coerente com o bolsão exploratório "hora 0–4h → 1,13x mais top 5% de comentários".
- **Ação:** o padrão é puxado pelo YouTube (`pockets-by-platform.md`) e não muda a média de comentários. Confirmar por A/B exigiria ~17 mil posts por grupo (`strategy.test_queue`), então: usar como desempate de agenda no YouTube e acompanhar no histórico. A regra geral continua "sem melhor horário".

## Insights replicados (hipóteses fortes para A/B)
| Métrica | Bolsão | Top 5% | Lift (1ª · 2ª metade) |
|---|---|---|---|
| views | duração longa (180–360 s) × audiência de gênero "unknown" | 7,4% | 1,48x (1,50 · 1,46) |
| views | madrugada × quinta-feira | 6,7% | 1,33x (1,35 · 1,31) |
| views | tech × sexta-feira | 6,7% | 1,33x (1,35 · 1,31) |
| views | seguidores 600–800 mil | 5,6% | 1,14x (1,15 · 1,12) |
| views | beauty × muito longo (360+ s) | 4,2% | **0,81x** (0,82 · 0,80) |
| views | lifestyle × sexta-feira | 4,0% | **0,77x** (0,74 · 0,81) |
| likes | texto × japonês | 8,3% | 1,66x (1,61 · 1,72) |
| likes | longo (180–360 s) × quarta | 6,6% | 1,33x (1,32 · 1,34) |
| likes | lifestyle × chinês | 5,9% | 1,20x (1,24 · 1,17) |
| likes | segunda × audiência EUA | 3,0% | **0,58x** (0,58 · 0,59) |
| likes | tech × médio (60–180 s) | 4,1% | **0,81x** (0,78 · 0,83) |
| comentários | Bilibili × hindi | 7,9% | 1,38x (1,48 · 1,29) |
| comentários | legenda de 10–14 palavras | 5,1% | **0,87x** (0,85 · 0,88) |

## Exploratórios em destaque (monitorar)
- **Vídeos de 504–599 s:** 0,82x de chance de top 5% de views (p = 0,03). Não replicou (1ª metade p = 0,24; 2ª p = 0,05).
- Comentários: madrugada × audiência 36–50 (1,30x), quinta × audiência feminina (0,76x).
- Likes: janeiro (1,19x), micro creators × audiência EUA (1,74x, n = 287).

## Top 1%: o que têm em comum antes de postar?
- **Perfil categórico:** nenhum atributo significativo após a correção. Pistas fracas no top 1% de views: audiência EUA 1,22x; agosto 0,71x.
- **Perfil numérico:** além do horário × comentários, há uma pista fraca no top 1% de likes, com legenda um pouco mais longa (19 vs. 18 palavras; q = 0,2).
- **Semelhança entre si:** os posts top 1% compartilham ~29,6% dos atributos, **igual** a conjuntos sorteados (p = 0,52 views · 0,50 likes · 0,24 comentários). Não há "receita" comum.
- **Creators:** o nº de creators com 2+ posts no top é o esperado por acaso (28 vs. 24 em views, p = 0,23).
- **Entre métricas:** quase nenhum post é top 1% em duas métricas (ex.: views & likes: 2 vs. 5,5 esperados), então "top em views" ≠ "top em likes".

## Mensagens para o site
1. "Buscamos 4.700 bolsões (atributos, janelas e combinações) e ranqueamos cada um pelo nível de evidência."
2. "O achado mais forte: posts que saem de madrugada e de manhã entram mais no top 1% de comentários, num padrão que se repetiu nos dois anos."
3. "13 combinações se repetiram nas duas metades do período, e elas são a fila de testes A/B."
4. "Os top 1% não seguem uma receita: são tão diferentes entre si quanto posts sorteados."

**Gráficos sugeridos:** vulcão de bolsões por métrica; dispersão lift 1ª × 2ª metade (replicados em destaque); barras de top 1% de comentários por período do dia e linha por hora; histograma de similaridade (sorteios × top 1%).

## Como utilizar
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, discovery as dv

df = data.load_posts()
pockets = dv.scan_pockets(df, "views")        # todos os bolsões, com evidência (robusta / replicada / exploratória)
dv.replication_summary(pockets)               # quanto replica vs. acaso
dv.insight_cards(pockets, n=10)               # frases prontas para o site
top = dv.top_mask(df, "comments_count")       # top 1%
dv.top_profile(df, "comments_count"); dv.top_numeric_profile(df, "comments_count")
dv.similarity_test(df, top); dv.creator_concentration(df, top)
dv.top_overlap(df, ["views", "likes", "comments_count", "shares"])
```
- **Parâmetros:** `TOP_Q` (0,95), `TOP1_Q` (0,99), `MIN_N` (200 posts por bolsão), `MAX_WINDOW_DECILES` (3), `PAIR_FEATURES`.
- **Rotina sugerida:** rodar `scan_pockets` todo mês com os dados novos. Um bolsão que continua aparecendo sobe de "exploratório" para "replicado".
- **Qualidade:** `solution/tests/test_discovery.py` verifica que um bolsão plantado sai como robusto e replicado, que a replicação fica no acaso em dados de ruído, que a similaridade bate com o cálculo exato e que um top homogêneo é detectado.
