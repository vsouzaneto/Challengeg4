# Builds 05_modelo_engajamento.ipynb: supervised approaches for "post features → estimated engagement".
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 05 — Modelo preditivo de engajamento

**Entrada:** características conhecidas **antes** de publicar (plataforma, formato, categoria, idioma, dia/hora, seguidores, duração, hashtags, legenda, patrocínio, audiência).
**Saída:** engajamento estimado = (likes + shares + comentários) / views, com intervalo de 90%.

**Protocolo (igual para todos):**
- mesmos 5 folds de validação cruzada;
- comparação contra um **baseline** que chuta a média;
- teste pareado entre folds: o modelo só é adotado se for **significativamente melhor** que o baseline;
- R² de treino ao lado do de validação, para expor overfitting.

| Família | Modelos |
|---|---|
| Baselines | média geral, média por plataforma |
| Lineares | Ridge, Lasso, ElasticNet |
| Vizinhos | KNN (k=50) |
| Rede neural | MLP (64-32) |
| Árvores | árvore de decisão, Random Forest, Extra Trees |
| Boosting | HistGradientBoosting, XGBoost, LightGBM, CatBoost |
""")
nb.code(SETUP + '''
from social_insights import engagement_model as em
from social_insights.questions import ENGAGEMENT
''')

nb.md("## 1. Comparação das 14 abordagens (regressão)")
nb.code("""
summary, fold_mse = em.compare_models(df)
summary.style.format({"R² validação": "{:.4f}", "R² treino": "{:.4f}", "MAE": "{:.5f}", "RMSE": "{:.5f}",
                      "ganho MAE vs. baseline (%)": "{:+.3f}", "p (melhor que baseline)": "{:.3f}"})
""")
nb.code("""
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
order = summary.sort_values("R² validação").index
y = np.arange(len(order))
axes[0].scatter(summary.loc[order, "R² treino"], y, color=plots.GRAY, s=40, label="treino", zorder=3)
axes[0].scatter(summary.loc[order, "R² validação"], y, color=plots.BLUE, s=40, label="validação (dados novos)", zorder=3)
for i, m in enumerate(order):
    axes[0].plot([summary.loc[m, "R² validação"], summary.loc[m, "R² treino"]], [i, i], color=plots.GRAY, linewidth=1)
axes[0].axvline(0, color=plots.INK, linewidth=1)
axes[0].set_yticks(y, order); axes[0].set_title("R²: treino vs. validação (distância = overfitting)"); axes[0].legend(fontsize=8)
axes[1].barh(y, summary.loc[order, "ganho MAE vs. baseline (%)"], color=plots.BLUE, height=0.6)
axes[1].axvline(0, color=plots.INK, linewidth=1)
axes[1].set_yticks(y, order); axes[1].set_title("Ganho de erro (MAE) vs. chutar a média (%)")
for ax in axes: ax.grid(axis="y", visible=False)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** nenhum modelo supera o baseline (todos com p ≥ 0,05; R² de validação ≤ 0).
Modelos flexíveis **decoram o treino**: Random Forest e Extra Trees chegam a R² 0,09 no treino, LightGBM 0,11 e XGBoost 0,05, e todos ficam **piores** que a média em dados novos. O KNN é o pior (−1% de MAE vs. a média).
Os lineares regularizados (Lasso/ElasticNet) empatam com a média porque zeram quase todos os coeficientes, ou seja, "aprendem" que não há sinal.
""")

nb.md("## 2. Outra formulação: classificar o post como top 10% de engajamento")
nb.code("""
top = tp.flag_top(df, ENGAGEMENT)
em.compare_classifiers(df, top).round(4)
""")
nb.md("**Leitura:** AUC ≈ 0,50 (cara ou coroa) nos 3 classificadores. Mudar a formulação não cria sinal.")

nb.md("## 3. Mais dados ajudariam? (curva de aprendizado)")
nb.code("""
lc = em.learning_curve_table(df, "LightGBM")
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(lc["posts de treino"], lc["R² treino"], "o-", color=plots.GRAY, linewidth=2, label="treino")
ax.plot(lc["posts de treino"], lc["R² validação"], "o-", color=plots.BLUE, linewidth=2, label="validação")
ax.axhline(0, color=plots.INK, linewidth=1); ax.set_xlabel("posts de treino"); ax.set_ylabel("R²")
ax.set_title("Curva de aprendizado — LightGBM"); ax.legend(); plt.show()
lc.round(4)
""")
nb.md("""
**Leitura:** com mais dados, o R² de treino **cai** de 0,59 para 0,11 (fica mais difícil decorar) e o de validação sobe de −0,08 para −0,01, **sem nunca passar de 0**.
Isso é o padrão de "não há sinal a aprender", e não de falta de dados. Coletar mais posts com as mesmas colunas não resolveria.
""")

nb.md("""
## 4. Teste de sensibilidade: quais modelos achariam um sinal real?
Plantamos dois tipos de efeito de **+5% nos likes** e repetimos a comparação:
- **A. Segmento** (aditivo): TikTok × vídeo × tech (~2% dos posts).
- **B. Não linear** (interação numérica): duração entre 100 e 200 **e** postado entre 18h e 22h (~4% dos posts).
""")
nb.code("""
SUBSET = ["Média (baseline)", "Ridge", "KNN (k=50)", "MLP (rede neural)", "Árvore de decisão", "Random Forest", "LightGBM", "CatBoost"]
models = {k: v for k, v in em.candidate_models().items() if k in SUBSET}
scenarios = {
    "A. segmento (TikTok × vídeo × tech)": va.demo_segment(df),
    "B. não linear (duração 100–200 & 18–22h)": df.content_length.between(100, 200) & df.hour.between(18, 21),
}
sensitivity = {}
for name, mask in scenarios.items():
    injected = va.inject_engagement_uplift(df, mask, uplift=0.05)
    s, _ = em.compare_models(injected, models=models)
    sensitivity[name] = s[["R² validação", "ganho MAE vs. baseline (%)", "p (melhor que baseline)", "supera baseline"]]
    print(f"{name}: {mask.mean():.1%} dos posts afetados")
