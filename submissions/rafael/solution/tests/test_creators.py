"""Tests for the creator analysis: quiet on noise, detects a planted creator effect, honest ranking shrinks noise."""
import pandas as pd
import pytest

from social_insights import creators, validation
from test_questions import make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 400).astype(str)
    df["creator_name"] = "n" + (df.index % 900).astype(str)
    return df


def test_no_creator_effect_on_noise(posts):
    share = creators.variance_share(posts)
    assert (share["ICC (% da variação ligada ao creator)"] < 1).all()
    spread = creators.spread_vs_chance(posts, draws=50)
    assert spread["p_value"] > 0.01
    assert creators.leaderboard(posts)["peso do histórico (%)"].max() < 20  # noisy creators are pulled back to the mean


def test_planted_creator_effect_is_detected(posts):
    planted = validation.inject_creator_effect(posts, "views", relative_sd=0.03)
    assert creators.variance_share(planted).loc["views", "ICC (% da variação ligada ao creator)"] > 50
    assert creators.spread_vs_chance(planted, draws=50)["p_value"] < 0.05
    assert creators.persistence(planted)["% que continuou"] > 50
    assert creators.leaderboard(planted)["peso do histórico (%)"].min() > 80


def test_identity_check(posts):
    table = creators.identity_check(posts)
    assert table.loc["creator_id", "valores únicos"] == 400
