"""Tests for the pre-publication views forecast: no look-ahead, temporal split, creator effect detection, fallback."""
import numpy as np
import pandas as pd
import pytest

from social_insights import validation as va, views_forecast as vf
from test_questions import make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 400).astype(str)
    return df


def test_inventory_marks_outcomes_as_post_publication():
    inv = vf.inventory()
    assert not inv.loc[["views", "likes", "comments_count"], "conhecido antes de postar"].any()
    assert inv.loc[["content_type", "follower_count", "is_sponsored"], "conhecido antes de postar"].all()


def test_creator_history_uses_only_past_posts(posts):
    hist = vf.add_creator_history(posts).sort_values("post_date")
    first = hist.groupby("creator_id").head(1)
    assert first["creator_mean_views_before"].isna().all() and (first["creator_posts_before"] == 0).all()
    one = hist[hist.creator_id == "c1"]
    expected = one["views"].shift(1).expanding().mean()
    assert np.allclose(one["creator_mean_views_before"].iloc[1:], expected.iloc[1:])


def test_temporal_split_has_no_overlap(posts):
    tr, te, cutoff = vf.temporal_split(posts)
    assert posts.loc[tr, "post_date"].max() < cutoff <= posts.loc[te, "post_date"].min()


def test_noise_falls_back_to_mean(posts):
    evaluation = vf.evaluate(posts, models=("LightGBM",))
    assert not evaluation["supera a média"].any()
    forecaster = vf.ViewsForecaster.train(posts, evaluation)
    assert forecaster.model is None and not forecaster.beats_baseline


def test_creator_effect_is_learned(posts):
    planted = va.inject_creator_effect(posts, "views", 0.05)
    evaluation = vf.evaluate(planted, models=("LightGBM",)).set_index("abordagem")
    assert evaluation.loc["2. + quem posta", "supera a média"] and evaluation.loc["2. + quem posta", "R²"] > 0.5
    forecaster = vf.ViewsForecaster.train(planted, evaluation.reset_index())
    assert forecaster.beats_baseline
