"""Pre-publication views forecast: which columns are known before posting, creator history, temporal validation.

Protocol: train on the earliest posts, test on the most recent ones (a real forecast never sees the future),
compare cumulative feature blocks against two baselines (global mean, creator's past mean).
"""
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from scipy import stats
from sklearn.metrics import mean_absolute_error, r2_score

SEED = 42
TARGET = "views"
TEST_SHARE = 0.20
INTERVAL = (0.05, 0.95)
MIN_HISTORY = 1

# Column → (known before posting?, role, note). Single source of truth for the inventory.
INVENTORY = {
    "platform": (True, "conteúdo", "escolhido na publicação"),
    "content_type": (True, "conteúdo", "vídeo / imagem / texto / misto"),
    "content_category": (True, "conteúdo", "tema"),
    "language": (True, "conteúdo", "idioma do post"),
    "content_length": (True, "conteúdo", "duração (s) ou nº de palavras; ATENÇÃO: 10–599 para todos os tipos, inclusive imagem"),
    "content_description": (True, "conteúdo", "legenda (texto livre); usada como nº de palavras"),
    "hashtags": (True, "conteúdo", "usada como nº de hashtags"),
    "creator_id": (True, "quem posta", "usado via histórico do creator (posts anteriores)"),
    "creator_name": (False, "quem posta", "muda a cada post do mesmo creator_id, então não identifica ninguém"),
    "follower_count": (True, "quem posta", "seguidores no momento do post"),
    "is_sponsored": (True, "patrocínio", "definido em contrato"),
    "sponsor_category": (True, "patrocínio", "setor do patrocinador"),
    "sponsor_name": (True, "patrocínio", "1,2 post por patrocinador, então não generaliza (fora do modelo)"),
    "disclosure_type": (True, "patrocínio", "explícito / implícito"),
    "disclosure_location": (True, "patrocínio", "legenda / vídeo / hashtags"),
    "post_date": (True, "horário", "agendamento: hora e dia da semana"),
    "audience_gender_distribution": (True, "audiência", "perfil histórico da audiência do creator"),
    "audience_age_distribution": (True, "audiência", "idem"),
    "audience_location": (True, "audiência", "idem"),
    "views": (False, "resultado", "ALVO"),
    "likes": (False, "resultado", "medido após a publicação"),
    "shares": (False, "resultado", "medido após a publicação"),
    "comments_count": (False, "resultado", "medido após a publicação"),
    "comments_text": (False, "resultado", "medido após a publicação"),
    "id": (False, "identificador", "sem significado preditivo"),
    "content_id": (False, "identificador", "único por post"),
    "content_url": (False, "identificador", "gerada na publicação"),
}

CREATOR_HISTORY = ["creator_posts_before", "creator_mean_views_before", "creator_last_views", "days_since_last_post"]
BLOCKS = {
    "1. conteúdo": (["platform", "content_type", "content_category", "language"], ["content_length", "caption_words", "n_hashtags"]),
    "2. + quem posta": ([], ["follower_count", *CREATOR_HISTORY]),
    "3. + patrocínio": (["is_sponsored", "sponsor_category", "disclosure_type", "disclosure_location"], []),
    "4. + horário": (["weekday"], ["hour"]),
    "5. + audiência": (["audience_gender_distribution", "audience_age_distribution", "audience_location"], []),
}


def inventory() -> pd.DataFrame:
    table = pd.DataFrame.from_dict(INVENTORY, orient="index", columns=["conhecido antes de postar", "bloco", "observação"])
    return table.rename_axis("coluna").sort_values(["conhecido antes de postar", "bloco"], ascending=[False, True])


def add_creator_history(df: pd.DataFrame, target: str = TARGET) -> pd.DataFrame:
    """Per post, creator stats computed ONLY from that creator's earlier posts (no look-ahead)."""
    out = df.sort_values("post_date").copy()
    g = out.groupby("creator_id")
    out["creator_posts_before"] = g.cumcount()
    out["creator_mean_views_before"] = g[target].transform(lambda s: s.shift(1).expanding().mean())
    out["creator_last_views"] = g[target].shift(1)
    out["days_since_last_post"] = g["post_date"].diff().dt.total_seconds() / 86_400
    return out.sort_index()


def temporal_split(df: pd.DataFrame, test_share: float = TEST_SHARE) -> tuple[pd.Index, pd.Index, pd.Timestamp]:
    cutoff = df["post_date"].quantile(1 - test_share)
    return df.index[df["post_date"] < cutoff], df.index[df["post_date"] >= cutoff], cutoff


def block_columns(upto: str) -> tuple[list[str], list[str]]:
    cats, nums = [], []
    for name, (c, n) in BLOCKS.items():
        cats, nums = cats + c, nums + n
        if name == upto:
            break
    return cats, nums


def _frame(df: pd.DataFrame, cats: list[str], nums: list[str]) -> pd.DataFrame:
    X = df[cats + nums].copy()
    for c in cats:
        X[c] = X[c].astype(str).astype("category")
    return X


def _model(name: str, cats: list[str]):
    if name == "LightGBM":
        return LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=31, min_child_samples=50, subsample=0.8,
                             subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=SEED)
    return CatBoostRegressor(iterations=400, depth=6, learning_rate=0.05, random_seed=SEED, verbose=0, allow_writing_files=False, cat_features=cats)


def _fit_predict(name: str, X_tr, y_tr, X_te, cats):
    if name == "CatBoost":
        X_tr, X_te = X_tr.astype({c: str for c in cats}), X_te.astype({c: str for c in cats})
    model = _model(name, cats).fit(X_tr, y_tr)
    return model.predict(X_tr), model.predict(X_te), model


