"""Bootstrap fixture set.

"""

from __future__ import annotations
from pathlib import Path, PurePath
from typing import TYPE_CHECKING
import json

from dagsesh import lazy
import pytest

if TYPE_CHECKING:
    from airflow.models.taskinstance import TaskInstance


LAZY_AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")
LAZY_AF_MODELS = lazy.Loader("airflow.models", globals(), "airflow.models")

CONFIG = PurePath(Path(__file__).resolve().parents[3]).joinpath(
    "src", "flowz", "config"
)


@pytest.mark.parametrize("config_path", [CONFIG.joinpath("tasks")])
def test_task_variables(bootstrap_task_variables: TaskInstance) -> None:
    """Load Airflow JSON task definitions into airflow.models.Variable DB."""
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
        CONFIG.joinpath("tasks", "task_variables.json.j2"), encoding="utf-8"
    ) as _fh:
        data = json.load(_fh)
        expected = len(data.keys())
    assert task_variable_count == expected, msg


@pytest.mark.parametrize("config_path", [CONFIG.joinpath("dags")])
def test_dag_variables(
    bootstrap_dag_variables: TaskInstance, dag_names: list[str]
) -> None:
    """Load Airflow DAG JSON definitions into airflow.models.Variable DB."""
    # When the DAG variable set is loaded in the airflow.models.Variable DB
    # bootstrap_dag_variables

    # then I should receive SUCCESS state
    msg = "Task loading JSON DAG definitions into airflow.models.Variable DB run error"
    assert (
        bootstrap_dag_variables.state == LAZY_AF_UTILS.state.State.SUCCESS  # type: ignore
    ), msg

    # and a list of DAG airflow.models.Variable should have a corresponding DAG
    with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore
        dag_variables: list[set[str]] = (
            session.query(LAZY_AF_MODELS.Variable.key)  # type: ignore
            .filter(LAZY_AF_MODELS.Variable.key.like("%_%_LOCAL"))  # type: ignore
            .all()
        )
        stray_dag_variables: set[str] = {
            item for dag_names in dag_variables for item in dag_names
        }

    msg = (
        f'DAG variable definition set {", ".join(stray_dag_variables)} in '
        '"dag_variables.json.j2"? does not exist in DagBag'
    )
    assert not stray_dag_variables, msg
