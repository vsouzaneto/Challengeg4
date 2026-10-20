"""Loads the dataset and builds (or reads from cache) the content payload and the trained models used by the server."""
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from social_insights import data, engagement_model, hit_probability, site_export, views_forecast

from . import explore
from .predict import PredictionService

CACHE_DIR = Path(__file__).resolve().parents[2] / "models"
PAYLOAD_FILE = CACHE_DIR / "site_payload.json"
MODELS_FILE = CACHE_DIR / "web_models.joblib"


@dataclass
class AppState:
    posts: pd.DataFrame          # dashboard-ready posts
    payload: dict                # every number/sentence shown on the content pages
    predictor: PredictionService


def train_models(df: pd.DataFrame, light: bool = False) -> dict:
    """Train every model the server uses. `light=True` compares fewer engagement models (tests)."""
    views_eval = views_forecast.evaluate(df)
    candidates = {k: v for k, v in engagement_model.candidate_models().items() if not light or k in site_export.LIGHT_ENGAGEMENT_MODELS}
    summary, _ = engagement_model.compare_models(df, models=candidates)
    return {"hits": hit_probability.HitPredictor.train(df), "views": views_forecast.ViewsForecaster.train(df, views_eval),
            "engagement": engagement_model.EngagementPredictor.train(df, summary), "views_eval": views_eval}


def load_state(rebuild: bool = False, df: pd.DataFrame | None = None, cache_dir: Path = CACHE_DIR, light: bool = False) -> AppState:
    """First run trains everything (~5 min) and caches it; later runs start in seconds. `rebuild=True` after new data."""
    df = data.load_posts() if df is None else df
    models_file, payload_file = cache_dir / MODELS_FILE.name, cache_dir / PAYLOAD_FILE.name
    cache_dir.mkdir(parents=True, exist_ok=True)
    if rebuild or not models_file.exists():
        joblib.dump(train_models(df, light), models_file)
    models = joblib.load(models_file)
    if rebuild or not payload_file.exists():
        payload = site_export.build_payload(df, light=light, hit_predictor=models["hits"], views_fc=models["views"], views_eval=models["views_eval"])
        payload_file.write_text(site_export.to_json(payload), encoding="utf-8")
    payload = json.loads(payload_file.read_text(encoding="utf-8"))
    service = PredictionService(df, models["hits"], models["views"], models["engagement"], payload["insights"]["bolsoes"])
    return AppState(explore.prepare(df), payload, service)
