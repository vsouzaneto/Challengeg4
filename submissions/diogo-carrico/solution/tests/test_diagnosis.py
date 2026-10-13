import numpy as np
import pandas as pd
import pytest

from support_triage.diagnosis import (
    max_deviation_test,
    minimum_detectable_deviation,
    segment_codes,
)
from support_triage.fmt import d, pct, seg
from support_triage.waste import ASSUMPTIONS, estimate, hours_saved, scenario


def test_max_deviation_test_finds_a_planted_segment():
    rng = np.random.default_rng(0)
    codes = np.repeat(np.arange(5), 400)
    y = rng.binomial(1, 0.3, size=codes.size).astype(float)
    y[codes == 3] = rng.binomial(1, 0.6, size=400)
    r = max_deviation_test(y, codes, [f"s{i}" for i in range(5)], n_perm=500)
    assert r["largest_deviation_segment"] == "s3"
    assert r["familywise_p_value"] < 0.01


def test_max_deviation_test_stays_quiet_on_noise():
    rng = np.random.default_rng(1)
    codes = np.repeat(np.arange(20), 100)
    y = rng.binomial(1, 0.5, size=codes.size).astype(float)
    r = max_deviation_test(y, codes, [f"s{i}" for i in range(20)], n_perm=500)
    assert r["familywise_p_value"] > 0.05
    assert abs(r["largest_deviation"]) <= r["null_95pct_of_largest_deviation"]


def test_minimum_detectable_deviation_shrinks_with_sample_size():
    assert minimum_detectable_deviation(1.0, 400, 4) < minimum_detectable_deviation(
        1.0, 100, 4
    )
    assert minimum_detectable_deviation(1.0, 100, 80) > minimum_detectable_deviation(
        1.0, 100, 4
    )


def test_segment_codes_join_columns():
    df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["1", "1", "1"]})
    codes, labels = segment_codes(df, ["a", "b"])
    assert labels == ["x | 1", "y | 1"]
    assert list(codes) == [0, 1, 0]


def test_waste_formula_by_hand():
    p = {
        "tickets_per_month": 1000,
        "auto_route_share": 0.5,
        "triage_minutes": 6,
        "misroute_rate": 0.1,
        "rework_minutes": 12,
    }
    # 500 routed tickets save 50 h; 50 misroutes cost 10 h of rework.
    assert hours_saved(p) == pytest.approx(40.0)


def test_waste_scenarios_are_ordered():
    s = estimate()["scenarios"]
    assert (
        s["pessimistic"]["brl_per_month"]
        < s["base"]["brl_per_month"]
        < s["optimistic"]["brl_per_month"]
    )
    pess = scenario("pessimistic")
    assert pess["misroute_rate"] == ASSUMPTIONS["misroute_rate"].high
    assert pess["triage_minutes"] == ASSUMPTIONS["triage_minutes"].low


def test_pt_br_formatting():
    assert d(1234.5, 1) == "1.234,5"
    assert d(-0.04, 2) == "−0,04"
    assert pct(0.673) == "67,3%"
    assert seg("Phone | Low") == "Phone · Low"
