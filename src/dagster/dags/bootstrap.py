"""Bootstrap takes care of Airflow instance startup dependencies.

"""

from typing import Optional
from pathlib import Path, PurePath

from airflow.decorators import task
import airflow

import dagster.task
import dagster.user
import dagster.variable
import dagster.connection
from dagster.primer import Primer


def dag_name() -> str:
    """Use the DAG module name as the default DAG name.

    Returns:
        String representation of the Airflow DAG name.

    """

    def inner():
        return PurePath(__file__).stem.replace("_", "-")

    return inner()


def dag_params() -> dict:
    """Bootstrapper DAG level parameter initialisation.

    Returns:
        Python dictionary of bootrapper parameters at the DAG level.

    """

    def inner():
        return {
            "tags": [dag_name().upper()],
            "schedule_interval": "@once",
            "is_paused_upon_creation": False,
        }

    return inner()


def config_path() -> str:
    """Bootstrapper configuration path.

    Returns:
        Python string representing the fully qualified path to the custom configuration.

    """
    def inner():
        return PurePath(Path(__file__).resolve().parents[1]).joinpath("config")

    return inner()


primer = Primer(dag_name=dag_name(), department="ADMIN")
primer.default_args.update({"description": "Once-off bootstrapper DAG"})
primer.dag_properties.update(dag_params())
dag = airflow.DAG(
    primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
)


@task(task_id="set-authentication")
def load_auth() -> None:
    """Task wrapper around setting the Airflow Admin/Superuser account."""
    return dagster.user.set_authentication()


@task(task_id="load-connections")
def load_connections(
    path_to_connections: str, environment_override: Optional[str] = None
) -> None:
    """Task wrapper to add configuration items to Airflow `airflow.models.Connection`."""
    return dagster.connection.set_templated_connection(
        path_to_connections=path_to_connections,
        environment_override=environment_override,
    )


TASK_LOAD_CONNECTION = load_connections(
    PurePath(config_path()).joinpath("connections"),
    environment_override=primer.get_env,
)


@task(task_id="load-dag-variables")
def task_load_dag_variables(
    path_to_variables: str, environment_override: Optional[str] = None
) -> int:
    """Task wrapper to add DAG variable items to Airflow `airflow.models.Variable`."""
    return dagster.variable.set_variables(
        path_to_variables=path_to_variables,
        environment_override=environment_override,
    )


TASK_LOAD_DAG_VARIABLES = task_load_dag_variables(
    path_to_variables=PurePath(config_path()).joinpath("dags"),
    environment_override=primer.get_env,
)


@task(task_id="load-task-variables")
def task_load_task_variables(
    path_to_variables: str, environment_override: Optional[str] = None
) -> int:
    """Task wrapper to add task variable items to Airflow `airflow.models.Variable`."""
    return dagster.variable.set_variables(
        path_to_variables=path_to_variables,
        environment_override=environment_override,
    )


TASK_LOAD_TASK_VARIABLES = task_load_task_variables(
    path_to_variables=PurePath(config_path()).joinpath("tasks"),
    environment_override=primer.get_env,
)


# pylint: disable=expression-not-assigned
(
    dagster.task.start(dag, default_args=primer.default_args)
    >> load_auth()
    >> [
        TASK_LOAD_CONNECTION,
        TASK_LOAD_DAG_VARIABLES,
        TASK_LOAD_TASK_VARIABLES,
    ]
    >> dagster.task.end(dag, default_args=primer.default_args)
)
