"""Local Apache Spark Context Apache Airflow hook via PySpark.

"""
from typing import Dict, Optional, Text, cast

from pyspark import SparkConf
from pyspark.sql import SparkSession

from airflow.hooks.base import BaseHook
from airflow.models.connection import Connection

import dagster.datastore.spark


class LocalSparkContextHook(BaseHook):
    """Local Apache Spark Context hook via PySpark.

    In PySpark, Python and JVM codes live in separate OS processes. PySpark uses Py4J, which is a
    framework that facilitates interoperation between the two languages, to exchange data between
    the Python and the JVM processes.

    When you launch a PySpark job, it starts as a Python process, which then spawns a JVM instance
    and runs some PySpark specific code in it. It then instantiates a Spark session in that JVM,
    which becomes the driver program that connects to Spark.

    Things to note: if your workloads trigger a JVM OOM then increase the `spark.driver.memory`
    (default 1g). As the instance of Spark runs in local mode, setting spark.executor.memory
    will not have any effect as the Worker "lives" within the driver JVM process. Local mode is a
    single JVM.

    """

    def __init__(
        self, *args: Text, conn_id: Text = "local_spark_context_default", **kwargs: Dict
    ):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.conn: Optional[SparkSession] = None

    def get_conn(self) -> SparkSession:
        """Get a SparkContext to a local PySpark instance."""
        if not self.conn:
            conn: Connection = self.get_connection(self.conn_id)

            conf = SparkConf()
            conf.set(
                "spark.driver.memory",
                conn.extra_dejson.get("spark.driver.memory", "1g"),
            )
            conf.set(
                "spark.local.dir", conn.extra_dejson.get("spark.local.dir", "/tmp")
            )
            conf.set("spark.ui.port", cast(Text, conn.port or "4050"))
            conf.set("spark.logConf", conn.extra_dejson.get("spark.logConf", True))
            conf.set(
                "spark.debug.maxToStringFields",
                conn.extra_dejson.get("spark.debug.maxToStringFields", 100),
            )
            conf.set(
                "spark.sql.session.timeZone",
                conn.extra_dejson.get("spark.sql.session.timeZone", "UTC"),
            )

            self.conn = dagster.datastore.spark.spark_session(
                app_name="dagster",
                conf=dagster.datastore.spark.aws_spark_conf(conf=conf),
            )

        return self.conn

    def __del__(self) -> None:
        """Grab the SparkContext (if any) and stop it."""
        if self.conn:
            self.conn.stop()
