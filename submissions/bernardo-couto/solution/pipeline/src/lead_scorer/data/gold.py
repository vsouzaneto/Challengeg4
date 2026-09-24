"""Gold layer: point-in-time tables for scoring, training and evaluation.

Everything here takes an explicit ``as_of`` and uses only information that was known on that
date. Three physically separate tables per ``as_of`` partition:

- ``opportunity_features``: one row per deal open at ``as_of``; deal/product/account/agent
  attributes plus history statistics computed from deals closed **on or before** ``as_of``.
  Never contains ``close_value``, ``close_date`` or a label.
- ``history_stats``: the aggregates themselves (win rate, median cycle, median value ratio,
  survival curve, open load per agent), in long format, for auditing and for the rule layer.
- ``labels``: the later outcome of the deals open at ``as_of`` (evaluation only).

``open_deals_as_of`` defines "open at T": ``engage_date <= T`` and (``close_date > T`` or null).
Prospecting deals have no dates at all, so they can only be considered open at the snapshot;
they are included with ``has_timeline = false`` only when ``as_of >= SNAPSHOT_DATE``.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from lead_scorer.config import GOLD_DIR, SNAPSHOT_DATE, SOLUTION_DIR, partition_dir
from lead_scorer.data.clean import CLOSED_STAGES

# --- parameters (documented in docs/data-quality-report.md) ---------------------------------------

#: Bayesian smoothing strength: pseudo-count of deals pulled towards the global base rate.
SMOOTHING_ALPHA = 20.0
#: Survival grid in days: P(Won | still open after d days) for d in 0..140 step 7.
SURVIVAL_GRID: tuple[int, ...] = tuple(range(0, 141, 7))
#: sales_price buckets for ``price_tier``.
PRICE_TIER_BOUNDS: tuple[float, float] = (2_000.0, 10_000.0)
#: 14-day Won hazard grid: one row per day of age, 0..ZOMBIE_DAYS (scoring-spec section 3.3).
HAZARD_MAX_DAY = 138
HAZARD_HORIZON_DAYS = 14
#: Minimum deals still open at ``d`` for the hazard to be estimated; below it, forward-filled.
HAZARD_MIN_ALIVE = 30

#: Outcome columns that must never appear in ``opportunity_features``.
OUTCOME_COLUMNS: frozenset[str] = frozenset(
    {"close_value", "close_date", "label_won", "cycle_days"}  # leakage-ok: the deny-list itself
)

FEATURES_TABLE = "opportunity_features"
HISTORY_TABLE = "history_stats"
LABELS_TABLE = "labels"
MANIFEST_NAME = "_manifest.json"  # underscore prefix: ignored by Spark/pyarrow directory readers

#: dimensions of ``history_stats``.
DIM_GLOBAL = "global"
DIM_PRODUCT = "product"
DIM_AGENT = "sales_agent"
DIM_SECTOR = "sector"
DIM_AGENT_PRODUCT = "agent_product"
DIM_ACCOUNT = "account"
DIM_SURVIVAL = "survival"
DIM_HAZARD14 = "hazard14"
DIM_OPEN_LOAD = "open_load"

_HISTORY_COLUMNS = (
    "dimension",
    "key",
    "key2",
    "n",
    "wins",
    "win_rate",
    "median_cycle_days",
    "median_value_ratio",
)


class LeakageError(AssertionError):
    """An outcome column reached the feature table."""


# --- open deals -----------------------------------------------------------------------------------


def open_deals_as_of(
    opportunities: DataFrame, as_of: date, snapshot: date = SNAPSHOT_DATE
) -> DataFrame:
    """Deals open at ``as_of`` with the stage **as known on that date**.

    - timeline deals (``has_timeline = true``): ``engage_date <= as_of`` and the deal had not
      closed yet (``close_date > as_of`` or null). Their ``deal_stage`` is rewritten to
      ``Engaging`` because that is what the CRM showed at ``as_of`` (Won/Lost is the future).
    - Prospecting deals (no dates, ``has_timeline = false``): only when ``as_of >= snapshot``.
    """
    as_of_lit = F.lit(as_of)
    close_col = F.col("close_date")  # leakage-ok: used only to decide "still open at as_of"
    timeline = (
        opportunities.filter(F.col("engage_date").isNotNull())
        .filter(F.col("engage_date") <= as_of_lit)
        .filter(close_col.isNull() | (close_col > as_of_lit))
        .withColumn("deal_stage", F.lit("Engaging"))
        .withColumn("has_timeline", F.lit(True))
    )
    if as_of < snapshot:
        return timeline
    prospecting = opportunities.filter(
        F.col("engage_date").isNull() & (F.col("deal_stage") == "Prospecting")
    ).withColumn("has_timeline", F.lit(False))
    return timeline.unionByName(prospecting)


# --- history --------------------------------------------------------------------------------------


def _closed_before(opportunities: DataFrame, as_of: date) -> DataFrame:
    """Closed deals whose outcome was known at ``as_of`` (``close_date <= as_of``)."""
    return (
        opportunities.filter(F.col("deal_stage").isin(list(CLOSED_STAGES)))
        .filter(F.col("close_date").isNotNull())  # leakage-ok: compute_history with as_of
        .filter(F.col("close_date") <= F.lit(as_of))  # leakage-ok: compute_history with as_of
        .withColumn("is_won", (F.col("deal_stage") == "Won").cast("int"))
        .withColumn(
            "cycle_days", F.datediff(F.col("close_date"), F.col("engage_date"))
        )  # leakage-ok: history
        .withColumn(
            "value_ratio",
            F.when(
                (F.col("deal_stage") == "Won") & (F.col("sales_price") > 0),
                F.col("close_value")
                / F.col("sales_price"),  # leakage-ok: Won value ratio for history
            ),
        )
    )


def _group_stats(closed: DataFrame, dimension: str, key: str, key2: str | None = None) -> DataFrame:
    group_cols = [key] + ([key2] if key2 else [])
    df = closed.filter(F.col(key).isNotNull())
    if key2:
        df = df.filter(F.col(key2).isNotNull())
    agg = df.groupBy(*group_cols).agg(
        F.count(F.lit(1)).alias("n"),
        F.sum("is_won").alias("wins"),
        F.expr("percentile(cycle_days, 0.5)").alias("median_cycle_days"),
        F.expr("percentile(value_ratio, 0.5)").alias("median_value_ratio"),
    )
    return agg.select(
        F.lit(dimension).alias("dimension"),
        F.col(key).cast("string").alias("key"),
        (F.col(key2).cast("string") if key2 else F.lit(None).cast("string")).alias("key2"),
        F.col("n").cast("long"),
        F.col("wins").cast("long"),
        (F.col("wins") / F.col("n")).alias("win_rate"),
        F.col("median_cycle_days").cast("double"),
        F.col("median_value_ratio").cast("double"),
    )


def _survival_curve(closed: DataFrame) -> DataFrame:
    """P(Won | deal still open after d days) from closed deals' cycle lengths, d on the grid."""
    grid = closed.sparkSession.createDataFrame([(d,) for d in SURVIVAL_GRID], "d int")
    joined = grid.join(
        closed.select("cycle_days", "is_won"), F.col("cycle_days") > F.col("d"), "left"
    )
    agg = joined.groupBy("d").agg(
        F.count("cycle_days").alias("n"), F.coalesce(F.sum("is_won"), F.lit(0)).alias("wins")
    )
    return agg.select(
        F.lit(DIM_SURVIVAL).alias("dimension"),
        F.col("d").cast("string").alias("key"),
        F.lit(None).cast("string").alias("key2"),
        F.col("n").cast("long"),
        F.col("wins").cast("long"),
        F.when(F.col("n") > 0, F.col("wins") / F.col("n")).alias("win_rate"),
        F.lit(None).cast("double").alias("median_cycle_days"),
        F.lit(None).cast("double").alias("median_value_ratio"),
    )


