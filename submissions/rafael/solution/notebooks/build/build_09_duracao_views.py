# Builds 09_duracao_views.ipynb: histograms of video length × views (also exports PNGs for the site).
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 09 — Duração do vídeo × views

Somente posts de **vídeo** (`content_type == "video"`); `content_length` = duração em segundos.
Figuras exportadas para `docs/figures/` (uso no site).
""")
nb.code(SETUP + '''
from scipy import stats
from social_insights.data import LENGTH_BINS
FIG_DIR = ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
videos = df[df.content_type == "video"].copy()
videos["faixa de duração"] = videos["length_bin"].astype(str)
print(f"{len(videos):,} vídeos · duração {videos.content_length.min()}–{videos.content_length.max()} s · views {videos.views.min():,}–{videos.views.max():,}")
''')

nb.md("## 1. Histograma 2D: duração × views")
nb.code("""
fig, ax = plt.subplots(figsize=(11, 5.5))
counts, xedges, yedges, image = ax.hist2d(videos.content_length, videos.views, bins=[40, 40], cmap="Blues")
fig.colorbar(image, ax=ax, label="nº de vídeos")
bins = pd.cut(videos.content_length, np.arange(0, 630, 30))
per_bin = videos.groupby(bins, observed=True).agg(x=("content_length", "median"), mediana=("views", "median"),
                                                  máximo=("views", "max"), mínimo=("views", "min"), vídeos=("views", "size"))
ax.plot(per_bin.x, per_bin["máximo"], "^-", color="#6250d6", linewidth=1.5, markersize=5, label="máximo de views (faixa de 30 s)")
ax.plot(per_bin.x, per_bin["mediana"], "o-", color=plots.ORANGE, linewidth=2, markersize=5, label="mediana de views")
ax.plot(per_bin.x, per_bin["mínimo"], "v-", color="#1baf7a", linewidth=1.5, markersize=5, label="mínimo de views")
ax.set_xlabel("duração do vídeo (segundos)"); ax.set_ylabel("views")
ax.set_title("Duração do vídeo × views (31.500 vídeos) — máximo, mediana e mínimo por faixa de 30 s")
ax.set_ylim(per_bin["mínimo"].min() - 40, per_bin["máximo"].max() + 140)
ax.legend(loc="upper center", ncol=3, fontsize=8, framealpha=0.95); ax.grid(False)
fig.tight_layout(); fig.savefig(FIG_DIR / "duracao_x_views_hist2d.png", dpi=150); plt.show()
""")
nb.code("""
# Extremes depend on how many videos fall in each bin: more draws → higher max and lower min.
per_bin["amplitude (máx − mín)"] = per_bin["máximo"] - per_bin["mínimo"]
rho_n, p_n = stats.spearmanr(per_bin["vídeos"], per_bin["amplitude (máx − mín)"])
display(Markdown(f"**Amplitude × nº de vídeos por faixa:** ρ = {rho_n:+.2f} (p = {p_n:.3f})"))
per_bin.drop(columns="x").rename_axis("faixa (s)")
""")

nb.md("## 2. Distribuição de views por faixa de duração")
nb.code("""
order = list(LENGTH_BINS)
colors = [plots.BLUE, plots.ORANGE, "#1baf7a", "#6250d6"]
fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
edges = np.arange(videos.views.min(), videos.views.max() + 10, 10)
for label, color in zip(order, colors):
    v = videos.loc[videos["faixa de duração"] == label, "views"]
    axes[0].hist(v, bins=edges, density=True, histtype="step", linewidth=2, color=color, label=f"{label} · n={len(v):,} · mediana {v.median():,.0f}")
axes[0].set_xlabel("views"); axes[0].set_ylabel("densidade"); axes[0].set_title("Histograma de views por faixa de duração")
axes[0].legend(fontsize=8)
axes[1].hist(videos.content_length, bins=np.arange(0, 630, 15), color=plots.BLUE, edgecolor="white", linewidth=0.5)
for edge in [60, 180, 360]:
    axes[1].axvline(edge, color=plots.GRAY, linestyle="--", linewidth=1)
axes[1].set_xlabel("duração do vídeo (segundos)"); axes[1].set_ylabel("nº de vídeos"); axes[1].set_title("Histograma de duração (tracejado = faixas)")
fig.tight_layout(); fig.savefig(FIG_DIR / "views_por_faixa_de_duracao.png", dpi=150); plt.show()

