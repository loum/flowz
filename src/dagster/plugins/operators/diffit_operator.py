"""Diffit Operator.

"""
from typing import Callable, List, Text
import filester
import diffit
import diffit.files
import diffit.reporter
from hooks.local_spark_context_hook import LocalSparkContextHook
from operators.parameterised_operator import ParameterisedOperator
from airflow.exceptions import AirflowFailException

from dagster.decorators import dry_run


class DiffitOperator(ParameterisedOperator):
    """Diffit: Symmetric differences between two Apache Spark DataFrames.

    """
    ui_color = '#e99beb'
    ui_fgcolor = '#000000'

    def __init__(self, *args, reader: Callable = None, **kwargs) -> None:
        """
            .. attribute:: reader

        """
        super().__init__(*args, **kwargs)

        self.__reader: Callable = reader
        self.__left: Text = self.get_param('left', nullable=False)
        self.__right: Text = self.get_param('right', nullable=False)
        self.__outpath: Text = self.get_param('outpath', nullable=False)
        self.__cols_to_drop: List[Text] = self.get_param('cols_to_drop') or []

    @property
    def reader(self) -> Callable: # pylint: disable=missing-function-docstring
        return self.__reader

    @property
    def left(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__left

    @property
    def right(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__right

    @property
    def outpath(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__outpath

    @property
    def cols_to_drop(self) -> List[Text]: # pylint: disable=missing-function-docstring
        return self.__cols_to_drop

    @dry_run
    def execute(self, context) -> None:
        """Create a Diffit job, monitor and report.

        """
        super().execute(context)

        hook = LocalSparkContextHook()
        spark = hook.spark()

        self.log.info('"%s": left source path: "%s"', self.task_name, self.left)
        left = diffit.files.sanitise_columns(self.reader(spark, self.left))
        left.show(truncate=False)
        self.log.info('"%s": right source path: "%s"', self.task_name, self.right)
        right = diffit.files.sanitise_columns(spark.read.parquet(self.right))
        right.show(truncate=False)

        self.log.info('"%s": outpath: "%s"', self.task_name, self.outpath)
        diffs = diffit.reporter.row_level(left, right, self.cols_to_drop)

        filester.create_dir(self.outpath)
        diffs.write.mode('overwrite').parquet(self.outpath)

        if diffs.count() > 0:
            self.log.error('"%s": diffit row-level total exceptions: "%d"',
                           self.task_name, diffs.count())
            diffs.show(truncate=False)
            raise AirflowFailException(f'{self.task_name}: diffit tool detected exceptions')
