"""OS-04 - Complementos: tabela de sanidade, hashtags com correcao de testes multiplos,
efeito maximo em valores absolutos e tamanho de amostra para testes futuros."""

import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

SEED = 42
MIN_POSTS_HASHTAG = 100
FDR = 0.05
Z_SOMA = 1.96 + 0.84          # poder 80%, significancia 5% bicaudal (formula da OS)
LIFTS = [0.05, 0.10, 0.20, 0.40]

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os04"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OS03C_BLOCO1 = SCRIPT_DIR.parent / "outputs" / "os03c" / "bloco1_equivalencia.csv"

METRICAS_HASH = ["taxa_engajamento", "shares"]
METRICAS_CV = ["engajamento", "shares", "comments_count"]

# faixas da OS-04: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

np.random.seed(SEED)


def salvar(df, nome):
    df.to_csv(OUT_DIR / nome, index=False)
    print(f"  -> {nome} ({len(df)} linhas)")


def num(x, dec=4):
    """Numero no formato pt-BR para as tabelas do resumo."""
    if isinstance(x, str):
        return x
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def tabela_md(df, cols=None):
    cols = list(df.columns) if cols is None else cols
    linhas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        linhas.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(linhas)


# ---------------------------------------------------------------- carga e derivadas
df = pd.read_csv(DATA_PATH)
df["engajamento"] = df["likes"] + df["shares"] + df["comments_count"]
df["taxa_engajamento"] = df["engajamento"] / df["views"]
df["faixa_seguidores"] = pd.cut(df["follower_count"], bins=FAIXA_SEG_BINS,
                                labels=FAIXA_SEG_LABELS, right=True).astype(str)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

MEDIA_ENG = df["engajamento"].mean()
MEDIA_SHARES = df["shares"].mean()
MEDIA_COMMENTS = df["comments_count"].mean()

# ---------------------------------------------------------------- Item 1: sanidade
print("\n[Item 1] Tabela de sanidade")
san = []


def ind(nome, valor):
    san.append({"indicador": nome, "valor": valor})


# 1.1 mediana de views por faixa de seguidores
for faixa in FAIXA_SEG_LABELS:
    sub = df[df["faixa_seguidores"] == faixa]
    ind(f"1. mediana de views - faixa {faixa} (n={len(sub)})", sub["views"].median())

# 1.2 correlacao likes x views
ind("2. correlação de Pearson likes × views", stats.pearsonr(df["likes"], df["views"])[0])
ind("2. correlação de Spearman likes × views", stats.spearmanr(df["likes"], df["views"])[0])

# 1.3 correlacao log10(follower_count) x log10(views)
log_seg = np.log10(df["follower_count"].to_numpy(dtype=float))
log_views = np.log10(df["views"].to_numpy(dtype=float))
ind("3. correlação de Pearson log10(follower_count) × log10(views)",
    stats.pearsonr(log_seg, log_views)[0])

# 1.4 variancia / media (indice de dispersao)
for m in ["views", "likes", "shares", "comments_count"]:
    ind(f"4. variância ÷ média - {m}", df[m].var(ddof=1) / df[m].mean())

# 1.5 engajamento no percentil 1 / mediana
p1_eng = np.percentile(df["engajamento"], 1)
med_eng = df["engajamento"].median()
ind("5. engajamento no percentil 1 ÷ mediana do engajamento", p1_eng / med_eng)

# 1.6 % de posts com engajamento abaixo de 10% da mediana
ind("6. % de posts com engajamento < 10% da mediana",
    100 * (df["engajamento"] < 0.10 * med_eng).mean())

# 1.7 minimo e maximo de views e de engajamento
ind("7. mínimo de views", df["views"].min())
ind("7. máximo de views", df["views"].max())
ind("7. mínimo de engajamento", df["engajamento"].min())
ind("7. máximo de engajamento", df["engajamento"].max())

# 1.8 / 1.9 creator_id
por_creator = df.groupby("creator_id").agg(
    n_posts=("id", "size"),
    n_plat=("platform", "nunique"),
    n_seg=("follower_count", "nunique"),
)
N_CREATORS = len(por_creator)
ind(f"8. % de creator_id em uma única plataforma (de {N_CREATORS} creators)",
    100 * (por_creator["n_plat"] == 1).mean())
ind("9. % de creator_id com o mesmo follower_count em todos os posts",
    100 * (por_creator["n_seg"] == 1).mean())

# 1.10 V de Cramer entre language e audience_location
tab = pd.crosstab(df["language"], df["audience_location"])
chi2 = stats.chi2_contingency(tab)[0]
v_cramer = np.sqrt(chi2 / (tab.to_numpy().sum() * (min(tab.shape) - 1)))
ind(f"10. V de Cramér language × audience_location ({tab.shape[0]}×{tab.shape[1]})", v_cramer)