summary = videos.groupby("faixa de duração")["views"].agg(["size", "min", "mean", "median", "max", "std"]).loc[order]
summary["vs. média geral (%)"] = (summary["mean"] / videos.views.mean() - 1) * 100
summary.round(2)
""")
nb.code("""
rho, p = stats.spearmanr(videos.content_length, videos.views)
h, p_kw = stats.kruskal(*[g.values for _, g in videos.groupby("faixa de duração")["views"]])
display(Markdown(f"**Spearman duração × views:** ρ = {rho:+.4f} (p = {p:.2f}) · **Kruskal entre faixas:** p = {p_kw:.2f}"))
""")
nb.code("""
short, long_ = videos[videos.content_length < 200].views, videos[videos.content_length >= 200].views
display(Markdown(f"**< 200 s:** {len(short):,} vídeos ({len(short) / len(videos):.0%}), média {short.mean():,.1f} views · "
                 f"**≥ 200 s:** {len(long_):,} vídeos, média {long_.mean():,.1f} views · "
                 f"p = {stats.ttest_ind(short, long_, equal_var=False).pvalue:.2f}"))
""")
nb.md("""
**Leitura:**
- **Duração:** não é uniforme. 58% dos vídeos têm entre ~20 e 200 s (≈ 2,9x mais vídeos por segundo de duração que acima de 200 s), e de 200 a 600 s a distribuição é plana. A mesma forma aparece em imagem, texto e misto, o que confirma que `content_length` não é uma duração real por formato.
- **Histograma 2D:** a mancha mais escura à esquerda é **quantidade de vídeos, não mais views**. Na vertical, a faixa é a mesma em toda duração (~10.000–10.200), e a mediana (laranja) é uma linha reta.
- **Máximos e mínimos:** oscilam de faixa em faixa sem tendência com a duração. As faixas abaixo de 200 s têm extremos um pouco mais abertos só porque têm ~3x mais vídeos (mais sorteios → extremos mais distantes; ver ρ amplitude × nº de vídeos). O pico e o vale de views são **acaso**, não efeito da duração.
- **Histogramas por faixa:** as 4 curvas se sobrepõem, com medianas de 10.099 a 10.102. Spearman ρ = 0,001 e Kruskal p = 0,83; abaixo × acima de 200 s, p = 0,79.
- **Conclusão: a duração do vídeo não muda as views.** Vídeo curto ou longo deve ser escolhido por custo de produção e formato da plataforma, não por alcance esperado.
""")

nb.md("""
## 3. Picos: mais vídeos ou mais chance de pico?
O histograma 2D sugere **mais picos entre 20 e 150 s**. Isso pode ter duas causas:
- **mais vídeos** naquela faixa (≈ 3x mais), e então mais "sorteios" geram mais picos;
- **mais chance de pico por vídeo**, que seria um efeito real da duração.

Para separar as duas, olhamos a **taxa** de picos (não a contagem) e comparamos o máximo observado com o **máximo esperado só pelo nº de vídeos**.
""")
nb.code("""
P95 = videos.views.quantile(0.95)
rng = np.random.default_rng(42)
per_bin["picos (top 5%)"] = videos.groupby(bins, observed=True)["views"].apply(lambda s: int((s >= P95).sum()))
per_bin["taxa de picos (%)"] = per_bin["picos (top 5%)"] / per_bin["vídeos"] * 100
p_hat = per_bin["taxa de picos (%)"] / 100
per_bin["IC95 taxa"] = 1.96 * np.sqrt(p_hat * (1 - p_hat) / per_bin["vídeos"]) * 100
all_views = videos.views.values
sims = np.array([[rng.choice(all_views, n).max() for _ in range(500)] for n in per_bin["vídeos"]])
per_bin["máx. esperado (sorteio)"] = sims.mean(axis=1)
per_bin["máx. esperado p5"], per_bin["máx. esperado p95"] = np.percentile(sims, 5, axis=1), np.percentile(sims, 95, axis=1)

x = per_bin["x"].values
fig, axes = plt.subplots(1, 3, figsize=(19, 4.6))
axes[0].bar(x, per_bin["picos (top 5%)"], width=24, color=plots.BLUE)
axes[0].set_title("1. Nº de vídeos no top 5% (o que o histograma sugere)")
axes[1].errorbar(x, per_bin["taxa de picos (%)"], yerr=per_bin["IC95 taxa"], fmt="o", color=plots.BLUE, capsize=3)
axes[1].axhline(5, color=plots.GRAY, linestyle="--", label="5% (esperado se a duração não importa)")
axes[1].set_ylim(0, 10); axes[1].legend(fontsize=8); axes[1].set_title("2. Chance de pico por vídeo (% no top 5%)")
axes[2].fill_between(x, per_bin["máx. esperado p5"], per_bin["máx. esperado p95"], color=plots.GRAY, alpha=0.25, linewidth=0,
                     label="máximo esperado só pelo nº de vídeos (90%)")
