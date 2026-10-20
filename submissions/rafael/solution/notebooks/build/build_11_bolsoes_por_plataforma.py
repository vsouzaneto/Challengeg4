# Builds 11_bolsoes_por_plataforma.ipynb: pocket discovery and top-1% analysis inside each platform.
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 11 — Bolsões e top 1% **por plataforma**

Mesmo método do notebook 10, rodado **dentro** de cada plataforma: o top 5% e o top 1% são recalculados por plataforma, e a própria plataforma não entra como atributo.
Evidência: **robusta** (FDR na tabela da plataforma; marcamos também a correção **global**, somando as 15 tabelas) · **replicada** (nas 2 metades do período) · **exploratória** (p < 0,05).
Cada plataforma tem ~10 mil posts, um quinto da base, então os testes têm menos poder que no notebook 10.
""")
nb.code(SETUP + '''
from scipy import stats
from statsmodels.stats.multitest import multipletests
from social_insights import discovery as dv
METRICS = ["views", "likes", "comments_count"]
PLATFORMS = data.PLATFORMS
T = pd.concat([dv.scan_by_platform(df, m, platforms=PLATFORMS) for m in METRICS], ignore_index=True)
T["q_global"] = multipletests(T["p_value"], method="fdr_bh")[1]
summary = dv.platform_summary(T)
summary[["bolsões testados", "p<0,05 nos dados completos", "esperado por acaso", "descobertos na 1ª metade", "replicaram na 2ª metade",
         "taxa de replicação (%)", "p (replicação acima do acaso)", "robustos (FDR)"]].round(3)
''')

nb.md("## 1. Panorama: quantos insights replicados/robustos em cada plataforma?")
nb.code("""
strong = T[T["evidência"].isin(["robusta (FDR)", "replicada (2 metades)"])]
counts = strong.pivot_table(index="plataforma", columns="alvo", values="bolsão", aggfunc="count", fill_value=0).reindex(index=PLATFORMS, columns=METRICS, fill_value=0)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
plots.heatmap(ax, counts.astype(float), "Bolsões replicados ou robustos", cmap="Blues", vmin=0, fmt="{:.0f}")
plt.show()
display(Markdown(f"**Total:** {len(strong)} bolsões replicados ou robustos · robustos na tabela da plataforma: {int((T['evidência'] == 'robusta (FDR)').sum())} · "
                 f"robustos na correção global (15 tabelas, {len(T):,} testes): {int((T['q_global'] < 0.05).sum())}"))
""")

nb.md("## 2. ⭐ Destaque robusto: TikTok · beauty em espanhol → likes")
nb.code("""
tk = df[df.platform == "TikTok"].copy()
tk["top5_likes"] = tk.likes >= tk.likes.quantile(0.95)
row = T[(T.plataforma == "TikTok") & (T.alvo == "likes") & (T["bolsão"] == "beauty · Spanish")].iloc[0]
display(Markdown(f"**{row['taxa top 5% (%)']:.1f}%** dos {row['posts']} posts chegam ao top 5% de likes do TikTok (**{row['lift']:.2f}x**). "
                 f"1ª metade {row['lift 1ª metade']:.2f}x · 2ª metade {row['lift 2ª metade']:.2f}x · q (TikTok) = {row['q_value']:.3f} · q (global) = {row['q_global']:.3f}"))
fig, axes = plt.subplots(1, 2, figsize=(15, 4))
for ax, (filt, by, title) in zip(axes, [(tk.content_category == "beauty", "language", "TikTok · beauty: por idioma"),
                                        (tk.language == "Spanish", "content_category", "TikTok · espanhol: por categoria")]):
    g = tk[filt].groupby(by)["top5_likes"].agg(["mean", "size"])
    g["ci"] = 1.96 * np.sqrt(g["mean"] * (1 - g["mean"]) / g["size"])
    ax.bar(g.index, g["mean"] * 100, yerr=g["ci"] * 100, color=[plots.ORANGE if i in ("Spanish", "beauty") else plots.BLUE for i in g.index],
           width=0.55, capsize=4)
    ax.axhline(5, color=plots.GRAY, linestyle="--", label="5% (base)"); ax.set_ylabel("% no top 5% de likes"); ax.set_title(title); ax.legend(fontsize=8)
