"""G1: confere contra o dataset as afirmações numéricas das respostas de baseline das IAs.

Uso: uv run python src/audit/verify_baseline_claims.py
Saída: outputs/tables/g1-baseline-claims-check.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "social_media_dataset.csv"
OUT = ROOT / "outputs" / "tables" / "g1-baseline-claims-check.csv"

TIERS = [0, 10_000, 50_000, 100_000, 500_000, 1_000_000, np.inf]
TIER_LABELS = ["nano <10K", "micro 10-50K", "mid 50-100K", "mid-high 100-500K", "macro 500K-1M", "mega >1M"]


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    df["post_date"] = pd.to_datetime(df["post_date"], format="mixed")
    df["interactions"] = df["likes"] + df["shares"] + df["comments_count"]
    df["er_pp"] = df["interactions"] / df["views"] * 100
    df["share_rate_pp"] = df["shares"] / df["views"] * 100
    df["er_followers_pp"] = df["interactions"] / df["follower_count"] * 100
    df["tier"] = pd.cut(df["follower_count"], TIERS, labels=TIER_LABELS, right=False)
    return df


def anova(df: pd.DataFrame, col: str, metric: str = "er_pp") -> tuple[float, float]:
    groups = [g[metric].to_numpy() for _, g in df.groupby(col, observed=True)]
    means = df.groupby(col, observed=True)[metric].mean()
    return stats.f_oneway(*groups).pvalue, means.max() - means.min()


def main() -> None:
    df = load()
    rows: list[dict] = []

    def add(source, claim, observed, verdict):
        rows.append({"fonte": source, "afirmacao": claim, "observado": observed, "veredito": verdict})

    # Perfil básico
    add("DeepSeek", "CSV tem 7.109 linhas", f"{len(df):,} linhas", "FALSO (leu só 37% do arquivo)")
    add("Claude", "período 01/01/2024 a 09/09/2024",
        f"{df.post_date.min():%d/%m/%Y} a {df.post_date.max():%d/%m/%Y}", "FALSO")
    add("Claude/Grok", "ER médio ~19,9%", f"{df.er_pp.mean():.3f}%", "VERDADEIRO")

    # Plataforma, formato, categoria
    p, rng = anova(df, "platform")
    add("Claude", "plataformas: ANOVA p=0,55; diferença máx. 0,10 p.p.", f"p={p:.3f}; diferença máx. {rng:.4f} p.p.",
        "p OK; amplitude superestimada ~10x")
    p, rng = anova(df, "content_type")
    add("Claude", "tipo de conteúdo: ANOVA p=0,21", f"p={p:.3f}; diferença máx. {rng:.4f} p.p.", "VERDADEIRO")
    p, rng = anova(df, "content_category")
    add("Claude", "categoria: ANOVA p=0,44", f"p={p:.3f}; categorias={sorted(df.content_category.unique())}", "VERDADEIRO")
    has_health = "health" in {c.lower() for c in df.content_category.unique()}
    add("Gemini", "nichos 'Tech e Health' são a interseção de ouro",
        f"categoria health existe? {has_health}", "FABRICADO" if not has_health else "conferir")

    # Patrocínio
    s = df[df.is_sponsored]
    o = df[~df.is_sponsored]
    t = stats.ttest_ind(s.er_pp, o.er_pp, equal_var=False)
    diff = s.er_pp.mean() - o.er_pp.mean()
    rel = diff / o.er_pp.mean() * 100
    add("Claude/Grok", "orgânico vs patrocinado: 0,01 p.p., p=0,80",
        f"diferença {diff:+.4f} p.p.; p={t.pvalue:.3f}", "VERDADEIRO (ordem de grandeza)")
    add("Gemini", "patrocínio reduz ER em 15%", f"variação relativa {rel:+.3f}%", "FALSO")
    add("Claude", "followers médios patrocinado 499.924 vs orgânico 499.855",
        f"{s.follower_count.mean():,.0f} vs {o.follower_count.mean():,.0f}", "VERDADEIRO")
    p, rng = anova(s, "sponsor_category")
    best = s.groupby("sponsor_category").er_pp.mean().sort_values(ascending=False).head(3)
    add("Grok", "Cosmetics e Food têm leve vantagem entre sponsors",
        f"ANOVA p={p:.3f}; top3={', '.join(f'{k} {v:.3f}' for k, v in best.items())}",
        "ruído (p>0,05)" if p > 0.05 else "sinal")

    # Tamanho de creator
    r = stats.pearsonr(df.follower_count, df.er_pp)
    add("Claude", "correlação seguidores x ER r=-0,002", f"r={r.statistic:.4f}; p={r.pvalue:.3f}", "VERDADEIRO")
    r_views = stats.pearsonr(np.log(df.follower_count), df.views)
    add("ChatGPT", "hipótese: mais seguidores -> mais views", f"r(log followers, views)={r_views.statistic:.4f}; p={r_views.pvalue:.3f}",
        "hipótese não se sustenta")
    by_tier = df.groupby("tier", observed=True).agg(n=("id", "size"), er=("er_pp", "mean"), er_f=("er_followers_pp", "mean"))
    add("Grok", "ER/followers: nano 51,7%, micro 8,1% (nano/micro 10-180x melhores)",
        "; ".join(f"{i}: n={v.n}, ER/fol={v.er_f:.2f}%, ER/views={v.er:.3f}%" for i, v in by_tier.iterrows()),
        "ARTEFATO: interações ~constantes divididas por seguidores = 1/x; ER por view é igual entre faixas")
    add("Gemini", "micro-creators ER 4,8-5,2%; mega <1% ou 1,8%",
        f"ER por view em todas as faixas entre {by_tier.er.min():.2f}% e {by_tier.er.max():.2f}%; mega (>1M) n={int(by_tier.n.get('mega >1M', 0))}",
        "FABRICADO (não existe creator >1M: máx. " + f"{df.follower_count.max():,})")

    # A dica do README: "3,2x mais shares"
    df["length_bucket"] = pd.cut(df.content_length, [0, 30, 60, 180, 600], right=False,
                                 labels=["<30", "30-60", "60-180", "180-600"])
    cells = (df.groupby(["platform", "content_category", "content_type", "tier", "length_bucket"], observed=True)
               .agg(n=("id", "size"), shares=("shares", "mean")))
    cells = cells[cells.n >= 30]
    platform_mean = df.groupby("platform").shares.mean()
    cells["ratio"] = cells.shares / platform_mean.reindex(cells.index.get_level_values("platform")).to_numpy()
    add("Gemini (dica do README)", "TikTok + Tech + vídeo 30-60s + micro = 3,2x mais shares que a média",
        f"{len(cells)} células com n>=30; razão shares/média da plataforma entre {cells.ratio.min():.3f}x e {cells.ratio.max():.3f}x",
        f"FALSO: teto real {cells.ratio.max():.2f}x")
    tiktok_cell = df[(df.platform == "TikTok") & (df.content_category == "tech") & (df.content_type == "video")
                     & df.content_length.between(30, 60) & df.follower_count.between(10_000, 50_000)]
    add("Gemini", "célula exata citada (TikTok, tech, video, 30-60, 10-50K)",
        f"n={len(tiktok_cell)}; shares médios={tiktok_cell.shares.mean():.1f} vs TikTok={platform_mean['TikTok']:.1f}",
        "FALSO")
    add("Gemini", "vídeos longos (>3 min) no TikTok", f"content_length máx.={df.content_length.max()} (unidade não documentada)",
        "não verificável")

    # Modelo preditivo
    X = pd.get_dummies(df[["platform", "content_type", "content_category", "is_sponsored"]], drop_first=True)
    X[["follower_count", "content_length"]] = df[["follower_count", "content_length"]]
    X_tr, X_te, y_tr, y_te = train_test_split(X, df.er_pp, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=100, min_samples_leaf=50, n_jobs=-1, random_state=42).fit(X_tr, y_tr)
    add("Claude/Grok", "Random Forest R² ≈ 0", f"R² teste={rf.score(X_te, y_te):.4f}", "VERDADEIRO")

    # Forense: Poisson com lambda fixo (não afirmado por nenhuma IA)
    for col in ["views", "likes", "shares", "comments_count"]:
        m, sd = df[col].mean(), df[col].std()
        add("Nosso achado", f"{col} ~ Poisson(λ fixo): desvio = √média",
            f"média={m:.1f}; desvio={sd:.2f}; √média={np.sqrt(m):.2f}; razão var/média={sd**2 / m:.3f}", "a formalizar no G2")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    with pd.option_context("display.max_colwidth", 140, "display.width", 250):
        print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
