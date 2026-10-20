"""Tests for the attribute × metric scan: every type of attribute must surface a planted effect, and only it."""
import numpy as np
import pandas as pd
import pytest

from social_insights import attribute_scan as sc
from test_questions import make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    df = make_posts()
    df["content_url"] = np.where(df.index % 2 == 0, "https://a.com/", "http://b.org/")
    df["creator_id"] = "creator_" + (df.index % 800).astype(str)
    df["comments_text"] = "Nice. Great!"
    return df


def _row(table, attribute, target):
    return table.set_index(["atributo", "alvo"]).loc[(attribute, target)]


def test_scan_is_quiet_on_noise(posts):
    table = sc.scan(posts, targets=["views"])
    assert not table["significativo"].any()


@pytest.mark.parametrize("attribute, plant", [
    ("platform", lambda d: d.platform == "TikTok"),
    ("follower_count", lambda d: d.follower_count > 500_000),
    ("creator_id", lambda d: d.creator_id.isin([f"creator_{i}" for i in range(80)])),
    ("content_description", lambda d: d.content_description.str.startswith("a much")),
])
def test_scan_flags_planted_attribute(posts, attribute, plant):
    posts.loc[plant(posts), "likes"] += 60
    row = _row(sc.scan(posts, targets=["likes"]), attribute, "likes")
    assert row["significativo"] and row["variância explicada (%)"] > 1


def test_skipped_and_matrix(posts):
    assert "sponsor_name" in sc.skipped_attributes().index
    matrix = sc.summary_matrix(sc.scan(posts, targets=["views", "likes"]))
    assert set(matrix.columns) == {"views", "likes"} and "platform" in matrix.index
