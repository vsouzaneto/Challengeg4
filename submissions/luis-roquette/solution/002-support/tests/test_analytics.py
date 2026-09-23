import json
import runpy
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import pytest

from support_copilot.analytics import (
    OperationalSummary,
    ScenarioAssumptions,
    _signal_status,
    add_operational_fields,
    grouped_bottlenecks,
    median_confidence_interval,
    operational_summary,
    recoverable_excess_hours,
    satisfaction_associations,
    scenario_projection,
)
from support_copilot.data import (
    CUSTOMER_COLUMNS,
    IT_TAXONOMY,
    load_customer_analytics,
)

ROOT = Path(__file__).parents[1]
reproduce = runpy.run_path(ROOT / "scripts" / "reproduce.py")["reproduce"]


def operational_frame(rows: list[dict] | None = None) -> pd.DataFrame:
    defaults = {
        "domain": "customer",
        "target": "Technical issue",
        "Ticket Status": "Closed",
        "Ticket Priority": "High",
        "Ticket Channel": "Email",
        "First Response Time": "2026-01-01T00:00:00Z",
        "Time to Resolution": "2026-01-01T01:00:00Z",
        "Customer Satisfaction Rating": None,
        "satisfaction_status": "missing",
    }
    source = rows or [{}]
    return pd.DataFrame([
        {**defaults, **row, "ticket_id": f"customer:{index + 1}"}
        for index, row in enumerate(source)
    ])


def summary() -> OperationalSummary:
    return OperationalSummary(
        1, "historical_observed", "development", "data-v1", 100, 80, 60, 48, 40,
        {"not_closed": 2, "missing": 2, "invalid_timestamp": 2, "negative": 2},
        1.0, 3.0, 1, "no_reliable_signal", 4, ("limitation",),
    )


def test_intervals_use_closed_valid_ordered_rows_and_reconcile_denominators() -> None:
    frame = operational_frame([
        {},
        {"Ticket Status": "Open", "First Response Time": "invalid",
         "Time to Resolution": "invalid"},
        {"First Response Time": None},
        {"First Response Time": "[INVALID_TIMESTAMP]"},
        {"First Response Time": "2026-01-02T00:00:00Z"},
    ])
    enriched = add_operational_fields(frame)
    assert enriched["interval_status"].tolist() == [
        "valid", "not_closed", "missing", "invalid_timestamp", "negative"
    ]
    assert enriched["post_response_hours"].tolist()[0] == 1
    assert enriched["post_response_hours"].isna().sum() == 4

    report = grouped_bottlenecks(enriched)
    assert set(report["grouping"]) == {
        "Ticket Channel", "Ticket Priority", "target",
        "Ticket Channel+Ticket Priority", "Ticket Channel+target",
        "Ticket Priority+target", "Ticket Channel+Ticket Priority+target",
    }
    for _, row in report.iterrows():
        assert row.n_total == row.n_eligible + row.n_excluded
        assert row.n_excluded == sum(row[f"excluded_{status}"] for status in (
            "not_closed", "missing", "invalid_timestamp", "negative"
        ))
        assert row.interval_name == "post_response_hours"
        assert not row.first_response_observable and not row.total_resolution_observable


def test_bottleneck_support_and_median_interval_are_explicit() -> None:
    values = pd.Series(range(1, 31), dtype=float)
    low, high = median_confidence_interval(values)
    assert low is not None and high is not None and low <= values.median() <= high
    assert median_confidence_interval(pd.Series([1.0, 2.0, 3.0, 4.0])) == (None, None)

    supported = grouped_bottlenecks(operational_frame([
        {"Time to Resolution": f"2026-01-01T{hour % 24:02d}:00:00Z"}
        for hour in range(30)
    ]))
    one_way = supported.loc[supported["grouping"].eq("Ticket Channel")].iloc[0]
    assert one_way["support_status"] == "supported"
    assert one_way["median_ci95_low"] <= one_way["median_hours"] <= one_way[
        "median_ci95_high"
    ]

    exploratory = grouped_bottlenecks(operational_frame([{}, {}, {}, {}, {}]))
    assert set(exploratory["support_status"]) == {"exploratory"}


@pytest.mark.parametrize("reverse", [False, True])
def test_intervals_accept_mixed_iso_timestamp_precision_in_any_order(reverse: bool) -> None:
    rows = [
        {"First Response Time": "2026-01-01T00:00:00Z",
         "Time to Resolution": "2026-01-01T00:00:01.123456Z"},
        {"First Response Time": "2026-01-01T00:00:00.500000Z",
         "Time to Resolution": "2026-01-01T00:00:02Z"},
    ]
    enriched = add_operational_fields(operational_frame(list(reversed(rows)) if reverse else rows))
    assert enriched["interval_status"].tolist() == ["valid", "valid"]
    assert sorted(enriched["post_response_hours"].tolist()) == pytest.approx(
        sorted([1.123456 / 3600, 1.5 / 3600])
    )


