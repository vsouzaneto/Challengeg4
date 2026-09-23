"""Operational evidence from the text-free Customer Support structured lane."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

INTERVAL_STATUSES = ("valid", "not_closed", "missing", "invalid_timestamp", "negative")
GROUP_COLUMNS = ("Ticket Channel", "Ticket Priority", "target")
MIN_WASTE_SUPPORT = 30
MIN_SATISFACTION_SUPPORT = 10
MIN_MAE_IMPROVEMENT = 0.02
BOTTLENECK_COLUMNS = (
    "grouping", *GROUP_COLUMNS, "n_total", "n_eligible", "n_excluded",
    "excluded_not_closed", "excluded_missing", "excluded_invalid_timestamp",
    "excluded_negative", "median_hours", "median_ci95_low", "median_ci95_high",
    "q1_hours", "q3_hours", "iqr_hours", "support_status", "rank_worst",
    "interval_name", "first_response_observable",
    "total_resolution_observable",
)
WASTE_COLUMNS = (
    "target", "Ticket Priority", "eligible_n", "peer_median_hours",
    "observed_excess_hours", "rank_excess", "share_of_supported_excess",
    "status", "evidence_kind", "realized_savings",
)


@dataclass(frozen=True)
class SatisfactionReport:
    status: Literal["supported", "no_reliable_signal", "insufficient_support"]
    total_rows: int
    valid_ratings: int
    missing_ratings: int
    invalid_ratings: int
    excluded_from_model: int
    univariate_effects: tuple[dict[str, object], ...]
    cv: dict[str, object] | None
    baseline_mae: float | None
    ridge_mae: float | None
    relative_mae_improvement: float | None
    permutation_importance: dict[str, float] | None
    conclusion: str
    selection_limitation: str


@dataclass(frozen=True)
class OperationalSummary:
    schema_version: int
    evidence_kind: Literal["historical_observed"]
    analysis_scope: str
    data_version: str | None
    source_rows: int | None
    sanitized_rows: int | None
    representative_rows: int | None
    development_rows: int
    valid_intervals: int
    interval_exclusions: dict[str, int]
    median_post_response_hours: float | None
    observed_excess_hours: float | None
    supported_waste_groups: int
    satisfaction_status: str
    satisfaction_sample: int
    limitations: tuple[str, ...]
    status: Literal["ready", "insufficient_support"] = "ready"
    reason: str | None = None
    analysis_rows: int | None = None
    source_lane: str | None = None
    text_fields_retained: bool | None = None
    cost_observed: bool = False


@dataclass(frozen=True)
class ScenarioAssumptions:
    annual_eligible_volume: int
    addressable_share: float
    minutes_saved: float
    hourly_cost: float
    name: Literal["conservative", "base", "optimistic"]

    def __post_init__(self) -> None:
        if (isinstance(self.annual_eligible_volume, bool)
                or not isinstance(self.annual_eligible_volume, int)
                or self.annual_eligible_volume < 0):
            raise ValueError("invalid_scenario:annual_eligible_volume")
        for field in ("addressable_share", "minutes_saved", "hourly_cost"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"invalid_scenario:{field}")
            if not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"invalid_scenario:{field}")
        if not 0 <= float(self.addressable_share) <= 1:
            raise ValueError("invalid_scenario:addressable_share")
        if self.name not in {"conservative", "base", "optimistic"}:
            raise ValueError("invalid_scenario:name")


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    annual_eligible_volume: int
    addressable_share: float
    minutes_saved: float
    hourly_cost: float
    annual_hours: float
    annual_cost: float
    evidence_kind: Literal["projected"]
    historical_data_version: str | None


def _require_sanitized_customer(frame: pd.DataFrame, columns: set[str]) -> None:
    forbidden = {
        "Customer Name", "Customer Email", "Customer Age", "Customer Gender",
        "Ticket Description", "text", "resolution", "text_group_id",
    }
    if forbidden & set(frame.columns):
        raise ValueError("analytics_requires_sanitized_frame")
    required = {"ticket_id", "domain", *columns}
    if not required.issubset(frame.columns):
        raise ValueError("analytics_schema_mismatch")
    if not frame["domain"].eq("customer").all():
        raise ValueError("analytics_domain_mismatch")
    if not frame["ticket_id"].astype(str).str.startswith("customer:").all():
        raise ValueError("analytics_invalid_ticket_id")


def _finite(value: float | int | np.number | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def median_confidence_interval(values: pd.Series) -> tuple[float | None, float | None]:
    """Return a deterministic distribution-free approximation for the median's 95% CI."""
    ordered = np.sort(pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float))
    size = len(ordered)
    if size < 5:
        return None, None
    half_width = 1.96 * math.sqrt(size) / 2
    lower = max(0, math.floor(size / 2 - half_width))
    upper = min(size - 1, math.ceil(size / 2 + half_width))
    return _finite(ordered[lower]), _finite(ordered[upper])


