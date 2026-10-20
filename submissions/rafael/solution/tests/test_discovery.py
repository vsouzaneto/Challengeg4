"""Tests for pocket discovery and top-1% similarity: planted pockets replicate, planted similarity is detected."""
import numpy as np
import pandas as pd
import pytest

from social_insights import discovery as dv
from test_questions import make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 800).astype(str)
    return df


def test_planted_pocket_is_robust_and_replicates(posts):
    pocket = (posts.platform == "TikTok") & (posts.content_category == "tech")
    posts.loc[pocket, "views"] += 150
    table = dv.scan_pockets(posts, "views").set_index(["dimensão", "bolsão"])
    row = table.loc[("platform × content_category", "TikTok · tech")]
    assert row["evidência"] == "robusta (FDR)" and row["replicou"] and row["lift"] > 2


def test_replication_near_chance_on_noise(posts):
    summary = dv.replication_summary(dv.scan_pockets(posts, "views"))
    assert summary["robustos (FDR)"] == 0 and summary["p (replicação acima do acaso)"] > 0.01


def test_mean_similarity_matches_bruteforce(posts):
    X = dv._onehot(posts.head(40))
    brute = np.mean([(X[i] @ X[j]) / len(dv.CATEGORICAL) for i in range(40) for j in range(40) if i != j])
    assert dv.mean_similarity(X) == pytest.approx(brute)


def test_similarity_detects_homogeneous_top(posts):
    homogeneous = (posts.platform == "TikTok") & (posts.content_type == "video") & (posts.content_category == "tech")
    posts.loc[homogeneous, "views"] += 500
    top = dv.top_mask(posts, "views")
    assert dv.similarity_test(posts, top, draws=50)["p_value"] < 0.05


def test_insight_cards_are_sentences(posts):
    posts.loc[(posts.platform == "TikTok") & (posts.content_category == "tech"), "views"] += 150
    cards = dv.insight_cards(dv.scan_pockets(posts, "views"), n=3)
    assert cards["insight"].str.contains("top 5% de views").all()


def test_scan_by_platform_finds_pocket_only_in_its_platform(posts):
    pocket = (posts.platform == "TikTok") & (posts.content_category == "tech")
    posts.loc[pocket, "likes"] += 120
    table = dv.scan_by_platform(posts, "likes", platforms=["TikTok", "YouTube"])
    assert "platform" not in " ".join(table["dimensão"])
    hits = table[(table["dimensão"] == "content_category") & (table["bolsão"] == "tech") & (table["evidência"] == "robusta (FDR)")]
    assert set(hits["plataforma"]) == {"TikTok"}


def test_daypart_top_rate_detects_morning_effect(posts):
    posts.loc[posts.daypart == "manhã", "comments_count"] += 30
    table = dv.daypart_top_rate(posts, "comments_count", q=0.95)
    assert (table["manhã"] > table["tarde"]).all() and (table["p (qui²)"] < 0.05).all()