# 1.11 sponsor_name entre os patrocinados
patro = df[df["is_sponsored"]]
ind("11. sponsor_name distintos entre os posts patrocinados", patro["sponsor_name"].nunique())
ind("11. total de posts patrocinados", len(patro))

# 1.12 % de posts em Bilibili + RedNote
ind("12. % de posts em Bilibili + RedNote",
    100 * df["platform"].isin(["Bilibili", "RedNote"]).mean())

# 1.13 mediana de content_length por content_type
for ct in sorted(df["content_type"].unique()):
    sub = df[df["content_type"] == ct]
    ind(f"13. mediana de content_length - {ct} (n={len(sub)})", sub["content_length"].median())

item1 = pd.DataFrame(san)
item1["valor"] = item1["valor"].astype(float).round(6)
salvar(item1, "item1_sanidade.csv")

# ---------------------------------------------------------------- Item 2: hashtags + BH
print("\n[Item 2] Hashtags com correcao de testes multiplos")
uni = df[df["hashtags"].notna()].reset_index(drop=True)
N_UNI = len(uni)
print(f"  universo (hashtags preenchido): {N_UNI} de {N} posts "
      f"({100 * N_UNI / N:.2f}%); fora: {N - N_UNI}")

tags_por_post = [set(t.strip() for t in s.split(",")) for s in uni["hashtags"]]
cont_tags = Counter()
for t in tags_por_post:
    cont_tags.update(t)
testaveis = sorted(t for t, c in cont_tags.items() if c >= MIN_POSTS_HASHTAG)
print(f"  hashtags distintas: {len(cont_tags)}; com n >= {MIN_POSTS_HASHTAG}: {len(testaveis)}")

pos_por_tag = {t: [] for t in testaveis}
for i, tags in enumerate(tags_por_post):
    for t in tags & pos_por_tag.keys():
        pos_por_tag[t].append(i)
pos_por_tag = {t: np.array(p) for t, p in pos_por_tag.items()}

vals_uni = {m: uni[m].to_numpy(dtype=float) for m in METRICAS_HASH}
linhas = []
for m in METRICAS_HASH:
    v = vals_uni[m]
    for t in testaveis:
        com_mask = np.zeros(N_UNI, dtype=bool)
        com_mask[pos_por_tag[t]] = True
        com, sem = v[com_mask], v[~com_mask]
        linhas.append({
            "metrica": m, "hashtag": t,
            "n_com": len(com), "n_sem": len(sem),
            "media_com": com.mean(), "media_sem": sem.mean(),
            "lift": com.mean() / sem.mean(),
            "p_valor": stats.ttest_ind(com, sem, equal_var=False).pvalue,
        })
item2 = pd.DataFrame(linhas)

# Benjamini-Hochberg (FDR 5%) separado por metrica
item2["q_valor"] = np.nan
item2["significativo_bh"] = ""
for m in METRICAS_HASH:
    sel = item2["metrica"] == m
    rej, q, _, _ = multipletests(item2.loc[sel, "p_valor"].to_numpy(), alpha=FDR, method="fdr_bh")
    item2.loc[sel, "q_valor"] = q
    item2.loc[sel, "significativo_bh"] = np.where(rej, "sim", "nao")

item2 = item2.sort_values(["metrica", "lift"], ascending=[True, False]).reset_index(drop=True)
for c in ["media_com", "media_sem", "lift", "p_valor", "q_valor"]:
    item2[c] = item2[c].round(8)
salvar(item2, "item2_hashtags.csv")

resumo2 = []
for m in METRICAS_HASH:
    sub = item2[item2["metrica"] == m]
    k = len(sub)
    resumo2.append({
        "metrica": m,
        "hashtags_testadas": k,
        "p_menor_005_sem_correcao": int((sub["p_valor"] < 0.05).sum()),
        "esperadas_por_acaso": round(k * 0.05, 2),
        "significativas_apos_bh": int((sub["significativo_bh"] == "sim").sum()),
        "menor_lift": round(sub["lift"].min(), 6),
        "maior_lift": round(sub["lift"].max(), 6),
    })
resumo2 = pd.DataFrame(resumo2)
print(resumo2.to_string(index=False))

top10 = pd.concat([item2[item2["metrica"] == m].head(10) for m in METRICAS_HASH])

# ---------------------------------------------------------------- Item 3: efeito absoluto
print("\n[Item 3] Efeito maximo em valores absolutos")
b1 = pd.read_csv(OS03C_BLOCO1)
print(f"  lido {OS03C_BLOCO1.name}: {len(b1)} linhas")

