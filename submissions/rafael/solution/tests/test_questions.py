"""Tests for the four business-question functions: each must detect a planted effect (and stay quiet on noise)."""
import numpy as np
import pandas as pd
import pytest

from social_insights import data, questions

N = 8_000


def make_posts(seed: int = 0) -> pd.DataFrame:
    """Synthetic posts shaped like the Kaggle file, with independent Poisson metrics (no effect)."""
    rng = np.random.default_rng(seed)
    sponsored = rng.random(N) < 0.45
    raw = pd.DataFrame({
        "post_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365 * 24 * 60, N), unit="min"),
        "platform": rng.choice(data.PLATFORMS, N), "content_type": rng.choice(["video", "image", "text"], N),
        "content_category": rng.choice(["tech", "beauty", "lifestyle"], N), "language": rng.choice(["English", "Spanish"], N),
        "views": rng.poisson(10_000, N), "likes": rng.poisson(1_500, N), "shares": rng.poisson(300, N),
        "comments_count": rng.poisson(200, N), "follower_count": rng.integers(1_000, 1_000_000, N),
        "content_length": rng.integers(10, 600, N), "hashtags": rng.choice(["", "a", "a,b", "a,b,c"], N), "comments_text": "nice",
        "content_description": rng.choice(["short caption", "a much longer caption here"], N), "is_sponsored": sponsored,
        "disclosure_type": np.where(sponsored, rng.choice(["explicit", "implicit"], N), "none"),
        "disclosure_location": np.where(sponsored, rng.choice(["caption", "video"], N), "none"),
        "sponsor_category": np.where(sponsored, rng.choice(["food", "gaming"], N), "Not sponsors"),
        "audience_gender_distribution": rng.choice(["female", "male"], N),
        "audience_age_distribution": rng.choice(["19-25", "26-35"], N), "audience_location": rng.choice(["USA", "Brazil"], N),
    })
    raw["post_date"] = raw["post_date"].dt.strftime(data.DATE_FORMAT)
    return data.add_features(raw)


@pytest.fixture
def posts() -> pd.DataFrame:
    return make_posts()


def _boost_likes(df: pd.DataFrame, mask: pd.Series, factor: float) -> pd.DataFrame:
    out = df.copy()
    out.loc[mask, "likes"] = (out.loc[mask, "likes"] * factor).round().astype(int)
    out["interactions"] = out[["likes", "shares", "comments_count"]].sum(axis=1)
    out[questions.ENGAGEMENT] = out["interactions"] / out["views"]
    return out


def test_q1_quiet_on_noise(posts):
    answer = questions.what_drives_engagement(posts)
    assert not answer.details["Segmentos significativos"].shape[0]
    assert answer.verdict.startswith("Nenhum")


def test_q1_finds_planted_segment(posts):
    mask = (posts.platform == "TikTok") & (posts.content_type == "video")
    answer = questions.what_drives_engagement(_boost_likes(posts, mask, 1.10))
    assert "TikTok · video" in answer.verdict


def test_q2_stratified_difference_recovers_known_uplift(posts):
    boosted = _boost_likes(posts, posts.is_sponsored, 1.10)
    result = questions.stratified_difference(boosted, boosted.is_sponsored, "likes", questions.STRATA)
    assert result["diferença (%)"] == pytest.approx(10, abs=1) and result["p_value"] < 1e-6


def test_q2_says_yes_only_with_effect(posts):
    assert questions.does_sponsorship_work(posts).verdict.startswith("Não")
    boosted = _boost_likes(posts, posts.is_sponsored & (posts.follower_tier == "mega (500K+)"), 1.15)
    answer = questions.does_sponsorship_work(boosted)
    assert answer.verdict.startswith("Sim")
    conditions = answer.details["Em que condições? (uplift do patrocínio por condição)"]
    assert conditions.iloc[0]["condição"] == "follower_tier = mega (500K+)"


def test_q2_implied_cpm_grows_with_followers(posts):
    cost = questions.does_sponsorship_work(posts).details["Custo implícito por porte de creator (patrocinados)"]
    assert cost["cpm_implicito_mediano"].is_monotonic_increasing


def test_q3_finds_audience_that_engages_in_context(posts):
    mask = (posts.content_category == "tech") & (posts.audience_gender_distribution == "female")
    answer = questions.audience_that_engages(_boost_likes(posts, mask, 1.10))
    sig = answer.details["Por contexto (plataforma, formato, categoria)"].query("significativo")
    assert "content_category = tech" in sig["contexto"].tolist()


def test_q4_belief_holds_when_true(posts):
    posts = posts.copy()
    posts["views"] = posts["views"] + posts["follower_count"] // 100
    beliefs = questions.what_does_not_work(posts).evidence.set_index("crença de mercado")
    assert beliefs.loc["Mais seguidores → mais alcance", "se sustenta?"] == "sim"
    assert beliefs.loc["Mais hashtags → mais alcance", "se sustenta?"] == "não"
