# Builds 02_insights_gerais.ipynb (cross-platform drivers, clustering, audience, NLP, method validation).
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 02 — Insights gerais (todas as plataformas)

**Pergunta:** o que leva um post a ter mais **views, likes, shares e comentários**? Para quem cada tipo de post fala?

| # | Frente | Método |
|---|---|---|
| 1 | Definir "post top" | top 10% de cada métrica |
| 2 | Atributos dos tops | lift + qui² + correção FDR (Benjamini-Hochberg) |
| 3 | Combinações vencedoras | regras de associação de 2 atributos (lift) |
| 4 | Previsibilidade | gradient boosting com validação cruzada (R², AUC) + árvore legível |
| 5 | Clusterização | K-Means em 2 espaços (desempenho; atributos) × nulo por permutação |
| 6 | Audiência | resíduos ajustados, V de Cramér, índice de engajamento por segmento |
| 7 | NLP nos comentários | sentimento (VADER), palavras distintivas (log-odds), tópicos (NMF) |
| 8 | Validação do método | efeito plantado (+2% views) precisa ser encontrado |

**Como ler:** *lift* = quanto um atributo aparece mais entre os tops do que na base (1,0 = igual; 1,2 = 20% a mais).
*q-value* = p-value corrigido para os milhares de testes feitos; só q < 0,05 conta como achado.
""")
nb.code(SETUP)

nb.md("## 1. O que é um post top?")
nb.code("""
TOPS = {m: tp.flag_top(df, m) for m in data.METRICS}
thresholds = pd.DataFrame({m: {"média": df[m].mean(), "corte top 10%": df[m].quantile(tp.TOP_QUANTILE),
                               "máximo": df[m].max(), "top / média": df[m].quantile(tp.TOP_QUANTILE) / df[m].mean()}
                           for m in data.METRICS}).T
display(thresholds.round(2))

fig, ax = plt.subplots(figsize=(6, 4.5))
plots.heatmap(ax, tp.top_overlap(df, data.METRICS), "Sobreposição dos tops (Jaccard)", cmap="Blues", vmin=0, vmax=1, fmt="{:.2f}")
plt.show()
""")
nb.md("""
**Leitura:** um post top em views fica só ~1,3% acima da média, e ser top em views não aumenta a chance de ser top em likes.
A sobreposição (~0,05) é exatamente a esperada se as métricas forem sorteadas de forma independente (0,01 / 0,19).
""")

nb.md("## 2. Quais atributos aparecem mais entre os tops?")
nb.code("""
LIFTS = {m: tp.lift_table(df, TOPS[m], data.FEATURES) for m in data.METRICS}

fig, axes = plt.subplots(2, 2, figsize=(15, 11))
for ax, m in zip(axes.flat, data.METRICS):
    plots.lift_bars(ax, LIFTS[m], f"Lift entre os top 10% de {m}")
fig.suptitle("Azul = significativo após FDR · cinza = compatível com acaso", y=1.0)
fig.tight_layout(); plt.show()

pd.DataFrame({m: {"testes": len(t), "p<0,05 (sem correção)": int((t.p_value < 0.05).sum()),
                  "falsos positivos esperados": tp.expected_false_positives(t),
                  "significativos (FDR)": int(t.significant.sum()), "maior lift": t.lift.max()}
              for m, t in LIFTS.items()}).T
""")
nb.md("""
**Leitura:** os lifts vão de ~0,75 a ~1,15. Os extremos aparecem nos grupos pequenos (ex.: creators nano = 1% dos posts), porque amostra pequena gera oscilação grande. O número de p < 0,05 é o esperado por acaso.
**Nenhum atributo sobrevive à correção.** Uma análise sem correção (o que um LLM costuma entregar) reportaria esses falsos positivos como insights.
""")

nb.md("## 3. Combinações de atributos (regras de associação)")
nb.code("""
PAIRS = {m: tp.pair_lift_table(df, TOPS[m], data.FEATURES) for m in data.METRICS}
summary = pd.DataFrame({m: {"regras testadas": len(t), "p<0,05 (sem correção)": int((t.p_value < 0.05).sum()),
                            "falsos positivos esperados": tp.expected_false_positives(t),
                            "significativas (FDR)": int(t.significant.sum())} for m, t in PAIRS.items()}).T
