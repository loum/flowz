"""A do-nothing Dummy Operator driven by Airflow Variables.

"""
from typing import Text
from operators.parameterised_operator import ParameterisedOperator

from dagster.decorators import dry_run


class DoNothingOperator(ParameterisedOperator):
    """Not much to see here ...

    """
    ui_color = '#bee0ec'
    ui_fgcolor = '#000000'

    def __init__(self, var_01: Text, *args, var_02: Text = None, **kwargs) -> None:
        """
            .. attribute:: var_01

            .. attribute:: var_02

        """
        super().__init__(*args, **kwargs)

        self.__var_01: Text = var_01
        self.__var_02: Text = var_02 or self.get_param('var_02', nullable=False)

    @property
    def var_01(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__var_01

    @property
    def var_02(self) -> Text: # pylint: disable=missing-function-docstring
        return self.__var_02

    @dry_run
    def execute(self, context) -> Text:
        """Execute the task to do nothing.

        Provides a token return value which is simply the task's ID.

        """
        super().execute(context)

        self.log.info('"%s": Doing nothing ... "%s"...', self.task_id, self.task_id)

        return self.task_id
