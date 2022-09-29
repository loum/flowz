""":class:`hooks.local_spark_context_hook.LocalSparkContextHook` unit test cases.
"""
import json
import unittest.mock
import pyspark
from airflow.models import Connection
from dagster.plugins.hooks.local_spark_context_hook import LocalSparkContextHook


def test_local_spark_context_hook_init():
    """Initialise a LocalSparkContextHook object.
    """
    # when I initialise a LocalSparkContextHook
    hook = LocalSparkContextHook()

    # I should get a LocalSparkContextHook instance
    msg = 'Object is not a LocalSparkContextHook instance'
    assert isinstance(hook, LocalSparkContextHook), msg


@unittest.mock.patch('airflow.hooks.base.BaseHook.get_connection')
def test_local_spark_context_hook_run(connections):
    """LocalSparkContextHook run.
    """
    # Given a Local Spark Context connection string
    conn_info = {
        'conn_id': 'local_spark_context_default',
        'conn_type': 'spark',
        'port': '4059',
    }
    conn_extra = {
        'spark.driver.memory': '512m',
    }
    conn = Connection(**conn_info)
    conn.set_extra(json.dumps(conn_extra))

    # when I make a connection attempt
    connections.return_value = conn
    hook = LocalSparkContextHook()

    # I should receive a pyspark.SparkContext instance
    msg = 'LocalSparkContextHook connection did not return a pyspark.SparkContext instance'
    assert isinstance(hook.get_conn(), pyspark.SparkContext), msg


@unittest.mock.patch('airflow.hooks.base.BaseHook.get_connection')
def test_spark_session(connections):
    """Access the SparkSession.
    """
    # Given a Local Spark Context connection string
    conn_info = {
        'conn_id': 'local_spark_context_default',
        'conn_type': 'spark',
        'port': '4059',
    }
    conn_extra = {
        'spark.driver.memory': '512m',
    }
    conn = Connection(**conn_info)
    conn.set_extra(json.dumps(conn_extra))

    # when I request a SparkSession
    connections.return_value = conn
    hook = LocalSparkContextHook()
    spark = hook.spark()

    # I should be able to access the PySpark version
    msg = 'SparkSession version error'
    assert spark.version.startswith('3.3'), msg
