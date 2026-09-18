from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import app_data
from src.audit.health import health_check, verdict
from src.decision.rules import sales_to_break_even

ASSETS = Path(__file__).resolve().parents[1] / "app" / "assets"


def poisson_like_challenge(n: int = 2_000) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "views": rng.poisson(10_100, n), "likes": rng.poisson(1_510, n),
        "shares": rng.poisson(300, n), "comments_count": rng.poisson(200, n),
        "is_sponsored": rng.random(n) < 0.4,
        "creator_id": rng.integers(0, 200, n), "creator_name": [f"n{i}" for i in range(n)],
        "post_date": "5/29/23 12:15 AM",
    })


def codes(checks, passed):
    return {c.code for c in checks if c.passed is passed}


def test_challenge_like_file_is_rejected_for_the_right_reasons():
    checks = health_check(poisson_like_challenge())
    ok, _ = verdict(checks)
    assert not ok
    assert {"H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11"} <= codes(checks, False)


def test_instrumented_example_is_approved():
    df = pd.read_csv(ASSETS / "exemplo_sintetico_contrato_de_dados.csv")
    ok, message = verdict(health_check(df))
    assert ok, message


def test_real_challenge_file_is_rejected():
    ok, _ = verdict(health_check(app_data.load_posts()))
    assert not ok


def test_missing_metrics_stop_early():
    checks = health_check(pd.DataFrame({"views": [1, 2, 3]}))
    assert len(checks) == 1 and not checks[0].passed


def test_small_files_are_not_judged_by_distribution_rules():
    df = pd.DataFrame({"views": [100, 110, 120], "likes": [10, 11, 12], "shares": [1, 1, 1], "comments": [1, 1, 1]})
    assert {"H4", "H5", "H7"} <= codes(health_check(df), True)


def test_sales_to_break_even():
    assert sales_to_break_even(3_000, 50) == 60
    assert sales_to_break_even(3_000, 50, 1_000) == 80
    with pytest.raises(ValueError):
        sales_to_break_even(3_000, 0)
