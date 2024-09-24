"""SparkSession as a data source.

"""

from configparser import ConfigParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import ClassVar
import os

from pyspark import SparkConf
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from flowz.logging_config import log
import flowz


@dataclass
class Mode(str, Enum):
    """Spark DataFrame write modes."""

    APPEND: ClassVar[str] = "append"
    ERROR: ClassVar[str] = "error"
    IGNORE: ClassVar[str] = "ignore"
    OVERWRITE: ClassVar[str] = "overwrite"


def spark_conf(app_name: str, conf: SparkConf | None = None) -> SparkConf:
    """Set up the SparkContext with appropriate config for test."""
    if conf is None:
        conf = SparkConf()

    # Common settings.
    conf.setAppName(app_name)
    conf.set("spark.ui.port", "4050")
    conf.set("spark.logConf", "true")
    conf.set("spark.debug.maxToStringFields", "100")
    conf.set("spark.sql.session.timeZone", "UTC")
    conf.set("spark.sql.jsonGenerator.ignoreNullFields", "false")

    return conf


def aws_spark_conf(conf: SparkConf | None = None) -> SparkConf:
    """AWS authentication config.

    Parameters:
        conf: Optional SparkConf to be extended. Otherwise, creates a new SparkConf.

    Returns:
        A SparkConf instance with AWS auth support.

    """
    if conf is None:
        conf = SparkConf()

    conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4")
    conf.set("spark.hadoop.fs.s3a.endpoint", "s3.ap-southeast-2.amazonaws.com")
    conf.set("spark.hadoop.fs.s3a.aws.experimental.input.fadvise", "random")
    aws_path = Path.home().joinpath(".aws", "credentials")
    if aws_path.exists():
        conf.set(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider",
        )
        with open(aws_path, encoding="utf-8") as _fh:
            aws_config = ConfigParser()
            aws_config.read_file(_fh)
            conf.set(
                "spark.hadoop.fs.s3a.access.key",
                aws_config.get("default", "aws_access_key_id"),
            )
            conf.set(
                "spark.hadoop.fs.s3a.secret.key",
                aws_config.get("default", "aws_secret_access_key"),
            )
            conf.set(
                "spark.hadoop.fs.s3a.session.token",
                aws_config.get("default", "aws_session_token"),
            )
    else:
        kms_key_arn = os.environ.get("KMS_KEY_ARN")
        if kms_key_arn:
            conf.set(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.auth.IAMInstanceCredentialsProvider",
            )
            conf.set("spark.hadoop.fs.s3a.server-side-encryption-algorithm", "SSE-KMS")
            conf.set("spark.hadoop.fs.s3a.server-side-encryption.key", kms_key_arn)

    return conf


def spark_session(
    app_name: str = flowz.__app_name__, conf: SparkConf | None = None
) -> SparkSession:
    """SparkSession."""
    return SparkSession.builder.config(
        conf=spark_conf(app_name=app_name, conf=conf)
    ).getOrCreate()


def parquet_writer(
    dataframe: DataFrame, outpath: str, mode: str = Mode.OVERWRITE
) -> None:
    """Write out Spark DataFrame *dataframe* to *outpath* directory as Spark Parquet.

    The write mode is defined by *mode*.

    """
    log.info("Writing Parquet to location: %s", outpath)
    dataframe.write.mode(mode).parquet(outpath)


def parquet_reader(spark: SparkSession, source_path: str) -> DataFrame:
    """Read in Spark Parquet files from *source_path* directory.

    Returns a Spark SQL DataFrame.

    """
    log.info('Reading Parquet data from "%s"', source_path)

    return spark.read.parquet(source_path)


def json_writer(dataframe: DataFrame, outpath: str, mode: str = Mode.OVERWRITE) -> None:
    """Write out Spark DataFrame *dataframe* to *outpath* directory as JSON

    The write mode is defined by *mode*.

    """
    dataframe.write.mode(mode).json(outpath)


def json_reader(
    spark: SparkSession, source_path: str, schema: StructType, multiline: bool = False
) -> DataFrame:
    """Read in JSON files from *source_path* directory.

    Here, we leave nothing to chance. So you must provide a *schema*.

    Returns a Spark SQL DataFrame.

    """
    return (
        spark.read.schema(schema)
        .option("multiline", multiline)
        .option("mode", "FAILFAST")
        .json(source_path)
    )