MEDIA_POR_METRICA = {"taxa_engajamento": MEDIA_ENG, "shares": MEDIA_SHARES,
                     "comments_count": MEDIA_COMMENTS}
UNIDADE = {"taxa_engajamento": "interacoes por post", "shares": "shares por post",
           "comments_count": "comentarios por post"}

item3 = b1[["variavel", "segmento", "metrica", "n", "lift",
            "efeito_maximo_plausivel_pct"]].copy()
item3["media_da_base"] = item3["metrica"].map(MEDIA_POR_METRICA)
item3["unidade"] = item3["metrica"].map(UNIDADE)
item3["efeito_maximo_absoluto"] = (item3["efeito_maximo_plausivel_pct"] / 100
                                   * item3["media_da_base"])
item3["media_da_base"] = item3["media_da_base"].round(6)
item3["efeito_maximo_absoluto"] = item3["efeito_maximo_absoluto"].round(6)
salvar(item3, "item3_efeito_absoluto.csv")

resumo3 = (item3.sort_values("efeito_maximo_plausivel_pct", ascending=False)
           .groupby(["variavel", "metrica"], as_index=False).first()
           [["variavel", "metrica", "segmento", "n", "efeito_maximo_plausivel_pct",
             "efeito_maximo_absoluto", "unidade"]]
           .sort_values(["metrica", "efeito_maximo_plausivel_pct"], ascending=[True, False]))
maior_base = (item3.sort_values("efeito_maximo_plausivel_pct", ascending=False)
              .groupby("metrica", as_index=False).first()
              [["metrica", "variavel", "segmento", "n", "efeito_maximo_plausivel_pct",
                "efeito_maximo_absoluto", "unidade"]])
print(maior_base.to_string(index=False))

# ---------------------------------------------------------------- Item 4: tamanho de amostra
print("\n[Item 4] Tamanho de amostra para testes futuros")
cvs = []
for m in METRICAS_CV:
    cv = df[m].std(ddof=1) / df[m].mean()
    cvs.append((f"CV da base - {m}", cv))
for c in [0.5, 0.7, 1.0]:
    cvs.append((f"cenario fixo CV = {c:.1f}", c))

linhas = []
for rotulo, cv in cvs:
    for lift in LIFTS:
        n_var = 2 * (Z_SOMA ** 2) * (cv ** 2) / (lift ** 2)
        linhas.append({
            "cv_rotulo": rotulo, "cv_valor": round(cv, 6),
            "lift_pct": round(lift * 100, 1),
            "n_por_variante": int(np.ceil(n_var)),
        })
item4 = pd.DataFrame(linhas)
salvar(item4, "item4_tamanho_amostra.csv")
print(item4.to_string(index=False))

# ---------------------------------------------------------------- resumo_os04.md
print("\n[Resumo] resumo_os04.md")

t1 = pd.DataFrame({
    "indicador": item1["indicador"],
    "valor": [num(v, 0) if abs(v) >= 1000 or float(v).is_integer() else num(v, 6)
              for v in item1["valor"]],
})

t2a = pd.DataFrame({
    "Métrica": resumo2["metrica"],
    "Hashtags testadas": [num(v, 0) for v in resumo2["hashtags_testadas"]],
    "p < 0,05 sem correção": [num(v, 0) for v in resumo2["p_menor_005_sem_correcao"]],
    "Esperadas por acaso": [num(v, 2) for v in resumo2["esperadas_por_acaso"]],
    "Significativas após BH": [num(v, 0) for v in resumo2["significativas_apos_bh"]],
    "Menor lift": [num(v, 6) for v in resumo2["menor_lift"]],
    "Maior lift": [num(v, 6) for v in resumo2["maior_lift"]],
})

t2b = pd.DataFrame({
    "Métrica": top10["metrica"],
    "Hashtag": top10["hashtag"],
    "n com": [num(v, 0) for v in top10["n_com"]],
    "n sem": [num(v, 0) for v in top10["n_sem"]],
    "Lift": [num(v, 6) for v in top10["lift"]],
    "p-valor": [num(v, 6) for v in top10["p_valor"]],
    "q-valor (BH)": [num(v, 6) for v in top10["q_valor"]],
})

t3a = pd.DataFrame({
    "Variável": resumo3["variavel"],
    "Métrica": resumo3["metrica"],
    "Segmento do maior efeito": resumo3["segmento"],
    "n": [num(v, 0) for v in resumo3["n"]],
    "Efeito máx. plausível (%)": [num(v, 4) for v in resumo3["efeito_maximo_plausivel_pct"]],
    "Efeito máx. absoluto": [num(v, 4) for v in resumo3["efeito_maximo_absoluto"]],
    "Unidade": resumo3["unidade"],
})

