"""Common DAG build components.

"""
import os
import datetime
import pendulum


class DagPrimer:
    """Common components that can get your DAGs running with minimal fuss.

    .. attribute:: dag_name

    .. attribute:: department

    .. attribute:: airflow_env_variable

    .. attribute:: default_args

    """
    def __init__(self,
                 dag_name: str,
                 department: str = 'dept',
                 airflow_env_variable: str = 'AIRFLOW_CUSTOM_ENV',
                 default_args: dict = None,
                 **kwargs):
        """
        *dag_name* and *department* form the :attr:`dag_id` that presents
        in the Airflow dashboard.

        *department* organisation/department/team delimiter to categorise DAG ID

        *airflow_env_variable* is the name used in the Airflow infrustructure
        environment that determines the instance context.  For example,
        ``local``, ``development`` and ``production``.  Environment naming
        rules are not enforced.

        *default_args* is a dictionary of default parameters to be used as
        constructor keyword parameters when initialising operators

        *kwargs* remaining parameters should represent configuration items to
        :class:`airflow.models.dag.DAG`

        """
        self.__dag_name = dag_name
        self.__department = department
        self.__airflow_env_variable = airflow_env_variable
        self.__default_args = default_args
        self.__kwargs = kwargs or {}

    @property
    def dag_name(self):
        """:attr:`dag_name`
        """
        return self.__dag_name

    @property
    def department(self):
        """:attr:`department`
        """
        return self.__department

    @property
    def airflow_env_variable(self):
        """:attr:`airflow_env_variable`
        """
        return self.__airflow_env_variable

    @property
    def dag_id(self):
        """:attr:`dag_id`
        """
        return f'{self.department}_{self.dag_name}_{self.get_env}'.upper()

    @property
    def default_args(self):
        """Possible DAG ``default_args`` that we may wish to override.

        """
        defaults = {
            'owner': 'airflow',
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 2,
            'retry_delay': datetime.timedelta(minutes=5),
        }
        if self.__default_args:
            defaults.update(self.__default_args)

        return defaults

    @property
    def default_dag_properties(self):
        """Provide sane DAG parameter defaults.
        """
        return {
            'schedule_interval': None,
            'start_date': DagPrimer.derive_start_date(),
            'catchup': False,
        }

    @property
    def dag_properties(self):
        """Argument to initialise the DAG.
        """
        return {**(self.default_dag_properties), **(self.__kwargs)}

    @property
    def get_env(self) -> str:
        """Return current environement name.
        """
        return os.environ.get(self.airflow_env_variable, 'local').upper()

    @staticmethod
    def derive_start_date(timezone='Australia/Melbourne') -> datetime:
        """Define the DAG start date.

        Supported date formats are `%Y-%m-%d`.

        If no date is identified in the `CONFIG` then date defaults
        to the first day of the current year.

        Returns:
            a :mod:`datetime` object representing the DAG start date

        """
        def current_year():
            return datetime.datetime.now().year

        local_tz = pendulum.timezone(timezone)

        _dt = datetime.datetime(current_year(), 1, 1, tzinfo=local_tz)

        return _dt
