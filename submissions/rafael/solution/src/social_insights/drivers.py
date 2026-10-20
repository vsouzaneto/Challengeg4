"""Supervised checks: can post attributes predict reach/engagement? (cross-validated models + readable tree)."""
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

SEED = 42
FOLDS = 5
NUMERIC = ["follower_count", "content_length", "n_hashtags"]


def feature_matrix(df: pd.DataFrame, categorical: list[str]) -> pd.DataFrame:
    cats = [c for c in categorical if c not in NUMERIC]
    onehot = pd.get_dummies(df[cats].astype(str), dtype=float)
    return pd.concat([df[NUMERIC].astype(float), onehot], axis=1)


def cv_regression(df: pd.DataFrame, target: str, categorical: list[str]) -> dict:
    """Cross-validated R² of a gradient-boosting model vs. predicting the mean (R² = 0)."""
    X, y = feature_matrix(df, categorical), np.log1p(df[target])
    model = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, random_state=SEED)
    r2 = cross_val_score(model, X, y, cv=FOLDS, scoring="r2")
    baseline = cross_val_score(DummyRegressor(), X, y, cv=FOLDS, scoring="r2")
    return {"target": target, "r2_model": r2.mean(), "r2_std": r2.std(), "r2_baseline": baseline.mean()}


def cv_top_classifier(df: pd.DataFrame, top: pd.Series, categorical: list[str]) -> float:
    """Cross-validated ROC AUC for "is this a top post?" — 0.5 means coin flip."""
    X = feature_matrix(df, categorical)
    model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=SEED)
    return float(cross_val_score(model, X, top.astype(int), cv=FOLDS, scoring="roc_auc").mean())


def importance_table(df: pd.DataFrame, target: str, categorical: list[str], top_n: int = 10) -> pd.DataFrame:
    """Permutation importance on a hold-out set (drop in R² when a column is shuffled)."""
    X, y = feature_matrix(df, categorical), np.log1p(df[target])
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=SEED)
    model = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, random_state=SEED).fit(X_tr, y_tr)
    result = permutation_importance(model, X_te, y_te, n_repeats=5, random_state=SEED, scoring="r2")
    table = pd.DataFrame({"feature": X.columns, "importance": result.importances_mean, "std": result.importances_std})
    return table.sort_values("importance", ascending=False, ignore_index=True).head(top_n)


def surrogate_tree(df: pd.DataFrame, top: pd.Series, categorical: list[str], max_depth: int = 3) -> str:
    """Shallow decision tree: human-readable rules for reaching the top group."""
    X = feature_matrix(df, categorical)
    tree = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=300, class_weight="balanced", random_state=SEED)
    return export_text(tree.fit(X, top.astype(int)), feature_names=list(X.columns), show_weights=True)