def _hazard14(closed: DataFrame) -> DataFrame:
    """14-day conditional Won hazard by age, for the urgency component of the score.

    ``hazard14[d] = #{closed: d < cycle <= d + 14 and Won} / #{closed: cycle > d}`` for every
    day ``d`` in 0..HAZARD_MAX_DAY, estimated only where at least HAZARD_MIN_ALIVE deals were
    still open at ``d`` and forward-filled from the last estimable day above that. Rows carry
    ``n`` = deals alive at ``d``, ``wins`` = Won closing within the horizon, ``win_rate`` = hazard.
    Ported from ``analysis/rules.py::hazard14`` (pandas prototype).
    """
    grid = closed.sparkSession.createDataFrame([(d,) for d in range(HAZARD_MAX_DAY + 1)], "d int")
    joined = grid.join(
        closed.select("cycle_days", "is_won"), F.col("cycle_days") > F.col("d"), "left"
    )
    win_soon = F.when(
        (F.col("cycle_days") <= F.col("d") + HAZARD_HORIZON_DAYS) & (F.col("is_won") == 1), 1
    ).otherwise(0)
    agg = joined.groupBy("d").agg(F.count("cycle_days").alias("n"), F.sum(win_soon).alias("wins"))
    raw = F.when(F.col("n") >= HAZARD_MIN_ALIVE, F.col("wins") / F.col("n"))
    ffill_window = Window.orderBy("d").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    hazard = F.last(raw, ignorenulls=True).over(ffill_window)
    return agg.select(
        F.lit(DIM_HAZARD14).alias("dimension"),
        F.col("d").cast("string").alias("key"),
        F.lit(None).cast("string").alias("key2"),
        F.col("n").cast("long"),
        F.col("wins").cast("long"),
        hazard.cast("double").alias("win_rate"),
        F.lit(None).cast("double").alias("median_cycle_days"),
        F.lit(None).cast("double").alias("median_value_ratio"),
    )


