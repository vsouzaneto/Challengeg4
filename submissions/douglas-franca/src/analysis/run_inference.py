"""G3: comparação justa com efeito, IC, equivalência (TOST), MDE e controle de múltiplos testes.

Régua pré-registrada (process-log/decisions.md): a métrica de decisão é a taxa de engajamento (p.p.),
com diferença mínima relevante de ±1 p.p. Views são guardrail.
Escopo: Instagram, TikTok e YouTube; Bilibili e RedNote só como referência.

Uso: uv run python src/analysis/run_inference.py
"""

import json
import sys
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold, cross_val_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.decision.rules import SESOI_PP as SESOI  # noqa: E402
from src.decision.stats import Z90, Z95, Z_POWER, compare, finalize  # noqa: E402

RAW = ROOT / "data" / "raw" / "social_media_dataset.csv"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

MAIN = ["Instagram", "TikTok", "YouTube"]
TIER_BINS = [0, 10_000, 50_000, 100_000, 500_000, np.inf]
TIER_LABELS = ["<10K", "10–50K", "50–100K", "100–500K", "500K–1M"]
COLORS = {"surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e4e3df",
          "band": "#eceae4", "series": "#2a78d6"}
CONTROLS = ("C(platform) + C(content_type) + C(content_category) + C(tier) + C(audience_age_distribution)"
            " + C(audience_gender_distribution) + C(audience_location) + C(language)")


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    df["interactions"] = df.likes + df.shares + df.comments_count
    df["er"] = df.interactions / df.views * 100
    df["share_rate"] = df.shares / df.views * 100
    df["comment_rate"] = df.comments_count / df.views * 100
    df["tier"] = pd.cut(df.follower_count, TIER_BINS, labels=TIER_LABELS, right=False).astype(str)
    df["length_q"] = pd.qcut(df.content_length, 4, labels=["Q1 curto", "Q2", "Q3", "Q4 longo"]).astype(str)
    n_tags = df.hashtags.fillna("").str.split(",").map(lambda t: len([x for x in t if x]))
    df["hashtag_count"] = n_tags.clip(upper=3).map({0: "0", 1: "1", 2: "2", 3: "3+"})
    df["sponsored"] = df.is_sponsored.astype(int)
    return df


def level_vs_rest(df: pd.DataFrame, factors: dict[str, str]) -> pd.DataFrame:
    rows = []
    for col, label in factors.items():
        levels = TIER_LABELS if col == "tier" else sorted(df[col].unique())
        for level in [lv for lv in levels if lv in set(df[col])]:
            mask = df[col] == level
            rows.append({"fator": label, "nivel": str(level), **compare(df.loc[mask, "er"], df.loc[~mask, "er"])})
    return finalize(pd.DataFrame(rows))


