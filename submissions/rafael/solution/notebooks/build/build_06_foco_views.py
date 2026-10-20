# Builds 06_foco_views.ipynb: deep dive on content_category, content_description, follower_count and is_sponsored vs. views.
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 06 — Foco: 4 relações com views

| # | Relação | Pergunta de negócio |
|---|---|---|
| 1 | `content_category` × views | Algum tema alcança mais gente? |
| 2 | `content_description` × views | O texto da legenda (tamanho, tom, palavras) muda o alcance? |
| 3 | `follower_count` × views | Creators maiores entregam mais views? |
| 4 | `is_sponsored` × views | Post patrocinado alcança mais? |

Para cada relação: descrição → teste → **tamanho do efeito com IC95** → **efeito mínimo detectável (MDE)** → gráfico.
O MDE responde: *se existisse um efeito relevante, estes dados o teriam encontrado?* (poder de 80%, α = 5%).
""")
nb.code(SETUP + '''
from social_insights import focus
MEAN_VIEWS = df.views.mean()
''')

nb.md("## 1. `content_category` × views")
nb.code("""
cat = focus.category_vs_views(df)
display(Markdown(f"**Resposta:** {cat.verdict}"))
display(cat.evidence.round(1))
display(cat.details["Comparações par a par"].round(4))
""")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(18, 4.2), gridspec_kw={"width_ratios": [1.2, 1, 1.2]})
cats = cat.evidence.index.tolist()
axes[0].boxplot([df.loc[df.content_category == c, "views"] for c in cats], tick_labels=cats, widths=0.5, showfliers=False,
                medianprops={"color": plots.ORANGE, "linewidth": 2}, boxprops={"color": plots.BLUE})
axes[0].set_title("Distribuição de views por categoria")
ev = cat.evidence
axes[1].errorbar(ev["média"], range(len(ev)), xerr=[ev["média"] - ev["IC95 inf"], ev["IC95 sup"] - ev["média"]],
                 fmt="o", color=plots.BLUE, capsize=4, markersize=7)
axes[1].axvspan(MEAN_VIEWS * 0.95, MEAN_VIEWS * 1.05, color=plots.ORANGE, alpha=0.08, label="±5% (efeito de negócio)")
axes[1].axvline(MEAN_VIEWS, color=plots.GRAY, linestyle="--")
axes[1].set_yticks(range(len(ev)), ev.index); axes[1].set_title("Média ± IC95 (faixa = ±5%)")
axes[1].legend(fontsize=8, loc="lower right")
plots.heatmap(axes[2], cat.details["Dentro de cada plataforma (% vs. média da plataforma)"], "Dentro da plataforma (% vs. média)",
              vmin=-1, vmax=1, fmt="{:+.3f}")
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** as 3 categorias têm a mesma distribuição. As médias diferem em ≤ 1,6 views (0,015%), com ICs sobrepostos. No painel do meio, a faixa laranja de ±5% engole tudo.
O MDE é de ~3 views: o teste enxergaria até 0,03% de diferença, então a ausência de efeito é **comprovada**, não falta de poder. O padrão se repete dentro de cada plataforma (±0,03%).
""")