def _open_load(open_deals: DataFrame) -> DataFrame:
    agg = open_deals.groupBy("sales_agent").agg(F.count(F.lit(1)).alias("n"))
    return agg.select(
        F.lit(DIM_OPEN_LOAD).alias("dimension"),
        F.col("sales_agent").alias("key"),
        F.lit(None).cast("string").alias("key2"),
        F.col("n").cast("long"),
        F.lit(None).cast("long").alias("wins"),
        F.lit(None).cast("double").alias("win_rate"),
        F.lit(None).cast("double").alias("median_cycle_days"),
        F.lit(None).cast("double").alias("median_value_ratio"),
    )


def compute_history(
    opportunities: DataFrame, as_of: date, snapshot: date = SNAPSHOT_DATE
) -> DataFrame:
    """Long-format history statistics using only deals with ``close_date <= as_of``.

    Rows: ``dimension`` in {global, product, sales_agent, sector, agent_product, account,
    survival, hazard14, open_load}; ``key``/``key2`` identify the group; ``n``, ``wins``,
    ``win_rate``, ``median_cycle_days``, ``median_value_ratio`` (Won only). ``survival`` rows
    have ``key = d`` days and ``win_rate = P(Won | cycle > d)``. ``hazard14`` rows have
    ``key = d`` for every day 0..138 and ``win_rate = P(Won within 14 days | open at d)``
    (see ``_hazard14``). ``open_load`` rows count deals open at ``as_of`` per agent (``n``).
    """
    closed = _closed_before(opportunities, as_of).withColumn("_all", F.lit("all"))
    parts = [
        _group_stats(closed, DIM_GLOBAL, "_all"),
        _group_stats(closed, DIM_PRODUCT, "product"),
        _group_stats(closed, DIM_AGENT, "sales_agent"),
        _group_stats(closed, DIM_SECTOR, "sector"),
        _group_stats(closed, DIM_AGENT_PRODUCT, "sales_agent", "product"),
        _group_stats(closed, DIM_ACCOUNT, "account"),
        _survival_curve(closed),
        _hazard14(closed),
        _open_load(open_deals_as_of(opportunities, as_of, snapshot)),
    ]
    out = parts[0]
    for part in parts[1:]:
        out = out.unionByName(part)
    return out.select(*_HISTORY_COLUMNS)


