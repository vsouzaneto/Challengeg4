"""OS-06 - Lacunas finais: alcance (views patrocinado vs. organico) e
formato x audiencia (content_type x variaveis de audiencia)."""

import os
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_BOOT = 1000
N_PERM = 200
MIN_1B = 30
MIN_1C = 20
MIN_N_P2 = 100

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os06"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS_P2 = ["taxa_engajamento", "shares", "comments_count"]

# faixas de seguidores mantidas: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

CONJUNTOS_P2 = [
    ["content_type", "audience_age_distribution"],
    ["content_type", "audience_gender_distribution"],
    ["content_type", "audience_location"],
]

COLS_P2 = ["variaveis", "segmento", "metrica", "n", "lift", "ic_inferior", "ic_superior",
           "ic_exclui_1", "lift_metade_A", "lift_metade_B", "mesmo_lado_nas_duas_metades"]


def salvar(df, nome):
    df.to_csv(OUT_DIR / nome, index=False)
    print(f"  -> {nome} ({len(df)} linhas)")


def num(x, dec=4):
    """Numero no formato pt-BR para as tabelas do resumo."""
    if isinstance(x, str):
        return x
    if pd.isna(x):
        return "-"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def tabela_md(df, cols=None):
    cols = list(df.columns) if cols is None else cols
    linhas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        # o separador de segmentos usa pipe; escapar para nao quebrar a tabela markdown
        linhas.append("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in cols) + " |")
    return "\n".join(linhas)


# ---------------------------------------------------------------- carga e derivadas
df = pd.read_csv(DATA_PATH)
df["engajamento"] = df["likes"] + df["shares"] + df["comments_count"]
df["taxa_engajamento"] = df["engajamento"] / df["views"]
df["faixa_seguidores"] = pd.cut(df["follower_count"], bins=FAIXA_SEG_BINS,
                                labels=FAIXA_SEG_LABELS, right=True).astype(str)
df["is_sponsored"] = df["is_sponsored"].astype(bool)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

eh_spon = df["is_sponsored"].to_numpy()
VIEWS = df["views"].to_numpy(dtype=float)

# mesma divisao em duas metades da OS-02: primeiro uso de um default_rng(42)
rng_split = np.random.default_rng(SEED)
metade = np.full(N, "B", dtype="<U1")
metade[rng_split.permutation(N)[: N // 2]] = "A"
eh_A = metade == "A"
print(f"Metades: A={eh_A.sum()}, B={(~eh_A).sum()}")

rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- helpers
def boot_media(v, B=N_BOOT, chunk=250):
    """IC 95% percentil da media de um vetor."""
    n = len(v)
    out = np.empty(B)
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        out[feitos:feitos + b] = v[rng.integers(0, n, size=(b, n))].mean(axis=1)
        feitos += b
    return np.percentile(out, [2.5, 97.5])


def monta_estratos(pos_base, cols, min_g):
    """(estratos_existentes, [(nome, pos_patrocinado, pos_organico)]) com n minimo nos 2 grupos."""
    chave = df[cols].astype(str).agg(" | ".join, axis=1).to_numpy()[pos_base]
    spon = eh_spon[pos_base]
    nomes = np.unique(chave)
    estratos = []
    for nm in nomes:
        m = chave == nm
        ps, po = pos_base[m & spon], pos_base[m & ~spon]
        if len(ps) >= min_g and len(po) >= min_g:
            estratos.append((nm, ps, po))
    return len(nomes), estratos


def efeito(estratos, v):
    """Media das razoes (patrocinado/organico) ponderada pelo tamanho do estrato."""
    razoes = np.array([v[ps].mean() / v[po].mean() for _, ps, po in estratos])
    tam = np.array([len(ps) + len(po) for _, ps, po in estratos], dtype=float)
    return np.average(razoes, weights=tam), razoes, tam


def efeito_na_metade(estratos, v, mask):
    """Mesmo efeito, restrito a uma metade. Estratos sem os dois grupos ficam de fora."""
    razoes, tam = [], []
    for _, ps, po in estratos:
        a, b = ps[mask[ps]], po[mask[po]]
        if len(a) and len(b):
            razoes.append(v[a].mean() / v[b].mean())
            tam.append(len(a) + len(b))
    if not razoes:
        return np.nan
    return np.average(razoes, weights=np.array(tam, dtype=float))


def boot_efeito(estratos, v, B=N_BOOT):
    """IC 95% percentil por bootstrap estratificado: reamostra dentro de cada estrato e grupo."""
    tam = np.array([len(ps) + len(po) for _, ps, po in estratos], dtype=float)
    peso = tam / tam.sum()
    acum = np.zeros(B)
    for i, (_, ps, po) in enumerate(estratos):
        ns, no = len(ps), len(po)
        amo_s = rng.integers(0, ns, size=(B, ns))
        amo_o = rng.integers(0, no, size=(B, no))
        acum += peso[i] * (v[ps][amo_s].mean(axis=1) / v[po][amo_o].mean(axis=1))
    return np.percentile(acum, [2.5, 97.5])


# ================================================================ PARTE 1 - ALCANCE
print("\n=== Parte 1 - Alcance: views patrocinado vs. organico ===")

# ---------------------------------------------------------------- 1a
print("\n[1a] Comparacao simples")
v_spon, v_org = VIEWS[eh_spon], VIEWS[~eh_spon]
lo_s, hi_s = boot_media(v_spon)
lo_o, hi_o = boot_media(v_org)

# razao das medias: reamostra os dois grupos de forma independente
ns, no = len(v_spon), len(v_org)
boot_razao = np.empty(N_BOOT)
feitos = 0
while feitos < N_BOOT:
    b = min(250, N_BOOT - feitos)
    ms = v_spon[rng.integers(0, ns, size=(b, ns))].mean(axis=1)
    mo = v_org[rng.integers(0, no, size=(b, no))].mean(axis=1)
    boot_razao[feitos:feitos + b] = ms / mo
    feitos += b
lo_r, hi_r = np.percentile(boot_razao, [2.5, 97.5])

t1a = pd.DataFrame([
    {"item": "patrocinado", "n": ns, "valor": round(v_spon.mean(), 6),
     "ic_inferior": round(lo_s, 6), "ic_superior": round(hi_s, 6),
     "mediana": round(np.median(v_spon), 6)},
    {"item": "organico", "n": no, "valor": round(v_org.mean(), 6),
     "ic_inferior": round(lo_o, 6), "ic_superior": round(hi_o, 6),
     "mediana": round(np.median(v_org), 6)},
    {"item": "razao_medias_patrocinado_organico", "n": N,
     "valor": round(v_spon.mean() / v_org.mean(), 6),
     "ic_inferior": round(lo_r, 6), "ic_superior": round(hi_r, 6),
     "mediana": np.nan},
])
t1a["ic_exclui_1"] = ["", "", "sim" if (lo_r > 1 or hi_r < 1) else "nao"]
salvar(t1a, "1a_comparacao_simples.csv")

# ---------------------------------------------------------------- 1b
print("\n[1b] Comparacao estratificada")
COLS_1B = ["platform", "content_category", "content_type", "faixa_seguidores"]
existentes_1b, estratos_1b = monta_estratos(np.arange(N), COLS_1B, MIN_1B)
pos_usados = np.concatenate([np.concatenate([ps, po]) for _, ps, po in estratos_1b])
n_spon_uso = sum(len(ps) for _, ps, _ in estratos_1b)
n_org_uso = sum(len(po) for _, _, po in estratos_1b)
print(f"  estratos existentes={existentes_1b}, usados={len(estratos_1b)}, "
      f"posts usados={len(pos_usados)}, fora={N - len(pos_usados)}")

ef_1b, razoes_1b, _ = efeito(estratos_1b, VIEWS)
lo_1b, hi_1b = boot_efeito(estratos_1b, VIEWS)
t1b = pd.DataFrame([{
    "metrica": "views",
    "estratos_existentes": existentes_1b,
    "estratos_usados": len(estratos_1b),
    "posts_usados": len(pos_usados),
    "posts_fora": N - len(pos_usados),
    "n_patrocinado_usado": n_spon_uso,
    "n_organico_usado": n_org_uso,
    "efeito_geral": round(ef_1b, 6),
    "ic_inferior": round(lo_1b, 6),
    "ic_superior": round(hi_1b, 6),
    "ic_exclui_1": "sim" if (lo_1b > 1 or hi_1b < 1) else "nao",
    "efeito_metade_A": round(efeito_na_metade(estratos_1b, VIEWS, eh_A), 6),
    "efeito_metade_B": round(efeito_na_metade(estratos_1b, VIEWS, ~eh_A), 6),
    "pct_estratos_razao_maior_1": round(100 * (razoes_1b > 1).mean(), 2),
    "razao_minimo": round(razoes_1b.min(), 6),
    "razao_p5": round(np.percentile(razoes_1b, 5), 6),
    "razao_mediana": round(np.median(razoes_1b), 6),
    "razao_p95": round(np.percentile(razoes_1b, 95), 6),
    "razao_maximo": round(razoes_1b.max(), 6),
    "comparacao_simples_sem_estratos": round(v_spon.mean() / v_org.mean(), 6),
}])
salvar(t1b, "1b_comparacao_estratificada.csv")

# ---------------------------------------------------------------- 1c
print("\n[1c] Por faixa de seguidores")
COLS_1C = ["platform", "content_category"]
linhas = []
for faixa in FAIXA_SEG_LABELS:
    pos_f = np.flatnonzero((df["faixa_seguidores"] == faixa).to_numpy())
    existentes, estratos = monta_estratos(pos_f, COLS_1C, MIN_1C)
    ef, _, _ = efeito(estratos, VIEWS)
    lo, hi = boot_efeito(estratos, VIEWS)
    linhas.append({
        "faixa_seguidores": faixa, "metrica": "views",
        "n_patrocinado": int(eh_spon[pos_f].sum()),
        "n_organico": int((~eh_spon[pos_f]).sum()),
        "estratos_existentes": existentes,
        "estratos_usados": len(estratos),
        "efeito": round(ef, 6),
        "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
        "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
        "efeito_metade_A": round(efeito_na_metade(estratos, VIEWS, eh_A), 6),
        "efeito_metade_B": round(efeito_na_metade(estratos, VIEWS, ~eh_A), 6),
    })
t1c = pd.DataFrame(linhas)
salvar(t1c, "1c_por_faixa_seguidores.csv")

# ---------------------------------------------------------------- 1d
print("\n[1d] Mediana de views por faixa x is_sponsored")
linhas = []
for faixa in FAIXA_SEG_LABELS:
    for flag in [True, False]:
        pos = np.flatnonzero((df["faixa_seguidores"] == faixa).to_numpy() & (eh_spon == flag))
        v = VIEWS[pos]
        linhas.append({
            "faixa_seguidores": faixa, "is_sponsored": flag, "n": len(pos),
            "mediana_views": round(np.median(v), 6),
            "media_views": round(v.mean(), 6),
        })
t1d = pd.DataFrame(linhas)
salvar(t1d, "1d_mediana_views_faixa_patrocinio.csv")

# ================================================================ PARTE 2 - FORMATO x AUDIENCIA
print("\n=== Parte 2 - Formato x audiencia ===")

# indice por post: valor / media da metrica na plataforma do post
IDX = {}
for m in METRICAS_P2:
    media_plat = df.groupby("platform")[m].transform("mean")
    IDX[m] = (df[m] / media_plat).to_numpy()

plat_pos = [np.flatnonzero((df["platform"] == p).to_numpy())
            for p in sorted(df["platform"].unique())]


def codigos(cols):
    chave = df[cols].astype(str).agg(" | ".join, axis=1)
    cod, nomes = pd.factorize(chave, sort=True)
    return cod, list(nomes)


def medias_por_grupo(valores, cod, k):
    soma = np.bincount(cod, weights=valores, minlength=k)
    cont = np.bincount(cod, minlength=k)
    with np.errstate(invalid="ignore", divide="ignore"):
        return soma / cont, cont


def bootstrap_ics(pos, B=N_BOOT, chunk=250):
    """IC 95% percentil do lift, para as 3 metricas, reusando as mesmas reamostragens."""
    n = len(pos)
    vals = {m: IDX[m][pos] for m in METRICAS_P2}
    acum = {m: [] for m in METRICAS_P2}
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        amostra = rng.integers(0, n, size=(b, n))
        for m in METRICAS_P2:
            acum[m].append(vals[m][amostra].mean(axis=1))
        feitos += b
    return {m: np.percentile(np.concatenate(a), [2.5, 97.5]) for m, a in acum.items()}


def teste_acaso(nome_vars, cod, k, valido):
    """Embaralha o indice dentro de cada plataforma e guarda o maior/menor lift do conjunto."""
    obs = {}
    for m in METRICAS_P2:
        med, _ = medias_por_grupo(IDX[m], cod, k)
        obs[m] = med[valido]

    maiores = {m: np.empty(N_PERM) for m in METRICAS_P2}
    menores = {m: np.empty(N_PERM) for m in METRICAS_P2}
    for r in range(N_PERM):
        emb = {}
        for m in METRICAS_P2:
            v = IDX[m].copy()
            for pos in plat_pos:
                v[pos] = IDX[m][rng.permutation(pos)]
            emb[m] = v
        for m in METRICAS_P2:
            med, _ = medias_por_grupo(emb[m], cod, k)
            todos = med[valido]
            maiores[m][r] = todos.max()
            menores[m][r] = todos.min()

    linhas = []
    for m in METRICAS_P2:
        o = obs[m]
        p95 = np.percentile(maiores[m], 95)
        p5 = np.percentile(menores[m], 5)
        linhas.append({
            "variaveis": nome_vars, "metrica": m,
            "segmentos_avaliados": len(o),
            "maior_lift_observado": round(o.max(), 6),
            "acaso_p95_dos_maiores": round(p95, 6),
            "maior_observado_acima_do_acaso": "sim" if o.max() > p95 else "nao",
            "menor_lift_observado": round(o.min(), 6),
            "acaso_p5_dos_menores": round(p5, 6),
            "menor_observado_abaixo_do_acaso": "sim" if o.min() < p5 else "nao",
        })
    return pd.DataFrame(linhas)


tabelas_p2, cobertura_p2, acaso_p2 = {}, [], []
for cols in CONJUNTOS_P2:
    nome_vars = " x ".join(cols)
    print(f"\n[P2] {nome_vars}")
    cod, nomes = codigos(cols)
    k = len(nomes)
    cont = np.bincount(cod, minlength=k)
    valido = cont >= MIN_N_P2
    print(f"  segmentos existentes={k}, mantidos={int(valido.sum())}, "
          f"fora={int((~valido).sum())}, posts fora={int(cont[~valido].sum())}")
    cobertura_p2.append({
        "variaveis": nome_vars, "segmentos_existentes": k,
        "segmentos_mantidos": int(valido.sum()),
        "segmentos_fora_por_n_menor_100": int((~valido).sum()),
        "posts_fora": int(cont[~valido].sum()),
    })

    linhas = []
    for g in np.flatnonzero(valido):
        pos = np.flatnonzero(cod == g)
        pos_A, pos_B = pos[eh_A[pos]], pos[~eh_A[pos]]
        ics = bootstrap_ics(pos)
        for m in METRICAS_P2:
            lift = IDX[m][pos].mean()
            lo, hi = ics[m]
            lA = IDX[m][pos_A].mean() if len(pos_A) else np.nan
            lB = IDX[m][pos_B].mean() if len(pos_B) else np.nan
            mesmo = (lA > 1 and lB > 1) or (lA < 1 and lB < 1)
            linhas.append({
                "variaveis": nome_vars, "segmento": nomes[g], "metrica": m, "n": len(pos),
                "lift": round(lift, 6),
                "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
                "lift_metade_A": round(lA, 6), "lift_metade_B": round(lB, 6),
                "mesmo_lado_nas_duas_metades": "sim" if mesmo else "nao",
            })
    tab = pd.DataFrame(linhas, columns=COLS_P2)
    nome_arq = "parte2_" + "_".join(c.replace("audience_", "").replace("_distribution", "")
                                    for c in cols) + ".csv"
    salvar(tab, nome_arq)
    tabelas_p2[nome_vars] = tab

    print(f"  teste contra o acaso ({N_PERM} permutacoes)")
    acaso_p2.append(teste_acaso(nome_vars, cod, k, valido))

t_cob = pd.DataFrame(cobertura_p2)
salvar(t_cob, "parte2_cobertura_segmentos.csv")
t_acaso = pd.concat(acaso_p2, ignore_index=True)
salvar(t_acaso, "parte2_teste_acaso.csv")

# ---------------------------------------------------------------- distribuicao dos lifts
linhas = []
for nome_vars, tab in tabelas_p2.items():
    for m in METRICAS_P2:
        sub = tab[tab["metrica"] == m]
        s = sub["lift"]
        linhas.append({
            "variaveis": nome_vars, "metrica": m, "segmentos": len(s),
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
t_dist = pd.DataFrame(linhas)
salvar(t_dist, "parte2_distribuicao_lifts.csv")

# 5 maiores e 5 menores lifts de taxa_engajamento por conjunto
blocos = []
for nome_vars, tab in tabelas_p2.items():
    t = tab[tab["metrica"] == "taxa_engajamento"].sort_values("lift", ascending=False)
    for rotulo, parte in [("5_maiores", t.head(5)), ("5_menores", t.tail(5)[::-1])]:
        b = parte.copy()
        b.insert(0, "grupo", rotulo)
        blocos.append(b)
t_topbottom = pd.concat(blocos, ignore_index=True)
salvar(t_topbottom, "parte2_top_bottom_taxa_engajamento.csv")

# ---------------------------------------------------------------- resumo_os06.md
print("\n[Resumo] resumo_os06.md")

m1a = t1a.copy()
for c in ["valor", "ic_inferior", "ic_superior", "mediana"]:
    m1a[c] = m1a[c].apply(lambda x: num(x, 6) if abs(x) < 10 else num(x, 2)
                          if pd.notna(x) else "-")
m1a["n"] = m1a["n"].apply(lambda x: num(x, 0))

m1b = t1b.T.reset_index()
m1b.columns = ["campo", "valor"]
m1b["valor"] = [num(v, 2) if c == "pct_estratos_razao_maior_1"
                else (num(v, 6) if isinstance(v, float) else str(v))
                for c, v in zip(m1b["campo"], m1b["valor"])]

m1c = t1c.copy()
for c in ["efeito", "ic_inferior", "ic_superior", "efeito_metade_A", "efeito_metade_B"]:
    m1c[c] = m1c[c].apply(lambda x: num(x, 6))
for c in ["n_patrocinado", "n_organico"]:
    m1c[c] = m1c[c].apply(lambda x: num(x, 0))

m1d = t1d.copy()
m1d["n"] = m1d["n"].apply(lambda x: num(x, 0))
for c in ["mediana_views", "media_views"]:
    m1d[c] = m1d[c].apply(lambda x: num(x, 2))

m_cob = t_cob.copy()
for c in ["segmentos_existentes", "segmentos_mantidos",
          "segmentos_fora_por_n_menor_100", "posts_fora"]:
    m_cob[c] = m_cob[c].apply(lambda x: num(x, 0))

m_dist = t_dist.copy()
for c in ["minimo", "p5", "mediana", "p95", "maximo"]:
    m_dist[c] = m_dist[c].apply(lambda x: num(x, 6))

m_top = t_topbottom.copy()
for c in ["lift", "ic_inferior", "ic_superior", "lift_metade_A", "lift_metade_B"]:
    m_top[c] = m_top[c].apply(lambda x: num(x, 6))
m_top["n"] = m_top["n"].apply(lambda x: num(x, 0))

m_acaso = t_acaso.copy()
for c in ["maior_lift_observado", "acaso_p95_dos_maiores",
          "menor_lift_observado", "acaso_p5_dos_menores"]:
    m_acaso[c] = m_acaso[c].apply(lambda x: num(x, 6))

# numeros usados na secao de pontos suspeitos
tot_p2 = sum(len(t) for t in tabelas_p2.values())
n_exclui_1 = sum(int((t["ic_exclui_1"] == "sim").sum()) for t in tabelas_p2.values())
n_mesmo_lado = sum(int((t["mesmo_lado_nas_duas_metades"] == "sim").sum())
                   for t in tabelas_p2.values())
limiares = ["acima_1_03", "acima_1_05", "acima_1_10",
            "abaixo_0_97", "abaixo_0_95", "abaixo_0_90"]
soma_limiares = int(t_dist[limiares].to_numpy().sum())
n_celulas_limiar = int(t_dist[limiares].size)
fora_maior = t_acaso[t_acaso["maior_observado_acima_do_acaso"] == "sim"]
fora_menor = t_acaso[t_acaso["menor_observado_abaixo_do_acaso"] == "sim"]
acaso_sim = len(fora_maior) + len(fora_menor)
acaso_total = 2 * len(t_acaso)
desc_fora = "; ".join(
    [f"maior lift de `{r.metrica}` em {r.variaveis} ({num(r.maior_lift_observado, 6)} contra "
     f"p95 do acaso {num(r.acaso_p95_dos_maiores, 6)})" for r in fora_maior.itertuples()]
    + [f"menor lift de `{r.metrica}` em {r.variaveis} ({num(r.menor_lift_observado, 6)} contra "
       f"p5 do acaso {num(r.acaso_p5_dos_menores, 6)})" for r in fora_menor.itertuples()]
) or "nenhuma"
lift_min_p2 = min(t["lift"].min() for t in tabelas_p2.values())
lift_max_p2 = max(t["lift"].max() for t in tabelas_p2.values())
med_1d = t1d.pivot(index="faixa_seguidores", columns="is_sponsored", values="mediana_views")
dif_1d = (med_1d[True] - med_1d[False]).abs()
ic_1c_sim = int((t1c["ic_exclui_1"] == "sim").sum())
lado_1c = int(((t1c["efeito_metade_A"] - 1) * (t1c["efeito_metade_B"] - 1) > 0).sum())

md = f"""# Resumo OS-06 — Lacunas finais: alcance e formato × audiência

Base: {num(N, 0)} posts (`datasets/social_media_dataset.csv`).
Script: `solution/analysis/os06_lacunas.py`. Saídas em `solution/outputs/os06/`.
Seed 42 em tudo. IC 95% por bootstrap percentil com 1.000 reamostragens.
Teste de repetição: a mesma divisão em duas metades da OS-02 (A = {num(int(eh_A.sum()), 0)}, B = {num(int((~eh_A).sum()), 0)}).
Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
Volume por grupo: {num(ns, 0)} posts patrocinados e {num(no, 0)} orgânicos.

---

# Parte 1 — Alcance: views patrocinado vs. orgânico

## 1a — Comparação simples

{tabela_md(m1a, ["item", "n", "valor", "ic_inferior", "ic_superior", "mediana", "ic_exclui_1"])}

`valor` = média de views nas duas primeiras linhas e razão das médias na terceira.

## 1b — Comparação estratificada

Estratos: platform × content_category × content_type × faixa_seguidores.
Critério: pelo menos 30 posts patrocinados **e** 30 orgânicos por estrato.
Efeito = média das razões (média patrocinado / média orgânico) ponderada pelo tamanho do estrato.
IC 95% por bootstrap estratificado (reamostragem dentro de cada estrato e de cada grupo).

{tabela_md(m1b)}

## 1c — Por faixa de seguidores

Estratos: platform × content_category, mínimo de 20 patrocinados e 20 orgânicos por estrato.

{tabela_md(m1c, ["faixa_seguidores", "n_patrocinado", "n_organico", "estratos_existentes",
                 "estratos_usados", "efeito", "ic_inferior", "ic_superior", "ic_exclui_1",
                 "efeito_metade_A", "efeito_metade_B"])}

## 1d — Mediana de views por faixa de seguidores × is_sponsored

{tabela_md(m1d, ["faixa_seguidores", "is_sponsored", "n", "mediana_views", "media_views"])}

---

# Parte 2 — Formato × audiência

Índice por post = valor / média da métrica na plataforma do post. Lift = média do índice no segmento.
Só segmentos com n ≥ 100.

## Cobertura dos segmentos

{tabela_md(m_cob)}

## Distribuição dos lifts por conjunto e métrica

{tabela_md(m_dist, ["variaveis", "metrica", "segmentos", "minimo", "p5", "mediana", "p95",
                    "maximo", "acima_1_03", "acima_1_05", "acima_1_10", "abaixo_0_97",
                    "abaixo_0_95", "abaixo_0_90", "ic_exclui_1_sim", "mesmo_lado_sim"])}

## 5 maiores e 5 menores lifts de `taxa_engajamento` por conjunto

{tabela_md(m_top, ["grupo", "variaveis", "segmento", "n", "lift", "ic_inferior",
                   "ic_superior", "ic_exclui_1", "lift_metade_A", "lift_metade_B",
                   "mesmo_lado_nas_duas_metades"])}

---

# Teste contra o acaso

Índice embaralhado dentro de cada plataforma, 200 repetições. Em cada repetição são recalculados
todos os segmentos do conjunto e guardados o maior e o menor lift.

{tabela_md(m_acaso, ["variaveis", "metrica", "segmentos_avaliados", "maior_lift_observado",
                     "acaso_p95_dos_maiores", "maior_observado_acima_do_acaso",
                     "menor_lift_observado", "acaso_p5_dos_menores",
                     "menor_observado_abaixo_do_acaso"])}

---

# Pontos suspeitos ou problemas encontrados

1. **Views de patrocinado e orgânico são praticamente iguais.** A razão das médias é
   {num(v_spon.mean() / v_org.mean(), 6)} com IC 95% [{num(lo_r, 6)}; {num(hi_r, 6)}], que
   {"exclui" if (lo_r > 1 or hi_r < 1) else "inclui"} 1. As médias são {num(v_spon.mean(), 2)}
   (patrocinado) e {num(v_org.mean(), 2)} (orgânico), diferença de
   {num(abs(v_spon.mean() - v_org.mean()), 2)} views por post.
2. **A estratificação não muda nada.** O efeito estratificado de 1b é {num(ef_1b, 6)}
   (IC [{num(lo_1b, 6)}; {num(hi_1b, 6)}], {"exclui" if (lo_1b > 1 or hi_1b < 1) else "inclui"} 1)
   contra {num(v_spon.mean() / v_org.mean(), 6)} na comparação simples. As {num(len(razoes_1b), 0)}
   razões por estrato ficam entre {num(razoes_1b.min(), 6)} e {num(razoes_1b.max(), 6)}, e
   {num(100 * (razoes_1b > 1).mean(), 2)}% delas estão acima de 1 — próximo dos 50% de um sorteio.
3. **1b descarta {num(existentes_1b - len(estratos_1b), 0)} dos {num(existentes_1b, 0)} estratos**
   pelo mínimo de 30+30, o que deixa {num(N - len(pos_usados), 0)} posts
   ({num(100 * (N - len(pos_usados)) / N, 2)}% da base) fora do cálculo.
4. **Nenhuma faixa de seguidores se destaca em 1c:** {num(ic_1c_sim, 0)} de
   {num(len(t1c), 0)} IC excluem 1, e {num(lado_1c, 0)} de {num(len(t1c), 0)} faixas têm as duas
   metades do mesmo lado de 1. Os efeitos ficam entre {num(t1c["efeito"].min(), 6)} e
   {num(t1c["efeito"].max(), 6)}.
5. **As 8 células de 1d têm medianas quase idênticas.** A maior diferença absoluta entre
   patrocinado e orgânico dentro de uma faixa é de {num(dif_1d.max(), 2)} views
   (faixa "{dif_1d.idxmax()}"), sobre medianas da ordem de {num(med_1d.to_numpy().mean(), 0)} views.
6. **Os lifts da Parte 2 são todos planos:** {num(tot_p2, 0)} linhas segmento × métrica com lift
   entre {num(lift_min_p2, 6)} e {num(lift_max_p2, 6)}. As {num(n_celulas_limiar, 0)} contagens de
   limiar (>1,03 / >1,05 / >1,10 e <0,97 / <0,95 / <0,90) somam {num(soma_limiares, 0)}.
7. **Quase nenhum IC da Parte 2 exclui 1:** {num(n_exclui_1, 0)} de {num(tot_p2, 0)}.
8. **O teste de repetição acerta o lado em {num(n_mesmo_lado, 0)} de {num(tot_p2, 0)} casos**
   ({num(100 * n_mesmo_lado / tot_p2, 1)}%), contra 50% esperados por sorteio.
9. **Teste contra o acaso: {num(acaso_sim, 0)} de {num(acaso_total, 0)} comparações ficam fora do
   acaso.** Fora do acaso: {desc_fora}. Nas outras {num(acaso_total - acaso_sim, 0)} comparações os
   extremos observados são menos extremos que os das permutações, o mesmo padrão já registrado na
   OS-02 e na OS-03b.
10. O padrão geral repete o das OS anteriores: as variáveis da base não separam desempenho nem
    em alcance (Parte 1) nem em formato × audiência (Parte 2). Nenhum número foi alterado.
"""

(OUT_DIR / "resumo_os06.md").write_text(md, encoding="utf-8")
print("  -> resumo_os06.md")

print(f"\nPronto. Saidas em {OUT_DIR}")
