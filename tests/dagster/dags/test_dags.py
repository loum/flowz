"""DAG loading unit test cases.
"""
from typing import List, Text
import os
import unittest.mock
from _collections_abc import dict_keys

from airflow.models.dagbag import DagBag


@unittest.mock.patch.dict(os.environ, {"AIRFLOW_CUSTOM_ENV": "LOCAL"})
def test_dagbag_set(
    dagbag: DagBag,
    dag_id_cntrl: dict_keys,
) -> None:
    """Test the dagbag load."""
    # Given a list of DAG names taken from the DagBag
    dag_names = list(dagbag.dags.keys())

    # less the DAG names that can be skipped from the check
    dag_names_to_skip: List[Text] = []
    received = [x for x in dag_names if x not in dag_names_to_skip]

    msg = (
        'DagBag to "DAG_TASK_IDS" control list mis-match: '
        "check the DAG names defined by DAG_TASK_IDS in fixtures. "
        'Or, add to "dag_names_to_skip" in test to skip the check'
    )
    expected = [x for x in dag_id_cntrl if x not in dag_names_to_skip]
    assert sorted(received) == sorted(expected), msg


def test_dag_task_ids(dagbag: DagBag, dag_id_cntrl_iterator: dict_keys) -> None:
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
