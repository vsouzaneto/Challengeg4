from pathlib import Path
from typing import Any

import pandas as pd


class CrossAnalysis:
    """Pairwise operational analysis for Dataset 1 only.

    This owner never joins Dataset 1 with Dataset 2. Every result is calculated
    from the operational support-ticket dataset selected below.
    """

    DIMENSIONS: dict[str, dict[str, str]] = {
        "channel": {
            "column": "Ticket Channel",
            "label": "Ticket Channel",
        },
        "priority": {
            "column": "Ticket Priority",
            "label": "Ticket Priority",
        },
        "ticket_type": {
            "column": "Ticket Type",
            "label": "Ticket Type",
        },
        "product": {
            "column": "Product Purchased",
            "label": "Product Purchased",
        },
        "subject": {
            "column": "Ticket Subject",
            "label": "Ticket Subject",
        },
    }

    METRICS: dict[str, dict[str, dict[str, Any]]] = {
        "open_pending": {
            "ticket_count": {
                "label": "Ticket Count",
                "kind": "count_all",
                "format": "integer",
                "semantics": "neutral",
                "secondary_label": "Scope share",
                "ranking_direction": "desc",
            },
            "no_first_response": {
                "label": "No First Response",
                "kind": "count_event",
                "format": "integer",
                "semantics": "risk_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
            "pending_customer_response": {
                "label": "Pending Customer Response",
                "kind": "count_event",
                "format": "integer",
                "semantics": "risk_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
            "commercial_loss": {
                "label": "Refund + Cancellation",
                "kind": "count_event",
                "format": "integer",
                "semantics": "risk_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
        },
        "closed": {
            "ticket_count": {
                "label": "Ticket Count",
                "kind": "count_all",
                "format": "integer",
                "semantics": "neutral",
                "secondary_label": "Scope share",
                "ranking_direction": "desc",
            },
            "rating_1_3": {
                "label": "Rating 1–3",
                "kind": "count_event",
                "format": "integer",
                "semantics": "risk_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
            "rating_4_5": {
                "label": "Rating 4–5",
                "kind": "count_event",
                "format": "integer",
                "semantics": "positive_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
            "average_csat": {
                "label": "Average CSAT",
                "kind": "mean",
                "format": "decimal",
                "semantics": "risk_low",
                "secondary_label": "Rated-ticket coverage",
                "ranking_direction": "asc",
            },
            "commercial_loss": {
                "label": "Refund + Cancellation",
                "kind": "count_event",
                "format": "integer",
                "semantics": "risk_high",
                "secondary_label": "Within-combination rate",
                "ranking_direction": "desc",
            },
            "solution_time": {
                "label": "Solution Time · Median",
                "kind": "median",
                "format": "hours",
                "semantics": "risk_high",
                "secondary_label": "Valid-time coverage",
                "ranking_direction": "desc",
            },
        },
    }

    SCOPE_LABELS = {
        "open_pending": "OPEN / PENDING",
        "closed": "CLOSED",
    }

    MIN_RATE_DENOMINATOR = 10
    MIN_CONTINUOUS_SUPPORT = 5

    def __init__(self, raw_dir: Path):
        self.raw_dir = Path(raw_dir)

    def analyze(
        self,
        scope: str,
        dimension_a: str,
        dimension_b: str,
        metric: str,
    ) -> dict[str, Any]:
        validation = self._validate_request(
            scope=scope,
            dimension_a=dimension_a,
            dimension_b=dimension_b,
            metric=metric,
        )

        if validation is not None:
            return validation

        source = (
            self.raw_dir
            / "customer_support_tickets.csv"
        )

        if not source.exists():
            return self._error(
                "dataset_not_found",
                "Operational Dataset 1 was not found.",
            )

        df = pd.read_csv(source)

        required_columns = {
            "Ticket Status",
            self.DIMENSIONS[dimension_a]["column"],
            self.DIMENSIONS[dimension_b]["column"],
        }

        required_columns.update(
            self._metric_columns(metric)
        )

        missing = sorted(
            required_columns
            - set(df.columns)
        )

        if missing:
            return self._error(
                "missing_columns",
                "Required Dataset 1 columns are missing: "
                + ", ".join(missing),
            )

        scoped = self._scope_dataframe(
            df,
            scope,
        )

        column_a = (
            self.DIMENSIONS[
                dimension_a
            ]["column"]
        )

        column_b = (
            self.DIMENSIONS[
                dimension_b
            ]["column"]
        )

        scoped = scoped.copy()

        scoped["_dimension_a"] = (
            scoped[column_a]
            .fillna("(missing)")
            .astype(str)
            .str.strip()
        )

        scoped["_dimension_b"] = (
            scoped[column_b]
            .fillna("(missing)")
            .astype(str)
            .str.strip()
        )

        scoped["_metric"] = (
            self._metric_series(
                scoped,
                metric,
            )
        )

        metric_config = (
            self.METRICS[
                scope
            ][metric]
        )

        scope_tickets = int(
            len(scoped)
        )

        result_rows: list[
            dict[str, Any]
        ] = []

        grouped = scoped.groupby(
            [
                "_dimension_a",
                "_dimension_b",
            ],
            dropna=False,
            sort=False,
        )

        for labels, group in grouped:
            label_a, label_b = labels

            row = self._aggregate_group(
                group=group,
                metric_config=metric_config,
                scope_tickets=scope_tickets,
            )

            row.update({
                "dimension_a_value":
                    str(label_a),

                "dimension_b_value":
                    str(label_b),
            })

            result_rows.append(
                row
            )

        overall = self._aggregate_group(
            group=scoped,
            metric_config=metric_config,
            scope_tickets=scope_tickets,
        )

        ranked = self._ranking(
            rows=result_rows,
            metric_config=metric_config,
        )

        volume_ranking = sorted(
            result_rows,
            key=lambda row: (
                -int(
                    row["tickets"]
                ),
                row[
                    "dimension_a_value"
                ],
                row[
                    "dimension_b_value"
                ],
            ),
        )

        top_rate = self._top_supported_rate(
            rows=result_rows,
            metric_config=metric_config,
        )

        matrix = self._matrix(
            scoped=scoped,
            result_rows=result_rows,
        )

        leader = (
            ranked[0]
            if ranked
            else None
        )

        top_volume = (
            volume_ranking[0]
            if volume_ranking
            else None
        )

        finding = self._finding(
            leader=leader,
            top_rate=top_rate,
            metric_config=metric_config,
        )

        possible_cells = (
            int(
                scoped[
                    "_dimension_a"
                ].nunique(
                    dropna=False
                )
            )
            *
            int(
                scoped[
                    "_dimension_b"
                ].nunique(
                    dropna=False
                )
            )
        )

        return {
            "status": "ready",

            "source":
                source.name,

            "scope": {
                "key": scope,
                "label":
                    self.SCOPE_LABELS[
                        scope
                    ],
                "tickets":
                    scope_tickets,
            },

            "dimensions": {
                "a": {
                    "key": dimension_a,
                    "label":
                        self.DIMENSIONS[
                            dimension_a
                        ]["label"],
                },
                "b": {
                    "key": dimension_b,
                    "label":
                        self.DIMENSIONS[
                            dimension_b
                        ]["label"],
                },
            },

            "metric": {
                "key": metric,
                "label":
                    metric_config[
                        "label"
                    ],
                "kind":
                    metric_config[
                        "kind"
                    ],
                "format":
                    metric_config[
                        "format"
                    ],
                "semantics":
                    metric_config[
                        "semantics"
                    ],
                "secondary_label":
                    metric_config[
                        "secondary_label"
                    ],
                "ranking_direction":
                    metric_config[
                        "ranking_direction"
                    ],
                "total_value":
                    overall[
                        "value"
                    ],
                "valid_count":
                    overall[
                        "metric_count"
                    ],
                "coverage_pct":
                    overall[
                        "coverage_pct"
                    ],
                "secondary_pct":
                    overall[
                        "secondary_pct"
                    ],
            },

            "summary": {
                "scope_tickets":
                    scope_tickets,

                "observed_combinations":
                    int(
                        len(
                            result_rows
                        )
                    ),

                "possible_matrix_cells":
                    possible_cells,

                "leader":
                    leader,

                "top_volume":
                    top_volume,

                "top_supported_rate":
                    top_rate,
            },

            "ranking":
                ranked[:15],

            "volume_ranking":
                volume_ranking[:15],

            "matrix":
                matrix,

            "finding":
                finding,

            "method": {
                "dataset":
                    "Dataset 1",

                "scope_rule":
                    (
                        "Ticket Status is Open or "
                        "Pending Customer Response."
                        if scope
                        == "open_pending"
                        else
                        "Ticket Status is Closed."
                    ),

                "rate_support_rule":
                    (
                        "Rate leaders require at least "
                        f"{self.MIN_RATE_DENOMINATOR} "
                        "valid observations in the combination."
                    ),

                "continuous_support_rule":
                    (
                        "Average/median priority rankings "
                        "require at least "
                        f"{self.MIN_CONTINUOUS_SUPPORT} "
                        "valid observations when available."
                    ),

                "solution_time_rule":
                    (
                        "Solution Time uses only non-negative "
                        "Time to Resolution − First Response Time "
                        "intervals. It is elapsed ticket time, "
                        "not active agent handling time."
                    ),

                "causality":
                    (
                        "Cross Analysis is descriptive. "
                        "Observed concentration does not establish causality."
                    ),
            },

            "available": {
                "dimensions": [
                    {
                        "key": key,
                        "label":
                            value[
                                "label"
                            ],
                    }
                    for key, value
                    in self.DIMENSIONS.items()
                ],

                "metrics": [
                    {
                        "key": key,
                        "label":
                            value[
                                "label"
                            ],
                    }
                    for key, value
                    in self.METRICS[
                        scope
                    ].items()
                ],
            },
        }

    def _validate_request(
        self,
        scope: str,
        dimension_a: str,
        dimension_b: str,
        metric: str,
    ) -> dict[str, Any] | None:
        if scope not in self.METRICS:
            return self._error(
                "invalid_scope",
                "Scope must be open_pending or closed.",
            )

        if dimension_a not in self.DIMENSIONS:
            return self._error(
                "invalid_dimension_a",
                "Unsupported Dimension A.",
            )

        if dimension_b not in self.DIMENSIONS:
            return self._error(
                "invalid_dimension_b",
                "Unsupported Dimension B.",
            )

        if dimension_a == dimension_b:
            return self._error(
                "same_dimension",
                "Dimension A and Dimension B must be different.",
            )

        if metric not in self.METRICS[scope]:
            return self._error(
                "invalid_metric",
                "Metric is not valid for the selected scope.",
            )

        return None

    @staticmethod
    def _error(
        code: str,
        message: str,
    ) -> dict[str, Any]:
        return {
            "status": "error",
            "code": code,
            "message": message,
        }

    @staticmethod
    def _scope_dataframe(
        df: pd.DataFrame,
        scope: str,
    ) -> pd.DataFrame:
        status = (
            df["Ticket Status"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        if scope == "open_pending":
            return df.loc[
                status.isin(
                    [
                        "Open",
                        "Pending Customer Response",
                    ]
                )
            ].copy()

        return df.loc[
            status.eq("Closed")
        ].copy()

    @staticmethod
    def _metric_columns(
        metric: str,
    ) -> set[str]:
        if metric == "no_first_response":
            return {
                "First Response Time",
            }

        if metric == "pending_customer_response":
            return {
                "Ticket Status",
            }

        if metric == "commercial_loss":
            return {
                "Ticket Type",
            }

        if metric in {
            "rating_1_3",
            "rating_4_5",
            "average_csat",
        }:
            return {
                "Customer Satisfaction Rating",
            }

        if metric == "solution_time":
            return {
                "First Response Time",
                "Time to Resolution",
            }

        return set()

    @staticmethod
    def _metric_series(
        df: pd.DataFrame,
        metric: str,
    ) -> pd.Series:
        if metric == "ticket_count":
            return pd.Series(
                1.0,
                index=df.index,
                dtype="float64",
            )

        if metric == "no_first_response":
            first = pd.to_datetime(
                df[
                    "First Response Time"
                ],
                errors="coerce",
            )

            return (
                first.isna()
                .astype(float)
            )

        if metric == "pending_customer_response":
            status = (
                df["Ticket Status"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            return (
                status.eq(
                    "Pending Customer Response"
                )
                .astype(float)
            )

        if metric == "commercial_loss":
            ticket_type = (
                df["Ticket Type"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            return (
                ticket_type.isin(
                    [
                        "Refund request",
                        "Cancellation request",
                    ]
                )
                .astype(float)
            )

        if metric in {
            "rating_1_3",
            "rating_4_5",
        }:
            rating = pd.to_numeric(
                df[
                    "Customer Satisfaction Rating"
                ],
                errors="coerce",
            )

            output = pd.Series(
                float("nan"),
                index=df.index,
                dtype="float64",
            )

            valid = rating.notna()

            if metric == "rating_1_3":
                output.loc[valid] = (
                    rating.loc[valid]
                    .le(3)
                    .astype(float)
                )
            else:
                output.loc[valid] = (
                    rating.loc[valid]
                    .ge(4)
                    .astype(float)
                )

            return output

        if metric == "average_csat":
            return pd.to_numeric(
                df[
                    "Customer Satisfaction Rating"
                ],
                errors="coerce",
            ).astype(float)

        if metric == "solution_time":
            first = pd.to_datetime(
                df[
                    "First Response Time"
                ],
                errors="coerce",
            )

            resolution = pd.to_datetime(
                df[
                    "Time to Resolution"
                ],
                errors="coerce",
            )

            output = pd.Series(
                float("nan"),
                index=df.index,
                dtype="float64",
            )

            valid = (
                first.notna()
                & resolution.notna()
                & resolution.ge(first)
            )

            output.loc[valid] = (
                (
                    resolution.loc[valid]
                    - first.loc[valid]
                )
                .dt.total_seconds()
                .div(3600)
            )

            return output

        raise ValueError(
            "Unsupported metric."
        )

    @classmethod
    def _aggregate_group(
        cls,
        group: pd.DataFrame,
        metric_config: dict[str, Any],
        scope_tickets: int,
    ) -> dict[str, Any]:
        tickets = int(
            len(group)
        )

        kind = metric_config[
            "kind"
        ]

        metric_values = (
            group["_metric"]
            .dropna()
        )

        metric_count = int(
            len(metric_values)
        )

        value: float | int | None
        secondary_pct: float | None

        if kind == "count_all":
            value = tickets
            metric_count = tickets

            secondary_pct = (
                tickets
                / scope_tickets
                * 100
                if scope_tickets
                else 0.0
            )

        elif kind == "count_event":
            value = int(
                metric_values.sum()
            )

            secondary_pct = (
                value
                / metric_count
                * 100
                if metric_count
                else None
            )

        elif kind == "mean":
            value = (
                float(
                    metric_values.mean()
                )
                if metric_count
                else None
            )

            secondary_pct = (
                metric_count
                / tickets
                * 100
                if tickets
                else None
            )

        elif kind == "median":
            value = (
                float(
                    metric_values.median()
                )
                if metric_count
                else None
            )

            secondary_pct = (
                metric_count
                / tickets
                * 100
                if tickets
                else None
            )

        else:
            raise ValueError(
                "Unsupported metric kind."
            )

        coverage_pct = (
            metric_count
            / tickets
            * 100
            if tickets
            else 0.0
        )

        return {
            "tickets":
                tickets,

            "value":
                cls._clean_value(
                    value,
                    metric_config[
                        "format"
                    ],
                ),

            "metric_count":
                metric_count,

            "coverage_pct":
                round(
                    coverage_pct,
                    2,
                ),

            "secondary_pct":
                (
                    round(
                        secondary_pct,
                        2,
                    )
                    if secondary_pct
                    is not None
                    else None
                ),
        }

    @staticmethod
    def _clean_value(
        value: float | int | None,
        format_name: str,
    ) -> float | int | None:
        if value is None:
            return None

        if pd.isna(value):
            return None

        if format_name == "integer":
            return int(
                round(
                    float(value)
                )
            )

        return round(
            float(value),
            4,
        )

    @classmethod
    def _ranking(
        cls,
        rows: list[dict[str, Any]],
        metric_config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        candidates = [
            row
            for row in rows
            if row["value"]
            is not None
        ]

        if metric_config[
            "kind"
        ] in {
            "mean",
            "median",
        }:
            supported = [
                row
                for row in candidates
                if int(
                    row["metric_count"]
                )
                >= cls.MIN_CONTINUOUS_SUPPORT
            ]

            if supported:
                candidates = supported

        reverse = (
            metric_config[
                "ranking_direction"
            ]
            == "desc"
        )

        return sorted(
            candidates,
            key=lambda row: (
                float(
                    row["value"]
                ),
                int(
                    row["tickets"]
                ),
            ),
            reverse=reverse,
        )

    @classmethod
    def _top_supported_rate(
        cls,
        rows: list[dict[str, Any]],
        metric_config: dict[str, Any],
    ) -> dict[str, Any] | None:
        if metric_config[
            "kind"
        ] != "count_event":
            return None

        candidates = [
            row
            for row in rows
            if (
                row[
                    "secondary_pct"
                ]
                is not None
                and int(
                    row[
                        "metric_count"
                    ]
                )
                >= cls.MIN_RATE_DENOMINATOR
            )
        ]

        if not candidates:
            return None

        return sorted(
            candidates,
            key=lambda row: (
                float(
                    row[
                        "secondary_pct"
                    ]
                ),
                int(
                    row[
                        "metric_count"
                    ]
                ),
            ),
            reverse=True,
        )[0]

    @staticmethod
    def _matrix(
        scoped: pd.DataFrame,
        result_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        a_counts = (
            scoped[
                "_dimension_a"
            ]
            .value_counts()
        )

        b_counts = (
            scoped[
                "_dimension_b"
            ]
            .value_counts()
        )

        a_order = [
            str(value)
            for value
            in a_counts.index.tolist()
        ]

        b_order = [
            str(value)
            for value
            in b_counts.index.tolist()
        ]

        lookup = {
            (
                row[
                    "dimension_a_value"
                ],
                row[
                    "dimension_b_value"
                ],
            ):
            row

            for row
            in result_rows
        }

        matrix_rows = []

        numeric_values = []

        for label_a in a_order:
            cells = []

            for label_b in b_order:
                row = lookup.get(
                    (
                        label_a,
                        label_b,
                    )
                )

                if row is None:
                    cell = {
                        "value": None,
                        "tickets": 0,
                        "secondary_pct": None,
                        "metric_count": 0,
                    }
                else:
                    cell = {
                        "value":
                            row[
                                "value"
                            ],

                        "tickets":
                            row[
                                "tickets"
                            ],

                        "secondary_pct":
                            row[
                                "secondary_pct"
                            ],

                        "metric_count":
                            row[
                                "metric_count"
                            ],
                    }

                    if (
                        row["value"]
                        is not None
                    ):
                        numeric_values.append(
                            float(
                                row[
                                    "value"
                                ]
                            )
                        )

                cells.append(
                    cell
                )

            matrix_rows.append({
                "label":
                    label_a,

                "tickets":
                    int(
                        a_counts.get(
                            label_a,
                            0,
                        )
                    ),

                "cells":
                    cells,
            })

        return {
            "columns": [
                {
                    "label":
                        label_b,

                    "tickets":
                        int(
                            b_counts.get(
                                label_b,
                                0,
                            )
                        ),
                }
                for label_b
                in b_order
            ],

            "rows":
                matrix_rows,

            "min_value":
                (
                    round(
                        min(
                            numeric_values
                        ),
                        4,
                    )
                    if numeric_values
                    else None
                ),

            "max_value":
                (
                    round(
                        max(
                            numeric_values
                        ),
                        4,
                    )
                    if numeric_values
                    else None
                ),
        }

    @classmethod
    def _finding(
        cls,
        leader: dict[str, Any] | None,
        top_rate: dict[str, Any] | None,
        metric_config: dict[str, Any],
    ) -> dict[str, Any]:
        if leader is None:
            return {
                "headline":
                    "No supported combination.",

                "detail":
                    "The selected cross-analysis returned no measurable combination.",
            }

        combination = (
            leader[
                "dimension_a_value"
            ]
            + " × "
            + leader[
                "dimension_b_value"
            ]
        )

        metric_label = (
            metric_config[
                "label"
            ]
        )

        value = leader[
            "value"
        ]

        kind = metric_config[
            "kind"
        ]

        if kind == "count_all":
            detail = (
                combination
                + " has the highest observed ticket volume: "
                + f"{int(value)} tickets, "
                + f"{leader['secondary_pct']:.2f}% "
                + "of the selected scope."
            )

        elif kind == "count_event":
            detail = (
                combination
                + " contains the largest observed "
                + metric_label
                + " volume: "
                + f"{int(value)} cases across "
                + f"{leader['tickets']} tickets"
            )

            if (
                leader[
                    "secondary_pct"
                ]
                is not None
            ):
                detail += (
                    ", equivalent to "
                    + f"{leader['secondary_pct']:.2f}% "
                    + "within that combination."
                )
            else:
                detail += "."

            if (
                top_rate is not None
                and top_rate
                is not leader
            ):
                detail += (
                    " Highest supported rate: "
                    + top_rate[
                        "dimension_a_value"
                    ]
                    + " × "
                    + top_rate[
                        "dimension_b_value"
                    ]
                    + " at "
                    + f"{top_rate['secondary_pct']:.2f}% "
                    + f"(n={top_rate['metric_count']})."
                )

        elif kind == "mean":
            detail = (
                combination
                + " has the lowest supported observed "
                + metric_label
                + ": "
                + f"{float(value):.2f}/5 across "
                + f"{leader['metric_count']} rated tickets."
            )

        else:
            detail = (
                combination
                + " has the highest supported observed "
                + metric_label
                + ": "
                + f"{float(value):.2f}h across "
                + f"{leader['metric_count']} valid intervals."
            )

        return {
            "headline":
                combination,

            "detail":
                detail,
        }
