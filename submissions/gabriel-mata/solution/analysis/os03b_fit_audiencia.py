"""OS-03b - Fit patrocinador x conteudo (Parte A) e perfis de audiencia (Parte B).
Logica de lift/IC/metades/teste contra o acaso replicada das OS-02 e OS-03."""

import os
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_BOOT = 1000
N_PERM = 200
MIN_SEG = 100   # n minimo por segmento (B1 e B2)
MIN_G = 20      # n minimo de cada grupo dentro do estrato (A2 e B3)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os03b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS = ["taxa_engajamento", "shares", "comments_count"]

# mesmas faixas da OS-02: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

# fit sponsor_category -> content_category
FIT = {
    "cosmetics": "beauty",
    "electronics": "tech",
    "gaming": "tech",
    "fashion": "lifestyle",
    "food": "lifestyle",
    "travel": "lifestyle",
}

COLS_SEG = ["variaveis", "segmento", "metrica", "n", "lift", "ic_inferior", "ic_superior",
            "ic_exclui_1", "lift_metade_A", "lift_metade_B", "mesmo_lado_nas_duas_metades"]

VARS_AUD = ["audience_age_distribution", "audience_gender_distribution", "audience_location"]


def salvar(df, nome):
    df.to_csv(OUT_DIR / nome, index=False)
    print(f"  -> {nome} ({len(df)} linhas)")


# ---------------------------------------------------------------- carga e derivadas
df = pd.read_csv(DATA_PATH)
df["post_date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p")
df["engajamento"] = df["likes"] + df["shares"] + df["comments_count"]
df["taxa_engajamento"] = df["engajamento"] / df["views"]
df["faixa_seguidores"] = pd.cut(df["follower_count"], bins=FAIXA_SEG_BINS,
                                labels=FAIXA_SEG_LABELS, right=True).astype(str)
df["is_sponsored"] = df["is_sponsored"].astype(bool)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

eh_spon = df["is_sponsored"].to_numpy()
VAL = {m: df[m].to_numpy(dtype=float) for m in METRICAS}

# fit: so faz sentido em post patrocinado
df["fit"] = np.where(
    eh_spon,
    np.where(df["sponsor_category"].map(FIT).to_numpy() == df["content_category"].to_numpy(),
             "sim", "nao"),
    "nao se aplica")
eh_fit = (df["fit"] == "sim").to_numpy()