axes[2].plot(x, per_bin["máx. esperado (sorteio)"], color=plots.GRAY, linewidth=1.5)
axes[2].plot(x, per_bin["máximo"], "^-", color="#6250d6", linewidth=1.5, label="máximo observado")
axes[2].legend(fontsize=8, loc="lower right"); axes[2].set_title("3. Máximo observado × esperado pelo tamanho da faixa")
for ax in axes: ax.set_xlabel("duração do vídeo (s)")
fig.tight_layout(); fig.savefig(FIG_DIR / "picos_por_duracao.png", dpi=150); plt.show()
""")
nb.code("""
zone = videos.content_length.between(20, 150)
rows = []
for name, q in [("top 5%", 0.95), ("top 1%", 0.99)]:
    hit = videos.views >= videos.views.quantile(q)
    table = pd.crosstab(zone, hit)
    rows.append({"pico": name, "vídeos 20–150 s": int(zone.sum()), "picos 20–150 s": int(table.loc[True, True]),
                 "taxa 20–150 s (%)": table.loc[True, True] / zone.sum() * 100,
                 "picos demais": int(table.loc[False, True]), "taxa demais (%)": table.loc[False, True] / (~zone).sum() * 100,
                 "p (qui²)": stats.chi2_contingency(table)[1]})
display(pd.DataFrame(rows).round(3))

# Equal-size comparison: mean max of 950-video subsamples, tested by permuting the zone label.
M, R, PERMS = 950, 100, 200
def max_gap(labels):
    a, b = all_views[labels], all_views[~labels]
    return (np.mean([rng.choice(a, M, replace=False).max() for _ in range(R)])
            - np.mean([rng.choice(b, M, replace=False).max() for _ in range(R)]))
observed = max_gap(zone.values)
null = np.array([max_gap(rng.permutation(zone.values)) for _ in range(PERMS)])
display(Markdown(f"**Máximo médio com amostras de mesmo tamanho ({M} vídeos):** 20–150 s fica {observed:+.1f} views acima das demais faixas · "
                 f"permutação p = {(np.sum(np.abs(null) >= abs(observed)) + 1) / (PERMS + 1):.2f}"))
""")
nb.md("""
**Leitura:**
- **Gráfico 1:** sim, há mais vídeos no top 5% entre 30 e 180 s (134–166 por faixa, contra 34–60 acima de 200 s). É exatamente o que o histograma mostra.
- **Gráfico 2:** quando se divide pelo nº de vídeos da faixa, a **chance de pico é a mesma** em toda duração (~5%; qui² entre as 20 faixas p ≈ 0,27; tendência com a duração p ≈ 0,79). Entre 20 e 150 s, 4,9% dos vídeos chegam ao top 5%, contra 5,1% nas demais faixas (p = 0,50). No top 1%, 0,98% contra 1,04% (p = 0,66).
- **Ressalva honesta:** as faixas acima de 480 s ficam um pouco abaixo de 5% (4,1% vs. 5,2%; p = 0,007 isolado). Mas essa janela foi escolhida **depois de olhar o gráfico**: com 20 faixas, alguma sempre parece diferente, e os testes definidos antes (tendência e qui² global) não acusam nada. A média de views dessas faixas também é igual. Fica como **hipótese a confirmar com dados novos**, não como conclusão.
- **Gráfico 3:** o máximo de cada faixa cai dentro do que se espera **só pelo nº de vídeos** sorteados da distribuição geral. Faixas com ~3.000 vídeos esperam máximo de ~10.450, e faixas com ~950 vídeos, ~10.420.
- **Mesmo tamanho de amostra:** a diferença de máximo (~+14 views) não é significativa (permutação p ≈ 0,2).

**Conclusão:** a impressão de "mais picos entre 20 e 150 s" é real na **contagem**, mas vem de haver **mais vídeos** ali, não de vídeos curtos terem mais chance de bombar. Para decidir a duração, o que importa é a **taxa** de picos por vídeo, e ela é igual.
""")

nb.save(sys.argv[1])
