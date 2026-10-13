"""OS-02 - Benchmark por segmento: lift vs. media da plataforma, IC bootstrap,
teste de repeticao (duas metades) e teste contra o acaso (permutacao)."""

import os
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_BOOT = 1000
N_PERM = 200
MIN_N = 100

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os02"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS = ["taxa_engajamento", "shares", "comments_count"]

# faixas desta OS (diferente do CLAUDE.md): ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

PERIODO_BINS = [-1, 5, 11, 17, 23]
PERIODO_LABELS = ["madrugada", "manha", "tarde", "noite"]

DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

VARS_N1 = ["content_type", "content_category", "language", "is_sponsored",
           "audience_age_distribution", "audience_gender_distribution",
           "audience_location", "faixa_seguidores", "n_hashtags",
           "periodo_dia", "dia_semana"]

COMBOS_N3 = [
    ["platform", "content_type", "content_category"],
    ["platform", "content_category", "faixa_seguidores"],
    ["platform", "content_type", "faixa_seguidores"],
    ["platform", "content_category", "audience_age_distribution"],
]

COMBO_N4 = ["platform", "content_type", "content_category", "faixa_seguidores"]

COLS_SAIDA = ["nivel", "variaveis", "segmento", "metrica", "n", "lift",
              "ic_inferior", "ic_superior", "ic_exclui_1",
              "lift_metade_A", "lift_metade_B", "mesmo_lado_nas_duas_metades"]

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
# hashtags vem como lista separada por virgula; nulo = 0
df["n_hashtags"] = df["hashtags"].fillna("").apply(
    lambda t: 0 if not str(t).strip() else len(str(t).split(",")))
df["periodo_dia"] = pd.cut(df["post_date"].dt.hour, bins=PERIODO_BINS,
                           labels=PERIODO_LABELS).astype(str)
df["dia_semana"] = df["post_date"].dt.weekday.map(dict(enumerate(DIAS)))
df["is_sponsored"] = df["is_sponsored"].astype(str)
df["n_hashtags"] = df["n_hashtags"].astype(str)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

# indice por post: valor / media da metrica na plataforma do post
IDX = {}
for m in METRICAS:
    media_plat = df.groupby("platform")[m].transform("mean")
    IDX[m] = (df[m] / media_plat).to_numpy()

