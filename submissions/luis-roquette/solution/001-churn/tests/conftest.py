import pandas as pd
import pytest

from ravenstack_churn.config import RAW_TABLE_NAMES
from ravenstack_churn.contracts import SCHEMAS


@pytest.fixture
def mini_tables() -> dict[str, pd.DataFrame]:
    tables = {
        "accounts": pd.DataFrame(
            [
                [
                    "A-1",
                    "Acme",
                    "FinTech",
                    "BR",
                    "2023-01-01",
                    "organic",
                    "Enterprise",
                    20,
                    False,
                    False,
                ],
                ["A-2", "Beta", "EdTech", "US", "2024-05-20", "partner", "Basic", 5, False, True],
            ],
            columns=SCHEMAS["accounts"],
        ),
        "subscriptions": pd.DataFrame(
            [
                [
                    "S-1",
                    "A-1",
                    "2023-06-15",
                    "2024-06-15",
                    "Enterprise",
                    20,
                    1000,
                    12000,
                    False,
                    False,
                    False,
                    True,
                    "annual",
                    True,
                ],
                [
                    "S-2",
                    "A-1",
                    "2024-04-01",
                    None,
                    "Pro",
                    10,
                    200,
                    2400,
                    False,
                    False,
                    False,
                    False,
                    "monthly",
                    True,
                ],
                [
                    "S-3",
                    "A-2",
                    "2024-05-20",
                    None,
                    "Basic",
                    5,
                    300,
                    3600,
                    False,
                    False,
                    False,
                    False,
                    "monthly",
                    True,
                ],
            ],
            columns=SCHEMAS["subscriptions"],
        ),
        "feature_usage": pd.DataFrame(
            [
                ["U-before", "S-2", "2024-03-15", "feature_1", 2, 60, 0, False],
                ["U-duplicate", "S-1", "2024-05-15", "feature_1", 1, 120, 0, False],
                ["U-duplicate", "S-1", "2024-05-16", "feature_2", 3, 180, 1, False],
                ["U-future", "S-2", "2024-06-10", "feature_3", 2, 90, 0, True],
            ],
            columns=SCHEMAS["feature_usage"],
        ),
        "support_tickets": pd.DataFrame(
            [
                ["T-before", "A-2", "2024-05-10", "2024-05-11", 24.0, "high", 30, 2.0, False],
                ["T-recent", "A-1", "2024-05-20", "2024-05-21", 24.0, "medium", 20, 4.0, False],
                ["T-future", "A-1", "2024-06-10", "2024-06-11", 24.0, "low", 10, 5.0, False],
            ],
            columns=SCHEMAS["support_tickets"],
        ),
        "churn_events": pd.DataFrame(
            [
                [
                    "C-1",
                    "A-1",
                    "2024-06-15",
                    "product",
                    0.0,
                    False,
                    False,
                    False,
                    "missing feature",
                ],
                ["C-2", "A-1", "2024-07-01", "reactivation", 0.0, False, False, True, "returned"],
            ],
            columns=SCHEMAS["churn_events"],
        ),
    }
    assert set(tables) == set(RAW_TABLE_NAMES)
    return tables


@pytest.fixture
def observed_panel(mini_tables) -> pd.DataFrame:
    from ravenstack_churn.panel import build_account_panel

    return build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")


@pytest.fixture
def strict_panel(mini_tables) -> pd.DataFrame:
    from ravenstack_churn.panel import build_account_panel

    return build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")


@pytest.fixture
def candidate_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for index in range(80):
        churn = int(index % 4 == 0)
        rows.append(
            {
                "account_id": f"A-{index:03d}",
                "cutoff": pd.Timestamp("2024-11-30"),
                "churn_next_30d": churn,
                "first_terminal_churn_date": (pd.Timestamp("2024-12-15") if churn else pd.NaT),
                "usage_change_30_vs_90": -0.5 if churn else -0.1,
                "error_rate_30d": 0.2 if churn else 0.02,
                "escalations_90d": 2 if churn else 0,
                "mean_satisfaction_90d": 2.5 if churn else 4.5,
                "downgrade_90d": bool(churn),
                "auto_renew_off": bool(churn),
                "industry": "FinTech" if index % 2 else "EdTech",
                "country": "BR" if index % 3 else "US",
                "referral_source": "organic",
                "plan_tier": "Pro",
                "billing_frequency": "monthly",
                "is_trial": False,
                "mrr_active": 100 + index,
                "seats": 10,
                "tenure_days": 400,
                "chronology": "observed",
            }
        )
    observed = pd.DataFrame(rows)
    strict = observed.copy()
    strict["chronology"] = "strict"
    strict.loc[strict.churn_next_30d.eq(1), "usage_change_30_vs_90"] = 0.2
    scoring = strict.assign(
        cutoff=pd.Timestamp("2024-12-31"),
        churn_next_30d=pd.NA,
        first_terminal_churn_date=pd.NaT,
    )
    strict = pd.concat([strict, scoring], ignore_index=True)
    churn_events = pd.DataFrame(
        {
            "churn_event_id": [f"C-{index:03d}" for index in range(20)],
            "account_id": [f"A-{index * 4:03d}" for index in range(20)],
            "churn_date": pd.Timestamp("2024-12-15"),
            "reason_code": ["product"] * 20,
            "refund_amount_usd": 0.0,
            "preceding_upgrade_flag": False,
            "preceding_downgrade_flag": False,
            "is_reactivation": False,
            "feedback_text": "fixture",
        }
    )
    return observed, strict, churn_events


