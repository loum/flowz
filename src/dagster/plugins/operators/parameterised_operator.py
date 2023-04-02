"""Generic Operator driven by parameters.

"""
from typing import Any, Dict, Optional, Text

from airflow.exceptions import AirflowFailException, AirflowSkipException
from airflow.models import BaseOperator, Variable
import airflow.utils.context


class ParameterisedOperator(BaseOperator):
    """Generic Operator driven by Airflow Variables."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.__task_name: Optional[Text] = kwargs.get("task_id")
        self.__configs: Optional[Dict] = None

        kwargs.update({"trigger_rule": "none_failed"})
        super().__init__(*args, **kwargs)

    @property
    def task_name(self) -> Optional[Text]:
        """Get the name of the DAG task."""
        return self.__task_name

    @property
    def configs(self) -> Optional[Dict]:
        """Get the Airflow variable value for DAG task name."""
        if self.__configs is None and self.task_name is not None:
            self.__configs = Variable.get(
                self.task_name, default_var={}, deserialize_json=True
            )

        return self.__configs

    @property
    def skip_task(self) -> bool:
        """Check if the DAG task is to be skipped."""
        return False if self.configs is None else self.configs.get("skip_task", False)

    def get_param(self, param_name: Text, nullable: bool = True) -> Optional[Any]:
        """Return the parameter defined in `airflow.models.Variable`.

        If `nullable` is set to `False` then the an `airflow.AirflowFailException`
        is raised to fail the task without a re-try. As such, this method should only be
        called from within the Operator's `execute` method.

        Raises an airflow.exceptions.AirflowFailException if parameter is not found
        and `nullable` is set to `False`.

        """
        param = None

        if self.configs is not None:
            param = self.configs.get(param_name)
            if not param and not nullable:
                raise AirflowFailException(
                    f'Parameter "{param_name}" value None but set not-nullable'
                )

        return param

    def execute(self, context: airflow.utils.context.Context) -> Optional[Text]:
        """Base execute for parameterised Operators.

        Validates the `skip_task` setting.

        Returns the name of the task under execution

        """
        self.log.info('"%s": Parameterised task starting ...', self.task_name)

        if self.skip_task:
            raise AirflowSkipException(f'"{self.task_name}: skipping task')

        return self.task_name