display(summary)
display(Markdown("**Top 8 combinações por lift (views) — note os q-values:**"))
PAIRS["views"].head(8)[["feature", "value", "n", "top_rate", "lift", "p_value", "q_value"]]
""")
nb.md("""
**Leitura:** a "melhor" combinação (ex.: idioma japonês + creator micro) tem lift de ~1,5, ou seja, 50% mais tops. Parece um insight, mas tem q = 1,0.
Com 2.108 regras testadas, ~105 passam de p < 0,05 por puro acaso, e foi exatamente isso que aconteceu. **Este é o erro que separa análise de achismo.**
""")

nb.md("## 4. Dá para prever o desempenho a partir dos atributos?")
nb.code("""
reg = pd.DataFrame([dr.cv_regression(df, m, data.FEATURES) for m in data.METRICS]).set_index("target")
reg["AUC top 10%"] = [dr.cv_top_classifier(df, TOPS[m], data.FEATURES) for m in data.METRICS]
reg
""")
nb.code("""
display(Markdown("**Importância por permutação (views):**"))
display(dr.importance_table(df, "views", data.FEATURES))
print(dr.surrogate_tree(df, TOPS["views"], data.FEATURES))
""")
nb.md("""
**Leitura:** R² ≈ 0 (o modelo não supera "chutar a média") e AUC ≈ 0,50 (cara ou coroa).
A importância por permutação fica ≈ 0. As poucas folhas da árvore com taxa de top diferente são pequenas e não se sustentam na validação cruzada.
Nenhuma combinação de plataforma, formato, categoria, creator, horário ou audiência explica o alcance.
""")

nb.md("## 5. Clusterização")
nb.md("""
Dois espaços:
- **Desempenho** (log de views, likes, shares, comments): existem "tipos" naturais de post?
- **Atributos** (one-hot de conteúdo + audiência → SVD): existem "receitas" de post?

O K-Means **sempre** devolve k grupos, mesmo em ruído. Por isso cada silhueta é comparada com um **nulo**: os mesmos dados com cada coluna embaralhada (mantém as distribuições e destrói as relações).
Ganho ≈ 0 → os clusters são artefato do algoritmo.
""")
nb.code("""
X_perf = cl.performance_space(df, data.METRICS)
X_attr = cl.attribute_space(df, data.FEATURES)
structure = {"desempenho": cl.structure_test(X_perf), "atributos": cl.structure_test(X_attr)}

fig, axes = plt.subplots(1, 2, figsize=(12, 3.5), sharey=True)
for ax, (name, t) in zip(axes, structure.items()):
    ax.plot(t.k, t.silhouette, "o-", color=plots.BLUE, linewidth=2, label="dados reais")
    ax.plot(t.k, t.silhouette_null, "o--", color=plots.GRAY, linewidth=2, label="nulo (permutado)")
    ax.set_title(f"Silhueta — espaço de {name}"); ax.set_xlabel("k"); ax.legend()
fig.tight_layout(); plt.show()
pd.concat(structure, names=["espaço"]).round(3)
""")
nb.code("""
K = 4
perf_labels = cl.fit_kmeans(X_perf, K)
display(Markdown("**Clusters de desempenho → o que há neles?** (médias das métricas e atributos mais sobre-representados)"))
display(cl.profile_clusters(df, perf_labels, data.METRICS))
display(cl.dominant_attributes(df, perf_labels, data.FEATURES).round(3))

