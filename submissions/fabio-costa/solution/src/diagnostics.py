from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kruskal


# -----------------------------------------------------------------------------
# OPERATIONAL DIAGNOSTICS — DATASET 1
# -----------------------------------------------------------------------------
class OperationalDiagnostics:
    """Evidence-first operational diagnostics for Dataset 1.

    This module intentionally refuses to manufacture SLA metrics when ticket
    creation timestamps or trustworthy duration fields are unavailable.
    """

    REQUIRED_COLUMNS = {
        "Ticket ID",
        "Ticket Type",
        "Ticket Status",
        "Ticket Priority",
        "Ticket Channel",
        "Customer Satisfaction Rating",
    }

    def __init__(self, raw_dir: Path, annual_context: int = 30_000):
        self.raw_dir = Path(raw_dir)
        self.annual_context = annual_context

    def run(self) -> dict[str, Any]:
        source = self._find_operational_dataset()
        if source is None:
            return {
                "status": "awaiting_data",
                "message": "Operational dataset not found in data/raw/.",
            }

        df = pd.read_csv(source)
        result: dict[str, Any] = {
            "status": "ready",
            "source": source.name,
            "rows": int(len(df)),
            "annual_context": self.annual_context,
            "sample": self._sample_summary(df),
            "scope": self._scope_normalization(df),
            "volume": self._volume_analysis(df),
            "flow": self._flow_analysis(df),
            "bottleneck_combinations": self._bottleneck_combinations(df),
            "satisfaction": self._satisfaction_analysis(df),
            "waste": self._waste_analysis(df),
            "measurement_limits": self._measurement_limits(df),
        }
        return result

    # -------------------------------------------------------------------------
    # SOURCE DISCOVERY
    # -------------------------------------------------------------------------
    def _find_operational_dataset(self) -> Path | None:
        if not self.raw_dir.exists():
            return None
        for path in sorted(self.raw_dir.glob("*.csv")):
            try:
                cols = set(pd.read_csv(path, nrows=0).columns)
            except Exception:
                continue
            if self.REQUIRED_COLUMNS.issubset(cols):
                return path
        return None

    # -------------------------------------------------------------------------
    # SHARED AGGREGATION HELPERS
    # -------------------------------------------------------------------------
    @staticmethod
    def _counts(df: pd.DataFrame, column: str) -> list[dict[str, Any]]:
        total = len(df)
        counts = df[column].fillna("(missing)").value_counts(dropna=False)
        return [
            {
                "label": str(label),
                "count": int(count),
                "pct": round((int(count) / total * 100) if total else 0.0, 2),
            }
            for label, count in counts.items()
        ]

    # -------------------------------------------------------------------------
    # SAMPLE AND SCOPE
    # -------------------------------------------------------------------------
    def _sample_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        status = df["Ticket Status"].astype(str)
        csat = pd.to_numeric(df["Customer Satisfaction Rating"], errors="coerce")
        first = pd.to_datetime(df.get("First Response Time"), errors="coerce")
        resolution = pd.to_datetime(df.get("Time to Resolution"), errors="coerce")

        return {
            "tickets": int(len(df)),
            "closed": int(status.eq("Closed").sum()),
            "open": int(status.eq("Open").sum()),
            "pending_customer": int(status.eq("Pending Customer Response").sum()),
            "csat_available": int(csat.notna().sum()),
            "first_response_available": int(first.notna().sum()),
            "resolution_available": int(resolution.notna().sum()),
        }


    def _scope_normalization(self, df: pd.DataFrame) -> dict[str, Any]:
        observed = int(len(df))
        annual = int(self.annual_context)
        share_pct = round(observed / annual * 100, 2) if annual else 0.0
        avg_daily = round(annual / 365, 2) if annual else 0.0
        equivalent_days = round(observed / annual * 365, 2) if annual else 0.0
        equivalent_weeks = round(equivalent_days / 7, 2) if equivalent_days else 0.0
        equivalent_months = round(observed / (annual / 12), 2) if annual else 0.0

        return {
            "observed_tickets": observed,
            "observed_base_pct": 100.0,
            "annual_context_tickets": annual,
            "relative_to_annual_context_pct": share_pct,
            "annual_average_tickets_per_day": avg_daily,
            "equivalent_volume_days": equivalent_days,
            "equivalent_volume_weeks": equivalent_weeks,
            "equivalent_volume_months": equivalent_months,
            "period_observed": None,
            "interpretation": (
                "The 8,469 tickets represent 100% of the provided and analyzed dataset. The equivalent number of days "
                "is only a volume normalization against the stated scale of 30,000 tickets/year; "
                "it does not represent the actual chronological period covered by the dataset."
            ),
        }

    # -------------------------------------------------------------------------
    # OPERATIONAL VOLUME AND FLOW
    # -------------------------------------------------------------------------
    def _volume_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        by_type = self._counts(df, "Ticket Type")
        by_channel = self._counts(df, "Ticket Channel")
        by_priority = self._counts(df, "Ticket Priority")
        by_status = self._counts(df, "Ticket Status")

        top_two_types = sum(x["count"] for x in by_type[:2]) if by_type else 0
        top_two_types_pct = round(top_two_types / len(df) * 100, 2) if len(df) else 0.0

        return {
            "by_type": by_type,
            "by_channel": by_channel,
            "by_priority": by_priority,
            "by_status": by_status,
            "top_two_types_count": int(top_two_types),
            "top_two_types_pct": top_two_types_pct,
            "interpretation": (
                "Channel, priority, and ticket-type distributions describe the sample mix; "
                "without Created At and reliable duration fields, volume does not establish a time-based bottleneck."
            ),
        }

    @staticmethod
    def _resolution_mask(df: pd.DataFrame) -> pd.Series:
        if "Resolution" not in df.columns:
            return pd.Series(False, index=df.index, dtype=bool)
        values = df["Resolution"]
        return values.notna() & values.astype(str).str.strip().ne("")

    def _flow_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        status = df["Ticket Status"].fillna("(missing)").astype(str).str.strip()
        has_resolution = self._resolution_mask(df)
        closed = status.eq("Closed")
        opened = status.eq("Open")
        pending = status.eq("Pending Customer Response")
        unresolved = ~closed
        first_response = pd.to_datetime(
            df["First Response Time"],
            errors="coerce",
        )

        closed_with_resolution = int((closed & has_resolution).sum())
        closed_without_resolution = int((closed & ~has_resolution).sum())
        non_closed_with_resolution = int((~closed & has_resolution).sum())

        dimensions = {}
        for column in ["Ticket Channel", "Ticket Priority", "Ticket Type"]:
            rows = []
            for label, group in df.groupby(column, dropna=False):
                idx = group.index
                group_status = status.loc[idx]
                group_resolution = has_resolution.loc[idx]
                total = int(len(group))
                group_closed = group_status.eq("Closed")
                group_unresolved = ~group_closed
                rows.append({
                    "label": str(label),
                    "count": total,
                    "pct": round(total / len(df) * 100, 2) if len(df) else 0.0,
                    "open": int(group_status.eq("Open").sum()),
                    "pending": int(group_status.eq("Pending Customer Response").sum()),
                    "closed": int(group_closed.sum()),
                    "unresolved": int(group_unresolved.sum()),
                    "unresolved_pct": round(float(group_unresolved.mean() * 100), 2) if total else 0.0,
                    "closed_with_resolution": int((group_closed & group_resolution).sum()),
                    "closed_without_resolution": int((group_closed & ~group_resolution).sum()),
                })
            rows.sort(key=lambda x: (-x["unresolved_pct"], -x["count"], x["label"]))
            dimensions[column] = rows

        return {
            "snapshot": {
                "open": int(opened.sum()),
                "pending_customer": int(pending.sum()),
                "closed": int(closed.sum()),
                "not_closed": int(unresolved.sum()),
                "not_closed_pct": round(float(unresolved.mean() * 100), 2) if len(df) else 0.0,
                "open_without_first_response": int(
                    (opened & first_response.isna()).sum()
                ),
                "pending_after_first_response": int(
                    (pending & first_response.notna()).sum()
                ),
                "closed_with_resolution": closed_with_resolution,
                "closed_without_resolution": closed_without_resolution,
                "non_closed_with_resolution": non_closed_with_resolution,
            },
            "dimensions": dimensions,
            "interpretation": (
                "The workflow state is a snapshot. Open and Pending identify tickets that are not closed, "
                "but they do not reveal ticket age. Closed without Resolution is handled separately as an operational "
                "completeness issue without assuming that the Resolution field represents solution quality."
            ),
        }

    # -------------------------------------------------------------------------
    # BOTTLENECK COMBINATIONS
    # -------------------------------------------------------------------------
    def _bottleneck_combinations(self, df: pd.DataFrame) -> dict[str, Any]:
        keys = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
        status = df["Ticket Status"].fillna("(missing)").astype(str).str.strip()
        has_resolution = self._resolution_mask(df)
        rows: list[dict[str, Any]] = []

        grouped = df.groupby(keys, dropna=False)
        for labels, group in grouped:
            idx = group.index
            group_status = status.loc[idx]
            group_closed = group_status.eq("Closed")
            total = int(len(group))
            unresolved = int((~group_closed).sum())
            closed = int(group_closed.sum())
            resolution_mask = has_resolution.loc[idx]
            rows.append({
                "channel": str(labels[0]),
                "priority": str(labels[1]),
                "ticket_type": str(labels[2]),
                "tickets": total,
                "open": int(group_status.eq("Open").sum()),
                "pending": int(group_status.eq("Pending Customer Response").sum()),
                "closed": closed,
                "unresolved": unresolved,
                "unresolved_pct": round(unresolved / total * 100, 2) if total else 0.0,
                "closed_with_resolution": int((group_closed & resolution_mask).sum()),
                "closed_without_resolution": int((group_closed & ~resolution_mask).sum()),
            })

        rows.sort(key=lambda x: (-x["unresolved_pct"], -x["tickets"], x["channel"], x["priority"], x["ticket_type"]))

        first_response = pd.to_datetime(
            df["First Response Time"],
            errors="coerce",
        )
        resolution_time = pd.to_datetime(
            df["Time to Resolution"],
            errors="coerce",
        )

        closed = status.eq("Closed")
        comparable = (
            closed
            & first_response.notna()
            & resolution_time.notna()
        )

        interval_hours = (
            resolution_time - first_response
        ).dt.total_seconds() / 3600

        fast_resolution = (
            comparable
            & interval_hours.lt(0)
        )

        rankable = (
            comparable
            & interval_hours.ge(0)
        )

        temporal = df.loc[
            rankable,
            keys,
        ].copy()

        temporal["_interval_hours"] = (
            interval_hours.loc[rankable]
        )

        resolution_rows: list[dict[str, Any]] = []

        for labels, group in temporal.groupby(
            keys,
            dropna=False,
        ):
            values = group["_interval_hours"]

            resolution_rows.append({
                "channel": str(labels[0]),
                "priority": str(labels[1]),
                "ticket_type": str(labels[2]),
                "tickets": int(len(group)),
                "mean_hours": round(
                    float(values.mean()),
                    2,
                ),
                "median_hours": round(
                    float(values.median()),
                    2,
                ),
                "p90_hours": round(
                    float(values.quantile(0.90)),
                    2,
                ),
                "max_hours": round(
                    float(values.max()),
                    2,
                ),
            })

        resolution_rows.sort(
            key=lambda x: (
                -x["median_hours"],
                -x["p90_hours"],
                -x["tickets"],
                x["channel"],
                x["priority"],
                x["ticket_type"],
            )
        )

        ranked_values = temporal[
            "_interval_hours"
        ]

        return {
            "status": "ready",
            "ranking_metric": "unresolved_pct",
            "ranking_label": "Snapshot non-closure rate",
            "resolution_time_status": "blocked",
            "resolution_time_reason": (
                "Dataset 1 has no Created At field, and the First Response/Resolution timestamps "
                "have inconsistent chronology; ranking combinations by resolution time is therefore not defensible."
            ),
            "closed_resolution_time": {
                "status": "derived",
                "provenance": "DERIVED",
                "metric": "post_first_response_to_resolution",
                "analytical_rule": (
                    "Negative intervals are classified as fast-resolution cases "
                    "and excluded from the resolution-time ranking."
                ),
                "valid_pairs": int(
                    comparable.sum()
                ),
                "fast_resolution_assumption": int(
                    fast_resolution.sum()
                ),
                "ranked_tickets": int(
                    rankable.sum()
                ),
                "zero_intervals": int(
                    (
                        comparable
                        & interval_hours.eq(0)
                    ).sum()
                ),
                "positive_intervals": int(
                    (
                        comparable
                        & interval_hours.gt(0)
                    ).sum()
                ),
                "overall_mean_hours": (
                    round(
                        float(ranked_values.mean()),
                        2,
                    )
                    if not ranked_values.empty
                    else None
                ),
                "overall_median_hours": (
                    round(
                        float(ranked_values.median()),
                        2,
                    )
                    if not ranked_values.empty
                    else None
                ),
                "overall_p90_hours": (
                    round(
                        float(
                            ranked_values.quantile(
                                0.90
                            )
                        ),
                        2,
                    )
                    if not ranked_values.empty
                    else None
                ),
                "overall_max_hours": (
                    round(
                        float(ranked_values.max()),
                        2,
                    )
                    if not ranked_values.empty
                    else None
                ),
                "rows": resolution_rows,
            },
            "total_combinations": int(len(rows)),
            "rows": rows,
        }

    # -------------------------------------------------------------------------
    # SATISFACTION ANALYSIS
    # -------------------------------------------------------------------------
    def _satisfaction_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        working = df.copy()
        working["__csat"] = pd.to_numeric(
            working["Customer Satisfaction Rating"], errors="coerce"
        )

        status = (
            working["Ticket Status"]
            .fillna("(missing)")
            .astype(str)
            .str.strip()
        )

        rated = working[
            status.eq("Closed")
            & working["__csat"].notna()
        ].copy()

        if rated.empty:
            return {
                "status": "unavailable",
                "reason": "No observable Closed-ticket CSAT data.",
            }

        analyses: dict[str, Any] = {}
        for column in [
            "Product Purchased",
            "Ticket Subject",
            "Ticket Type",
            "Ticket Channel",
            "Ticket Priority",
        ]:
            if column in rated.columns:
                analyses[column] = self._csat_by_group(
                    rated,
                    column,
                )

        rating_counts = (
            rated["__csat"]
            .value_counts()
            .sort_index()
        )

        dissatisfied = rated["__csat"].le(3)
        satisfied = rated["__csat"].ge(4)

        loss_types = [
            "Refund request",
            "Cancellation request",
        ]

        if "Ticket Type" in rated.columns:
            loss = rated[
                rated["Ticket Type"].isin(
                    loss_types
                )
            ].copy()
        else:
            loss = rated.iloc[0:0].copy()

        loss_dissatisfied = (
            int(loss["__csat"].le(3).sum())
            if len(loss)
            else 0
        )

        loss_satisfied = (
            int(loss["__csat"].ge(4).sum())
            if len(loss)
            else 0
        )

        first = pd.to_datetime(
            rated.get("First Response Time"),
            errors="coerce",
        )

        resolution = pd.to_datetime(
            rated.get("Time to Resolution"),
            errors="coerce",
        )

        solution_hours = (
            resolution - first
        ).dt.total_seconds() / 3600

        temporal_present = solution_hours.notna()
        temporal_negative = (
            temporal_present
            & solution_hours.lt(0)
        )
        temporal_valid = (
            temporal_present
            & solution_hours.ge(0)
        )

        valid_hours = solution_hours[
            temporal_valid
        ]

        low_hours = solution_hours[
            temporal_valid
            & rated["__csat"].le(3)
        ]

        high_hours = solution_hours[
            temporal_valid
            & rated["__csat"].ge(4)
        ]

        def metric_or_none(series, method, *args):
            if series.empty:
                return None
            return round(
                float(
                    getattr(series, method)(*args)
                ),
                4,
            )

        return {
            "status": "ready",
            "rated_tickets": int(len(rated)),
            "coverage_pct": round(
                len(rated) / len(df) * 100,
                2,
            ) if len(df) else 0.0,
            "mean": round(
                float(rated["__csat"].mean()),
                4,
            ),
            "median": round(
                float(rated["__csat"].median()),
                4,
            ),
            "distribution": [
                {
                    "rating": int(rating),
                    "count": int(count),
                }
                for rating, count
                in rating_counts.items()
            ],
            "rating_rule": {
                "dissatisfied_ratings": [1, 2, 3],
                "satisfied_ratings": [4, 5],
                "rating_4": (
                    "Satisfied with improvement opportunity"
                ),
                "rating_5": "Full satisfaction",
            },
            "dissatisfied": {
                "count": int(
                    dissatisfied.sum()
                ),
                "pct": round(
                    float(
                        dissatisfied.mean() * 100
                    ),
                    4,
                ),
            },
            "satisfied": {
                "count": int(
                    satisfied.sum()
                ),
                "pct": round(
                    float(
                        satisfied.mean() * 100
                    ),
                    4,
                ),
            },
            "groups": analyses,
            "commercial_loss": {
                "count": int(len(loss)),
                "pct_closed": round(
                    len(loss) / len(rated) * 100,
                    4,
                ) if len(rated) else 0.0,
                "dissatisfied_count":
                    loss_dissatisfied,
                "dissatisfied_pct": round(
                    loss_dissatisfied
                    / len(loss)
                    * 100,
                    4,
                ) if len(loss) else 0.0,
                "satisfied_count":
                    loss_satisfied,
                "satisfied_pct": round(
                    loss_satisfied
                    / len(loss)
                    * 100,
                    4,
                ) if len(loss) else 0.0,
                "refund_count": int(
                    loss[
                        "Ticket Type"
                    ].eq(
                        "Refund request"
                    ).sum()
                ) if len(loss) else 0,
                "cancellation_count": int(
                    loss[
                        "Ticket Type"
                    ].eq(
                        "Cancellation request"
                    ).sum()
                ) if len(loss) else 0,
            },
            "solution_time": {
                "status": (
                    "constrained"
                    if len(valid_hours)
                    else "unavailable"
                ),
                "valid_count": int(
                    temporal_valid.sum()
                ),
                "negative_excluded": int(
                    temporal_negative.sum()
                ),
                "overall_mean_hours":
                    metric_or_none(
                        valid_hours,
                        "mean",
                    ),
                "overall_median_hours":
                    metric_or_none(
                        valid_hours,
                        "median",
                    ),
                "overall_p90_hours":
                    metric_or_none(
                        valid_hours,
                        "quantile",
                        0.90,
                    ),
                "dissatisfied_mean_hours":
                    metric_or_none(
                        low_hours,
                        "mean",
                    ),
                "dissatisfied_median_hours":
                    metric_or_none(
                        low_hours,
                        "median",
                    ),
                "satisfied_mean_hours":
                    metric_or_none(
                        high_hours,
                        "mean",
                    ),
                "satisfied_median_hours":
                    metric_or_none(
                        high_hours,
                        "median",
                    ),
                "note": (
                    "Solution time is derived from First Response Time "
                    "to Time to Resolution only where the interval is "
                    "non-negative. It is not first-response latency "
                    "because Created At is unavailable."
                ),
            },
            "note": (
                "This analysis uses Closed tickets with observable CSAT. "
                "Ratings 1-3 are treated as unmet expectation / dissatisfaction; "
                "ratings 4-5 indicate satisfaction. Group comparisons are "
                "descriptive associations and do not establish causality."
            ),
        }

    @staticmethod
    def _csat_by_group(rated: pd.DataFrame, column: str) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        samples: list[np.ndarray] = []

        for label, group in rated.groupby(
            column,
            dropna=False,
        ):
            values = (
                group["__csat"]
                .dropna()
                .astype(float)
                .to_numpy()
            )

            if values.size == 0:
                continue

            samples.append(values)

            dissatisfied = int(
                (values <= 3).sum()
            )
            satisfied = int(
                (values >= 4).sum()
            )

            rows.append(
                {
                    "label": str(label),
                    "n": int(values.size),
                    "mean": round(
                        float(values.mean()),
                        4,
                    ),
                    "median": round(
                        float(np.median(values)),
                        4,
                    ),
                    "dissatisfied":
                        dissatisfied,
                    "dissatisfied_pct": round(
                        dissatisfied
                        / values.size
                        * 100,
                        4,
                    ),
                    "satisfied":
                        satisfied,
                    "satisfied_pct": round(
                        satisfied
                        / values.size
                        * 100,
                        4,
                    ),
                }
            )

        rows.sort(
            key=lambda x: (
                -x["dissatisfied_pct"],
                -x["n"],
                x["label"],
            )
        )

        test: dict[str, Any]

        if (
            len(samples) >= 2
            and all(
                len(sample) > 0
                for sample in samples
            )
        ):
            stat, p_value = kruskal(
                *samples
            )

            test = {
                "method":
                    "Kruskal-Wallis",
                "statistic": round(
                    float(stat),
                    6,
                ),
                "p_value": round(
                    float(p_value),
                    8,
                ),
                "significant_005": bool(
                    p_value < 0.05
                ),
            }
        else:
            test = {
                "method":
                    "Kruskal-Wallis",
                "statistic": None,
                "p_value": None,
                "significant_005": False,
            }

        mean_spread = 0.0
        dissatisfaction_spread = 0.0
        dissatisfaction_min = 0.0
        dissatisfaction_max = 0.0

        if rows:
            means = [
                row["mean"]
                for row in rows
            ]

            dissatisfaction_rates = [
                row["dissatisfied_pct"]
                for row in rows
            ]

            mean_spread = (
                max(means)
                - min(means)
            )

            dissatisfaction_min = min(
                dissatisfaction_rates
            )
            dissatisfaction_max = max(
                dissatisfaction_rates
            )

            dissatisfaction_spread = (
                dissatisfaction_max
                - dissatisfaction_min
            )

        return {
            "rows": rows,
            "mean_spread": round(
                float(mean_spread),
                4,
            ),
            "dissatisfaction_min": round(
                float(dissatisfaction_min),
                4,
            ),
            "dissatisfaction_max": round(
                float(dissatisfaction_max),
                4,
            ),
            "dissatisfaction_spread_pp":
                round(
                    float(
                        dissatisfaction_spread
                    ),
                    4,
                ),
            "test": test,
        }

    # -------------------------------------------------------------------------
    # WASTE AND MEASUREMENT LIMITS
    # -------------------------------------------------------------------------

    def _waste_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        status = (
            df["Ticket Status"]
            .fillna("(missing)")
            .astype(str)
            .str.strip()
        )
        ticket_type = (
            df["Ticket Type"]
            .fillna("(missing)")
            .astype(str)
            .str.strip()
        )

        total = int(len(df))

        open_pending = status.isin([
            "Open",
            "Pending Customer Response",
        ])
        pending = status.eq(
            "Pending Customer Response"
        )
        closed = status.eq("Closed")

        empty_time = pd.Series(
            pd.NaT,
            index=df.index,
            dtype="datetime64[ns]",
        )

        first = pd.to_datetime(
            df["First Response Time"]
            if "First Response Time" in df.columns
            else empty_time,
            errors="coerce",
        )

        resolution = pd.to_datetime(
            df["Time to Resolution"]
            if "Time to Resolution" in df.columns
            else empty_time,
            errors="coerce",
        )

        no_first_response = first.isna()

        loss_mask = ticket_type.isin([
            "Refund request",
            "Cancellation request",
        ])

        active_loss = (
            open_pending
            & loss_mask
        )

        closed_loss = (
            closed
            & loss_mask
        )

        waste_mask = (
            open_pending
            | closed_loss
        )

        comparable = (
            first.notna()
            & resolution.notna()
        )

        valid_time = (
            comparable
            & resolution.ge(first)
        )

        negative_time = (
            comparable
            & resolution.lt(first)
        )

        elapsed_hours = (
            resolution[valid_time]
            - first[valid_time]
        ).dt.total_seconds() / 3600

        mean_hours = (
            float(elapsed_hours.mean())
            if not elapsed_hours.empty
            else None
        )

        median_hours = (
            float(elapsed_hours.median())
            if not elapsed_hours.empty
            else None
        )

        p90_hours = (
            float(
                elapsed_hours.quantile(0.90)
            )
            if not elapsed_hours.empty
            else None
        )

        estimated_targets: dict[str, Any] = {}

        if mean_hours is not None:
            for target in [2.0, 1.0]:
                reduction = max(
                    mean_hours - target,
                    0.0,
                )

                estimated_targets[
                    f"target_{int(target)}h"
                ] = {
                    "target_hours": target,
                    "reduction_per_ticket_hours": round(
                        reduction,
                        4,
                    ),
                    "estimated_reduction_ticket_hours": round(
                        reduction
                        * int(open_pending.sum()),
                        2,
                    ),
                }

        def commercial_dimension(
            column: str,
        ) -> list[dict[str, Any]]:
            if column not in df.columns:
                return []

            working = pd.DataFrame({
                "label": (
                    df[column]
                    .fillna("(missing)")
                    .astype(str)
                    .str.strip()
                ),
                "loss": loss_mask.astype(int),
                "active_loss": active_loss.astype(int),
                "closed_loss": closed_loss.astype(int),
            })

            grouped = (
                working
                .groupby(
                    "label",
                    dropna=False,
                )
                .agg(
                    tickets=("loss", "size"),
                    loss_count=("loss", "sum"),
                    active_loss=("active_loss", "sum"),
                    closed_loss=("closed_loss", "sum"),
                )
            )

            grouped["loss_rate_pct"] = (
                grouped["loss_count"]
                / grouped["tickets"]
                * 100
            )

            grouped["recovery_window_pct"] = (
                grouped["active_loss"]
                / grouped["loss_count"].replace(
                    0,
                    float("nan"),
                )
                * 100
            )

            grouped = grouped.sort_values(
                [
                    "loss_rate_pct",
                    "loss_count",
                    "tickets",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )

            return [
                {
                    "label": str(label),
                    "tickets": int(
                        row["tickets"]
                    ),
                    "loss_count": int(
                        row["loss_count"]
                    ),
                    "active_loss": int(
                        row["active_loss"]
                    ),
                    "closed_loss": int(
                        row["closed_loss"]
                    ),
                    "loss_rate_pct": round(
                        float(
                            row["loss_rate_pct"]
                        ),
                        2,
                    ),
                    "recovery_window_pct": round(
                        float(
                            row[
                                "recovery_window_pct"
                            ]
                        ),
                        2,
                    )
                    if pd.notna(
                        row[
                            "recovery_window_pct"
                        ]
                    )
                    else 0.0,
                }
                for label, row
                in grouped.iterrows()
            ]

        product_rows = commercial_dimension(
            "Product Purchased"
        )

        subject_rows = commercial_dimension(
            "Ticket Subject"
        )

        issue_subjects = [
            row
            for row in subject_rows
            if row["label"] not in {
                "Refund request",
                "Cancellation request",
            }
        ]

        unresolved = int(
            open_pending.sum()
        )

        unresolved_pct = (
            round(
                unresolved / total * 100,
                2,
            )
            if total
            else 0.0
        )

        loss_total = int(
            loss_mask.sum()
        )

        active_loss_count = int(
            active_loss.sum()
        )

        closed_loss_count = int(
            closed_loss.sum()
        )

        return {
            "hours_recoverable": None,
            "cost_recoverable": None,
            "quantification_status": (
                "estimated_cost_available"
            ),
            "unresolved_snapshot_count": unresolved,
            "unresolved_snapshot_pct": unresolved_pct,
            "annual_context": self.annual_context,
            "annual_projection_allowed": False,

            "waste": {
                "count": int(
                    waste_mask.sum()
                ),
                "pct_base": round(
                    float(
                        waste_mask.mean() * 100
                    ),
                    2,
                )
                if total
                else 0.0,
                "no_first_response": int(
                    no_first_response.sum()
                ),
                "no_first_response_pct": round(
                    float(
                        no_first_response.mean()
                        * 100
                    ),
                    2,
                )
                if total
                else 0.0,
                "pending_customer": int(
                    pending.sum()
                ),
                "pending_customer_pct": round(
                    float(
                        pending.mean() * 100
                    ),
                    2,
                )
                if total
                else 0.0,
                "open_pending": unresolved,
                "open_pending_pct": (
                    unresolved_pct
                ),
                "closed_refund_cancellation": (
                    closed_loss_count
                ),
                "closed_refund_cancellation_pct": round(
                    closed_loss_count
                    / total
                    * 100,
                    2,
                )
                if total
                else 0.0,
            },

            "time_cost": {
                "classification": "ESTIMATED",
                "valid_closed_intervals": int(
                    valid_time.sum()
                ),
                "negative_intervals_excluded": int(
                    negative_time.sum()
                ),
                "mean_hours": round(
                    mean_hours,
                    4,
                )
                if mean_hours is not None
                else None,
                "median_hours": round(
                    median_hours,
                    4,
                )
                if median_hours is not None
                else None,
                "p90_hours": round(
                    p90_hours,
                    4,
                )
                if p90_hours is not None
                else None,
                "estimate_basis_tickets": unresolved,
                "targets": estimated_targets,
            },

            "commercial_cost": {
                "count": loss_total,
                "pct_base": round(
                    loss_total
                    / total
                    * 100,
                    2,
                )
                if total
                else 0.0,
                "active_count": active_loss_count,
                "active_pct_of_loss": round(
                    active_loss_count
                    / loss_total
                    * 100,
                    2,
                )
                if loss_total
                else 0.0,
                "closed_count": (
                    closed_loss_count
                ),
            },

            "financial_exposure": {
                "top_products": (
                    product_rows[:5]
                ),
                "top_issue_subjects": (
                    issue_subjects[:5]
                ),
            },

            "recoverable_waste": {
                "operational_count": unresolved,
                "operational_pct_base": (
                    unresolved_pct
                ),
                "commercial_active_count": (
                    active_loss_count
                ),
                "commercial_active_pct_of_loss": round(
                    active_loss_count
                    / loss_total
                    * 100,
                    2,
                )
                if loss_total
                else 0.0,
            },

            "reason": (
                "Waste is quantified from the observed "
                "workflow snapshot. Time cost is estimated "
                "from the valid Closed post-response "
                "baseline using a redesigned 1–2 hour target."
            ),

            "next_measurement": (
                "The redesigned prototype will capture "
                "created_at, first_response_at, follow_up_at, "
                "assigned_at, and resolved_at for direct "
                "lifecycle measurement."
            ),
        }

    @staticmethod
    def _measurement_limits(df: pd.DataFrame) -> dict[str, Any]:
        created_at_present = any(
            str(c).strip().lower().replace("_", " ") in {"created at", "ticket created at", "created"}
            for c in df.columns
        )
        first = pd.to_datetime(df.get("First Response Time"), errors="coerce")
        resolution = pd.to_datetime(df.get("Time to Resolution"), errors="coerce")
        mask = first.notna() & resolution.notna()
        comparable = int(mask.sum())
        negative = int((resolution[mask] < first[mask]).sum()) if comparable else 0

        same_seconds = 0
        if comparable:
            same_seconds = int(
                (
                    first[mask].dt.second.to_numpy()
                    == resolution[mask].dt.second.to_numpy()
                ).sum()
            )

        return {
            "created_at_present": created_at_present,
            "comparable_response_resolution": comparable,
            "resolution_before_response": negative,
            "resolution_before_response_pct": round(negative / comparable * 100, 2) if comparable else 0.0,
            "same_second_component": same_seconds,
            "same_second_component_pct": round(same_seconds / comparable * 100, 2) if comparable else 0.0,
            "sla_raw_allowed": False,
        }
