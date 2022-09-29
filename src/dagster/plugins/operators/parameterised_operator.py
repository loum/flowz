"""Generic Operator driven by parameters.

"""
from typing import Any, Optional, Text
from airflow.exceptions import AirflowFailException, AirflowSkipException
from airflow.models import BaseOperator, Variable


class ParameterisedOperator(BaseOperator):
    """Generic Operator driven by Airflow Variables.

    """
    def __init__(self, *args, **kwargs) -> None:
        """
            .. attribute:: skip_task

        """
        self.__task_name = kwargs.get('task_id')
        self.__configs = Variable.get(self.__task_name,
                                      default_var={},
                                      deserialize_json=True)

        kwargs.update({'trigger_rule': 'none_failed'})
        super().__init__(*args, **kwargs)

    @property
    def task_name(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__task_name

    @property
    def configs(self) -> Optional[Any]: # pylint: disable=missing-function-docstring
        return self.__configs

    @property
    def skip_task(self) -> bool: # pylint: disable=missing-function-docstring
        return self.configs.get('skip_task', False)

    def get_param(self, param_name: Text, nullable=True) -> Optional[Any]:
        """Return the parameter defined in :class:`airflow.models.Variable`.

        If *nullable* is set to `False` then the an :class:`airflow.AirflowFailException`
        is raised to fail the task without a re-try. As such, this method should only be
        called from within the Operator's `execute` method.

        Raises an airflow.exceptions.AirflowFailException if parameter is not found
        and `nullable` is set to `False`.

        """
        param = self.configs.get(param_name)

        #if not param and not nullable:
        #    raise AirflowFailException(f'Parameter "{param_name}" value None but set not-nullable')

        return param

    def execute(self, context) -> Text:
        """Base execute for parameterised Operators.

        Validates the :attr:`skip_task` setting.

        Returns the name of the task under execution

        """
        self.log.info('"%s": Parameterised task starting ...', self.task_name)

        if not self.configs:
            raise AirflowFailException(f'Task ID "{self.__task_name}" parameter definition '
                                       'not found in airflow.models.Variable')

        if self.skip_task:
            raise AirflowSkipException(f'"{self.task_name}: skipping task')

        return self.task_name