attr_labels = cl.fit_kmeans(X_attr, K)
display(Markdown("**Clusters de atributos → desempenham diferente?**"))
display(cl.dominant_attributes(df, attr_labels, data.FEATURES).round(3))
cl.profile_clusters(df, attr_labels, data.METRICS)
""")
nb.md("""
**Leitura:**
- **Clusters de desempenho:** o ganho sobre o nulo é ≈ 0, então o K-Means só fatia uma nuvem única ("um pouco mais de likes", "um pouco mais de shares").
  O Kruskal p = 0 ali é circular (os clusters foram feitos com as próprias métricas), e os atributos dentro deles têm lift ≈ 1,0–1,2.
- **Clusters de atributos:** separam bem receitas de post (patrocinado de moda/comida, creators mega orgânicos...), mas **todos têm as mesmas métricas** (Kruskal p > 0,3).
""")

nb.md("## 6. Audiência: quem consome cada tipo de post?")
nb.code("""
CONTENT_FOR_AUDIENCE = ["platform", "content_type", "content_category", "language", "follower_tier", "is_sponsored"]
assoc = au.association_summary(df, CONTENT_FOR_AUDIENCE, data.AUDIENCE)
assoc["significativo"] = assoc.p_value < 0.05 / len(assoc)
assoc.round(4)
""")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(17, 4))
for ax, (by, aud) in zip(axes, [("content_type", "audience_gender_distribution"),
                                ("content_type", "audience_age_distribution"),
                                ("content_category", "audience_location")]):
    plots.heatmap(ax, au.audience_mix(df, by, aud) * 100, f"{by} × {aud.replace('_distribution', '')} (% da linha)",
                  cmap="Blues", vmin=0, fmt="{:.0f}")
fig.tight_layout(); plt.show()
""")
nb.code("""
# Who engages most? Views/likes per (content type × audience), indexed to the content type's mean (100 = average).
fig, axes = plt.subplots(1, 2, figsize=(14, 3.5))
for ax, m in zip(axes, ["views", "likes"]):
    idx = au.engagement_by_segment(df, "content_type", "audience_gender_distribution", m)
    plots.heatmap(ax, idx, f"Índice de {m} (100 = média do formato)", vmin=99.5, vmax=100.5, fmt="{:.2f}")
fig.tight_layout(); plt.show()
display(Markdown("**p-value (Kruskal): dentro de cada formato, o segmento de audiência muda as views?**"))
pd.DataFrame({aud: au.interaction_pvalues(df, "content_type", aud, "views") for aud in data.AUDIENCE})
""")
nb.code("""
rows = []
for by in CONTENT_FOR_AUDIENCE:
    for aud in data.AUDIENCE:
        rows.append(au.strongest_cells(df, by, aud).assign(content=by, audience=aud).rename(columns={by: "valor", aud: "segmento"}))
cells = pd.concat(rows)
print(f"Células com |resíduo ajustado| > {au.RESIDUAL_THRESHOLD}: {len(cells)}")
cells
""")
nb.md("""
**Leitura:** o mix de audiência é o mesmo em todo formato, categoria e plataforma (V de Cramér < 0,02, ou seja, independência).
Exemplo: vídeo tem 40% de público feminino, e imagem e texto também. Os índices de engajamento por segmento ficam a ±0,3% de 100.
""")