# mesma divisao em duas metades da OS-02: primeiro uso de um default_rng(42)
rng_split = np.random.default_rng(SEED)
metade = np.full(N, "B", dtype="<U1")
metade[rng_split.permutation(N)[: N // 2]] = "A"
eh_A = metade == "A"
print(f"Metades: A={eh_A.sum()}, B={(~eh_A).sum()}")

rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- helpers de segmento
def codigos(frame, cols):
    """Rotulos de grupo (int) e nomes dos segmentos para um conjunto de colunas."""
    chave = frame[cols[0]].astype(str) if len(cols) == 1 else \
        frame[cols].astype(str).agg(" | ".join, axis=1)
    cod, nomes = pd.factorize(chave, sort=True)
    return cod, list(nomes)


def medias_por_grupo(valores, cod, k):
    soma = np.bincount(cod, weights=valores, minlength=k)
    cont = np.bincount(cod, minlength=k)
    with np.errstate(invalid="ignore", divide="ignore"):
        return soma / cont, cont


def indice_por_plataforma(frame):
    """Indice por post: valor / media da metrica na plataforma do post (dentro do frame)."""
    idx = {}
    for m in METRICAS:
        media_plat = frame.groupby("platform")[m].transform("mean")
        idx[m] = (frame[m] / media_plat).to_numpy()
    return idx


def bootstrap_ics(idx, pos, B=N_BOOT, chunk=250):
    """IC 95% percentil do lift, para as 3 metricas, reusando as mesmas reamostragens."""
    n = len(pos)
    vals = {m: idx[m][pos] for m in METRICAS}
    acum = {m: [] for m in METRICAS}
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        amostra = rng.integers(0, n, size=(b, n))
        for m in METRICAS:
            acum[m].append(vals[m][amostra].mean(axis=1))
        feitos += b
    return {m: np.percentile(np.concatenate(a), [2.5, 97.5]) for m, a in acum.items()}


def tabela_segmentos(frame, conjuntos, idx, A_sub, min_n):
    """Lift, IC e teste de repeticao de cada segmento. Retorna (tabela, cobertura, specs)."""
    linhas, cobertura, specs = [], [], []
    for cols in conjuntos:
        nome_vars = " x ".join(cols)
        cod, nomes = codigos(frame, cols)
        k = len(nomes)
        cont = np.bincount(cod, minlength=k)
        valido = cont >= min_n if min_n else np.ones(k, dtype=bool)
        cobertura.append({"variaveis": nome_vars, "segmentos_existentes": k,
                          "segmentos_mantidos": int(valido.sum()),
                          "segmentos_fora": int((~valido).sum()),
                          "posts_fora": int(cont[~valido].sum())})
        specs.append((nome_vars, cod, k, valido))

        for g in np.flatnonzero(valido):
            pos = np.flatnonzero(cod == g)
            pos_A, pos_B = pos[A_sub[pos]], pos[~A_sub[pos]]
            ics = bootstrap_ics(idx, pos)
            for m in METRICAS:
                lift = idx[m][pos].mean()
                lo, hi = ics[m]
                lA = idx[m][pos_A].mean() if len(pos_A) else np.nan
                lB = idx[m][pos_B].mean() if len(pos_B) else np.nan
                mesmo = (lA > 1 and lB > 1) or (lA < 1 and lB < 1)
                linhas.append({
                    "variaveis": nome_vars, "segmento": nomes[g], "metrica": m, "n": len(pos),
                    "lift": round(lift, 6),
                    "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                    "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
                    "lift_metade_A": round(lA, 6), "lift_metade_B": round(lB, 6),
                    "mesmo_lado_nas_duas_metades": "sim" if mesmo else "nao",
                })
    return pd.DataFrame(linhas, columns=COLS_SEG), cobertura, specs


def teste_acaso(conjunto, specs, idx, plat_pos, cobertura):
    """Embaralha o indice dentro de cada plataforma e guarda o maior/menor lift do conjunto."""
    obs = {m: [] for m in METRICAS}
    for _, cod, k, valido in specs:
        for m in METRICAS:
            med, _ = medias_por_grupo(idx[m], cod, k)
            obs[m].append(med[valido])

    maiores = {m: np.empty(N_PERM) for m in METRICAS}
    menores = {m: np.empty(N_PERM) for m in METRICAS}
    for r in range(N_PERM):
        for m in METRICAS:
            v = idx[m].copy()
            for pos in plat_pos:
                v[pos] = idx[m][rng.permutation(pos)]
            todos = []
            for _, cod, k, valido in specs:
                med, _ = medias_por_grupo(v, cod, k)
                todos.append(med[valido])
            todos = np.concatenate(todos)
            maiores[m][r] = todos.max()
            menores[m][r] = todos.min()

    existentes = sum(c["segmentos_existentes"] for c in cobertura)
    fora = sum(c["segmentos_fora"] for c in cobertura)
    posts_fora = sum(c["posts_fora"] for c in cobertura)
    linhas = []
    for m in METRICAS:
        o = np.concatenate(obs[m])
        p95 = np.percentile(maiores[m], 95)
        p5 = np.percentile(menores[m], 5)
        linhas.append({
            "conjunto": conjunto, "metrica": m,
            "segmentos_existentes": existentes,
            "segmentos_avaliados": len(o),
            "segmentos_fora_por_n_minimo": fora,
            "posts_fora_por_n_minimo": posts_fora,
            "maior_lift_observado": round(o.max(), 6),
            "acaso_p95_dos_maiores": round(p95, 6),
            "maior_observado_acima_do_acaso": "sim" if o.max() > p95 else "nao",
            "menor_lift_observado": round(o.min(), 6),
            "acaso_p5_dos_menores": round(p5, 6),
            "menor_observado_abaixo_do_acaso": "sim" if o.min() < p5 else "nao",
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- helpers de estratos
def chave_estrato(cols):
    return df[cols].astype(str).agg(" | ".join, axis=1).to_numpy()


def monta_estratos(pos_base, cols, grupo, min_g):
    """(estratos_existentes, [(nome, pos_grupo1, pos_grupo0)]) com n minimo nos 2 grupos."""
    chave = chave_estrato(cols)[pos_base]
    g = grupo[pos_base]
    nomes = np.unique(chave)
    estratos = []
    for nm in nomes:
        m = chave == nm
        p1, p0 = pos_base[m & g], pos_base[m & ~g]
        if len(p1) >= min_g and len(p0) >= min_g:
            estratos.append((nm, p1, p0))
    return len(nomes), estratos


def efeito(estratos, v):
    """Media das razoes (grupo1/grupo0) ponderada pelo tamanho do estrato."""
    razoes = np.array([v[p1].mean() / v[p0].mean() for _, p1, p0 in estratos])
    tam = np.array([len(p1) + len(p0) for _, p1, p0 in estratos], dtype=float)
    return np.average(razoes, weights=tam), razoes, tam


def efeito_na_metade(estratos, v, mask):
    """Mesmo efeito, restrito a uma metade. Estratos sem os dois grupos ficam de fora."""
    razoes, tam = [], []
    for _, p1, p0 in estratos:
        a, b = p1[mask[p1]], p0[mask[p0]]
        if len(a) and len(b):
            razoes.append(v[a].mean() / v[b].mean())
            tam.append(len(a) + len(b))
    if not razoes:
        return np.nan
    return np.average(razoes, weights=np.array(tam, dtype=float))


def boot_efeito(estratos, B=N_BOOT):
    """IC 95% percentil por bootstrap estratificado: reamostra dentro de cada estrato e grupo."""
    tam = np.array([len(p1) + len(p0) for _, p1, p0 in estratos], dtype=float)
    peso = tam / tam.sum()
    acum = {m: np.zeros(B) for m in METRICAS}
    for i, (_, p1, p0) in enumerate(estratos):
        n1, n0 = len(p1), len(p0)
        amo1 = rng.integers(0, n1, size=(B, n1))
        amo0 = rng.integers(0, n0, size=(B, n0))
        for m in METRICAS:
            v1, v0 = VAL[m][p1], VAL[m][p0]
            acum[m] += peso[i] * (v1[amo1].mean(axis=1) / v0[amo0].mean(axis=1))
    return {m: np.percentile(a, [2.5, 97.5]) for m, a in acum.items()}


acaso = []

# ================================================================ PARTE A
pos_spon = np.flatnonzero(eh_spon)
spon = df.loc[eh_spon].reset_index(drop=True)
A_spon = eh_A[pos_spon]
fit_spon = eh_fit[pos_spon]
N_SPON = len(spon)
print(f"\nPatrocinados: {N_SPON} (com fit={fit_spon.sum()}, sem fit={(~fit_spon).sum()})")

# ---------------------------------------------------------------- A1
print("\n[A1] Volume com e sem fit")
linhas = [{
    "escopo": "total", "content_category": "todas",
    "n_patrocinado": N_SPON,
    "n_com_fit": int(fit_spon.sum()),
    "n_sem_fit": int((~fit_spon).sum()),
    "pct_com_fit": round(100 * fit_spon.mean(), 4),
    "pct_sem_fit": round(100 * (~fit_spon).mean(), 4),
}]
for cat in sorted(spon["content_category"].unique()):
    m = (spon["content_category"] == cat).to_numpy()
    linhas.append({
        "escopo": "content_category", "content_category": cat,
        "n_patrocinado": int(m.sum()),
        "n_com_fit": int((m & fit_spon).sum()),
        "n_sem_fit": int((m & ~fit_spon).sum()),
        "pct_com_fit": round(100 * (m & fit_spon).sum() / m.sum(), 4),
        "pct_sem_fit": round(100 * (m & ~fit_spon).sum() / m.sum(), 4),
    })
a1 = pd.DataFrame(linhas)
salvar(a1, "a1_volume_fit.csv")

# ---------------------------------------------------------------- A2
print("\n[A2] Fit vs. sem fit (estratificado)")
COLS_A2 = ["platform", "content_category", "faixa_seguidores"]
exist_a2, estratos_a2 = monta_estratos(pos_spon, COLS_A2, eh_fit, MIN_G)
usados_a2 = np.concatenate([np.concatenate([p1, p0]) for _, p1, p0 in estratos_a2])
n_fit_uso = sum(len(p1) for _, p1, _ in estratos_a2)
n_nofit_uso = sum(len(p0) for _, _, p0 in estratos_a2)
print(f"  estratos existentes={exist_a2}, usados={len(estratos_a2)}, "
      f"posts usados={len(usados_a2)}, fora={N_SPON - len(usados_a2)}")

ics_a2 = boot_efeito(estratos_a2)
linhas = []
for m in METRICAS:
    ef, razoes, _ = efeito(estratos_a2, VAL[m])
    lo, hi = ics_a2[m]
    simples = VAL[m][pos_spon][fit_spon].mean() / VAL[m][pos_spon][~fit_spon].mean()
    linhas.append({
        "metrica": m,
        "estratos_existentes": exist_a2,
        "estratos_usados": len(estratos_a2),
        "estratos_fora": exist_a2 - len(estratos_a2),
        "posts_base_patrocinados": N_SPON,
        "posts_usados": len(usados_a2),
        "posts_fora": N_SPON - len(usados_a2),
        "n_com_fit_usado": n_fit_uso,
        "n_sem_fit_usado": n_nofit_uso,
        "efeito_geral": round(ef, 6),
        "ic_inferior": round(lo, 6),
        "ic_superior": round(hi, 6),
        "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
        "efeito_metade_A": round(efeito_na_metade(estratos_a2, VAL[m], eh_A), 6),
        "efeito_metade_B": round(efeito_na_metade(estratos_a2, VAL[m], ~eh_A), 6),
        "pct_estratos_razao_maior_1": round(100 * (razoes > 1).mean(), 2),
        "razao_minimo": round(razoes.min(), 6),
        "razao_mediana": round(np.median(razoes), 6),
        "razao_maximo": round(razoes.max(), 6),
        "comparacao_simples_sem_estratos": round(simples, 6),
    })
a2 = pd.DataFrame(linhas)
salvar(a2, "a2_fit_vs_sem_fit.csv")

# ---------------------------------------------------------------- A3
print("\n[A3] sponsor_category x content_category")
IDX_SPON = indice_por_plataforma(spon)
plat_pos_spon = [np.flatnonzero((spon["platform"] == p).to_numpy())
                 for p in sorted(spon["platform"].unique())]
a3, cob_a3, specs_a3 = tabela_segmentos(
    spon, [["sponsor_category", "content_category"]], IDX_SPON, A_spon, 0)
a3.insert(3, "tem_fit", [
    "sim" if FIT.get(s.split(" | ")[0]) == s.split(" | ")[1] else "nao"
    for s in a3["segmento"]])
salvar(a3, "a3_sponsor_x_content.csv")
print(f"  teste contra o acaso ({N_PERM} permutacoes)")
acaso.append(teste_acaso("A3 sponsor_category x content_category (so patrocinados)",
                         specs_a3, IDX_SPON, plat_pos_spon, cob_a3))

# ================================================================ PARTE B
IDX = indice_por_plataforma(df)
plat_pos = [np.flatnonzero((df["platform"] == p).to_numpy())
            for p in sorted(df["platform"].unique())]

# ---------------------------------------------------------------- B1
print("\n[B1] Personas (idade x genero x local)")
b1, cob_b1, specs_b1 = tabela_segmentos(df, [VARS_AUD], IDX, eh_A, MIN_SEG)
print(f"  {cob_b1[0]}")
salvar(b1, "b1_personas.csv")
print(f"  teste contra o acaso ({N_PERM} permutacoes)")
acaso.append(teste_acaso("B1 personas (idade x genero x local)",
                         specs_b1, IDX, plat_pos, cob_b1))

# ---------------------------------------------------------------- B2
print("\n[B2] Audiencia x conteudo")
b2_tabs, cob_b2 = [], []
for var in VARS_AUD:
    cols = ["content_category", var]
    tab, cob, specs = tabela_segmentos(df, [cols], IDX, eh_A, MIN_SEG)
    print(f"  {cob[0]}")
    b2_tabs.append(tab)
    cob_b2.extend(cob)
    acaso.append(teste_acaso("B2 " + " x ".join(cols), specs, IDX, plat_pos, cob))
b2 = pd.concat(b2_tabs, ignore_index=True)
salvar(b2, "b2_audiencia_x_conteudo.csv")

# ---------------------------------------------------------------- B3
print("\n[B3] Audiencia x patrocinio")
COLS_B3 = ["platform", "content_category"]
COLS_SAIDA_B3 = ["variavel", "valor", "metrica", "n_patrocinado", "n_organico",
                 "estratos_usados", "efeito", "ic_inferior", "ic_superior", "ic_exclui_1",
                 "efeito_metade_A", "efeito_metade_B"]
linhas = []
for var in VARS_AUD:
    for valor in sorted(df[var].astype(str).unique()):
        pos_v = np.flatnonzero((df[var].astype(str) == valor).to_numpy())
        _, estratos = monta_estratos(pos_v, COLS_B3, eh_spon, MIN_G)
        ics = boot_efeito(estratos)
        for m in METRICAS:
            ef, _, _ = efeito(estratos, VAL[m])
            lo, hi = ics[m]
            linhas.append({
                "variavel": var, "valor": valor, "metrica": m,
                "n_patrocinado": int(eh_spon[pos_v].sum()),
                "n_organico": int((~eh_spon[pos_v]).sum()),
                "estratos_usados": len(estratos),
                "efeito": round(ef, 6),
                "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
                "efeito_metade_A": round(efeito_na_metade(estratos, VAL[m], eh_A), 6),
                "efeito_metade_B": round(efeito_na_metade(estratos, VAL[m], ~eh_A), 6),
            })
b3 = pd.DataFrame(linhas, columns=COLS_SAIDA_B3)
salvar(b3, "b3_audiencia_x_patrocinio.csv")

tab_acaso = pd.concat(acaso, ignore_index=True)
salvar(tab_acaso, "testes_acaso.csv")


# ---------------------------------------------------------------- distribuicao dos lifts
def distribuicao(tab, conjunto):
    linhas = []
    for m in METRICAS:
        sub = tab[tab["metrica"] == m]
        s = sub["lift"]
        linhas.append({
            "conjunto": conjunto, "metrica": m, "segmentos": len(s),
            "minimo": round(s.min(), 6), "p5": round(s.quantile(0.05), 6),
            "mediana": round(s.median(), 6), "p95": round(s.quantile(0.95), 6),
            "maximo": round(s.max(), 6),
            "acima_1_03": int((s > 1.03).sum()),
            "acima_1_05": int((s > 1.05).sum()),
            "acima_1_10": int((s > 1.10).sum()),
            "abaixo_0_97": int((s < 0.97).sum()),
            "abaixo_0_95": int((s < 0.95).sum()),
            "abaixo_0_90": int((s < 0.90).sum()),
            "ic_exclui_1_sim": int((sub["ic_exclui_1"] == "sim").sum()),
            "mesmo_lado_sim": int((sub["mesmo_lado_nas_duas_metades"] == "sim").sum()),
        })
    return pd.DataFrame(linhas)


conjuntos_b = [("B1 personas (idade x genero x local)", b1)]
for var in VARS_AUD:
    nome = f"content_category x {var}"
    conjuntos_b.append(("B2 " + nome, b2[b2["variaveis"] == nome]))
dist_b = pd.concat([distribuicao(t, c) for c, t in conjuntos_b], ignore_index=True)


# ---------------------------------------------------------------- resumo
def md(tabela):
    # o separador dos segmentos (" | ") colide com o pipe da tabela markdown
    def cel(v):
        return "" if pd.isna(v) else str(v).replace("|", "\\|")

    cols = list(tabela.columns)
    linhas = ["| " + " | ".join(cols) + " |",
              "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in tabela.iterrows():
        linhas.append("| " + " | ".join(cel(v) for v in r) + " |")
    return "\n".join(linhas)


def top_bottom(tab, k=10):
    t = tab[tab["metrica"] == "taxa_engajamento"].sort_values("lift", ascending=False)
    maiores = t.head(k).copy()
    menores = t.tail(k)[::-1].copy()
    cols = ["segmento", "n", "lift", "ic_inferior", "ic_superior", "ic_exclui_1",
            "lift_metade_A", "lift_metade_B", "mesmo_lado_nas_duas_metades"]
    return maiores[cols], menores[cols]


L = []
L.append("# OS-03b - Fit de patrocinio e audiencia\n")
L.append(f"Base: {N} posts. Patrocinados: {N_SPON} "
         f"(com fit: {int(fit_spon.sum())}; sem fit: {int((~fit_spon).sum())}). "
         f"Metades: A={int(eh_A.sum())}, B={int((~eh_A).sum())}.\n")
L.append("Metricas: `taxa_engajamento`, `shares`, `comments_count`. "
         "Indice por post = valor / media da metrica na plataforma do post. "
         "Lift = media do indice no segmento. IC 95% por bootstrap percentil "
         f"({N_BOOT} reamostragens). Teste contra o acaso: {N_PERM} permutacoes. Seed {SEED}.\n")

L.append("\n## Parte A - Fit patrocinador x conteudo (so posts patrocinados)\n")
L.append("### A1. Volume com e sem fit\n")
L.append(md(a1))
L.append("\n### A2. Comparacao fit vs. sem fit (estratos platform x content_category x "
         f"faixa_seguidores, minimo de {MIN_G} posts em cada grupo)\n")
L.append("Efeito = media das razoes (media com fit / media sem fit) ponderada pelo tamanho "
         "do estrato.\n")
L.append(md(a2))
L.append("\n### A3. sponsor_category x content_category (18 combinacoes)\n")
L.append("Lift com referencia na media dos posts patrocinados da plataforma.\n")
L.append(md(a3))

L.append("\n## Parte B - Audiencia (todos os posts)\n")
L.append("### B1 e B2 - cobertura dos conjuntos\n")
L.append(md(pd.DataFrame(cob_b1 + cob_b2)))
L.append(f"\nSegmentos com n < {MIN_SEG} ficaram de fora.\n")
L.append("\n### B1 e B2 - distribuicao dos lifts por conjunto e metrica\n")
L.append(md(dist_b))
for conjunto, tab in conjuntos_b:
    maiores, menores = top_bottom(tab)
    L.append(f"\n### {conjunto} - 10 maiores lifts de taxa_engajamento\n")
    L.append(md(maiores))
    L.append(f"\n### {conjunto} - 10 menores lifts de taxa_engajamento\n")
    L.append(md(menores))

L.append("\n### B3. Audiencia x patrocinio (estratos platform x content_category, "
         f"minimo de {MIN_G} patrocinados e {MIN_G} organicos)\n")
L.append("Efeito = media das razoes (media patrocinado / media organico) ponderada pelo "
         "tamanho do estrato.\n")
L.append(md(b3))

L.append("\n## Testes contra o acaso\n")
L.append(md(tab_acaso))

L.append("\n## Pontos suspeitos ou problemas encontrados\n")
sus = []
sus.append(f"- `sponsor_category` esta praticamente uniforme dentro de cada "
           f"`content_category`, entao a proporcao de posts com fit e definida pela regra da "
           f"tabela de fit, nao pelos dados: "
           + "; ".join(f"{r.content_category} {r.pct_com_fit}%"
                       for r in a1[a1['escopo'] == 'content_category'].itertuples())
           + ".")
sus.append(f"- A2 deixou {exist_a2 - len(estratos_a2)} de {exist_a2} estratos de fora "
           f"({N_SPON - len(usados_a2)} posts patrocinados, "
           f"{round(100 * (N_SPON - len(usados_a2)) / N_SPON, 2)}%) por nao atingirem "
           f"{MIN_G} posts em um dos grupos; as faixas 'ate 50K' e '50-100K' tem poucos posts.")
fora_b = [c for c in (cob_b1 + cob_b2) if c["segmentos_fora"] > 0]
if fora_b:
    sus.append("- Conjuntos de B com segmentos abaixo do n minimo: "
               + "; ".join(f"{c['variaveis']} ({c['segmentos_fora']} de "
                           f"{c['segmentos_existentes']}, {c['posts_fora']} posts)"
                           for c in fora_b) + ".")
else:
    sus.append(f"- Nenhum segmento de B1 ou B2 ficou abaixo de n = {MIN_SEG}.")
ic_sim = tab_acaso[(tab_acaso["maior_observado_acima_do_acaso"] == "sim") |
                   (tab_acaso["menor_observado_abaixo_do_acaso"] == "sim")]
if len(ic_sim):
    sus.append("- Extremos fora da faixa do acaso: "
               + "; ".join(f"{r.conjunto} / {r.metrica}" for r in ic_sim.itertuples()) + ".")
else:
    sus.append("- Nenhum extremo observado ficou fora da faixa do acaso em nenhum conjunto.")
pequenos = [c for c, t in conjuntos_b
            if len(t[t["metrica"] == "taxa_engajamento"]) < 20]
if pequenos:
    sus.append("- Conjuntos com menos de 20 segmentos: as listas dos 10 maiores e dos 10 "
               "menores lifts se sobrepoem (" + "; ".join(pequenos) + ").")
n_ic = int((pd.concat([a3, b1, b2])["ic_exclui_1"] == "sim").sum())
n_tot = len(pd.concat([a3, b1, b2]))
sus.append(f"- Linhas com IC que exclui 1 nas tabelas de segmentos (A3, B1, B2): "
           f"{n_ic} de {n_tot}.")
L.extend(sus)
L.append("")

(OUT_DIR / "resumo_os03b.md").write_text("\n".join(L), encoding="utf-8")
print(f"  -> resumo_os03b.md")
print(f"\nPronto. Saidas em {OUT_DIR}")
