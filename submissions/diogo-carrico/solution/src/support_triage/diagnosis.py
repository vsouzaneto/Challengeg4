"""Operational diagnosis of Dataset 1, run as tested hypotheses.

The brief asks where the flow stalls, what drives satisfaction and how much time is wasted.
The audit showed the data is synthetic, so every apparent pattern is tested against what
random relabelling produces, and the smallest effect each test could detect is reported.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import make_column_transformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

SEED = 42
ALPHA = 0.05
POWER = 0.80

CUTS = {
    "channel": ["Ticket Channel"],
    "priority": ["Ticket Priority"],
    "type": ["Ticket Type"],
    "subject": ["Ticket Subject"],
    "product": ["Product Purchased"],
    "channel_x_priority": ["Ticket Channel", "Ticket Priority"],
    "channel_x_type": ["Ticket Channel", "Ticket Type"],
    "priority_x_type": ["Ticket Priority", "Ticket Type"],
    "channel_x_priority_x_type": ["Ticket Channel", "Ticket Priority", "Ticket Type"],
}

CSAT_CATEGORICALS = [
    "Ticket Channel",
    "Ticket Priority",
    "Ticket Type",
    "Ticket Subject",
    "Product Purchased",
    "Customer Gender",
]


# ---------------------------------------------------------------- data


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Add the outcome columns the diagnosis tests."""
    out = df.copy()
    frt = pd.to_datetime(out["First Response Time"])
    ttr = pd.to_datetime(out["Time to Resolution"])
    out["unresolved"] = out["Ticket Status"].ne("Closed").astype(float)
    out["never_answered"] = out["Ticket Status"].eq("Open").astype(float)
    # Recorded resolution minus recorded first response; negative in about half the closed tickets.
    out["resolution_hours_as_recorded"] = (ttr - frt).dt.total_seconds() / 3600
    return out


# ---------------------------------------------------------------- tests


def segment_codes(df: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, list[str]]:
    key = df[cols].astype(str).agg(" | ".join, axis=1)
    codes, labels = pd.factorize(key)
    return codes, list(labels)


def minimum_detectable_deviation(sd: float, n: float, n_tests: int) -> float:
    """Smallest deviation of one segment from the overall mean detectable with 80% power,
    two-sided, Bonferroni-corrected across n_tests segments."""
    z_alpha = stats.norm.ppf(1 - ALPHA / (2 * n_tests))
    z_power = stats.norm.ppf(POWER)
    return float((z_alpha + z_power) * sd / np.sqrt(n))


def max_deviation_test(
    y: np.ndarray, codes: np.ndarray, labels: list[str], n_perm: int = 5000
) -> dict:
    """Does any segment's mean differ from the overall mean by more than random relabelling would produce?

    The statistic is the largest absolute deviation across segments, so the p-value controls the
    family-wise error over every segment in the cut (the 'worst combination' is always extreme by chance).
    """
    k = codes.max() + 1
    counts = np.bincount(codes, minlength=k)
    overall = y.mean()

    def deviations(values: np.ndarray) -> np.ndarray:
        return np.bincount(codes, weights=values, minlength=k) / counts - overall

    dev = deviations(y)
    worst = int(np.argmax(np.abs(dev)))
    best = int(np.argmin(dev))
    top = int(np.argmax(dev))
    rng = np.random.default_rng(SEED)
    null_max = np.array(
        [np.abs(deviations(rng.permutation(y))).max() for _ in range(n_perm)]
    )
    observed = float(np.abs(dev).max())
    return {
        "n": len(y),
        "n_segments": int(k),
        "segment_size_median": float(np.median(counts)),
        "segment_size_min": int(counts.min()),
        "overall": float(overall),
        "highest_segment": labels[top],
        "highest_value": float(overall + dev[top]),
        "lowest_segment": labels[best],
        "lowest_value": float(overall + dev[best]),
        "largest_deviation_segment": labels[worst],
        "largest_deviation": float(dev[worst]),
        "null_95pct_of_largest_deviation": float(np.quantile(null_max, 0.95)),
        "familywise_p_value": float((np.sum(null_max >= observed) + 1) / (n_perm + 1)),
        "minimum_detectable_deviation": minimum_detectable_deviation(
            y.std(ddof=1), np.median(counts), int(k)
        ),
    }