# divisao unica em duas metades (mesma divisao para todos os segmentos)
metade = np.full(N, "B", dtype="<U1")
metade[rng.permutation(N)[: N // 2]] = "A"
eh_A = metade == "A"
print(f"Metades: A={eh_A.sum()}, B={(~eh_A).sum()}")

plat_pos = [np.flatnonzero((df["platform"] == p).to_numpy())
            for p in sorted(df["platform"].unique())]


# ---------------------------------------------------------------- helpers
def codigos(cols):
    """Rotulos de grupo (int) e nomes dos segmentos para um conjunto de colunas."""
    chave = df[cols[0]].astype(str) if len(cols) == 1 else \
        df[cols].astype(str).agg(" | ".join, axis=1)
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
    vals = {m: IDX[m][pos] for m in METRICAS}
    acum = {m: [] for m in METRICAS}
    feitos = 0
    while feitos < B:
        b = min(chunk, B - feitos)
        amostra = rng.integers(0, n, size=(b, n))
        for m in METRICAS:
            acum[m].append(vals[m][amostra].mean(axis=1))
        feitos += b
    return {m: np.percentile(np.concatenate(a), [2.5, 97.5]) for m, a in acum.items()}


def tabela_nivel(nivel, conjuntos, min_n):
    """Lift, IC e teste de repeticao de cada segmento. Retorna (tabela, cobertura, specs)."""
    linhas, cobertura, specs = [], [], []
    for cols in conjuntos:
        nome_vars = " x ".join(cols)
        cod, nomes = codigos(cols)
        k = len(nomes)
        cont = np.bincount(cod, minlength=k)
        valido = cont >= min_n if min_n else np.ones(k, dtype=bool)
        cobertura.append({"nivel": nivel, "variaveis": nome_vars,
                          "segmentos_existentes": k,
                          "segmentos_mantidos": int(valido.sum()),
                          "segmentos_fora_por_n_menor_100": int((~valido).sum())})
        specs.append((cod, k, valido))

        for g in np.flatnonzero(valido):
            pos = np.flatnonzero(cod == g)
            pos_A, pos_B = pos[eh_A[pos]], pos[~eh_A[pos]]
            ics = bootstrap_ics(pos)
            for m in METRICAS:
                lift = IDX[m][pos].mean()
                lo, hi = ics[m]
                lA = IDX[m][pos_A].mean() if len(pos_A) else np.nan
                lB = IDX[m][pos_B].mean() if len(pos_B) else np.nan
                mesmo = (lA > 1 and lB > 1) or (lA < 1 and lB < 1)
                linhas.append({
                    "nivel": nivel, "variaveis": nome_vars, "segmento": nomes[g],
                    "metrica": m, "n": len(pos),
                    "lift": round(lift, 6),
                    "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                    "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
                    "lift_metade_A": round(lA, 6), "lift_metade_B": round(lB, 6),
                    "mesmo_lado_nas_duas_metades": "sim" if mesmo else "nao",
                })
    return pd.DataFrame(linhas, columns=COLS_SAIDA), cobertura, specs


def teste_acaso(nivel, specs):
    """Embaralha o indice dentro de cada plataforma e guarda o maior/menor lift do nivel."""
    obs = {m: [] for m in METRICAS}
    for cod, k, valido in specs:
        for m in METRICAS:
            med, _ = medias_por_grupo(IDX[m], cod, k)
            obs[m].append(med[valido])

    maiores = {m: np.empty(N_PERM) for m in METRICAS}
    menores = {m: np.empty(N_PERM) for m in METRICAS}
    for r in range(N_PERM):
        emb = {}
        for m in METRICAS:
            v = IDX[m].copy()
            for pos in plat_pos:
                v[pos] = IDX[m][rng.permutation(pos)]
            emb[m] = v
        for m in METRICAS:
            todos = []
            for cod, k, valido in specs:
                med, _ = medias_por_grupo(emb[m], cod, k)
                todos.append(med[valido])
            todos = np.concatenate(todos)
            maiores[m][r] = todos.max()
            menores[m][r] = todos.min()

    linhas = []
    for m in METRICAS:
        o = np.concatenate(obs[m])
        linhas.append({
            "nivel": nivel, "metrica": m,
            "segmentos_avaliados": len(o),
            "maior_lift_observado": round(o.max(), 6),
            "acaso_p95_dos_maiores": round(np.percentile(maiores[m], 95), 6),
            "maior_observado_acima_do_acaso": "sim" if o.max() > np.percentile(maiores[m], 95) else "nao",
            "menor_lift_observado": round(o.min(), 6),
            "acaso_p5_dos_menores": round(np.percentile(menores[m], 5), 6),
            "menor_observado_abaixo_do_acaso": "sim" if o.min() < np.percentile(menores[m], 5) else "nao",
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- plataforma
print("\n[1] Plataforma")
linhas = []
for m in METRICAS:
    media_geral = df[m].mean()
    for p in sorted(df["platform"].unique()):
        pos = np.flatnonzero((df["platform"] == p).to_numpy())
        v = df[m].to_numpy()[pos]
        n = len(pos)
        boot = np.empty(N_BOOT)
        feitos = 0
        while feitos < N_BOOT:
            b = min(250, N_BOOT - feitos)
            boot[feitos:feitos + b] = v[rng.integers(0, n, size=(b, n))].mean(axis=1)
            feitos += b
        lo, hi = np.percentile(boot, [2.5, 97.5])
        linhas.append({
            "platform": p, "metrica": m, "n": n,
            "media_plataforma": round(v.mean(), 6),
            "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
            "media_geral": round(media_geral, 6),
            "razao_vs_media_geral": round(v.mean() / media_geral, 6),
            "razao_ic_inferior": round(lo / media_geral, 6),
            "razao_ic_superior": round(hi / media_geral, 6),
            "ic_exclui_media_geral": "sim" if (lo > media_geral or hi < media_geral) else "nao",
        })
salvar(pd.DataFrame(linhas), "plataforma.csv")

# ---------------------------------------------------------------- niveis 1 a 4
niveis = {
    1: ([[v] for v in VARS_N1], 0),
    2: ([["platform", v] for v in VARS_N1], MIN_N),
    3: (COMBOS_N3, MIN_N),
    4: ([COMBO_N4], MIN_N),
}

tabelas, coberturas, acaso = {}, [], []
for nivel, (conjuntos, min_n) in niveis.items():
    print(f"\n[2] Nivel {nivel}")
    tab, cob, specs = tabela_nivel(nivel, conjuntos, min_n)
    salvar(tab, f"nivel{nivel}.csv")
    tabelas[nivel] = tab
    coberturas.extend(cob)
    print(f"  teste contra o acaso ({N_PERM} permutacoes)")
    acaso.append(teste_acaso(nivel, specs))

salvar(pd.DataFrame(coberturas), "cobertura_niveis.csv")
salvar(pd.concat(acaso, ignore_index=True), "teste_acaso.csv")

# ---------------------------------------------------------------- distribuicao dos lifts
print("\n[3] Distribuicao dos lifts")
linhas = []
for nivel, tab in tabelas.items():
    for m in METRICAS:
        s = tab.loc[tab["metrica"] == m, "lift"]
        linhas.append({
            "nivel": nivel, "metrica": m, "segmentos": len(s),
            "minimo": round(s.min(), 6), "p5": round(s.quantile(0.05), 6),
            "mediana": round(s.median(), 6), "p95": round(s.quantile(0.95), 6),
            "maximo": round(s.max(), 6),
            "acima_1_03": int((s > 1.03).sum()),
            "acima_1_05": int((s > 1.05).sum()),
            "acima_1_10": int((s > 1.10).sum()),
            "abaixo_0_97": int((s < 0.97).sum()),
            "abaixo_0_95": int((s < 0.95).sum()),
            "abaixo_0_90": int((s < 0.90).sum()),
            "ic_exclui_1_sim": int((tab.loc[tab["metrica"] == m, "ic_exclui_1"] == "sim").sum()),
            "mesmo_lado_sim": int((tab.loc[tab["metrica"] == m,
                                           "mesmo_lado_nas_duas_metades"] == "sim").sum()),
        })
salvar(pd.DataFrame(linhas), "distribuicao_lifts.csv")

# 10 maiores e 10 menores lifts de taxa_engajamento por nivel
blocos = []
for nivel, tab in tabelas.items():
    t = tab[tab["metrica"] == "taxa_engajamento"].sort_values("lift", ascending=False)
    for rotulo, parte in [("10_maiores", t.head(10)), ("10_menores", t.tail(10)[::-1])]:
        b = parte.copy()
        b.insert(0, "grupo", rotulo)
        blocos.append(b)
salvar(pd.concat(blocos, ignore_index=True), "top_bottom_taxa_engajamento.csv")

print(f"\nPronto. Saidas em {OUT_DIR}")
