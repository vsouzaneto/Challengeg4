"""Loads the Kaggle CSV and derives the features shared by every analysis."""
from pathlib import Path

import numpy as np
import pandas as pd

CSV_NAME = "social_media_dataset.csv"
DATE_FORMAT = "%m/%d/%y %I:%M %p"

METRICS = ["views", "likes", "shares", "comments_count"]
PLATFORMS = ["Instagram", "TikTok", "YouTube", "Bilibili", "RedNote"]
AUDIENCE = ["audience_gender_distribution", "audience_age_distribution", "audience_location"]
CONTENT = ["platform", "content_type", "content_category", "language", "follower_tier",
           "length_bin", "n_hashtags", "daypart", "weekday", "is_sponsored", "sponsor_category"]
FEATURES = CONTENT + AUDIENCE

# Industry-standard influencer tiers (followers).
FOLLOWER_TIERS = {"nano (<10K)": 10_000, "micro (10–50K)": 50_000, "mid (50–100K)": 100_000,
                  "macro (100–500K)": 500_000, "mega (500K+)": np.inf}
LENGTH_BINS = {"curto (<60)": 60, "médio (60–180)": 180, "longo (180–360)": 360, "muito longo (360+)": np.inf}
DAYPARTS = {"madrugada": 6, "manhã": 12, "tarde": 18, "noite": 24}


def find_submission_root(start: Path | None = None) -> Path:
    """Walk up from `start` until the folder holding data/raw is found."""
    path = (start or Path.cwd()).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "data" / "raw" / CSV_NAME).exists():
            return candidate
    raise FileNotFoundError(f"{CSV_NAME} not found above {path}")


def _bin(values: pd.Series, edges: dict) -> pd.Categorical:
    bins = [-np.inf, *edges.values()]
    return pd.cut(values, bins=bins, labels=list(edges), right=False)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with engagement rates and binned/temporal features."""
    out = df.copy()
    out["post_date"] = pd.to_datetime(out["post_date"], format=DATE_FORMAT)
    out["interactions"] = out[["likes", "shares", "comments_count"]].sum(axis=1)
    out["eng_rate_views"] = out["interactions"] / out["views"]
    out["follower_tier"] = _bin(out["follower_count"], FOLLOWER_TIERS)
    out["length_bin"] = _bin(out["content_length"], LENGTH_BINS)
    out["n_hashtags"] = out["hashtags"].fillna("").str.split(",").map(lambda tags: sum(bool(t.strip()) for t in tags))
    out["daypart"] = _bin(out["post_date"].dt.hour, DAYPARTS)
    out["weekday"] = out["post_date"].dt.day_name()
    out["hour"] = out["post_date"].dt.hour
    out["caption_words"] = out["content_description"].fillna("").str.split().str.len()
    out["comments_text"] = out["comments_text"].fillna("")
    return out


def add_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Normalized metrics: per view (engagement quality) and per follower (reach efficiency)."""
    out = df.copy()
    out["like_rate"] = out["likes"] / out["views"]
    out["comment_rate"] = out["comments_count"] / out["views"]
    out["likes_per_follower"] = out["likes"] / out["follower_count"]
    out["views_per_follower"] = out["views"] / out["follower_count"]
    return out


def load_posts(root: Path | None = None) -> pd.DataFrame:
    root = root or find_submission_root()
    return add_features(pd.read_csv(root / "data" / "raw" / CSV_NAME))
