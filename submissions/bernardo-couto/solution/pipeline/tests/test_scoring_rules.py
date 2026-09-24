"""Invariants of the rules layer (docs/specs/scoring-spec.md section 6) on synthetic frames."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import pandas as pd
import pytest
from pyspark.sql import DataFrame, SparkSession

from lead_scorer.contracts import ReasonCode
from lead_scorer.data.gold import (
    DIM_ACCOUNT,
    DIM_GLOBAL,
    DIM_HAZARD14,
    DIM_PRODUCT,
    HAZARD_MAX_DAY,
)
from lead_scorer.scoring import rules
from lead_scorer.scoring.score import FEATURE_INPUTS, SCORED_DEAL_COLUMNS, score_frame
from lead_scorer.scoring.weights import DEFAULT_WEIGHTS, Weights

AS_OF = date(2017, 12, 31)
P0 = 0.63

FEATURE_SCHEMA = (
    "opportunity_id string, sales_agent string, manager string, regional_office string, "
    "product string, account string, account_known boolean, sector string, revenue double, "
    "employees int, deal_stage string, sales_price double, days_in_engaging int, "
    "global_win_rate double, win_rate_product double, n_product long, "
    "value_ratio_product double, win_rate_agent double, n_agent long, "
    "win_rate_agent_product double, n_agent_product long, win_rate_sector double, "
    "n_sector long, n_account long, win_rate_survival double, open_deals_agent long"
)

HISTORY_SCHEMA = (
    "dimension string, key string, key2 string, n long, wins long, win_rate double, "
    "median_cycle_days double, median_value_ratio double"
)


def deal(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "opportunity_id": "X1",
        "sales_agent": "Ana",
        "manager": "M",
        "regional_office": "Central",
        "product": "GTX Pro",
        "account": "Konex",
        "account_known": True,
        "sector": "medical",
        "revenue": 1200.5,
        "employees": 3000,
        "deal_stage": "Engaging",
        "sales_price": 4821.0,
        "days_in_engaging": 60,
        "global_win_rate": P0,
        "win_rate_product": 0.66,
        "n_product": 500,
        "value_ratio_product": 1.0,
        "win_rate_agent": 0.65,
        "n_agent": 200,
        "win_rate_agent_product": 0.70,
        "n_agent_product": 40,
        "win_rate_sector": 0.61,
        "n_sector": 300,
        "n_account": 5,
        "win_rate_survival": 0.70,
        "open_deals_agent": 20,
    }
    base.update(overrides)
    if base["deal_stage"] == "Prospecting":
        base["days_in_engaging"] = None
        base["win_rate_survival"] = None
    if not base["account_known"]:
        base.update(account=None, sector=None, revenue=None, employees=None, n_account=None)
    return base


def features_df(spark: SparkSession, deals: list[dict[str, Any]]) -> DataFrame:
    rows = [tuple(d[c] for c in FEATURE_INPUTS) for d in deals]
    return spark.createDataFrame(rows, FEATURE_SCHEMA)


def history_df(spark: SparkSession) -> DataFrame:
    rows: list[tuple[Any, ...]] = [
        (DIM_GLOBAL, "all", None, 6000, 3780, P0, 50.0, 1.0),
        (DIM_PRODUCT, "GTX Pro", None, 500, 330, 0.66, 50.0, 1.0),
        (DIM_ACCOUNT, "Konex", None, 5, 3, 0.6, 50.0, 1.0),
    ]
    # hazard rising until day 60 then falling; forward-filled flat above 120
    for d in range(HAZARD_MAX_DAY + 1):
        h = 0.10 + 0.20 * (d / 60) if d <= 60 else max(0.05, 0.30 - 0.20 * ((d - 60) / 60))
        rows.append((DIM_HAZARD14, str(d), None, 1000 - 5 * d, 100, round(h, 4), None, None))
    return spark.createDataFrame(rows, HISTORY_SCHEMA)


def score(
    spark: SparkSession, deals: list[dict[str, Any]], w: Weights = DEFAULT_WEIGHTS
) -> pd.DataFrame:
    out = score_frame(
        features_df(spark, deals), history_df(spark), as_of=AS_OF, model_version="test", weights=w
    ).toPandas()
    out["codes"] = out["reasons"].map(lambda rs: [r["code"] for r in rs])
    return out.set_index("opportunity_id", drop=False)


@pytest.fixture(scope="module")
def scored(spark: SparkSession) -> pd.DataFrame:
    deals = [
        deal(opportunity_id="alive_known", open_deals_agent=5),
        deal(opportunity_id="alive_unknown", account_known=False),
        deal(opportunity_id="late", days_in_engaging=130),
        deal(opportunity_id="zombie", days_in_engaging=200),
        deal(opportunity_id="zombie_rich", days_in_engaging=200, sales_price=26768.0),
        deal(opportunity_id="prosp_known", deal_stage="Prospecting"),
        deal(opportunity_id="prosp_unknown", deal_stage="Prospecting", account_known=False),
        deal(opportunity_id="cheap", sales_price=55.0),
        deal(opportunity_id="new_product", product="GTK 9000", win_rate_product=P0, n_product=0),
        deal(opportunity_id="small_agent", n_agent=10),
        deal(opportunity_id="overloaded", open_deals_agent=90),
    ]
    return score(spark, deals)


# --- 1. monotonic in sales_price ------------------------------------------------------------------


@pytest.mark.parametrize("days", [30, 100, 200, None])
def test_score_non_decreasing_in_price(spark: SparkSession, days: int | None) -> None:
    stage = "Prospecting" if days is None else "Engaging"
    prices = [55.0, 600.0, 1096.0, 4821.0, 5482.0, 26768.0]
    deals = [
        deal(opportunity_id=f"p{i}", sales_price=p, days_in_engaging=days, deal_stage=stage)
        for i, p in enumerate(prices)
    ]
    out = score(spark, deals).loc[[f"p{i}" for i in range(len(prices))], "priority_score"]
    assert list(out) == sorted(out)


# --- 2. zombies -----------------------------------------------------------------------------------


def test_zombie_invariants(scored: pd.DataFrame) -> None:
    for oid in ("zombie", "zombie_rich"):
        z = scored.loc[oid]
        assert ReasonCode.ZOMBIE_RISK.value in z["codes"]
        assert z["tier"] in {"C", "D"}
        assert z["priority_score"] <= DEFAULT_WEIGHTS.zombie_score_cap
        assert z["urgency"] == pytest.approx(DEFAULT_WEIGHTS.zombie_urgency)
        assert z["p_win"] == pytest.approx(0.66 * DEFAULT_WEIGHTS.zombie_p_factor, abs=1e-6)
        assert z["confidence"] == "baixa"
        assert z["next_action"] == rules.ACTION_ZOMBIE
    zr = next(r for r in scored.loc["zombie"]["reasons"] if r["code"] == "ZOMBIE_RISK")
    assert zr["direction"] == "-"
    # 25 * (p_scaled(0.33) - p_scaled(0.66)) = 25 * (0.06 - 0.72)
    assert zr["weight"] == pytest.approx(-16.5, abs=0.01)


def test_alive_has_no_zombie_reason_and_uses_hazard(scored: pd.DataFrame) -> None:
    a = scored.loc["alive_known"]
    assert ReasonCode.ZOMBIE_RISK.value not in a["codes"]
    assert ReasonCode.SURVIVAL_POSITIVE.value in a["codes"]
    assert a["urgency"] == pytest.approx(1.0)  # day 60 is the hazard peak in the fixture
    assert a["next_action"] == rules.ACTION_CALL and a["tier"] in {"A", "B"}


def test_late_cycle_countdown(scored: pd.DataFrame) -> None:
    late = scored.loc["late"]
    assert late["next_action"] == "Faltam 8 dias do ciclo máximo: fechar ou desistir esta semana."
    surv = next(r for r in late["reasons"] if r["code"] == "SURVIVAL_POSITIVE")
    assert "faltam 8 dias" in surv["text_pt"]


# --- 3. unknown account ---------------------------------------------------------------------------


def test_unknown_account_never_high_confidence(scored: pd.DataFrame) -> None:
    for oid in ("alive_unknown", "prosp_unknown"):
        row = scored.loc[oid]
        assert row["confidence"] != "alta"
        assert ReasonCode.ACCOUNT_UNKNOWN.value in row["codes"]
        for code in ("SECTOR_FIT", "ACCOUNT_SIZE", "ACCOUNT_HISTORY"):
            assert code not in row["codes"]
    known = scored.loc["alive_known"]
    assert known["confidence"] == "alta"
    assert {"SECTOR_FIT", "ACCOUNT_SIZE", "ACCOUNT_HISTORY"} <= set(known["codes"])


# --- 4. prospecting -------------------------------------------------------------------------------


def test_prospecting_invariants(scored: pd.DataFrame) -> None:
    for oid in ("prosp_known", "prosp_unknown"):
        p = scored.loc[oid]
        assert pd.isna(p["days_in_engaging"])
        assert p["urgency"] == pytest.approx(DEFAULT_WEIGHTS.prospecting_urgency)
        assert ReasonCode.PROSPECTING_NO_TIMELINE.value in p["codes"]
        assert ReasonCode.SURVIVAL_POSITIVE.value not in p["codes"]
    assert scored.loc["prosp_unknown"]["tier"] != "A"
    assert scored.loc["prosp_unknown"]["confidence"] == "baixa"
    assert scored.loc["prosp_known"]["confidence"] == "media"
    assert scored.loc["prosp_known"]["next_action"] == rules.ACTION_PROSPECTING
    assert scored.loc["prosp_unknown"]["next_action"] == rules.ACTION_PROSPECTING_NO_ACCOUNT


# --- 5. completeness and bounds -------------------------------------------------------------------


def test_every_deal_scored_without_nan(scored: pd.DataFrame) -> None:
    assert list(scored.columns[: len(SCORED_DEAL_COLUMNS)]) == list(SCORED_DEAL_COLUMNS)
    assert len(scored) == 11
    assert scored["score_breakdown"].map(lambda b: b is not None).all()
    for col in ("priority_score", "p_win", "expected_value", "urgency", "tier", "confidence"):
        assert scored[col].notna().all(), col
    assert scored["priority_score"].between(0, 100).all()
    assert scored["p_win"].between(0, 1).all()
    assert scored["urgency"].between(0, 1).all()
    assert (scored["reasons"].map(len) >= 1).all()
    assert (scored["expected_value"] >= 0).all()


# --- 6. determinism -------------------------------------------------------------------------------


def test_two_runs_are_identical(spark: SparkSession) -> None:
    deals = [deal(opportunity_id=f"d{i}", sales_price=100.0 * (i + 1)) for i in range(5)]
    a = score(spark, deals).drop(columns=["codes"])
    b = score(spark, deals).drop(columns=["codes"])
    pd.testing.assert_frame_equal(a, b)


# --- 10. unseen product -> prior ------------------------------------------------------------------


def test_unseen_product_gets_prior(scored: pd.DataFrame) -> None:
    row = scored.loc["new_product"]
    assert row["p_win"] == pytest.approx(P0)
    base = next(r for r in row["reasons"] if r["code"] == "PRODUCT_BASE_RATE")
    assert base["weight"] == pytest.approx(25 * (P0 - 0.30) / 0.50, abs=0.01)
    assert "0 deals no histórico" in base["text_pt"]


SCORE_CODES = {"PRODUCT_BASE_RATE", "HIGH_TICKET", "LOW_TICKET", "URGENCY_WINDOW", "ZOMBIE_RISK"}


def test_score_reasons_and_breakdown_add_up(scored: pd.DataFrame) -> None:
    """PRODUCT_BASE_RATE + ticket + URGENCY_WINDOW + ZOMBIE_RISK == priority_score (when a ticket
    reason exists); score_breakdown always adds up."""
    for _, row in scored.iterrows():
        b = row["score_breakdown"]
        assert b["p_win_points"] + b["value_points"] + b["urgency_points"] == pytest.approx(
            row["priority_score"], abs=0.01
        )
        codes = {r["code"] for r in row["reasons"]}
        assert "URGENCY_WINDOW" in codes and "PRODUCT_BASE_RATE" in codes
        total = sum(r["weight"] for r in row["reasons"] if r["code"] in SCORE_CODES)
        if codes & {"HIGH_TICKET", "LOW_TICKET"}:
            assert total == pytest.approx(row["priority_score"], abs=0.05), row["opportunity_id"]
        else:
            assert total + b["value_points"] == pytest.approx(row["priority_score"], abs=0.05)
        urg = next(r for r in row["reasons"] if r["code"] == "URGENCY_WINDOW")
        assert urg["weight"] == pytest.approx(40 * row["urgency"], abs=0.01)


# --- 11. reason contract --------------------------------------------------------------------------


def test_reason_codes_and_texts(scored: pd.DataFrame) -> None:
    valid = {c.value for c in ReasonCode}
    for reasons in scored["reasons"]:
        weights = [abs(r["weight"]) for r in reasons]
        assert weights == sorted(weights, reverse=True), "reasons must be ordered by |weight|"
        for r in reasons:
            assert r["code"] in valid
            assert r["direction"] in {"+", "-", "i"}
            assert re.search(r"\d", r["text_pt"]), r
            assert 1 <= len(r["text_pt"]) <= 400
            if r["direction"] == "i":
                assert r["weight"] == 0.0


def test_ticket_reasons(scored: pd.DataFrame) -> None:
    high = next(r for r in scored.loc["alive_known"]["reasons"] if r["code"] == "HIGH_TICKET")
    assert high["direction"] == "+" and high["weight"] > 0
    assert "R$ 4.821" in high["text_pt"]
    low = next(r for r in scored.loc["cheap"]["reasons"] if r["code"] == "LOW_TICKET")
    assert low["direction"] == "-" and 0 < low["weight"] < high["weight"]
    assert "R$ 55" in low["text_pt"]


def test_small_sample_and_overload_notes(scored: pd.DataFrame) -> None:
    assert scored.loc["small_agent"]["confidence"] == "baixa"
    over = scored.loc["overloaded"]
    assert ReasonCode.AGENT_OVERLOAD.value in over["codes"]
    text = next(r for r in over["reasons"] if r["code"] == "AGENT_OVERLOAD")["text_pt"]
    assert "90 deals abertos" in text
    assert ReasonCode.AGENT_OVERLOAD.value not in scored.loc["alive_known"]["codes"]


def test_weights_must_sum_to_100() -> None:
    with pytest.raises(ValueError):
        Weights(w_p=50.0, w_v=50.0, w_u=50.0)
    assert DEFAULT_WEIGHTS.points_per_p_win == pytest.approx(50.0)
