"""Tests for the engagement predictor: adopts a model only when it beats the baseline, falls back otherwise."""
import pandas as pd
import pytest

from social_insights import engagement_model as em
from test_questions import _boost_likes, make_posts

FAST = ["Média (baseline)", "LightGBM", "Ridge"]


@pytest.fixture
def posts() -> pd.DataFrame:
    return make_posts()


def _models():
    return {k: v for k, v in em.candidate_models().items() if k in FAST}


def test_no_model_beats_baseline_on_noise(posts):
    summary, _ = em.compare_models(posts, models=_models(), folds=3)
    assert not summary["supera baseline"].any()


def test_boosting_beats_baseline_with_planted_effect(posts):
    boosted = _boost_likes(posts, (posts.platform == "TikTok") & (posts.content_type == "video"), 1.10)
    summary, _ = em.compare_models(boosted, models=_models(), folds=3)
    assert summary.loc["LightGBM", "supera baseline"]


def test_predictor_falls_back_to_baseline_and_roundtrips(posts, tmp_path):
    summary, _ = em.compare_models(posts, models=_models(), folds=3)
    predictor = em.EngagementPredictor.train(posts, summary)
    assert predictor.model_name == "Média (baseline)" and not predictor.beats_baseline
    pred = predictor.predict(posts.head(3))
    assert (pred["intervalo 90% inf"] < pred["engajamento estimado"]).all()
    assert (pred["engajamento estimado"] < pred["intervalo 90% sup"]).all()
    predictor.save(tmp_path / "m.joblib")
    assert em.EngagementPredictor.load(tmp_path / "m.joblib").model_name == predictor.model_name
