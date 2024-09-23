"""Primer provides consistent context for your program's workflows.

- `dag_name` and `department` form the `dag_id` that presents in the Airflow dashboard.
- `department` organisation/department/team delimiter to categorise DAG ID.
- `airflow_env_variable` is the name used in the Airflow infrustructure
  environment that determines the instance context. For example,
  `local`, `development` and `production`. Environment naming rules are not enforced.

`kwargs` accepts parameters that are passed into `airflow.models.dag.DAG`.

"""

from typing import Any
import os
import datetime

import pendulum


class Primer:
    """Common components that can get your DAGs running with minimal fuss."""

    def __init__(
        self,
        dag_name: str,
        department: str = "dept",
        airflow_env_variable: str = "AIRFLOW_CUSTOM_ENV",
    ):
        self.__dag_name = dag_name
        self.__department = department
        self.__airflow_env_variable = airflow_env_variable
        self.__default_args = {
            "owner": "airflow",
            "depends_on_past": False,
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 2,
            "retry_delay": datetime.timedelta(minutes=5),
        }
        self.__dag_properties = {
            "schedule_interval": None,
            "start_date": Primer.derive_start_date(),
            "catchup": False,
        }

    @property
    def dag_name(self) -> str:
        """`dag_name` getter."""
        return self.__dag_name

    @property
    def department(self) -> str:
        """`department` getter."""
        return self.__department

    @property
    def airflow_env_variable(self) -> str:
        """`airflow_env_variable` getter."""
        return self.__airflow_env_variable

    @property
    def dag_id(self) -> str:
        """`dag_id` getter."""
        return f"{self.department}_{self.dag_name}_{self.get_env}".upper()

    @property
    def default_args(self) -> dict[str, Any]:
        """The DAG's Operator-specific default arguments."""
        return self.__default_args

    @property
    def dag_properties(self) -> dict[Any, Any]:
        """Provide sane DAG parameter defaults."""
        return self.__dag_properties

    @property
    def get_env(self) -> str:
        """Return current environement name."""
        return os.environ.get(self.airflow_env_variable, "local").upper()

    @staticmethod
    def derive_start_date(timezone: str = "Australia/Melbourne") -> datetime.datetime:
        """Define the DAG start date.

        Supported date formats are `%Y-%m-%d`.

        If no date is identified in the `CONFIG` then date defaults
        to the first day of the current year.

        Parameters:
            timezone: Timezone context.

        Returns:
            `datetime` object representing the DAG start date.

        """

        def current_year() -> int:
            return datetime.datetime.now().year

        local_tz = pendulum.timezone(timezone)  # type: ignore

        _dt = datetime.datetime(current_year(), 1, 1, tzinfo=local_tz)

        return _dt