sens = pd.concat(sensitivity, axis=1)
sens
""")
nb.code("""
fig, ax = plt.subplots(figsize=(10, 4.5))
r2 = pd.concat({k: v["R² validação"] for k, v in sensitivity.items()}, axis=1).loc[SUBSET[::-1]]
y = np.arange(len(r2))
for i, (col, color) in enumerate(zip(r2.columns, [plots.BLUE, plots.ORANGE])):
    ax.barh(y + (0.2 if i == 0 else -0.2), r2[col], height=0.38, color=color, label=col)
ax.axvline(0, color=plots.INK, linewidth=1)
ax.set_yticks(y, r2.index); ax.set_title("R² de validação com efeito plantado"); ax.legend(fontsize=8); ax.grid(axis="y", visible=False)
plt.show()
""")
nb.md("""
**Leitura:**
- **Efeito de segmento (A):** CatBoost, MLP, árvore, Random Forest e LightGBM recuperam o sinal (R² 0,04–0,05, ~1,5% menos erro).
  O Ridge supera o baseline só formalmente (R² 0,009, ~1/5 do sinal), porque o efeito é uma interação de 3 dummies, e um modelo linear sem interações não a representa.
- **Efeito não linear (B):** CatBoost, árvore e LightGBM captam a janela de duração × horário (R² ~0,10, ~4% menos erro). O Random Forest capta parcialmente (0,06), a MLP pouco (0,03) e o Ridge quase nada (0,008).
- **O KNN falha nos dois:** com 30 dimensões, a vizinhança se dilui.
- **Logo, a escolha de modelo importa quando há sinal,** e o protocolo detecta isso sozinho. Nos dados originais, a ausência de ganho é real.
""")

nb.md("## 5. Previsor final (pronto para uso)")
nb.code("""
predictor = em.EngagementPredictor.train(df, summary)
print(f"Modelo adotado: {predictor.model_name} · supera baseline: {predictor.beats_baseline} · R² validação: {predictor.cv_r2:.4f}")
examples = pd.DataFrame([
    {"platform": "TikTok", "content_type": "video", "content_category": "tech", "follower_count": 25_000},
    {"platform": "Instagram", "content_type": "image", "content_category": "beauty", "follower_count": 800_000},
    {"platform": "YouTube", "content_type": "video", "content_category": "lifestyle", "follower_count": 5_000},
])
defaults = {c: df[c].astype(str).mode()[0] for c in em.CATEGORICAL} | {c: df[c].median() for c in em.NUMERIC}
examples = pd.DataFrame([defaults | row for row in examples.to_dict("records")])
pd.concat([examples[["platform", "content_type", "content_category", "follower_count"]], predictor.predict(examples)], axis=1)
""")
nb.code("""
# Same training on the data with a planted segment effect: the predictor switches to a real model by itself.
injected = va.inject_engagement_uplift(df, va.demo_segment(df), uplift=0.05)
s_inj, _ = em.compare_models(injected, models=models)
p_inj = em.EngagementPredictor.train(injected, s_inj)
print(f"Com efeito plantado → modelo adotado: {p_inj.model_name} (R² validação {p_inj.cv_r2:.3f})")
pd.concat([examples[["platform", "content_type", "content_category"]], p_inj.predict(examples)], axis=1)
""")
nb.md("""
**Leitura:** nos dados originais, o previsor adota a **média** (19,9%, intervalo de 90%: 19,1%–20,7%) e avisa que a estimativa é igual para qualquer post. Prometer mais seria vender ruído.
Com sinal plantado, ele troca sozinho para um modelo real, e o post TikTok × vídeo × tech passa a ter previsão maior que os demais.

Para usar: `.venv/bin/python solution/cli/predict_engagement.py --platform TikTok --content_type video --content_category tech --follower_count 25000`

## 6. Conclusões
1. **14 abordagens supervisionadas** (lineares, vizinhos, rede neural, árvores, boosting) e uma formulação de classificação: **nenhuma prevê engajamento melhor que a média**.
2. Modelos flexíveis **decoram ruído** (R² de treino > 0, validação < 0). Sem validação, seriam vendidos como "explica X%".
3. **Mais dados não ajudam** (curva de aprendizado). O que falta são variáveis com relação real com o engajamento.
4. O protocolo é **sensível**: com +5% plantado, o boosting (CatBoost/LightGBM) detecta efeitos de segmento e não lineares. O linear capta só uma fração e o KNN falha. **Com dados reais, a recomendação é o CatBoost/LightGBM**, com adoção automática apenas se superar o baseline.
5. **Entregável:** `EngagementPredictor` + CLI. Ele escolhe sozinho o melhor modelo que supera o baseline, dá intervalo de 90% e cai para a média quando não há sinal.
""")

nb.save(sys.argv[1])
