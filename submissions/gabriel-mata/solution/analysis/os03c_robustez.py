"""OS-03c - Robustez da conclusao: limite maximo do efeito (equivalencia), menor efeito
detectavel, controle positivo (injecao), caudas da distribuicao e tendencia no tempo."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

SEED = 42
N_BOOT = 1000
N_PERM = 200
MIN_N = 100
Z_WILSON = 1.96
MDE_Z = 1.96 + 0.84          # poder 80%, significancia 5% bicaudal (formula da OS)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os03c"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS = ["taxa_engajamento", "shares", "comments_count"]

# faixas da OS-02/OS-03c: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

VARS = ["platform", "content_type", "content_category", "faixa_seguidores", "is_sponsored",
        "audience_age_distribution", "audience_gender_distribution", "audience_location"]

COMBO_N4 = ["platform", "content_type", "content_category", "faixa_seguidores"]

rng = np.random.default_rng(SEED)


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
df["is_sponsored"] = df["is_sponsored"].astype(str)

mes_abs = df["post_date"].dt.year * 12 + df["post_date"].dt.month
df["mes_num"] = (mes_abs - mes_abs.min() + 1).to_numpy()
df["mes_rotulo"] = df["post_date"].dt.to_period("M").astype(str)

N = len(df)
N_MESES = int(df["mes_num"].max())
PLATAFORMAS = sorted(df["platform"].unique())
print(f"Base: {N} linhas, {N_MESES} meses (origem: {DATA_PATH})")

# mesma divisao em duas metades da OS-02 (primeira extracao do gerador seed 42)
metade = np.full(N, "B", dtype="<U1")
metade[rng.permutation(N)[: N // 2]] = "A"
eh_A = metade == "A"
print(f"Metades: A={eh_A.sum()}, B={(~eh_A).sum()}")

plat_pos = [np.flatnonzero((df["platform"] == p).to_numpy()) for p in PLATAFORMAS]


def indices(d):
    """Indice por post. Regra: valor / media da metrica na plataforma do post.
    Excecao da OS: para a variavel platform, valor / media geral da base."""
    por_plat, por_geral = {}, {}
    for m in METRICAS:
        por_plat[m] = (d[m] / d.groupby("platform")[m].transform("mean")).to_numpy()
        por_geral[m] = (d[m] / d[m].mean()).to_numpy()
    return por_plat, por_geral


IDX_P, IDX_G = indices(df)


def idx_de(var, m, por_plat=None, por_geral=None):
    por_plat = IDX_P if por_plat is None else por_plat
    por_geral = IDX_G if por_geral is None else por_geral
    return por_geral[m] if var == "platform" else por_plat[m]


SEGMENTOS = [(v, val, np.flatnonzero((df[v] == val).to_numpy()))
             for v in VARS for val in sorted(df[v].unique())]
print(f"Segmentos: {len(SEGMENTOS)} ({len(SEGMENTOS) * len(METRICAS)} linhas segmento x metrica)")


def amostras_boot(n, B=N_BOOT, chunk=200):
    """Gera as reamostragens em blocos (mesmas reamostragens reusadas entre metricas)."""
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        yield rng.integers(0, n, size=(b, n))
        feitos += b


def boot_percentis(valores_por_metrica, pcts):
    """Percentis bootstrap da media, para varias metricas, com as mesmas reamostragens."""
    chaves = list(valores_por_metrica)
    n = len(valores_por_metrica[chaves[0]])
    acum = {k: [] for k in chaves}
    for amostra in amostras_boot(n):
        for k in chaves:
            acum[k].append(valores_por_metrica[k][amostra].mean(axis=1))
    return {k: np.percentile(np.concatenate(a), pcts) for k, a in acum.items()}


def com_injecao(metrica, pos, efeito):
    """Copia da base com a metrica multiplicada por `efeito` nos posts de `pos`."""
    d = df.copy()
    col = d[metrica].to_numpy().copy()
    col[pos] = col[pos] * efeito
    d[metrica] = col
    return d


def wilson(k, n, z=Z_WILSON):
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meia = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centro - meia, centro + meia


# ---------------------------------------------------------------- Bloco 1: equivalencia
print("\n[Bloco 1] Limite maximo do efeito")
linhas = []
for var, val, pos in SEGMENTOS:
    vals = {m: idx_de(var, m)[pos] for m in METRICAS}
    pct = boot_percentis(vals, [2.5, 97.5, 5, 95])
    for m in METRICAS:
        lo95, hi95, lo90, hi90 = pct[m]
        lift = vals[m].mean()
        efeito_max = max(abs(lo95 - 1), abs(hi95 - 1)) * 100
        linhas.append({
            "variavel": var, "segmento": val, "metrica": m, "n": len(pos),
            "lift": round(lift, 6),
            "ic95_inferior": round(lo95, 6), "ic95_superior": round(hi95, 6),
            "ic90_inferior": round(lo90, 6), "ic90_superior": round(hi90, 6),
            "efeito_maximo_plausivel_pct": round(efeito_max, 4),
            "equivalente_1pct": "sim" if (lo90 >= 0.99 and hi90 <= 1.01) else "nao",
            "equivalente_2pct": "sim" if (lo90 >= 0.98 and hi90 <= 1.02) else "nao",
        })
bloco1 = pd.DataFrame(linhas)
salvar(bloco1, "bloco1_equivalencia.csv")

# ---------------------------------------------------------------- Bloco 2: MDE
print("\n[Bloco 2] Menor efeito detectavel")
linhas = []
for var, val, pos in SEGMENTOS:
    n_seg = len(pos)
    n_resto = N - n_seg
    for m in METRICAS:
        sd = idx_de(var, m).std(ddof=1)
        mde = MDE_Z * sd * np.sqrt(1 / n_seg + 1 / n_resto)
        linhas.append({
            "variavel": var, "segmento": val, "metrica": m,
            "n_segmento": n_seg, "n_resto": n_resto,
            "sd_indice_base": round(sd, 6),
            "mde_pct": round(mde * 100, 4),
        })
bloco2 = pd.DataFrame(linhas)
salvar(bloco2, "bloco2_mde.csv")

# ---------------------------------------------------------------- Bloco 3a: injecao isolada
print("\n[Bloco 3a] Controle positivo - segmentos isolados")
EFEITOS = [1.01, 1.02, 1.05]
menor_seg = {}
for var in VARS:
    cont = df[var].value_counts()
    menor_seg[var] = cont.idxmin()
    print(f"  {var}: menor n = {menor_seg[var]} ({cont.min()})")

linhas = []
for var in VARS:
    val = menor_seg[var]
    pos = np.flatnonzero((df[var] == val).to_numpy())
    for m in METRICAS:
        for efeito in EFEITOS:
            d = com_injecao(m, pos, efeito)    # sempre numa copia; a base original nao muda
            ip, ig = indices(d)
            idx = idx_de(var, m, ip, ig)
            v = idx[pos]
            lo, hi = boot_percentis({m: v}, [2.5, 97.5])[m]
            pos_A, pos_B = pos[eh_A[pos]], pos[~eh_A[pos]]
            lA, lB = idx[pos_A].mean(), idx[pos_B].mean()
            detectado = (lo > 1 or hi < 1) and lA > 1 and lB > 1
            linhas.append({
                "variavel": var, "segmento": val, "n": len(pos), "metrica": m,
                "efeito_injetado_pct": round((efeito - 1) * 100, 2),
                "lift_medido": round(v.mean(), 6),
                "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                "lift_metade_A": round(lA, 6), "lift_metade_B": round(lB, 6),
                "detectado": "sim" if detectado else "nao",
            })
bloco3a = pd.DataFrame(linhas)
salvar(bloco3a, "bloco3a_injecao_isolada.csv")

# ---------------------------------------------------------------- Bloco 3b: injecao na busca
print("\n[Bloco 3b] Controle positivo - injecao numa busca entre muitos segmentos")
chave4 = df[COMBO_N4].astype(str).agg(" | ".join, axis=1)
cod4, nomes4 = pd.factorize(chave4, sort=True)
cont4 = np.bincount(cod4, minlength=len(nomes4))

candidatos = [g for g in range(len(nomes4)) if 100 <= cont4[g] <= 150]
rng_sorteio = np.random.default_rng(SEED)
g_sorteado = int(rng_sorteio.choice(candidatos))
pos_sorteado = np.flatnonzero(cod4 == g_sorteado)
print(f"  candidatos (n entre 100 e 150): {len(candidatos)}")
print(f"  sorteado: {nomes4[g_sorteado]} (n={len(pos_sorteado)})")

valido4 = cont4 >= MIN_N
k4 = len(nomes4)
print(f"  segmentos da busca com n >= {MIN_N}: {int(valido4.sum())} de {k4}")

linhas = []
for cenario, efeito in enumerate([1.05, 1.10], start=1):
    d = com_injecao("taxa_engajamento", pos_sorteado, efeito)
    media_plat = d.groupby("platform")["taxa_engajamento"].transform("mean")
    idx = (d["taxa_engajamento"] / media_plat).to_numpy()

    soma = np.bincount(cod4, weights=idx, minlength=k4)
    lifts = soma / cont4
    lift_seg = lifts[g_sorteado]
    lo, hi = boot_percentis({"m": idx[pos_sorteado]}, [2.5, 97.5])["m"]

    ordenados = np.argsort(-lifts[valido4])
    ranking = list(np.flatnonzero(valido4)[ordenados])
    posicao = ranking.index(g_sorteado) + 1

    # teste contra o acaso: embaralha o indice dentro de cada plataforma
    maiores = np.empty(N_PERM)
    for r in range(N_PERM):
        emb = idx.copy()
        for pos in plat_pos:
            emb[pos] = idx[rng.permutation(pos)]
        med = np.bincount(cod4, weights=emb, minlength=k4) / cont4
        maiores[r] = med[valido4].max()
    p95 = np.percentile(maiores, 95)

    linhas.append({
        "cenario": cenario, "efeito_injetado_pct": round((efeito - 1) * 100, 2),
        "segmento_sorteado": nomes4[g_sorteado], "n": len(pos_sorteado),
        "metrica": "taxa_engajamento",
        "lift_medido": round(lift_seg, 6),
        "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
        "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
        "posicao_no_ranking": posicao,
        "segmentos_no_ranking": int(valido4.sum()),
        "maior_lift_por_acaso_p95": round(p95, 6),
        "supera_o_acaso": "sim" if lift_seg > p95 else "nao",
    })
bloco3b = pd.DataFrame(linhas)
salvar(bloco3b, "bloco3b_injecao_na_busca.csv")

# ---------------------------------------------------------------- Bloco 4: caudas
print("\n[Bloco 4] Caudas da distribuicao")
plat_arr = df["platform"].to_numpy()
CAUDAS = ["top10", "top1", "bottom10"]
ESPERADO = {"top10": 0.10, "top1": 0.01, "bottom10": 0.10}

marca = {}            # (metrica, cauda) -> bool por post
taxa_base = {}        # (metrica, cauda) -> taxa realizada na plataforma, por post
cortes_por_plat = {}  # (metrica, cauda) -> valor do corte da plataforma, por post
for m in METRICAS:
    v = df[m].to_numpy()
    g = df.groupby("platform")[m]
    corte_10 = df["platform"].map(g.quantile(0.10)).to_numpy()
    corte_90 = df["platform"].map(g.quantile(0.90)).to_numpy()
    corte_99 = df["platform"].map(g.quantile(0.99)).to_numpy()
    marca[(m, "top10")] = v >= corte_90
    marca[(m, "top1")] = v >= corte_99
    marca[(m, "bottom10")] = v <= corte_10
    for c in CAUDAS:
        taxa_p = pd.Series(marca[(m, c)]).groupby(plat_arr).mean()
        taxa_base[(m, c)] = df["platform"].map(taxa_p).to_numpy()
        cortes_por_plat[(m, c)] = {"top10": corte_90, "top1": corte_99,
                                   "bottom10": corte_10}[c]

# cortes por plataforma e metrica (passo pedido no Bloco 4) + taxa que o corte realiza
linhas = []
for m in METRICAS:
    for p in PLATAFORMAS:
        eh_p = (plat_arr == p)
        for c in CAUDAS:
            linhas.append({
                "platform": p, "metrica": m, "cauda": c,
                "corte": round(float(cortes_por_plat[(m, c)][eh_p][0]), 6),
                "esperado_pct": 100 * ESPERADO[c],
                "taxa_realizada_na_plataforma_pct": round(100 * marca[(m, c)][eh_p].mean(), 4),
                "n_plataforma": int(eh_p.sum()),
            })
salvar(pd.DataFrame(linhas), "bloco4_cortes_plataforma.csv")

linhas = []
for var, val, pos in SEGMENTOS:
    resto = np.setdiff1d(np.arange(N), pos, assume_unique=True)
    for m in METRICAS:
        idx = idx_de(var, m)
        ks = stats.ks_2samp(idx[pos], idx[resto])
        linha = {"variavel": var, "segmento": val, "metrica": m, "n": len(pos)}
        for c in CAUDAS:
            k = int(marca[(m, c)][pos].sum())
            n = len(pos)
            lo, hi = wilson(k, n)
            esp = ESPERADO[c]
            linha[f"{c}_pct"] = round(100 * k / n, 4)
            linha[f"{c}_ic_inferior_pct"] = round(100 * lo, 4)
            linha[f"{c}_ic_superior_pct"] = round(100 * hi, 4)
            linha[f"{c}_exclui_esperado"] = "sim" if (lo > esp or hi < esp) else "nao"
            # o corte por quantil nao realiza 10%/1% exatos quando a metrica tem empates:
            # taxa_base = taxa que o corte realiza nas plataformas do segmento
            base = taxa_base[(m, c)][pos].mean()
            linha[f"{c}_taxa_base_plataformas_pct"] = round(100 * base, 4)
            linha[f"{c}_exclui_taxa_base"] = "sim" if (lo > base or hi < base) else "nao"
        linha["ks_estatistica"] = round(ks.statistic, 6)
        linha["ks_p_valor"] = round(ks.pvalue, 6)
        linha["ks_p_menor_005"] = "sim" if ks.pvalue < 0.05 else "nao"
        linhas.append(linha)
bloco4 = pd.DataFrame(linhas)
salvar(bloco4, "bloco4_caudas.csv")

# ---------------------------------------------------------------- Bloco 5: tendencia
print("\n[Bloco 5] Tendencia no tempo")
ESCOPOS = [("geral", "base inteira", np.ones(N, dtype=bool))]
for v in ["platform", "content_type", "is_sponsored"]:
    for val in sorted(df[v].unique()):
        ESCOPOS.append((v, val, (df[v] == val).to_numpy()))

linhas = []

# 1) medias mensais
for escopo, val, mask in ESCOPOS:
    sub = df[mask]
    for m in METRICAS:
        g = sub.groupby("mes_rotulo")[m].agg(["size", "mean"])
        for rotulo, (n_mes, media) in g.iterrows():
            linhas.append({"tabela": "media_mensal", "escopo": escopo, "valor": val,
                           "metrica": m, "chave": rotulo, "n": int(n_mes),
                           "estimativa": round(media, 6), "ic_inferior": "",
                           "ic_superior": "", "p_valor": ""})

# 2) tendencia: metrica ~ numero do mes (1..25), HC3, no nivel do post
for escopo, val, mask in ESCOPOS:
    sub = df[mask]
    X = sm.add_constant(sub["mes_num"].to_numpy(dtype=float))
    for m in METRICAS:
        y = sub[m].to_numpy(dtype=float)
        res = sm.OLS(y, X).fit(cov_type="HC3")
        b, se, p = res.params[1], res.bse[1], res.pvalues[1]
        fator = 12 * 100 / y.mean()          # inclinacao por mes -> % da media por ano
        linhas.append({"tabela": "tendencia", "escopo": escopo, "valor": val,
                       "metrica": m, "chave": "pct_da_media_por_ano", "n": len(y),
                       "estimativa": round(b * fator, 6),
                       "ic_inferior": round((b - 1.96 * se) * fator, 6),
                       "ic_superior": round((b + 1.96 * se) * fator, 6),
                       "p_valor": round(p, 6)})

# 3) primeiro ano vs ultimo ano, por plataforma (mes 13 fica fora: 25 meses)
primeiros = df["mes_num"].between(1, 12).to_numpy()
ultimos = df["mes_num"].between(N_MESES - 11, N_MESES).to_numpy()
for p in PLATAFORMAS:
    eh_p = (df["platform"] == p).to_numpy()
    pos_i = np.flatnonzero(eh_p & primeiros)
    pos_f = np.flatnonzero(eh_p & ultimos)
    for m in METRICAS:
        v = df[m].to_numpy()
        vi, vf = v[pos_i], v[pos_f]
        razoes = []
        for am_i in amostras_boot(len(vi)):
            am_f = rng.integers(0, len(vf), size=(am_i.shape[0], len(vf)))
            razoes.append(vf[am_f].mean(axis=1) / vi[am_i].mean(axis=1))
        razoes = np.concatenate(razoes)
        lo, hi = np.percentile(razoes, [2.5, 97.5])
        linhas.append({"tabela": "primeiro_vs_ultimo_ano", "escopo": "platform", "valor": p,
                       "metrica": m, "chave": f"razao_meses_{N_MESES-11}a{N_MESES}_sobre_1a12",
                       "n": len(pos_i) + len(pos_f),
                       "estimativa": round(vf.mean() / vi.mean(), 6),
                       "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                       "p_valor": ""})

bloco5 = pd.DataFrame(linhas)
salvar(bloco5, "bloco5_tendencia.csv")

print(f"\nPronto. Saidas em {OUT_DIR}")