# --- features -------------------------------------------------------------------------------------


def _smoothed(wins: str, n: str, p0: str, alpha: float = SMOOTHING_ALPHA) -> Any:
    """Bayesian shrinkage ``(wins + alpha*p0) / (n + alpha)``; equals ``p0`` when ``n`` is 0."""
    return (F.coalesce(F.col(wins), F.lit(0)) + F.lit(alpha) * F.col(p0)) / (
        F.coalesce(F.col(n), F.lit(0)) + F.lit(alpha)
    )


def _join_dim(
    features: DataFrame,
    history: DataFrame,
    dimension: str,
    suffix: str,
    left_key: str,
    left_key2: str | None = None,
) -> DataFrame:
    """Left-join one history dimension and add ``n_<s>``, ``win_rate_<s>``, medians."""
    stats = history.filter(F.col("dimension") == dimension).select(
        F.col("key").alias(f"_k_{suffix}"),
        F.col("key2").alias(f"_k2_{suffix}"),
        F.col("n").alias(f"n_{suffix}"),
        F.col("wins").alias(f"_wins_{suffix}"),
        F.col("median_cycle_days").alias(f"median_cycle_{suffix}"),
        F.col("median_value_ratio").alias(f"value_ratio_{suffix}"),
    )
    cond = features[left_key] == stats[f"_k_{suffix}"]
    if left_key2:
        cond = cond & (features[left_key2] == stats[f"_k2_{suffix}"])
    joined = features.join(stats, cond, "left")
    joined = joined.withColumn(f"n_{suffix}", F.coalesce(F.col(f"n_{suffix}"), F.lit(0)))
    joined = joined.withColumn(
        f"win_rate_{suffix}", _smoothed(f"_wins_{suffix}", f"n_{suffix}", "global_win_rate")
    )
    # Unknown key (e.g. account null) => statistics are unknown, not "zero history".
    key_null = F.col(left_key).isNull() | (F.col(left_key2).isNull() if left_key2 else F.lit(False))
    for col in (f"n_{suffix}", f"win_rate_{suffix}"):
        joined = joined.withColumn(col, F.when(key_null, F.lit(None)).otherwise(F.col(col)))
    return joined.drop(f"_k_{suffix}", f"_k2_{suffix}", f"_wins_{suffix}")


