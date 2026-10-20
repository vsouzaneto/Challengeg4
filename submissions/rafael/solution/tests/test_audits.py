"""Tests for the audits: rules are applied correctly, quiet on noise, and each planted effect is detected."""
import pandas as pd
import pytest

from social_insights import audits
from test_questions import _boost_likes, make_posts


@pytest.fixture
def posts() -> pd.DataFrame:
    return make_posts()


def test_disclosure_risk_levels():
    df = pd.DataFrame({"is_sponsored": [True, True, True, False],
                       "disclosure_type": ["implicit", "explicit", "explicit", "none"],
                       "disclosure_location": ["caption", "video", "hashtags", "none"]})
    assert audits.disclosure_risk(df).tolist()[:3] == ["alto", "médio", "baixo"]
    assert pd.isna(audits.disclosure_risk(df).iloc[3])


def test_ad_marker_needs_a_real_label():
    df = pd.DataFrame({"hashtags": ["fun,#ad", "bad,road", None], "content_description": ["hi", "hi", "Sponsored by X"]})
    assert audits.has_ad_marker(df).tolist() == [True, False, True]


def test_disclosure_audit_quiet_then_detects_cost(posts):
    quiet = audits.disclosure_audit(posts)
    assert not quiet.details["Disclosure × engajamento"]["significativo"].any()
    assert "não mudam o engajamento" in quiet.verdict
    planted = _boost_likes(posts, posts.disclosure_type == "implicit", 1.10)
    assert audits.disclosure_audit(planted).details["Disclosure × engajamento"]["significativo"].any()


def test_sponsor_fit_quiet_then_detects_in_niche_uplift(posts):
    assert "não rende" in audits.sponsor_fit(posts).verdict
    in_niche = audits.sponsor_fits(posts).fillna(False).astype(bool)
    assert "rendem mais" in audits.sponsor_fit(_boost_likes(posts, in_niche, 1.10)).verdict


def test_market_coherence_flags():
    df = pd.DataFrame({"language": ["Chinese", "English", "Hindi"], "audience_location": ["China", "China", "India"],
                       "platform": ["Bilibili", "Bilibili", "TikTok"]})
    flags = audits.market_coherence_flags(df)
    assert flags["coerente"].tolist() == [True, False, False]
    assert flags["plataforma disponível"].tolist() == [True, True, False]


def test_market_coherence_detects_planted_effect(posts):
    assert not audits.market_coherence(posts).details["Coerentes × incoerentes"]["significativo"].any()
    coherent = audits.market_coherence_flags(posts)["coerente"]
    assert audits.market_coherence(_boost_likes(posts, coherent, 1.10)).details["Coerentes × incoerentes"]["significativo"].any()


def test_length_by_format_quiet_then_detects_video_length(posts):
    assert not audits.length_by_format(posts).evidence["significativo"].any()
    planted = posts.copy()
    video = planted.content_type == "video"
    planted.loc[video, "views"] = planted.loc[video, "views"] + planted.loc[video, "content_length"]
    hits = audits.length_by_format(planted).evidence.query("significativo")
    assert set(hits["formato"]) == {"video"}


def test_subgroup_power_flags_small_groups(posts):
    table = audits.subgroup_power(posts.head(300), relevant=0.002).evidence  # Poisson noise is tiny: use a strict bar
    assert not table["conclusivo"].all()
    full = audits.subgroup_power(posts).evidence
    assert full["MDE (%)"].min() < table["MDE (%)"].min()  # more posts → smaller detectable effect
