from pyspark.sql import SparkSession

from lead_scorer.spark import SUPPORTED_MAJORS, _java_major, resolve_java_home


def test_resolved_jdk_is_supported() -> None:
    assert _java_major(resolve_java_home()) in SUPPORTED_MAJORS


def test_session_starts_with_test_config(spark: SparkSession) -> None:
    assert spark.range(3).count() == 3
    assert spark.conf.get("spark.sql.shuffle.partitions") == "4"
    assert spark.conf.get("spark.sql.session.timeZone") == "UTC"
