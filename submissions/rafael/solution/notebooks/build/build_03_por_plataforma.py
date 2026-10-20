# Builds 03_por_plataforma.ipynb (same methods as 02, run inside each platform + cross-platform comparison).
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 03 — Insights por plataforma

Os métodos do notebook 02 rodam **dentro de cada plataforma** (Instagram, TikTok, YouTube, Bilibili, RedNote).
O "top 10%" é recalculado por plataforma, porque um post top no TikTok é comparado com outros posts do TikTok.

1. Painel-resumo por plataforma
2. Formato × categoria × audiência: o que muda entre plataformas?
3. Raio-X de cada plataforma (atributos, combinações, modelo, clusters, audiência, comentários)
4. Validação: um efeito plantado **só no TikTok** aparece só no TikTok?
""")
nb.code(SETUP)
nb.code("""
CONTENT_NO_PLATFORM = [f for f in data.FEATURES if f != "platform"]
df["sentiment"] = nlp.sentiment(df["comments_text"])
BY_PLATFORM = {p: df[df.platform == p].reset_index(drop=True) for p in data.PLATFORMS}
""")

nb.md("## 1. Painel-resumo por plataforma")
nb.code("""
def platform_summary(name: str, sub: pd.DataFrame) -> dict:
    row = {"plataforma": name, "posts": len(sub), "% patrocinado": sub.is_sponsored.mean() * 100}
    row |= {f"média {m}": sub[m].mean() for m in data.METRICS}
    for m in data.METRICS:
        top = tp.flag_top(sub, m)
        lifts = tp.lift_table(sub, top, CONTENT_NO_PLATFORM)
        row[f"achados FDR ({m})"] = int(lifts.significant.sum())
        row[f"AUC ({m})"] = dr.cv_top_classifier(sub, top, CONTENT_NO_PLATFORM)
    row["ganho silhueta (k=4)"] = cl.structure_test(cl.attribute_space(sub, CONTENT_NO_PLATFORM), range(4, 5))["gain"].iloc[0]
    row["p sentimento (top views vs. demais)"] = nlp.compare_sentiment(sub["sentiment"], tp.flag_top(sub, "views"))["p_value"]
    return row

summary = pd.DataFrame([platform_summary(p, s) for p, s in BY_PLATFORM.items()]).set_index("plataforma")
summary.T
""")
nb.md("""
**Leitura:** as 5 plataformas têm as mesmas médias (~10.100 views, ~1.510 likes, ~300 shares, ~200 comentários). Em nenhuma delas um atributo sobrevive ao FDR, a AUC fica ≈ 0,50 e os clusters não superam o nulo.
""")

nb.md("## 2. O que muda entre plataformas?")
nb.code("""
fig, axes = plt.subplots(2, 2, figsize=(15, 8))
for ax, m in zip(axes.flat, data.METRICS):
    idx = df.pivot_table(m, "platform", "content_type").div(df.groupby("platform")[m].mean(), axis=0) * 100
    plots.heatmap(ax, idx.loc[data.PLATFORMS], f"Índice de {m}: formato dentro da plataforma (100 = média)", vmin=99, vmax=101, fmt="{:.2f}")
fig.tight_layout(); plt.show()

pvals = pd.DataFrame({m: au.interaction_pvalues(df, "platform", "content_type", m) for m in data.METRICS}).loc[data.PLATFORMS]
display(Markdown("**p-value (Kruskal): o formato muda a métrica dentro da plataforma?**"))
pvals
""")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(17, 4))
for ax, aud in zip(axes, data.AUDIENCE):
    plots.heatmap(ax, au.audience_mix(df, "platform", aud).loc[data.PLATFORMS] * 100,
                  f"Audiência por plataforma — {aud.replace('_distribution', '')} (%)", cmap="Blues", vmin=0, fmt="{:.0f}")
fig.tight_layout(); plt.show()
""")
nb.code("""
# Audience × content type inside each platform: any cell clearly over/under-represented?
rows = []
for p, sub in BY_PLATFORM.items():
    for by in ["content_type", "content_category", "is_sponsored"]:
        for aud in data.AUDIENCE:
            _, v, pval = au.adjusted_residuals(sub, by, aud)
            rows.append({"plataforma": p, "conteúdo": by, "audiência": aud, "cramers_v": v, "p_value": pval})
aud_tests = pd.DataFrame(rows)
aud_tests["significativo (Bonferroni)"] = aud_tests.p_value < 0.05 / len(aud_tests)
display(aud_tests.sort_values("cramers_v", ascending=False).head(10))
print("Associações significativas:", int(aud_tests["significativo (Bonferroni)"].sum()), "de", len(aud_tests))
""")