nb.md("## 7. NLP nos comentários")
nb.code("""
df["sentiment"] = nlp.sentiment(df["comments_text"])
df["sentiment_label"] = nlp.sentiment_label(df["sentiment"])

fig, axes = plt.subplots(1, 2, figsize=(13, 3.5))
axes[0].hist(df["sentiment"].dropna(), bins=40, color=plots.BLUE, edgecolor="white", linewidth=0.3)
axes[0].set_title("Sentimento dos comentários (VADER compound)")
mix = pd.crosstab(TOPS["views"].map({True: "top 10% views", False: "demais"}), df["sentiment_label"], normalize="index") * 100
mix.plot.barh(stacked=True, ax=axes[1], color=[plots.ORANGE, plots.GRAY, plots.BLUE], width=0.5, edgecolor="white")
axes[1].set_title("Mix de sentimento (%)"); axes[1].legend(loc="lower right", fontsize=8); axes[1].grid(axis="y", visible=False)
fig.tight_layout(); plt.show()

pd.DataFrame({m: nlp.compare_sentiment(df["sentiment"], TOPS[m]) for m in data.METRICS}).T
""")
nb.code("""
bottom_views = df["views"] <= df["views"].quantile(1 - tp.TOP_QUANTILE)
kw = nlp.log_odds_keywords(df.loc[TOPS["views"], "comments_text"], df.loc[bottom_views, "comments_text"], top_n=10)
display(Markdown("**Palavras mais típicas dos comentários: top 10% vs. bottom 10% de views** (|z| > 1,96 = significativo)"))
kw
""")
nb.code("""
display(Markdown("**Sugestão:** aplicar o mesmo método à *legenda* e às *hashtags*, que o time controla (os comentários são consequência, não causa)."))
display(nlp.log_odds_keywords(df.loc[TOPS["views"], "content_description"], df.loc[bottom_views, "content_description"], top_n=5))
display(nlp.log_odds_keywords(df.loc[TOPS["views"], "hashtags"].fillna("").str.replace(",", " "),
                              df.loc[bottom_views, "hashtags"].fillna("").str.replace(",", " "), top_n=5, min_count=10))
display(Markdown("**Tópicos dos comentários (NMF):**"))
nlp.topics(df["comments_text"])
""")
nb.md("""
**Leitura:** o sentimento é igual em tops e demais (p > 0,05), e nenhuma palavra passa de |z| = 1,96.
Os tópicos são misturas aleatórias de palavras ("car, spring, baby"), o que confirma que os textos são gerados (Faker), sem semântica de marketing.
""")

nb.md("""
## 8. Validação do método (controle positivo)
Se os dados tivessem sinal, o pipeline acharia? Plantamos um efeito pequeno e realista: **+2% de views em vídeos de tech no TikTok** (≈ 2% dos posts).
""")
nb.code("""
planted = va.demo_segment(df)
injected = va.inject_uplift(df, planted, "views", uplift=0.02)
top_inj = tp.flag_top(injected, "views")

display(Markdown(f"Posts afetados: **{planted.sum():,}** ({planted.mean():.1%})"))
display(tp.summarize_significant(tp.pair_lift_table(injected, top_inj, data.FEATURES), 6)[["feature", "value", "n", "lift", "q_value"]])
display(pd.DataFrame([dr.cv_regression(df, "views", data.FEATURES) | {"dados": "originais"},
                      dr.cv_regression(injected, "views", data.FEATURES) | {"dados": "com efeito +2%"}]).set_index("dados"))
fig, ax = plt.subplots(figsize=(7, 4))
plots.lift_bars(ax, tp.lift_table(injected, top_inj, data.FEATURES), "Lift top 10% views — com efeito plantado")
plt.show()
""")
nb.md("""
**Leitura:** com só +2% de efeito, o pipeline encontra exatamente TikTok × tech × vídeo (q ≈ 0), e o R² sobe de 0 para ~0,08.
**Logo, a ausência de achados nos dados originais é real e não falta de sensibilidade do método.**

## 9. Conclusões (gerais)
1. **Nenhum atributo do post, do creator ou da audiência explica views, likes, shares ou comentários** (testado com lift + FDR, regras de associação, gradient boosting e árvore).
2. **Não há segmentos naturais:** os clusters não superam o nulo por permutação.
3. **A audiência é idêntica entre formatos, categorias e plataformas.** Não existe "público do vídeo" diferente do "público da imagem".
4. **Comentários não diferenciam posts de alto e baixo alcance** (sentimento, palavras e tópicos).
5. **O método é sensível** (detecta um efeito de 2%) e está pronto para rodar com dados reais da empresa.
6. Patrocínio não muda o desempenho → no dataset, **pagar não compra alcance nem engajamento** (ver notebook 03 por plataforma).
""")

nb.save(sys.argv[1])
