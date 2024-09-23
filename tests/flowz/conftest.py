"""Global fixture arrangement.

"""

from datetime import timedelta
from pathlib import Path, PurePath
from typing import cast
import uuid

from pyspark import SparkConf
from pyspark.sql import SparkSession
import _pytest.fixtures
import pytest

from dagsesh import lazy  # type: ignore[import]
from flowz.primer import Primer  # type: ignore[import]

import flowz.datastore.spark  # type: ignore[import]
import flowz.user  # type: ignore[import]
import flowz.data.factory.dummy  # type: ignore[import]

LAZY_ETLER_API = lazy.Loader("flowz.api", globals(), "flowz.api")
LAZY_ETLER_VAR = lazy.Loader("flowz.variable", globals(), "flowz.variable")


LAZY_AF = lazy.Loader("airflow", globals(), "airflow")
LAZY_TI = lazy.Loader(
    "airflow.models.taskinstance", globals(), "airflow.models.taskinstance"
)
LAZY_PYTHON_OPERATOR = lazy.Loader(
    "airflow.operators.python", globals(), "airflow.operators.python"
)
LAZY_AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")

CONFIG = PurePath(Path(__file__).resolve().parents[1]).joinpath("config")


@pytest.fixture
def bootstrap_authentication(request: _pytest.fixtures.SubRequest) -> None:
    """Load Airflow JSON auth definition into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        for user in flowz.user.list_airflow_users():
            flowz.user.delete_airflow_user(user)

    request.addfinalizer(fin)

    dag_name = "bootstrap_load_authentication_fixture"
    description = "Bootstrap load-authentication fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(  # type: ignore
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task = LAZY_PYTHON_OPERATOR.PythonOperator(  # type: ignore
        task_id="task-authentication",
        python_callable=flowz.user.set_authentication,
        dag=dag,
    )

    execution_date = primer.dag_properties.get("start_date")
    _ti = LAZY_TI.TaskInstance(task=task, execution_date=execution_date)  # type: ignore
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_connections(config_path: str) -> None:
    """Load Airflow JSON connection definitions into airflow.models.Connection DB."""
    dag_name = "bootstrap_load_connection_fixture"
    description = "Bootstrap load-connection fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(  # type: ignore
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-connections"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(  # type: ignore
        task_id=task_id,
        python_callable=LAZY_ETLER_API.set_connection,
        op_args=[config_path or str(CONFIG.joinpath("connections"))],
        dag=dag,
    )

    execution_date = cast(timedelta, primer.dag_properties.get("start_date"))
    execution_date_end = execution_date + timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,  # type: ignore
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,  # type: ignore
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture(scope="function")
def bootstrap_task_variables(
    request: _pytest.fixtures.SubRequest, config_path: str
) -> None:
    """Load Airflow JSON task definitions into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        LAZY_ETLER_VAR.del_variables(  # type: ignore
            config_path or str(CONFIG.joinpath("tasks"))
        )

    request.addfinalizer(fin)

    dag_name = f"bootstrap_load_task_variables_fixture-{str(uuid.uuid1())}"
    description = "Bootstrap load-task-variables fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(  # type: ignore
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-task-variables"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(  # type: ignore
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variables,
        op_args=[config_path or str(CONFIG.joinpath("tasks"))],
        dag=dag,
    )

    execution_date = cast(timedelta, primer.dag_properties.get("start_date"))
    execution_date_end = execution_date + timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,  # type: ignore
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,  # type: ignore
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_dag_variables(
    request: _pytest.fixtures.SubRequest, config_path: str
) -> None:
    """Load Airflow JSON DAG definitions into airflow.models.Variable DB."""

    def fin() -> None:
        """Tear down."""
        LAZY_ETLER_VAR.del_variables(  # type: ignore
            config_path or str(CONFIG.joinpath("dags"))
        )

    request.addfinalizer(fin)

    dag_name = "bootstrap_load_dag_variables_fixture"
    description = "Bootstrap load-dag-variables fixture"
    primer = Primer(dag_name=dag_name, department="FIXTURE")
    primer.default_args.update({"description": description})
    dag = LAZY_AF.DAG(  # type: ignore
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    task_id = "load-dag-variables"
    task = LAZY_PYTHON_OPERATOR.PythonOperator(  # type: ignore
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variables,
        op_args=[config_path or str(CONFIG.joinpath("dags"))],
        dag=dag,
    )

    execution_date = cast(timedelta, primer.dag_properties.get("start_date"))
    execution_date_end = execution_date + timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=LAZY_AF_UTILS.state.DagRunState.RUNNING,  # type: ignore
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL,  # type: ignore
    )

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture()
def task_variables(request: _pytest.fixtures.SubRequest, config_path: str) -> int:
    """Airflow Variables load and delete."""

    def fin() -> None:
        """Clear out loaded Airflow variables from DB."""
        LAZY_ETLER_VAR.del_variables(config_path)  # type: ignore

    request.addfinalizer(fin)
    counter = LAZY_ETLER_VAR.set_variables(config_path)  # type: ignore

    return counter


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Handler to the SparkSession for the test harness."""
    conf = SparkConf()
    conf.set("spark.driver.memory", "1g")

    return flowz.datastore.spark.spark_session(app_name="test", conf=conf)


@pytest.fixture()
def runtime_config_path() -> PurePath:
    """Path to the Airflow runtime configuration."""
    return PurePath(Path(__file__).resolve().parents[2]).joinpath(
        "src",
        "flowz",
        "config",
    )
