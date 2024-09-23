"""Parameterised Operator checks against required airflow.models.Variable.

"""

from __future__ import annotations
from pathlib import Path, PurePath
from typing import TYPE_CHECKING
import pytest

import airflow.utils

from flowz.plugins.operators.parameterised_operator import (  # type: ignore[import]
    ParameterisedOperator,
)

if TYPE_CHECKING:
    from airflow.models import DagBag, TaskInstance
    from collections.abc import KeysView

CONFIG = PurePath(Path(__file__).resolve().parents[3]).joinpath(
    "src", "flowz", "config"
)


@pytest.mark.parametrize("config_path", [str(CONFIG.joinpath("tasks"))])
def test_dag_parameterised_task_id_variables(  # pylint: disable=unused-argument
    dagbag: DagBag,
    dag_id_cntrl: KeysView,
    bootstrap_task_variables: TaskInstance,
) -> None:
    """Check DAG Parameterised Operator tasks have a matching airflow.models.Model."""
    # Given a tuple of parameterised Airflow Operators to check
    # OPERATORS_TO_CHECK

    # and a list of all Parameterised Operator tasks
    task_ids = []
    msg = 'DAG "{}" is listed under DAG_TASK_IDS but not part of the DagBag.  Maybe remove?'
    for dag_name in dag_id_cntrl:
        _dag = dagbag.get_dag(dag_id=dag_name)
        assert _dag, msg.format(dag_name)

        for task_id, operator_class in _dag.task_dict.items():
            for base_class in operator_class.__class__.__bases__:
                if base_class.__name__ == ParameterisedOperator.__name__:
                    task_ids.append(task_id)
                    break

    # and I search the airflow.models.Variable for a corresponding value
    task_id_vars = []
    with airflow.utils.db.create_session() as session:
        for task_id in task_ids:
            for task in session.query(airflow.models.Variable.key).filter(
                airflow.models.Variable.key == task_id
            ):
                task_id_vars.append(task.key)

    # then there should be a match
    received = [x for x in task_ids if x not in task_id_vars]
    missing_task_configs = ", ".join([f'"{x}"' for x in received])
    msg = f'Parameterised tasks missing from "task_variables.json.j2": {missing_task_configs}'
    assert not received, msg
