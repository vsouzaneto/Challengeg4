from __future__ import annotations

import json
import warnings
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint
from statsmodels.tools.sm_exceptions import (
    PerfectSeparationError,
    PerfectSeparationWarning,
    SingularMatrixWarning,
)

from .config import (
    BOOTSTRAP_REPLICATES,
    HISTORICAL_START,
    MIN_COVERAGE,
    MIN_SEGMENT_ACCOUNTS,
    MIN_SEGMENT_CHURNS,
    OBSERVATION_END,
    RANDOM_SEED,
    RECENT_PERIOD,
    REFERENCE_PERIOD,
    SCORING_CUTOFF,
)
from .contracts import _coerce_tables
from .panel import mrr_lost_at_churn, select_first_terminal_events

HISTORICAL_DIMENSIONS = (
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
    "is_trial",
    "mrr_band",
)

MONTHLY_CHURN_COLUMNS = (
    "evidence_id",
    "period_start",
    "period_end",
    "population",
    "chronology",
    "status",
    "limitation",
    "source_refs",
    "calculation",
    "period_kind",
    "dimension",
    "segment",
    "comparison_kind",
    "at_risk_accounts",
    "unique_accounts",
    "terminal_churns",
    "new_accounts",
    "entrant_churns",
    "excluded_events",
    "observation_complete",
    "churn_rate",
    "rate_unit",
    "ci_low",
    "ci_high",
    "ci_level",
    "ci_method",
    "comparator_id",
    "comparator_rate",
    "relative_risk",
    "rr_ci_low",
    "rr_ci_high",
    "rate_difference",
    "difference_ci_low",
    "difference_ci_high",
    "mrr_lost",
    "mrr_known_accounts",
    "mrr_unknown_accounts",
    "mrr_exposed",
    "mrr_exposed_as_of",
    "currency",
    "financial_unit",
)

REASON_DISTRIBUTION_COLUMNS = (
    "evidence_id",
    "period_start",
    "period_end",
    "population",
    "chronology",
    "status",
    "limitation",
    "source_refs",
    "calculation",
    "reason_code",
    "terminal_accounts",
    "eligible_events",
    "excluded_events",
    "share",
    "unit",
    "ci_low",
    "ci_high",
    "ci_method",
    "ci_level",
    "comparator_id",
    "mrr_lost",
    "mrr_known_accounts",
    "mrr_unknown_accounts",
    "currency",
)

EVIDENCE_LEVELS = frozenset(
    {"confirmed_fact", "supported_mechanism", "plausible_hypothesis", "rejected_claim"}
)
GATE_STATES = frozenset({"pass", "fail", "unavailable"})

EVENT_METRIC_DEFINITIONS = {
    "F-product-usage-drop": (
        "usage_count_30d",
        "usage_coverage_30d",
        "usage_events/account/day",
        1 / 30,
        None,
        False,
    ),
    "F-product-errors": (
        "error_rate_30d",
        "error_rate_30d_available",
        "errors/usage_event",
        1.0,
        None,
        False,
    ),
    "F-support-escalation": (
        "escalations_30d",
        "support_coverage_30d",
        "escalations/account/30d",
        1.0,
        None,
        False,
    ),
    "F-support-satisfaction": (
        "mean_satisfaction_30d",
        "support_coverage_30d",
        "satisfaction_points/response",
        1.0,
        "satisfaction_responses_30d",
        False,
    ),
    "F-commercial-downgrade": (
        "downgrade_90d",
        "includes_90d_context",
        "share_of_accounts",
        1.0,
        None,
        True,
    ),
    "F-commercial-renewal": (
        "auto_renew_off",
        "includes_90d_context",
        "share_of_accounts",
        1.0,
        None,
        True,
    ),
}

CANDIDATES = {
    "F-product-usage-drop": ("usage_change_30_vs_90", "lower", "product", "le", -0.30),
    "F-product-errors": ("error_rate_30d", "higher", "product", "ge", 0.10),
    "F-support-escalation": ("escalations_90d", "higher", "support", "ge", 1),
    "F-support-satisfaction": (
        "mean_satisfaction_90d",
        "lower",
        "support",
        "le",
        3.0,
    ),
    "F-commercial-downgrade": (
        "downgrade_90d",
        "higher",
        "commercial",
        "eq",
        True,
    ),
    "F-commercial-renewal": (
        "auto_renew_off",
        "higher",
        "commercial",
        "eq",
        True,
    ),
}

ACTIONS = {
    "product": {
        "immediate_action": "CS revisa em 7 dias as contas expostas e confirma o fluxo que perdeu uso.",
        "structural_action": "Produto e Engenharia corrigem em 30–90 dias o fluxo corroborado e medem a coorte.",
        "owner": "Head de Produto",
        "success_metric": "MRR perdido e uso de 30 dias da coorte exposta",
    },
    "support": {
        "immediate_action": "Suporte revisa em 7 dias escaladas abertas das contas expostas e define responsável.",
        "structural_action": "Support Ops ajusta em 30–90 dias triagem e SLA da causa corroborada.",
        "owner": "Head de Suporte",
        "success_metric": "MRR perdido, taxa de escalada e satisfação da coorte exposta",
    },
    "commercial": {
        "immediate_action": "CS revisa em 7 dias renovações próximas e mudanças contratuais das contas expostas.",
        "structural_action": "RevOps testa em 30–90 dias o playbook comercial na coorte exposta.",
        "owner": "Head de Receita",
        "success_metric": "MRR perdido e renovação da coorte exposta",
    },
}

CONTROL_COLUMNS = (
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
    "is_trial",
    "mrr_active",
    "seats",
    "tenure_days",
)


