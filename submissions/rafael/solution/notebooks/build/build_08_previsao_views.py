# Builds 08_previsao_views.ipynb: what is known before posting, and can it forecast views?
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 08 — Prever views **antes** de postar

1. **Inventário:** quais colunas são conhecidas antes da publicação (e quais só existem depois).
2. **Checagem dos dados pré-publicação:** tipo, categoria, duração, quem posta, patrocínio.
3. **"Quem posta" vira histórico do creator:** média e último resultado dos posts **anteriores** (sem olhar o futuro).
4. **Validação temporal:** treina no passado (~80% iniciais do período) e testa nos posts mais recentes, como numa previsão real.
5. **Blocos acumulados:** conteúdo → + quem posta → + patrocínio → + horário → + audiência (LightGBM e CatBoost).
6. **Controle positivo:** se "quem posta" importasse, o método perceberia?
""")
nb.code(SETUP + '''
from social_insights import views_forecast as vf
''')

nb.md("## 1. Inventário: o que se sabe antes de postar")
nb.code("""
inv = vf.inventory()
display(Markdown(f"**{int(inv['conhecido antes de postar'].sum())} colunas conhecidas antes** · {int((~inv['conhecido antes de postar']).sum())} só depois ou sem uso"))
inv
""")

nb.md("## 2. Checagem dos dados pré-publicação")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(18, 4))
for ax, col in zip(axes, ["content_type", "content_category", "is_sponsored"]):
    counts = df[col].astype(str).value_counts().sort_values()
    ax.barh(counts.index, counts.values, color=plots.BLUE, height=0.6)
    ax.set_title(f"{col}: posts"); ax.grid(axis="y", visible=False)
fig.tight_layout(); plt.show()

length = df.groupby("content_type")["content_length"].describe()[["count", "min", "50%", "max"]]
display(Markdown("**Duração (`content_length`) por formato:** deveria ser segundos para vídeo e palavras para texto, mas a faixa é a mesma em todos"))
display(length)
display(Markdown("**Quem posta:**"))
pd.DataFrame({"creators": [df.creator_id.nunique()], "posts por creator (mediana)": [df.creator_id.value_counts().median()],
              "nomes por creator_id (mediana)": [df.groupby("creator_id").creator_name.nunique().median()],
              "seguidores distintos por creator (mediana)": [df.groupby("creator_id").follower_count.nunique().median()]})
""")
nb.md("""
**Leitura:**
- `content_length` vai de 10 a 599 em **todos** os formatos, inclusive imagem. É usado no modelo, mas não representa "tamanho do vídeo" de forma confiável.
- `creator_id` existe (5 mil creators, ~10 posts cada), mas o **nome e o nº de seguidores mudam a cada post**. Por isso "quem posta" entra como **histórico de resultados** do creator_id, e o seguidor como valor do momento.
""")

nb.md("## 3. Quem posta: creators mantêm o nível?")
nb.code("""
cons = vf.creator_consistency(df)
data_sorted = df.sort_values("post_date")
rank = data_sorted.groupby("creator_id").cumcount(); size = data_sorted.groupby("creator_id")["views"].transform("size")
first = data_sorted[rank < size / 2].groupby("creator_id")["views"].mean()
second = data_sorted[rank >= size / 2].groupby("creator_id")["views"].mean()
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(first, second, s=4, alpha=0.3, color=plots.BLUE)
ax.set_xlabel("média de views — 1ª metade dos posts"); ax.set_ylabel("média de views — 2ª metade")
ax.set_title(f"Consistência do creator: ρ = {cons['ρ (1ª metade × 2ª metade)']:.3f}")
plt.show()
""")
nb.md("""
**Leitura:** a média de um creator na 1ª metade dos posts **não diz nada** sobre a 2ª (ρ ≈ 0, nuvem redonda). Nenhum creator é consistentemente forte ou fraco.
Em dados reais, esse ρ costuma ser alto (o creator tem audiência própria). É o teste mais direto de "quem postou importa?".
""")

