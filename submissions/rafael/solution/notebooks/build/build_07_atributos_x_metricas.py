# Builds 07_atributos_x_metricas.ipynb: every attribute × views, likes and comments_count.
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 07 — Todos os atributos × views, likes e comentários

Cada atributo do dataset é testado contra as 3 métricas com o teste adequado ao seu tipo:

| Tipo | Teste | Efeito em escala comum | Efeito de negócio |
|---|---|---|---|
| Categórico | Kruskal-Wallis | η² (% da variância explicada) | melhor vs. pior grupo (%) |
| Numérico | Spearman | ρ² (%) | quintil mais alto vs. mais baixo (%) |
| Alta cardinalidade (`creator_id`) | ANOVA | η² **acima do esperado por acaso** com 5 mil grupos | p90/p10 das médias por creator |
| Texto (legenda, hashtags, comentários) | TF-IDF + Ridge (CV) | R² de validação (%) | — |

Todos os p-values são corrigidos juntos (Benjamini-Hochberg). **MDE** = menor diferença (%) que o teste detectaria com 80% de poder.
""")
nb.code(SETUP + '''
from social_insights import attribute_scan as sc
TARGETS = sc.TARGETS
table = sc.scan(df)
display(Markdown(f"**{len(table)} testes** · p < 0,05 sem correção: **{int((table.p_value < 0.05).sum())}** "
                 f"(esperado por acaso: {len(table) * 0.05:.0f}) · significativos após correção: **{int(table.significativo.sum())}**"))
display(Markdown("**Atributos fora da varredura (e por quê):**"))
sc.skipped_attributes()
''')

nb.md("## 1. Mapa geral: quanto cada atributo explica de cada métrica?")
nb.code("""
matrix = sc.summary_matrix(table)[TARGETS]
matrix = matrix.loc[matrix.max(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(8, 11))
plots.heatmap(ax, matrix, "Variância explicada (%) — escala até 1%", cmap="Blues", vmin=0, vmax=1, fmt="{:.3f}")
plt.show()
""")
nb.md("""
**Leitura:** o maior valor do mapa é **0,06%** da variância (creator_id × likes, e mesmo esse está dentro do acaso, p = 0,37). A escala vai até 1%, e todo o mapa fica branco.
Para comparação: em dados reais de redes sociais, seguidores sozinhos costumam explicar 20–50% da variância das views.
""")

nb.md("## 2. Ranking por métrica (os 10 atributos com maior efeito aparente)")
nb.code("""
COLS = ["atributo", "tipo", "variância explicada (%)", "efeito de negócio (%)", "MDE (%)", "leitura do efeito", "p_value", "q_value"]
for t in TARGETS:
    display(Markdown(f"### {t}"))
    display(table[table.alvo == t][COLS].head(10).style.format(
        {"variância explicada (%)": "{:.4f}", "efeito de negócio (%)": "{:+.3f}", "MDE (%)": "{:.3f}", "p_value": "{:.3f}", "q_value": "{:.3f}"}, na_rep="—"))
""")
nb.code("""
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
for ax, t in zip(axes, TARGETS):
    sub = table[(table.alvo == t) & table["efeito de negócio (%)"].notna() & (table.tipo != "alta cardinalidade")]
    sub = sub.sort_values("efeito de negócio (%)", key=abs).tail(12)
    y = np.arange(len(sub))
    ax.barh(y, sub["efeito de negócio (%)"].abs(), color=[plots.BLUE if s else plots.GRAY for s in sub["significativo"]], height=0.6, label="|efeito| observado")
    ax.scatter(sub["MDE (%)"], y, color=plots.ORANGE, marker="|", s=250, linewidths=2.5, label="MDE (detectável)", zorder=3)
    ax.set_yticks(y, sub["atributo"], fontsize=8); ax.set_title(f"{t}: |efeito| (%) vs. MDE"); ax.grid(axis="y", visible=False)
axes[0].legend(fontsize=8, loc="lower right")
fig.suptitle("Barras cinza = não significativas. Toda barra que passa do MDE ficou dentro do acaso após a correção.", y=1.01)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** os efeitos de negócio ficam entre 0,01% e 0,5%. Mesmo os que passam do MDE (ex.: mês × comentários, 0,53%) **não sobrevivem à correção para 96 testes**.
Note que 0,5% de 200 comentários é **1 comentário**.
""")

nb.md("## 3. Os \"melhores aparentes\" de perto")
nb.code("""
picks = table.sort_values("p_value").groupby("alvo").head(2)
picks = picks[picks.tipo.isin(["categórico", "numérico"])]
fig, axes = plt.subplots(1, len(picks), figsize=(4.2 * len(picks), 4), squeeze=False)
for ax, (_, row) in zip(axes[0], picks.iterrows()):
    prof = sc.group_profile(df, row["atributo"], row["alvo"])
    x = np.arange(len(prof))
    ax.errorbar(x, prof["mean"], yerr=prof["IC95"], fmt="o", color=plots.BLUE, capsize=3, markersize=5)
    ax.axhline(df[row["alvo"]].mean(), color=plots.GRAY, linestyle="--", linewidth=1)
    ax.set_xticks(x, [str(i)[:9] for i in prof.index], rotation=60, fontsize=7)
    ax.set_title(f"{row['atributo']} × {row['alvo']}\\np={row['p_value']:.3f} · q={row['q_value']:.2f}", fontsize=9)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:** os 2 atributos de menor p-value por métrica (ex.: período do dia × views, mês × comentários). As diferenças são de 1–3 views em 10.100 ou de ~1 comentário em 200, com ICs que quase tocam a média geral (tracejado).
São os candidatos que um relatório sem correção chamaria de "insight". Com 96 testes, ~5 passam de p < 0,05 por acaso, e foi o que aconteceu.
""")

nb.md("## 4. Relações entre as próprias métricas")
nb.code("""
metrics = ["views", "likes", "shares", "comments_count"]
frame = sc.attribute_frame(df)
corr = frame[metrics + ["comment_sentences"]].corr("spearman")
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
plots.heatmap(axes[0], corr, "Spearman entre métricas", vmin=-1, vmax=1, fmt="{:.3f}")
g = frame.groupby("comment_sentences")["comments_count"].agg(["mean", "sem", "size"])
axes[1].errorbar(g.index, g["mean"], yerr=1.96 * g["sem"], fmt="o-", color=plots.BLUE, capsize=3)
axes[1].set_xlabel("frases em comments_text"); axes[1].set_ylabel("comments_count (média)")
axes[1].set_title("Texto dos comentários × contagem de comentários"); axes[1].set_ylim(195, 205)
fig.tight_layout(); plt.show()
""")
nb.md("""
**Leitura:**
- Views, likes, shares e comentários são **independentes entre si** (|ρ| < 0,01). Em redes reais, likes e comentários sobem junto com as views (ρ costuma passar de 0,7).
- **Inconsistência interna:** `comments_count` marca ~200 comentários por post, mas `comments_text` traz de 0 a 5 frases, sem relação nenhuma com a contagem. As colunas foram geradas separadamente.

## 5. Conclusão
1. **96 combinações atributo × métrica, 0 efeitos reais.** Nenhum atributo explica mais que 0,06% de views, likes ou comentários, e os ~5 "achados" sem correção são o acaso esperado.
2. Vale para **todos os tipos de atributo**: categóricos (plataforma, formato, audiência, tempo), numéricos (seguidores, duração, hashtags, horário, tendência no tempo), creator (5 mil creators sem diferença além do acaso) e textos (legenda, hashtags e comentários com R² ≤ 0).
3. **As métricas não se relacionam entre si**, nem o texto dos comentários com a contagem de comentários. Isso é a assinatura de um dataset gerado com cada coluna sorteada de forma independente.
4. **Método validado:** em testes com efeito plantado (plataforma, seguidores, creator e legenda), a varredura acusa o atributo certo (ver `solution/tests/test_attribute_scan.py`). Rodando com dados reais, este mesmo notebook vira o mapa de "o que move cada métrica".
""")

nb.save(sys.argv[1])
