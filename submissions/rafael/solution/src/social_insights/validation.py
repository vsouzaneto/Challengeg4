"""Method validation: inject a known effect into the data and check the pipeline recovers it (positive control)."""
import numpy as np
import pandas as pd

SEED = 42


def demo_segment(df: pd.DataFrame) -> pd.Series:
    """A plausible "real" winning recipe used as the planted effect."""
    return (df["platform"] == "TikTok") & (df["content_type"] == "video") & (df["content_category"] == "tech")


def inject_uplift(df: pd.DataFrame, mask: pd.Series, metric: str, uplift: float, seed: int = SEED) -> pd.DataFrame:
    """Copy of df where `metric` is redrawn as Poisson(mean × (1 + uplift)) on masked rows."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    out.loc[mask, metric] = rng.poisson(out.loc[mask, metric] * (1 + uplift))
    return out


def inject_engagement_uplift(df: pd.DataFrame, mask: pd.Series, uplift: float, seed: int = SEED) -> pd.DataFrame:
    """Copy of df where likes on masked rows get +uplift (Poisson redraw) and engagement columns are recomputed."""
    out = inject_uplift(df, mask, "likes", uplift, seed)
    out["interactions"] = out[["likes", "shares", "comments_count"]].sum(axis=1)
    out["eng_rate_views"] = out["interactions"] / out["views"]
    return out


def inject_creator_effect(df: pd.DataFrame, metric: str, relative_sd: float, seed: int = SEED) -> pd.DataFrame:
    """Copy of df where each creator gets a persistent multiplier ~ N(1, relative_sd) on `metric` (a "who posts matters" world)."""
    rng = np.random.default_rng(seed)
    creators = df["creator_id"].unique()
    factor = pd.Series(1 + rng.normal(0, relative_sd, len(creators)), index=creators)
    out = df.copy()
    out[metric] = (out[metric] * out["creator_id"].map(factor)).round().astype(int)
    return out