fig.tight_layout(); plt.show()
display(Markdown(f"Média de likes: {tk.loc[(tk.content_category == 'beauty') & (tk.language == 'Spanish'), 'likes'].mean():,.1f} vs. "
                 f"{tk.loc[~((tk.content_category == 'beauty') & (tk.language == 'Spanish')), 'likes'].mean():,.1f} no resto do TikTok"))
""")
nb.md("""
**Leitura:** é o **único achado de todo o projeto que sobrevive à correção global** (≈ 14,7 mil testes por plataforma, q ≈ 0,03), e ele **se repete nos dois anos**.
O efeito é na **cauda**: a média de likes quase não muda (+0,4%), mas a chance de um post bombar em likes **dobra**.
**Ação:** priorizar conteúdo de beauty em espanhol no TikTok e validar com teste A/B (ex.: versão em espanhol × inglês do mesmo conteúdo).
""")

nb.md("## 3. Insights replicados por plataforma")
nb.code("""
for p in PLATFORMS:
    sub = T[T.plataforma == p].sort_values(["evidência", "p_value"], ascending=[False, True])
    cards = pd.concat([dv.insight_cards(sub[sub.alvo == m], n=4) for m in METRICS], ignore_index=True)
    cards = cards[cards["evidência"] != "exploratória"] if (cards["evidência"] != "exploratória").any() else cards.head(3)
    display(Markdown(f"### {p}"))
    display(cards.style.hide(axis="index").set_properties(**{"text-align": "left"}))