nb.md("## 4. Previsão com validação temporal")
nb.code("""
history = vf.add_creator_history(df)
tr, te, cutoff = vf.temporal_split(history)
display(Markdown(f"Treino: posts até **{cutoff.date()}** ({len(tr):,}) · Teste: posts depois ({len(te):,})"))
evaluation = vf.evaluate(df)
evaluation.style.format({"R² treino": "{:.4f}", "R²": "{:.4f}", "MAE (views)": "{:.1f}", "erro médio (%)": "{:.3f}",
                         "p (melhor que média)": "{:.3f}", "ganho MAE vs. média (%)": "{:+.2f}"}, na_rep="—")
""")
nb.code("""
fig, axes = plt.subplots(1, 2, figsize=(16, 4.5))
ev = evaluation.copy(); ev["rótulo"] = ev["abordagem"] + np.where(ev["modelo"] == "—", "", " · " + ev["modelo"])
y = np.arange(len(ev))[::-1]
axes[0].barh(y, ev["ganho MAE vs. média (%)"], color=[plots.BLUE if s else plots.GRAY for s in ev["supera a média"]], height=0.6)
axes[0].axvline(0, color=plots.INK, linewidth=1); axes[0].set_yticks(y, ev["rótulo"], fontsize=8)
axes[0].set_title("Ganho de erro vs. média histórica (%) — teste nos posts mais recentes"); axes[0].grid(axis="y", visible=False)
sub = ev[ev.modelo != "—"]
for name, color in [("LightGBM", plots.BLUE), ("CatBoost", plots.ORANGE)]:
    s = sub[sub.modelo == name]
    axes[1].plot(s["abordagem"], s["R² treino"], "o--", color=color, label=f"{name} treino")
    axes[1].plot(s["abordagem"], s["R²"], "o-", color=color, linewidth=2, label=f"{name} teste")
axes[1].axhline(0, color=plots.INK, linewidth=1); axes[1].set_title("R² por bloco de variáveis (treino × teste)")
axes[1].tick_params(axis="x", rotation=20); axes[1].legend(fontsize=8)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:**
- **Nenhum bloco supera a média histórica** nos posts mais recentes. Acrescentar quem posta, patrocínio, horário ou audiência não reduz o erro.
- **Usar a média passada do creator piora** (+5,8% de erro), porque o histórico dele é ruído e não um sinal.
- O LightGBM "aprende" cada vez mais no treino (R² até ~0,10) e nada no teste: **decora**.
- O erro típico já é de ~0,8% (~80 views), simplesmente porque as views quase não variam.
""")

nb.md("## 5. Controle positivo: e se quem posta importasse?")
nb.code("""
planted = va.inject_creator_effect(df, "views", relative_sd=0.03)          # each creator with a persistent level (±3%)
planted = va.inject_uplift(planted, va.demo_segment(planted), "views", 0.03)  # + content effect: TikTok × video × tech
display(Markdown(f"Consistência do creator com o efeito plantado: ρ = **{vf.creator_consistency(planted)['ρ (1ª metade × 2ª metade)']:.2f}**"))
ev_planted = vf.evaluate(planted, models=("LightGBM",))
ev_planted[["abordagem", "modelo", "R²", "erro médio (%)", "ganho MAE vs. média (%)", "supera a média"]].round(4)
""")
nb.md("""
**Leitura:** quando cada creator tem um nível próprio, o bloco **"+ quem posta"** salta para R² ≈ 0,88 e erra ~66% menos que a média. O histórico do creator vira o principal preditor, como esperado.
**Logo, a ausência de previsão nos dados originais é real:** o método enxergaria "quem posta" e "o que posta" se isso existisse.
""")

nb.md("## 6. Previsor pronto para uso")
nb.code("""
forecaster = vf.ViewsForecaster.train(df, evaluation)
planned = pd.DataFrame([
    {"platform": "TikTok", "content_type": "video", "content_category": "tech", "language": "English", "content_length": 45,
     "caption_words": 15, "n_hashtags": 3, "follower_count": 25_000, "is_sponsored": True, "sponsor_category": "electronics",
     "disclosure_type": "explicit", "disclosure_location": "caption", "weekday": "Friday", "hour": 19,
     "audience_gender_distribution": "male", "audience_age_distribution": "19-25", "audience_location": "USA",
     **vf.creator_snapshot(df, "creator_586")},
])
display(Markdown(f"Modelo adotado nos dados originais: **{forecaster.model_name}**"))
display(forecaster.predict(planned))
planted_forecaster = vf.ViewsForecaster.train(planted, ev_planted)
planned_planted = planned.assign(**vf.creator_snapshot(planted, "creator_586"))
display(Markdown(f"Com efeito plantado: **{planted_forecaster.model_name}**"))
planted_forecaster.predict(planned_planted)
""")
nb.md("""
**Uso:** `.venv/bin/python solution/cli/predict_views.py --creator_id creator_586 --platform TikTok --content_type video --content_category tech --content_length 45`

## 7. Conclusões
1. **Dá para saber antes de postar:** plataforma, formato, categoria, idioma, duração, legenda/hashtags (como contagem), creator (via histórico), seguidores, patrocínio/disclosure, horário e audiência do creator. O resto (views, likes, shares, comentários) é resultado.
2. **Nenhuma combinação desses dados prevê as views** melhor que a média histórica (10.100 ± ~165 views, intervalo de 90%), nem com validação temporal e modelos de boosting.
3. **"Quem posta" não importa neste dataset:** creators não mantêm o nível (ρ ≈ 0) e o histórico deles piora a previsão.
4. **Qualidade:** `content_length` não distingue formatos, e nome/seguidores do creator mudam a cada post.
5. **O previsor está pronto e é honesto:** usa a média e avisa enquanto nada ajudar. Com dados reais (ou com o efeito plantado), adota sozinho o modelo com histórico do creator.
""")

nb.save(sys.argv[1])
