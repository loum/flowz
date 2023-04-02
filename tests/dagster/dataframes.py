"""PyTest plugin that defines sample Spark SQL DataFrames.

"""
from pyspark.sql import DataFrame, SparkSession
import pytest

import dagster.data.factory.dummy  # type: ignore[import]


@pytest.fixture()
def dummy(spark: SparkSession, dummy_count: int) -> DataFrame:
    """Sample Dummy DataFrame."""
    _factory = dagster.data.factory.dummy.Data(dummy_count)

    return spark.createDataFrame(*(_factory.args()))