""")

nb.md("## 4. Horário × comentários em cada plataforma")
nb.code("""
dp = dv.daypart_top_rate(df, "comments_count").reindex(PLATFORMS)
order = ["madrugada", "manhã", "tarde", "noite"]
fig, axes = plt.subplots(1, 2, figsize=(16, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
plots.heatmap(axes[0], dp[order], "% no top 1% de comentários (base 1%)", cmap="RdBu_r", vmin=0.4, vmax=1.6, fmt="{:.2f}")
x = np.arange(len(order)); w = 0.16
for i, p in enumerate(PLATFORMS):
    axes[1].bar(x + (i - 2) * w, dp.loc[p, order], width=w, label=p)
axes[1].axhline(1, color=plots.GRAY, linestyle="--"); axes[1].set_xticks(x, order); axes[1].legend(fontsize=8, ncol=5)
axes[1].set_title("Chance de top 1% de comentários por período do dia")
fig.tight_layout(); plt.show()
yt = df[df.platform == "YouTube"]; top = yt.comments_count >= yt.comments_count.quantile(0.99); half = yt.post_date < yt.post_date.median()
halves = [{"metade": n, "hora mediana top": yt.loc[top & h, "hour"].median(), "hora mediana demais": yt.loc[~top & h, "hour"].median(),
           "p": stats.mannwhitneyu(yt.loc[top & h, "hour"], yt.loc[~top & h, "hour"]).pvalue, "posts top": int((top & h).sum())}
          for n, h in [("1ª", half), ("2ª", ~half)]]
display(dp.round(3))
display(Markdown("**YouTube por metade do período:**")); display(pd.DataFrame(halves).round(3))
""")
nb.md("""
**Leitura:** o insight geral "postar cedo → mais posts no top 1% de comentários" vem principalmente do **YouTube**.
Lá, o top 1% sai às **9h** na mediana contra 12h (q ≈ 0,02), com madrugada 1,53% e manhã 1,37% contra noite 0,76%, e **se repete nos dois anos**.
No **RedNote**, a tarde é fraca (0,58%; qui² p = 0,04). Instagram e Bilibili seguem a mesma direção, sem significância.
No **TikTok**, não há padrão: a noite é até a melhor faixa (1,36%). **A recomendação de horário deve ser por plataforma.**
""")

nb.md("## 5. Top 1% por plataforma: semelhanças antes da postagem")
nb.code("""
rows, sims = [], []
for p in PLATFORMS:
    sub = df[df.platform == p].reset_index(drop=True)
    for m in METRICS:
        top = dv.top_mask(sub, m)
        prof = dv.top_numeric_profile(sub, m).reset_index().assign(plataforma=p, alvo=m)
        rows.append(prof)
        sim = dv.similarity_test(sub, top, draws=100)
        conc = dv.creator_concentration(sub, top, draws=100)
        sims.append({"plataforma": p, "alvo": m, "posts top": int(top.sum()), "similaridade top (%)": sim["similaridade média no top (%)"],
                     "similaridade sorteios (%)": sim["similaridade em sorteios (%)"], "p similaridade": sim["p_value"],
                     "creators ≥2 no top": conc["creators com ≥2 posts no top"], "esperado": conc["esperado por acaso"], "p creators": conc["p_value"]})
numeric = pd.concat(rows, ignore_index=True)
numeric["q (60 testes)"] = multipletests(numeric["p_value"], method="fdr_bh")[1]
display(Markdown("**Variáveis numéricas mais diferentes no top 1% (menor p):**"))
display(numeric.sort_values("p_value").head(8)[["plataforma", "alvo", "variável", "mediana top 1%", "mediana demais", "efeito (rank-biserial)",
                                                "p_value", "p 1ª metade", "p 2ª metade", "q (60 testes)"]].round(3))
display(Markdown("**O top 1% de cada plataforma é mais parecido entre si do que conjuntos sorteados? Concentra-se em poucos creators?**"))
pd.DataFrame(sims).set_index(["plataforma", "alvo"]).round(3)
""")
nb.md("""
**Leitura:**
- **Semelhança:** em 14 de 15 combinações (plataforma × métrica), o top 1% é tão diverso quanto conjuntos sorteados. A exceção é **YouTube · likes**: 36,2% de atributos em comum vs. 34,3% (p = 0,04). Em 15 testes, ~1 assim é esperado por acaso, então fica como pista exploratória. Não há creators campeões em nenhuma plataforma.
- **Pistas numéricas no top 1% (antes de postar):**
  - **TikTok · likes:** posts **mais curtos** (duração mediana 132 vs. 175; p = 0,003; 2ª metade p = 0,009, 1ª p = 0,09), o que é quase replicado.
  - **YouTube · comentários:** postados mais cedo (9h vs. 12h), replicado nas 2 metades.
  - **YouTube e Instagram · views:** postados mais cedo (9h–9h30 vs. 12h; p = 0,02–0,03), mas não replicado.
  - Nessa família ampla (60 testes), nenhuma passa de q < 0,05 (melhores q ≈ 0,11). Ou seja, são **hipóteses priorizadas**.

## 6. Resumo por plataforma (para o time)
| Plataforma | Insight mais forte | Evidência | Ação |
|---|---|---|---|
| **TikTok** | beauty em espanhol → 2x mais chance de top 5% de likes | **robusta** (q global 0,03) + replicada | priorizar e testar A/B |
| **TikTok** | top 1% de likes com vídeos mais curtos (~130 vs. 175) | quase replicada | testar versões mais curtas |
| **YouTube** | top 1% de comentários sai às 9h na mediana (madrugada/manhã) | replicada + q 0,02 | publicar conteúdo de conversa antes do meio-dia |
| **YouTube** | tech com vídeo longo (180–360 s) ou creator mega → mais top 5% de views (1,5–1,6x) | replicada | teste A/B |
| **Bilibili** | hindi → 1,5x mais top 5% de comentários; chinês × creator mega → 1,5x views | replicada | teste A/B |
| **Instagram** | 16h–21h → 0,69x no top 5% de comentários; japonês → mais likes | replicada | evitar fim de tarde para posts de conversa |
| **RedNote** | tarde fraca para comentários (0,58x top 1%); texto × lifestyle → 1,6x likes | replicada / exploratória | testar horário |

**Cautela:** fora o destaque do TikTok, a taxa de replicação por plataforma fica perto do acaso (~5%). Os demais itens são hipóteses priorizadas, e o teste A/B decide.
""")

nb.save(sys.argv[1])