nb.md("## 2. `content_description` × views (NLP)")
nb.code("""
desc = focus.description_vs_views(df)
display(Markdown(f"**Resposta:** {desc.verdict}"))
display(desc.evidence.round(4))
display(desc.details["Modelo de texto (TF-IDF + Ridge)"].round(4))
display(df[["content_description", "content_category", "views"]].sample(5, random_state=1))
""")
nb.code("""
feats = focus.description_features(df)
kw = desc.details["Palavras mais típicas: top 10% vs. bottom 10% de views"]
fig, axes = plt.subplots(1, 3, figsize=(18, 4.5))
axes[0].hexbin(feats["palavras"], df["views"], gridsize=35, cmap="Blues", bins="log")
q = desc.details["Views por quintil de tamanho da legenda (palavras)"]
mids = [float(i.split(",")[0][1:]) / 2 + float(i.split(",")[1][:-1]) / 2 for i in q.index]
axes[0].plot(mids, q["median"], "o-", color=plots.ORANGE, linewidth=2, label="mediana por quintil")
axes[0].set_xlabel("palavras na legenda"); axes[0].set_ylabel("views"); axes[0].set_title("Tamanho da legenda × views"); axes[0].legend(fontsize=8)
sent_bins = pd.cut(feats["sentimento"], [-1.01, -0.05, 0.05, 1.01], labels=["negativo", "neutro", "positivo"])
g = df.groupby(sent_bins, observed=True)["views"].agg(["mean", "sem", "size"])
axes[1].errorbar(range(len(g)), g["mean"], yerr=1.96 * g["sem"], fmt="o", color=plots.BLUE, capsize=4, markersize=7)
axes[1].set_xticks(range(len(g)), [f"{i}\\n(n={n:,})" for i, n in zip(g.index, g["size"])])
axes[1].axhline(MEAN_VIEWS, color=plots.GRAY, linestyle="--"); axes[1].set_title("Tom da legenda (VADER) × views — média ± IC95")
kw_plot = kw.iloc[::-1]
axes[2].barh(kw_plot["word"], kw_plot["z"], color=[plots.BLUE if z > 0 else plots.ORANGE for z in kw_plot["z"]], height=0.6)
for v in (-1.96, 1.96):
    axes[2].axvline(v, color=plots.INK, linestyle="--", linewidth=1)
axes[2].set_title("Palavras: top vs. bottom 10% de views (z; tracejado = significância)"); axes[2].tick_params(axis="y", labelsize=7)
axes[2].grid(axis="y", visible=False)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** tamanho e tom da legenda não mudam as views (|ρ| ≤ 0,002 contra um MDE de 0,012), e nenhuma palavra cruza a linha de significância.
O modelo de texto (5 mil termos, uni e bigramas) tem R² ≈ 0. As legendas são frases aleatórias (ex.: *"Professional radio usually something letter half pattern…"*) sem relação com a categoria do post. Por isso **não há semântica a extrair**.
Não há "?" nem "!" em nenhuma legenda, então essas características não puderam ser testadas.
""")

nb.md("## 3. `follower_count` × views")
nb.code("""
fol = focus.followers_vs_views(df)
display(Markdown(f"**Resposta:** {fol.verdict}"))
display(fol.evidence.round(5))
display(fol.details["Views por decil de seguidores"].round(1))
""")
nb.code("""
REAL_ELASTICITY = 0.7  # typical order of magnitude in real platforms (illustrative contrast)
fig, axes = plt.subplots(1, 2, figsize=(16, 4.8))
axes[0].hexbin(df["follower_count"], df["views"], gridsize=45, cmap="Blues", bins="log")
dec = df.groupby(pd.qcut(df.follower_count, 10), observed=True).agg(x=("follower_count", "median"), y=("views", "median"))
axes[0].plot(dec["x"], dec["y"], "o-", color=plots.ORANGE, linewidth=2, label="mediana por decil")
axes[0].set_xlabel("seguidores"); axes[0].set_ylabel("views"); axes[0].set_title("Seguidores × views (dados)"); axes[0].legend(fontsize=8)
x = np.linspace(df.follower_count.min(), df.follower_count.max(), 200)
anchor_x, anchor_y = df.follower_count.median(), df.views.median()
axes[1].plot(x, np.full_like(x, anchor_y), color=plots.BLUE, linewidth=2, label="observado (elasticidade ≈ 0)")
axes[1].plot(x, anchor_y * (x / anchor_x) ** REAL_ELASTICITY, color=plots.ORANGE, linewidth=2, linestyle="--",
             label=f"esperado numa rede real (elasticidade ≈ {REAL_ELASTICITY}, ancorado na mediana)")
axes[1].set_yscale("log"); axes[1].set_xscale("log"); axes[1].set_xlabel("seguidores (log)"); axes[1].set_ylabel("views (log)")
axes[1].set_title("Contraste: dados vs. comportamento típico"); axes[1].legend(fontsize=8)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** a nuvem é uma faixa horizontal: creators de 1 mil e de 1 milhão têm a mesma mediana (~10.100 views). A elasticidade é 0,0001.
Numa rede real (laranja), 100x mais seguidores renderiam ~25x mais views. Aqui, renderiam **0x**.
**Implicação prática:** "views por seguidor" vai de 10 (nano) a 0,01 (mega). Pagar por seguidores é pagar por algo que não vira alcance.
""")