def add_operational_fields(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the observable post-response interval and one exclusive status per row."""
    _require_sanitized_customer(
        frame, {"Ticket Status", "First Response Time", "Time to Resolution"}
    )
    result = frame.copy()
    first = pd.to_datetime(
        result["First Response Time"], errors="coerce", format="mixed", utc=True
    )
    resolved = pd.to_datetime(
        result["Time to Resolution"], errors="coerce", format="mixed", utc=True
    )
    statuses: list[str] = []
    hours: list[float | None] = []
    for closed, raw_first, raw_resolved, first_at, resolved_at in zip(
        result["Ticket Status"].eq("Closed"), result["First Response Time"],
        result["Time to Resolution"], first, resolved, strict=True
    ):
        if not closed:
            status, interval = "not_closed", None
        elif (raw_first is None or raw_resolved is None
              or pd.isna(raw_first) or pd.isna(raw_resolved)):
            status, interval = "missing", None
        elif pd.isna(first_at) or pd.isna(resolved_at):
            status, interval = "invalid_timestamp", None
        else:
            interval = (resolved_at - first_at).total_seconds() / 3600
            if interval < 0:
                status, interval = "negative", None
            else:
                status = "valid"
        statuses.append(status)
        hours.append(interval)
    result["post_response_hours"] = hours
    result["interval_status"] = statuses
    return result


def grouped_bottlenecks(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate all non-empty channel/priority/type combinations with reconciled counts."""
    _require_sanitized_customer(frame, set(GROUP_COLUMNS) | {"Ticket Status",
                                                             "First Response Time",
                                                             "Time to Resolution"})
    data = frame if {"post_response_hours", "interval_status"} <= set(frame) \
        else add_operational_fields(frame)
    rows: list[dict[str, object]] = []
    for size in range(1, len(GROUP_COLUMNS) + 1):
        for dimensions in combinations(GROUP_COLUMNS, size):
            grouper: str | list[str] = dimensions[0] if len(dimensions) == 1 else list(dimensions)
            for keys, group in data.groupby(grouper, dropna=False, sort=True):
                key_values = (keys,) if len(dimensions) == 1 else keys
                values = group.loc[group["interval_status"].eq("valid"),
                                   "post_response_hours"].astype(float)
                row: dict[str, object] = {
                    "grouping": "+".join(dimensions),
                    **{column: None for column in GROUP_COLUMNS},
                    **dict(zip(dimensions, key_values, strict=True)),
                    "n_total": int(len(group)),
                    "n_eligible": int(len(values)),
                    "n_excluded": int(len(group) - len(values)),
                }
                for status in INTERVAL_STATUSES[1:]:
                    row[f"excluded_{status}"] = int(group["interval_status"].eq(status).sum())
                ci_low, ci_high = median_confidence_interval(values)
                row.update({
                    "median_hours": _finite(values.median()) if len(values) else None,
                    "median_ci95_low": ci_low,
                    "median_ci95_high": ci_high,
                    "q1_hours": _finite(values.quantile(0.25)) if len(values) else None,
                    "q3_hours": _finite(values.quantile(0.75)) if len(values) else None,
                    "iqr_hours": _finite(values.quantile(0.75) - values.quantile(0.25))
                    if len(values) else None,
                    "support_status": (
                        "supported" if len(values) >= MIN_WASTE_SUPPORT
                        else "exploratory" if len(values) else "unavailable"
                    ),
                    "interval_name": "post_response_hours",
                    "first_response_observable": False,
                    "total_resolution_observable": False,
                })
                rows.append(row)
    report = pd.DataFrame(rows)
    if report.empty:
        return pd.DataFrame(columns=BOTTLENECK_COLUMNS)
    report["rank_worst"] = (
        report.groupby("grouping")["median_hours"]
        .rank(method="min", ascending=False).astype("Int64")
    )
    return report.loc[:, BOTTLENECK_COLUMNS].sort_values(
        ["grouping", "rank_worst", "n_eligible"], ascending=[True, True, False],
        na_position="last",
    ).reset_index(drop=True)


def recoverable_excess_hours(frame: pd.DataFrame) -> pd.DataFrame:
    """Estimate a non-negative observed proxy, never realized savings."""
    _require_sanitized_customer(frame, {"target", "Ticket Priority", "Ticket Status",
                                        "First Response Time", "Time to Resolution"})
    data = frame if {"post_response_hours", "interval_status"} <= set(frame) \
        else add_operational_fields(frame)
    rows = []
    for (ticket_type, priority), group in data.groupby(
        ["target", "Ticket Priority"], dropna=False, sort=True
    ):
        values = group.loc[group["interval_status"].eq("valid"),
                           "post_response_hours"].astype(float)
        supported = len(values) >= MIN_WASTE_SUPPORT
        median = _finite(values.median()) if supported else None
        excess = _finite((values - float(median)).clip(lower=0).sum()) if supported else None
        rows.append({
            "target": ticket_type,
            "Ticket Priority": priority,
            "eligible_n": int(len(values)),
            "peer_median_hours": median,
            "observed_excess_hours": excess,
            "status": "supported" if supported else "insufficient_support",
            "evidence_kind": "observed_proxy",
            "realized_savings": False,
        })
    report = pd.DataFrame(rows)
    if report.empty:
        return pd.DataFrame(columns=WASTE_COLUMNS)
    supported = report["status"].eq("supported")
    total = report.loc[supported, "observed_excess_hours"].sum()
    report["rank_excess"] = pd.Series(pd.NA, index=report.index, dtype="Int64")
    report.loc[supported, "rank_excess"] = (
        report.loc[supported, "observed_excess_hours"]
        .rank(method="min", ascending=False).astype("Int64")
    )
    report["share_of_supported_excess"] = None
    if total > 0:
        report.loc[supported, "share_of_supported_excess"] = (
            report.loc[supported, "observed_excess_hours"] / total
        )
    return report.loc[:, WASTE_COLUMNS].sort_values(
        ["rank_excess", "target", "Ticket Priority"], na_position="last"
    ).reset_index(drop=True)


def _signal_status(baseline_mae: float, ridge_mae: float) -> tuple[str, float]:
    if baseline_mae <= 0:
        improvement = 0.0
    else:
        improvement = (baseline_mae - ridge_mae) / baseline_mae
    status = "supported" if improvement + 1e-12 >= MIN_MAE_IMPROVEMENT \
        else "no_reliable_signal"
    return status, improvement


def _univariate_effects(data: pd.DataFrame) -> tuple[dict[str, object], ...]:
    effects: list[dict[str, object]] = []
    rating = "Customer Satisfaction Rating"
    for feature in GROUP_COLUMNS:
        for level, group in data.groupby(feature, dropna=False, sort=True):
            effects.append({
                "feature": feature,
                "level": None if pd.isna(level) else str(level),
                "n": int(len(group)),
                "mean_rating": _finite(group[rating].mean()),
                "median_rating": _finite(group[rating].median()),
                "association_metric": "group_rating",
                "association_value": None,
                "evidence_kind": "univariate_association",
            })
    pair = data[[rating, "post_response_hours"]].dropna()
    correlation = None
    if len(pair) >= MIN_SATISFACTION_SUPPORT:
        correlation = _finite(
            pair[rating].rank(method="average").corr(
                pair["post_response_hours"].rank(method="average")
            )
        )
    effects.append({
        "feature": "post_response_hours", "level": None, "n": int(len(pair)),
        "mean_rating": None, "median_rating": None,
        "association_metric": "spearman_rank_correlation",
        "association_value": correlation,
        "evidence_kind": "univariate_association",
    })
    return tuple(effects)


def satisfaction_associations(frame: pd.DataFrame) -> SatisfactionReport:
    """Compare fold-local Ridge preprocessing with a median baseline."""
    required = set(GROUP_COLUMNS) | {"Customer Satisfaction Rating", "satisfaction_status",
                                    "Ticket Status", "First Response Time",
                                    "Time to Resolution"}
    _require_sanitized_customer(frame, required)
    data = frame if {"post_response_hours", "interval_status"} <= set(frame) \
        else add_operational_fields(frame)
    valid = data.loc[data["satisfaction_status"].eq("valid")].copy()
    valid["Customer Satisfaction Rating"] = pd.to_numeric(
        valid["Customer Satisfaction Rating"], errors="coerce"
    )
    valid = valid.loc[valid["Customer Satisfaction Rating"].between(1, 5)]
    missing = int(data["satisfaction_status"].eq("missing").sum())
    invalid = int(data["satisfaction_status"].eq("invalid").sum())
    effects = _univariate_effects(valid)
    limitation = (
        "Apenas campos operacionais estruturados foram usados; avaliações ausentes ou inválidas "
        "podem introduzir viés de seleção e associações não demonstram causalidade."
    )
    if len(valid) < MIN_SATISFACTION_SUPPORT:
        return SatisfactionReport(
            "insufficient_support", len(data), len(valid), missing, invalid,
            len(data) - len(valid), effects, None, None, None, None, None,
            "Amostra válida insuficiente; nenhum sinal multivariado foi estimado.", limitation,
        )

    feature_columns = [*GROUP_COLUMNS, "post_response_hours"]
    x = valid[feature_columns]
    y = valid["Customer Satisfaction Rating"].astype(float)
    categorical = list(GROUP_COLUMNS)
    numeric = ["post_response_hours"]
    folds = min(5, len(valid))
    splitter = KFold(n_splits=folds, shuffle=True, random_state=42)
    baseline_scores: list[float] = []
    ridge_scores: list[float] = []
    retained: list[tuple[object, pd.DataFrame, pd.Series]] = []
    interval_feature_used_folds = 0
    for train_index, held_index in splitter.split(x):
        x_train, x_held = x.iloc[train_index], x.iloc[held_index]
        y_train, y_held = y.iloc[train_index], y.iloc[held_index]
        baseline = DummyRegressor(strategy="median").fit(x_train, y_train)
        transformers = [
            ("categorical", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                          OneHotEncoder(handle_unknown="ignore")), categorical),
        ]
        # An all-missing interval is absence of evidence, not an observed zero.
        if x_train["post_response_hours"].notna().any():
            transformers.append(
                ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
                 numeric)
            )
            interval_feature_used_folds += 1
        preprocessing = ColumnTransformer(transformers)
        ridge = make_pipeline(preprocessing, Ridge(alpha=1.0)).fit(x_train, y_train)
        baseline_scores.append(float(mean_absolute_error(y_held, baseline.predict(x_held))))
        ridge_scores.append(float(mean_absolute_error(y_held, ridge.predict(x_held))))
        retained.append((ridge, x_held, y_held))
    baseline_mae = float(np.mean(baseline_scores))
    ridge_mae = float(np.mean(ridge_scores))
    status, improvement = _signal_status(baseline_mae, ridge_mae)
    importance = None
    if status == "supported":
        values = {feature: [] for feature in feature_columns}
        for fold_number, (ridge, x_held, y_held) in enumerate(retained):
            result = permutation_importance(
                ridge, x_held, y_held, scoring="neg_mean_absolute_error", n_repeats=5,
                random_state=42 + fold_number,
            )
            for feature, value in zip(feature_columns, result.importances_mean, strict=True):
                values[feature].append(float(value))
        importance = {feature: float(np.mean(scores)) for feature, scores in values.items()}
    conclusion = (
        "Ridge superou o baseline em pelo menos 2%; importâncias são associações em folds "
        "retidos, não causas."
        if status == "supported" else
        "Ridge não superou o baseline de mediana em pelo menos 2%; sem sinal confiável."
    )
    return SatisfactionReport(
        status, len(data), len(valid), missing, invalid, len(data) - len(valid), effects,
        {"strategy": "KFold(shuffle=True, random_state=42)", "folds": folds,
         "preprocessing": "imputation, scaling and one-hot fitted inside each fold",
         "interval_feature_used_folds": interval_feature_used_folds,
         "baseline_fold_mae": baseline_scores, "ridge_fold_mae": ridge_scores},
        baseline_mae, ridge_mae, improvement, importance, conclusion, limitation,
    )


