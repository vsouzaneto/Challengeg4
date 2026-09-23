from pathlib import Path

import pandas as pd

from .config import RAW_FILE_SHA256, sha256_file

SCHEMAS = {
    "accounts": (
        "account_id",
        "account_name",
        "industry",
        "country",
        "signup_date",
        "referral_source",
        "plan_tier",
        "seats",
        "is_trial",
        "churn_flag",
    ),
    "subscriptions": (
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
    "feature_usage": (
        "usage_id",
        "subscription_id",
        "usage_date",
        "feature_name",
        "usage_count",
        "usage_duration_secs",
        "error_count",
        "is_beta_feature",
    ),
    "support_tickets": (
        "ticket_id",
        "account_id",
        "submitted_at",
        "closed_at",
        "resolution_time_hours",
        "priority",
        "first_response_time_minutes",
        "satisfaction_score",
        "escalation_flag",
    ),
    "churn_events": (
        "churn_event_id",
        "account_id",
        "churn_date",
        "reason_code",
        "refund_amount_usd",
        "preceding_upgrade_flag",
        "preceding_downgrade_flag",
        "is_reactivation",
        "feedback_text",
    ),
}

PRIMARY_KEYS = {
    "accounts": "account_id",
    "subscriptions": "subscription_id",
    "feature_usage": "usage_id",
    "support_tickets": "ticket_id",
    "churn_events": "churn_event_id",
}
FOREIGN_KEYS = (
    ("subscriptions", "account_id", "accounts", "account_id"),
    ("feature_usage", "subscription_id", "subscriptions", "subscription_id"),
    ("support_tickets", "account_id", "accounts", "account_id"),
    ("churn_events", "account_id", "accounts", "account_id"),
)
DATE_FIELDS = {
    "signup_date",
    "start_date",
    "end_date",
    "usage_date",
    "submitted_at",
    "closed_at",
    "churn_date",
}
BOOLEAN_FIELDS = {
    "is_trial",
    "churn_flag",
    "upgrade_flag",
    "downgrade_flag",
    "auto_renew_flag",
    "is_beta_feature",
    "escalation_flag",
    "preceding_upgrade_flag",
    "preceding_downgrade_flag",
    "is_reactivation",
}
INTEGER_FIELDS = {
    "seats",
    "mrr_amount",
    "arr_amount",
    "usage_count",
    "usage_duration_secs",
    "error_count",
    "first_response_time_minutes",
}
FLOAT_FIELDS = {"resolution_time_hours", "satisfaction_score", "refund_amount_usd"}
NON_NEGATIVE_FIELDS = INTEGER_FIELDS | FLOAT_FIELDS


class DataContractError(ValueError):
    pass


def _parse_boolean(series: pd.Series, table: str, column: str) -> pd.Series:
    parsed = series.map({True: True, False: False, "True": True, "False": False})
    invalid = series.notna() & parsed.isna()
    if invalid.any():
        raise DataContractError(f"{table}.{column}: {int(invalid.sum())} invalid boolean")
    return parsed.astype("boolean")


def _parse_numeric(series: pd.Series, table: str, column: str, *, integer: bool) -> pd.Series:
    parsed = pd.to_numeric(series, errors="coerce")
    invalid = series.notna() & parsed.isna()
    if integer:
        invalid |= parsed.notna() & parsed.mod(1).ne(0)
    if invalid.any():
        raise DataContractError(f"{table}.{column}: {int(invalid.sum())} invalid numeric value")
    return parsed.astype("Int64" if integer else "Float64")


def _coerce_table(name: str, table: pd.DataFrame) -> pd.DataFrame:
    expected = SCHEMAS[name]
    missing = [column for column in expected if column not in table.columns]
    if missing:
        raise DataContractError(f"{name}: missing columns {missing}")

    parsed = table.copy()
    for column in expected:
        source = parsed[column]
        if column in DATE_FIELDS:
            values = pd.to_datetime(source, errors="coerce")
            invalid = source.notna() & values.isna()
            if invalid.any():
                raise DataContractError(f"{name}.{column}: {int(invalid.sum())} invalid date")
            parsed[column] = values
        elif column in BOOLEAN_FIELDS:
            parsed[column] = _parse_boolean(source, name, column)
        elif column in INTEGER_FIELDS:
            parsed[column] = _parse_numeric(source, name, column, integer=True)
        elif column in FLOAT_FIELDS:
            parsed[column] = _parse_numeric(source, name, column, integer=False)
        else:
            parsed[column] = source.astype("string")
    return parsed


def _coerce_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    missing = sorted(set(SCHEMAS) - set(tables))
    if missing:
        raise DataContractError(f"missing tables: {missing}")
    return {name: _coerce_table(name, tables[name]) for name in SCHEMAS}


def load_raw_tables(raw_dir: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for filename in RAW_FILE_SHA256:
        path = raw_dir / filename
        if not path.is_file():
            raise DataContractError(f"missing file: {path}")
        if sha256_file(path) != RAW_FILE_SHA256[filename]:
            raise DataContractError(f"{filename}: checksum mismatch")
        name = filename.removeprefix("ravenstack_").removesuffix(".csv")
        tables[name] = pd.read_csv(path, dtype="string")
    return _coerce_tables(tables)


def add_usage_row_key(usage: pd.DataFrame) -> pd.DataFrame:
    keyed = usage.copy()
    occurrence = keyed.groupby("usage_id", dropna=False).cumcount()
    keyed["usage_row_id"] = keyed["usage_id"].astype("string") + "#" + occurrence.astype(str)
    return keyed


def validate_contracts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    parsed = _coerce_tables(tables)
    tables.update(parsed)

    for name, key in PRIMARY_KEYS.items():
        null_count = int(parsed[name][key].isna().sum())
        if null_count:
            raise DataContractError(f"{name}.{key}: {null_count} missing primary key")
        if name != "feature_usage":
            duplicate_count = int(parsed[name][key].duplicated().sum())
            if duplicate_count:
                raise DataContractError(f"{name}.{key}: {duplicate_count} duplicate primary key")

    for child, child_key, parent, parent_key in FOREIGN_KEYS:
        orphan = parsed[child][child_key].notna() & ~parsed[child][child_key].isin(
            parsed[parent][parent_key]
        )
        if orphan.any():
            raise DataContractError(f"{child}.{child_key}: {int(orphan.sum())} orphan rows")

    for name, table in parsed.items():
        for column in NON_NEGATIVE_FIELDS.intersection(table.columns):
            negative = table[column].lt(0).fillna(False)
            if negative.any():
                raise DataContractError(f"{name}.{column}: {int(negative.sum())} negative values")

    subscriptions = parsed["subscriptions"]
    mismatched_arr = subscriptions["arr_amount"].ne(subscriptions["mrr_amount"] * 12)
    if mismatched_arr.any():
        raise DataContractError(
            f"subscriptions.arr_amount: {int(mismatched_arr.sum())} rows differ from 12 * mrr_amount"
        )

    from .quality import build_quality_report

    contradictions = build_quality_report(parsed)["contradictions"]
    return pd.DataFrame(
        [
            {"severity": "warning", "rule": rule, "count": count}
            for rule, count in contradictions.items()
            if count
        ]
    )