@pytest.fixture
def accepted_findings() -> pd.DataFrame:
    common = {
        "confidence": "accepted",
        "evidence_level": "association_controlled",
        "actionability": "immediate",
    }
    return pd.DataFrame(
        [
            {
                **common,
                "finding_id": "F-commercial-renewal",
                "mrr_exposed_max": 8_000,
                "affected_accounts": 100,
            },
            {
                **common,
                "finding_id": "F-support-escalation",
                "mrr_exposed_max": 10_000,
                "affected_accounts": 50,
            },
        ]
    )


@pytest.fixture
def claim_panel() -> pd.DataFrame:
    rows = []
    cutoffs = pd.date_range("2024-06-30", periods=6, freq="ME")
    for month, cutoff in enumerate(cutoffs):
        for index in range(10):
            churn = int(index < 2)
            daily_usage = 60 - month * 5 if churn else 30 + month * 8
            rows.append(
                {
                    "account_id": f"A-{month}-{index}",
                    "cutoff": cutoff,
                    "churn_next_30d": churn,
                    "usage_count_30d": daily_usage * 30,
                    "usage_coverage_30d": True,
                    "mean_satisfaction_90d": 3.0 if churn else 4.5,
                    "satisfaction_responses_90d": 1,
                    "tickets_90d": 1,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def model_panel() -> pd.DataFrame:
    from hashlib import sha256

    rows = []
    cutoffs = pd.to_datetime(["2024-08-31", "2024-09-30", "2024-10-31", "2024-11-30", "2024-12-31"])
    for account_number in range(30):
        account_id = f"M-{account_number:03d}"
        for month, cutoff in enumerate(cutoffs):
            is_scoring = cutoff == pd.Timestamp("2024-12-31")
            positive = (account_number + month) % 5 == 0
            churn = pd.NA if is_scoring else int(positive)
            rows.append(
                {
                    "account_id": account_id,
                    "cutoff": cutoff,
                    "chronology": "strict",
                    "churn_next_30d": churn,
                    "mrr_active": 100 + account_number * 10,
                    "seats": 5 + account_number % 10,
                    "tenure_days": 300 + month * 30,
                    "days_to_annual_renewal": 60 - month * 5,
                    "usage_count_30d": 80 if positive else 100,
                    "usage_change_30_vs_90": -0.4 if positive else 0.1,
                    "error_rate_30d": 0.2 if positive else 0.02,
                    "feature_breadth_30d": 5,
                    "tickets_30d": 3 if positive else 1,
                    "ticket_change_30_vs_90": 0.5 if positive else -0.1,
                    "escalations_90d": 2 if positive else 0,
                    "mean_satisfaction_90d": 3.0 if positive else 4.5,
                    "downgrade_90d": positive,
                    "auto_renew_off": positive,
                    "industry": "FinTech" if account_number % 2 else "EdTech",
                    "country": "BR" if account_number % 3 else "US",
                    "referral_source": "organic",
                    "plan_tier": "Pro",
                    "billing_frequency": "monthly",
                    "is_trial": False,
                }
            )
    panel = pd.DataFrame(rows)
    buckets = {
        account_id: int(sha256(f"42:{account_id}".encode()).hexdigest()[:8], 16) % 100
        for account_id in panel.account_id.unique()
    }
    assert any(bucket < 80 for bucket in buckets.values())
    assert any(bucket >= 80 for bucket in buckets.values())
    return panel


@pytest.fixture
def analysis_result(accepted_findings, claim_panel):
    from ravenstack_churn.diagnosis import build_claim_checks
    from ravenstack_churn.publish import AnalysisResult

    findings = accepted_findings.assign(
        driver_group=["commercial", "support"],
        immediate_action="Ação imediata revisada.",
        structural_action="Ação estrutural revisada.",
        owner=["Head de Receita", "Head de Suporte"],
        counterevidence="Limite do fixture.",
        limitation="Associação observacional.",
        failure_reason=pd.NA,
    )
    panel = pd.DataFrame(
        [
            {
                "account_id": "A-1",
                "cutoff": pd.Timestamp("2024-12-31"),
                "chronology": "strict",
                "has_active_subscription": True,
                "mrr_active": 1_000,
                "plan_tier": "Pro",
                "escalations_90d": 2,
                "auto_renew_off": True,
            },
            {
                "account_id": "A-2",
                "cutoff": pd.Timestamp("2024-12-31"),
                "chronology": "strict",
                "has_active_subscription": True,
                "mrr_active": 500,
                "plan_tier": "Basic",
                "escalations_90d": 0,
                "auto_renew_off": True,
            },
        ]
    )
    return AnalysisResult(
        quality_report={"rows": {"accounts": 2}},
        panel=panel,
        claim_checks=build_claim_checks(claim_panel),
        findings=findings,
        segment_metrics=pd.DataFrame(
            [
                {
                    "dimension": "industry",
                    "segment": "FinTech",
                    "churn_rate": 0.2,
                    "relative_risk": 1.2,
                    "mrr_lost": 500.0,
                    "confidence": "eligible",
                }
            ]
        ),
        monthly_churn=pd.DataFrame(
            [
                {
                    "evidence_id": "churn:reference",
                    "period_start": pd.Timestamp("2023-07-01"),
                    "period_end": pd.Timestamp("2023-12-31"),
                    "population": "registered_at_start",
                    "status": "available",
                    "source_refs": "accounts|churn_events",
                    "calculation": "fixture",
                    "period_kind": "comparison_period",
                    "dimension": "all",
                    "segment": "all",
                    "at_risk_accounts": 100,
                    "terminal_churns": 2,
                    "churn_rate": 0.02,
                    "rate_difference": pd.NA,
                    "difference_ci_low": pd.NA,
                    "difference_ci_high": pd.NA,
                    "ci_method": "cluster_bootstrap_account",
                    "ci_level": 0.95,
                    "mrr_lost": 200.0,
                    "rate_unit": "account_churn/account_month",
                },
                {
                    "evidence_id": "churn:recent",
                    "period_start": pd.Timestamp("2024-06-01"),
                    "period_end": pd.Timestamp("2024-11-30"),
                    "population": "registered_at_start",
                    "status": "available",
                    "source_refs": "accounts|churn_events",
                    "calculation": "fixture",
                    "period_kind": "comparison_period",
                    "dimension": "all",
                    "segment": "all",
                    "at_risk_accounts": 100,
                    "terminal_churns": 6,
                    "churn_rate": 0.06,
                    "rate_difference": 0.04,
                    "difference_ci_low": 0.01,
                    "difference_ci_high": 0.07,
                    "ci_method": "cluster_bootstrap_account",
                    "ci_level": 0.95,
                    "mrr_lost": 600.0,
                    "rate_unit": "account_churn/account_month",
                },
            ]
        ),
        reason_distribution=pd.DataFrame(
            [
                {
                    "evidence_id": "reason:diagnostic:product",
                    "period_start": pd.Timestamp("2024-12-01"),
                    "period_end": pd.Timestamp("2024-12-30"),
                    "population": "diagnostic_horizon",
                    "reason_code": "product",
                    "terminal_accounts": 10,
                    "eligible_events": 20,
                    "share": 0.5,
                    "unit": "share_of_first_valid_terminal_accounts",
                }
            ]
        ),
        event_cohort_metrics=pd.DataFrame(
            [
                {
                    "evidence_id": "event:strict:usage:cases",
                    "period_start": pd.Timestamp("2024-06-01"),
                    "period_end": pd.Timestamp("2024-11-30"),
                    "population": "terminal_event",
                    "chronology": "strict",
                    "metric": "F-product-usage-drop",
                    "cohort": "terminal_cases",
                    "relative_window_start": -30,
                    "relative_window_end": -1,
                    "value": 1.0,
                    "difference": -0.5,
                    "unit": "usage_events/account/day",
                }
            ]
        ),
        mechanism_scorecard=pd.DataFrame(
            [
                {
                    "evidence_id": f"mechanism:{finding_id}",
                    "period_start": pd.Timestamp("2024-11-30"),
                    "period_end": pd.Timestamp("2024-11-30"),
                    "population": "diagnostic_horizon",
                    "status": "available",
                    "limitation": "Associação observacional.",
                    "source_refs": "findings|event_cohort_metrics",
                    "calculation": "fixture",
                    "mechanism_id": finding_id,
                    "finding_id": finding_id,
                    "claim": f"{finding_id} antecede churn.",
                    "evidence_level": "supported_mechanism",
                    "temporal_support": "pass",
                    "comparison_support": "pass",
                    "sample_support": "pass",
                    "association_support": "pass",
                    "chronology_support": "pass",
                    "cross_table_support": "pass",
                    "effect": 2.0,
                    "effect_unit": "adjusted_odds_ratio",
                    "ci_low": 1.2,
                    "ci_high": 3.0,
                    "ci_level": 0.95,
                    "ci_method": "glm_hc3",
                    "counterevidence": "Limite do fixture.",
                }
                for finding_id in ("F-commercial-renewal", "F-support-escalation")
            ]
        ),
        model_evaluation={"publish_model": False, "failure_reasons": ["fixture"]},
        model_scores=None,
    )


@pytest.fixture
def generated_artifacts(tmp_path, analysis_result):
    from ravenstack_churn.publish import publish_artifacts

    publish_artifacts(analysis_result, tmp_path)
    return tmp_path
