"""OS-03 - Patrocinio (comparacao estratificada, regressao com controles, detalhes do
patrocinio, engajamento entregue, volume) e validacao geral com modelo preditivo."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold, cross_validate, train_test_split

SEED = 42
N_BOOT = 1000
MIN_B1 = 30
MIN_B3 = 20

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
OUT_DIR = SCRIPT_DIR.parent / "outputs" / "os03"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRICAS = ["taxa_engajamento", "shares", "comments_count"]
METRICAS_ABS = METRICAS + ["engajamento"]

# mesmas faixas da OS-02: ate 50K, 50-100K, 100-500K, 500K-1M
FAIXA_SEG_BINS = [0, 50_000, 100_000, 500_000, 1_000_000]
FAIXA_SEG_LABELS = ["ate 50K", "50-100K", "100-500K", "500K-1M"]

PERIODO_BINS = [-1, 5, 11, 17, 23]
PERIODO_LABELS = ["madrugada", "manha", "tarde", "noite"]

DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


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
df["hora"] = df["post_date"].dt.hour
df["is_sponsored"] = df["is_sponsored"].astype(bool)

N = len(df)
print(f"Base: {N} linhas (origem: {DATA_PATH})")

eh_spon = df["is_sponsored"].to_numpy()
VAL = {m: df[m].to_numpy(dtype=float) for m in METRICAS_ABS}

# mesma divisao em duas metades da OS-02: primeiro uso de um default_rng(42)
rng_split = np.random.default_rng(SEED)
metade = np.full(N, "B", dtype="<U1")
metade[rng_split.permutation(N)[: N // 2]] = "A"
eh_A = metade == "A"
print(f"Metades: A={eh_A.sum()}, B={(~eh_A).sum()}")

rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- helpers estratos
def chave_estrato(cols):
    return df[cols].astype(str).agg(" | ".join, axis=1).to_numpy()


def monta_estratos(pos_base, cols, min_g):
    """(estratos_existentes, [(nome, pos_patrocinado, pos_organico)]) com n minimo nos 2 grupos."""
    chave = chave_estrato(cols)[pos_base]
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


def boot_efeito(estratos, metricas, B=N_BOOT):
    """IC 95% percentil por bootstrap estratificado: reamostra dentro de cada estrato e grupo."""
    tam = np.array([len(ps) + len(po) for _, ps, po in estratos], dtype=float)
    peso = tam / tam.sum()
    acum = {m: np.zeros(B) for m in metricas}
    for i, (_, ps, po) in enumerate(estratos):
        ns, no = len(ps), len(po)
        amo_s = rng.integers(0, ns, size=(B, ns))
        amo_o = rng.integers(0, no, size=(B, no))
        for m in metricas:
            vs, vo = VAL[m][ps], VAL[m][po]
            acum[m] += peso[i] * (vs[amo_s].mean(axis=1) / vo[amo_o].mean(axis=1))
    return {m: np.percentile(a, [2.5, 97.5]) for m, a in acum.items()}


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


# ---------------------------------------------------------------- bloco 1
print("\n[Bloco 1] Comparacao justa (estratificada)")
COLS_B1 = ["platform", "content_category", "content_type", "faixa_seguidores"]
existentes_b1, estratos_b1 = monta_estratos(np.arange(N), COLS_B1, MIN_B1)
pos_usados = np.concatenate([np.concatenate([ps, po]) for _, ps, po in estratos_b1])
n_spon_uso = sum(len(ps) for _, ps, _ in estratos_b1)
n_org_uso = sum(len(po) for _, _, po in estratos_b1)
print(f"  estratos existentes={existentes_b1}, usados={len(estratos_b1)}, "
      f"posts usados={len(pos_usados)}, fora={N - len(pos_usados)}")

ics_b1 = boot_efeito(estratos_b1, METRICAS)
linhas = []
for m in METRICAS:
    ef, razoes, _ = efeito(estratos_b1, VAL[m])
    lo, hi = ics_b1[m]
    simples = VAL[m][eh_spon].mean() / VAL[m][~eh_spon].mean()
    linhas.append({
        "metrica": m,
        "estratos_existentes": existentes_b1,
        "estratos_usados": len(estratos_b1),
        "posts_usados": len(pos_usados),
        "posts_fora": N - len(pos_usados),
        "n_patrocinado_usado": n_spon_uso,
        "n_organico_usado": n_org_uso,
        "efeito_geral": round(ef, 6),
        "ic_inferior": round(lo, 6),
        "ic_superior": round(hi, 6),
        "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
        "efeito_metade_A": round(efeito_na_metade(estratos_b1, VAL[m], eh_A), 6),
        "efeito_metade_B": round(efeito_na_metade(estratos_b1, VAL[m], ~eh_A), 6),
        "pct_estratos_razao_maior_1": round(100 * (razoes > 1).mean(), 2),
        "razao_minimo": round(razoes.min(), 6),
        "razao_p5": round(np.percentile(razoes, 5), 6),
        "razao_mediana": round(np.median(razoes), 6),
        "razao_p95": round(np.percentile(razoes, 95), 6),
        "razao_maximo": round(razoes.max(), 6),
        "comparacao_simples_sem_estratos": round(simples, 6),
    })
salvar(pd.DataFrame(linhas), "bloco1_comparacao_estratificada.csv")

# ---------------------------------------------------------------- bloco 2
print("\n[Bloco 2] Regressao com controles (OLS, HC3)")
df["is_sponsored_num"] = df["is_sponsored"].astype(int)
CONTROLES = ("C(platform) + C(content_type) + C(content_category) + C(faixa_seguidores) "
             "+ C(language) + C(audience_age_distribution) + C(audience_gender_distribution) "
             "+ C(audience_location) + C(n_hashtags) + C(periodo_dia) + C(dia_semana)")
linhas = []
for m in METRICAS:
    res = smf.ols(f"{m} ~ is_sponsored_num + {CONTROLES}", data=df).fit(cov_type="HC3")
    coef = res.params["is_sponsored_num"]
    lo, hi = res.conf_int().loc["is_sponsored_num"]
    media = df[m].mean()
    linhas.append({
        "metrica": m,
        "n": int(res.nobs),
        "media_metrica": round(media, 6),
        "coef_is_sponsored": round(coef, 6),
        "coef_pct_da_media": round(100 * coef / media, 4),
        "ic_inferior": round(lo, 6),
        "ic_superior": round(hi, 6),
        "ic_exclui_0": "sim" if (lo > 0 or hi < 0) else "nao",
        "p_valor": round(res.pvalues["is_sponsored_num"], 6),
        "r2": round(res.rsquared, 6),
        "r2_ajustado": round(res.rsquared_adj, 6),
        "p_valor_teste_F": round(res.f_pvalue, 6),
        "numero_de_condicao": round(res.condition_number, 2),
        "n_parametros": len(res.params),
    })
salvar(pd.DataFrame(linhas), "bloco2_regressao_controles.csv")

# ---------------------------------------------------------------- bloco 3
print("\n[Bloco 3] Patrocinio por faixa de seguidores")
COLS_B3 = ["platform", "content_category"]
linhas = []
for faixa in FAIXA_SEG_LABELS:
    pos_f = np.flatnonzero((df["faixa_seguidores"] == faixa).to_numpy())
    existentes, estratos = monta_estratos(pos_f, COLS_B3, MIN_B3)
    ics = boot_efeito(estratos, METRICAS)
    for m in METRICAS:
        ef, _, _ = efeito(estratos, VAL[m])
        lo, hi = ics[m]
        linhas.append({
            "faixa_seguidores": faixa, "metrica": m,
            "n_patrocinado": int(eh_spon[pos_f].sum()),
            "n_organico": int((~eh_spon[pos_f]).sum()),
            "estratos_existentes": existentes,
            "estratos_usados": len(estratos),
            "efeito": round(ef, 6),
            "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
            "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
            "efeito_metade_A": round(efeito_na_metade(estratos, VAL[m], eh_A), 6),
            "efeito_metade_B": round(efeito_na_metade(estratos, VAL[m], ~eh_A), 6),
        })
salvar(pd.DataFrame(linhas), "bloco3_por_faixa_seguidores.csv")

# ---------------------------------------------------------------- bloco 4
print("\n[Bloco 4] Detalhes do patrocinio (so posts patrocinados)")
pos_spon = np.flatnonzero(eh_spon)
spon = df.loc[eh_spon]
# indice por post: valor / media da metrica entre os patrocinados da plataforma
IDX = {}
for m in METRICAS:
    media_plat = spon.groupby("platform")[m].transform("mean")
    IDX[m] = (spon[m] / media_plat).to_numpy()

SEGMENTOS_B4 = [["disclosure_type"], ["disclosure_location"], ["sponsor_category"],
                ["disclosure_type", "disclosure_location"]]
COLS_B4 = ["variaveis", "segmento", "metrica", "n", "lift", "ic_inferior", "ic_superior",
           "ic_exclui_1", "lift_metade_A", "lift_metade_B", "mesmo_lado_nas_duas_metades"]
A_spon = eh_A[pos_spon]
linhas = []
for cols in SEGMENTOS_B4:
    nome_vars = " x ".join(cols)
    chave = spon[cols].astype(str).agg(" | ".join, axis=1).to_numpy()
    for nm in np.unique(chave):
        loc = np.flatnonzero(chave == nm)
        loc_A, loc_B = loc[A_spon[loc]], loc[~A_spon[loc]]
        n = len(loc)
        # bootstrap reusando as mesmas reamostragens para as 3 metricas
        feitos = 0
        boot = {m: np.empty(N_BOOT) for m in METRICAS}
        while feitos < N_BOOT:
            b = min(250, N_BOOT - feitos)
            amo = rng.integers(0, n, size=(b, n))
            for m in METRICAS:
                boot[m][feitos:feitos + b] = IDX[m][loc][amo].mean(axis=1)
            feitos += b
        for m in METRICAS:
            lift = IDX[m][loc].mean()
            lo, hi = np.percentile(boot[m], [2.5, 97.5])
            lA = IDX[m][loc_A].mean() if len(loc_A) else np.nan
            lB = IDX[m][loc_B].mean() if len(loc_B) else np.nan
            mesmo = (lA > 1 and lB > 1) or (lA < 1 and lB < 1)
            linhas.append({
                "variaveis": nome_vars, "segmento": nm, "metrica": m, "n": n,
                "lift": round(lift, 6),
                "ic_inferior": round(lo, 6), "ic_superior": round(hi, 6),
                "ic_exclui_1": "sim" if (lo > 1 or hi < 1) else "nao",
                "lift_metade_A": round(lA, 6), "lift_metade_B": round(lB, 6),
                "mesmo_lado_nas_duas_metades": "sim" if mesmo else "nao",
            })
salvar(pd.DataFrame(linhas, columns=COLS_B4), "bloco4_detalhes_patrocinio.csv")

# ---------------------------------------------------------------- bloco 5
print("\n[Bloco 5] Engajamento entregue por faixa")
eng = VAL["engajamento"]
eng_por_seg = eng / df["follower_count"].to_numpy(dtype=float)
linhas = []
for faixa in FAIXA_SEG_LABELS:
    for flag in [True, False]:
        pos = np.flatnonzero((df["faixa_seguidores"] == faixa).to_numpy() & (eh_spon == flag))
        v = eng[pos]
        lo, hi = boot_media(v)
        linhas.append({
            "faixa_seguidores": faixa,
            "is_sponsored": flag,
            "n": len(pos),
            "media_engajamento": round(v.mean(), 6),
            "ic_inferior": round(lo, 6),
            "ic_superior": round(hi, 6),
            "mediana_engajamento": round(np.median(v), 6),
            "p10_engajamento": round(np.percentile(v, 10), 6),
            "p90_engajamento": round(np.percentile(v, 90), 6),
            "mediana_engajamento_por_seguidor": round(np.median(eng_por_seg[pos]), 9),
        })
salvar(pd.DataFrame(linhas), "bloco5_engajamento_por_faixa.csv")

# ---------------------------------------------------------------- bloco 6
print("\n[Bloco 6] Volume patrocinado")
eng_total = eng.sum()
linhas = []
for var in ["platform", "content_category", "content_type", "faixa_seguidores"]:
    for seg in sorted(df[var].astype(str).unique()):
        m = (df[var].astype(str) == seg).to_numpy()
        n_s = int((m & eh_spon).sum())
        linhas.append({
            "variavel": var, "segmento": seg,
            "n_total": int(m.sum()),
            "n_patrocinado": n_s,
            "n_organico": int(m.sum()) - n_s,
            "pct_patrocinado": round(100 * n_s / m.sum(), 4),
            "engajamento_total": float(eng[m].sum()),
            "engajamento_patrocinado": float(eng[m & eh_spon].sum()),
            "pct_engajamento_patrocinado": round(100 * eng[m & eh_spon].sum() / eng[m].sum(), 4),
        })
linhas.append({
    "variavel": "base", "segmento": "todos",
    "n_total": N,
    "n_patrocinado": int(eh_spon.sum()),
    "n_organico": int((~eh_spon).sum()),
    "pct_patrocinado": round(100 * eh_spon.sum() / N, 4),
    "engajamento_total": float(eng_total),
    "engajamento_patrocinado": float(eng[eh_spon].sum()),
    "pct_engajamento_patrocinado": round(100 * eng[eh_spon].sum() / eng_total, 4),
})
salvar(pd.DataFrame(linhas), "bloco6_volume_patrocinado.csv")

# ---------------------------------------------------------------- bloco 7
print("\n[Bloco 7] Validacao geral (modelo preditivo)")
CAT_FEATS = ["platform", "content_type", "content_category", "language",
             "audience_age_distribution", "audience_gender_distribution",
             "audience_location", "dia_semana"]
NUM_FEATS = ["is_sponsored_num", "follower_count", "n_hashtags", "content_length", "hora"]
X = df[CAT_FEATS + NUM_FEATS].copy()
for c in CAT_FEATS:
    X[c] = X[c].astype("category")

kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
linhas_cv, linhas_imp = [], []
for alvo in METRICAS_ABS:
    y = df[alvo].to_numpy(dtype=float)
    modelo = HistGradientBoostingRegressor(random_state=SEED)
    cv = cross_validate(modelo, X, y, cv=kf,
                        scoring=["r2", "neg_mean_absolute_error"], n_jobs=1)
    cv_dummy = cross_validate(DummyRegressor(strategy="mean"), X, y, cv=kf,
                              scoring=["r2", "neg_mean_absolute_error"], n_jobs=1)
    mae_mod = -cv["test_neg_mean_absolute_error"].mean()
    mae_med = -cv_dummy["test_neg_mean_absolute_error"].mean()
    linhas_cv.append({
        "alvo": alvo,
        "r2_medio": round(cv["test_r2"].mean(), 6),
        "r2_desvio": round(cv["test_r2"].std(), 6),
        "mae_modelo": round(mae_mod, 6),
        "mae_modelo_da_media": round(mae_med, 6),
        "dif_pct_mae_vs_media": round(100 * (mae_mod - mae_med) / mae_med, 4),
        "r2_medio_modelo_da_media": round(cv_dummy["test_r2"].mean(), 6),
    })
    print(f"  {alvo}: R2={cv['test_r2'].mean():.6f} MAE={mae_mod:.6f} (media={mae_med:.6f})")

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)
    mod_fit = HistGradientBoostingRegressor(random_state=SEED).fit(Xtr, ytr)
    imp = permutation_importance(mod_fit, Xte, yte, scoring="r2",
                                 n_repeats=10, random_state=SEED, n_jobs=1)
    ordem = np.argsort(imp.importances_mean)[::-1][:10]
    for rank, j in enumerate(ordem, 1):
        linhas_imp.append({
            "alvo": alvo, "posicao": rank, "variavel": X.columns[j],
            "queda_r2_media": round(imp.importances_mean[j], 6),
            "queda_r2_desvio": round(imp.importances_std[j], 6),
        })
salvar(pd.DataFrame(linhas_cv), "bloco7a_desempenho_modelo.csv")
salvar(pd.DataFrame(linhas_imp), "bloco7b_importancia_permutacao.csv")

print(f"\nPronto. Saidas em {OUT_DIR}")