nb.md("## 4. `is_sponsored` × views")
nb.code("""
spo = focus.sponsorship_vs_views(df)
display(Markdown(f"**Resposta:** {spo.verdict}"))
display(spo.evidence.round(3))
""")
nb.code("""
conds = spo.details["Por condição"].sort_values("diferença (views)")
mde = spo.evidence.loc["bruta", "MDE (views)"]
fig, axes = plt.subplots(1, 2, figsize=(17, 6), gridspec_kw={"width_ratios": [1, 1.3]})
bins = np.arange(df.views.min(), df.views.max(), 10)
for flag, color, label in [(False, plots.GRAY, "orgânico"), (True, plots.BLUE, "patrocinado")]:
    axes[0].hist(df.loc[df.is_sponsored == flag, "views"], bins=bins, density=True, histtype="step", linewidth=2, color=color, label=label)
axes[0].set_title("Distribuição de views: patrocinado × orgânico"); axes[0].legend(); axes[0].set_xlabel("views")
y = np.arange(len(conds))
axes[1].errorbar(conds["diferença (views)"], y, xerr=[conds["diferença (views)"] - conds["IC95 inf"], conds["IC95 sup"] - conds["diferença (views)"]],
                 fmt="o", color=plots.BLUE, capsize=3, markersize=5)
axes[1].axvline(0, color=plots.INK, linewidth=1)
axes[1].axvspan(-MEAN_VIEWS * 0.05, MEAN_VIEWS * 0.05, color=plots.ORANGE, alpha=0.06)
axes[1].set_xlim(-30, 30)
axes[1].set_yticks(y, conds["condição"], fontsize=7)
axes[1].set_title("Patrocinado − orgânico (views) ± IC95 por condição · ±5% = ±505 views (fora da escala)")
axes[1].grid(axis="y", visible=False)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** as duas distribuições se sobrepõem. A diferença é de +0,3 views (IC95 −1,4 a +2,0), e a estratificada (mesma plataforma, formato, categoria e porte) é de +0,4.
Nenhuma das 21 condições se afasta de zero após a correção. O maior ponto (TikTok, +3,8 views, q = 0,95) é ruído, e um efeito de 5% (±505 views) ficaria **fora do gráfico**.

## 5. Síntese: o que os dados permitem afirmar
""")
nb.code("""
summary = pd.DataFrame([
    {"relação": "content_category × views", "efeito observado": f"{cat.evidence['média'].max() - cat.evidence['média'].min():.1f} views (máx. entre categorias)",
     "detectável a partir de": f"{cat.details['Comparações par a par']['MDE (views)'].max():.1f} views", "conclusão": "sem efeito (comprovado)"},
    {"relação": "content_description × views", "efeito observado": f"|ρ| ≤ {desc.evidence['ρ Spearman'].abs().max():.3f}; R² texto = {desc.details['Modelo de texto (TF-IDF + Ridge)']['R² médio'].iloc[0]:.4f}",
     "detectável a partir de": f"ρ = {focus.mde_correlation(len(df)):.3f}", "conclusão": "sem efeito; texto sem semântica"},
    {"relação": "follower_count × views", "efeito observado": f"ρ = {fol.evidence.loc['ρ Spearman', 'valor']:.4f}; elasticidade {fol.evidence.loc['elasticidade (log-log)', 'valor']:.4f}",
     "detectável a partir de": f"ρ = {focus.mde_correlation(len(df)):.3f}", "conclusão": "sem efeito (atípico vs. redes reais)"},
    {"relação": "is_sponsored × views", "efeito observado": f"{spo.evidence.loc['bruta', 'diferença (views)']:+.1f} views",
     "detectável a partir de": f"{spo.evidence.loc['bruta', 'MDE (views)']:.1f} views", "conclusão": "sem efeito (comprovado)"},
]).set_index("relação")
summary
""")
nb.md("""
**Conclusão:** nas 4 relações, o teste tinha poder para enxergar efeitos **~150 a 200 vezes menores** que um efeito de negócio relevante (5% = ~505 views; o efeito mínimo detectável é de 2,5–3,4 views) e não encontrou nada.
A impressão de que "os dados não trazem insight" está correta e agora está **quantificada**. O insight de negócio é justamente este:
**tema, legenda, tamanho do creator e patrocínio não compram alcance neste dataset**, então a decisão deve ser por custo (ver `strategy-recommendations.md`).

> Por que o MDE é tão pequeno? Porque as views quase não variam (desvio de 100 em 10.100, 1%). Em dados reais, a variação costuma ser de 100% ou mais, e o MDE seria proporcionalmente maior. O método já calcula isso automaticamente.
""")

nb.save(sys.argv[1])
