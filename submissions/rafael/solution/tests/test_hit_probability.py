"""Tests for the top-5% hit predictor: EB segment math, BH-gated adoption, planted segment detection, fallback."""
import numpy as np
import pandas as pd
import pytest

from social_insights import hit_probability as hp
from test_questions import _boost_likes, make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    df = make_posts()
    df["creator_id"] = "c" + (df.index % 400).astype(str)
    return df


def test_segment_rate_shrinks_toward_base():
    X = pd.DataFrame({"platform": ["a"] * 10 + ["b"] * 990, "content_category": "x", "language": "y"})
    y = np.r_[np.ones(10), np.zeros(990)]
    model = hp.SegmentRate(k=200).fit(X, y)
    p_small = model.predict_proba(X.head(1))[0, 1]
    assert 0.01 < p_small < 0.1  # 10/10 hits, but heavily shrunk toward the 1% base
    low, high = model.interval("a · x · y")
    assert low < p_small < high


def test_mark_adoptable_requires_correction():
    table = pd.DataFrame({"modelo": ["taxa base", "m1", "m2"], "p (AUC > 0,5)": [1.0, 0.03, 0.04], "ganho Brier vs. base (%)": [0, 0.5, 0.5]})
    nulls = pd.DataFrame({"modelo": "m3", "p (AUC > 0,5)": np.linspace(0.2, 0.99, 38), "ganho Brier vs. base (%)": 0.1})
    assert not hp.mark_adoptable(pd.concat([table, nulls], ignore_index=True))["adotável"].any()  # 2 lucky p's among 40 tests
    strong = table.assign(**{"p (AUC > 0,5)": [1.0, 1e-6, 0.9]})
    assert hp.mark_adoptable(strong)["adotável"].tolist() == [False, True, False]


def test_planted_segment_is_learned_and_raises_chance(posts):
    pocket = (posts.platform == "TikTok") & (posts.content_category == "tech")
    boosted = _boost_likes(posts, pocket, 1.06)
    predictor = hp.HitPredictor.train(boosted, metrics=["likes"], media_types=["video"])
    assert predictor.chosen[("likes", "video")] != "taxa base"
    planned = boosted[boosted.content_type == "video"].head(400)
    from social_insights.views_forecast import add_creator_history
    pred = predictor.predict(add_creator_history(planned).loc[planned.index])
    inside = pred[pred["segmento"].str.startswith("TikTok · tech")]["chance top 5% (%)"].mean()
    outside = pred[~pred["segmento"].str.startswith("TikTok · tech")]["chance top 5% (%)"].mean()
    assert inside > 2 * outside


def test_noise_falls_back_to_base_rate(posts):
    predictor = hp.HitPredictor.train(posts, metrics=["views"], media_types=["video", "image"])
    assert set(predictor.chosen.values()) == {"taxa base"}
