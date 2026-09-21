"""Invariantes do score e da calibração. Rodam sobre dados sintéticos pequenos, sem os CSVs reais."""
import numpy as np
import pandas as pd

from leadscorer.calibration import AGE_BANDS, MAX_SUPPORT_DAYS, Calibration, build_panel, calibrate, snapshot_dates, wilson
from leadscorer.data import enrich, load_tables, reference_date
from leadscorer.scoring import (CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW, CAT_QUALIFY, SUPPORT_BEYOND, SUPPORT_NONE, SUPPORT_OK,
                                score_pipeline)


def _cal(as_of="2017-12-31"):
    return Calibration(as_of=pd.Timestamp(as_of), horizon_days=90, snapshots=("2017-03-31", "2017-04-30"), n_rows=1000,
                       p_by_band={"0-14": 0.47, "15-90": 0.55, "91-120": 0.44, "121-138": 0.13},
                       n_by_band={"0-14": 500, "15-90": 400, "91-120": 80, "121-138": 60},
                       ci_by_band={k: (0.4, 0.6) for k in ("0-14", "15-90", "91-120", "121-138")})


def _big_pipeline(n=80, seed=1):
    rng = np.random.default_rng(seed)
    ages = rng.integers(0, 200, n)
    df = pd.DataFrame({
        "opportunity_id": [f"O{i}" for i in range(n)],
        "sales_agent": rng.choice(["A", "B", "C"], n),
        "product": rng.choice(["P1", "P2", "P3"], n),
        "account": rng.choice(["Acme", None], n),
        "deal_stage": ["Engaging"] * n,
        "engage_date": pd.Timestamp("2017-12-31") - pd.to_timedelta(ages, unit="D"),
        "close_date": pd.NaT, "close_value": np.nan,
        "sales_price": rng.choice([55.0, 550.0, 4821.0, 26768.0], n),
        "sector": "x", "revenue": 1.0, "manager": "M", "regional_office": "R",
    })
    df.loc[:4, "deal_stage"] = "Prospecting"; df.loc[:4, "engage_date"] = pd.NaT
    df["is_open"] = True; df["is_closed"] = False; df["has_account"] = df["account"].notna()
    return df


def test_score_range_and_support():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    ok = scored[scored["support"] == SUPPORT_OK]
    assert ok["score"].between(0, 100).all()
    assert scored.loc[scored["support"] != SUPPORT_OK, "score"].isna().all()
    assert (scored.loc[scored["age_days"] > MAX_SUPPORT_DAYS, "support"] == SUPPORT_BEYOND).all()
    assert (scored.loc[scored["stage_at_asof"] == "Prospecting", "support"] == SUPPORT_NONE).all()


def test_deterministic():
    a, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    b, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_frame_equal(a, b)


