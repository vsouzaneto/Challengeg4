# Builds 10_bolsoes_e_top1.ipynb: exploratory pockets (ranked by evidence) and top-1% similarity.
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 10 — Bolsões de desempenho e o top 1%

**Objetivo:** buscar variações como a de "vídeos acima de 480 s" e tratá-las como **insights exploratórios**, ranqueados pelo nível de evidência.
Depois, olhar os posts **top 1%** e procurar o que eles têm em comum **antes** da postagem.

**Bolsão** = um valor de atributo (ex.: categoria = tech), uma janela de variável numérica (ex.: duração entre 480 e 599) ou uma combinação de dois valores (ex.: TikTok · tech).
**Métrica** = % dos posts do bolsão que chegam ao top 5% de views, likes ou comentários (base: 5%).

| Evidência | Critério | Como usar |
|---|---|---|
| **robusta** | sobrevive à correção para todos os testes (FDR) | decisão |
| **replicada** | p < 0,05 na 1ª metade do período **e** mesma direção com p < 0,05 na 2ª metade | hipótese forte: priorizar teste A/B |
| **exploratória** | p < 0,05 nos dados completos | hipótese: monitorar |

Referência de acaso: ~5% dos bolsões dão p < 0,05, e ~5% das descobertas da 1ª metade replicam por acaso.
""")
nb.code(SETUP + '''
from scipy import stats
from statsmodels.stats.multitest import multipletests
from social_insights import discovery as dv
METRICS = ["views", "likes", "comments_count"]
TABLES = {m: dv.scan_pockets(df, m) for m in METRICS}
summary = pd.DataFrame({m: dv.replication_summary(t) for m, t in TABLES.items()}).T
summary
''')

nb.md("## 1. Mapa de bolsões (vulcão)")
nb.code("""
COLORS = {"robusta (FDR)": "#e34948", "replicada (2 metades)": plots.ORANGE, "exploratória": plots.BLUE, "—": "#d0cfca"}
fig, axes = plt.subplots(1, 3, figsize=(19, 5), sharey=True)
for ax, m in zip(axes, METRICS):
    t = TABLES[m]
    for tier, color in COLORS.items():
        s = t[t["evidência"] == tier]
        ax.scatter(np.log2(s["lift"]), -np.log10(s["p_value"]), s=12 if tier == "—" else 28, color=color, label=f"{tier} ({len(s)})",
                   alpha=0.6 if tier == "—" else 0.9, edgecolors="none")
    ax.axhline(-np.log10(0.05), color=plots.GRAY, linestyle="--", linewidth=1)
    ax.set_xlabel("log2(lift): direita = mais tops"); ax.set_title(f"{m}: {len(t):,} bolsões"); ax.legend(fontsize=7, loc="upper left")
axes[0].set_ylabel("-log10(p)")
fig.tight_layout(); plt.show()
""")

nb.md("## 2. Os padrões se repetem no tempo?")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(19, 5))
for ax, m in zip(axes, METRICS):
    t = TABLES[m].dropna(subset=["lift 1ª metade", "lift 2ª metade"])
    rho, p = stats.spearmanr(t["lift 1ª metade"], t["lift 2ª metade"])
    ax.scatter(t["lift 1ª metade"], t["lift 2ª metade"], s=8, alpha=0.35, color=plots.BLUE, edgecolors="none")
    rep = t[t["replicou"]]
    ax.scatter(rep["lift 1ª metade"], rep["lift 2ª metade"], s=40, color=plots.ORANGE, label=f"replicados ({len(rep)})")
    ax.axhline(1, color=plots.GRAY, linewidth=1); ax.axvline(1, color=plots.GRAY, linewidth=1)
    ax.set_xlabel("lift na 1ª metade do período"); ax.set_ylabel("lift na 2ª metade")
    ax.set_title(f"{m}: ρ entre metades = {rho:+.3f} (p = {p:.2f})"); ax.legend(fontsize=8)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Como ler:** se os bolsões tivessem efeito real, os pontos formariam uma diagonal (quem é bom na 1ª metade continua bom na 2ª).
Uma nuvem redonda (ρ ≈ 0) indica que, **no conjunto**, os padrões não persistem. Os pontos laranja são os que persistiram, e eles são os candidatos mais fortes.
O p do ρ superestima a evidência, porque os bolsões se sobrepõem (os mesmos posts entram em muitos deles). Por isso o ρ = −0,07 de likes **não** indica efeito invertido, só ausência de persistência no conjunto.
""")