def build_opportunity_features(open_deals: DataFrame, history: DataFrame, as_of: date) -> DataFrame:
    """One row per open deal with only information known at ``as_of``; no outcome columns."""
    n_open = open_deals.count()
    as_of_lit = F.lit(as_of)

    base = open_deals.drop(*[c for c in OUTCOME_COLUMNS if c in open_deals.columns]).drop(
        "_ingested_from"
    )
    base = (
        base.withColumn("as_of", as_of_lit)
        .withColumn("days_in_engaging", F.datediff(as_of_lit, F.col("engage_date")))
        .withColumn("engage_month", F.date_format(F.col("engage_date"), "yyyy-MM"))
        .withColumn(
            "price_tier",
            F.when(F.col("sales_price") < PRICE_TIER_BOUNDS[0], "low")
            .when(F.col("sales_price") < PRICE_TIER_BOUNDS[1], "mid")
            .when(F.col("sales_price").isNotNull(), "high"),
        )
        .withColumn("account_age_years", F.lit(as_of.year) - F.col("year_established"))
        .withColumn(
            "_survival_d",
            F.least(F.floor(F.col("days_in_engaging") / 7) * 7, F.lit(SURVIVAL_GRID[-1])).cast(
                "string"
            ),
        )
    )

    global_row = history.filter(F.col("dimension") == DIM_GLOBAL).select(
        F.col("win_rate").alias("global_win_rate"),
        F.col("n").alias("n_global"),
        F.col("median_cycle_days").alias("median_cycle_global"),
    )
    features = base.crossJoin(F.broadcast(global_row))
    if features.count() != n_open:
        # No closed deals before as_of => no global row; keep every deal with null history.
        features = (
            base.withColumn("global_win_rate", F.lit(None).cast("double"))
            .withColumn("n_global", F.lit(0).cast("long"))
            .withColumn("median_cycle_global", F.lit(None).cast("double"))
        )

    features = _join_dim(features, history, DIM_PRODUCT, "product", "product")
    features = _join_dim(features, history, DIM_AGENT, "agent", "sales_agent")
    features = _join_dim(features, history, DIM_SECTOR, "sector", "sector")
    features = _join_dim(
        features, history, DIM_AGENT_PRODUCT, "agent_product", "sales_agent", "product"
    )
    features = _join_dim(features, history, DIM_ACCOUNT, "account", "account")
    features = _join_dim(features, history, DIM_SURVIVAL, "survival", "_survival_d")
    features = features.drop("median_cycle_survival", "value_ratio_survival", "_survival_d")

    load = history.filter(F.col("dimension") == DIM_OPEN_LOAD).select(
        F.col("key").alias("_agent_load"), F.col("n").alias("open_deals_agent")
    )
    features = features.join(load, features["sales_agent"] == load["_agent_load"], "left").drop(
        "_agent_load"
    )
    features = features.withColumn(
        "open_deals_agent", F.coalesce(F.col("open_deals_agent"), F.lit(0))
    )

    ordered = [
        "opportunity_id",
        "as_of",
        "sales_agent",
        "manager",
        "regional_office",
        "agent_matched",
        "product",
        "series",
        "sales_price",
        "price_tier",
        "product_matched",
        "account",
        "account_known",
        "sector",
        "revenue",
        "employees",
        "office_location",
        "year_established",
        "account_age_years",
        "is_subsidiary",
        "subsidiary_of",
        "deal_stage",
        "has_timeline",
        "engage_date",
        "engage_month",
        "days_in_engaging",
    ]
    rest = [c for c in features.columns if c not in ordered]
    features = features.select(*ordered, *rest)

    _assert_features_contract(features, n_open)
    return features


def _assert_features_contract(features: DataFrame, n_open: int) -> None:
    leaked = OUTCOME_COLUMNS & set(features.columns)
    if leaked:
        raise LeakageError(f"outcome columns in opportunity_features: {sorted(leaked)}")
    n = features.count()
    if n != n_open:
        raise AssertionError(f"opportunity_features has {n} rows, expected {n_open} open deals")
    if features.select("opportunity_id").distinct().count() != n:
        raise AssertionError("opportunity_features: duplicated opportunity_id after joins")


# --- labels ---------------------------------------------------------------------------------------


def build_labels(
    opportunities: DataFrame, as_of: date, snapshot: date = SNAPSHOT_DATE
) -> DataFrame:
    """Outcome of deals open at ``as_of`` that closed afterwards (evaluation only).

    Physically separate from the features. Empty at the snapshot (nothing has closed yet).
    """
    open_deals = open_deals_as_of(opportunities, as_of, snapshot).select("opportunity_id")
    outcomes = opportunities.filter(F.col("deal_stage").isin(list(CLOSED_STAGES))).select(
        "opportunity_id",
        (F.col("deal_stage") == "Won").alias("label_won"),
        F.col("close_date"),  # leakage-ok: labels table, separate from features
        F.col("close_value"),  # leakage-ok: labels table, separate from features
        F.datediff(F.col("close_date"), F.lit(as_of)).alias(
            "days_to_close_from_as_of"
        ),  # leakage-ok: labels
    )
    return open_deals.join(outcomes, "opportunity_id", "inner").withColumn("as_of", F.lit(as_of))