def sponsorship_models(main: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = main.creator_id.astype("category").cat.codes
    for outcome, label in [("er", "taxa de engajamento (p.p.)"), ("share_rate", "share rate (p.p.)"),
                           ("comment_rate", "comment rate (p.p.)"), ("views", "views (guardrail)")]:
        fit = smf.ols(f"{outcome} ~ sponsored + {CONTROLS}", data=main).fit(
            cov_type="cluster", cov_kwds={"groups": groups})
        coef, se = fit.params["sponsored"], fit.bse["sponsored"]
        rows.append({"desfecho": label, "efeito_ajustado": coef, "se_cluster_creator": se,
                     "ic95_inf": coef - Z95 * se, "ic95_sup": coef + Z95 * se, "p": fit.pvalues["sponsored"],
                     "mde": (Z95 + Z_POWER) * se, "media_organico": main.loc[main.sponsored == 0, outcome].mean(),
                     "r2_modelo": fit.rsquared, "n": int(fit.nobs)})
    out = pd.DataFrame(rows)
    out["efeito_relativo_%"] = out.efeito_ajustado / out.media_organico * 100
    out["ic95_relativo_%"] = [f"{lo / m * 100:+.3f} a {hi / m * 100:+.3f}"
                              for lo, hi, m in zip(out.ic95_inf, out.ic95_sup, out.media_organico)]
    er = out.iloc[0]
    out["veredito_er"] = ["EQUIVALENTE" if (er.efeito_ajustado - Z90 * er.se_cluster_creator > -SESOI
                                            and er.efeito_ajustado + Z90 * er.se_cluster_creator < SESOI)
                          else "NÃO EQUIVALENTE"] + [""] * (len(out) - 1)
    return out


def sponsorship_by_condition(main: pd.DataFrame) -> pd.DataFrame:
    organic = main[main.sponsored == 0]
    sponsored = main[main.sponsored == 1]
    rows = []
    for col, label in [("platform", "plataforma"), ("tier", "faixa de seguidores"),
                       ("content_type", "formato"), ("content_category", "categoria")]:
        levels = TIER_LABELS if col == "tier" else sorted(main[col].unique())
        for level in [lv for lv in levels if lv in set(main[col])]:
            rows.append({"condicao": label, "nivel": level,
                         **compare(sponsored.loc[sponsored[col] == level, "er"], organic.loc[organic[col] == level, "er"])})
    for level in sorted(sponsored.disclosure_type.unique()):
        rows.append({"condicao": "tipo de divulgação (vs orgânico)", "nivel": level,
                     **compare(sponsored.loc[sponsored.disclosure_type == level, "er"], organic.er)})
    for level in sorted(sponsored.sponsor_category.unique()):
        rows.append({"condicao": "categoria do patrocinador (vs orgânico)", "nivel": level,
                     **compare(sponsored.loc[sponsored.sponsor_category == level, "er"], organic.er)})
    return finalize(pd.DataFrame(rows))


def sponsorship_cells(main: pd.DataFrame, min_arm: int = 30) -> pd.DataFrame:
    keys = ["platform", "content_category", "content_type", "tier"]
    rows = []
    for key, cell in main.groupby(keys):
        s, o = cell.loc[cell.sponsored == 1, "er"], cell.loc[cell.sponsored == 0, "er"]
        if len(s) >= min_arm and len(o) >= min_arm:
            rows.append({**dict(zip(keys, key)), **compare(s, o)})
    return finalize(pd.DataFrame(rows))


def followers_curve(main: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    main = main.assign(decil=pd.qcut(main.follower_count, 10, labels=False) + 1)
    curve = main.groupby("decil").agg(seguidores_min=("follower_count", "min"), seguidores_max=("follower_count", "max"),
                                      n=("er", "size"), er=("er", "mean"), sd=("er", "std"))
    curve["ic95"] = Z95 * curve.sd / np.sqrt(curve.n)
    fit = smf.ols("er ~ I(follower_count / 1e6)", data=main).fit(
        cov_type="cluster", cov_kwds={"groups": main.creator_id.astype("category").cat.codes})
    slope, se = fit.params.iloc[1], fit.bse.iloc[1]
    return curve.reset_index(), {"efeito_de_0_a_1M_pp": slope, "ic95": [slope - Z95 * se, slope + Z95 * se],
                                 "equivalente": bool(slope - Z90 * se > -SESOI and slope + Z90 * se < SESOI)}


def hashtag_pairs(main: pd.DataFrame, min_n: int = 100) -> dict:
    tags = main.hashtags.fillna("").str.lower().str.split(",").map(lambda t: sorted({x.strip() for x in t if x.strip()}))
    pairs = tags.map(lambda t: list(combinations(t, 2)))
    exploded = pairs.explode().dropna()
    counts = exploded.value_counts()
    frequent = counts[counts >= min_n].index
    rows = []
    for pair in frequent:
        mask = pd.Series(False, index=main.index)
        mask.loc[exploded[exploded == pair].index.unique()] = True
        rows.append({"par": "+".join(pair), **compare(main.loc[mask, "er"], main.loc[~mask, "er"])})
    table = finalize(pd.DataFrame(rows)) if rows else pd.DataFrame()

    singles = tags.explode().dropna()
    single_counts = singles.value_counts()
    single_rows = []
    for tag in single_counts[single_counts >= min_n].index:
        mask = pd.Series(False, index=main.index)
        mask.loc[singles[singles == tag].index.unique()] = True
        single_rows.append({"hashtag": tag, **compare(main.loc[mask, "er"], main.loc[~mask, "er"])})
    single_table = finalize(pd.DataFrame(single_rows))
    single_table.to_csv(TABLES / "inf-hashtags.csv", index=False)
    top = single_table.nlargest(3, "diferenca_pp")
    return {"hashtags_individuais_testadas": len(single_table),
            "individuais_sig_sem_correcao": int((single_table.p < 0.05).sum()),
            "individuais_falsos_positivos_esperados": round(0.05 * len(single_table), 1),
            "individuais_sig_com_bh": int((single_table.p_ajustado_bh < 0.05).sum()),
            "individuais_vereditos": single_table.veredito.value_counts().to_dict(),
            "top3_sem_correcao": [f"#{r.hashtag} {r.diferenca_pp:+.3f} p.p. (p={r.p:.3f}, p_bh={r.p_ajustado_bh:.2f})"
                                  for r in top.itertuples()],
            "posts_com_hashtag": int((tags.map(len) > 0).sum()), "pares_distintos": int(counts.size),
            "pares_com_n_min": int(len(frequent)), "n_min": min_n,
            "max_n_de_um_par": int(counts.max()) if len(counts) else 0,
            "significativos_sem_correcao": int((table.p < 0.05).sum()) if len(table) else 0,
            "significativos_com_bh": int((table.p_ajustado_bh < 0.05).sum()) if len(table) else 0}


def audience_cells(main: pd.DataFrame) -> dict:
    keys = ["audience_age_distribution", "audience_gender_distribution", "audience_location"]
    rows = []
    cell_id = main[keys].astype(str).agg(" | ".join, axis=1)
    for cid in cell_id.unique():
        mask = cell_id == cid
        rows.append({"celula": cid, **compare(main.loc[mask, "er"], main.loc[~mask, "er"])})
    table = finalize(pd.DataFrame(rows))
    table.to_csv(TABLES / "inf-audience-cells.csv", index=False)
    raw_sig = int((table.p < 0.05).sum())
    return {"celulas": len(table), "n_mediano": int(table.n_grupo.median()),
            "significativas_sem_correcao": raw_sig, "falsos_positivos_esperados": round(0.05 * len(table), 1),
            "significativas_com_bh": int((table.p_ajustado_bh < 0.05).sum()),
            "maior_diferenca_absoluta_pp": float(table.diferenca_pp.abs().max()),
            "vereditos": table.veredito.value_counts().to_dict()}


def predictive_gate(main: pd.DataFrame) -> dict:
    features = ["platform", "content_type", "content_category", "sponsored", "follower_count", "content_length",
                "audience_age_distribution", "audience_gender_distribution", "audience_location", "language",
                "disclosure_type", "hashtag_count"]
    X = pd.get_dummies(main[features], drop_first=True).astype(float)
    model = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, random_state=42)
    scores = cross_val_score(model, X, main.er, cv=GroupKFold(n_splits=5), groups=main.creator_id, scoring="r2")
    return {"modelo": "HistGradientBoosting, 5 folds agrupados por creator", "r2_medio": float(scores.mean()),
            "r2_por_fold": [round(float(s), 4) for s in scores],
            "decisao": "NO-GO" if scores.mean() < 0.01 else "reavaliar"}


def plot_forest(table: pd.DataFrame, path: Path) -> None:
    table = table.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8, 0.26 * len(table) + 1.6), facecolor=COLORS["surface"])
    ax.set_facecolor(COLORS["surface"])
    ax.axvspan(-SESOI, SESOI, color=COLORS["band"], zorder=0)
    ax.axvline(0, color=COLORS["ink2"], lw=1, zorder=1)
    y = np.arange(len(table))
    ax.hlines(y, table.ic95_inf, table.ic95_sup, color=COLORS["series"], lw=2, zorder=2)
    ax.scatter(table.diferenca_pp, y, s=36, color=COLORS["series"], edgecolor=COLORS["surface"], lw=2, zorder=3)
    ax.set_yticks(y, [f"{f}: {n}" for f, n in zip(table.fator, table.nivel)], fontsize=8, color=COLORS["ink"])
    ax.set_xlim(-1.3, 1.3)
    ax.set_xlabel("Diferença na taxa de engajamento vs. resto (p.p.), IC 95%", color=COLORS["ink2"], fontsize=9)
    ax.text(0, len(table) + 0.2, "faixa irrelevante para decisão (±1 p.p.)", ha="center", va="bottom",
            fontsize=8, color=COLORS["ink2"], zorder=4,
            bbox={"facecolor": COLORS["band"], "edgecolor": "none", "pad": 2})
    ax.set_title("Nenhum fator move a taxa de engajamento para fora da faixa irrelevante\n"
                 "Instagram, TikTok e YouTube · 31.214 posts", loc="left", fontsize=11, color=COLORS["ink"])
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=COLORS["ink2"], labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=COLORS["surface"])
    plt.close(fig)


