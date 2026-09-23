import pandas as pd

from ravenstack_churn.panel import (
    build_account_panel,
    build_event_aligned_panel,
    first_terminal_churn,
    mrr_lost_at_churn,
    select_first_terminal_events,
)


def _terminal_events(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    selected, _ = select_first_terminal_events(
        tables["accounts"], tables["churn_events"], pd.Timestamp("2024-12-31")
    )
    return selected


def test_event_aligned_features_stop_day_before_churn(mini_tables) -> None:
    same_day = mini_tables["feature_usage"].iloc[[1]].copy()
    same_day["usage_id"] = "U-churn-day"
    same_day["usage_date"] = "2024-06-15"
    same_day["usage_count"] = 1_000
    mini_tables["feature_usage"] = pd.concat(
        [mini_tables["feature_usage"], same_day], ignore_index=True
    )

    panel = build_event_aligned_panel(mini_tables, _terminal_events(mini_tables), "strict")
    anchor = panel.loc[panel["anchor_date"].eq(pd.Timestamp("2024-06-15"))]
    case = anchor.loc[
        anchor["cohort"].eq("terminal_cases") & anchor["relative_window_start"].eq(-30)
    ].iloc[0]
    late_control = anchor.loc[anchor["account_id"].eq("A-2")]

    assert case["usage_count_30d"] == 5
    assert late_control["relative_window_start"].tolist() == [-90, -60, -30]
    assert late_control["eligible_at_window_cutoff"].tolist() == [False, False, True]


def test_control_may_churn_after_outcome_horizon(mini_tables) -> None:
    later = mini_tables["churn_events"].iloc[[0]].copy()
    later["churn_event_id"] = "C-later"
    later["account_id"] = "A-2"
    later["churn_date"] = "2024-07-20"
    mini_tables["churn_events"] = pd.concat([mini_tables["churn_events"], later], ignore_index=True)

    panel = build_event_aligned_panel(mini_tables, _terminal_events(mini_tables), "observed")
    control = panel.loc[
        panel["anchor_date"].eq(pd.Timestamp("2024-06-15")) & panel["account_id"].eq("A-2")
    ]

    assert len(control) == 3
    assert control["cohort"].eq("contemporaneous_controls").all()
    assert control["first_terminal_churn_date"].eq(pd.Timestamp("2024-07-20")).all()


def test_strict_and_observed_event_panels_share_anchors_and_labels(mini_tables) -> None:
    terminal = _terminal_events(mini_tables)
    observed = build_event_aligned_panel(mini_tables, terminal, "observed")
    strict = build_event_aligned_panel(mini_tables, terminal, "strict")
    key = ["account_id", "anchor_date", "cohort", "relative_window_start"]

    assert observed[key].to_dict("records") == strict[key].to_dict("records")
    assert (
        observed["churn_in_outcome_horizon"].tolist() == strict["churn_in_outcome_horizon"].tolist()
    )
    assert strict.loc[strict["account_id"].eq("A-2"), "reused_control"].all()


def test_scoring_cutoff_keeps_incomplete_label_unknown(mini_tables) -> None:
    panel = build_account_panel(
        mini_tables, pd.DatetimeIndex([pd.Timestamp("2024-12-31")]), "strict"
    )

    assert panel["churn_next_30d"].isna().all()


def test_first_terminal_churn_ignores_reactivation(mini_tables) -> None:
    result = first_terminal_churn(
        mini_tables["churn_events"], mini_tables["accounts"], pd.Timestamp("2024-12-31")
    )
    assert result["A-1"] == pd.Timestamp("2024-06-15")


def test_first_terminal_churn_uses_valid_event_after_invalid_event(mini_tables) -> None:
    invalid = mini_tables["churn_events"].iloc[[0]].copy()
    invalid["churn_event_id"] = "C-invalid"
    invalid["churn_date"] = "2022-12-31"
    events = pd.concat([invalid, mini_tables["churn_events"]], ignore_index=True)

    selected, exclusions = select_first_terminal_events(
        mini_tables["accounts"], events, pd.Timestamp("2024-12-31")
    )
    terminal = first_terminal_churn(events, mini_tables["accounts"], pd.Timestamp("2024-12-31"))

    assert selected.set_index("account_id").loc["A-1", "churn_event_id"] == "C-1"
    assert terminal["A-1"] == pd.Timestamp("2024-06-15")
    assert exclusions.loc[
        exclusions.churn_event_id.eq("C-invalid"), "exclusion_reason"
    ].tolist() == ["before_signup"]


def test_missing_reactivation_flag_is_not_terminal(mini_tables) -> None:
    events = mini_tables["churn_events"].copy()
    events["is_reactivation"] = events["is_reactivation"].astype("boolean")
    events.loc[events.churn_event_id.eq("C-1"), "is_reactivation"] = pd.NA

    selected, exclusions = select_first_terminal_events(
        mini_tables["accounts"], events, pd.Timestamp("2024-12-31")
    )

    assert selected.empty
    assert "unknown_reactivation_flag" in set(exclusions["exclusion_reason"])


def test_terminal_selection_breaks_same_day_tie_by_event_id(mini_tables) -> None:
    earlier_id = mini_tables["churn_events"].iloc[[0]].copy()
    earlier_id["churn_event_id"] = "C-0"
    events = pd.concat([mini_tables["churn_events"], earlier_id], ignore_index=True)

    selected, _ = select_first_terminal_events(
        mini_tables["accounts"], events, pd.Timestamp("2024-12-31")
    )

    assert selected.set_index("account_id").loc["A-1", "churn_event_id"] == "C-0"


def test_terminal_selection_excludes_missing_and_future_dates(mini_tables) -> None:
    missing = mini_tables["churn_events"].iloc[[0]].copy()
    missing["churn_event_id"] = "C-missing"
    missing["churn_date"] = None
    future = mini_tables["churn_events"].iloc[[0]].copy()
    future["churn_event_id"] = "C-future"
    future["churn_date"] = "2025-01-01"
    events = pd.concat([mini_tables["churn_events"], missing, future], ignore_index=True)

    selected, exclusions = select_first_terminal_events(
        mini_tables["accounts"], events, pd.Timestamp("2024-12-31")
    )
    reasons = exclusions.set_index("churn_event_id")["exclusion_reason"]

    assert selected.set_index("account_id").loc["A-1", "churn_event_id"] == "C-1"
    assert reasons["C-missing"] == "missing_churn_date"
    assert reasons["C-future"] == "after_observation_end"


def test_panel_excludes_events_after_cutoff(mini_tables) -> None:
    panel = build_account_panel(
        mini_tables, pd.DatetimeIndex(["2024-05-31"]), chronology="observed"
    )
    row = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert row["tickets_30d"] == 1
    assert row["usage_count_30d"] == 4
    assert row["churn_next_30d"] == 1


def test_support_outcomes_remain_hidden_until_they_occur(mini_tables) -> None:
    ticket = mini_tables["support_tickets"]["ticket_id"].eq("T-recent")
    mini_tables["support_tickets"].loc[ticket, "closed_at"] = "2024-06-02"
    mini_tables["support_tickets"].loc[ticket, "first_response_time_minutes"] = 20_000
    mini_tables["support_tickets"].loc[ticket, "escalation_flag"] = True
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    row = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert row["tickets_30d"] == 1
    assert row["escalations_30d"] == 0
    assert pd.isna(row["mean_first_response_30d"])
    assert pd.isna(row["mean_resolution_30d"])
    assert pd.isna(row["mean_satisfaction_30d"])
    assert row["satisfaction_responses_30d"] == 0


def test_strict_panel_excludes_pre_lifecycle_events(mini_tables) -> None:
    observed = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")
    strict = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    observed_a1 = observed.loc[observed.account_id.eq("A-1")].iloc[0]
    strict_a1 = strict.loc[strict.account_id.eq("A-1")].iloc[0]
    strict_a2 = strict.loc[strict.account_id.eq("A-2")].iloc[0]
    assert strict_a1["usage_count_90d"] < observed_a1["usage_count_90d"]
    assert pd.isna(strict_a2["tickets_90d"])
    assert not bool(strict_a2["support_coverage_90d"])


def test_strict_panel_excludes_usage_after_subscription_end(mini_tables) -> None:
    mini_tables["subscriptions"].loc[
        mini_tables["subscriptions"].subscription_id.eq("S-1"), "end_date"
    ] = "2024-05-01"
    observed = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")
    strict = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    observed_a1 = observed.loc[observed.account_id.eq("A-1")].iloc[0]
    strict_a1 = strict.loc[strict.account_id.eq("A-1")].iloc[0]
    assert observed_a1["usage_count_30d"] == 4
    assert strict_a1["usage_count_30d"] == 0


def test_annual_renewal_uses_next_start_anniversary(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    annual = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert annual["next_annual_renewal"] == pd.Timestamp("2024-06-15")
    assert annual["days_to_annual_renewal"] == 15


def test_mrr_lost_is_active_revenue_immediately_before_churn(mini_tables) -> None:
    terminal = first_terminal_churn(
        mini_tables["churn_events"], mini_tables["accounts"], pd.Timestamp("2024-12-31")
    )
    lost = mrr_lost_at_churn(mini_tables["subscriptions"], terminal)
    assert lost["A-1"] == 1200
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    assert panel.loc[panel.account_id.eq("A-1"), "mrr_lost_next_30d"].iloc[0] == 1200


def test_mrr_unknown_is_not_zero() -> None:
    terminal = pd.Series(
        {"A-known": pd.Timestamp("2024-06-15"), "A-unknown": pd.Timestamp("2024-06-15")}
    )
    subscriptions = pd.DataFrame(
        [
            [
                "S-known",
                "A-known",
                "2024-01-01",
                "2024-05-01",
                "Pro",
                1,
                100,
                1200,
                False,
                False,
                False,
                True,
                "monthly",
                False,
            ]
        ],
        columns=(
            "subscription_id",
            "account_id",
            "start_date",
            "end_date",
            "plan_tier",
            "seats",
            "mrr_amount",
            "arr_amount",
            "is_trial",
            "upgrade_flag",
            "downgrade_flag",
            "churn_flag",
            "billing_frequency",
            "auto_renew_flag",
        ),
    )

    lost = mrr_lost_at_churn(subscriptions, terminal)

    assert lost["A-known"] == 0
    assert pd.isna(lost["A-unknown"])


def test_concurrent_subscriptions_preserve_revenue_and_mixed_dimensions(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    account = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert account["mrr_active"] == 1200
    assert account["plan_tier"] == "mixed"
    assert account["billing_frequency"] == "mixed"


def test_incomplete_observation_window_is_null_not_zero(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    recent = panel.loc[panel.account_id.eq("A-2")].iloc[0]
    assert pd.isna(recent["usage_count_30d"])
    assert not bool(recent["usage_coverage_30d"])


def test_panel_key_is_unique(observed_panel, strict_panel) -> None:
    panel = pd.concat([observed_panel, strict_panel], ignore_index=True)
    assert not panel.duplicated(["account_id", "cutoff", "chronology"]).any()
