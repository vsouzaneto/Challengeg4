"""Per-target models (Random Forest, XGBoost, CatBoost) in two scenarios, plus SHAP interpretation."""
import numpy as np
import pandas as pd
import shap
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from xgboost import XGBRegressor

from .cleaning import PRE_PUBLICATION

SEED = 42
FOLDS = 3
SHAP_SAMPLE = 3_000
INTERACTION_SAMPLE = 800


def scenario_columns(target: str, scenario: str, metrics: list[str]) -> tuple[list[str], list[str]]:
    """(categorical, numeric) inputs. 'explicativo' adds the other post-publication metrics."""
    numeric = list(PRE_PUBLICATION["numeric"])
    if scenario == "explicativo":
        numeric += [m for m in metrics if m != target]
    return list(PRE_PUBLICATION["categorical"]), numeric


def _frame(df: pd.DataFrame, cats: list[str], nums: list[str]) -> pd.DataFrame:
    X = df[cats + nums].copy()
    for c in cats:
        X[c] = X[c].astype(str).astype("category")
    return X


def _onehot(X: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(X, dtype=float)


def make_model(name: str, cats: list[str]):
    if name == "Random Forest":
        return RandomForestRegressor(n_estimators=150, min_samples_leaf=20, max_features="sqrt", n_jobs=-1, random_state=SEED)
    if name == "XGBoost":
        return XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                            enable_categorical=True, tree_method="hist", random_state=SEED, n_jobs=-1)
    if name == "CatBoost":
        return CatBoostRegressor(iterations=300, depth=6, learning_rate=0.05, cat_features=cats, random_seed=SEED, verbose=0, allow_writing_files=False)
    raise ValueError(name)


def _prepare(name: str, X: pd.DataFrame, cats: list[str]) -> pd.DataFrame:
    if name == "Random Forest":
        return _onehot(X)
    if name == "CatBoost":
        return X.astype({c: str for c in cats})
    return X


def cross_validate(df: pd.DataFrame, target: str, scenario: str, model_name: str, metrics: list[str]) -> dict:
    """K-fold R² on log1p(target), with train R² to expose overfitting."""
    cats, nums = scenario_columns(target, scenario, metrics)
    X, y = _prepare(model_name, _frame(df, cats, nums), cats), np.log1p(df[target]).values
    train_r2, test_r2 = [], []
    for tr, te in KFold(FOLDS, shuffle=True, random_state=SEED).split(X):
        model = make_model(model_name, cats).fit(X.iloc[tr], y[tr])
        train_r2.append(r2_score(y[tr], model.predict(X.iloc[tr])))
        test_r2.append(r2_score(y[te], model.predict(X.iloc[te])))
    return {"alvo": target, "cenário": scenario, "modelo": model_name,
            "R² treino": np.mean(train_r2), "R² validação": np.mean(test_r2), "desvio validação": np.std(test_r2)}


def fit_xgb(df: pd.DataFrame, target: str, scenario: str, metrics: list[str], shuffle_target: bool = False):
    """Fit XGBoost on all rows; shuffle_target=True gives the null model (importance of pure noise)."""
    cats, nums = scenario_columns(target, scenario, metrics)
    X, y = _frame(df, cats, nums), np.log1p(df[target]).values
    if shuffle_target:
        y = np.random.default_rng(SEED).permutation(y)
    return make_model("XGBoost", cats).fit(X, y), X


def shap_values(model, X: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    sample = X.sample(min(SHAP_SAMPLE, len(X)), random_state=SEED)
    return shap.TreeExplainer(model).shap_values(sample), sample


def shap_importance(values: np.ndarray, sample: pd.DataFrame) -> pd.DataFrame:
    """Mean |SHAP| per feature, translated to % change of the target (SHAP is on the log scale)."""
    mean_abs = np.abs(values).mean(axis=0)
    table = pd.DataFrame({"variável": sample.columns, "mean |SHAP| (log)": mean_abs, "efeito médio (%)": (np.exp(mean_abs) - 1) * 100})
    return table.sort_values("mean |SHAP| (log)", ascending=False, ignore_index=True)


def shap_direction(values: np.ndarray, sample: pd.DataFrame, top_n: int = 8) -> pd.DataFrame:
    """For each feature value/bin: mean SHAP in % — positive raises the prediction, negative lowers it."""
    rows = []
    for i, col in enumerate(sample.columns):
        keys = sample[col].astype(str) if str(sample[col].dtype) == "category" else pd.qcut(sample[col], 4, duplicates="drop").astype(str)
        means = pd.Series(values[:, i]).groupby(keys.values).mean()
        rows += [{"variável": col, "valor": k, "efeito (%)": (np.exp(v) - 1) * 100} for k, v in means.items()]
    table = pd.DataFrame(rows)
    return pd.concat([table.nlargest(top_n, "efeito (%)"), table.nsmallest(top_n, "efeito (%)")])


def shap_interactions(model, X: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Strongest pairwise SHAP interactions (mean |interaction| on the log scale, off-diagonal)."""
    sample = X.sample(min(INTERACTION_SAMPLE, len(X)), random_state=SEED)
    inter = np.abs(shap.TreeExplainer(model).shap_interaction_values(sample)).mean(axis=0)
    cols, rows = list(sample.columns), []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            rows.append({"par": f"{cols[i]} × {cols[j]}", "interação média (%)": (np.exp(2 * inter[i, j]) - 1) * 100})
    return pd.DataFrame(rows).nlargest(top_n, "interação média (%)").reset_index(drop=True)