def operational_summary(frame: pd.DataFrame) -> OperationalSummary:
    data = frame if {"post_response_hours", "interval_status"} <= set(frame) \
        else add_operational_fields(frame)
    satisfaction = satisfaction_associations(data)
    waste = recoverable_excess_hours(data)
    valid = data.loc[data["interval_status"].eq("valid"), "post_response_hours"].astype(float)
    supported = waste.loc[waste["status"].eq("supported"), "observed_excess_hours"]
    source = frame.attrs.get("source", {})
    quality = source.get("quality", frame.attrs.get("quality", {}))
    has_analysis_rows = bool(len(data))
    return OperationalSummary(
        schema_version=1,
        evidence_kind="historical_observed",
        analysis_scope="customer_structured_operational_all_rows",
        data_version=source.get("data_version"),
        source_rows=source.get("total_rows"),
        sanitized_rows=quality.get("sanitized_rows"),
        representative_rows=None,
        development_rows=len(data),
        valid_intervals=len(valid),
        interval_exclusions={status: int(data["interval_status"].eq(status).sum())
                             for status in INTERVAL_STATUSES[1:]},
        median_post_response_hours=_finite(valid.median()) if len(valid) else None,
        observed_excess_hours=_finite(supported.sum()) if len(supported) else None,
        supported_waste_groups=int(waste["status"].eq("supported").sum()),
        satisfaction_status=satisfaction.status,
        satisfaction_sample=satisfaction.valid_ratings,
        limitations=(
            "post_response_hours mede somente resolução menos primeira resposta; primeira "
            "resposta e resolução total não são observáveis.",
            "Excesso é proxy histórico não negativo, não economia realizada.",
            satisfaction.selection_limitation,
            "O diagnóstico histórico usa todas as linhas estruturadas e permanece separado "
            "dos splits textuais de modelo e recuperação.",
            "Custo e moeda não são observados; qualquer valor financeiro é somente cenário.",
        ),
        status="ready" if has_analysis_rows else "insufficient_support",
        reason=None if has_analysis_rows else "no_structured_operational_rows",
        analysis_rows=len(data),
        source_lane=source.get("lane", frame.attrs.get("lane")),
        text_fields_retained=quality.get("text_fields_retained"),
        cost_observed=False,
    )


def scenario_projection(
    summary: OperationalSummary, assumptions: ScenarioAssumptions
) -> ScenarioResult:
    if not isinstance(summary, OperationalSummary):
        raise ValueError("invalid_scenario:operational_summary")
    annual_hours = (
        assumptions.annual_eligible_volume * assumptions.addressable_share
        * assumptions.minutes_saved / 60
    )
    return ScenarioResult(
        name=assumptions.name,
        annual_eligible_volume=assumptions.annual_eligible_volume,
        addressable_share=float(assumptions.addressable_share),
        minutes_saved=float(assumptions.minutes_saved),
        hourly_cost=float(assumptions.hourly_cost),
        annual_hours=float(annual_hours),
        annual_cost=float(annual_hours * assumptions.hourly_cost),
        evidence_kind="projected",
        historical_data_version=summary.data_version,
    )
