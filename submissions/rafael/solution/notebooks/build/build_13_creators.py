# Builds 13_creators.ipynb: does who posts matter for views (and likes/comments)?
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 13 — Creator × views: quem posta importa?

Em redes reais, o creator costuma ser o fator que mais pesa: cada um tem sua audiência.
Aqui testamos isso de quatro formas:
1. **Identidade:** qual coluna identifica um creator (`creator_id` ou `creator_name`)?
2. **Quanto da variação é do creator?** ICC = % da variação de views, likes e comentários ligada ao creator.
3. **As médias dos creators variam mais que o acaso?** Comparamos com os mesmos posts redistribuídos ao acaso entre creators.
4. **Os melhores continuam os melhores?** Top 10% do 1º ano × 2º ano, e um ranking honesto (média ajustada pelo nº de posts).
""")
nb.code(SETUP + '''
from social_insights import creators as cr
cr.identity_check(df)
''')
nb.md("""
**Leitura:** `creator_id` é a única identidade possível (5 mil creators, ~10 posts cada). `creator_name` tem 42 mil valores, e o mesmo nome aparece em vários ids (nomes gerados). Mesmo assim, cada `creator_id` aparece com ~10 nomes e seguidores diferentes, então é um identificador fraco.
""")
nb.md("## 1. Quanto da variação pertence ao creator?")
nb.code("cr.variance_share(df).round(4)")
nb.md("**Leitura:** ICC ≈ 0% nas três métricas. Saber quem postou não explica nada do resultado.")

nb.md("## 2. As médias dos creators variam mais que o acaso?")
nb.code("""
spread = cr.spread_vs_chance(df)
fig, ax = plt.subplots(figsize=(10, 4))
bins = np.linspace(min(spread["medias"].min(), spread["medias_acaso"].min()), max(spread["medias"].max(), spread["medias_acaso"].max()), 50)
ax.hist(spread["medias_acaso"], bins=bins, color=plots.GRAY, alpha=0.6, label="posts redistribuídos ao acaso")
ax.hist(spread["medias"], bins=bins, histtype="step", linewidth=2.5, color=plots.BLUE, label="creators reais")
ax.set_xlabel("média de views do creator"); ax.set_ylabel("nº de creators"); ax.legend()
ax.set_title(f"Desvio entre creators: {spread['desvio observado']:.1f} views (acaso: {spread['desvio esperado por acaso']:.1f}) · p = {spread['p_value']:.2f}")
plt.show()
""")
nb.md("""
**Leitura:** as duas distribuições se sobrepõem. A diferença entre o "melhor" e o "pior" creator é **exatamente** a que surgiria sorteando os posts entre eles.
""")

nb.md("## 3. Os melhores continuam os melhores?")
nb.code("""
pers = cr.persistence(df)
t = pers["tabela"]
fig, ax = plt.subplots(figsize=(6.5, 5.5))
ax.scatter(t["1º ano"], t["2º ano"], s=5, alpha=0.3, color=plots.BLUE)
ax.set_xlabel("média de views no 1º ano"); ax.set_ylabel("média de views no 2º ano")
ax.set_title(f"ρ = {pers['ρ 1º × 2º ano']:.3f} · {pers['% que continuou']:.1f}% dos top 10% continuaram no top (acaso: 10%)")
plt.show()
{k: v for k, v in pers.items() if k != "tabela"}
""")
nb.md("""
**Leitura:** nuvem redonda, sem diagonal. Dos 500 creators no top 10% do 1º ano, só 44 (8,8%) continuaram no top no 2º, **menos** que os 10% do acaso.
""")

nb.md("## 4. Ranking honesto: média bruta × média ajustada")
nb.code("""
board = cr.leaderboard(df)
display(board.round(1))
fig, ax = plt.subplots(figsize=(9, 4.5))
y = np.arange(len(board))[::-1]
ax.scatter(board["média bruta"], y, color=plots.ORANGE, s=50, label="média bruta (parece campeão)", zorder=3)
ax.scatter(board["média ajustada"], y, color=plots.BLUE, s=50, label="média ajustada (descontada a sorte)", zorder=3)
for i, (_, r) in zip(y, board.iterrows()):
    ax.plot([r["média ajustada"], r["média bruta"]], [i, i], color=plots.GRAY, linewidth=1)
ax.axvline(df.views.mean(), color=plots.GRAY, linestyle="--", linewidth=1)
ax.set_yticks(y, board.index); ax.set_xlabel("views"); ax.legend(fontsize=8); ax.set_title("Top 10 creators por média de views")
plt.show()
""")
nb.md("""
**Leitura:** os "campeões" têm ~10.200 views de média, mas com ~10 posts cada essa vantagem é sorte. Descontada a sorte, todos voltam à média geral (10.100), e o histórico deles tem **peso 0%**.

## 5. Controle positivo
Se cada creator tivesse um nível próprio (±3%), as mesmas funções acusariam: ICC > 50%, médias espalhadas além do acaso e mais de 50% dos top continuando no top (`solution/tests/test_creators.py`).

## Conclusões
1. **Quem posta não importa neste dataset:** 0% da variação de views, likes e comentários está ligada ao creator.
2. **Não há creators campeões:** os rankings por média são sorte e não se repetem de um ano para o outro.
3. **Implicação:** não vale pagar prêmio por um creator por causa do desempenho passado; contratar por preço e por resultado (ver Estratégia).
4. **Com dados reais**, este é provavelmente o primeiro fator a reaparecer, e as mesmas funções medem isso.
""")
nb.save(sys.argv[1])