def test_agent_product_sector_do_not_change_score():
    base = _big_pipeline()
    s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    mod = base.copy()
    mod["sales_agent"] = mod["sales_agent"].map({"A": "C", "B": "A", "C": "B"})
    mod["sector"] = "outro"; mod["product"] = mod["product"].map({"P1": "P3", "P2": "P1", "P3": "P2"})
    s2, _ = score_pipeline(mod, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"], s2.set_index("opportunity_id")["score"])


def test_close_value_and_close_date_of_open_deal_are_ignored():
    base = _big_pipeline()
    s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    leak = base.copy()
    leak["close_value"] = 99999.0
    leak["close_date"] = pd.Timestamp("2018-01-15")
    s2, _ = score_pipeline(leak, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"], s2.set_index("opportunity_id")["score"])


def test_deal_without_account_gets_score_and_flag():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    no_acc = scored[scored["account"].isna() & (scored["support"] == SUPPORT_OK)]
    assert len(no_acc) > 0 and no_acc["score"].notna().all() and no_acc["needs_account"].all()
    assert no_acc["explanation"].str.contains("Sem conta cadastrada").all()
    # conta não é fator: mesmo deal com e sem conta tem o mesmo score
    base = _big_pipeline(); s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    filled = base.copy(); filled["account"] = "Acme"; s2, _ = score_pipeline(filled, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"].sort_index(), s2.set_index("opportunity_id")["score"].sort_index())


def test_expected_value_monotone_in_score_and_age_matters():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    ok = scored[scored["support"] == SUPPORT_OK].sort_values("score")
    assert ok["expected_value"].is_monotonic_increasing
    # o score não é só ordenar por preço: o mesmo preço recebe scores diferentes conforme a idade
    same_price = ok[ok["list_value"] == 4821.0]
    assert same_price["score"].nunique() > 1


def test_categories_follow_rules():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    assert (scored.loc[scored["category"] == CAT_QUALIFY, "stage_at_asof"] == "Prospecting").all()
    assert (scored.loc[scored["category"] == CAT_ALIVE, "age_days"] > MAX_SUPPORT_DAYS).all()
    assert (scored.loc[scored["category"] == CAT_CRITICAL, "age_days"] <= 14).all()
    assert (scored.loc[scored["category"] == CAT_FOCUS, "score"] >= 70).all()
    assert (scored.loc[scored["category"] == CAT_FOLLOW, "score"] < 70).all()
    assert set(scored["category"]) <= {CAT_QUALIFY, CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW}


def test_snapshot_dates_never_cross_as_of():
    dates = snapshot_dates(pd.Timestamp("2017-12-31"), 90)
    assert dates[0] == pd.Timestamp("2017-03-31")
    assert all(d + pd.Timedelta(days=90) <= pd.Timestamp("2017-12-31") for d in dates)
    assert snapshot_dates(pd.Timestamp("2017-05-01"), 90) == []


def test_panel_uses_only_outcomes_inside_horizon():
    df = _big_pipeline()
    # deal engajado em 2017-03-01, ganho em 2017-08-15: aberto no snapshot 2017-03-31, mas fora do horizonte de 90 d
    df.loc[10, ["deal_stage", "engage_date", "close_date", "close_value", "account"]] = ["Won", pd.Timestamp("2017-03-01"), pd.Timestamp("2017-08-15"), 500.0, "Acme"]
    # deal engajado em 2017-03-10, ganho em 2017-05-01: dentro do horizonte
    df.loc[11, ["deal_stage", "engage_date", "close_date", "close_value", "account"]] = ["Won", pd.Timestamp("2017-03-10"), pd.Timestamp("2017-05-01"), 500.0, "Acme"]
    panel = build_panel(df, [pd.Timestamp("2017-03-31")], 90)
    row10 = panel[panel["opportunity_id"] == "O10"].iloc[0]; row11 = panel[panel["opportunity_id"] == "O11"].iloc[0]
    assert bool(row10["won_h"]) is False and bool(row11["won_h"]) is True


def test_calibration_falls_back_and_says_so_on_small_data(raw_dir):
    e = enrich(load_tables(raw_dir))
    cal = calibrate(e, pd.Timestamp("2017-12-31"))
    assert cal.mode.startswith("fallback")
    assert set(cal.p_by_band) == {name for _, _, name in AGE_BANDS}
    assert all(0.0 <= p <= 1.0 for p in cal.p_by_band.values())


def test_wilson_bounds():
    lo, hi = wilson(50, 100)
    assert 0.40 < lo < 0.5 < hi < 0.60
    assert wilson(0, 0) == (0.0, 1.0)


def test_reference_date_anchor_not_today(raw_dir):
    t = load_tables(raw_dir)
    assert reference_date(t.pipeline) < pd.Timestamp("2018-01-01")


def test_snapshot_includes_deals_closed_later_and_excludes_closed_before():
    df = _big_pipeline()
    df.loc[10, ["deal_stage", "engage_date", "close_date", "close_value", "is_open", "is_closed"]] = ["Won", pd.Timestamp("2017-05-01"), pd.Timestamp("2017-07-15"), 500.0, False, True]
    scored, _ = score_pipeline(df, pd.Timestamp("2017-06-30"), _cal("2017-06-30"))
    assert "O10" in set(scored["opportunity_id"])
    scored2, _ = score_pipeline(df, pd.Timestamp("2017-08-01"), _cal("2017-08-01"))
    assert "O10" not in set(scored2["opportunity_id"])
