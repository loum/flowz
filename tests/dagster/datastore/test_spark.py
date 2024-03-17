"""Spark datastore `dagster.datastore.spark` unit test cases.

"""

from pathlib import Path, PurePath
import json

import pyspark.sql
import pyspark.sql.types
import pytest

import dagster.datastore.spark
import dagster.schema.dummy


def test_parquet_reader(working_dir: str, spark: pyspark.sql.SparkSession) -> None:
    """Read in a custom Parquet file."""
    # Given a SparkSession
    # spark

    # and a path to parquet data
    data = [
        ("James", "", "Smith", "36636", "M", 3000),
        ("Michael", "Rose", "", "40288", "M", 4000),
        ("Robert", "", "Williams", "42114", "M", 4000),
        ("Maria", "Anne", "Jones", "39192", "F", 4000),
        ("Jen", "Mary", "Brown", "", "F", -1),
    ]
    columns = ["firstname", "middlename", "lastname", "dob", "gender", "salary"]
    _df = spark.createDataFrame(data, columns)
    parquet_path = str(PurePath(Path(working_dir)).joinpath("parquet.out"))
    _df.write.parquet(parquet_path)

    # when I read into a Spark SQL DataFrame
    received = dagster.datastore.spark.parquet_reader(spark, parquet_path)

    # then I should receive content
    msg = "Parquet Spark SQL reader DataFrame error"
    assert received.count() == 5, msg


@pytest.mark.parametrize("dummy_count", [100])
def test_parquet_write_read(
    working_dir: str, spark: pyspark.sql.SparkSession, dummy: pyspark.sql.DataFrame
) -> None:
    """Write and then read back in a custom Parquet file."""
    # Given a large, Dummy Spark DataFrame
    # dummy

    # and a target output/source path
    # working_dir

    # when I write out the Dummy Spark DataFrame as Spark Parquet
    dagster.datastore.spark.parquet_writer(dummy, working_dir)

    # and then read back in
    received = dagster.datastore.spark.parquet_reader(spark, working_dir)

    # then I should get a matching count
    expected = 100
    msg = "Large, source Dummy DataFrame error for overridden row count creation"
    assert received.count() == expected, msg


def test_json_reader_multiline(
    working_dir: str, spark: pyspark.sql.SparkSession
) -> None:
    """Read JSON data into a Spark DataFrame: multiline."""
    # Given a SparkSession
    # spark

    # and a path to JSON data
    data = [
        {"dummy_col01": 1, "dummy_col02": "dummy_col02_val01"},
        {"dummy_col01": 1, "dummy_col02": "dummy_col02_val01"},
    ]
    json_path = str(PurePath(Path(working_dir)).joinpath("dummy.json"))
    with open(json_path, mode="w", encoding="utf-8") as _fh:
        json.dump(data, _fh)

    # and a schema
    schema: pyspark.sql.types.StructType = dagster.schema.dummy.schema()

    # when I read in the JSON file
    received: pyspark.sql.DataFrame = dagster.datastore.spark.json_reader(
        spark, source_path=json_path, schema=schema, multiline=True
    )

    # then I should receive an instance of a Spark SQL DataFrame
    msg = "Spark JSON read expected DataFrame"
    assert isinstance(received, pyspark.sql.DataFrame), msg

    # and a row count to match
    msg = "Spark JSON read row count error"
    assert received.count() == 2, msg


def test_json_reader_multiline_false(
    working_dir: str, spark: pyspark.sql.SparkSession
) -> None:
    """Read JSON data into a Spark DataFrame: JSON record per line."""
    # Given a SparkSession
    # spark

    # and a path to line-based JSON data
    data = [
        {"dummy_col01": 1, "dummy_col02": "dummy_col02_val01"},
        {"dummy_col01": 1, "dummy_col02": "dummy_col02_val01"},
    ]
    json_path = str(PurePath(Path(working_dir)).joinpath("dummy.json"))
    with open(json_path, mode="w", encoding="utf-8") as _fh:
        json.dump(data, _fh)

    # and a schema
    schema: pyspark.sql.types.StructType = dagster.schema.dummy.schema()

    # when I read in the JSON file
    received: pyspark.sql.DataFrame = dagster.datastore.spark.json_reader(
        spark, source_path=json_path, schema=schema
    )

    # then I should receive an instance of a Spark SQL DataFrame
    msg = "Spark JSON read expected DataFrame"
    assert isinstance(received, pyspark.sql.DataFrame), msg

    # and a row count to match
    msg = "Spark JSON read row count error"
    assert received.count() == 2, msg
