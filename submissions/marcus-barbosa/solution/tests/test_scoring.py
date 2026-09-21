"""Invariantes do score e da calibração. Rodam sobre dados sintéticos pequenos, sem os CSVs reais."""
import numpy as np
import pandas as pd

from leadscorer.calibration import (AGE_BANDS, MAX_SUPPORT_DAYS, MIN_BAND_DEALS, WINDOW_START, Calibration, build_panel, calibrate,
                                    open_engaging_at, snapshot_dates)
from leadscorer.data import enrich, load_tables, reference_date
from leadscorer.scoring import (CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW, CAT_LAST, CAT_QUALIFY, SUPPORT_BEYOND, SUPPORT_NONE, SUPPORT_OK,
                                SUPPORT_THIN, open_pipeline_at, score_pipeline)

BANDS = [b for _, _, b in AGE_BANDS]


def _cal(as_of="2017-12-31", p=None):
    p = p or {"0-14": 0.37, "15-90": 0.41, "91-120": 0.25, "121-138": 0.05}
    return Calibration(as_of=pd.Timestamp(as_of), horizon_days=90, snapshots=("2017-03-31", "2017-04-30"), n_obs=1000, n_deals=600,
                       p_by_band=p, p_close_by_band={k: 0.8 for k in BANDS}, n_deals_by_band={k: 100 for k in BANDS}, n_obs_by_band={k: 200 for k in BANDS},
                       ci_by_band={k: (0.3, 0.5) for k in BANDS})


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


def _synthetic_history(n_deals=900, seed=11):
    """Base sintética com histórico suficiente para o painel: deals engajados ao longo de 2017."""
    rng = np.random.default_rng(seed)
    engage = pd.Timestamp("2017-02-01") + pd.to_timedelta(rng.integers(0, 300, n_deals), unit="D")
    cycle = rng.integers(1, 139, n_deals)
    close = engage + pd.to_timedelta(cycle, unit="D")
    won = rng.random(n_deals) < 0.6
    stage = np.where(won, "Won", "Lost")
    still_open = rng.random(n_deals) < 0.25
    stage = np.where(still_open, "Engaging", stage)
    close = pd.Series(close).where(~still_open, pd.NaT)
    df = pd.DataFrame({
        "opportunity_id": [f"D{i}" for i in range(n_deals)], "sales_agent": "A", "product": "P", "account": np.where(still_open & (rng.random(n_deals) < 0.6), None, "Acme"),
        "deal_stage": stage, "engage_date": engage, "close_date": close, "close_value": np.where(won, 500.0, 0.0), "sales_price": 500.0,
        "sector": "x", "revenue": 1.0, "manager": "M", "regional_office": "R",
    })
    df["is_open"] = df["deal_stage"].isin(("Prospecting", "Engaging")); df["is_closed"] = ~df["is_open"]; df["has_account"] = df["account"].notna()
    return df


