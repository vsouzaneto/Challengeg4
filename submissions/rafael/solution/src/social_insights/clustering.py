"""Clustering of posts by performance and by content/audience attributes, plus cluster-tendency checks."""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SEED = 42
SILHOUETTE_SAMPLE = 5_000
K_RANGE = range(2, 7)


def permute_columns(X: np.ndarray, seed: int = SEED) -> np.ndarray:
    """Shuffle each column independently: keeps every marginal distribution, destroys any joint structure."""
    rng = np.random.default_rng(seed)
    return np.column_stack([rng.permutation(col) for col in X.T])


def performance_space(df: pd.DataFrame, metrics: list[str]) -> np.ndarray:
    return StandardScaler().fit_transform(np.log1p(df[metrics]))


def attribute_space(df: pd.DataFrame, features: list[str], n_components: int = 10) -> np.ndarray:
    """One-hot encode categorical attributes and compress them (MCA-like) with truncated SVD."""
    onehot = pd.get_dummies(df[features].astype(str), dtype=float)
    return TruncatedSVD(n_components=n_components, random_state=SEED).fit_transform(onehot)


def kmeans_scan(X: np.ndarray, k_range=K_RANGE, seed: int = SEED) -> pd.DataFrame:
    """Silhouette per k (sampled). Below ~0.25 there is no meaningful cluster structure."""
    rows = []
    for k in k_range:
        labels = KMeans(n_clusters=k, n_init=5, random_state=seed).fit_predict(X)
        score = silhouette_score(X, labels, sample_size=min(SILHOUETTE_SAMPLE, len(X)), random_state=seed)
        rows.append({"k": k, "silhouette": score})
    return pd.DataFrame(rows)


def structure_test(X: np.ndarray, k_range=K_RANGE, seed: int = SEED) -> pd.DataFrame:
    """Silhouette on real data vs. on a column-permuted null. Gain ≈ 0 → the clusters are an artifact of the algorithm."""
    real = kmeans_scan(X, k_range, seed)
    null = kmeans_scan(permute_columns(X, seed), k_range, seed)
    return real.assign(silhouette_null=null["silhouette"], gain=real["silhouette"] - null["silhouette"])


def fit_kmeans(X: np.ndarray, k: int, seed: int = SEED) -> np.ndarray:
    return KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(X)


def profile_clusters(df: pd.DataFrame, labels: np.ndarray, metrics: list[str]) -> pd.DataFrame:
    """Mean of each metric per cluster, plus a Kruskal-Wallis p-value row."""
    grouped = df.assign(cluster=labels).groupby("cluster")
    profile = grouped[metrics].mean().round(1)
    profile["n"] = grouped.size()
    pvalues = {m: stats.kruskal(*[g[m].values for _, g in grouped]).pvalue for m in metrics}
    profile.loc["Kruskal p"] = pd.Series(pvalues).round(3)
    return profile


def dominant_attributes(df: pd.DataFrame, labels: np.ndarray, features: list[str], top_n: int = 3) -> pd.DataFrame:
    """For each cluster, the attribute values most over-represented vs. the full base (lift)."""
    rows = []
    for cluster in np.unique(labels):
        members = df[labels == cluster]
        for f in features:
            share = members[f].astype(str).value_counts(normalize=True)
            base = df[f].astype(str).value_counts(normalize=True)
            lift = (share / base).dropna()
            rows += [{"cluster": cluster, "feature": f, "value": v, "lift": l} for v, l in lift.items()]
    table = pd.DataFrame(rows).sort_values("lift", ascending=False)
    return table.groupby("cluster").head(top_n).sort_values(["cluster", "lift"], ascending=[True, False])
