"""Unit test cases for :class:`dagster.utils.DagPrimer`.
"""
import datetime

from dagster.utils.dagprimer import DagPrimer


def test_dagprimer_init():
    """Initialise a DagPrimer object.
    """
    # Given a DAG load ID
    dag_name = 'sample-staging'

    # and a department
    department = """Department"""

    # when I initialise a DagPrimer object
    _dp = DagPrimer(dag_name=dag_name, department=department)

    # I should get a DagPrimer instance
    msg = 'Object is not a DagPrimer instance'
    assert isinstance(_dp, DagPrimer), msg

    # and the dag_id generates
    msg = 'dag_id error'
    assert _dp.dag_id == 'DEPARTMENT_SAMPLE-STAGING_LOCAL', msg


def test_default_args_override():
    """DagPrimer Operator default_arg override.
    """
    # Given a DAG load name
    dag_name = 'sample-staging'

    # and a department and desc
    department = """Department"""

    # and an overriden Operator parameter
    operator_params = {
        'owner': 'AIRFLOW',
        'retry_delay': datetime.timedelta(minutes=60),
    }

    # when I initialise a DagPrimer object
    _dp = DagPrimer(dag_name=dag_name, department=department, default_args=operator_params)

    # I should get an overriden Operator parameter data structure
    msg = 'Overriden Operator default_args error'
    expected = {
        'owner': 'AIRFLOW',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': datetime.timedelta(minutes=60)
    }
    assert _dp.default_args == expected, msg


def test_dag_params_override():
    """DagPrimer Dag parameter override.
    """
    # Given a DAG load name and description
    dag_name = 'sample-staging'
    description = 'Super-cool DAG'

    # and a department
    department = """Department"""

    # and an overriden Operator parameters
    dag_params = {
        'start_date': datetime.datetime(2020, 1, 1),
        'end_date': datetime.datetime(2021, 12, 31),
        'schedule_interval': '@daily',
    }

    # when I initialise a DagPrimer object
    _dp = DagPrimer(dag_name=dag_name,
                     department=department,
                     description=description,
                     **dag_params)

    # I should get an overriden DAG parameter data structure
    msg = 'Overriden DAG parameter error'
    expected = {
        'catchup': False,
        'description': 'Super-cool DAG',
        'start_date': datetime.datetime(2020, 1, 1),
        'end_date': datetime.datetime(2021, 12, 31),
        'schedule_interval': '@daily',
    }
    assert _dp.dag_properties == expected, msg
