"""Unit tests: each method must find a planted signal and stay quiet on pure noise."""
import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_blobs

from social_insights import audience, cleaning, clustering, data, exploration, modeling, nlp, top_performers, validation

RNG = np.random.default_rng(0)
N = 4_000


@pytest.fixture
def raw() -> pd.DataFrame:
    return pd.DataFrame({
        "post_date": ["5/29/23 12:15 AM", "1/2/24 3:40 PM"] * (N // 2),
        "likes": RNG.poisson(1500, N), "shares": RNG.poisson(300, N), "comments_count": RNG.poisson(200, N),
        "views": RNG.poisson(10_000, N), "follower_count": RNG.integers(1_000, 1_000_000, N),
        "content_length": RNG.integers(10, 600, N), "hashtags": ["a,b", None] * (N // 2),
        "comments_text": ["great love it", None] * (N // 2), "content_description": ["nice post today"] * N,
        "platform": RNG.choice(["TikTok", "YouTube"], N), "content_type": RNG.choice(["video", "image"], N),
        "content_category": RNG.choice(["tech", "beauty"], N),
    })


def test_add_features_derives_columns(raw):
    df = data.add_features(raw)
    assert df["n_hashtags"].tolist()[:2] == [2, 0]
    assert df["daypart"].tolist()[:2] == ["madrugada", "tarde"]
    assert df["comments_text"].isna().sum() == 0
    assert np.allclose(df["eng_rate_views"], df["interactions"] / df["views"])


def test_flag_top_respects_groups(raw):
    top = top_performers.flag_top(raw, "views", by="platform")
    assert top.groupby(raw["platform"]).mean().between(0.08, 0.12).all()


def test_lift_detects_planted_effect_and_ignores_noise(raw):
    raw.loc[raw["platform"] == "TikTok", "views"] += 300
    table = top_performers.lift_table(raw, top_performers.flag_top(raw, "views"), ["platform", "content_type"])
    winners = top_performers.summarize_significant(table)
    assert "TikTok" in winners["value"].tolist()
    assert not table.query("feature == 'content_type'")["significant"].any()


def test_pair_lift_builds_combined_keys(raw):
    table = top_performers.pair_lift_table(raw, top_performers.flag_top(raw, "views"), ["platform", "content_type"])
    assert table["value"].str.contains(" & ").all()


def test_structure_test_separates_clusters_from_noise():
    blobs, _ = make_blobs(2_000, centers=3, cluster_std=0.3, random_state=0)
    noise = RNG.normal(size=(2_000, 2))
    assert clustering.structure_test(blobs, range(3, 4))["gain"].iloc[0] > 0.2
    assert abs(clustering.structure_test(noise, range(3, 4))["gain"].iloc[0]) < 0.05


def test_kmeans_scan_prefers_true_k():
    blobs, _ = make_blobs(1_500, centers=3, cluster_std=0.3, random_state=0)
    scan = clustering.kmeans_scan(blobs, range(2, 5))
    assert scan.loc[scan["silhouette"].idxmax(), "k"] == 3


def test_adjusted_residuals_flag_overrepresented_cell():
    df = pd.DataFrame({"type": ["video"] * 600 + ["image"] * 600 + ["text"] * 600,
                       "gender": (["female"] * 400 + ["male"] * 200) + (["female"] * 300 + ["male"] * 300) * 2})
    cells = audience.strongest_cells(df, "type", "gender")
    assert cells.iloc[0][["type", "gender"]].tolist() == ["video", "female"]


def test_log_odds_finds_distinctive_word():
    a = pd.Series(["amazing tutorial camera"] * 100)
    b = pd.Series(["boring camera"] * 100)
    table = nlp.log_odds_keywords(a, b, top_n=1, min_count=5)
    assert table.iloc[0]["word"] in {"amazing", "tutorial"}
    assert table.iloc[-1]["word"] == "boring"


def test_sentiment_sign():
    scores = nlp.sentiment(pd.Series(["I love this, amazing!", "Terrible, I hate it", ""]))
    assert scores[0] > 0 > scores[1] and np.isnan(scores[2])


def test_inject_uplift_only_touches_mask(raw):
    mask = raw["platform"] == "TikTok"
    out = validation.inject_uplift(raw, mask, "views", 0.05)
    assert out.loc[~mask, "views"].equals(raw.loc[~mask, "views"])
    assert out.loc[mask, "views"].mean() > raw.loc[mask, "views"].mean() * 1.03


def test_add_rates_and_spurious_ratio(raw):
    df = data.add_rates(data.add_features(raw))
    assert np.allclose(df["like_rate"], df["likes"] / df["views"])
    demo = exploration.spurious_ratio_demo(df)["Spearman ρ"]
    assert demo["likes EMBARALHADOS/seguidor × seguidores"] < -0.9 and abs(demo["likes × seguidores"]) < 0.1


def test_quality_report_counts_duplicates(raw):
    df = data.add_features(raw).assign(id=range(N), content_id=[f"c{i}" for i in range(N)])
    report = cleaning.quality_report(pd.concat([df, df.iloc[:3]]))["valor"]
    assert report["linhas duplicadas (todas as colunas)"] == 3


def test_categorical_tests_detect_group_effect(raw):
    raw.loc[raw["platform"] == "TikTok", "views"] += 200
    table = exploration.categorical_tests(raw, ["platform", "content_type"], ["views"]).set_index("variável")
    assert table.loc["platform", "significativo"] and not table.loc["content_type", "significativo"]


def test_explanatory_scenario_adds_other_metrics():
    cats, nums = modeling.scenario_columns("likes", "explicativo", data.METRICS)
    assert "views" in nums and "likes" not in nums
    assert set(modeling.scenario_columns("likes", "pré-publicação", data.METRICS)[1]).isdisjoint(data.METRICS)
