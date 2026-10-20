"""Engagement predictor: compares supervised approaches (post features → engagement rate) and serves the best one.

Every candidate is evaluated on the same K folds against a mean baseline; a model is only adopted if it beats
the baseline significantly (paired test over folds). Otherwise the predictor falls back to the baseline and says so.
"""
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from scipy import stats
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LogisticRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold, learning_curve
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from .cleaning import PRE_PUBLICATION
from .questions import ENGAGEMENT

SEED = 42
FOLDS = 5
ALPHA = 0.05
CATEGORICAL = PRE_PUBLICATION["categorical"]
NUMERIC = PRE_PUBLICATION["numeric"]
FEATURES = CATEGORICAL + NUMERIC
INTERVAL = (0.05, 0.95)  # 90% prediction interval from out-of-fold residuals


def _encoder(scale: bool = True) -> ColumnTransformer:
    numeric = StandardScaler() if scale else "passthrough"
    return ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
                              ("num", numeric, NUMERIC)])


class PlatformMean(DummyRegressor):
    """Baseline: average engagement of the post's platform."""

    def fit(self, X, y, sample_weight=None):
        self.means_ = pd.Series(np.asarray(y), index=X.index).groupby(X["platform"].values).mean()
        self.global_ = float(np.mean(y))
        return self

    def predict(self, X):
        return X["platform"].map(self.means_).fillna(self.global_).values


class CatBoostWrapper(CatBoostRegressor):
    """CatBoost reading categoricals as strings (native categorical handling)."""

    def fit(self, X, y, **kw):
        return super().fit(X.astype({c: str for c in CATEGORICAL}), y, cat_features=CATEGORICAL, verbose=0, **kw)

    def predict(self, X, **kw):
        return super().predict(X.astype({c: str for c in CATEGORICAL}), **kw)


def candidate_models() -> dict:
    """Name → (family, unfitted estimator taking the raw feature frame)."""
    trees = lambda m: make_pipeline(_encoder(scale=False), m)  # noqa: E731
    return {
        "Média (baseline)": ("baseline", DummyRegressor()),
        "Média por plataforma": ("baseline", PlatformMean()),
        "Ridge": ("linear", make_pipeline(_encoder(), Ridge(alpha=10))),
        "Lasso": ("linear", make_pipeline(_encoder(), Lasso(alpha=1e-5, max_iter=5000))),
        "ElasticNet": ("linear", make_pipeline(_encoder(), ElasticNet(alpha=1e-5, l1_ratio=0.5, max_iter=5000))),
        "KNN (k=50)": ("vizinhos", make_pipeline(_encoder(), KNeighborsRegressor(n_neighbors=50, n_jobs=-1))),
        "MLP (rede neural)": ("rede neural", make_pipeline(_encoder(), MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-3, early_stopping=True,
                                                                                    max_iter=200, random_state=SEED))),
        "Árvore de decisão": ("árvore", trees(DecisionTreeRegressor(max_depth=6, min_samples_leaf=200, random_state=SEED))),
        "Random Forest": ("ensemble de árvores", trees(RandomForestRegressor(n_estimators=150, min_samples_leaf=20, max_features="sqrt",
                                                                            n_jobs=-1, random_state=SEED))),
        "Extra Trees": ("ensemble de árvores", trees(ExtraTreesRegressor(n_estimators=150, min_samples_leaf=20, max_features="sqrt",
                                                                        n_jobs=-1, random_state=SEED))),
        "HistGradientBoosting": ("boosting", trees(HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=SEED))),
        "XGBoost": ("boosting", trees(XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
                                                   colsample_bytree=0.8, n_jobs=-1, random_state=SEED))),
        "LightGBM": ("boosting", trees(LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31, subsample=0.8,
                                                     subsample_freq=1, verbose=-1, random_state=SEED))),
        "CatBoost": ("boosting", CatBoostWrapper(iterations=300, depth=6, learning_rate=0.05, random_seed=SEED, allow_writing_files=False)),
    }


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURES].astype({c: str for c in CATEGORICAL})


