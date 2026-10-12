#!/usr/bin/env python3
"""
Auditoria de sinal do dataset "Social Media Sponsorship & Engagement" (Kaggle / omenkj).

Uso:
    python run_audit.py caminho/para/social_media_dataset.csv [--out outputs]

Gera:
    outputs/summary.json        -> números usados no relatório e no dashboard
    outputs/segments.csv        -> engajamento médio por célula (plataforma x tipo x categoria x patrocínio)
    outputs/fig_*.svg           -> gráficos do relatório

Pergunta que o script responde: "existe ALGUM sinal nesses dados que justifique uma decisão?"
Antes de responder "o que funciona", a gente tem que responder "dá pra confiar?".
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

# ---------- helpers ----------
def eng_rate(d):
    return (d["likes"] + d["shares"] + d["comments_count"]) / d["views"]

def load(path):
    df = pd.read_csv(path)
    df["post_date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p", errors="coerce")
    df["eng"] = eng_rate(df)
    df["n_hash"] = df["hashtags"].fillna("").apply(lambda s: 0 if s == "" else len(s.split(",")))
    df["hour"] = df["post_date"].dt.hour
    df["dow"] = df["post_date"].dt.dayofweek
    df["month"] = df["post_date"].dt.to_period("M").astype(str)
    # faixa de creator (como o README do challenge sugere analisar)
    df["creator_tier"] = pd.cut(df["follower_count"], [0, 10_000, 50_000, 250_000, 1e9],
                                labels=["<10K", "10K-50K", "50K-250K", ">250K"])
    return df

FACTORS = ["platform", "content_type", "content_category", "language", "is_sponsored",
           "disclosure_type", "sponsor_category", "disclosure_location", "audience_age_distribution",
           "audience_gender_distribution", "audience_location", "creator_tier", "hour", "dow", "month", "n_hash"]
METRICS = ["views", "likes", "shares", "comments_count", "eng"]

# ---------- testes ----------
def kruskal_grid(df):
    rows = []
    for m in METRICS:
        for f in FACTORS:
            groups = [g[m].dropna().values for _, g in df.groupby(f, observed=True) if len(g) > 5]
            p = stats.kruskal(*groups).pvalue if len(groups) > 1 else np.nan
            rows.append({"metric": m, "factor": f, "p": float(p)})
    return pd.DataFrame(rows)

def split_half(df, keys):
    a = df.sample(frac=0.5, random_state=1)
    b = df.drop(a.index)
    ca = a.groupby(keys, observed=True)["eng"].mean()
    cb = b.groupby(keys, observed=True)["eng"].mean()
    idx = ca.index.intersection(cb.index)
    return float(np.corrcoef(ca.loc[idx], cb.loc[idx])[0, 1])

def model_r2(df):
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import cross_val_score
    X = pd.get_dummies(df[["platform", "content_type", "content_category", "language", "is_sponsored",
                           "disclosure_type", "audience_age_distribution", "audience_gender_distribution",
                           "audience_location", "content_length", "follower_count", "hour", "dow", "n_hash"]],
                       drop_first=True)
    out = {}
    for y in ["eng", "views", "shares"]:
        s = cross_val_score(HistGradientBoostingRegressor(max_iter=200), X, df[y], cv=5, scoring="r2")
        out[y] = {"r2_mean": float(s.mean()), "r2_std": float(s.std())}
    return out

def naive_findings(df):
    """O que uma análise 'copiar o brief na IA' reportaria como insight."""
    cells = (df.groupby(["platform", "content_type", "content_category", "is_sponsored"], observed=True)["eng"]
               .agg(["mean", "count"]).reset_index().sort_values("mean", ascending=False))
    base = df["eng"].mean()
    top = cells.iloc[0]
    bot = cells.iloc[-1]
    sp = df.groupby("is_sponsored")["eng"].mean()
    plat = df.groupby("platform")["eng"].mean().sort_values(ascending=False)
    tier = df.groupby("creator_tier", observed=True)["eng"].mean()
    return {
        "top_cell": {k: (bool(v) if isinstance(v, (np.bool_, bool)) else (float(v) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, (int, np.integer)) else str(v)))) for k, v in top.items()},
        "bottom_cell": {k: (bool(v) if isinstance(v, (np.bool_, bool)) else (float(v) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, (int, np.integer)) else str(v)))) for k, v in bot.items()},
        "lift_top_vs_base_pct": float((top["mean"] / base - 1) * 100),
        "spread_top_vs_bottom_pct": float((top["mean"] / bot["mean"] - 1) * 100),
        "sponsored_eng": float(sp.get(True)), "organic_eng": float(sp.get(False)),
        "platform_rank": {k: float(v) for k, v in plat.items()},
        "creator_tier_eng": {str(k): float(v) for k, v in tier.items()},
    }, cells

# ---------- gráficos ----------
def figures(df, grid, cells, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    C1, C2, C3 = "#2F5D8A", "#C97B2A", "#8A8A8A"

    # 1. views: histograma vs Normal ajustada
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["views"], bins=60, density=True, color=C1, alpha=.75, label="views observadas")
    mu, sd = df["views"].mean(), df["views"].std()
    x = np.linspace(df["views"].min(), df["views"].max(), 300)
    ax.plot(x, stats.norm.pdf(x, mu, sd), color=C2, lw=2, label=f"Normal({mu:.0f}, {sd:.0f})")
    ax.set_title("Views por post: 52 mil posts, todos entre 9.6K e 10.6K views")
    ax.set_xlabel("views"); ax.set_ylabel("densidade"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{out}/fig_01_views_normal.svg"); plt.close(fig)

    # 2. engajamento por plataforma x patrocínio com IC95
    g = df.groupby(["platform", "is_sponsored"])["eng"].agg(["mean", "sem", "count"]).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    plats = sorted(df["platform"].unique()); xs = np.arange(len(plats)); w = .38
    for i, (sp, col, lab) in enumerate([(False, C1, "orgânico"), (True, C2, "patrocinado")]):
        sub = g[g.is_sponsored == sp].set_index("platform").reindex(plats)
        ax.bar(xs + (i - .5) * w, sub["mean"] * 100, w, yerr=sub["sem"] * 196, color=col, label=lab, capsize=3)
    ax.set_xticks(xs, plats); ax.set_ylabel("engagement rate (%)")
    ax.set_ylim(19.5, 20.3)
    ax.set_title("Engajamento por plataforma × patrocínio (IC 95%) — tudo em 19,9%")
    ax.legend(); fig.tight_layout(); fig.savefig(f"{out}/fig_02_eng_platform_sponsored.svg"); plt.close(fig)

    # 3. histograma de p-values
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(grid["p"].dropna(), bins=10, range=(0, 1), color=C1, alpha=.8)
    ax.axhline(len(grid) / 10, color=C2, ls="--", label="esperado se nada tiver efeito (uniforme)")
    ax.set_title(f"{len(grid)} testes fator × métrica: distribuição de p-values")
    ax.set_xlabel("p-value (Kruskal-Wallis)"); ax.set_ylabel("nº de testes"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{out}/fig_03_pvalues.svg"); plt.close(fig)

    # 4. split-half: o ranking de segmentos se replica?
    a = df.sample(frac=.5, random_state=1); b = df.drop(a.index)
    keys = ["platform", "content_type", "content_category", "is_sponsored"]
    ca = a.groupby(keys, observed=True)["eng"].mean(); cb = b.groupby(keys, observed=True)["eng"].mean()
    idx = ca.index.intersection(cb.index)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(ca.loc[idx] * 100, cb.loc[idx] * 100, color=C1, alpha=.7)
    r = np.corrcoef(ca.loc[idx], cb.loc[idx])[0, 1]
    ax.set_xlabel("engajamento do segmento — metade A (%)"); ax.set_ylabel("mesmo segmento — metade B (%)")
    ax.set_title(f"120 segmentos: o 'melhor' numa metade não é melhor na outra (r = {r:.2f})")
    fig.tight_layout(); fig.savefig(f"{out}/fig_04_split_half.svg"); plt.close(fig)

    # 5. follower_count do mesmo creator ao longo dos posts
    top_creators = df["creator_id"].value_counts().index[:6]
    fig, ax = plt.subplots(figsize=(7, 4))
    for c in top_creators:
        s = df[df.creator_id == c].sort_values("post_date")
        ax.plot(range(len(s)), s["follower_count"] / 1e3, marker="o", lw=1, label=c)
    ax.set_xlabel("post nº (ordem cronológica)"); ax.set_ylabel("followers (mil)")
    ax.set_title("Mesmo creator_id, followers sorteados a cada post: 'creator' não é uma entidade")
    ax.legend(fontsize=7, ncol=2); fig.tight_layout(); fig.savefig(f"{out}/fig_05_creator_followers.svg"); plt.close(fig)

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    df = load(a.csv)

    grid = kruskal_grid(df)
    naive, cells = naive_findings(df)
    cells.to_csv(f"{a.out}/segments.csv", index=False)

    num = ["content_length", "views", "likes", "shares", "comments_count", "follower_count"]
    corr = df[num].corr()
    creator = df.groupby("creator_id").agg(n=("id", "size"), n_names=("creator_name", "nunique"),
                                           n_followers=("follower_count", "nunique"), n_platforms=("platform", "nunique"))
    sp_t = stats.ttest_ind(df.loc[df.is_sponsored, "eng"], df.loc[~df.is_sponsored, "eng"])

    summary = {
        "n_posts": int(len(df)), "n_creators": int(df.creator_id.nunique()),
        "date_min": str(df.post_date.min().date()), "date_max": str(df.post_date.max().date()),
        "metrics": {m: {"mean": float(df[m].mean()), "std": float(df[m].std()), "min": float(df[m].min()),
                        "max": float(df[m].max()), "cv_pct": float(df[m].std() / df[m].mean() * 100)} for m in num + ["eng"]},
        "zeros": {m: int((df[m] == 0).sum()) for m in num},
        "max_abs_corr_between_numeric": float(np.abs(corr.values[np.triu_indices(len(num), 1)]).max()),
        "views_normality_shapiro_p": float(stats.shapiro(df["views"].sample(5000, random_state=0)).pvalue),
        "followers_uniform_ks_p": float(stats.kstest((df.follower_count - df.follower_count.min()) /
                                                      (df.follower_count.max() - df.follower_count.min()), "uniform").pvalue),
        "tests_total": int(grid["p"].notna().sum()),
        "tests_p_below_05": int((grid["p"] < .05).sum()),
        "tests_expected_by_chance": float(grid["p"].notna().sum() * .05),
        "sponsored_vs_organic": {"sponsored_eng": naive["sponsored_eng"], "organic_eng": naive["organic_eng"],
                                 "t_p": float(sp_t.pvalue)},
        "split_half_r_cells": split_half(df, ["platform", "content_type", "content_category", "is_sponsored"]),
        "split_half_r_platform_tier": split_half(df, ["platform", "creator_tier"]),
        "model": model_r2(df),
        "creator_consistency": {"posts_per_creator": float(creator.n.mean()),
                                "distinct_names_per_creator": float(creator.n_names.mean()),
                                "distinct_follower_counts_per_creator": float(creator.n_followers.mean()),
                                "distinct_platforms_per_creator": float(creator.n_platforms.mean())},
        "text": {"unique_descriptions": int(df.content_description.nunique()),
                 "unique_sponsor_names": int(df.sponsor_name.nunique()),
                 "sponsored_posts": int(df.is_sponsored.sum())},
        "mix": {f: {str(k): float(v) for k, v in df[f].value_counts(normalize=True).items()}
                for f in ["platform", "content_type", "content_category", "is_sponsored", "creator_tier"]},
        "naive_findings": naive,
        "grid_pvalues": grid.to_dict(orient="records"),
    }
    with open(f"{a.out}/summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    figures(df, grid, cells, a.out)

    # veredito no terminal
    print(f"posts={summary['n_posts']}  testes={summary['tests_total']}  p<.05={summary['tests_p_below_05']} "
          f"(acaso≈{summary['tests_expected_by_chance']:.1f})  split-half r={summary['split_half_r_cells']:.2f}  "
          f"R² modelo(eng)={summary['model']['eng']['r2_mean']:.4f}")
    verdict = "SEM SINAL — não use para decidir" if (summary["tests_p_below_05"] <= summary["tests_expected_by_chance"] * 1.5
                                                        and summary["split_half_r_cells"] < .5) else "há sinal — prossiga com cautela"
    print("VEREDITO:", verdict)

if __name__ == "__main__":
    main()
