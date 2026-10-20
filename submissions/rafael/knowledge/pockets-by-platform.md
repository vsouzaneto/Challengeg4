# Bolsões e top 1% por plataforma — insights e como usar

Fonte: `solution/src/social_insights/discovery.py` (`scan_by_platform`, `platform_summary`, `daypart_top_rate`) · notebook: `solution/notebooks/11_bolsoes_por_plataforma.ipynb` · 2026-10-19.
Método do `pockets-and-top1.md`, rodado **dentro** de cada plataforma (top 5% e top 1% recalculados por plataforma; ~10 mil posts cada). 14.763 bolsões no total (5 plataformas × 3 métricas).

## Panorama
- **31** bolsões replicados ou robustos; **1** robusto, inclusive na correção global das 15 tabelas.
- A taxa de replicação por plataforma fica perto do acaso (0–8%), exceto YouTube · views (12,5%, p = 0,07). Os itens abaixo são **hipóteses priorizadas**, exceto o destaque do TikTok.

## ⭐ Destaque robusto (único de todo o projeto): TikTok · beauty em espanhol → likes
- **10,0%** dos 451 posts chegam ao top 5% de likes do TikTok (**2,02x**). Nas metades: 2,23x e 1,83x.
- q (TikTok) = 0,002 · **q global (14,7 mil testes) = 0,035**.
- O efeito está na **cauda**: a média de likes quase não muda (1.516 vs. 1.510, +0,4%), mas a chance de bombar dobra.
- **Ressalvas:** não aparece nas outras plataformas (beauty·espanhol: 4,5–5,5%) nem em views/shares do TikTok (4,7% / 4,4%); o desvio de likes no segmento é um pouco maior (42,6 vs. 38,9; Levene p = 0,045).
- **Ação:** hipótese nº 1 da fila de testes (`strategy.test_queue`): A/B com o mesmo conteúdo em espanhol × inglês, ~1.430 posts por grupo. Não mudar o mix antes do resultado.

## Horário × comentários (top 1%) por plataforma
| Plataforma | madrugada | manhã | tarde | noite | hora mediana top vs. resto | evidência |
|---|---|---|---|---|---|---|
| **YouTube** | **1,53%** | **1,37%** | 0,93% | **0,76%** | **9h vs. 12h** (q = 0,02) | **replicada** (p = 0,044 e 0,034) |
| RedNote | 1,28% | 1,32% | **0,58%** | 1,08% | 8h vs. 11h | qui² p = 0,04 |
| Instagram | 1,27% | 1,32% | 1,27% | 0,79% | 11h vs. 12h | n.s. |
| Bilibili | 1,39% | 0,84% | 1,16% | 1,05% | 11h vs. 11h | n.s. |
| TikTok | 1,19% | 1,17% | 0,86% | **1,36%** | 11h vs. 11h | n.s. (sem padrão) |
(base = 1%)
- **O insight geral "postar cedo → mais comentários" é puxado pelo YouTube.** No TikTok, não vale. **A recomendação de horário deve ser por plataforma.**

## Insights replicados por plataforma (hipóteses para A/B)
| Plataforma | Métrica | Bolsão | Chance de top 5% |
|---|---|---|---|
| TikTok | views | vídeo longo (180–360 s) × terça | 1,91x |
| TikTok | views | audiência 19–25 | **0,74x** |
| TikTok | likes | janeiro | 1,61x |
| TikTok | likes | muito longo (360+) × tarde | 1,54x |
| TikTok | comentários | duração 174–316 | 1,37x |
| TikTok | comentários | lifestyle × inglês | 1,33x |
| YouTube | views | tech × vídeo longo (180–360 s) | 1,65x |
| YouTube | views | tech × creator mega (500K+) | 1,46x |
| YouTube | views | audiência masculina × Japão | 1,60x (feminina × Japão: **0,46x**) |
| YouTube | comentários | creator macro × audiência Brasil | 1,72x |
| YouTube | comentários | sábado × audiência feminina | 1,57x |
| Bilibili | views | chinês × creator mega | 1,51x |
| Bilibili | views | vídeo × audiência Japão | 1,49x |
| Bilibili | views | tech × sexta | 1,69x |
| Bilibili | comentários | hindi | 1,47x |
| Bilibili | comentários | médio (60–180) × quarta | **0,50x** |
| Instagram | comentários | hora 16–21 | **0,69x** |
| Instagram | comentários | audiência 26–35 × Alemanha | 1,71x |
| Instagram | likes | japonês × tarde | 1,86x |
| Instagram | likes | japonês × creator macro | 1,61x |
| RedNote | likes | texto × lifestyle | 1,58x |
| RedNote | comentários | médio (60–180) × audiência Índia | 1,56x |
| RedNote | comentários | quinta × audiência feminina | **0,43x** |
| RedNote | views | tech × terça | **0,31x** |

## Top 1% por plataforma: semelhanças antes de postar
- **Receita comum:** não há. Em 14 de 15 combinações, o top 1% é tão diverso quanto sorteios. Exceção: YouTube · likes (36,2% vs. 34,3% de atributos em comum; p = 0,04, esperado ~1 em 15).
- **Creators campeões:** não há, em nenhuma plataforma.
- **Pistas numéricas:**
  - TikTok · likes: top 1% com vídeos **mais curtos** (132 vs. 175; quase replicado).
  - YouTube · comentários: postados às **9h** (replicado).
  - YouTube/Instagram · views: postados mais cedo (não replicado).

## Mensagens para o site
1. "Cada plataforma tem seus bolsões, e um deles é robusto: no TikTok, beauty em espanhol dobra a chance de um post bombar em likes."
2. "Horário importa no YouTube, não no TikTok: no YouTube, o top 1% de comentários sai às 9h; no TikTok, a noite vai tão bem quanto a manhã."
3. "Não existe receita universal: os top 1% de cada plataforma são tão diferentes entre si quanto posts sorteados."

## Como utilizar
```python
from social_insights import data, discovery as dv
df = data.load_posts()
tables = dv.scan_by_platform(df, "likes")            # bolsões por plataforma (colunas: plataforma, evidência, lifts por metade…)
dv.platform_summary(tables)                          # replicação por plataforma × métrica
dv.insight_cards(tables[tables.plataforma == "TikTok"], n=5)
dv.daypart_top_rate(df, "comments_count")            # % no top 1% por período do dia, em cada plataforma
```
**Qualidade:** `solution/tests/test_discovery.py` verifica que um bolsão plantado só no TikTok aparece só no TikTok e que um efeito de manhã é detectado em todas as plataformas.
