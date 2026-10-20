"""Pre-publication probability that a post lands in the top 5% (of its media type) for views, likes or comments.

One model per (metric, media type). Candidates: base rate, empirical-Bayes segment rate (platform × category × language),
logistic regression and calibrated LightGBM. Temporal validation (train on the past, test on the most recent posts);
a model is adopted only if it beats the base rate on the Brier score AND its AUC > 0.5 survives BH correction across
all (metric × media type × model) tests. The segment history is always reported alongside, with a 90% credible interval.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .views_forecast import add_creator_history, temporal_split

SEED = 42
TOP_Q = 0.95
METRICS = ["views", "likes", "comments_count"]
SEGMENT = ["platform", "content_category", "language"]
PRIOR_STRENGTH = 200  # pseudo-posts pulling small segments toward the base rate
CATEGORICAL = ["platform", "content_category", "language", "is_sponsored", "sponsor_category", "disclosure_type",
               "disclosure_location", "weekday", "daypart", "audience_gender_distribution", "audience_age_distribution", "audience_location"]
NUMERIC = ["content_length", "caption_words", "n_hashtags", "follower_count", "hour",
           "creator_posts_before", "creator_mean_views_before", "creator_last_views", "days_since_last_post"]
CANDIDATES = ["taxa base", "segmento (plataforma × categoria × idioma)", "regressão logística", "LightGBM calibrado"]
CALIBRATION_BINS = 5


def label_hits(df: pd.DataFrame, metric: str, q: float = TOP_Q, within: str = "content_type") -> pd.Series:
    """True if the post is in the top (1 − q) of `metric` among posts of the same media type."""
    return df[metric] >= df.groupby(within)[metric].transform("quantile", q)


class BaseRate:
    def fit(self, X, y):
        self.rate_ = float(np.mean(y))
        return self

    def predict_proba(self, X):
        return np.column_stack([1 - np.full(len(X), self.rate_), np.full(len(X), self.rate_)])


class SegmentRate:
    """Empirical-Bayes hit rate per segment: (hits + k·base) / (n + k)."""

    def __init__(self, keys=SEGMENT, k: float = PRIOR_STRENGTH):
        self.keys, self.k = keys, k

    def fit(self, X, y):
        self.base_ = float(np.mean(y))
        g = pd.DataFrame({"key": self._key(X), "y": np.asarray(y)}).groupby("key")["y"].agg(["sum", "size"])
        self.table_ = (g["sum"] + self.k * self.base_) / (g["size"] + self.k)
        self.sizes_, self.hits_ = g["size"], g["sum"]
        return self

    def interval(self, key: str, level: float = 0.90) -> tuple[float, float]:
        """Beta posterior credible interval of the segment hit rate."""
        hits, n = self.hits_.get(key, 0), self.sizes_.get(key, 0)
        a, b = hits + self.k * self.base_, n - hits + self.k * (1 - self.base_)
        return tuple(stats.beta.ppf([(1 - level) / 2, (1 + level) / 2], a, b))

    def _key(self, X):
        return X[self.keys].astype(str).agg(" · ".join, axis=1)

    def predict_proba(self, X):
        p = self._key(X).map(self.table_).fillna(self.base_).values
        return np.column_stack([1 - p, p])


def make_candidate(name: str):
    encoder = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
                                 ("num", StandardScaler(), NUMERIC)])
    if name == "taxa base":
        return BaseRate()
    if name.startswith("segmento"):
        return SegmentRate()
    if name == "regressão logística":
        return make_pipeline(encoder, LogisticRegression(C=0.1, max_iter=2000))
    lgbm = LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=100, subsample=0.8,
                          subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=SEED)
    return CalibratedClassifierCV(make_pipeline(encoder, lgbm), method="sigmoid", cv=3)


def _features(df: pd.DataFrame) -> pd.DataFrame:
    X = df[CATEGORICAL + NUMERIC].copy()
    X[CATEGORICAL] = X[CATEGORICAL].astype(str)
    X[NUMERIC] = X[NUMERIC].fillna(X[NUMERIC].median())
    return X


def _scores(y: np.ndarray, p: np.ndarray, base: float) -> dict:
    auc = roc_auc_score(y, p) if len(np.unique(p)) > 1 else 0.5
    hits, misses = p[y == 1], p[y == 0]
    p_auc = stats.mannwhitneyu(hits, misses, alternative="greater").pvalue if len(np.unique(p)) > 1 else 1.0
    brier, brier_base = brier_score_loss(y, p), brier_score_loss(y, np.full(len(y), base))
    top_decile = p >= np.quantile(p, 0.9)
    return {"AUC": auc, "p (AUC > 0,5)": p_auc, "Brier": brier, "ganho Brier vs. base (%)": (1 - brier / brier_base) * 100,
            "taxa real no top 10% previsto (%)": y[top_decile].mean() * 100 if len(np.unique(p)) > 1 else base * 100}


def evaluate(df: pd.DataFrame, metric: str, media_type: str, candidates: list[str] = CANDIDATES) -> tuple[pd.DataFrame, dict]:
    """Temporal hold-out for one (metric, media type). Returns (scores table, test predictions per candidate)."""
    data = add_creator_history(df)
    data["hit"] = label_hits(data, metric)
    data = data[data["content_type"] == media_type]
    tr, te, _ = temporal_split(data)
    X_tr, X_te = _features(data.loc[tr]), _features(data.loc[te])
    y_tr, y_te = data.loc[tr, "hit"].astype(int).values, data.loc[te, "hit"].astype(int).values
    base = y_tr.mean()
    rows, preds = [], {}
    for name in candidates:
        p = make_candidate(name).fit(X_tr, y_tr).predict_proba(X_te)[:, 1]
        preds[name] = p
        rows.append({"métrica": metric, "formato": media_type, "modelo": name, "posts teste": len(y_te), "hits teste": int(y_te.sum()),
                     **_scores(y_te, p, base)})
    return pd.DataFrame(rows), {"y": y_te, **preds}


def mark_adoptable(evaluation: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """BH over the AUC p-values of every non-baseline candidate; adoptable = q < alpha and better Brier than the base rate."""
    out = evaluation.copy()
    candidates = out["modelo"] != "taxa base"
    out["q (AUC)"] = np.nan
    out.loc[candidates, "q (AUC)"] = multipletests(out.loc[candidates, "p (AUC > 0,5)"], method="fdr_bh")[1]
    out["adotável"] = candidates & (out["q (AUC)"] < alpha) & (out["ganho Brier vs. base (%)"] > 0)
    return out


def calibration_table(y: np.ndarray, p: np.ndarray, bins: int = CALIBRATION_BINS) -> pd.DataFrame:
    """Predicted vs. observed hit rate per quantile bin of the predicted probability."""
    frame = pd.DataFrame({"y": y, "p": p})
    frame["faixa"] = pd.qcut(frame["p"].rank(method="first"), bins, labels=[f"Q{i}" for i in range(1, bins + 1)])
    return frame.groupby("faixa", observed=True).agg(previsto=("p", "mean"), observado=("y", "mean"), posts=("y", "size")).mul(
        {"previsto": 100, "observado": 100, "posts": 1})


@dataclass
class HitPredictor:
    """Chance (%) of a planned post landing in the top 5% of its media type, per metric."""
    models: dict = field(default_factory=dict)       # (metric, media type) → fitted model
    chosen: dict = field(default_factory=dict)       # (metric, media type) → model name
    base_rates: dict = field(default_factory=dict)
    segment_tables: dict = field(default_factory=dict)
    evaluation: pd.DataFrame | None = None

    @classmethod
    def train(cls, df: pd.DataFrame, metrics: list[str] = METRICS, media_types: list[str] | None = None) -> "HitPredictor":
        media_types = media_types or sorted(df["content_type"].unique())
        data = add_creator_history(df)
        predictor = cls()
        evaluation = mark_adoptable(pd.concat([evaluate(df, m, t)[0] for m in metrics for t in media_types], ignore_index=True))
        for metric in metrics:
            data["hit"] = label_hits(data, metric)
            for media in media_types:
                table = evaluation[(evaluation["métrica"] == metric) & (evaluation["formato"] == media)]
                ok = table[table["adotável"]].sort_values("ganho Brier vs. base (%)", ascending=False)
                name = ok.iloc[0]["modelo"] if len(ok) else "taxa base"
                sub = data[data["content_type"] == media]
                X, y = _features(sub), sub["hit"].astype(int).values
                predictor.models[(metric, media)] = make_candidate(name).fit(X, y)
                predictor.chosen[(metric, media)] = name
                predictor.base_rates[(metric, media)] = float(y.mean())
                predictor.segment_tables[(metric, media)] = SegmentRate().fit(X, y)
        predictor.evaluation = evaluation
        return predictor

    def predict(self, posts: pd.DataFrame) -> pd.DataFrame:
        """One row per (post, metric): chance %, base %, lift, model used and the post's segment history."""
        rows = []
        X = _features(posts)
        for i, (_, post) in enumerate(posts.iterrows()):
            media = post["content_type"]
            for metric in METRICS:
                key = (metric, media)
                if key not in self.models:
                    continue
                p = self.models[key].predict_proba(X.iloc[[i]])[0, 1]
                seg = self.segment_tables[key]
                seg_key = seg._key(X.iloc[[i]]).iloc[0]
                low, high = seg.interval(seg_key)
                rows.append({"post": i, "formato": media, "métrica": metric, "chance top 5% (%)": p * 100,
                             "base (%)": self.base_rates[key] * 100, "vs. base": p / self.base_rates[key],
                             "modelo": self.chosen[key], "segmento": seg_key,
                             "sinal do segmento (%)": seg.table_.get(seg_key, seg.base_) * 100,
                             "segmento IC90 (%)": f"{low * 100:.1f}–{high * 100:.1f}",
                             "posts no segmento": int(seg.sizes_.get(seg_key, 0))})
        return pd.DataFrame(rows)
