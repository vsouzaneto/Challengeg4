from collections.abc import Iterator

import pytest
from pyspark.sql import SparkSession

from lead_scorer.spark import get_spark


@pytest.fixture(scope="session")
def spark() -> Iterator[SparkSession]:
    session = get_spark("lead-scorer-tests", for_tests=True)
    yield session
    session.stop()