def bottlenecks(df: pd.DataFrame, n_perm: int = 5000) -> dict:
    """Test every cut for the outcomes the data can express."""
    closed = df[df["Ticket Status"].eq("Closed")]
    outcomes = {
        "unresolved": (df, "unresolved"),
        "never_answered": (df, "never_answered"),
        "csat": (closed, "Customer Satisfaction Rating"),
        "resolution_hours_as_recorded": (closed, "resolution_hours_as_recorded"),
    }
    results: dict = {}
    for name, (frame, col) in outcomes.items():
        y = frame[col].to_numpy(dtype=float)
        results[name] = {}
        for cut, cols in CUTS.items():
            codes, labels = segment_codes(frame, cols)
            results[name][cut] = max_deviation_test(y, codes, labels, n_perm=n_perm)
    n_tests = sum(len(v) for v in results.values())
    smallest = min(
        r["familywise_p_value"] for v in results.values() for r in v.values()
    )
    results["_summary"] = {
        "n_tests": n_tests,
        "smallest_familywise_p_value": smallest,
        "smallest_p_after_bonferroni_across_tests": min(1.0, smallest * n_tests),
    }
    return results


def csat_drivers(df: pd.DataFrame) -> dict:
    """Which variables are associated with satisfaction? Closed tickets only (CSAT exists only there)."""
    closed = df[df["Ticket Status"].eq("Closed")].copy()
    y = closed["Customer Satisfaction Rating"].to_numpy(dtype=float)
    n = len(closed)
    tests = []
    for col in CSAT_CATEGORICALS:
        groups = [
            g["Customer Satisfaction Rating"].to_numpy() for _, g in closed.groupby(col)
        ]
        h, p = stats.kruskal(*groups)
        k = len(groups)
        means = closed.groupby(col)["Customer Satisfaction Rating"].mean()
        tests.append(
            {
                "variable": col,
                "test": "kruskal",
                "statistic": float(h),
                "p_value": float(p),
                "effect_size_epsilon_squared": float(max(0.0, (h - k + 1) / (n - k))),
                "n_groups": k,
                "mean_range": [float(means.min()), float(means.max())],
            }
        )
    for col in ["Customer Age", "resolution_hours_as_recorded"]:
        r = stats.spearmanr(closed[col], y)
        tests.append(
            {
                "variable": col,
                "test": "spearman",
                "statistic": float(r.statistic),
                "p_value": float(r.pvalue),
            }
        )
    q = stats.false_discovery_control([t["p_value"] for t in tests])
    for t, qv in zip(tests, q, strict=True):
        t["q_value_bh"] = float(qv)

    features = CSAT_CATEGORICALS + ["Customer Age", "resolution_hours_as_recorded"]
    model = make_pipeline(
        make_column_transformer(
            (OneHotEncoder(handle_unknown="ignore"), CSAT_CATEGORICALS),
            remainder="passthrough",
        ),
        RandomForestRegressor(
            n_estimators=300, min_samples_leaf=20, random_state=SEED, n_jobs=-1
        ),
    )
    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
    model_mae = -cross_val_score(
        model, closed[features], y, cv=cv, scoring="neg_mean_absolute_error"
    )
    base_mae = -cross_val_score(
        DummyRegressor(), closed[features], y, cv=cv, scoring="neg_mean_absolute_error"
    )

    sd = float(y.std(ddof=1))
    smallest_group = closed.groupby("Ticket Channel").size().min()
    z = stats.norm.ppf(1 - ALPHA / (2 * len(tests))) + stats.norm.ppf(POWER)
    return {
        "n_closed": n,
        "csat_mean": float(y.mean()),
        "csat_sd": sd,
        "tests": tests,
        "any_q_below_0_05": bool(min(q) < 0.05),
        "model": {
            "model": "random forest on all variables, 5-fold cross-validation",
            "mae_model": float(model_mae.mean()),
            "mae_model_sd": float(model_mae.std()),
            "mae_predicting_the_average": float(base_mae.mean()),
            "improvement_over_average": float(base_mae.mean() - model_mae.mean()),
        },
        "minimum_detectable_difference_between_two_channels": float(
            z * sd * np.sqrt(2 / smallest_group)
        ),
    }
