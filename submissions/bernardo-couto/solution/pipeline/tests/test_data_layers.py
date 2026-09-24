"""Contracts of the data layers: cleaning, reference counts, joins, point-in-time, leakage."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from lead_scorer.config import RAW_DIR, SNAPSHOT_DATE
from lead_scorer.data import clean, gold
from lead_scorer.data.checks import REFERENCE_COUNTS, DataQualityError, check_silver, expect_unique
from lead_scorer.data.load import (
    Bronze,
    ChecksumMismatchError,
    load_bronze,
    read_checksum_file,
    verify_checksums,
)
from lead_scorer.data.schemas import INGESTED_FROM
from lead_scorer.data.silver import RowLossError, Silver, build_silver, enrich_opportunities
from lead_scorer.jobs.build_features import run

T_JUN = date(2017, 6, 30)
T_SEP = date(2017, 9, 30)


@pytest.fixture(scope="module")
def bronze(spark: SparkSession) -> Bronze:
    return load_bronze(spark, RAW_DIR)


@pytest.fixture(scope="module")
def silver(bronze: Bronze) -> Silver:
    built = build_silver(bronze)
    built.opportunities.cache().count()
    return built


@pytest.fixture(scope="module")
def opps(silver: Silver) -> DataFrame:
    return silver.opportunities


# --- bronze ---------------------------------------------------------------------------------------


def test_checksums_match_and_cover_every_raw_table() -> None:
    digests = verify_checksums(RAW_DIR)
    assert set(digests) >= {"sales_pipeline.csv", "accounts.csv", "products.csv", "sales_teams.csv"}
    assert all(len(d) == 64 for d in digests.values())


def test_checksum_mismatch_fails(tmp_path: Path) -> None:
    (tmp_path / "SHA256SUMS").write_text("0" * 64 + "  x.csv\n")
    (tmp_path / "x.csv").write_text("a,b\n1,2\n")
    with pytest.raises(ChecksumMismatchError):
        verify_checksums(tmp_path)
    assert read_checksum_file(tmp_path) == {"x.csv": "0" * 64}


def test_bronze_is_schema_explicit_and_stamped(bronze: Bronze) -> None:
    assert bronze.opportunities.count() == REFERENCE_COUNTS["opportunities"]
    assert dict(bronze.opportunities.dtypes)["engage_date"] == "string"  # parsing is silver's job
    assert dict(bronze.opportunities.dtypes)["close_value"] == "double"
    stamps = bronze.opportunities.select(INGESTED_FROM).distinct().collect()
    assert [row[0] for row in stamps] == [bronze.checksums["sales_pipeline.csv"]]


# --- cleaning -------------------------------------------------------------------------------------


def test_cleaning_mappings(spark: SparkSession) -> None:
    df = spark.createDataFrame(
        [("GTXPro", " technolgy "), ("GTX Pro", "Retail"), ("MG Special", None)],
        "product string, sector string",
    )
    out = df.select(
        clean.normalize_product(F.col("product")).alias("product"),
        clean.normalize_sector(F.col("sector")).alias("sector"),
    ).collect()
    assert [r.product for r in out] == ["GTX Pro", "GTX Pro", "MG Special"]
    assert [r.sector for r in out] == ["technology", "retail", None]


def test_trim_strings_turns_blank_into_null(spark: SparkSession) -> None:
    df = spark.createDataFrame([(" a ", ""), ("b", "  ")], "x string, y string")
    rows = clean.trim_strings(df).collect()
    assert [(r.x, r.y) for r in rows] == [("a", None), ("b", None)]


def test_parse_date_iso(spark: SparkSession) -> None:
    df = spark.createDataFrame([("2017-03-01",), (None,)], "d string")
    rows = df.select(clean.parse_date(F.col("d")).alias("d")).collect()
    assert rows[0].d == date(2017, 3, 1) and rows[1].d is None


def test_silver_products_are_canonical_and_sectors_fixed(silver: Silver, opps: DataFrame) -> None:
    pipeline_products = {r[0] for r in opps.select("product").distinct().collect()}
    catalogue = {r[0] for r in silver.products.select("product").distinct().collect()}
    assert pipeline_products == catalogue
    sectors = {r[0] for r in silver.accounts.select("sector").distinct().collect()}
    assert "technology" in sectors and not any(s in clean.SECTOR_MAP for s in sectors)


# --- silver contract ------------------------------------------------------------------------------


def test_reference_counts_and_checks_pass(silver: Silver, bronze: Bronze) -> None:
    counts = check_silver(silver, bronze.opportunities)
    assert counts["opportunities"] == 8_800
    assert counts["open"] == 2_089 and counts["engaging"] == 1_589 and counts["prospecting"] == 500
    assert counts["won"] == 4_238 and counts["lost"] == 2_473
    assert counts["accounts"] == 85 and counts["products"] == 7 and counts["sales_teams"] == 35


def test_no_row_loss_and_flags(silver: Silver, bronze: Bronze, opps: DataFrame) -> None:
    assert opps.count() == 8_800
    assert opps.filter(~F.col("product_matched")).count() == 0
    assert opps.filter(~F.col("agent_matched")).count() == 0
    assert opps.filter(F.col("account").isNull() & F.col("account_known")).count() == 0
    assert opps.filter(F.col("account").isNotNull() & ~F.col("account_known")).count() == 0
    # Left joins must not fan out even if a dimension had duplicate keys.
    dup_products = silver.products.unionByName(silver.products)
    with pytest.raises(RowLossError):
        enrich_opportunities(
            clean.clean_opportunities(bronze.opportunities),
            dup_products,
            silver.accounts,
            silver.sales_teams,
        )


def test_checks_fail_on_bad_stage(spark: SparkSession, silver: Silver, bronze: Bronze) -> None:
    broken = silver.opportunities.withColumn(
        "deal_stage",
        F.when(F.col("opportunity_id") == "1C1I7A6R", "Closed").otherwise(F.col("deal_stage")),
    )
    bad = Silver(silver.accounts, silver.products, silver.sales_teams, broken)
    with pytest.raises(DataQualityError):
        check_silver(bad, bronze.opportunities)


def test_expect_unique_detects_duplicates(spark: SparkSession) -> None:
    df = spark.createDataFrame([(1,), (1,)], "id int")
    with pytest.raises(DataQualityError):
        expect_unique(df, "id", "t")


def test_open_deals_without_account_are_kept(opps: DataFrame) -> None:
    open_deals = gold.open_deals_as_of(opps, SNAPSHOT_DATE)
    n = open_deals.count()
    unknown = open_deals.filter(~F.col("account_known")).count()
    assert n == 2_089
    assert 0.66 < unknown / n < 0.70  # ~68% of open deals have no account


# --- gold: point-in-time --------------------------------------------------------------------------


def test_open_deals_definition(opps: DataFrame) -> None:
    open_sep = gold.open_deals_as_of(opps, T_SEP)
    rows = open_sep.select(
        F.min("engage_date"),
        F.max("engage_date"),
        F.min("close_date"),
        F.sum(F.col("has_timeline").cast("int")),  # leakage-ok: test
    ).first()
    assert rows is not None
    assert rows[1] <= T_SEP
    assert rows[2] > T_SEP  # every open deal that has a close_date closed after T
    assert rows[3] == open_sep.count()  # no Prospecting before the snapshot
    assert open_sep.filter(F.col("deal_stage") != "Engaging").count() == 0
    snap = gold.open_deals_as_of(opps, SNAPSHOT_DATE)
    assert snap.filter(~F.col("has_timeline")).count() == 500


def test_history_is_point_in_time(opps: DataFrame) -> None:
    """A deal closed in 2017-10 must not affect history_stats/as_of=2017-09-30."""
    hist_sep = gold.compute_history(opps, T_SEP)
    glob = hist_sep.filter(F.col("dimension") == gold.DIM_GLOBAL).first()
    assert glob is not None
    closed_by_sep = opps.filter(
        F.col("close_date") <= F.lit(T_SEP)
    ).count()  # leakage-ok: test oracle
    assert glob["n"] == closed_by_sep
    assert (
        glob["n"] < opps.filter(F.col("close_date").isNotNull()).count()
    )  # leakage-ok: test oracle

    # A deal engaged after T (and closed in October) was neither closed nor open at T:
    # removing it must leave history_stats/as_of=T byte-identical.
    october = opps.filter(
        (F.col("engage_date") > F.lit(T_SEP))
        & (F.col("close_date") <= F.lit(date(2017, 10, 31)))  # leakage-ok: test oracle
    ).limit(1)
    victim = october.first()
    assert victim is not None
    without = opps.filter(F.col("opportunity_id") != victim["opportunity_id"])
    a = gold.compute_history(opps, T_SEP).orderBy("dimension", "key", "key2").collect()
    b = gold.compute_history(without, T_SEP).orderBy("dimension", "key", "key2").collect()
    assert a == b
    # Whereas removing a deal that was open at T changes only the open_load dimension.
    open_victim = (
        gold.open_deals_as_of(opps, T_SEP).filter(F.col("close_date").isNotNull()).first()
    )  # leakage-ok: test
    assert open_victim is not None
    without_open = opps.filter(F.col("opportunity_id") != open_victim["opportunity_id"])
    c = (
        gold.compute_history(without_open, T_SEP)
        .filter(F.col("dimension") != gold.DIM_OPEN_LOAD)
        .orderBy("dimension", "key", "key2")
        .collect()
    )
    assert [r for r in a if r["dimension"] != gold.DIM_OPEN_LOAD] == c


def test_history_stats_shape(opps: DataFrame) -> None:
    hist = gold.compute_history(opps, SNAPSHOT_DATE)
    dims = {r[0]: r[1] for r in hist.groupBy("dimension").count().collect()}
    assert (
        dims[gold.DIM_GLOBAL] == 1 and dims[gold.DIM_PRODUCT] == 7 and dims[gold.DIM_SECTOR] == 10
    )
    assert dims[gold.DIM_SURVIVAL] == len(gold.SURVIVAL_GRID)
    assert dims[gold.DIM_HAZARD14] == gold.HAZARD_MAX_DAY + 1
    hazard = {
        int(r["key"]): r for r in hist.filter(F.col("dimension") == gold.DIM_HAZARD14).collect()
    }
    # Estimated where >= 30 deals were alive, forward-filled above; always a probability.
    assert hazard[0]["n"] >= gold.HAZARD_MIN_ALIVE and hazard[0]["win_rate"] is not None
    assert all(0.0 <= r["win_rate"] <= 1.0 for r in hazard.values())
    assert hazard[gold.HAZARD_MAX_DAY]["n"] < gold.HAZARD_MIN_ALIVE
    last_estimable = max(d for d, r in hazard.items() if r["n"] >= gold.HAZARD_MIN_ALIVE)
    assert hazard[gold.HAZARD_MAX_DAY]["win_rate"] == hazard[last_estimable]["win_rate"]
    glob = hist.filter(F.col("dimension") == gold.DIM_GLOBAL).first()
    assert glob is not None
    assert glob["n"] == 6_711 and glob["wins"] == 4_238
    assert abs(glob["win_rate"] - 0.6315) < 0.001
    surv = {
        int(r["key"]): r for r in hist.filter(F.col("dimension") == gold.DIM_SURVIVAL).collect()
    }
    assert surv[0]["n"] == 6_711  # every closed deal had cycle > 0 days
    assert surv[140]["n"] == 0 and surv[140]["win_rate"] is None  # max observed cycle is 138
    assert surv[91]["win_rate"] > surv[0]["win_rate"]  # surviving is a positive signal


def test_features_have_no_outcome_columns(opps: DataFrame) -> None:
    build = gold.build_gold(opps, T_SEP)
    assert set(build.features.columns).isdisjoint(
        {"close_value", "close_date", "label_won"}
    )  # leakage-ok: test
    assert set(build.features.columns).isdisjoint(gold.OUTCOME_COLUMNS)
    assert {"close_date", "close_value", "label_won"} <= set(
        build.labels.columns
    )  # leakage-ok: labels table


def test_features_one_row_per_open_deal_and_smoothing(opps: DataFrame) -> None:
    build = gold.build_gold(opps, T_SEP)
    feats = build.features
    n_open = gold.open_deals_as_of(opps, T_SEP).count()
    assert feats.count() == n_open == 2_409
    assert feats.select("opportunity_id").distinct().count() == n_open
    assert feats.filter(F.col("deal_stage") != "Engaging").count() == 0  # stage as known at T
    assert feats.filter(F.col("days_in_engaging") < 0).count() == 0
    # Unknown account => account/sector statistics are null, not zero.
    unknown = feats.filter(~F.col("account_known"))
    assert unknown.count() > 0
    assert (
        unknown.filter(
            F.col("win_rate_account").isNotNull() | F.col("n_account").isNotNull()
        ).count()
        == 0
    )
    # Smoothed rates stay strictly inside (0, 1) and shrink towards the global rate for tiny groups.
    row = feats.select(F.min("win_rate_agent_product"), F.max("win_rate_agent_product")).first()
    assert row is not None and row[0] > 0.0 and row[1] < 1.0
    tiny = (
        feats.filter(F.col("n_agent_product") == 0)
        .select("win_rate_agent_product", "global_win_rate")
        .first()
    )
    if tiny is not None:
        assert abs(tiny[0] - tiny[1]) < 1e-9


def test_labels_are_future_outcomes_only(opps: DataFrame) -> None:
    labels = gold.build_labels(opps, T_SEP)
    assert labels.count() == 935
    assert labels.filter(F.col("close_date") <= F.lit(T_SEP)).count() == 0  # leakage-ok: labels
    ids_open = {r[0] for r in gold.open_deals_as_of(opps, T_SEP).select("opportunity_id").collect()}
    assert {r[0] for r in labels.select("opportunity_id").collect()} <= ids_open
    assert gold.build_labels(opps, SNAPSHOT_DATE).count() == 0


def test_history_and_features_in_june(opps: DataFrame) -> None:
    build = gold.build_gold(opps, T_JUN)
    assert build.features.count() == 1_686
    assert build.labels.count() == 970


# --- job: idempotency and manifest ----------------------------------------------------------------


def test_build_features_job_is_idempotent(spark: SparkSession, tmp_path: Path) -> None:
    kwargs = dict(
        spark=spark,
        bronze_dir=tmp_path / "bronze",
        silver_dir=tmp_path / "silver",
        gold_dir=tmp_path / "gold",
    )
    first = run(T_SEP, **kwargs)  # type: ignore[arg-type]
    second = run(T_SEP, **kwargs)  # type: ignore[arg-type]
    assert (
        first.gold_counts
        == second.gold_counts
        == {
            "opportunity_features": 2_409,
            "history_stats": 360 + gold.HAZARD_MAX_DAY + 1,
            "labels": 935,
        }
    )
    part = tmp_path / "gold" / "opportunity_features" / "as_of=2017-09-30"
    assert (part / gold.MANIFEST_NAME).exists()
    manifest = gold.read_manifest("labels", T_SEP, tmp_path / "gold")
    assert manifest["row_counts"] == second.gold_counts
    assert manifest["params"]["prospecting_included"] is False
    assert set(manifest["raw_checksums"]) >= {"sales_pipeline.csv"}
    reread = spark.read.parquet(str(part))
    assert reread.count() == 2_409  # a re-run overwrote (not appended to) the partition


def test_job_rejects_as_of_after_snapshot(spark: SparkSession, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        run(date(2018, 1, 1), spark=spark, gold_dir=tmp_path)
