"""Bootstrap fixture set.

"""
import os
import json
import pathlib

import pytest

from dagsesh import lazy  # type: ignore[import]
from airflow.models.taskinstance import TaskInstance

LAZY_AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")
LAZY_AF_MODELS = lazy.Loader("airflow.models", globals(), "airflow.models")

CONFIG = os.path.join(
    pathlib.Path(__file__).resolve().parents[3], "src", "dagster", "config"
)


@pytest.mark.parametrize("config_path", [os.path.join(CONFIG, "tasks")])
def test_task_variables(bootstrap_task_variables: TaskInstance) -> None:
    """Test load Airflow JSON task definitions into airflow.models.Variable DB."""
    # then I should receive SUCCESS state
    msg = "Task loading JSON task definitions into airflow.models.Variable DB run error"
    assert (
        bootstrap_task_variables.state
        == LAZY_AF_UTILS.state.State.SUCCESS  # type: ignore
    ), msg

    # and a list of DAG airflow.models.Variable
    with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore
        task_variable_count = (
            session.query(LAZY_AF_MODELS.Variable.id)  # type: ignore
            .filter(~LAZY_AF_MODELS.Variable.id.like("%_%_LOCAL"))  # type: ignore
            .count()
        )

    msg = "Task Variables list should be empty"
    with open(
        os.path.join(CONFIG, "tasks", "task_variables.json.j2"), encoding="utf-8"
    ) as _fh:
        data = json.load(_fh)
        expected = len(data.keys())
    assert task_variable_count == expected, msg


@pytest.mark.parametrize("config_path", [os.path.join(CONFIG, "dags")])
def test_dag_variables(
    bootstrap_dag_variables: TaskInstance, dag_names: list[str]
) -> None:
    """Test load Airflow DAG JSON definitions into airflow.models.Variable DB."""
    # then I should receive SUCCESS state
    msg = "Task loading JSON DAG definitions into airflow.models.Variable DB run error"
    assert (
        bootstrap_dag_variables.state == LAZY_AF_UTILS.state.State.SUCCESS  # type: ignore
    ), msg

    # and a list of DAG airflow.models.Variable
    with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore
        dag_variables = (
            session.query(LAZY_AF_MODELS.Variable.key)  # type: ignore
            .filter(LAZY_AF_MODELS.Variable.key.like("%_%_LOCAL"))  # type: ignore
            .all()
        )

    msg = (
        "DAG Variable list error: "
        'did you add the DAG variable definition to "dag_variables.json.j2"? '
        'Or, add to "dag_names_to_skip" in test to skip the check'
    )
    dag_names_to_skip = ["ADMIN_BOOTSTRAP_LOCAL"]
    expected = [x for x in dag_names if x not in dag_names_to_skip]
    assert sorted([x[0] for x in dag_variables]) == sorted(expected), msg