def _scores(y, pred) -> dict:
    return {"R²": r2_score(y, pred), "MAE (views)": mean_absolute_error(y, pred), "erro médio (%)": np.mean(np.abs(y - pred) / y) * 100}


def evaluate(df: pd.DataFrame, target: str = TARGET, models: tuple[str, ...] = ("LightGBM", "CatBoost")) -> pd.DataFrame:
    """Temporal hold-out: baselines + each cumulative feature block × model. Includes train R² and a paired test vs. the mean."""
    data = add_creator_history(df, target)
    tr, te, _ = temporal_split(data)
    y_tr, y_te = data.loc[tr, target].values, data.loc[te, target].values
    base_pred = np.full(len(te), y_tr.mean())
    base_err = np.abs(y_te - base_pred)
    rows = [{"abordagem": "baseline: média histórica", "modelo": "—", "R² treino": 0.0, **_scores(y_te, base_pred), "p (melhor que média)": np.nan}]
    creator_pred = data.loc[te, "creator_mean_views_before"].fillna(y_tr.mean()).values
    rows.append({"abordagem": "baseline: média passada do creator", "modelo": "—", "R² treino": np.nan, **_scores(y_te, creator_pred),
                 "p (melhor que média)": stats.wilcoxon(np.abs(y_te - creator_pred), base_err, alternative="less").pvalue})
    for block in BLOCKS:
        cats, nums = block_columns(block)
        X_tr, X_te = _frame(data.loc[tr], cats, nums), _frame(data.loc[te], cats, nums)
        for name in models:
            fit_tr, pred, _ = _fit_predict(name, X_tr, y_tr, X_te, cats)
            rows.append({"abordagem": block, "modelo": name, "R² treino": r2_score(y_tr, fit_tr), **_scores(y_te, pred),
                         "p (melhor que média)": stats.wilcoxon(np.abs(y_te - pred), base_err, alternative="less").pvalue})
    table = pd.DataFrame(rows)
    table["ganho MAE vs. média (%)"] = (1 - table["MAE (views)"] / table.loc[0, "MAE (views)"]) * 100
    table["supera a média"] = table["p (melhor que média)"] < 0.05
    return table


def creator_consistency(df: pd.DataFrame, target: str = TARGET) -> dict:
    """Do creators keep their level? Correlation between a creator's mean in the first and second half of their posts."""
    data = df.sort_values("post_date")
    rank = data.groupby("creator_id").cumcount()
    size = data.groupby("creator_id")[target].transform("size")
    first = data[rank < size / 2].groupby("creator_id")[target].mean()
    second = data[rank >= size / 2].groupby("creator_id")[target].mean()
    rho, p = stats.spearmanr(first, second)
    return {"creators": len(first), "ρ (1ª metade × 2ª metade)": rho, "p_value": p}


@dataclass
class ViewsForecaster:
    """Pre-publication forecaster: point estimate + 90% interval; falls back to the historical mean if no model helps."""
    model_name: str
    model: object
    categorical: list[str]
    numeric: list[str]
    fallback_mean: float
    residual_quantiles: tuple[float, float]
    beats_baseline: bool

    @classmethod
    def train(cls, df: pd.DataFrame, evaluation: pd.DataFrame, target: str = TARGET) -> "ViewsForecaster":
        data = add_creator_history(df, target)
        tr, te, _ = temporal_split(data)
        winners = evaluation[evaluation["supera a média"] & (evaluation["modelo"] != "—")].sort_values("MAE (views)")
        if winners.empty:
            residuals = data.loc[te, target] - data.loc[tr, target].mean()
            return cls("média histórica", None, [], [], float(data[target].mean()), tuple(np.quantile(residuals, INTERVAL)), False)
        best = winners.iloc[0]
        cats, nums = block_columns(best["abordagem"])
        _, pred, _ = _fit_predict(best["modelo"], _frame(data.loc[tr], cats, nums), data.loc[tr, target], _frame(data.loc[te], cats, nums), cats)
        residuals = data.loc[te, target].values - pred
        X_all = _frame(data, cats, nums)
        _, _, model = _fit_predict(best["modelo"], X_all, data[target], X_all.head(1), cats)
        return cls(f"{best['modelo']} ({best['abordagem']})", model, cats, nums, float(data[target].mean()),
                   tuple(np.quantile(residuals, INTERVAL)), True)

    def predict(self, posts: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            point = np.full(len(posts), self.fallback_mean)
        else:
            X = _frame(posts, self.categorical, self.numeric)
            if "CatBoost" in self.model_name:
                X = X.astype({c: str for c in self.categorical})
            point = self.model.predict(X)
        low, high = self.residual_quantiles
        return pd.DataFrame({"views previstas": point, "intervalo 90% inf": point + low, "intervalo 90% sup": point + high,
                             "modelo": self.model_name}, index=posts.index)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path: Path) -> "ViewsForecaster":
        return joblib.load(path)


def creator_snapshot(df: pd.DataFrame, creator_id: str, target: str = TARGET) -> dict:
    """History features for a creator's NEXT post (used when forecasting a planned post)."""
    past = df[df["creator_id"] == creator_id].sort_values("post_date")
    if past.empty:
        return {c: np.nan for c in CREATOR_HISTORY} | {"creator_posts_before": 0}
    return {"creator_posts_before": len(past), "creator_mean_views_before": past[target].mean(),
            "creator_last_views": past[target].iloc[-1], "days_since_last_post": (df["post_date"].max() - past["post_date"].iloc[-1]).days}