def test_waste_requires_30_valid_peers_and_never_has_negative_excess() -> None:
    rows = []
    for count, priority in ((29, "Low"), (30, "High")):
        rows.extend({
            "Ticket Priority": priority,
            "Time to Resolution": f"2026-01-02T{hour % 24:02d}:00:00Z",
        } for hour in range(count))
    report = recoverable_excess_hours(operational_frame(rows)).set_index("Ticket Priority")
    assert report.loc["Low", "status"] == "insufficient_support"
    assert pd.isna(report.loc["Low", "observed_excess_hours"])
    assert report.loc["High", "status"] == "supported"
    assert report.loc["High", "observed_excess_hours"] >= 0
    assert report.loc["High", "rank_excess"] == 1
    assert report.loc["High", "share_of_supported_excess"] == pytest.approx(1.0)
    assert not report.loc["High", "realized_savings"]


def test_satisfaction_scarcity_and_two_percent_cut_are_honest() -> None:
    sparse = operational_frame([
        {"Customer Satisfaction Rating": value, "satisfaction_status": "valid"}
        for value in (1, 2, 3, 4)
    ] + [{} for _ in range(30)])
    report = satisfaction_associations(sparse)
    assert report.status == "insufficient_support"
    assert report.valid_ratings == 4
    assert report.missing_ratings == 30
    assert report.permutation_importance is None
    assert "causalidade" in report.selection_limitation

    assert _signal_status(1.0, 0.9801)[0] == "no_reliable_signal"
    status, improvement = _signal_status(1.0, 0.98)
    assert status == "supported"
    assert improvement == pytest.approx(0.02)


@pytest.mark.parametrize("valid_intervals", [0, 1])
def test_satisfaction_handles_interval_absence_inside_folds(valid_intervals: int) -> None:
    rows = []
    for index in range(10):
        rows.append({
            "Ticket Status": "Closed" if index < valid_intervals else "Open",
            "Customer Satisfaction Rating": index % 5 + 1,
            "satisfaction_status": "valid",
            "Ticket Channel": "Email" if index % 2 else "Chat",
        })
    report = satisfaction_associations(operational_frame(rows))
    assert report.status in {"supported", "no_reliable_signal"}
    assert report.cv["folds"] == 5
    assert report.cv["interval_feature_used_folds"] == (0 if valid_intervals == 0 else 4)


@pytest.mark.parametrize(
    "changes,field",
    [
        ({"annual_eligible_volume": -1}, "annual_eligible_volume"),
        ({"addressable_share": 1.1}, "addressable_share"),
        ({"minutes_saved": float("nan")}, "minutes_saved"),
        ({"hourly_cost": float("inf")}, "hourly_cost"),
    ],
)
def test_scenarios_reject_invalid_values(changes: dict, field: str) -> None:
    values = {"annual_eligible_volume": 1200, "addressable_share": 0.25,
              "minutes_saved": 6.0, "hourly_cost": 30.0, "name": "base"}
    with pytest.raises(ValueError, match=field):
        ScenarioAssumptions(**(values | changes))


def test_scenario_changes_only_projection_not_historical_summary() -> None:
    historical = summary()
    before = asdict(historical)
    result = scenario_projection(
        historical, ScenarioAssumptions(1200, 0.25, 6.0, 30.0, "base")
    )
    assert result.annual_hours == 30
    assert result.annual_cost == 900
    assert result.evidence_kind == "projected"
    assert asdict(historical) == before


def test_raw_or_wrong_domain_frames_are_rejected() -> None:
    raw = operational_frame().assign(**{"Customer Name": "Private"})
    with pytest.raises(ValueError, match="sanitized"):
        add_operational_fields(raw)
    with pytest.raises(ValueError, match="domain"):
        add_operational_fields(operational_frame().assign(domain="it"))
    with pytest.raises(ValueError, match="sanitized"):
        add_operational_fields(operational_frame().assign(text="model input"))


