"""Data-quality checks and the split between pre-publication inputs and post-publication outcomes."""
import pandas as pd
from scipy import stats

IQR_FACTOR = 1.5

# Known before posting (controllable or creator context) vs. only observed after posting.
PRE_PUBLICATION = {
    "categorical": ["platform", "content_type", "content_category", "language", "weekday", "is_sponsored",
                    "sponsor_category", "disclosure_type", "disclosure_location",
                    "audience_gender_distribution", "audience_age_distribution", "audience_location"],
    "numeric": ["follower_count", "content_length", "n_hashtags", "caption_words", "hour"],
}
POST_PUBLICATION = ["views", "likes", "shares", "comments_count", "comments_text"]
IDENTIFIERS = ["id", "content_id", "creator_id", "creator_name", "content_url", "sponsor_name"]


def pre_publication_columns() -> list[str]:
    return PRE_PUBLICATION["categorical"] + PRE_PUBLICATION["numeric"]


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Nulls, duplicates and identifiers in one table."""
    content_cols = [c for c in df.columns if c not in IDENTIFIERS]
    checks = {
        "linhas": len(df),
        "linhas duplicadas (todas as colunas)": int(df.duplicated().sum()),
        "duplicadas ignorando ids": int(df[content_cols].duplicated().sum()),
        "content_id repetido": int(df["content_id"].duplicated().sum()),
        "legenda repetida": int(df["content_description"].duplicated().sum()),
        "likes > views": int((df["likes"] > df["views"]).sum()),
        "métricas negativas": int((df[["views", "likes", "shares", "comments_count"]] < 0).any(axis=1).sum()),
    }
    checks |= {f"nulos em {c}": int(n) for c, n in df.isna().sum().items() if n}
    return pd.Series(checks, name="valor").to_frame()


def outlier_report(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Tukey fences (Q1 − 1.5·IQR, Q3 + 1.5·IQR): how many points fall outside."""
    rows = []
    for c in columns:
        q1, q3 = df[c].quantile([0.25, 0.75])
        low, high = q1 - IQR_FACTOR * (q3 - q1), q3 + IQR_FACTOR * (q3 - q1)
        n_out = int(((df[c] < low) | (df[c] > high)).sum())
        rows.append({"coluna": c, "limite inferior": low, "limite superior": high, "outliers": n_out, "% outliers": n_out / len(df) * 100})
    return pd.DataFrame(rows).set_index("coluna")


def target_profile(df: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    """Mean, median, percentiles, skewness and coefficient of variation of each target."""
    rows = {}
    for t in targets:
        s = df[t]
        rows[t] = {"média": s.mean(), "mediana": s.median(), "p1": s.quantile(0.01), "p10": s.quantile(0.10),
                   "p90": s.quantile(0.90), "p99": s.quantile(0.99), "desvio": s.std(),
                   "CV (desvio/média)": s.std() / s.mean(), "assimetria": stats.skew(s), "curtose": stats.kurtosis(s)}
    return pd.DataFrame(rows).T


def survivorship_check(df: pd.DataFrame, metrics: tuple[str, ...] = ("views", "likes", "shares", "comments_count")) -> pd.DataFrame:
    """Posts with zero in each outcome metric, and its range: a dataset without failures cannot show what fails."""
    return pd.DataFrame({m: {"posts com zero": int((df[m] == 0).sum()), "mínimo": df[m].min(), "máximo": df[m].max()} for m in metrics}).T