def truncate_history(enriched: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """A base como um analista a veria em as_of: fechamentos futuros viram abertos, engajamentos futuros não existem."""
    df = enriched[enriched["engage_date"].isna() | (enriched["engage_date"] <= as_of)].copy()
    future = df["close_date"].notna() & (df["close_date"] > as_of)
    df.loc[future, ["close_date", "close_value"]] = [pd.NaT, np.nan]
    df.loc[future, "deal_stage"] = "Engaging"
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


def test_agent_and_sector_do_not_change_score():
    base = _big_pipeline()
    s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    mod = base.copy()
    mod["sales_agent"] = mod["sales_agent"].map({"A": "C", "B": "A", "C": "B"}); mod["sector"] = "outro"
    s2, _ = score_pipeline(mod, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"].sort_index(), s2.set_index("opportunity_id")["score"].sort_index())


def test_close_value_and_close_date_of_open_deal_are_ignored():
    base = _big_pipeline()
    s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    leak = base.copy(); leak["close_value"] = 99999.0; leak["close_date"] = pd.Timestamp("2018-01-15")
    s2, _ = score_pipeline(leak, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"].sort_index(), s2.set_index("opportunity_id")["score"].sort_index())


def test_account_is_action_not_factor():
    base = _big_pipeline()
    s1, _ = score_pipeline(base, pd.Timestamp("2017-12-31"), _cal())
    no_acc = s1[s1["account"].isna() & (s1["support"] == SUPPORT_OK)]
    assert len(no_acc) > 0 and no_acc["score"].notna().all() and no_acc["needs_account"].all()
    assert no_acc["next_step"].str.startswith("Cadastrar a conta no CRM hoje; depois, ").all()
    filled = base.copy(); filled["account"] = "Acme"; s2, _ = score_pipeline(filled, pd.Timestamp("2017-12-31"), _cal())
    pd.testing.assert_series_equal(s1.set_index("opportunity_id")["score"].sort_index(), s2.set_index("opportunity_id")["score"].sort_index())


def test_expected_value_monotone_and_age_changes_score():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    ok = scored[scored["support"] == SUPPORT_OK].sort_values("score")
    assert ok["expected_value"].is_monotonic_increasing
    assert ok[ok["list_value"] == 4821.0]["score"].nunique() > 1


def test_categories_follow_rules():
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), _cal())
    assert (scored.loc[scored["category"] == CAT_QUALIFY, "stage_at_asof"] == "Prospecting").all()
    assert (scored.loc[scored["category"] == CAT_ALIVE, "age_days"] > MAX_SUPPORT_DAYS).all()
    assert scored.loc[scored["category"] == CAT_LAST, "age_days"].between(91, MAX_SUPPORT_DAYS).all()
    assert (scored.loc[scored["category"] == CAT_CRITICAL, "age_days"] <= 14).all()
    focus = scored[scored["category"] == CAT_FOCUS]
    assert (focus["score"] >= 70).all() and focus["age_days"].between(15, 90).all()
    assert (scored.loc[scored["category"] == CAT_FOLLOW, "score"] < 70).all()
    assert set(scored["category"]) <= {CAT_QUALIFY, CAT_ALIVE, CAT_LAST, CAT_CRITICAL, CAT_FOCUS, CAT_FOLLOW}


def test_thin_band_gets_no_score_and_says_so():
    cal = _cal(p={"0-14": 0.37, "15-90": 0.41, "91-120": None, "121-138": None})
    scored, _ = score_pipeline(_big_pipeline(), pd.Timestamp("2017-12-31"), cal)
    thin = scored[scored["age_days"].between(91, 138)]
    assert (thin["support"] == SUPPORT_THIN).all() and thin["score"].isna().all()
    assert thin["explanation"].str.contains("amostra suficiente").all()


def test_snapshot_dates_never_cross_as_of():
    dates = snapshot_dates(pd.Timestamp("2017-12-31"), 90)
    assert dates[0] == pd.Timestamp("2017-03-31")
    assert all(d + pd.Timedelta(days=90) <= pd.Timestamp("2017-12-31") for d in dates)
    assert snapshot_dates(pd.Timestamp("2017-05-01"), 90) == []


def test_panel_respects_window_start_and_horizon():
    df = _big_pipeline()
    df.loc[10, ["deal_stage", "engage_date", "close_date", "close_value", "account"]] = ["Won", pd.Timestamp("2017-03-01"), pd.Timestamp("2017-08-15"), 500.0, "Acme"]
    df.loc[11, ["deal_stage", "engage_date", "close_date", "close_value", "account"]] = ["Won", pd.Timestamp("2017-03-10"), pd.Timestamp("2017-05-01"), 500.0, "Acme"]
    df.loc[12, ["deal_stage", "engage_date", "close_date", "close_value", "account"]] = ["Won", pd.Timestamp("2016-12-01"), pd.Timestamp("2017-04-10"), 500.0, "Acme"]
    panel = build_panel(df, [pd.Timestamp("2017-03-31")], 90)
    ids = set(panel["opportunity_id"])
    assert "O12" not in ids                      # engajado antes de 2017-03-01: fora do painel
    assert bool(panel.set_index("opportunity_id").loc["O10", "won_h"]) is False   # ganho fora do horizonte
    assert bool(panel.set_index("opportunity_id").loc["O11", "won_h"]) is True
    assert (open_engaging_at(df, pd.Timestamp("2017-03-31"))["engage_date"] >= WINDOW_START).all()


def test_calibration_and_score_do_not_see_the_future():
    full = _synthetic_history()
    as_of = pd.Timestamp("2017-09-30")
    cal_full = calibrate(full, as_of)
    cal_trunc = calibrate(truncate_history(full, as_of), as_of)
    assert cal_full.mode == "painel" and cal_full.p_by_band == cal_trunc.p_by_band
    for b in BANDS:
        np.testing.assert_allclose(cal_full.ci_by_band[b], cal_trunc.ci_by_band[b], equal_nan=True)
    s_full, _ = score_pipeline(full, as_of, cal_full, include_prospecting=False)
    s_trunc, _ = score_pipeline(truncate_history(full, as_of), as_of, cal_trunc, include_prospecting=False)
    pd.testing.assert_series_equal(s_full.set_index("opportunity_id")["score"].sort_index(), s_trunc.set_index("opportunity_id")["score"].sort_index())


def test_small_band_pools_with_older_bands_never_younger():
    full = _synthetic_history(n_deals=900)
    # tira quase todos os deals que estariam na faixa 121-138 em algum snapshot: força a fusão
    as_of = pd.Timestamp("2017-12-31")
    panel = build_panel(full, snapshot_dates(as_of), 90)
    old_ids = set(panel.loc[panel["band"] == "121-138", "opportunity_id"])
    keep = list(old_ids)[: MIN_BAND_DEALS - 5]
    reduced = full[~full["opportunity_id"].isin(old_ids - set(keep))]
    cal = calibrate(reduced, as_of)
    assert cal.mode == "painel"
    if "121-138" in cal.pooled_from:
        assert cal.pooled_from["121-138"] == "121-138" or cal.pooled_from["121-138"].startswith("121-138")
        assert "15-90" not in cal.pooled_from["121-138"] and "0-14" not in cal.pooled_from["121-138"]


def test_calibration_ci_is_by_deal_and_bands_have_counts():
    full = _synthetic_history()
    cal = calibrate(full, pd.Timestamp("2017-12-31"))
    for b in BANDS:
        if cal.p_by_band[b] is not None:
            lo, hi = cal.ci_by_band[b]
            assert 0.0 <= lo <= cal.p_by_band[b] <= hi <= 1.0
            assert cal.n_deals_by_band[b] <= cal.n_obs_by_band[b]


def test_calibration_falls_back_and_says_so_on_small_data(raw_dir):
    e = enrich(load_tables(raw_dir))
    cal = calibrate(e, pd.Timestamp("2017-12-31"))
    assert cal.mode.startswith("fallback")
    assert set(cal.p_by_band) == set(BANDS)


def test_reference_date_anchor_not_today(raw_dir):
    t = load_tables(raw_dir)
    assert reference_date(t.pipeline) < pd.Timestamp("2018-01-01")


def test_open_pipeline_excludes_closed_before_and_prospecting_when_asked():
    df = _big_pipeline()
    df.loc[10, ["deal_stage", "engage_date", "close_date", "close_value", "is_open", "is_closed"]] = ["Won", pd.Timestamp("2017-05-01"), pd.Timestamp("2017-07-15"), 500.0, False, True]
    at_june = open_pipeline_at(df, pd.Timestamp("2017-06-30"))
    assert "O10" in set(at_june["opportunity_id"])
    assert "O10" not in set(open_pipeline_at(df, pd.Timestamp("2017-08-01"))["opportunity_id"])
    assert (open_pipeline_at(df, pd.Timestamp("2017-06-30"), include_prospecting=False)["stage_at_asof"] == "Engaging").all()
