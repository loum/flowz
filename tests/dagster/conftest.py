"""Global fixture arrangement.

"""
from typing import Text

import datetime
import os
import pathlib
import uuid

from pyspark import SparkConf
from pyspark.sql import SparkSession
import pytest
import _pytest.fixtures

from dagsesh.utils import lazy  # type: ignore[import]
from dagster.primer import Primer  # type: ignore[import]

import dagster.datastore.spark  # type: ignore[import]
import dagster.user  # type: ignore[import]
import dagster.data.factory.dummy  # type: ignore[import]

LAZY_ETLER_API = lazy.Loader("dagster.api", globals(), "dagster.api")
LAZY_ETLER_VAR = lazy.Loader("dagster.variable", globals(), "dagster.variable")


LAZY_AF = lazy.Loader("airflow", globals(), "airflow")
LAZY_TI = lazy.Loader(
    "airflow.models.taskinstance", globals(), "airflow.models.taskinstance"
)
LAZY_PYTHON_OPERATOR = lazy.Loader(
    "airflow.operators.python", globals(), "airflow.operators.python"
)
LAZY_AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")

CONFIG = os.path.join(pathlib.Path(__file__).resolve().parents[1], "config")


@pytest.fixture
def bootstrap_authentication(request: _pytest.fixtures.SubRequest) -> None:
    """Load Airflow JSON auth definition into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        for user in dagster.user.list_airflow_users():
            dagster.user.delete_airflow_user(user)

    request.addfinalizer(fin)

    dag_name = "bootstrap_load_authentication_fixture"
    description = "Bootstrap load-authentication fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id="task-authentication",
        python_callable=dagster.user.set_authentication,
        dag=dag,
    )

    execution_date = primer.dag_properties.get("start_date")
    _ti = LAZY_TI.TaskInstance(task=task, execution_date=execution_date)
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_connections(config_path: Text) -> None:
    """Load Airflow JSON connection definitions into airflow.models.Connection DB."""
    dag_name = "bootstrap_load_connection_fixture"
    description = "Bootstrap load-connection fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-connections"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_API.set_connection,
        op_args=[config_path or os.path.join(CONFIG, "connections")],
        dag=dag,
    )

    execution_date = primer.dag_properties.get("start_date")
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture(scope="function")
def bootstrap_task_variables(
    request: _pytest.fixtures.SubRequest, config_path: Text
) -> None:
    """Load Airflow JSON task definitions into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        LAZY_ETLER_VAR.del_variables(config_path or os.path.join(CONFIG, "tasks"))

    request.addfinalizer(fin)

    dag_name = f"bootstrap_load_task_variables_fixture-{str(uuid.uuid1())}"
    description = "Bootstrap load-task-variables fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-task-variables"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variables,
        op_args=[config_path or os.path.join(CONFIG, "tasks")],
        dag=dag,
    )

    execution_date = primer.dag_properties.get("start_date")
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_dag_variables(
    request: _pytest.fixtures.SubRequest, config_path: Text
) -> None:
    """Load Airflow JSON DAG definitions into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        LAZY_ETLER_VAR.del_variables(config_path or os.path.join(CONFIG, "dags"))

    request.addfinalizer(fin)

    dag_name = "bootstrap_load_dag_variables_fixture"
    description = "Bootstrap load-dag-variables fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-dag-variables"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variables,
        op_args=[config_path or os.path.join(CONFIG, "dags")],
        dag=dag,
    )

    execution_date = primer.dag_properties.get("start_date")
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture()
def task_variables(request: _pytest.fixtures.SubRequest, config_path: Text) -> int:
    """Airflow Variables load and delete."""

    def fin() -> None:
        """Clear out loaded Airflow variables from DB."""
        LAZY_ETLER_VAR.del_variables(config_path)

    request.addfinalizer(fin)
    counter = LAZY_ETLER_VAR.set_variables(config_path)

    return counter


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Handler to the SparkSession for the test harness."""
    conf = SparkConf()
    conf.set("spark.driver.memory", "1g")

    return dagster.datastore.spark.spark_session(app_name="test", conf=conf)
