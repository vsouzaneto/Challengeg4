from typing import Literal

import numpy as np
import pandas as pd

from .config import DEFAULT_WINDOWS, OBSERVATION_END, RECENT_PERIOD, SCORING_CUTOFF
from .contracts import _coerce_table, _coerce_tables


def select_first_terminal_events(
    accounts: pd.DataFrame,
    churn_events: pd.DataFrame,
    observation_end: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    parsed_accounts = _coerce_table("accounts", accounts)
    churn = _coerce_table("churn_events", churn_events)
    joined = churn.merge(
        parsed_accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    end = pd.Timestamp(observation_end)
    reasons = (
        ("unknown_account", joined["_merge"].ne("both")),
        ("missing_signup_date", joined["signup_date"].isna()),
        ("missing_churn_date", joined["churn_date"].isna()),
        (
            "before_signup",
            joined["signup_date"].notna()
            & joined["churn_date"].notna()
            & joined["churn_date"].lt(joined["signup_date"]),
        ),
        ("after_observation_end", joined["churn_date"].gt(end)),
        ("unknown_reactivation_flag", joined["is_reactivation"].isna()),
        ("reactivation", joined["is_reactivation"].eq(True).fillna(False)),
    )
    invalid = pd.Series(False, index=joined.index)
    exclusion_parts = []
    for reason, mask in reasons:
        invalid |= mask
        excluded = joined.loc[mask, ["churn_event_id", "account_id"]].copy()
        excluded["exclusion_reason"] = reason
        exclusion_parts.append(excluded)

    selected = (
        joined.loc[~invalid, list(churn.columns)]
        .sort_values(["account_id", "churn_date", "churn_event_id"])
        .drop_duplicates("account_id", keep="first")
        .reset_index(drop=True)
    )
    exclusions = pd.concat(exclusion_parts, ignore_index=True).sort_values(
        ["churn_event_id", "exclusion_reason"]
    )
    return selected, exclusions.reset_index(drop=True)


def first_terminal_churn(
    churn_events: pd.DataFrame,
    accounts: pd.DataFrame,
    observation_end: pd.Timestamp,
) -> pd.Series:
    selected, _ = select_first_terminal_events(accounts, churn_events, observation_end)
    if selected.empty:
        return pd.Series(dtype="datetime64[ns]", name="churn_date")
    return selected.set_index("account_id")["churn_date"].sort_index()


def mrr_lost_at_churn(subscriptions: pd.DataFrame, terminal_churn: pd.Series) -> pd.Series:
    parsed = _coerce_table("subscriptions", subscriptions)
    lost = {}
    for account_id, churn_date in terminal_churn.items():
        account_history = parsed.loc[parsed["account_id"].eq(account_id)]
        if account_history.empty:
            lost[account_id] = pd.NA
            continue
        day_before = pd.Timestamp(churn_date) - pd.Timedelta(days=1)
        active = account_history.loc[
            account_history["start_date"].le(day_before)
            & (account_history["end_date"].isna() | account_history["end_date"].gt(day_before))
        ]
        lost[account_id] = (
            pd.NA if active["mrr_amount"].isna().any() else int(active["mrr_amount"].sum())
        )
    return pd.Series(lost, name="mrr_lost", dtype="Int64")


def _single_or_mixed(values: pd.Series) -> object:
    unique = values.dropna().astype(str).unique()
    if len(unique) == 0:
        return pd.NA
    if len(unique) == 1:
        return unique[0]
    return "mixed"


def _next_anniversary(start: pd.Timestamp, cutoff: pd.Timestamp) -> pd.Timestamp:
    years = max(cutoff.year - start.year, 0)
    anniversary = start + pd.DateOffset(years=years)
    while anniversary <= cutoff:
        years += 1
        anniversary = start + pd.DateOffset(years=years)
    return anniversary


def _change(recent: float, recent_days: int, prior: float, prior_days: int) -> tuple[float, bool]:
    if prior <= 0:
        return np.nan, False
    return (recent / recent_days) / (prior / prior_days) - 1, True


def _events_between(
    events: pd.DataFrame, date_column: str, start: pd.Timestamp, end: pd.Timestamp
) -> pd.DataFrame:
    return events.loc[events[date_column].gt(start) & events[date_column].le(end)]


def _add_usage_window(
    row: dict[str, object],
    events: pd.DataFrame,
    subscriptions: pd.DataFrame,
    signup_date: pd.Timestamp,
    cutoff: pd.Timestamp,
    window: int,
) -> None:
    start = cutoff - pd.Timedelta(days=window)
    spans_window = subscriptions["start_date"].le(start) & (
        subscriptions["end_date"].isna() | subscriptions["end_date"].gt(cutoff)
    )
    covered = bool(signup_date <= start and spans_window.any())
    row[f"usage_coverage_{window}d"] = covered
    if not covered:
        for metric in (
            "usage_count",
            "usage_duration",
            "errors",
            "feature_breadth",
            "beta_share",
        ):
            row[f"{metric}_{window}d"] = np.nan
        return

    selected = _events_between(events, "usage_date", start, cutoff)
    row[f"usage_count_{window}d"] = int(selected["usage_count"].sum())
    row[f"usage_duration_{window}d"] = int(selected["usage_duration_secs"].sum())
    row[f"errors_{window}d"] = int(selected["error_count"].sum())
    row[f"feature_breadth_{window}d"] = int(selected["feature_name"].nunique())
    row[f"beta_share_{window}d"] = (
        float(selected["is_beta_feature"].mean()) if len(selected) else np.nan
    )


def _add_support_window(
    row: dict[str, object],
    events: pd.DataFrame,
    signup_date: pd.Timestamp,
    cutoff: pd.Timestamp,
    window: int,
) -> None:
    start = cutoff - pd.Timedelta(days=window)
    covered = bool(signup_date <= start)
    row[f"support_coverage_{window}d"] = covered
    if not covered:
        for metric in (
            "tickets",
            "escalations",
            "mean_first_response",
            "mean_resolution",
            "mean_satisfaction",
            "satisfaction_responses",
            "satisfaction_field_coverage",
        ):
            row[f"{metric}_{window}d"] = np.nan
        return

    selected = _events_between(events, "submitted_at", start, cutoff)
    ticket_count = len(selected)
    first_response_at = selected["submitted_at"] + pd.to_timedelta(
        selected["first_response_time_minutes"].astype("Float64"), unit="m"
    )
    responded = selected.loc[first_response_at.le(cutoff)]
    closed = selected.loc[selected["closed_at"].notna() & selected["closed_at"].le(cutoff)]
    satisfaction_count = int(closed["satisfaction_score"].notna().sum())
    row[f"tickets_{window}d"] = ticket_count
    row[f"escalations_{window}d"] = int(closed["escalation_flag"].fillna(False).sum())
    row[f"mean_first_response_{window}d"] = responded["first_response_time_minutes"].mean()
    row[f"mean_resolution_{window}d"] = closed["resolution_time_hours"].mean()
    row[f"mean_satisfaction_{window}d"] = closed["satisfaction_score"].mean()
    row[f"satisfaction_responses_{window}d"] = satisfaction_count
    row[f"satisfaction_field_coverage_{window}d"] = (
        satisfaction_count / ticket_count if ticket_count else np.nan
    )


def _add_trends(
    row: dict[str, object],
    usage: pd.DataFrame,
    tickets: pd.DataFrame,
    cutoff: pd.Timestamp,
) -> None:
    usage_7 = _events_between(usage, "usage_date", cutoff - pd.Timedelta(days=7), cutoff)[
        "usage_count"
    ].sum()
    usage_prior_23 = _events_between(
        usage,
        "usage_date",
        cutoff - pd.Timedelta(days=30),
        cutoff - pd.Timedelta(days=7),
    )["usage_count"].sum()
    usage_30 = row["usage_count_30d"]
    usage_90 = row["usage_count_90d"]
    if row["usage_coverage_30d"]:
        row["usage_change_7_vs_30"], row["usage_change_7_vs_30_available"] = _change(
            float(usage_7), 7, float(usage_prior_23), 23
        )
    else:
        row["usage_change_7_vs_30"] = np.nan
        row["usage_change_7_vs_30_available"] = False

    if row["usage_coverage_90d"] and pd.notna(usage_30) and pd.notna(usage_90):
        prior_60 = float(usage_90) - float(usage_30)
        row["usage_change_30_vs_90"], row["usage_change_30_vs_90_available"] = _change(
            float(usage_30), 30, prior_60, 60
        )
    else:
        row["usage_change_30_vs_90"] = np.nan
        row["usage_change_30_vs_90_available"] = False

    if row["usage_coverage_30d"] and pd.notna(usage_30) and float(usage_30) > 0:
        row["error_rate_30d"] = float(row["errors_30d"]) / float(usage_30)
        row["error_rate_30d_available"] = True
    else:
        row["error_rate_30d"] = np.nan
        row["error_rate_30d_available"] = False

    tickets_30 = row["tickets_30d"]
    tickets_90 = row["tickets_90d"]
    if row["support_coverage_90d"] and pd.notna(tickets_30) and pd.notna(tickets_90):
        prior_60 = float(tickets_90) - float(tickets_30)
        row["ticket_change_30_vs_90"], row["ticket_change_30_vs_90_available"] = _change(
            float(tickets_30), 30, prior_60, 60
        )
    else:
        row["ticket_change_30_vs_90"] = np.nan
        row["ticket_change_30_vs_90_available"] = False


def build_account_panel(
    tables: dict[str, pd.DataFrame],
    cutoffs: pd.DatetimeIndex,
    chronology: Literal["observed", "strict"],
) -> pd.DataFrame:
    if chronology not in {"observed", "strict"}:
        raise ValueError("chronology must be 'observed' or 'strict'")

    parsed = _coerce_tables(tables)
    accounts = parsed["accounts"].copy()
    subscriptions = parsed["subscriptions"].copy()
    usage = (
        parsed["feature_usage"]
        .merge(
            subscriptions[["subscription_id", "account_id", "start_date", "end_date"]],
            on="subscription_id",
            how="left",
            validate="many_to_one",
        )
        .merge(
            accounts[["account_id", "signup_date"]],
            on="account_id",
            how="left",
            validate="many_to_one",
        )
    )
    tickets = parsed["support_tickets"].merge(
        accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
    )
    if chronology == "strict":
        usage = usage.loc[
            usage["usage_date"].ge(usage["signup_date"])
            & usage["usage_date"].ge(usage["start_date"])
            & (usage["end_date"].isna() | usage["usage_date"].le(usage["end_date"]))
        ]
        tickets = tickets.loc[tickets["submitted_at"].ge(tickets["signup_date"])]

    terminal = first_terminal_churn(parsed["churn_events"], accounts, OBSERVATION_END)
    lost_at_churn = mrr_lost_at_churn(subscriptions, terminal)
    usage_by_account = {key: value for key, value in usage.groupby("account_id")}
    tickets_by_account = {key: value for key, value in tickets.groupby("account_id")}
    subscriptions_by_account = {key: value for key, value in subscriptions.groupby("account_id")}
    rows: list[dict[str, object]] = []

    for raw_cutoff in pd.DatetimeIndex(cutoffs):
        cutoff = pd.Timestamp(raw_cutoff)
        eligible = accounts.loc[accounts["signup_date"].le(cutoff)].copy()
        eligible_terminal = eligible["account_id"].map(terminal)
        eligible = eligible.loc[eligible_terminal.isna() | eligible_terminal.gt(cutoff)]

        for account in eligible.sort_values("account_id").itertuples(index=False):
            account_id = account.account_id
            account_subscriptions = subscriptions_by_account.get(
                account_id, subscriptions.iloc[0:0]
            )
            active = account_subscriptions.loc[
                account_subscriptions["start_date"].le(cutoff)
                & (
                    account_subscriptions["end_date"].isna()
                    | account_subscriptions["end_date"].gt(cutoff)
                )
            ]
            annual = active.loc[active["billing_frequency"].eq("annual")]
            renewals = [_next_anniversary(start, cutoff) for start in annual["start_date"].dropna()]
            next_renewal = min(renewals) if renewals else pd.NaT
            terminal_date = terminal.get(account_id, pd.NaT)
            usage_events = usage_by_account.get(account_id, usage.iloc[0:0])
            ticket_events = tickets_by_account.get(account_id, tickets.iloc[0:0])

            row: dict[str, object] = {
                "account_id": account_id,
                "cutoff": cutoff,
                "chronology": chronology,
                "account_name": account.account_name,
                "industry": account.industry,
                "country": account.country,
                "signup_date": account.signup_date,
                "referral_source": account.referral_source,
                "is_trial": account.is_trial,
                "account_churn_flag": account.churn_flag,
                "first_terminal_churn_date": terminal_date,
                "has_active_subscription": bool(len(active)),
                "mrr_active": int(active["mrr_amount"].sum()),
                "seats": int(active["seats"].sum()),
                "plan_tier": _single_or_mixed(active["plan_tier"]),
                "billing_frequency": _single_or_mixed(active["billing_frequency"]),
                "next_annual_renewal": next_renewal,
                "days_to_annual_renewal": (
                    int((next_renewal - cutoff).days) if pd.notna(next_renewal) else np.nan
                ),
                "tenure_days": int((cutoff - account.signup_date).days),
                "auto_renew_off": bool(
                    len(annual) and (~annual["auto_renew_flag"].fillna(False)).any()
                ),
            }

            for window in DEFAULT_WINDOWS:
                _add_usage_window(
                    row,
                    usage_events,
                    account_subscriptions,
                    account.signup_date,
                    cutoff,
                    window,
                )
                _add_support_window(row, ticket_events, account.signup_date, cutoff, window)

            recent_subscriptions = _events_between(
                account_subscriptions,
                "start_date",
                cutoff - pd.Timedelta(days=90),
                cutoff,
            )
            row["downgrade_90d"] = bool(recent_subscriptions["downgrade_flag"].fillna(False).any())
            row["upgrade_90d"] = bool(recent_subscriptions["upgrade_flag"].fillna(False).any())
            _add_trends(row, usage_events, ticket_events, cutoff)

            row["is_scoring_row"] = bool(cutoff == SCORING_CUTOFF)
            if row["is_scoring_row"]:
                row["churn_next_30d"] = pd.NA
                row["mrr_lost_next_30d"] = pd.NA
            else:
                row["churn_next_30d"] = int(
                    pd.notna(terminal_date)
                    and terminal_date > cutoff
                    and terminal_date <= cutoff + pd.Timedelta(days=30)
                )
                lost_mrr = lost_at_churn.get(account_id, pd.NA)
                row["mrr_lost_next_30d"] = (
                    pd.NA
                    if row["churn_next_30d"] and pd.isna(lost_mrr)
                    else int(lost_mrr)
                    if row["churn_next_30d"]
                    else 0
                )
            rows.append(row)

    panel = pd.DataFrame(rows).sort_values(["cutoff", "account_id"]).reset_index(drop=True)
    if panel.duplicated(["account_id", "cutoff", "chronology"]).any():
        raise ValueError("duplicate account/cutoff/chronology rows")
    return panel


def build_event_aligned_panel(
    tables: dict[str, pd.DataFrame],
    terminal_events: pd.DataFrame,
    chronology: Literal["observed", "strict"],
) -> pd.DataFrame:
    if chronology not in {"observed", "strict"}:
        raise ValueError("chronology must be 'observed' or 'strict'")

    parsed = _coerce_tables(tables)
    terminal = terminal_events.copy()
    if terminal.empty:
        terminal = terminal.reindex(columns=parsed["churn_events"].columns)
    selected, _ = select_first_terminal_events(
        parsed["accounts"], parsed["churn_events"], OBSERVATION_END
    )
    if set(terminal.get("churn_event_id", [])) != set(selected.get("churn_event_id", [])):
        raise ValueError("terminal_events must match shared terminal selection")

    historical_dates = sorted(
        terminal.loc[
            terminal["churn_date"].between(RECENT_PERIOD[0], RECENT_PERIOD[1]),
            "churn_date",
        ].unique()
    )
    diagnostic_start = SCORING_CUTOFF - pd.Timedelta(days=30)
    anchors = [
        {
            "anchor_date": pd.Timestamp(anchor_date),
            "anchor_kind": "terminal_event",
            "outcome_end": pd.Timestamp(anchor_date) + pd.Timedelta(days=29),
        }
        for anchor_date in historical_dates
    ]
    anchors.append(
        {
            "anchor_date": diagnostic_start,
            "anchor_kind": "diagnostic_horizon",
            "outcome_end": SCORING_CUTOFF - pd.Timedelta(days=1),
        }
    )
    windows = ((-90, -61), (-60, -31), (-30, -1))
    cutoffs = pd.DatetimeIndex(
        sorted(
            {
                anchor["anchor_date"] + pd.Timedelta(days=window_end)
                for anchor in anchors
                for _, window_end in windows
            }
        )
    )
    base = build_account_panel(parsed, cutoffs, chronology)
    base_index = base.set_index(["account_id", "cutoff"], drop=False)
    terminal_dates = terminal.set_index("account_id")["churn_date"]
    rows: list[dict[str, object]] = []

    for anchor in anchors:
        anchor_date = anchor["anchor_date"]
        outcome_end = anchor["outcome_end"]
        primary_cutoff = anchor_date - pd.Timedelta(days=1)
        primary = base.loc[base["cutoff"].eq(primary_cutoff) & base["has_active_subscription"]]
        if anchor["anchor_kind"] == "terminal_event":
            case_ids = set(terminal_dates.loc[terminal_dates.eq(anchor_date)].index)
        else:
            case_ids = set(
                terminal_dates.loc[terminal_dates.between(anchor_date, outcome_end)].index
            )
        case_ids &= set(primary["account_id"])
        outcome_complete = bool(outcome_end <= OBSERVATION_END)
        control_ids = (
            set(
                primary.loc[
                    primary["first_terminal_churn_date"].isna()
                    | primary["first_terminal_churn_date"].gt(outcome_end),
                    "account_id",
                ]
            )
            if outcome_complete
            else set()
        )

        for cohort, account_ids in (
            ("terminal_cases", case_ids),
            ("contemporaneous_controls", control_ids),
        ):
            for account_id in sorted(account_ids):
                terminal_date = terminal_dates.get(account_id, pd.NaT)
                for window_start, window_end in windows:
                    cutoff = anchor_date + pd.Timedelta(days=window_end)
                    key = (account_id, cutoff)
                    if key in base_index.index:
                        row = base_index.loc[key].to_dict()
                        eligible_at_window = True
                    else:
                        row = {column: pd.NA for column in base.columns}
                        row.update(
                            account_id=account_id,
                            cutoff=cutoff,
                            chronology=chronology,
                            first_terminal_churn_date=terminal_date,
                        )
                        eligible_at_window = False
                    row.update(
                        anchor_id=f"{anchor['anchor_kind']}:{anchor_date.date()}",
                        anchor_date=anchor_date,
                        anchor_kind=anchor["anchor_kind"],
                        cohort=cohort,
                        outcome_start=anchor_date,
                        outcome_end=outcome_end,
                        outcome_complete=outcome_complete,
                        relative_window_start=window_start,
                        relative_window_end=window_end,
                        eligible_at_window_cutoff=eligible_at_window,
                        includes_90d_context=eligible_at_window and window_start == -30,
                        churn_in_outcome_horizon=int(cohort == "terminal_cases"),
                    )
                    rows.append(row)

    annotation_columns = [
        "anchor_id",
        "anchor_date",
        "anchor_kind",
        "cohort",
        "outcome_start",
        "outcome_end",
        "outcome_complete",
        "relative_window_start",
        "relative_window_end",
        "eligible_at_window_cutoff",
        "includes_90d_context",
        "churn_in_outcome_horizon",
        "reused_control",
    ]
    if not rows:
        return pd.DataFrame(columns=[*base.columns, *annotation_columns])

    result = pd.DataFrame(rows)
    control_anchor_counts = (
        result.loc[result["cohort"].eq("contemporaneous_controls")]
        .drop_duplicates(["account_id", "anchor_date"])
        .groupby("account_id")["anchor_date"]
        .nunique()
    )
    result["reused_control"] = result["cohort"].eq("contemporaneous_controls") & result[
        "account_id"
    ].map(control_anchor_counts).gt(1).fillna(False)
    result = result.sort_values(
        ["anchor_date", "cohort", "account_id", "relative_window_start"]
    ).reset_index(drop=True)
    if result.duplicated(
        [
            "account_id",
            "anchor_date",
            "cohort",
            "relative_window_start",
            "relative_window_end",
            "chronology",
        ]
    ).any():
        raise ValueError("duplicate event-aligned panel rows")
    return result