def test_reproduce_keeps_structured_diagnostic_when_text_split_is_insufficient(
    tmp_path,
) -> None:
    customer = tmp_path / "customer.csv"
    row = dict.fromkeys(CUSTOMER_COLUMNS, "")
    row.update({
        "Ticket ID": "1", "Customer Name": "Example Person",
        "Customer Email": "example@example.invalid", "Customer Age": "31",
        "Customer Gender": "Other", "Ticket Type": "Technical issue",
        "Ticket Description": "device does not boot", "Ticket Status": "Closed",
        "Ticket Priority": "High", "Ticket Channel": "Email",
        "First Response Time": "2026-01-01T00:00:00Z",
        "Time to Resolution": "2026-01-01T01:00:00.123456Z",
        "Customer Satisfaction Rating": "4",
    })
    pd.DataFrame([row]).to_csv(customer, index=False)
    it = tmp_path / "it.csv"
    pd.DataFrame({
        "Document": [f"support request {index}" for index in range(len(IT_TAXONOMY))],
        "Topic_group": IT_TAXONOMY,
    }).to_csv(it, index=False)

    output = tmp_path / "artifacts"
    manifest = reproduce(customer, it, output)
    summary_payload = json.loads(
        (output / "analytics" / "operational-summary.json").read_text()
    )
    waste = pd.read_csv(output / "analytics" / "waste-opportunities.csv")
    bottlenecks = pd.read_csv(output / "analytics" / "bottlenecks.csv")

    assert manifest["splits"]["customer"]["status"] == "insufficient_support"
    assert summary_payload["status"] == "ready"
    assert summary_payload["reason"] is None
    assert summary_payload["analysis_scope"] == "customer_structured_operational_all_rows"
    assert summary_payload["analysis_rows"] == 1
    assert summary_payload["source_rows"] == summary_payload["sanitized_rows"] == 1
    assert summary_payload["representative_rows"] is None
    assert summary_payload["source_lane"] == "structured_operational"
    assert summary_payload["text_fields_retained"] is False
    assert summary_payload["median_post_response_hours"] == pytest.approx(
        1.0000342933333333
    )
    assert summary_payload["observed_excess_hours"] is None
    assert not waste.empty and set(waste["status"]) == {"insufficient_support"}
    assert not bottlenecks.empty and set(bottlenecks["n_eligible"]) == {1}
    analytics_source = manifest["sources"]["customer"]["analytics"]
    assert analytics_source["lane"] == "structured_operational"
    assert analytics_source["quality"]["text_fields_retained"] is False
    assert manifest["artifacts"]["data.customer.analytics"]["status"] == "ready"
    assert manifest["artifacts"]["analytics.operational_summary"]["dependencies"] == [
        "data.customer.analytics"
    ]


REAL_CUSTOMER_FIXTURE = ROOT / "data/raw/customer_support_tickets.csv"


@pytest.mark.skipif(
    not REAL_CUSTOMER_FIXTURE.is_file(), reason="optional public CSV not downloaded"
)
def test_real_customer_diagnostic_has_traceable_denominators_and_rankings() -> None:
    frame = load_customer_analytics(REAL_CUSTOMER_FIXTURE)
    operational = add_operational_fields(frame)
    operational.attrs = frame.attrs.copy()
    bottlenecks = grouped_bottlenecks(operational)
    waste = recoverable_excess_hours(operational)
    satisfaction = satisfaction_associations(operational)
    report = operational_summary(operational)

    assert report.analysis_rows == report.source_rows == report.sanitized_rows == 8469
    assert report.valid_intervals == 1404
    assert report.satisfaction_sample == 2769
    assert report.source_lane == "structured_operational"
    assert report.text_fields_retained is False and report.cost_observed is False
    assert report.observed_excess_hours == pytest.approx(4047.833333333333)
    assert report.supported_waste_groups == 20

    one_way = {
        grouping: bottlenecks.loc[bottlenecks["grouping"].eq(grouping)].iloc[0]
        for grouping in ("Ticket Channel", "Ticket Priority", "target")
    }
    assert one_way["Ticket Channel"]["Ticket Channel"] == "Chat"
    assert one_way["Ticket Channel"]["median_hours"] == pytest.approx(6.516666666666667)
    assert one_way["Ticket Priority"]["Ticket Priority"] == "High"
    assert one_way["Ticket Priority"]["median_hours"] == pytest.approx(7.116666666666666)
    assert one_way["target"]["target"] == "Product inquiry"
    assert one_way["target"]["median_hours"] == pytest.approx(6.983333333333333)

    worst = bottlenecks.loc[
        bottlenecks["grouping"].eq("Ticket Channel+Ticket Priority+target")
    ].iloc[0]
    assert (worst["Ticket Channel"], worst["Ticket Priority"], worst["target"]) == (
        "Chat", "Low", "Technical issue"
    )
    assert worst["n_eligible"] == 15
    assert worst["median_hours"] == pytest.approx(13.233333333333333)
    assert worst["support_status"] == "exploratory"

    top_waste = waste.loc[waste["status"].eq("supported")].iloc[0]
    assert (top_waste["target"], top_waste["Ticket Priority"]) == (
        "Refund request", "High"
    )
    assert top_waste["observed_excess_hours"] == pytest.approx(274.1666666666667)
    assert satisfaction.status == "no_reliable_signal"
    assert satisfaction.baseline_mae == pytest.approx(1.1867039645909088)
    assert satisfaction.ridge_mae == pytest.approx(1.2026170582002638)
    assert satisfaction.relative_mae_improvement == pytest.approx(-0.013409488873529385)
    assert satisfaction.permutation_importance is None
    interval_effect = next(
        effect for effect in satisfaction.univariate_effects
        if effect["feature"] == "post_response_hours"
    )
    assert interval_effect["association_metric"] == "spearman_rank_correlation"
    assert interval_effect["n"] == 1404
    assert interval_effect["association_value"] == pytest.approx(0.002637570495552492)
