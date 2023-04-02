"""Unit test cases for `dagster.Primer`.
"""
import datetime

from dagster.primer import Primer  # type: ignore[import]


def test_primer_init() -> None:
    """Initialise a Primer object."""
    # Given a DAG load ID
    dag_name = "sample-staging"

    # and a department
    department = "Department"

    # when I initialise a Primer object
    primer = Primer(dag_name=dag_name, department=department)

    # I should get a Primer instance
    msg = "Object is not a Primer instance"
    assert isinstance(primer, Primer), msg

    # and the dag_id generates
    msg = "dag_id error"
    assert primer.dag_id == "DEPARTMENT_SAMPLE-STAGING_LOCAL", msg


def test_default_args_override() -> None:
    """Primer Operator default_arg override."""
    # Given a DAG load name
    dag_name = "sample-staging"

    # and a department and desc
    department = "Department"

    # and an overriden Operator parameter
    operator_params = {
        "owner": "AIRFLOW",
        "retry_delay": datetime.timedelta(minutes=60),
    }

    # when I initialise a Primer object
    primer = Primer(dag_name=dag_name, department=department)
    primer.default_args.update(operator_params)

    # I should get an overriden Operator parameter data structure
    msg = "Overriden Operator default_args error"
    expected = {
        "owner": "AIRFLOW",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 2,
        "retry_delay": datetime.timedelta(minutes=60),
    }
    assert primer.default_args == expected, msg


def test_dag_properties_override() -> None:
    """Primer Dag parameter override."""
    # Given a DAG load name and description
    dag_name = "sample-staging"

    # and a department
    department = "Department"

    # and an overriden Operator parameters
    dag_properties = {
        "start_date": datetime.datetime(2020, 1, 1),
        "end_date": datetime.datetime(2021, 12, 31),
        "schedule_interval": "@daily",
    }

    # when I initialise a Primer object
    primer = Primer(dag_name=dag_name, department=department)
    primer.dag_properties.update(dag_properties)

    # I should get an overriden DAG parameter data structure
    msg = "Overriden DAG parameter error"
    expected = {
        "catchup": False,
        "start_date": datetime.datetime(2020, 1, 1),
        "end_date": datetime.datetime(2021, 12, 31),
        "schedule_interval": "@daily",
    }
    assert primer.dag_properties == expected, msg