t3b = pd.DataFrame({
    "Métrica": maior_base["metrica"],
    "Variável": maior_base["variavel"],
    "Segmento": maior_base["segmento"],
    "n": [num(v, 0) for v in maior_base["n"]],
    "Efeito máx. plausível (%)": [num(v, 4) for v in maior_base["efeito_maximo_plausivel_pct"]],
    "Efeito máx. absoluto": [num(v, 4) for v in maior_base["efeito_maximo_absoluto"]],
    "Unidade": maior_base["unidade"],
})

piv = item4.pivot(index=["cv_rotulo", "cv_valor"], columns="lift_pct",
                  values="n_por_variante").reset_index()
t4 = pd.DataFrame({
    "CV (rótulo)": piv["cv_rotulo"].str.replace("cenario", "cenário", regex=False)
                                   .str.replace("CV = 0.", "CV = 0,", regex=False)
                                   .str.replace("CV = 1.0", "CV = 1,0", regex=False),
    "CV (valor)": [num(v, 6) for v in piv["cv_valor"]],
    **{f"lift {num(l, 0)}%": [num(v, 0) for v in piv[l]] for l in [5.0, 10.0, 20.0, 40.0]},
})

n_sig_bh = int(resumo2["significativas_apos_bh"].sum())
n_sig_bruto = int(resumo2["p_menor_005_sem_correcao"].sum())
n_test_total = int(resumo2["hashtags_testadas"].sum())