nb.md("## 3. Insights exploratórios (ranqueados)")
nb.code("""
for m in METRICS:
    display(Markdown(f"### {m}"))
    display(dv.insight_cards(TABLES[m], n=8).style.hide(axis="index").set_properties(**{"text-align": "left"}))
""")

nb.md("""
## 4. O caso "vídeos acima de 480 s" dentro desta busca
Mesma busca restrita a vídeos (como na análise original): janelas de duração × top 5% de views.
Resultado: **504–599 s** tem lift 0,82 (p = 0,03), ou seja, **evidência exploratória**. Na 2ª metade, p = 0,05; na 1ª, p = 0,24, então não chegou a replicar. Segue como hipótese a monitorar.
""")
nb.code("""
videos = df[df.content_type == "video"]
vt = dv.scan_pockets(videos, "views")
windows = vt[vt["dimensão"] == "content_length (janela)"].sort_values("lift")
windows[["bolsão", "posts", "taxa top 5% (%)", "lift", "lift 1ª metade", "lift 2ª metade", "p_value", "q_value", "evidência"]].round(3)
""")

nb.md("## 5. Top 1%: o que os melhores posts têm em comum antes de postar?")
nb.code("""
TOPS = {m: dv.top_mask(df, m) for m in METRICS}
display(Markdown(f"Top 1%: **{TOPS['views'].sum()}** posts por métrica (views ≥ {df.views.quantile(0.99):,.0f} · "
                 f"likes ≥ {df.likes.quantile(0.99):,.0f} · comentários ≥ {df.comments_count.quantile(0.99):,.0f})"))
fig, axes = plt.subplots(1, 3, figsize=(20, 5.5))
for ax, m in zip(axes, METRICS):
    prof = dv.top_profile(df, m).head(12).iloc[::-1]
    labels = prof["atributo"].str.replace("_distribution", "") + " = " + prof["valor"]
    ax.barh(labels, prof["lift"] - 1, left=1, color=[plots.BLUE if q < 0.05 else plots.GRAY for q in prof["q_value"]], height=0.6)
    ax.axvline(1, color=plots.INK, linewidth=1); ax.tick_params(axis="y", labelsize=8); ax.grid(axis="y", visible=False)
    ax.set_title(f"Top 1% de {m}: atributos mais/menos frequentes (menor p)")
fig.tight_layout(); plt.show()
numeric = pd.concat({m: dv.top_numeric_profile(df, m) for m in METRICS})
numeric["q_value (12 testes)"] = multipletests(numeric["p_value"], method="fdr_bh")[1]
numeric.round(3)
""")
nb.code("""
p99 = df.comments_count.quantile(0.99)
rate = df.groupby("daypart", observed=True)["comments_count"].agg(posts="size", top=lambda s: int((s >= p99).sum()))
rate["% no top 1% de comentários"] = rate["top"] / rate["posts"] * 100
fig, axes = plt.subplots(1, 2, figsize=(14, 3.8))
axes[0].bar(rate.index.astype(str), rate["% no top 1% de comentários"], color=plots.BLUE, width=0.55)
axes[0].axhline(1, color=plots.GRAY, linestyle="--", label="1% (base)"); axes[0].legend(fontsize=8)
axes[0].set_title("Chance de entrar no top 1% de comentários, por período do dia")
hours = df.groupby("hour")["comments_count"].apply(lambda s: (s >= p99).mean() * 100)
axes[1].plot(hours.index, hours.values, "o-", color=plots.BLUE, linewidth=2)
axes[1].axhline(1, color=plots.GRAY, linestyle="--"); axes[1].set_xlabel("hora da postagem"); axes[1].set_title("Por hora")
fig.tight_layout(); plt.show()
rate.round(2)
""")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(18, 3.8))
rows = []
for ax, m in zip(axes, METRICS):
    sim = dv.similarity_test(df, TOPS[m])
    ax.hist(sim["null"], bins=30, color=plots.GRAY, edgecolor="white", linewidth=0.3, label="conjuntos sorteados de mesmo tamanho")
    ax.axvline(sim["similaridade média no top (%)"], color=plots.ORANGE, linewidth=2.5, label="top 1%")
    ax.set_xlabel("% de atributos em comum entre pares de posts"); ax.set_title(f"{m}: o top 1% é mais parecido entre si?"); ax.legend(fontsize=7)
    conc = dv.creator_concentration(df, TOPS[m])
    rows.append({"métrica": m, "similaridade no top (%)": sim["similaridade média no top (%)"], "similaridade em sorteios (%)": sim["similaridade em sorteios (%)"],
                 "p similaridade": sim["p_value"], **{f"{k}": v for k, v in conc.items() if k != "p_value"}, "p creators": conc["p_value"]})