nb.md("## 3. Raio-X por plataforma")
nb.code("""
ALL_RULES = []

def platform_xray(name: str, sub: pd.DataFrame) -> None:
    display(Markdown(f"### {name}  ·  {len(sub):,} posts"))
    fig, axes = plt.subplots(1, 4, figsize=(22, 5))
    rules = {}
    for ax, m in zip(axes, data.METRICS):
        top = tp.flag_top(sub, m)
        plots.lift_bars(ax, tp.lift_table(sub, top, CONTENT_NO_PLATFORM), f"{name} — top 10% {m}", n=10)
        pairs = tp.pair_lift_table(sub, top, CONTENT_NO_PLATFORM)
        ALL_RULES.append(pairs.assign(plataforma=name, métrica=m))
        rules[m] = {"regras": len(pairs), "p<0,05": int((pairs.p_value < 0.05).sum()),
                    "esperado por acaso": tp.expected_false_positives(pairs), "FDR": int(pairs.significant.sum()),
                    "melhor regra (aparente)": pairs.iloc[0]["feature"] + " = " + pairs.iloc[0]["value"], "lift": pairs.iloc[0]["lift"], "q": pairs.iloc[0]["q_value"]}
    fig.tight_layout(); plt.show()
    display(pd.DataFrame(rules).T)

for name, sub in BY_PLATFORM.items():
    platform_xray(name, sub)
""")
nb.md("""
**Leitura:** em cada plataforma, a "melhor regra aparente" tem lift de 1,5–1,8x, e o número de p < 0,05 bate com o esperado por acaso.
Um relatório sem correção daria 5 estratégias diferentes (uma por plataforma), todas baseadas em ruído.
""")
nb.md("""
### 3.1 Os poucos "achados" sobrevivem a uma correção global?
O FDR acima foi aplicado em cada tabela (plataforma × métrica). São 20 tabelas, e com 20 famílias 1–2 falsos achados são esperados.
A pergunta certa é: corrigindo **todos os ~23 mil testes juntos**, sobra algo?
""")
nb.code("""
from statsmodels.stats.multitest import multipletests

rules = pd.concat(ALL_RULES, ignore_index=True)
rules["q_global"] = multipletests(rules["p_value"], method="fdr_bh")[1]
display(Markdown(f"Testes: **{len(rules):,}** · significativos por tabela: **{int(rules.significant.sum())}** · "
                 f"significativos na correção global: **{int((rules.q_global < tp.ALPHA).sum())}**"))
rules[rules.significant][["plataforma", "métrica", "feature", "value", "n", "lift", "p_value", "q_value", "q_global"]]
""")
nb.md("""
**Leitura:** 3 regras passaram por tabela: espanhol + beleza e espanhol + vídeo → likes no TikTok (são quase os mesmos posts), e 4 hashtags + sexta → shares no Bilibili.
"Vídeo em espanhol no TikTok" até parece plausível, e é aí que mora o perigo. **Nenhuma passa pela correção global** (q ≥ 0,12), e nenhuma se repete em outra métrica ou plataforma. Isso é típico de falso positivo.
**Regra para o time:** um achado só vira ação se (1) sobreviver à correção global, (2) fizer sentido de negócio e (3) se repetir num teste A/B.
""")

nb.md("## 4. Validação: efeito plantado só no TikTok")
nb.code("""
planted = va.demo_segment(df)  # TikTok × video × tech
injected = va.inject_uplift(df, planted, "views", uplift=0.02)
rows = []
for p in data.PLATFORMS:
    sub = injected[injected.platform == p].reset_index(drop=True)
    top = tp.flag_top(sub, "views")
    lifts = tp.lift_table(sub, top, CONTENT_NO_PLATFORM)
    best = tp.summarize_significant(lifts, 1)
    rows.append({"plataforma": p, "achados FDR": int(lifts.significant.sum()),
                 "principal achado": (best.feature + " = " + best.value).iloc[0] if len(best) else "—",
                 "AUC": dr.cv_top_classifier(sub, top, CONTENT_NO_PLATFORM)})
pd.DataFrame(rows).set_index("plataforma")
""")
nb.md("""
**Leitura:** o efeito plantado aparece **só no TikTok** (categoria tech e formato vídeo, AUC > 0,5). As outras plataformas continuam sem achados.
O método separa bem sinal de ruído por plataforma.

## 5. Conclusões por plataforma
1. **Nenhuma plataforma tem uma "receita" vencedora** nos dados: formato, categoria, creator, horário, patrocínio e audiência não mudam views, likes, shares ou comentários em nenhuma delas.
2. **A audiência é igual entre plataformas** (mesmo mix de gênero, idade e país). Os dados não sustentam a ideia de "TikTok = jovem".
3. **Recomendações específicas por plataforma tiradas destes dados seriam ruído.** O valor está no pipeline, validado para achar efeitos de 2% por plataforma, rodando sobre os dados reais da empresa.
""")

nb.save(sys.argv[1])
