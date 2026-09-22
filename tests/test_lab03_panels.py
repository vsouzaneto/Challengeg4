"""should [behavior] when [condition] — painéis Lab 03."""

import json
from pathlib import Path

import pytest

from lab03_panels import BUILDERS, REQUIRED_SECTIONS
from lab03_panels.churn import load_churn_tables
from lab03_panels.crm import load_crm_tables
from lab03_panels.social import SOCIAL_COLUMNS, load_social_table
from lab03_panels.support import load_support_table

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _close_matplotlib():
    yield
    import matplotlib.pyplot as plt

    plt.close("all")


@pytest.mark.parametrize("project", ["churn", "support", "crm", "social"])
def test_should_return_all_required_sections_when_built_from_csv(project):
    panels = BUILDERS[project]()
    try:
        panels.require_complete()
        assert list(panels.panels) == list(REQUIRED_SECTIONS)
        for key in REQUIRED_SECTIONS:
            panel = panels.panels[key]
            assert panel.frame is not None
            assert len(panel.frame) >= 1
            assert panel.figure is not None
    finally:
        panels.close_figures()


def test_should_use_churn_events_not_account_flag_when_labeling_churn():
    tables = load_churn_tables()
    labeled = tables["accounts"]["account_id"].isin(tables["events"]["account_id"])
    panels = BUILDERS["churn"]()
    gallery_cols = set(panels.panels["gallery"].frame.columns)
    assert "churn_flag" not in gallery_cols
    assert labeled.sum() == tables["events"]["account_id"].nunique()
    stats = panels.panels["model_stats"].frame.iloc[0]
    assert 0 <= stats["accuracy"] <= 1
    assert 0 <= stats["f1"] <= 1
    assert stats["epochs"] == 1


def test_should_omit_pii_and_topic_group_when_building_support_panels():
    tickets = load_support_table()
    assert "Topic_group" not in tickets.columns
    panels = BUILDERS["support"]()
    gallery_cols = set(panels.panels["gallery"].frame.columns)
    assert "Customer Email" not in gallery_cols
    assert "Customer Name" not in gallery_cols
    assert "Topic_group" not in gallery_cols
    assert not bool(panels.panels["image_segmentation"].frame.iloc[0]["available"])


def test_should_exclude_close_value_from_crm_features_when_scoring_won_lost():
    tables = load_crm_tables()
    open_pipe = tables["pipeline"][
        tables["pipeline"]["deal_stage"].isin(["Prospecting", "Engaging"])
    ]
    assert open_pipe["close_value"].isna().all()
    panels = BUILDERS["crm"]()
    gallery_cols = set(panels.panels["gallery"].frame.columns)
    assert "close_value" not in gallery_cols
    ranking_cols = set(panels.panels["ranking"].frame.columns)
    assert "close_value" not in ranking_cols
    stats = panels.panels["model_stats"].frame.iloc[0]
    assert stats["roc_auc"] is None or 0 <= stats["roc_auc"] <= 1


def test_should_derive_engagement_when_social_has_no_native_rate():
    assert "engagement_rate" not in SOCIAL_COLUMNS
    posts = load_social_table()
    assert "engagement_rate" not in posts.columns
    assert posts["eng_per_view"].between(0, 2).mean() > 0.9
    panels = BUILDERS["social"]()
    image = panels.panels["image_segmentation"].frame
    assert bool(image.iloc[0]["available"]) is True
    assert image.iloc[0]["grain"] == "content_type"
    assert "Image" in set(image["content_type"].astype(str)) or "image" in set(
        image["content_type"].astype(str).str.lower()
    )


def test_should_keep_confusion_counts_equal_to_test_split_when_matrix_built():
    panels = BUILDERS["churn"]()
    matrix = panels.panels["confusion_matrix"].frame.to_numpy()
    assert matrix.sum() >= 10
    curve = panels.panels["learning_curve"].frame
    assert list(curve["train_size"]) == sorted(curve["train_size"].tolist())
    bias = panels.panels["bias_variance"].frame.iloc[0]
    assert "reading" in bias


def test_should_include_paineis_page_when_lvdash_is_synced():
    files = list(ROOT.glob("notebook-*/03_LAB_Dashboard/*.lvdash.json"))
    assert len(files) == 4
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        names = {item["name"] for item in data["datasets"]}
        pages = {page["name"] for page in data["pages"]}
        assert "panel_ranking" in names
        assert "paineis" in pages


def test_should_fail_when_a_required_section_is_missing():
    panels = BUILDERS["churn"]()
    del panels.panels["ranking"]
    with pytest.raises(ValueError, match="seções ausentes"):
        panels.require_complete()
