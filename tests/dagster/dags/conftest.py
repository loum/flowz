"""DAG fixtures at the unit test level.

"""
from __future__ import annotations
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest
    from airflow.models.dagbag import DagBag
    from collections.abc import KeysView, Iterable


# --8<-- [start:dag_task_ids]
DAG_TASK_IDS = {
# --8<-- [start:admin_bootstrap_local]
    "ADMIN_BOOTSTRAP_LOCAL": [
        "end",
        "load-connections",
        "load-dag-variables",
        "load-task-variables",
        "set-authentication",
        "start",
    ],
# --8<-- [end:admin_bootstrap_local]
}
# --8<-- [end:dag_task_ids]


@pytest.fixture()
def dag_id_cntrl(  # pylint: disable=unused-argument
    request: SubRequest
) -> KeysView:
    """Return each DAG ID from the "DAG_TASK_IDS" control list."""
    return list(DAG_TASK_IDS.keys())


@pytest.fixture(params=list(DAG_TASK_IDS.items()))
def dag_id_cntrl_iterator(request: SubRequest) -> KeysView:
    """Iterate over each DAG ID from the "DAG_TASK_IDS" control list."""
    return request.param


@pytest.fixture()
def dag_names(dagbag: DagBag) -> Iterable[str]:
    """Get a list of DAG names: dagbag context."""
    return list(dagbag.dags.keys())