def _wilson(count: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return np.nan, np.nan
    low, high = proportion_confint(count, total, alpha=0.05, method="wilson")
    return float(low), float(high)


def _bootstrap_rate_contrast(
    account_months: pd.DataFrame,
    target: pd.Series,
    comparator: pd.Series | None,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = RANDOM_SEED,
) -> dict[str, object]:
    work = account_months.assign(
        _target=target,
        _comparator=False if comparator is None else comparator,
    )
    work = work.loc[work["_target"] | work["_comparator"]]
    accounts = pd.Index(work["account_id"].astype(str).unique())
    if len(accounts) < 2:
        return {"status": "unavailable", "limitation": "fewer_than_two_accounts"}

    grouped = work.groupby("account_id", sort=True)
    vectors = pd.DataFrame(
        {
            "target_den": grouped["_target"].sum(),
            "target_num": grouped.apply(
                lambda group: int((group["_target"] & group["is_terminal_churn"]).sum()),
                include_groups=False,
            ),
            "comparator_den": grouped["_comparator"].sum(),
            "comparator_num": grouped.apply(
                lambda group: int((group["_comparator"] & group["is_terminal_churn"]).sum()),
                include_groups=False,
            ),
        }
    ).reindex(accounts, fill_value=0)
    weights = np.random.default_rng(seed).multinomial(
        len(accounts), np.full(len(accounts), 1 / len(accounts)), size=replicates
    )
    target_den = weights @ vectors["target_den"].to_numpy()
    comparator_den = weights @ vectors["comparator_den"].to_numpy()
    target_rate = np.divide(
        weights @ vectors["target_num"].to_numpy(),
        target_den,
        out=np.full(replicates, np.nan),
        where=target_den > 0,
    )
    valid_target = target_rate[np.isfinite(target_rate)]
    if len(valid_target) < 0.95 * replicates:
        return {"status": "unavailable", "limitation": "insufficient_valid_bootstrap_replicates"}

    result: dict[str, object] = {
        "status": "available",
        "limitation": "",
        "target_ci_low": float(np.quantile(valid_target, 0.025)),
        "target_ci_high": float(np.quantile(valid_target, 0.975)),
    }
    if comparator is None:
        return result

    comparator_rate = np.divide(
        weights @ vectors["comparator_num"].to_numpy(),
        comparator_den,
        out=np.full(replicates, np.nan),
        where=comparator_den > 0,
    )
    difference = target_rate - comparator_rate
    ratio = np.divide(
        target_rate,
        comparator_rate,
        out=np.full(replicates, np.nan),
        where=comparator_rate > 0,
    )
    valid_difference = difference[np.isfinite(difference)]
    valid_ratio = ratio[np.isfinite(ratio)]
    if len(valid_difference) < 0.95 * replicates:
        return {"status": "unavailable", "limitation": "insufficient_valid_bootstrap_replicates"}

    result.update(
        difference_ci_low=float(np.quantile(valid_difference, 0.025)),
        difference_ci_high=float(np.quantile(valid_difference, 0.975)),
    )
    if len(valid_ratio) >= 0.95 * replicates:
        result.update(
            rr_ci_low=float(np.quantile(valid_ratio, 0.025)),
            rr_ci_high=float(np.quantile(valid_ratio, 0.975)),
        )
    else:
        result.update(rr_ci_low=np.nan, rr_ci_high=np.nan)
        result["limitation"] = "relative_risk_bootstrap_unavailable"
    return result


def _active_subscription_attributes(
    subscriptions: pd.DataFrame, account_ids: pd.Index, as_of: pd.Timestamp
) -> pd.DataFrame:
    active = subscriptions.loc[
        subscriptions["account_id"].isin(account_ids)
        & subscriptions["start_date"].le(as_of)
        & (subscriptions["end_date"].isna() | subscriptions["end_date"].gt(as_of))
    ].drop_duplicates("subscription_id")
    rows = []
    for account_id in account_ids:
        history = subscriptions.loc[subscriptions["account_id"].eq(account_id)]
        group = active.loc[active["account_id"].eq(account_id)]

        def one_or_mixed(column: str, active_group: pd.DataFrame = group) -> object:
            values = active_group[column].dropna().unique()
            if not len(values):
                return "unknown"
            return values[0] if len(values) == 1 else "mixed"

        mrr = group["mrr_amount"]
        mrr_active = np.nan if history.empty or mrr.isna().any() else float(mrr.sum())
        rows.append(
            {
                "account_id": account_id,
                "plan_tier": one_or_mixed("plan_tier"),
                "billing_frequency": one_or_mixed("billing_frequency"),
                "is_trial": one_or_mixed("is_trial"),
                "mrr_active": mrr_active,
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(
            columns=[
                "account_id",
                "plan_tier",
                "billing_frequency",
                "is_trial",
                "mrr_active",
                "mrr_band",
            ]
        )
    result["mrr_band"] = (
        pd.cut(
            result["mrr_active"],
            bins=[-np.inf, 500, 2_000, np.inf],
            labels=["low", "mid", "high"],
        )
        .astype("string")
        .fillna("unknown")
    )
    return result


def _historical_account_months(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    accounts = tables["accounts"]
    subscriptions = tables["subscriptions"]
    terminal = terminal_events.set_index("account_id")
    months = pd.date_range(HISTORICAL_START, RECENT_PERIOD[1], freq="MS")
    rows = []
    for month_start in months:
        month_end = month_start + pd.offsets.MonthBegin(1)
        churn_date = accounts["account_id"].map(terminal["churn_date"])
        eligible = accounts["signup_date"].le(month_start) & (
            churn_date.isna() | churn_date.ge(month_start)
        )
        at_risk = accounts.loc[eligible].drop(columns=["plan_tier", "is_trial"]).copy()
        attributes = _active_subscription_attributes(
            subscriptions, pd.Index(at_risk["account_id"]), month_start
        )
        at_risk = at_risk.merge(attributes, on="account_id", how="left", validate="one_to_one")
        at_risk[["plan_tier", "billing_frequency", "is_trial", "mrr_band"]] = at_risk[
            ["plan_tier", "billing_frequency", "is_trial", "mrr_band"]
        ].fillna("unknown")
        at_risk["period_start"] = month_start
        at_risk["period_end"] = month_end - pd.Timedelta(days=1)
        at_risk["terminal_date"] = at_risk["account_id"].map(terminal["churn_date"])
        at_risk["is_terminal_churn"] = at_risk["terminal_date"].ge(month_start) & at_risk[
            "terminal_date"
        ].lt(month_end)
        rows.append(at_risk)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _financial_loss(lost: pd.Series, account_ids: pd.Series) -> tuple[float, int, int]:
    if account_ids.empty:
        return 0.0, 0, 0
    values = account_ids.map(lost)
    known = int(values.notna().sum())
    unknown = int(values.isna().sum())
    return (float(values.dropna().sum()) if known else np.nan, known, unknown)


def build_monthly_churn(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    parsed = _coerce_tables(tables)
    terminal = terminal_events.copy()
    if terminal.empty:
        terminal = terminal.reindex(columns=parsed["churn_events"].columns)
    selected, exclusions = select_first_terminal_events(
        parsed["accounts"], parsed["churn_events"], OBSERVATION_END
    )
    if set(terminal.get("churn_event_id", [])) != set(selected.get("churn_event_id", [])):
        raise ValueError("terminal_events must match shared terminal selection")
    account_months = _historical_account_months(parsed, terminal)
    terminal_series = terminal.set_index("account_id")["churn_date"]
    lost = mrr_lost_at_churn(parsed["subscriptions"], terminal_series)
    raw_exclusions = exclusions.merge(
        parsed["churn_events"][["churn_event_id", "churn_date"]],
        on="churn_event_id",
        how="left",
    )
    rows: list[dict[str, object]] = []

    def add_row(
        data: pd.DataFrame,
        period_start: pd.Timestamp,
        period_end: pd.Timestamp,
        period_kind: str,
        dimension: str,
        segment: str,
        comparison_kind: str = "none",
        comparator: pd.DataFrame | None = None,
        comparator_id: str | None = None,
    ) -> None:
        churned = data.loc[data["is_terminal_churn"]]
        count = len(churned)
        denominator = len(data)
        rate = count / denominator if denominator else np.nan
        ci_low, ci_high = _wilson(count, denominator)
        mrr_lost, known, unknown = _financial_loss(lost, churned["account_id"])
        is_month = period_kind == "month"
        new_mask = parsed["accounts"]["signup_date"].gt(period_start) & parsed["accounts"][
            "signup_date"
        ].le(period_end)
        new_accounts = int(new_mask.sum()) if dimension == "all" else 0
        entrant_ids = set(parsed["accounts"].loc[new_mask, "account_id"])
        entrant_churns = (
            int(
                (
                    terminal["account_id"].isin(entrant_ids)
                    & terminal["churn_date"].ge(period_start)
                    & terminal["churn_date"].le(period_end)
                ).sum()
            )
            if dimension == "all"
            else 0
        )
        excluded_events = (
            int(
                raw_exclusions.loc[
                    raw_exclusions["churn_date"].ge(period_start)
                    & raw_exclusions["churn_date"].le(period_end),
                    "churn_event_id",
                ].nunique()
            )
            if dimension == "all"
            else 0
        )
        status = "available" if denominator else "unavailable"
        limitation = "" if denominator else "zero_denominator"
        comparator_rate = relative_risk = rate_difference = np.nan
        rr_low = rr_high = diff_low = diff_high = np.nan
        target_mask = account_months.index.isin(data.index)
        if not is_month and denominator:
            period_bootstrap = _bootstrap_rate_contrast(account_months, target_mask, None)
            ci_low = period_bootstrap.get("target_ci_low", np.nan)
            ci_high = period_bootstrap.get("target_ci_high", np.nan)
            if period_bootstrap["status"] != "available":
                status = "inconclusive"
                limitation = str(period_bootstrap["limitation"])
        if comparator is not None and denominator:
            comparator_rate = (
                float(comparator["is_terminal_churn"].mean()) if len(comparator) else np.nan
            )
            relative_risk = (
                float(rate / comparator_rate)
                if pd.notna(rate) and pd.notna(comparator_rate) and comparator_rate > 0
                else np.nan
            )
            rate_difference = (
                float(rate - comparator_rate)
                if pd.notna(rate) and pd.notna(comparator_rate)
                else np.nan
            )
            contrast = _bootstrap_rate_contrast(
                account_months,
                target_mask,
                account_months.index.isin(comparator.index),
            )
            rr_low = contrast.get("rr_ci_low", np.nan)
            rr_high = contrast.get("rr_ci_high", np.nan)
            diff_low = contrast.get("difference_ci_low", np.nan)
            diff_high = contrast.get("difference_ci_high", np.nan)
            if contrast["status"] != "available":
                status = "inconclusive"
                limitation = str(contrast["limitation"])
            elif contrast.get("limitation"):
                limitation = str(contrast["limitation"])
            if comparison_kind == "segment_complement" and (
                data["account_id"].nunique() < MIN_SEGMENT_ACCOUNTS
                or count < MIN_SEGMENT_CHURNS
                or comparator["account_id"].nunique() < MIN_SEGMENT_ACCOUNTS
                or int(comparator["is_terminal_churn"].sum()) < MIN_SEGMENT_CHURNS
            ):
                status = "inconclusive"
                limitation = "insufficient_segment_or_complement_sample"
        mrr_exposed = (
            np.nan
            if not is_month or data["mrr_active"].isna().any()
            else float(data["mrr_active"].sum())
        )
        financial_limitations = []
        if unknown:
            financial_limitations.append("mrr_lost_unknown_for_some_accounts")
        if is_month and data["mrr_active"].isna().any():
            financial_limitations.append("mrr_exposed_unknown_for_some_accounts")
        if not is_month:
            financial_limitations.append("mrr_exposed_not_aggregated_across_months")
        if financial_limitations:
            limitation = "|".join(filter(None, [limitation, *financial_limitations]))
            if status == "available" and (
                unknown or (is_month and data["mrr_active"].isna().any())
            ):
                status = "partial"
        evidence_id = (
            f"churn:{period_kind}:{period_start.date()}:{period_end.date()}:"
            f"{dimension}:{segment}:{comparison_kind}"
        )
        rows.append(
            {
                "evidence_id": evidence_id,
                "period_start": period_start,
                "period_end": period_end,
                "population": "registered_at_start",
                "chronology": "shared",
                "status": status,
                "limitation": limitation,
                "source_refs": "accounts|subscriptions|churn_events",
                "calculation": "build_monthly_churn:v1",
                "period_kind": period_kind,
                "dimension": dimension,
                "segment": segment,
                "comparison_kind": comparison_kind,
                "at_risk_accounts": denominator,
                "unique_accounts": int(data["account_id"].nunique()),
                "terminal_churns": count,
                "new_accounts": new_accounts,
                "entrant_churns": entrant_churns,
                "excluded_events": excluded_events,
                "observation_complete": bool(period_end <= RECENT_PERIOD[1]),
                "churn_rate": rate,
                "rate_unit": "account_churn/account_month",
                "ci_low": ci_low,
                "ci_high": ci_high,
                "ci_level": 0.95,
                "ci_method": "wilson" if is_month else "cluster_bootstrap_account",
                "comparator_id": comparator_id,
                "comparator_rate": comparator_rate,
                "relative_risk": relative_risk,
                "rr_ci_low": rr_low,
                "rr_ci_high": rr_high,
                "rate_difference": rate_difference,
                "difference_ci_low": diff_low,
                "difference_ci_high": diff_high,
                "mrr_lost": mrr_lost,
                "mrr_known_accounts": known,
                "mrr_unknown_accounts": unknown,
                "mrr_exposed": mrr_exposed,
                "mrr_exposed_as_of": period_start if is_month else pd.NaT,
                "currency": "USD",
                "financial_unit": "monthly_recurring_revenue",
            }
        )

    for month_start in pd.date_range(HISTORICAL_START, RECENT_PERIOD[1], freq="MS"):
        month_data = account_months.loc[account_months["period_start"].eq(month_start)]
        month_end = month_start + pd.offsets.MonthEnd(1)
        add_row(month_data, month_start, month_end, "month", "all", "all")
        for dimension in HISTORICAL_DIMENSIONS:
            for segment in sorted(month_data[dimension].astype(str).unique()):
                add_row(
                    month_data.loc[month_data[dimension].astype(str).eq(segment)],
                    month_start,
                    month_end,
                    "month",
                    dimension,
                    segment,
                )

    periods = {"reference": REFERENCE_PERIOD, "recent": RECENT_PERIOD}
    period_data = {
        name: account_months.loc[
            account_months["period_start"].ge(start) & account_months["period_start"].le(end)
        ]
        for name, (start, end) in periods.items()
    }
    add_row(
        period_data["reference"],
        REFERENCE_PERIOD[0],
        REFERENCE_PERIOD[1],
        "comparison_period",
        "all",
        "all",
    )
    add_row(
        period_data["recent"],
        RECENT_PERIOD[0],
        RECENT_PERIOD[1],
        "comparison_period",
        "all",
        "all",
        "previous_period",
        period_data["reference"],
        f"churn:comparison_period:{REFERENCE_PERIOD[0].date()}:{REFERENCE_PERIOD[1].date()}:all:all:none",
    )
    for period_name, data in period_data.items():
        start, end = periods[period_name]
        for dimension in HISTORICAL_DIMENSIONS:
            for segment in sorted(data[dimension].astype(str).unique()):
                selected_segment = data.loc[data[dimension].astype(str).eq(segment)]
                complement = data.loc[~data[dimension].astype(str).eq(segment)]
                add_row(
                    selected_segment,
                    start,
                    end,
                    "comparison_period",
                    dimension,
                    segment,
                    "segment_complement",
                    complement,
                    f"complement:{period_name}:{dimension}:{segment}",
                )
                if period_name == "recent":
                    reference_segment = period_data["reference"].loc[
                        period_data["reference"][dimension].astype(str).eq(segment)
                    ]
                    add_row(
                        selected_segment,
                        start,
                        end,
                        "comparison_period",
                        dimension,
                        segment,
                        "previous_period",
                        reference_segment,
                        f"reference:{dimension}:{segment}",
                    )
    return pd.DataFrame(rows, columns=MONTHLY_CHURN_COLUMNS)


def build_reason_distribution(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    parsed = _coerce_tables(tables)
    terminal = terminal_events.copy()
    if terminal.empty:
        terminal = terminal.reindex(columns=parsed["churn_events"].columns)
    selected_terminal, exclusions = select_first_terminal_events(
        parsed["accounts"], parsed["churn_events"], OBSERVATION_END
    )
    if set(terminal.get("churn_event_id", [])) != set(selected_terminal.get("churn_event_id", [])):
        raise ValueError("terminal_events must match shared terminal selection")
    terminal_series = terminal.set_index("account_id")["churn_date"]
    lost = mrr_lost_at_churn(parsed["subscriptions"], terminal_series)
    diagnostic_cutoff = SCORING_CUTOFF - pd.Timedelta(days=31)
    windows = (
        (
            "reference_period",
            REFERENCE_PERIOD[0],
            REFERENCE_PERIOD[1],
            "registered_at_start",
            None,
        ),
        (
            "recent_period",
            RECENT_PERIOD[0],
            RECENT_PERIOD[1],
            "registered_at_start",
            None,
        ),
        (
            "diagnostic_horizon",
            diagnostic_cutoff + pd.Timedelta(days=1),
            diagnostic_cutoff + pd.Timedelta(days=30),
            "diagnostic_horizon",
            diagnostic_cutoff,
        ),
    )
    rows = []
    accounts = parsed["accounts"].set_index("account_id")
    raw_exclusions = exclusions.merge(
        parsed["churn_events"][["churn_event_id", "churn_date"]],
        on="churn_event_id",
        how="left",
    )
    for window_id, start, end, population, eligibility_cutoff in windows:
        in_window = terminal["churn_date"].ge(start) & terminal["churn_date"].le(end)
        selected = terminal.loc[in_window].copy()
        if population == "registered_at_start" and not selected.empty:
            month_start = selected["churn_date"].dt.to_period("M").dt.start_time
            signup = selected["account_id"].map(accounts["signup_date"])
            selected = selected.loc[signup.le(month_start)]
        elif population == "diagnostic_horizon" and not selected.empty:
            selected = selected.loc[
                selected["account_id"].map(accounts["signup_date"]).le(eligibility_cutoff)
            ]
        reasons = selected["reason_code"].astype("string").fillna("unknown")
        reason_values = sorted(set(reasons) | {"unknown"})
        excluded_count = int(
            raw_exclusions.loc[
                raw_exclusions["churn_date"].ge(start) & raw_exclusions["churn_date"].le(end),
                "churn_event_id",
            ].nunique()
        )
        for reason in reason_values:
            reason_events = selected.loc[reasons.eq(reason)]
            count = len(reason_events)
            denominator = len(selected)
            ci_low, ci_high = _wilson(count, denominator)
            mrr_lost, known, unknown = _financial_loss(lost, reason_events["account_id"])
            status = "available" if denominator else "unavailable"
            limitation = "" if denominator else "zero_eligible_events"
            if unknown:
                status = "partial" if status == "available" else status
                limitation = "|".join(
                    filter(None, [limitation, "mrr_lost_unknown_for_some_accounts"])
                )
            rows.append(
                {
                    "evidence_id": f"reason:{window_id}:{population}:{reason}",
                    "period_start": start,
                    "period_end": end,
                    "population": population,
                    "chronology": "shared",
                    "status": status,
                    "limitation": limitation,
                    "source_refs": "accounts|subscriptions|churn_events",
                    "calculation": "build_reason_distribution:v1",
                    "reason_code": reason,
                    "terminal_accounts": count,
                    "eligible_events": denominator,
                    "excluded_events": excluded_count,
                    "share": count / denominator if denominator else np.nan,
                    "unit": "share_of_first_valid_terminal_accounts",
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "ci_method": "wilson",
                    "ci_level": 0.95,
                    "comparator_id": None,
                    "mrr_lost": mrr_lost,
                    "mrr_known_accounts": known,
                    "mrr_unknown_accounts": unknown,
                    "currency": "USD",
                }
            )
    return pd.DataFrame(rows, columns=REASON_DISTRIBUTION_COLUMNS)


def _event_observed_mask(
    frame: pd.DataFrame,
    value_column: str,
    coverage_column: str,
    response_column: str | None,
) -> pd.Series:
    observed = (
        frame["eligible_at_window_cutoff"].fillna(False)
        & frame[coverage_column].fillna(False)
        & frame[value_column].notna()
    )
    if response_column:
        observed &= frame[response_column].fillna(0).gt(0)
    return observed


def _cluster_bootstrap_event_metric(
    frame: pd.DataFrame,
    value_column: str,
    coverage_column: str,
    scale: float,
    response_column: str | None,
    anchors: list[pd.Timestamp],
    replicates: int,
) -> dict[str, object]:
    accounts = pd.Index(sorted(frame["account_id"].astype(str).unique()))
    if len(accounts) < 2 or not anchors:
        return {"status": "unavailable", "limitation": "insufficient_accounts_or_anchors"}
    account_position = {account_id: position for position, account_id in enumerate(accounts)}
    weights = np.random.default_rng(RANDOM_SEED).multinomial(
        len(accounts), np.full(len(accounts), 1 / len(accounts)), size=replicates
    )
    case_weights = []
    cohort_values: dict[str, list[np.ndarray]] = {
        "terminal_cases": [],
        "contemporaneous_controls": [],
    }
    for anchor in anchors:
        anchor_frame = frame.loc[frame["anchor_date"].eq(anchor)]
        case_vector = np.zeros(len(accounts))
        case_rows = anchor_frame.loc[anchor_frame["cohort"].eq("terminal_cases")]
        for account_id in case_rows["account_id"].astype(str).unique():
            case_vector[account_position[account_id]] = 1
        case_weights.append(weights @ case_vector)

        for cohort, values in cohort_values.items():
            cohort_frame = anchor_frame.loc[anchor_frame["cohort"].eq(cohort)]
            observed = _event_observed_mask(
                cohort_frame, value_column, coverage_column, response_column
            )
            observed_frame = cohort_frame.loc[observed]
            numerator = np.zeros(len(accounts))
            denominator = np.zeros(len(accounts))
            for row in observed_frame.itertuples(index=False):
                position = account_position[str(row.account_id)]
                response_weight = float(getattr(row, response_column)) if response_column else 1.0
                numerator[position] += float(getattr(row, value_column)) * scale * response_weight
                denominator[position] += response_weight
            bootstrap_denominator = weights @ denominator
            values.append(
                np.divide(
                    weights @ numerator,
                    bootstrap_denominator,
                    out=np.full(replicates, np.nan),
                    where=bootstrap_denominator > 0,
                )
            )

    case_weight_matrix = np.column_stack(case_weights)
    aggregate: dict[str, np.ndarray] = {}
    terminal_matrix = np.column_stack(cohort_values["terminal_cases"])
    control_matrix = np.column_stack(cohort_values["contemporaneous_controls"])
    comparable = (
        np.isfinite(terminal_matrix) & np.isfinite(control_matrix) & (case_weight_matrix > 0)
    )
    comparable_weight = np.where(comparable, case_weight_matrix, 0)
    total_weight = comparable_weight.sum(axis=1)
    for cohort, values in (
        ("terminal_cases", terminal_matrix),
        ("contemporaneous_controls", control_matrix),
    ):
        aggregate[cohort] = np.divide(
            (np.where(comparable, values, 0) * comparable_weight).sum(axis=1),
            total_weight,
            out=np.full(replicates, np.nan),
            where=total_weight > 0,
        )
    difference = aggregate["terminal_cases"] - aggregate["contemporaneous_controls"]
    valid_difference = difference[np.isfinite(difference)]
    if len(valid_difference) < 0.95 * replicates:
        return {"status": "unavailable", "limitation": "insufficient_valid_bootstrap_replicates"}

    result: dict[str, object] = {
        "status": "available",
        "limitation": "",
        "difference_ci_low": float(np.quantile(valid_difference, 0.025)),
        "difference_ci_high": float(np.quantile(valid_difference, 0.975)),
    }
    for cohort, values in aggregate.items():
        valid = values[np.isfinite(values)]
        result[f"{cohort}_ci_low"] = float(np.quantile(valid, 0.025))
        result[f"{cohort}_ci_high"] = float(np.quantile(valid, 0.975))
    return result


def build_event_cohort_metrics(
    event_panel: pd.DataFrame,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> pd.DataFrame:
    if event_panel.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    grouping = ["anchor_kind", "chronology", "relative_window_start", "relative_window_end"]
    for group_key, frame in event_panel.groupby(grouping, sort=True, dropna=False):
        anchor_kind, chronology, window_start, window_end = group_key
        for mechanism_id, definition in EVENT_METRIC_DEFINITIONS.items():
            value_column, coverage_column, unit, scale, response_column, primary_only = definition
            if value_column not in frame or coverage_column not in frame:
                continue
            if primary_only and int(window_start) != -30:
                continue

            anchor_values = []
            for (anchor_date, cohort), anchor_frame in frame.groupby(
                ["anchor_date", "cohort"], sort=True
            ):
                observed = _event_observed_mask(
                    anchor_frame, value_column, coverage_column, response_column
                )
                observed_frame = anchor_frame.loc[observed]
                if response_column:
                    responses = pd.to_numeric(
                        observed_frame[response_column], errors="coerce"
                    ).fillna(0)
                    denominator = float(responses.sum())
                    value = (
                        float(
                            np.average(
                                pd.to_numeric(observed_frame[value_column]),
                                weights=responses,
                            )
                            * scale
                        )
                        if denominator
                        else np.nan
                    )
                else:
                    value = (
                        float(pd.to_numeric(observed_frame[value_column]).mean() * scale)
                        if len(observed_frame)
                        else np.nan
                    )
                anchor_values.append(
                    {
                        "anchor_date": anchor_date,
                        "cohort": cohort,
                        "value": value,
                        "eligible_cases": int(
                            frame.loc[
                                frame["anchor_date"].eq(anchor_date)
                                & frame["cohort"].eq("terminal_cases"),
                                "account_id",
                            ].nunique()
                        ),
                    }
                )
            anchor_values_frame = pd.DataFrame(anchor_values)
            if anchor_values_frame.empty:
                continue
            pivot = anchor_values_frame.pivot(index="anchor_date", columns="cohort", values="value")
            cohorts = ("terminal_cases", "contemporaneous_controls")
            required = set(cohorts)
            comparable_anchors = sorted(
                pivot.dropna(subset=list(required)).index
                if required.issubset(pivot.columns)
                else []
            )
            case_weights = (
                anchor_values_frame.drop_duplicates("anchor_date")
                .set_index("anchor_date")["eligible_cases"]
                .reindex(comparable_anchors)
            )
            aggregate_values = {
                cohort: (
                    float(np.average(pivot.loc[comparable_anchors, cohort], weights=case_weights))
                    if comparable_anchors and case_weights.sum() > 0
                    else np.nan
                )
                for cohort in cohorts
            }
            difference = (
                aggregate_values["terminal_cases"] - aggregate_values["contemporaneous_controls"]
                if all(pd.notna(value) for value in aggregate_values.values())
                else np.nan
            )
            bootstrap = _cluster_bootstrap_event_metric(
                frame,
                value_column,
                coverage_column,
                scale,
                response_column,
                comparable_anchors,
                replicates,
            )
            comparable_frame = frame.loc[frame["anchor_date"].isin(comparable_anchors)]
            for cohort in ("terminal_cases", "contemporaneous_controls"):
                cohort_frame = comparable_frame.loc[comparable_frame["cohort"].eq(cohort)]
                observed = _event_observed_mask(
                    cohort_frame, value_column, coverage_column, response_column
                )
                observed_frame = cohort_frame.loc[observed]
                eligible_pairs = cohort_frame.drop_duplicates(["account_id", "anchor_date"])
                observed_pairs = observed_frame.drop_duplicates(["account_id", "anchor_date"])
                evidence_id = (
                    f"event:{anchor_kind}:{chronology}:{mechanism_id}:"
                    f"{cohort}:{int(window_start)}:{int(window_end)}"
                )
                status = "available" if comparable_anchors else "unavailable"
                limitation = "" if comparable_anchors else "no_comparable_anchors"
                if comparable_anchors and bootstrap["status"] != "available":
                    status = "inconclusive"
                    limitation = str(bootstrap["limitation"])
                rows.append(
                    {
                        "evidence_id": evidence_id,
                        "period_start": min(comparable_anchors) if comparable_anchors else pd.NaT,
                        "period_end": max(comparable_anchors) if comparable_anchors else pd.NaT,
                        "population": anchor_kind,
                        "chronology": chronology,
                        "status": status,
                        "limitation": limitation,
                        "source_refs": "event_aligned_panel",
                        "calculation": "build_event_cohort_metrics:v1",
                        "metric": mechanism_id,
                        "cohort": cohort,
                        "relative_window_start": int(window_start),
                        "relative_window_end": int(window_end),
                        "anchor_period_start": (
                            min(comparable_anchors) if comparable_anchors else pd.NaT
                        ),
                        "anchor_period_end": (
                            max(comparable_anchors) if comparable_anchors else pd.NaT
                        ),
                        "eligible_accounts": int(cohort_frame["account_id"].nunique()),
                        "observed_accounts": int(observed_frame["account_id"].nunique()),
                        "unique_accounts": int(cohort_frame["account_id"].nunique()),
                        "account_anchor_rows": len(eligible_pairs),
                        "eligible_account_anchors": len(eligible_pairs),
                        "observed_account_anchors": len(observed_pairs),
                        "reused_control_accounts": int(
                            cohort_frame.loc[
                                cohort_frame["reused_control"].fillna(False), "account_id"
                            ].nunique()
                        ),
                        "coverage": (
                            len(observed_pairs) / len(eligible_pairs)
                            if len(eligible_pairs)
                            else np.nan
                        ),
                        "coverage_unit": "covered_account_anchors/eligible_account_anchors",
                        "response_count": (
                            int(observed_frame[response_column].fillna(0).sum())
                            if response_column
                            else pd.NA
                        ),
                        "ticket_count": (
                            int(
                                cohort_frame.get("tickets_30d", pd.Series(dtype=float))
                                .fillna(0)
                                .sum()
                            )
                            if response_column
                            else pd.NA
                        ),
                        "respondent_accounts": (
                            int(observed_frame["account_id"].nunique())
                            if response_column
                            else pd.NA
                        ),
                        "value": aggregate_values[cohort],
                        "unit": unit,
                        "weighting": (
                            "responses_within_anchor;eligible_cases_between_anchors"
                            if response_column
                            else "accounts_within_anchor;eligible_cases_between_anchors"
                        ),
                        "comparator_id": evidence_id.replace(
                            cohort,
                            cohorts[1] if cohort == cohorts[0] else cohorts[0],
                        ),
                        "difference": difference,
                        "ci_low": bootstrap.get(f"{cohort}_ci_low", np.nan),
                        "ci_high": bootstrap.get(f"{cohort}_ci_high", np.nan),
                        "difference_ci_low": bootstrap.get("difference_ci_low", np.nan),
                        "difference_ci_high": bootstrap.get("difference_ci_high", np.nan),
                        "ci_method": "cluster_bootstrap_account",
                        "ci_level": 0.95,
                    }
                )
    return pd.DataFrame(rows)


def build_mechanism_scorecard(
    findings: pd.DataFrame,
    event_metrics: pd.DataFrame,
    reasons: pd.DataFrame,
) -> pd.DataFrame:
    del event_metrics, reasons
    rows = []
    gate_columns = (
        "temporal_support",
        "comparison_support",
        "sample_support",
        "association_support",
        "chronology_support",
        "cross_table_support",
    )
    for finding in findings.itertuples(index=False):
        confidence = getattr(finding, "confidence", "inconclusive")
        evidence_level = getattr(finding, "evidence_level", None)
        if evidence_level not in EVIDENCE_LEVELS:
            evidence_level = (
                "supported_mechanism" if confidence == "accepted" else "plausible_hypothesis"
            )
        gates = {column: getattr(finding, column, "unavailable") for column in gate_columns}
        rows.append(
            {
                "evidence_id": f"mechanism:{finding.finding_id}",
                "period_start": getattr(finding, "diagnostic_cutoff", pd.NaT),
                "period_end": getattr(finding, "diagnostic_cutoff", pd.NaT),
                "population": "diagnostic_horizon",
                "chronology": "strict",
                "status": "available" if confidence == "accepted" else "inconclusive",
                "limitation": getattr(finding, "limitation", ""),
                "source_refs": f"finding:{finding.finding_id}|event_cohort_metrics|reason_distribution",
                "calculation": "build_mechanism_scorecard:v1",
                "mechanism_id": finding.finding_id,
                "finding_id": finding.finding_id,
                "claim": finding.claim,
                "evidence_level": evidence_level,
                **gates,
                "gate_reasons": getattr(finding, "gate_reasons", json.dumps({})),
                "effect": getattr(finding, "adjusted_odds_ratio", np.nan),
                "effect_unit": "adjusted_odds_ratio",
                "comparator_id": "diagnostic_unexposed",
                "ci_low": getattr(finding, "ci_low", np.nan),
                "ci_high": getattr(finding, "ci_high", np.nan),
                "ci_level": 0.95,
                "ci_method": "glm_hc3",
                "p_adjusted": getattr(finding, "p_adjusted", np.nan),
                "observed_coverage": getattr(finding, "observed_coverage", np.nan),
                "strict_coverage": getattr(finding, "candidate_coverage", np.nan),
                "counterevidence": getattr(finding, "counterevidence", None),
                "rejected_statement": (
                    getattr(finding, "claim", None) if evidence_level == "rejected_claim" else None
                ),
                "recommended_validation": "Executar experimento prospectivo com grupo comparável.",
            }
        )
    return pd.DataFrame(rows)


def build_diagnostic_snapshot(panel: pd.DataFrame) -> pd.DataFrame:
    labeled = panel.loc[
        panel["churn_next_30d"].notna() & panel["cutoff"].le(pd.Timestamp("2024-11-30"))
    ].copy()
    if "has_active_subscription" in labeled:
        labeled = labeled.loc[labeled["has_active_subscription"].fillna(False)]
    if labeled.empty:
        return labeled.reset_index(drop=True)
    common_cutoff = labeled["cutoff"].max()
    return labeled.loc[labeled["cutoff"].eq(common_cutoff)].reset_index(drop=True)


def _fit_association(snapshot: pd.DataFrame, feature: str) -> dict[str, Any]:
    coverage = float(snapshot[feature].notna().mean()) if len(snapshot) else 0.0
    data = snapshot.loc[snapshot[feature].notna()].copy()
    if data[feature].nunique(dropna=True) < 2:
        return {"failure_reason": "zero_variance", "coverage": coverage}
    if data["churn_next_30d"].nunique(dropna=True) < 2:
        return {"failure_reason": "single_class", "coverage": coverage}

    candidate = data[feature].astype(float).rename("candidate")
    controls = data[[column for column in CONTROL_COLUMNS if column in data]].copy()
    controls["log_mrr_active"] = np.log1p(pd.to_numeric(controls.pop("mrr_active")))
    controls["cutoff_quarter"] = data["cutoff"].dt.to_period("Q").astype(str)
    categorical = [
        column
        for column in controls
        if controls[column].dtype == "object" or isinstance(controls[column].dtype, pd.StringDtype)
    ]
    controls = pd.get_dummies(controls, columns=categorical, drop_first=True, dtype=float)
    controls = controls.apply(pd.to_numeric, errors="coerce").astype(float)
    design = pd.concat([candidate, controls], axis=1).replace([np.inf, -np.inf], np.nan)
    usable = design.notna().all(axis=1)
    design = sm.add_constant(design.loc[usable], has_constant="add")
    outcome = data.loc[usable, "churn_next_30d"].astype(float)
    if outcome.nunique() < 2 or design["candidate"].nunique() < 2:
        return {"failure_reason": "insufficient_complete_cases", "coverage": coverage}

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = sm.GLM(outcome, design, family=sm.families.Binomial()).fit(cov_type="HC3")
        if any(
            issubclass(item.category, (PerfectSeparationWarning, SingularMatrixWarning))
            for item in caught
        ):
            raise ValueError("separation_or_singular_design")
        coefficient = float(result.params["candidate"])
        ci = result.conf_int().loc["candidate"]
        ci_low, ci_high = float(np.exp(ci.iloc[0])), float(np.exp(ci.iloc[1]))
        odds_ratio = float(np.exp(coefficient))
        if not result.converged or not np.isfinite([coefficient, ci_low, ci_high]).all():
            raise ValueError("non_finite_or_non_converged")
        return {
            "coefficient": coefficient,
            "odds_ratio": odds_ratio,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "p_value": float(result.pvalues["candidate"]),
            "effective_n": len(outcome),
            "coverage": coverage,
            "failure_reason": None,
        }
    except (ValueError, FloatingPointError, np.linalg.LinAlgError, PerfectSeparationError) as error:
        return {
            "failure_reason": f"model_failure:{type(error).__name__}",
            "coverage": coverage,
        }


def _exposure_mask(series: pd.Series, operator: str, threshold: object) -> pd.Series:
    if operator == "le":
        return series.le(threshold)
    if operator == "ge":
        return series.ge(threshold)
    if operator == "eq":
        return series.eq(threshold)
    raise ValueError(f"unknown exposure operator: {operator}")


def _reason_corroborates(
    driver_group: str,
    exposed_accounts: set[str],
    churn_events: pd.DataFrame,
    cutoff: pd.Timestamp | None = None,
    reasons: pd.DataFrame | None = None,
) -> bool:
    terminal = (
        churn_events.loc[~churn_events["is_reactivation"].fillna(False)]
        .sort_values(["churn_date", "account_id"])
        .drop_duplicates("account_id", keep="first")
        .copy()
    )
    if cutoff is not None:
        cutoff = pd.Timestamp(cutoff)
        terminal = terminal.loc[
            terminal["churn_date"].gt(cutoff)
            & terminal["churn_date"].le(cutoff + pd.Timedelta(days=30))
        ]
    if reasons is not None:
        diagnostic = reasons.loc[reasons["population"].eq("diagnostic_horizon")]
        if diagnostic.empty or int(diagnostic["eligible_events"].max()) < MIN_SEGMENT_CHURNS:
            return False
    if len(terminal) < MIN_SEGMENT_CHURNS:
        return False
    patterns = {
        "product": r"product|feature|usability|technical",
        "support": r"support|service|sla",
        "commercial": r"price|pricing|competitor|budget|commercial",
    }
    reason_match = (
        terminal["reason_code"]
        .astype("string")
        .str.contains(patterns[driver_group], case=False, na=False, regex=True)
    )
    overall = float(reason_match.mean())
    exposed = terminal["account_id"].isin(exposed_accounts)
    if not exposed.any() or overall == 0:
        return False
    return bool(reason_match.loc[exposed].mean() / overall >= 1.25)


def _event_gate_inputs(
    event_metrics: pd.DataFrame | None,
    finding_id: str,
) -> pd.DataFrame:
    if event_metrics is None or event_metrics.empty:
        return pd.DataFrame(
            columns=[
                "chronology",
                "cohort",
                "status",
                "difference",
                "difference_ci_low",
                "difference_ci_high",
                "unique_accounts",
                "coverage",
            ]
        )
    return event_metrics.loc[
        event_metrics["metric"].eq(finding_id)
        & event_metrics["population"].eq("terminal_event")
        & event_metrics["relative_window_start"].eq(-30)
    ].copy()


def _direction_passes(value: float, expected_direction: str) -> bool:
    return bool(value < 0 if expected_direction == "lower" else value > 0)


def rank_findings(findings: pd.DataFrame) -> pd.DataFrame:
    ranked = findings.copy()
    ranked["priority_rank"] = pd.Series(pd.NA, index=ranked.index, dtype="Int64")
    accepted = ranked["confidence"].eq("accepted")
    actionability = ranked.get("actionability", pd.Series("structural-only", index=ranked.index))
    ranked["_actionability_order"] = actionability.map(
        {"immediate": 0, "structural-only": 1}
    ).fillna(2)
    accepted_order = ranked.loc[accepted].sort_values(
        ["mrr_exposed_max", "affected_accounts", "_actionability_order"],
        ascending=[False, False, True],
    )
    ranked.loc[accepted_order.index, "priority_rank"] = range(1, len(accepted_order) + 1)
    return (
        ranked.sort_values(
            ["priority_rank", "mrr_exposed_max", "affected_accounts"],
            ascending=[True, False, False],
            na_position="last",
        )
        .drop(columns="_actionability_order")
        .reset_index(drop=True)
    )


def _segment_metrics(snapshot: pd.DataFrame) -> pd.DataFrame:
    if snapshot.empty:
        return pd.DataFrame()
    data = snapshot.copy()
    overall_churn_rate = float(data["churn_next_30d"].astype(int).mean())
    data["mrr_band"] = pd.cut(
        data["mrr_active"],
        bins=[-np.inf, 500, 2_000, np.inf],
        labels=["low", "mid", "high"],
    )
    rows = []
    for dimension in (
        "industry",
        "country",
        "referral_source",
        "plan_tier",
        "billing_frequency",
        "is_trial",
        "mrr_band",
    ):
        for value, group in data.groupby(dimension, dropna=False, observed=True):
            churn = group["churn_next_30d"].astype(int)
            churn_count = int(churn.sum())
            lost_mrr = group.get("mrr_lost_next_30d", group["mrr_active"]).loc[churn.eq(1)]
            rows.append(
                {
                    "dimension": dimension,
                    "segment": str(value),
                    "sample_size": len(group),
                    "churn_count": churn_count,
                    "churn_rate": float(churn.mean()),
                    "overall_churn_rate": overall_churn_rate,
                    "churn_rate_delta": float(churn.mean() - overall_churn_rate),
                    "relative_risk": (
                        float(churn.mean() / overall_churn_rate) if overall_churn_rate else np.nan
                    ),
                    "mrr_lost": (np.nan if lost_mrr.isna().any() else float(lost_mrr.sum())),
                    "mrr_exposed": float(group["mrr_active"].sum()),
                    "coverage": float(group["churn_next_30d"].notna().mean()),
                    "confidence": (
                        "eligible"
                        if len(group) >= MIN_SEGMENT_ACCOUNTS and churn_count >= MIN_SEGMENT_CHURNS
                        else "inconclusive"
                    ),
                }
            )
    return pd.DataFrame(rows)


def evaluate_candidates(
    observed: pd.DataFrame,
    strict: pd.DataFrame,
    churn_events: pd.DataFrame,
    event_metrics: pd.DataFrame | None = None,
    reasons: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed_snapshot = build_diagnostic_snapshot(observed)
    strict_snapshot = build_diagnostic_snapshot(strict)
    scoring = strict.loc[strict["cutoff"].eq(SCORING_CUTOFF)].copy()
    fits = {
        finding_id: {
            "observed": _fit_association(observed_snapshot, candidate[0]),
            "strict": _fit_association(strict_snapshot, candidate[0]),
        }
        for finding_id, candidate in CANDIDATES.items()
    }
    valid_ids = [
        finding_id
        for finding_id, fit in fits.items()
        if not fit["strict"].get("failure_reason")
        and np.isfinite(fit["strict"].get("p_value", np.nan))
    ]
    adjusted_p = {finding_id: np.nan for finding_id in CANDIDATES}
    if valid_ids:
        corrected = multipletests(
            [fits[finding_id]["strict"]["p_value"] for finding_id in valid_ids],
            alpha=0.05,
            method="holm",
        )[1]
        adjusted_p.update(dict(zip(valid_ids, corrected, strict=True)))
    rows = []

    for finding_id, candidate in CANDIDATES.items():
        feature, expected_direction, driver_group, operator, threshold = candidate
        observed_fit = fits[finding_id]["observed"]
        strict_fit = fits[finding_id]["strict"]
        failure_reason = strict_fit.get("failure_reason") or observed_fit.get("failure_reason")
        observed_effect = observed_fit.get("coefficient", np.nan)
        strict_effect = strict_fit.get("coefficient", np.nan)
        sensitivity_delta = (
            abs(strict_effect - observed_effect) / max(abs(observed_effect), 1e-9)
            if pd.notna(observed_effect) and pd.notna(strict_effect)
            else np.nan
        )
        direction_stable = bool(
            pd.notna(observed_effect)
            and pd.notna(strict_effect)
            and np.sign(observed_effect) == np.sign(strict_effect)
            and sensitivity_delta <= 0.25
        )
        expected = _direction_passes(strict_effect, expected_direction)
        interval_passes = bool(
            strict_fit.get("ci_high", np.inf) < 1
            if expected_direction == "lower"
            else strict_fit.get("ci_low", -np.inf) > 1
        )
        exposure = _exposure_mask(strict_snapshot[feature], operator, threshold).fillna(False)
        exposed_snapshot = strict_snapshot.loc[exposure]
        exposed_accounts = set(exposed_snapshot["account_id"].astype(str))
        sample_passes = bool(
            len(exposed_snapshot) >= MIN_SEGMENT_ACCOUNTS
            and int(exposed_snapshot["churn_next_30d"].sum()) >= MIN_SEGMENT_CHURNS
            and strict_fit.get("coverage", 0.0) >= MIN_COVERAGE
        )
        metric_rows = _event_gate_inputs(event_metrics, finding_id)
        chronology_rows = {
            chronology: metric_rows.loc[
                metric_rows["chronology"].eq(chronology)
                & metric_rows["cohort"].eq("terminal_cases")
            ]
            for chronology in ("observed", "strict")
        }
        temporal_available = all(
            len(frame) == 1 and frame.iloc[0]["status"] != "unavailable"
            for frame in chronology_rows.values()
        )
        temporal_passes = temporal_available and all(
            _direction_passes(float(frame.iloc[0]["difference"]), expected_direction)
            for frame in chronology_rows.values()
        )
        strict_metric = chronology_rows["strict"]
        comparison_available = temporal_available and strict_metric.iloc[0]["status"] == "available"
        comparison_passes = comparison_available and _direction_passes(
            float(
                strict_metric.iloc[0][
                    "difference_ci_high" if expected_direction == "lower" else "difference_ci_low"
                ]
            ),
            expected_direction,
        )
        strict_sample = metric_rows.loc[metric_rows["chronology"].eq("strict")]
        cohort_sample_passes = bool(
            {"terminal_cases", "contemporaneous_controls"}.issubset(set(strict_sample["cohort"]))
            and strict_sample.groupby("cohort")["unique_accounts"].max().ge(30).all()
            and strict_sample.groupby("cohort")["coverage"].min().ge(MIN_COVERAGE).all()
        )
        sample_available = bool(
            {"terminal_cases", "contemporaneous_controls"}.issubset(set(strict_sample["cohort"]))
            and strict_sample["coverage"].notna().all()
        )
        sample_gate_passes = sample_passes and cohort_sample_passes
        association_available = bool(
            not strict_fit.get("failure_reason") and np.isfinite(adjusted_p[finding_id])
        )
        association_passes = bool(
            association_available
            and expected
            and interval_passes
            and adjusted_p[finding_id] <= 0.05
        )
        chronology_available = not (
            observed_fit.get("failure_reason") or strict_fit.get("failure_reason")
        )
        corroborated = _reason_corroborates(
            driver_group,
            exposed_accounts,
            churn_events,
            strict_snapshot["cutoff"].max(),
            reasons,
        )
        diagnostic_reasons = (
            reasons.loc[reasons["population"].eq("diagnostic_horizon")]
            if reasons is not None and not reasons.empty
            else pd.DataFrame()
        )
        reason_available = bool(
            not diagnostic_reasons.empty
            and int(diagnostic_reasons["eligible_events"].max()) >= MIN_SEGMENT_CHURNS
        )

        gate_states = {
            "temporal_support": (
                "pass" if temporal_passes else "fail" if temporal_available else "unavailable"
            ),
            "comparison_support": (
                "pass" if comparison_passes else "fail" if comparison_available else "unavailable"
            ),
            "sample_support": (
                "pass" if sample_gate_passes else "fail" if sample_available else "unavailable"
            ),
            "association_support": (
                "pass" if association_passes else "fail" if association_available else "unavailable"
            ),
            "chronology_support": (
                "pass" if direction_stable else "fail" if chronology_available else "unavailable"
            ),
            "cross_table_support": (
                "pass" if corroborated else "fail" if reason_available else "unavailable"
            ),
        }
        accepted = all(state == "pass" for state in gate_states.values())
        gate_reasons = {
            "temporal_support": "strict_and_observed_event_contrast_expected_direction",
            "comparison_support": "strict_event_difference_ci_expected_side_of_zero",
            "sample_support": "snapshot_and_event_cohort_sample_coverage_thresholds",
            "association_support": "glm_direction_ci_and_holm_adjusted_p",
            "chronology_support": "observed_strict_direction_and_relative_delta",
            "cross_table_support": "diagnostic_horizon_reason_share_ratio_at_least_1.25",
        }
        if not failure_reason and gate_states["chronology_support"] != "pass":
            failure_reason = "chronology_instability"
        elif not failure_reason and gate_states["sample_support"] != "pass":
            failure_reason = "sample_or_coverage_gate"
        elif not failure_reason and gate_states["cross_table_support"] != "pass":
            failure_reason = "cross_table_gate"
        elif not failure_reason and gate_states["association_support"] != "pass":
            failure_reason = "association_gate"
        elif not failure_reason and gate_states["temporal_support"] != "pass":
            failure_reason = "temporal_gate"
        elif not failure_reason and gate_states["comparison_support"] != "pass":
            failure_reason = "comparison_gate"

        scoring_exposure = (
            _exposure_mask(scoring[feature], operator, threshold).fillna(False)
            if feature in scoring
            else pd.Series(False, index=scoring.index)
        )
        exposed_scoring = scoring.loc[scoring_exposure].drop_duplicates("account_id")
        diagnostic_churns = int(exposed_snapshot["churn_next_30d"].sum())
        if str(failure_reason).startswith("model_failure"):
            counterevidence = "O modelo estatístico não produziu uma estimativa estável."
        elif failure_reason == "chronology_instability":
            counterevidence = (
                f"Efeito observed={observed_effect:.3f}, strict={strict_effect:.3f}, "
                f"delta={sensitivity_delta:.3f}."
            )
        elif failure_reason == "sample_or_coverage_gate":
            counterevidence = (
                f"Amostra exposta={len(exposed_snapshot)}, churns={diagnostic_churns}, "
                f"cobertura={strict_fit.get('coverage', 0.0):.3f}."
            )
        elif failure_reason == "cross_table_gate":
            counterevidence = "Os motivos do primeiro churn não corroboraram o sinal."
        elif failure_reason == "association_gate":
            counterevidence = (
                f"OR={strict_fit.get('odds_ratio', np.nan):.3f}; intervalo de 95%="
                f"[{strict_fit.get('ci_low', np.nan):.3f}, "
                f"{strict_fit.get('ci_high', np.nan):.3f}]."
            )
        else:
            counterevidence = "Efeito, intervalo e cronologias passaram os gates definidos."
        actions = ACTIONS[driver_group]
        rows.append(
            {
                "finding_id": finding_id,
                "driver_group": driver_group,
                "claim": f"{feature} está associado ao churn futuro de 30 dias.",
                "evidence_level": ("supported_mechanism" if accepted else "plausible_hypothesis"),
                "adjusted_odds_ratio": strict_fit.get("odds_ratio", np.nan),
                "ci_low": strict_fit.get("ci_low", np.nan),
                "ci_high": strict_fit.get("ci_high", np.nan),
                "p_value": strict_fit.get("p_value", np.nan),
                "p_adjusted": adjusted_p[finding_id],
                "effective_n": strict_fit.get("effective_n", pd.NA),
                "observed_effect": observed_effect,
                "strict_effect": strict_effect,
                "sensitivity_delta": sensitivity_delta,
                "diagnostic_cutoff": strict_snapshot["cutoff"].max(),
                "horizon_days": 30,
                "exposure_rule": f"{feature} {operator} {threshold}",
                "diagnostic_exposed_accounts": len(exposed_snapshot),
                "diagnostic_exposed_churns": diagnostic_churns,
                "candidate_coverage": strict_fit.get("coverage", 0.0),
                "observed_coverage": observed_fit.get("coverage", 0.0),
                "source_tables": "accounts|subscriptions|feature_usage|support_tickets|churn_events",
                "affected_accounts": len(exposed_scoring),
                "mrr_exposed_max": float(exposed_scoring["mrr_active"].sum()),
                "confidence": "accepted" if accepted else "inconclusive",
                "failure_reason": failure_reason,
                "counterevidence": counterevidence,
                "limitation": "Dados observacionais sustentam associação, não causalidade comprovada.",
                "actionability": "immediate",
                **gate_states,
                "gate_reasons": json.dumps(gate_reasons, sort_keys=True),
                **actions,
            }
        )

    return rank_findings(pd.DataFrame(rows)), _segment_metrics(strict_snapshot)


def _monthly_values(frame: pd.DataFrame, value_column: str) -> pd.Series:
    return frame.groupby("cutoff", observed=True)[value_column].mean().sort_index()


def build_claim_checks(strict_panel: pd.DataFrame) -> pd.DataFrame:
    labeled = strict_panel.loc[strict_panel["churn_next_30d"].notna()].copy()
    if "has_active_subscription" in labeled:
        labeled = labeled.loc[labeled["has_active_subscription"].fillna(False)]
    cutoffs = sorted(labeled["cutoff"].drop_duplicates())[-6:]
    labeled = labeled.loc[labeled["cutoff"].isin(cutoffs)]
    cohorts = {
        "overall": labeled,
        "retained": labeled.loc[labeled["churn_next_30d"].eq(0)],
        "churn_next_30d": labeled.loc[labeled["churn_next_30d"].eq(1)],
    }
    rows = []

    for cohort_name, cohort in cohorts.items():
        usage = cohort.loc[
            cohort["usage_coverage_30d"].fillna(False) & cohort["usage_count_30d"].notna()
        ].copy()
        usage["daily_usage"] = usage["usage_count_30d"] / 30
        monthly_usage = _monthly_values(usage, "daily_usage")
        if len(monthly_usage) >= 2:
            slope = float(np.polyfit(np.arange(len(monthly_usage)), monthly_usage.values, 1)[0])
            usage_start, usage_end = float(monthly_usage.iloc[0]), float(monthly_usage.iloc[-1])
            endpoint_change = usage_end - usage_start
            status = (
                "up" if endpoint_change > 1e-9 else "down" if endpoint_change < -1e-9 else "flat"
            )
        else:
            slope, usage_start, usage_end, status = np.nan, np.nan, np.nan, "insufficient"
        rows.append(
            {
                "claim_id": "C-usage-growth",
                "cohort": cohort_name,
                "start_value": usage_start,
                "end_value": usage_end,
                "slope": slope,
                "status": status,
                "coverage": float(len(usage) / len(cohort)) if len(cohort) else 0.0,
                "cutoff_start": min(cutoffs) if cutoffs else pd.NaT,
                "cutoff_end": max(cutoffs) if cutoffs else pd.NaT,
                "limitation": "Tendência descritiva; não identifica causa.",
            }
        )

        valid_satisfaction = cohort.loc[
            cohort["mean_satisfaction_90d"].notna() & cohort["satisfaction_responses_90d"].gt(0)
        ].copy()
        monthly_satisfaction = valid_satisfaction.groupby("cutoff", observed=True).apply(
            lambda group: np.average(
                group["mean_satisfaction_90d"],
                weights=group["satisfaction_responses_90d"],
            ),
            include_groups=False,
        )
        responses = float(valid_satisfaction["satisfaction_responses_90d"].sum())
        tickets = float(cohort.get("tickets_90d", pd.Series(0, index=cohort.index)).sum())
        coverage = responses / tickets if tickets else np.nan
        weighted_mean = (
            float(
                np.average(
                    valid_satisfaction["mean_satisfaction_90d"],
                    weights=valid_satisfaction["satisfaction_responses_90d"],
                )
            )
            if responses
            else np.nan
        )
        status = (
            "insufficient"
            if pd.isna(weighted_mean) or pd.isna(coverage)
            else "ok"
            if weighted_mean >= 4.0 and coverage >= MIN_COVERAGE
            else "concern"
        )
        rows.append(
            {
                "claim_id": "C-satisfaction-ok",
                "cohort": cohort_name,
                "start_value": (
                    float(monthly_satisfaction.iloc[0]) if len(monthly_satisfaction) else np.nan
                ),
                "end_value": (
                    float(monthly_satisfaction.iloc[-1]) if len(monthly_satisfaction) else np.nan
                ),
                "slope": np.nan,
                "status": status,
                "coverage": coverage,
                "cutoff_start": min(cutoffs) if cutoffs else pd.NaT,
                "cutoff_end": max(cutoffs) if cutoffs else pd.NaT,
                "limitation": "Média ponderada somente entre tickets com resposta.",
            }
        )

    return pd.DataFrame(rows)
