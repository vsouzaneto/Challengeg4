"""Tests for the executive-summary proofs: rate-per-follower artifact, survivorship, quarterly stability, test brief, AI claims × data."""
import pandas as pd
import pytest

from social_insights import cleaning, exploration, strategy
from test_questions import _boost_likes, make_posts


@pytest.fixture(scope="module")
def posts() -> pd.DataFrame:
    return make_posts()


@pytest.fixture(scope="module")
def queue(posts) -> strategy.Recommendation:
    return strategy.test_queue(posts)


def test_rate_per_follower_shows_denominator_artifact_on_noise(posts):
    tiers = exploration.engagement_rate_by_tier(posts)
    per_follower, per_view = tiers["interações por seguidor (mediana)"], tiers["interações por view (mediana)"]
    assert per_follower.is_monotonic_decreasing and per_follower.iloc[0] / per_follower.iloc[-1] > 10
    assert per_view.max() / per_view.min() < 1.02 and tiers["views (mediana)"].max() / tiers["views (mediana)"].min() < 1.02


def test_survivorship_detects_planted_zeros(posts):
    assert cleaning.survivorship_check(posts)["posts com zero"].sum() == 0
    planted = posts.copy()
    planted.loc[planted.index[:3], "likes"] = 0
    zeros = cleaning.survivorship_check(planted)
    assert zeros.loc["likes", "posts com zero"] == 3 and zeros.loc["likes", "mínimo"] == 0


def test_quarters_flat_on_noise_and_detect_planted_season(posts):
    _, noise = exploration.engagement_by_quarter(posts)
    _, season = exploration.engagement_by_quarter(_boost_likes(posts, posts["post_date"].dt.quarter == 1, 1.05))
    assert noise["p_value"] > 0.05 and season["p_value"] < 0.05


def test_pocket_mask_reads_categorical_pairs_and_numeric_windows(posts):
    pair = pd.Series({"plataforma": "TikTok", "dimensão": "content_category × language", "bolsão": "beauty · Spanish"})
    expected = (posts["platform"] == "TikTok") & (posts["content_category"] == "beauty") & (posts["language"] == "Spanish")
    assert strategy.pocket_mask(posts, pair).equals(expected)
    window = pd.Series({"plataforma": "TikTok", "dimensão": "hour (janela)", "bolsão": "6–9"})
    assert strategy.pocket_mask(posts, window).equals((posts["platform"] == "TikTok") & posts["hour"].between(6, 9))


def test_brief_of_first_test_is_complete_and_sized(queue):
    brief = queue.details["Brief do teste 1"]["valor"]
    assert list(brief.index) == ["Grupos", "Formato", "Faixa de creator", "Público-alvo", "Horário", "Duração", "Critério de sucesso"]
    assert f"{queue.evidence.iloc[0]['posts por grupo']:,} posts por grupo" in brief["Critério de sucesso"]


def test_claims_vs_data_lists_beliefs_and_ends_with_the_surviving_pocket(posts, queue):
    table = strategy.claims_vs_data(posts, queue)
    assert len(table) == 1 + len(strategy.AI_CLAIMS) + 1
    assert table.iloc[-1]["veredito"].startswith("único que passou no filtro")
