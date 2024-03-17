"""A do-nothing EmptyOperator workflow driven by Airflow Variables.

"""

from operators.parameterised_operator import ParameterisedOperator  # type: ignore[import]
import airflow.utils.context

from dagster.decorators import dry_run


class DoNothingOperator(ParameterisedOperator):
    """Not much to see here ..."""

    ui_color = "#bee0ec"
    ui_fgcolor = "#000000"

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

        self.__var_01: str | None = self.get_param("var_02")
        self.__var_02: str = self.get_param("var_02", nullable=False)

    @property
    def var_01(self) -> str | None:
        """Dummy `var_01` getter."""
        return self.__var_01

    @property
    def var_02(self) -> str:
        """Dummy `var_02` getter."""
        return self.__var_02

    @dry_run
    def execute(self, context: airflow.utils.context.Context) -> str:
        """Execute the task to do nothing.

        Provides a token return value which is simply the task's ID.

        Parameters:
            context. Airflow context.

        Returns:
            ID of the Airflow task under execution.

        """
        super().execute(context)

        self.log.info('"%s": Doing nothing ... "%s"...', self.task_id, self.task_id)

        return self.task_id
