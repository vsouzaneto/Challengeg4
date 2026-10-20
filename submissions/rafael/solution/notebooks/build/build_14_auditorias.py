# Builds 14_auditorias.ipynb: disclosure compliance, sponsor fit, market coherence, length per format and power per subgroup.
import sys

from nbbuilder import SETUP, Notebook

nb = Notebook()
nb.md("""
# 14 — Auditorias que não dependem de achar efeito

Mesmo quando o engajamento é ruído, a **composição** da carteira pode ser auditada. Esta parte responde a quatro perguntas de gestão e a uma de método:
1. **Disclosure:** quantos patrocínios têm risco regulatório, e o rótulo aparece no texto?
2. **Fit:** o patrocinador combina com o nicho do creator?
3. **Mercado:** o post fala o idioma da audiência e está numa plataforma que ela consegue abrir?
4. **Duração:** o tamanho importa quando medido na unidade certa (segundos no vídeo, palavras no texto)?
5. **Poder:** em cada subgrupo, qual o menor efeito que daria para ver?

As regras (risco, fit, idioma e plataforma por mercado) são constantes editáveis em `social_insights/audits.py`. Elas vêm do conhecimento de mercado, não deste dataset, e não são parecer jurídico.
""")
nb.code(SETUP + '''
from social_insights import audits
''')

nb.md("## 1. Disclosure: risco regulatório por mercado")
nb.code("""
disc = audits.disclosure_audit(df)
display(Markdown(f"**{disc.verdict}**"))
display(disc.evidence)
for name, table in disc.details.items():
    display(Markdown(f"**{name}**")); display(table)
""")
nb.code("""
risk = disc.evidence[["% risco alto", "% risco médio", "% risco baixo"]]
ax = risk.plot.barh(stacked=True, figsize=(9, 4.5), color=[plots.ORANGE, plots.GRAY, plots.BLUE])
ax.set_xlabel("% dos posts patrocinados"); ax.set_ylabel(""); ax.legend(loc="lower right", fontsize=8)
ax.set_title("Risco de disclosure por mercado da audiência")
plt.show()
""")
nb.md("""
**Leitura:** quase metade dos patrocínios usa disclosure implícito, que não identifica o post como publicidade em nenhum dos 8 mercados. Além disso, o rótulo declarado na base não aparece no texto: os posts com disclosure "em hashtags" têm #ad tanto quanto os orgânicos (~2%). Com dados reais, **o rótulo precisa ser verificável** (#ad/#publi no texto), não só um campo de planilha.
""")

nb.md("## 2. Fit patrocinador × nicho")
nb.code("""
fit = audits.sponsor_fit(df)
display(Markdown(f"**{fit.verdict}**"))
display(fit.evidence)
for name, table in fit.details.items():
    display(Markdown(f"**{name}**")); display(table)
""")
nb.md("""
**Leitura:** os patrocinadores estão distribuídos por igual entre os nichos (~1/6 cada), então 60% dos patrocínios ficam fora do nicho (ex.: gaming em beauty). Aqui isso não muda o desempenho. Com dados reais, este é o primeiro filtro de seleção de creator a testar.
""")

nb.md("## 3. Coerência idioma × mercado × plataforma")
nb.code("""
mkt = audits.market_coherence(df)
display(Markdown(f"**{mkt.verdict}**"))
display(mkt.evidence)
for name, table in mkt.details.items():
    display(Markdown(f"**{name}**")); display(table)
""")
nb.code("""
ax = mkt.evidence["% coerente"].sort_values().plot.barh(figsize=(8, 4), color=plots.BLUE)
ax.set_xlabel("% dos posts no idioma do mercado e em plataforma disponível"); ax.set_ylabel("")
ax.set_title("Posts que a audiência consegue ver e entender")
plt.show()
""")
nb.md("""
**Leitura:** Brasil, Alemanha e Rússia não têm nenhum post no próprio idioma (não existe português, alemão nem russo na base), e 1 em cada 8 posts mira um mercado onde a plataforma é bloqueada. Isso mostra que audiência e conteúdo foram sorteados de forma independente. Com dados reais, a mesma função vira **checagem de qualidade** e **mapa de cobertura** (quais mercados estão sem conteúdo no idioma).
""")

nb.md("## 4. Duração na unidade correta")
nb.code("""
length = audits.length_by_format(df)
display(Markdown(f"**{length.verdict}**"))
display(length.evidence)
for name, table in length.details.items():
    display(Markdown(f"**{name}**")); display(table)
""")
nb.md("""
**Leitura:** imagem e misto têm "duração" de 10 a 599, igual a vídeo e texto, ou seja, o campo não tem significado nesses formatos. Separando segundos (vídeo) e palavras (texto), o tamanho continua sem efeito, e o teste teria poder para ver |ρ| ≥ 0,04. As análises anteriores com `length_bin` (notebooks 02–12, crença "conteúdo curto") misturam unidades e devem ser lidas com essa ressalva.
""")

nb.md("## 5. Poder estatístico por subgrupo")
nb.code("""
power = audits.subgroup_power(df)
display(Markdown(f"**{power.verdict}**"))
display(power.evidence.head(15))
""")
nb.code("""
eng = power.evidence.query("métrica == @audits.ENGAGEMENT")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(eng["n"], eng["MDE (%)"], color=plots.BLUE, s=20)
for _, r in eng.nlargest(4, "MDE (%)").iterrows():
    ax.annotate(r["valor"], (r["n"], r["MDE (%)"]), fontsize=8, xytext=(5, 0), textcoords="offset points")
ax.set_xscale("log"); ax.set_xlabel("posts no subgrupo (log)"); ax.set_ylabel("menor efeito detectável (% da média)")
ax.set_title("Quanto menor o grupo, maior o efeito necessário para aparecer")
plt.show()
""")
nb.md("""
**Leitura:** até o menor grupo (nano, 454 posts) detectaria uma diferença de 0,3% no engajamento. Então "equivalente" significa "sem diferença relevante", não "sem dados". Com dados reais (variância muito maior que a do Poisson), esta tabela mostra onde ainda faltam posts antes de decidir.

## Conclusões
1. **Compliance é a ação mais segura desta entrega:** quase metade dos patrocínios tem disclosure implícito. Exigir rótulo explícito no texto não custa engajamento.
2. **O rótulo de disclosure da base não é auditável**, porque não aparece no texto. Com dados reais, verificar no próprio post.
3. **Fit e coerência de mercado** não mudam o desempenho aqui (dados sorteados), mas expõem lacunas de carteira: 60% dos patrocínios fora do nicho e 3 mercados sem conteúdo no idioma.
4. **Duração** só tem significado em vídeo e texto, e não tem efeito em nenhum dos dois.
5. **Poder:** todos os "sem efeito" desta entrega são conclusivos para efeitos de 5% ou mais.
""")
nb.save(sys.argv[1])
