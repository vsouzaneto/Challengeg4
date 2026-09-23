from typing import Any

import pandas as pd

from .config import OBSERVATION_END
from .contracts import FOREIGN_KEYS, PRIMARY_KEYS, _coerce_tables
from .panel import select_first_terminal_events


def _orphan_counts(tables: dict[str, pd.DataFrame]) -> dict[str, int]:
    return {
        f"{child}.{child_key}": int(
            (
                tables[child][child_key].notna()
                & ~tables[child][child_key].isin(tables[parent][parent_key])
            ).sum()
        )
        for child, child_key, parent, parent_key in FOREIGN_KEYS
    }


def build_quality_report(tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
    parsed = _coerce_tables(tables)
    accounts = parsed["accounts"]
    subscriptions = parsed["subscriptions"]
    usage = parsed["feature_usage"]
    tickets = parsed["support_tickets"]
    churn = parsed["churn_events"]

    usage_lifecycle = usage.merge(
        subscriptions[["subscription_id", "account_id", "start_date", "end_date"]],
        on="subscription_id",
        how="left",
        validate="many_to_one",
    ).merge(
        accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
    )
    ticket_lifecycle = tickets.merge(
        accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
    )
    churn_lifecycle = churn.merge(
        accounts[["account_id", "signup_date"]],
        on="account_id",
        how="left",
        validate="many_to_one",
    )

    terminal_events, _ = select_first_terminal_events(accounts, churn, OBSERVATION_END)
    terminal_accounts = set(terminal_events["account_id"].dropna())
    account_terminal = accounts["account_id"].isin(terminal_accounts)
    subscription_account_flag = (
        subscriptions.groupby("account_id")["churn_flag"].any().reindex(accounts["account_id"])
    )

    contradictions = {
        "duplicate_usage_id_groups": int((usage.groupby("usage_id").size() > 1).sum()),
        "usage_before_subscription": int(
            usage_lifecycle["usage_date"].lt(usage_lifecycle["start_date"]).sum()
        ),
        "usage_before_signup": int(
            usage_lifecycle["usage_date"].lt(usage_lifecycle["signup_date"]).sum()
        ),
        "usage_after_subscription": int(
            (
                usage_lifecycle["end_date"].notna()
                & usage_lifecycle["usage_date"].gt(usage_lifecycle["end_date"])
            ).sum()
        ),
        "tickets_before_signup": int(
            ticket_lifecycle["submitted_at"].lt(ticket_lifecycle["signup_date"]).sum()
        ),
        "events_before_signup": int(
            churn_lifecycle["churn_date"].lt(churn_lifecycle["signup_date"]).sum()
        ),
        "tickets_closed_before_submission": int(
            tickets["closed_at"].lt(tickets["submitted_at"]).sum()
        ),
        "accounts_flag_vs_terminal_event": int(
            accounts["churn_flag"].fillna(False).ne(account_terminal).sum()
        ),
        "subscription_accounts_flag_vs_terminal_event": int(
            (
                subscription_account_flag.fillna(False).to_numpy() != account_terminal.to_numpy()
            ).sum()
        ),
    }

    return {
        "rows": {name: len(table) for name, table in parsed.items()},
        "nulls": {
            name: {column: int(count) for column, count in table.isna().sum().items()}
            for name, table in parsed.items()
        },
        "duplicate_ids": {
            name: int(table[key].duplicated().sum())
            for name, key in PRIMARY_KEYS.items()
            for table in (parsed[name],)
        },
        "orphan_counts": _orphan_counts(parsed),
        "contradictions": contradictions,
        "label_policy": "first_valid_non_reactivation_event",
    }
