"""Oráculos do PRD nos CSVs reais (CP-01): conferidos aqui, de forma reproduzível."""
import pytest

pytestmark = pytest.mark.real_data


def test_reconciliation_8800(real_dataset):
    assert real_dataset.audited
    assert [step.rows for step in real_dataset.steps] == [8800] * 4
    gaps = {step.table: step.gap_count for step in real_dataset.steps}
    assert gaps["products"] == 0
    assert gaps["sales_teams"] == 0
    assert gaps["accounts"] == 0


def test_gtxpro_regression_1480(real_dataset):
    assert real_dataset.unmatched_without_map == 1480


def test_stage_counts(real_dataset):
    stages = real_dataset.opportunities["deal_stage"].value_counts().to_dict()
    assert stages == {"Won": 4238, "Lost": 2473, "Engaging": 1589, "Prospecting": 500}
