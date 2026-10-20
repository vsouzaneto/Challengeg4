"""Tests for the four focused relations: power formulas and detection of planted effects on views."""
import numpy as np
import pandas as pd
import pytest

from social_insights import focus
from test_questions import make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    return make_posts()


def test_mde_formulas():
    assert focus.mde_two_groups(100, 10_000, 10_000) == pytest.approx(2.80 * 100 * np.sqrt(2 / 10_000), rel=0.01)
    assert focus.mde_correlation(52_214) == pytest.approx(0.0123, abs=0.0005)


def test_category_detects_planted_difference(posts):
    assert focus.category_vs_views(posts).details["Comparações par a par"]["q_value"].min() > 0.05
    posts.loc[posts.content_category == "tech", "views"] += 50
    pairs = focus.category_vs_views(posts).details["Comparações par a par"].set_index("par")
    assert pairs.filter(like="tech", axis=0)["q_value"].max() < 0.05


def test_followers_elasticity_recovered(posts):
    posts = posts.copy()
    posts["views"] = (10 * posts["follower_count"] ** 0.5).round().astype(int)
    stats_table = focus.followers_vs_views(posts).evidence
    assert stats_table.loc["elasticidade (log-log)", "valor"] == pytest.approx(0.5, abs=0.01)


def test_sponsorship_detects_planted_uplift(posts):
    posts.loc[posts.is_sponsored, "views"] += 30
    overview = focus.sponsorship_vs_views(posts).evidence
    assert overview.loc["bruta", "p_value"] < 1e-6 and overview.loc["bruta", "diferença (views)"] == pytest.approx(30, abs=6)


def test_description_text_model_finds_signal_word(posts):
    posts = posts.copy()
    posts["content_description"] = np.where(posts.index % 2 == 0, "amazing tutorial today", "boring update today")
    posts["views"] = np.where(posts.index % 2 == 0, 11_000, 10_000) + np.random.default_rng(0).poisson(100, len(posts))
    answer = focus.description_vs_views(posts)
    assert answer.details["Modelo de texto (TF-IDF + Ridge)"]["R² médio"].iloc[0] > 0.9