md = f"""# OS-04 — Complementos

Script: `solution/analysis/os04_complementos.py`
Fonte: `datasets/social_media_dataset.csv` ({num(N, 0)} posts)
Saídas: `solution/outputs/os04/` (4 arquivos .csv)

**Regras mantidas:** `engajamento` = likes + shares + comments_count; `taxa_engajamento` = engajamento / views; faixas de seguidores até 50K, 50–100K, 100–500K, 500K–1M; seed 42.

| Arquivo | Conteúdo |
|---|---|
| `item1_sanidade.csv` | os {num(len(item1), 0)} indicadores de sanidade (indicador, valor) |
| `item2_hashtags.csv` | as {num(len(testaveis), 0)} hashtags testadas × 2 métricas, com lift, p-valor e q-valor BH ({num(len(item2), 0)} linhas) |
| `item3_efeito_absoluto.csv` | efeito máximo plausível em % e em unidades absolutas ({num(len(item3), 0)} linhas) |
| `item4_tamanho_amostra.csv` | n por variante para 6 CV × 4 lifts ({num(len(item4), 0)} linhas) |

---

## 1. Tabela de sanidade

{tabela_md(t1, ["indicador", "valor"])}

---

## 2. Hashtags com correção de testes múltiplos

**Universo:** {num(N_UNI, 0)} posts com `hashtags` preenchido ({num(100 * N_UNI / N, 2)}% da base); {num(N - N_UNI, 0)} posts com nulo ficaram fora. {num(len(cont_tags), 0)} hashtags distintas, {num(len(testaveis), 0)} com n ≥ {MIN_POSTS_HASHTAG}. Comparação: posts com a hashtag × posts do universo sem a hashtag; teste t de Welch; correção de Benjamini-Hochberg com FDR de 5% aplicada separadamente por métrica.

### Resumo por métrica

{tabela_md(t2a)}

### 10 hashtags de maior lift em cada métrica

{tabela_md(t2b)}

---

## 3. Efeito máximo em valores absolutos

Entrada: `solution/outputs/os03c/bloco1_equivalencia.csv` ({num(len(b1), 0)} linhas). Conversão: efeito máximo plausível (%) ÷ 100 × média da base da métrica. Médias usadas: engajamento = {num(MEDIA_ENG, 4)} interações por post; shares = {num(MEDIA_SHARES, 4)}; comments_count = {num(MEDIA_COMMENTS, 4)}.

### Resumo por variável (maior efeito de cada variável × métrica)

{tabela_md(t3a)}

### Maior valor da base inteira, por métrica

{tabela_md(t3b)}

---

## 4. Tamanho de amostra para testes futuros

Fórmula da OS: `n por variante = 2 × (1,96 + 0,84)² × CV² ÷ lift²` (poder 80%, significância 5% bicaudal, duas variantes). Arredondado para cima.

{tabela_md(t4)}

---

## Pontos suspeitos ou problemas encontrados

1. **Views e engajamento quase constantes.** Views vão de {num(df["views"].min(), 0)} a {num(df["views"].max(), 0)} (amplitude de {num(df["views"].max() - df["views"].min(), 0)} em torno de uma média de {num(df["views"].mean(), 1)}) e o engajamento de {num(df["engajamento"].min(), 0)} a {num(df["engajamento"].max(), 0)}. O engajamento no percentil 1 é {num(p1_eng / med_eng, 6)} da mediana e **{num(100 * (df["engajamento"] < 0.10 * med_eng).mean(), 4)}%** dos posts ficam abaixo de 10% da mediana.
2. **Variância ÷ média colada em 1 nas quatro métricas** (views {num(df["views"].var(ddof=1) / df["views"].mean(), 6)}; likes {num(df["likes"].var(ddof=1) / df["likes"].mean(), 6)}; shares {num(df["shares"].var(ddof=1) / df["shares"].mean(), 6)}; comments_count {num(df["comments_count"].var(ddof=1) / df["comments_count"].mean(), 6)} — todas entre {num(min(df[m].var(ddof=1) / df[m].mean() for m in ["views", "likes", "shares", "comments_count"]), 4)} e {num(max(df[m].var(ddof=1) / df[m].mean() for m in ["views", "likes", "shares", "comments_count"]), 4)}). O valor 1 é o de uma Poisson; em métricas de redes sociais esse índice costuma ser muito maior que 1.
3. **Likes e views sem correlação** (Pearson {num(stats.pearsonr(df["likes"], df["views"])[0], 6)}, Spearman {num(stats.spearmanr(df["likes"], df["views"])[0], 6)}); **log10(follower_count) e log10(views) também** ({num(stats.pearsonr(log_seg, log_views)[0], 6)}). As medianas de views nas quatro faixas de seguidores são praticamente iguais.
4. **`sponsor_name` tem {num(patro["sponsor_name"].nunique(), 0)} valores distintos em {num(len(patro), 0)} posts patrocinados** — quase um patrocinador por post.
5. **Hashtags: {num(n_sig_bruto, 0)} resultados com p < 0,05 sem correção em {num(n_test_total, 0)} testes, contra {num(resumo2["esperadas_por_acaso"].sum(), 1)} esperados por acaso; após a correção BH sobram {num(n_sig_bh, 0)}.** Os lifts extremos ficam entre {num(item2["lift"].min(), 6)} e {num(item2["lift"].max(), 6)}.
6. **Efeito máximo plausível em unidades absolutas, no pior caso de cada métrica:** {"; ".join(f"{r.metrica} = {num(r.efeito_maximo_absoluto, 4)} {r.unidade} sobre uma média de {num(MEDIA_POR_METRICA[r.metrica], 4)}" for r in maior_base.itertuples())}.
7. **Os CV da base são muito baixos** ({num(df["engajamento"].std(ddof=1) / df["engajamento"].mean(), 6)} para engajamento; {num(df["shares"].std(ddof=1) / df["shares"].mean(), 6)} para shares; {num(df["comments_count"].std(ddof=1) / df["comments_count"].mean(), 6)} para comments_count), então o n por variante do item 4 fica em poucas unidades com esses CV, contra centenas ou milhares nos cenários fixos de 0,5 a 1,0.
8. **Faixas de seguidores desbalanceadas:** 50–100K e até 50K têm {num(int((df["faixa_seguidores"] == "50-100K").sum()), 0)} e {num(int((df["faixa_seguidores"] == "ate 50K").sum()), 0)} posts, contra {num(int((df["faixa_seguidores"] == "500K-1M").sum()), 0)} em 500K–1M.
9. **Indicadores 8 e 9 dão exatamente {num(100 * (por_creator["n_plat"] == 1).mean(), 4)}% e {num(100 * (por_creator["n_seg"] == 1).mean(), 4)}%** sobre {num(N_CREATORS, 0)} creators: nenhum creator está restrito a uma plataforma e nenhum tem `follower_count` constante. Todos os {num(N_CREATORS, 0)} creators têm mais de 1 post ({num(int(por_creator["n_posts"].min()), 0)} a {num(int(por_creator["n_posts"].max()), 0)} posts), aparecem em {num(int(por_creator["n_plat"].min()), 0)} a {num(int(por_creator["n_plat"].max()), 0)} plataformas e têm {num(int(por_creator["n_seg"].min()), 0)} a {num(int(por_creator["n_seg"].max()), 0)} valores distintos de `follower_count`.
"""

(OUT_DIR / "resumo_os04.md").write_text(md, encoding="utf-8")
print(f"  -> resumo_os04.md")
print(f"\nPronto. Saidas em {OUT_DIR}")
