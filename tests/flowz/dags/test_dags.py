"""DAG loading unit test cases.

"""

from __future__ import annotations
from inspect import currentframe
from typing import TYPE_CHECKING
import os
import unittest.mock

if TYPE_CHECKING:
    from airflow.models import DagBag
    from collections.abc import KeysView, Iterable
    from types import FrameType


# --8<-- [start:test_dagbag_set]
@unittest.mock.patch.dict(os.environ, {"AIRFLOW_CUSTOM_ENV": "LOCAL"})
def test_dagbag_set(
    dag_names: Iterable[str],
    dag_id_cntrl: KeysView,
) -> None:
    """Test the dagbag load."""
    # Given a list of DAG names taken from the DagBag
    # dag_names

    # less the DAG names that can be skipped from the check
    dag_names_to_skip: list[str] = []
    received = [x for x in dag_names if x not in dag_names_to_skip]

    frame: FrameType | None = currentframe()
    assert frame is not None
    test_to_skip: str = frame.f_code.co_name
    msg = (
        'DagBag to "DAG_TASK_IDS" control list mis-match: '
        "check the DAG names defined by DAG_TASK_IDS in fixtures. "
        f'Or, add to "dag_names_to_skip" in the {test_to_skip}() '
        "test to skip the check."
    )
    expected = [x for x in dag_id_cntrl if x not in dag_names_to_skip]
    assert sorted(received) == sorted(expected), msg


# --8<-- [end:test_dagbag_set]


def test_dag_task_ids(dagbag: DagBag, dag_id_cntrl_iterator: KeysView) -> None:
    """Check DAG task count against the "DAG_TASK_IDS" control list.."""
    # Given a DAG and it's associated tasks taken from the "DAG_TASK_IDS" control fixture
    dag_name, tasks = dag_id_cntrl_iterator

    # when I source the DAG instance from Airflow's DagBag
    dag = dagbag.get_dag(dag_id=dag_name)

    # then the DAG must exist in Airflow's DagBag
    msg = f'DAG {dag_name} from "DAG_TASK_IDS" control fixture does not exist in the Airflow DagBag'
    assert dag, msg

    # and the task list should match the "DAG_TASK_IDS" control fixture entries
    msg = f"DAG {dag_name} task ID error: check the DAG names defined by DAG_TASK_IDS in fixtures"
    assert sorted([x.task_id for x in dag.tasks]) == sorted(tasks), msg
