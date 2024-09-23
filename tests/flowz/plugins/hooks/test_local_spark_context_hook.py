"""`hooks.local_spark_context_hook.LocalSparkContextHook` unit test cases.

"""

import unittest.mock

from pyspark.sql import SparkSession
from airflow.models import Connection

from flowz.plugins.hooks.local_spark_context_hook import (  # type: ignore[import]
    LocalSparkContextHook,
)


def test_local_spark_context_hook_init() -> None:
    """Initialise a LocalSparkContextHook object."""
    # when I initialise a LocalSparkContextHook
    hook = LocalSparkContextHook()

    # I should get a LocalSparkContextHook instance
    msg = "Object is not a LocalSparkContextHook instance"
    assert isinstance(hook, LocalSparkContextHook), msg


@unittest.mock.patch("airflow.hooks.base.BaseHook.get_connection")
def test_local_spark_context_hook_run(connections: Connection) -> None:
    """LocalSparkContextHook run."""
    # Given a Local Spark Context connection string
    conn = Connection(
        conn_id="local_spark_context_default",
        conn_type="spark",
        port=4059,
    )
    conn.set_extra('{"spark.driver.memory": "512m"}')

    # when I make a connection attempt
    print(f"type(connections): {type(connections)}")
    connections.return_value = conn
    hook = LocalSparkContextHook()

    # I should receive a pyspark.SparkContext instance
    msg = "LocalSparkContextHook connection did not return a pyspark.SparkContext instance"
    assert isinstance(hook.get_conn(), SparkSession), msg


@unittest.mock.patch("airflow.hooks.base.BaseHook.get_connection")
def test_spark_session(connections: Connection) -> None:
    """Access the SparkSession."""
    # Given a Local Spark Context connection string
    conn = Connection(
        conn_id="local_spark_context_default",
        conn_type="spark",
        port=4059,
    )
    conn.set_extra('{"spark.driver.memory": "512m"}')

    # when I request a SparkSession
    connections.return_value = conn
    hook = LocalSparkContextHook()
    spark = hook.get_conn()

    # I should be able to access the PySpark version
    msg = "SparkSession version error"
    assert spark.version.startswith("3.5"), msg