def compare_models(df: pd.DataFrame, target: str = ENGAGEMENT, models: dict | None = None, folds: int = FOLDS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Same-fold CV for every model. Returns (summary, per-fold squared errors relative to the baseline)."""
    models = models or candidate_models()
    X, y = feature_frame(df), df[target].values
    splits = list(KFold(folds, shuffle=True, random_state=SEED).split(X))
    rows, fold_mse = [], {}
    for name, (family, model) in models.items():
        scores, mses = [], []
        for tr, te in splits:
            fitted = clone(model).fit(X.iloc[tr], y[tr])
            pred = fitted.predict(X.iloc[te])
            train_pred = fitted.predict(X.iloc[tr])
            scores.append({"r2": r2_score(y[te], pred), "mae": mean_absolute_error(y[te], pred),
                           "rmse": mean_squared_error(y[te], pred) ** 0.5, "r2_train": r2_score(y[tr], train_pred)})
            mses.append(mean_squared_error(y[te], pred))
        s = pd.DataFrame(scores).mean()
        fold_mse[name] = mses
        rows.append({"modelo": name, "família": family, "R² validação": s.r2, "R² treino": s.r2_train, "MAE": s.mae, "RMSE": s.rmse})
    summary = pd.DataFrame(rows).set_index("modelo")
    fold_mse = pd.DataFrame(fold_mse)
    base = fold_mse["Média (baseline)"]
    summary["ganho MAE vs. baseline (%)"] = (1 - summary["MAE"] / summary.loc["Média (baseline)", "MAE"]) * 100
    summary["p (melhor que baseline)"] = [1.0 if c == "Média (baseline)" else stats.ttest_rel(fold_mse[c], base, alternative="less").pvalue
                                          for c in summary.index]
    summary["supera baseline"] = summary["p (melhor que baseline)"] < ALPHA
    return summary.sort_values("R² validação", ascending=False), fold_mse


def compare_classifiers(df: pd.DataFrame, top: pd.Series, folds: int = FOLDS) -> pd.DataFrame:
    """Alternative framing: is the post going to be top-10% engagement? (ROC AUC; 0.5 = coin flip)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from xgboost import XGBClassifier
    X, y = feature_frame(df), top.astype(int).values
    models = {
        "Regressão logística": make_pipeline(_encoder(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "HistGradientBoosting": make_pipeline(_encoder(scale=False), HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, random_state=SEED)),
        "XGBoost": make_pipeline(_encoder(scale=False), XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, n_jobs=-1, random_state=SEED)),
    }
    rows = []
    for name, model in models.items():
        aucs = [roc_auc_score(y[te], clone(model).fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1])
                for tr, te in StratifiedKFold(folds, shuffle=True, random_state=SEED).split(X, y)]
        rows.append({"modelo": name, "AUC média": np.mean(aucs), "AUC desvio": np.std(aucs)})
    return pd.DataFrame(rows).set_index("modelo")


def learning_curve_table(df: pd.DataFrame, model_name: str = "LightGBM", target: str = ENGAGEMENT) -> pd.DataFrame:
    """Does more data help? Validation R² as the training set grows."""
    model = candidate_models()[model_name][1]
    sizes, train, valid = learning_curve(model, feature_frame(df), df[target].values, cv=FOLDS, scoring="r2",
                                         train_sizes=np.linspace(0.1, 1.0, 6), shuffle=True, random_state=SEED)
    return pd.DataFrame({"posts de treino": sizes, "R² treino": train.mean(axis=1), "R² validação": valid.mean(axis=1)})


@dataclass
class EngagementPredictor:
    """Fitted predictor for new posts: point estimate + 90% interval from out-of-fold residuals."""
    model_name: str
    model: object
    residual_quantiles: tuple[float, float]
    beats_baseline: bool
    cv_r2: float

    @classmethod
    def train(cls, df: pd.DataFrame, summary: pd.DataFrame, target: str = ENGAGEMENT) -> "EngagementPredictor":
        """Adopt the best CV model only if it significantly beats the baseline; otherwise use the baseline."""
        winners = summary[summary["supera baseline"]]
        name = winners.index[0] if len(winners) else "Média (baseline)"
        model = candidate_models()[name][1]
        X, y = feature_frame(df), df[target].values
        oof = np.empty(len(y))
        for tr, te in KFold(FOLDS, shuffle=True, random_state=SEED).split(X):
            oof[te] = clone(model).fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
        residuals = y - oof
        return cls(name, clone(model).fit(X, y), tuple(np.quantile(residuals, INTERVAL)), bool(len(winners)), float(summary.loc[name, "R² validação"]))

    def predict(self, posts: pd.DataFrame) -> pd.DataFrame:
        point = self.model.predict(feature_frame(posts))
        low, high = self.residual_quantiles
        return pd.DataFrame({"engajamento estimado": point, "intervalo 90% inf": point + low, "intervalo 90% sup": point + high,
                             "modelo": self.model_name}, index=posts.index)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path: Path) -> "EngagementPredictor":
        return joblib.load(path)
