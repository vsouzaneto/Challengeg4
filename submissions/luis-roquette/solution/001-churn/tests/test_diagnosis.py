import numpy as np
import pandas as pd

from ravenstack_churn import diagnosis
from ravenstack_churn.diagnosis import (
    EVIDENCE_LEVELS,
    GATE_STATES,
    _bootstrap_rate_contrast,
    _reason_corroborates,
    _segment_metrics,
    build_claim_checks,
    build_diagnostic_snapshot,
    build_event_cohort_metrics,
    build_mechanism_scorecard,
    build_monthly_churn,
    build_reason_distribution,
    evaluate_candidates,
    rank_findings,
)
from ravenstack_churn.panel import select_first_terminal_events


def _terminal_events(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    selected, _ = select_first_terminal_events(
        tables["accounts"], tables["churn_events"], pd.Timestamp("2024-12-31")
    )
    return selected


def test_satisfaction_two_level_weighting_is_3_35() -> None:
    rows = []
    anchors = (("2024-06-10", 1, 1.4), ("2024-07-10", 3, 4.0))
    for anchor, case_count, case_value in anchors:
        for cohort, count, value in (
            ("terminal_cases", case_count, case_value),
            ("contemporaneous_controls", 2, 3.0),
        ):
            for index in range(count):
                rows.append(
                    {
                        "account_id": f"{anchor}-{cohort}-{index}",
                        "anchor_date": pd.Timestamp(anchor),
                        "anchor_kind": "terminal_event",
                        "chronology": "strict",
                        "cohort": cohort,
                        "relative_window_start": -30,
                        "relative_window_end": -1,
                        "eligible_at_window_cutoff": True,
                        "reused_control": False,
                        "mean_satisfaction_30d": value,
                        "satisfaction_responses_30d": 1,
                        "tickets_30d": 1,
                        "support_coverage_30d": True,
                    }
                )

    metrics = build_event_cohort_metrics(pd.DataFrame(rows), replicates=200)
    satisfaction = metrics.loc[
        metrics["metric"].eq("F-support-satisfaction") & metrics["cohort"].eq("terminal_cases")
    ].iloc[0]

    assert satisfaction["value"] == 3.35
    assert satisfaction["weighting"] == "responses_within_anchor;eligible_cases_between_anchors"


def test_wide_interval_remains_plausible_and_inconclusive() -> None:
    findings = pd.DataFrame(
        [
            {
                "finding_id": "F-product-usage-drop",
                "claim": "Uso menor antecede churn.",
                "confidence": "inconclusive",
                "adjusted_odds_ratio": 1.1,
                "ci_low": 0.8,
                "ci_high": 1.4,
                "candidate_coverage": 1.0,
                "counterevidence": "Intervalo inclui 1.",
            }
        ]
    )

    scorecard = build_mechanism_scorecard(findings, pd.DataFrame(), pd.DataFrame())
    row = scorecard.iloc[0]

    assert row["evidence_level"] == "plausible_hypothesis"
    assert row["status"] == "inconclusive"
    assert pd.isna(row["rejected_statement"])


def test_all_gates_have_closed_states_before_ranking(candidate_frames) -> None:
    findings, _ = evaluate_candidates(*candidate_frames)
    gates = [
        "temporal_support",
        "comparison_support",
        "sample_support",
        "association_support",
        "chronology_support",
        "cross_table_support",
    ]

    assert set(findings[gates].stack()) <= GATE_STATES
    assert set(findings["evidence_level"]) <= EVIDENCE_LEVELS
    assert findings.loc[findings["confidence"].ne("accepted"), "priority_rank"].isna().all()


def test_holm_correction_restricts_six_candidate_tests(candidate_frames, monkeypatch) -> None:
    lower = {"usage_change_30_vs_90", "mean_satisfaction_90d"}

    def stable_fit(_snapshot, feature):
        coefficient = -1.0 if feature in lower else 1.0
        return {
            "coefficient": coefficient,
            "odds_ratio": 0.5 if coefficient < 0 else 2.0,
            "ci_low": 0.2 if coefficient < 0 else 1.2,
            "ci_high": 0.8 if coefficient < 0 else 3.0,
            "p_value": 0.01,
            "effective_n": 100,
            "coverage": 1.0,
            "failure_reason": None,
        }

    monkeypatch.setattr(diagnosis, "_fit_association", stable_fit)
    findings, _ = diagnosis.evaluate_candidates(*candidate_frames)

    assert np.allclose(findings["p_adjusted"], 0.06)
    assert findings["association_support"].eq("fail").all()


def test_monthly_churn_uses_registered_at_start_denominator(mini_tables) -> None:
    entrant = mini_tables["accounts"].iloc[[1]].copy()
    entrant["account_id"] = "A-3"
    entrant["account_name"] = "Gamma"
    entrant["signup_date"] = "2024-06-10"
    mini_tables["accounts"] = pd.concat([mini_tables["accounts"], entrant], ignore_index=True)
    entrant_churn = mini_tables["churn_events"].iloc[[0]].copy()
    entrant_churn["churn_event_id"] = "C-3"
    entrant_churn["account_id"] = "A-3"
    entrant_churn["churn_date"] = "2024-06-20"
    mini_tables["churn_events"] = pd.concat(
        [mini_tables["churn_events"], entrant_churn], ignore_index=True
    )

    history = build_monthly_churn(mini_tables, _terminal_events(mini_tables))
    june = history.loc[
        history["period_kind"].eq("month")
        & history["period_start"].eq(pd.Timestamp("2024-06-01"))
        & history["dimension"].eq("all")
    ].iloc[0]

    assert june["at_risk_accounts"] == 2
    assert june["terminal_churns"] == 1
    assert june["new_accounts"] == 1
    assert june["entrant_churns"] == 1
    assert june["churn_rate"] == 0.5


def test_monthly_churn_preserves_zero_denominator_month(mini_tables) -> None:
    mini_tables["accounts"]["signup_date"] = "2024-06-01"

    history = build_monthly_churn(mini_tables, _terminal_events(mini_tables))
    april = history.loc[
        history["period_kind"].eq("month")
        & history["period_start"].eq(pd.Timestamp("2023-04-01"))
        & history["dimension"].eq("all")
    ].iloc[0]

    assert april["at_risk_accounts"] == 0
    assert april["status"] == "unavailable"
    assert april["limitation"] == "zero_denominator"
    february = history.loc[
        history["period_kind"].eq("month")
        & history["period_start"].eq(pd.Timestamp("2024-02-01"))
        & history["dimension"].eq("all")
    ].iloc[0]
    assert february["period_end"] == pd.Timestamp("2024-02-29")


def test_monthly_churn_keeps_missing_subscription_history_unknown(mini_tables) -> None:
    mini_tables["subscriptions"] = mini_tables["subscriptions"].loc[
        ~mini_tables["subscriptions"]["account_id"].eq("A-2")
    ]
    mini_tables["subscriptions"].loc[
        mini_tables["subscriptions"]["subscription_id"].eq("S-1"), "mrr_amount"
    ] = np.nan

    history = build_monthly_churn(mini_tables, _terminal_events(mini_tables))
    june = history.loc[
        history["period_kind"].eq("month")
        & history["period_start"].eq(pd.Timestamp("2024-06-01"))
        & history["dimension"].eq("all")
    ].iloc[0]

    assert pd.isna(june["mrr_exposed"])
    assert pd.isna(june["mrr_lost"])
    assert june["mrr_unknown_accounts"] == 1
    assert june["status"] == "partial"
    assert "mrr_exposed_unknown_for_some_accounts" in june["limitation"]


def test_period_rate_is_weighted_by_account_month(mini_tables) -> None:
    history = build_monthly_churn(mini_tables, _terminal_events(mini_tables))
    recent = history.loc[
        history["period_kind"].eq("comparison_period")
        & history["dimension"].eq("all")
        & history["comparison_kind"].eq("previous_period")
    ].iloc[0]
    months = history.loc[
        history["period_kind"].eq("month")
        & history["period_start"].between("2024-06-01", "2024-11-01")
    ]

    assert (
        recent["churn_rate"] == months["terminal_churns"].sum() / months["at_risk_accounts"].sum()
    )
    assert recent["churn_rate"] != months["churn_rate"].mean()


def test_period_bootstrap_counts_duplicate_account_draws() -> None:
    account_months = pd.DataFrame(
        {
            "account_id": ["A", "A", "A", "B", "B", "B", "C", "C", "D"],
            "is_terminal_churn": [True, False, False, False, False, True, True, True, False],
        }
    )
    target = pd.Series([True, True, False, True, False, False, True, False, False])
    comparator = pd.Series([False, False, True, False, True, True, False, True, False])

    result = _bootstrap_rate_contrast(account_months, target, comparator, replicates=200, seed=42)
    weights = np.random.default_rng(42).multinomial(3, [1 / 3] * 3, size=200)
    target_rate = (weights @ np.array([1, 0, 1])) / (weights @ np.array([2, 1, 1]))
    comparator_rate = (weights @ np.array([0, 1, 1])) / (weights @ np.array([1, 2, 1]))
    expected = target_rate - comparator_rate

    assert result["difference_ci_low"] == np.quantile(expected, 0.025)
    assert result["difference_ci_high"] == np.quantile(expected, 0.975)


def test_segment_comparator_is_disjoint_complement(mini_tables) -> None:
    history = build_monthly_churn(mini_tables, _terminal_events(mini_tables))
    fintech = history.loc[
        history["period_kind"].eq("comparison_period")
        & history["period_start"].eq(pd.Timestamp("2024-06-01"))
        & history["dimension"].eq("industry")
        & history["segment"].eq("FinTech")
        & history["comparison_kind"].eq("segment_complement")
    ].iloc[0]

    assert fintech["comparator_rate"] == 0
    assert fintech["comparator_id"] == "complement:recent:industry:FinTech"
    assert fintech["status"] == "inconclusive"
    assert "insufficient_segment_or_complement_sample" in fintech["limitation"]


def test_reason_distribution_uses_first_valid_event_in_window(mini_tables) -> None:
    reasons = build_reason_distribution(mini_tables, _terminal_events(mini_tables))
    recent = reasons.loc[
        reasons["population"].eq("registered_at_start")
        & reasons["period_start"].eq(pd.Timestamp("2024-06-01"))
    ].set_index("reason_code")

    assert recent.loc["product", "terminal_accounts"] == 1
    assert recent.loc["product", "eligible_events"] == 1
    assert recent.loc["product", "share"] == 1
    assert recent.loc["unknown", "terminal_accounts"] == 0


def test_reason_distribution_excludes_accounts_registered_after_diagnostic_cutoff(
    mini_tables,
) -> None:
    entrant = mini_tables["accounts"].iloc[[1]].copy()
    entrant["account_id"] = "A-3"
    entrant["signup_date"] = "2024-12-01"
    mini_tables["accounts"] = pd.concat([mini_tables["accounts"], entrant], ignore_index=True)
    event = mini_tables["churn_events"].iloc[[0]].copy()
    event["churn_event_id"] = "C-3"
    event["account_id"] = "A-3"
    event["churn_date"] = "2024-12-15"
    mini_tables["churn_events"] = pd.concat([mini_tables["churn_events"], event], ignore_index=True)
    outside = event.copy()
    outside["churn_event_id"] = "C-4"
    outside["account_id"] = "A-2"
    outside["churn_date"] = "2024-12-31"
    mini_tables["churn_events"] = pd.concat(
        [mini_tables["churn_events"], outside], ignore_index=True
    )

    reasons = build_reason_distribution(mini_tables, _terminal_events(mini_tables))
    diagnostic = reasons.loc[reasons["population"].eq("diagnostic_horizon")]

    assert diagnostic["eligible_events"].eq(0).all()


def test_reason_corroboration_uses_only_first_terminal_event() -> None:
    first = pd.DataFrame(
        {
            "account_id": [f"A-{index}" for index in range(10)],
            "churn_date": pd.to_datetime(["2024-01-01"] * 10),
            "reason_code": ["other"] * 10,
            "is_reactivation": [False] * 10,
        }
    )
    later = pd.DataFrame(
        {
            "account_id": [f"A-{index}" for index in range(5)],
            "churn_date": pd.to_datetime(["2024-02-01"] * 5),
            "reason_code": ["product_issue"] * 5,
            "is_reactivation": [False] * 5,
        }
    )
    assert not _reason_corroborates(
        "product", {f"A-{index}" for index in range(5)}, pd.concat([first, later])
    )


def test_diagnostic_snapshot_uses_one_common_cutoff() -> None:
    panel = pd.DataFrame(
        [
            {
                "account_id": "A-churned",
                "cutoff": pd.Timestamp("2024-10-31"),
                "churn_next_30d": 1,
                "has_active_subscription": True,
            },
            {
                "account_id": "A-active",
                "cutoff": pd.Timestamp("2024-10-31"),
                "churn_next_30d": 0,
                "has_active_subscription": True,
            },
            {
                "account_id": "A-active",
                "cutoff": pd.Timestamp("2024-11-30"),
                "churn_next_30d": 0,
                "has_active_subscription": True,
            },
        ]
    )
    snapshot = build_diagnostic_snapshot(panel)
    assert snapshot.account_id.tolist() == ["A-active"]
    assert snapshot.cutoff.nunique() == 1
    assert snapshot.cutoff.iloc[0] == pd.Timestamp("2024-11-30")


def test_unstable_candidate_is_not_ranked(candidate_frames) -> None:
    findings, _ = evaluate_candidates(*candidate_frames)
    unstable = findings.loc[findings.finding_id.eq("F-product-usage-drop")].iloc[0]
    assert unstable["confidence"] == "inconclusive"
    assert pd.isna(unstable["priority_rank"])
    assert unstable["diagnostic_cutoff"] == pd.Timestamp("2024-11-30")
    assert unstable["horizon_days"] == 30
    assert unstable["exposure_rule"] == "usage_change_30_vs_90 le -0.3"
    assert unstable["diagnostic_exposed_accounts"] >= unstable["diagnostic_exposed_churns"]
    assert (
        unstable["counterevidence"] == "O modelo estatístico não produziu uma estimativa estável."
    )


def test_rank_uses_mrr_then_reach_then_actionability(accepted_findings) -> None:
    ranked = rank_findings(accepted_findings)
    assert ranked.finding_id.tolist() == [
        "F-support-escalation",
        "F-commercial-renewal",
    ]


def test_segment_metrics_include_relative_risk(candidate_frames) -> None:
    observed, strict, churn_events = candidate_frames
    _, segments = evaluate_candidates(observed, strict, churn_events)
    assert {"overall_churn_rate", "churn_rate_delta", "relative_risk"}.issubset(segments)


def test_segment_metrics_preserve_unknown_mrr_lost(candidate_frames) -> None:
    observed, _, _ = candidate_frames
    snapshot = observed.loc[observed["account_id"].isin(["A-000", "A-001"])].copy()
    snapshot["mrr_lost_next_30d"] = [pd.NA, 0]

    segments = _segment_metrics(snapshot)

    assert segments.loc[segments["churn_count"].eq(1), "mrr_lost"].isna().all()
    assert segments.loc[segments["churn_count"].eq(0), "mrr_lost"].eq(0).all()


def test_zero_variance_candidate_is_inconclusive(candidate_frames) -> None:
    observed, strict, churn_events = candidate_frames
    observed = observed.assign(error_rate_30d=0.0)
    strict = strict.assign(error_rate_30d=0.0)
    findings, _ = evaluate_candidates(observed, strict, churn_events)
    row = findings.loc[findings.finding_id.eq("F-product-errors")].iloc[0]
    assert row["confidence"] == "inconclusive"
    assert row["failure_reason"] == "zero_variance"


def test_claim_checks_expose_aggregate_contradictions(claim_panel) -> None:
    checks = build_claim_checks(claim_panel).set_index(["claim_id", "cohort"])
    assert checks.loc[("C-usage-growth", "overall"), "status"] == "up"
    assert checks.loc[("C-usage-growth", "churn_next_30d"), "status"] == "down"
    assert checks.loc[("C-satisfaction-ok", "overall"), "status"] == "ok"
    assert checks.loc[("C-satisfaction-ok", "churn_next_30d"), "status"] == "concern"


def test_usage_status_uses_endpoint_change_not_regression_slope(claim_panel) -> None:
    churn = claim_panel["churn_next_30d"].eq(1)
    monthly_daily_usage = dict(
        zip(sorted(claim_panel.cutoff.unique()), [10, 1, 1, 1, 100, 9], strict=True)
    )
    claim_panel.loc[churn, "usage_count_30d"] = (
        claim_panel.loc[churn, "cutoff"].map(monthly_daily_usage) * 30
    )
    row = (
        build_claim_checks(claim_panel)
        .set_index(["claim_id", "cohort"])
        .loc[("C-usage-growth", "churn_next_30d")]
    )
    assert row["slope"] > 0
    assert row["status"] == "down"