# --- writing --------------------------------------------------------------------------------------


@dataclass
class GoldBuild:
    as_of: date
    features: DataFrame
    history: DataFrame
    labels: DataFrame
    row_counts: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, DataFrame]:
        return {
            FEATURES_TABLE: self.features,
            HISTORY_TABLE: self.history,
            LABELS_TABLE: self.labels,
        }


def build_gold(opportunities: DataFrame, as_of: date, snapshot: date = SNAPSHOT_DATE) -> GoldBuild:
    """Open deals -> history -> features (+ labels) for one ``as_of``."""
    open_deals = open_deals_as_of(opportunities, as_of, snapshot)
    history = compute_history(opportunities, as_of, snapshot)
    features = build_opportunity_features(open_deals, history, as_of)
    labels = build_labels(opportunities, as_of, snapshot)
    return GoldBuild(as_of=as_of, features=features, history=history, labels=labels)


def git_sha(repo_dir: Path = SOLUTION_DIR) -> str:
    """Short git SHA of the working tree, or ``unknown`` (e.g. inside the Docker image)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except OSError:
        return "unknown"
    return out.stdout.strip() or "unknown"


def write_gold(build: GoldBuild, gold_dir: Path = GOLD_DIR) -> dict[str, int]:
    """Write each table to ``<gold>/<table>/as_of=YYYY-MM-DD/`` (overwrite); return row counts."""
    counts: dict[str, int] = {}
    for table, df in build.as_dict().items():
        target = partition_dir(gold_dir, table, build.as_of)
        df.coalesce(1).write.mode("overwrite").parquet(str(target))
        counts[table] = df.count()
    build.row_counts.update(counts)
    return counts


def write_manifest(
    build: GoldBuild,
    *,
    raw_checksums: dict[str, str],
    silver_counts: dict[str, int],
    duration_seconds: float,
    spark_version: str,
    gold_dir: Path = GOLD_DIR,
) -> dict[str, Any]:
    """Write ``_manifest.json`` into every gold partition of this ``as_of``; return its content."""
    manifest: dict[str, Any] = {
        "job": "build_features",
        "as_of": build.as_of.isoformat(),
        "snapshot_date": SNAPSHOT_DATE.isoformat(),
        "git_sha": git_sha(),
        "spark_version": spark_version,
        "params": {
            "smoothing_alpha": SMOOTHING_ALPHA,
            "survival_grid_days": list(SURVIVAL_GRID),
            "hazard14": {
                "max_day": HAZARD_MAX_DAY,
                "horizon_days": HAZARD_HORIZON_DAYS,
                "min_alive": HAZARD_MIN_ALIVE,
            },
            "price_tier_bounds": list(PRICE_TIER_BOUNDS),
            "prospecting_included": build.as_of >= SNAPSHOT_DATE,
        },
        "raw_checksums": raw_checksums,
        "silver_counts": silver_counts,
        "row_counts": build.row_counts,
        "feature_columns": build.features.columns,
        "duration_seconds": round(duration_seconds, 2),
    }
    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    for table in build.as_dict():
        (partition_dir(gold_dir, table, build.as_of) / MANIFEST_NAME).write_text(
            payload, encoding="utf-8"
        )
    return manifest


def read_manifest(table: str, as_of: date, gold_dir: Path = GOLD_DIR) -> dict[str, Any]:
    path = partition_dir(gold_dir, table, as_of) / MANIFEST_NAME
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


__all__ = [
    "DIM_HAZARD14",
    "FEATURES_TABLE",
    "HAZARD_MAX_DAY",
    "HISTORY_TABLE",
    "LABELS_TABLE",
    "OUTCOME_COLUMNS",
    "SMOOTHING_ALPHA",
    "SURVIVAL_GRID",
    "GoldBuild",
    "LeakageError",
    "build_gold",
    "build_labels",
    "build_opportunity_features",
    "compute_history",
    "open_deals_as_of",
    "read_manifest",
    "write_gold",
    "write_manifest",
]