def plot_followers(curve: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.6), facecolor=COLORS["surface"])
    ax.set_facecolor(COLORS["surface"])
    mean = curve.er.mean()
    ax.axhspan(mean - SESOI, mean + SESOI, color=COLORS["band"], zorder=0)
    x = curve.decil
    ax.errorbar(x, curve.er, yerr=curve.ic95, fmt="o-", color=COLORS["series"], lw=2, ms=6,
                mec=COLORS["surface"], mew=2, capsize=0, zorder=3)
    ax.set_xticks(x, [f"{lo / 1000:.0f}–{hi / 1000:.0f}K" for lo, hi in zip(curve.seguidores_min, curve.seguidores_max)],
                  fontsize=7, rotation=30, color=COLORS["ink2"])
    ax.set_ylim(mean - 1.5, mean + 1.5)
    ax.set_ylabel("Taxa de engajamento (%)", color=COLORS["ink2"], fontsize=9)
    ax.set_title("Seguidores não mudam a taxa de engajamento: não existe threshold de tamanho de creator\n"
                 "Decis de seguidores · faixa cinza = média ±1 p.p.", loc="left", fontsize=11, color=COLORS["ink"])
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(COLORS["grid"])
    ax.tick_params(axis="y", colors=COLORS["ink2"], labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=COLORS["surface"])
    plt.close(fig)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = load()
    main_df = df[df.platform.isin(MAIN)].copy()
    summary: dict = {"sesoi_pp": SESOI, "n_total": len(df), "n_escopo": len(main_df),
                     "er_media_escopo": main_df.er.mean()}

    platforms = level_vs_rest(df, {"platform": "plataforma (5, com referência)"})
    platforms.to_csv(TABLES / "inf-platforms-all.csv", index=False)

    factors = {"platform": "plataforma", "content_type": "formato", "content_category": "categoria",
               "tier": "seguidores", "sponsored": "patrocinado (1=sim)", "disclosure_type": "divulgação",
               "audience_age_distribution": "idade audiência", "audience_gender_distribution": "gênero audiência",
               "audience_location": "país audiência", "language": "idioma", "length_q": "content_length (quartil)",
               "hashtag_count": "nº hashtags"}
    lvr = level_vs_rest(main_df, factors)
    lvr.to_csv(TABLES / "inf-factors.csv", index=False)
    summary["fatores"] = {"comparacoes": len(lvr), "vereditos": lvr.veredito.value_counts().to_dict(),
                          "maior_diferenca_abs_pp": float(lvr.diferenca_pp.abs().max()),
                          "maior_ic95_abs_pp": float(np.maximum(lvr.ic95_inf.abs(), lvr.ic95_sup.abs()).max()),
                          "mde_mediano_pp": float(lvr.mde_pp.median()), "mde_max_pp": float(lvr.mde_pp.max())}
    plot_forest(lvr, FIGURES / "g3-forest-fatores.png")

    models = sponsorship_models(main_df)
    models.to_csv(TABLES / "inf-sponsorship-adjusted.csv", index=False)
    summary["patrocinio_ajustado"] = models.round(5).to_dict(orient="records")

    by_cond = sponsorship_by_condition(main_df)
    by_cond.to_csv(TABLES / "inf-sponsorship-conditions.csv", index=False)
    summary["patrocinio_condicoes"] = {"comparacoes": len(by_cond), "vereditos": by_cond.veredito.value_counts().to_dict(),
                                       "maior_diferenca_abs_pp": float(by_cond.diferenca_pp.abs().max())}

    cells = sponsorship_cells(main_df)
    cells.to_csv(TABLES / "inf-sponsorship-cells.csv", index=False)
    summary["patrocinio_celulas"] = {"celulas_n30_por_braco": len(cells), "vereditos": cells.veredito.value_counts().to_dict(),
                                     "diferenca_min_pp": float(cells.diferenca_pp.min()),
                                     "diferenca_max_pp": float(cells.diferenca_pp.max()),
                                     "mde_mediano_pp": float(cells.mde_pp.median()),
                                     "p_bruto_menor_005": int((cells.p < 0.05).sum()),
                                     "p_bh_menor_005": int((cells.p_ajustado_bh < 0.05).sum())}

    curve, slope = followers_curve(main_df)
    curve.to_csv(TABLES / "inf-followers-deciles.csv", index=False)
    summary["seguidores"] = slope
    plot_followers(curve, FIGURES / "g3-seguidores-decis.png")

    summary["hashtags"] = hashtag_pairs(main_df)
    summary["audiencia"] = audience_cells(main_df)
    summary["modelo_preditivo"] = predictive_gate(main_df)
    summary["frequencia"] = "não testável: cada creator tem 10–11 posts em 2 anos (DQ-09)"

    (TABLES / "inf-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float))
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=float))


if __name__ == "__main__":
    main()