fig.tight_layout(); plt.show()
display(pd.DataFrame(rows).set_index("métrica").round(3))
display(Markdown("**O top 1% de uma métrica coincide com o de outra?**"))
dv.top_overlap(df, ["views", "likes", "comments_count", "shares"]).round(3)
""")
nb.md("""
**Leitura (top 1%):**
- **⭐ Insight mais forte desta busca: horário × comentários.** Os posts do **top 1% de comentários** saem mais cedo (hora mediana **10h** vs. 12h no resto). O efeito sobrevive à correção entre os 12 testes numéricos (q ≈ 0,02) e **se repete nas duas metades do período** (p = 0,013 e 0,047). Pela taxa: **madrugada 1,33%** e **manhã 1,20%** chegam ao top 1% de comentários, contra **tarde 0,96%** e noite 1,01%. É coerente com o bolsão exploratório "hora 0–4 → mais top 5% de comentários". **Hipótese prioritária para teste A/B:** postar conteúdo que busca conversa antes do meio-dia.
- **Perfil (categóricos):** nenhum atributo é significativamente mais frequente no top 1% após a correção. As maiores diferenças são pistas fracas (ex.: no top 1% de views, audiência dos EUA aparece 1,2x mais e posts de agosto, 0,7x). No top 1% de likes, as legendas são ligeiramente mais longas (19 vs. 18 palavras; p = 0,03, q = 0,2), o que é uma pista fraca.
- **Semelhança:** os posts do top 1% compartilham ~29,6% dos atributos entre si, **o mesmo** que conjuntos sorteados. Não existe uma "receita" comum.
- **Creators:** o nº de creators com 2+ posts no top é o esperado por acaso. Não há creators "campeões".
- **Entre métricas:** quase nenhum post é top 1% em duas métricas ao mesmo tempo (o mesmo que o acaso), então "top em views" não é "top em likes".

## 6. Como usar estes insights
1. **Prioridade 1:** horário × comentários (top 1% concentrado de madrugada e de manhã; replicado e com correção).
2. **Os replicados** (laranja) são as próximas apostas para **teste A/B**. Ex.: vídeos longos (180–360 s) com audiência de gênero não identificado (1,48x mais top 5% de views), ou tech às sextas (1,33x).
3. **Os exploratórios** entram em monitoramento: rodar `dv.scan_pockets` a cada mês e ver se o bolsão continua aparecendo.
4. **Cautela:** no conjunto, a taxa de replicação é próxima do acaso (~5%). Por isso cada bolsão é uma **hipótese**, e o teste A/B é o que transforma hipótese em decisão.
""")

nb.save(sys.argv[1])
