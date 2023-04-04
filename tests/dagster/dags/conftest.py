"""Test DAG level fixtures.

"""
from typing import Iterable
from _collections_abc import dict_keys

import _pytest.fixtures
import pytest

from airflow.models.dagbag import DagBag


DAG_TASK_IDS = {
    "ADMIN_BOOTSTRAP_LOCAL": [
        "end",
        "load-connections",
        "load-task-variables",
        "set-authentication",
        "start",
    ],
}


@pytest.fixture()
def dag_id_cntrl(  # pylint: disable=unused-argument
    request: _pytest.fixtures.SubRequest,
) -> dict_keys:
    """Return each DAG ID from the "DAG_TASK_IDS" control list."""
    return DAG_TASK_IDS.keys()


@pytest.fixture(params=list(DAG_TASK_IDS.items()))
def dag_id_cntrl_iterator(request: _pytest.fixtures.SubRequest) -> dict_keys:
    """Iterate over each DAG ID from the "DAG_TASK_IDS" control list."""
    return request.param


@pytest.fixture()
def dag_names(dagbag: DagBag) -> Iterable[str]:
    """Get a list of DAG names: dagbag context."""
    return list(dagbag.dags.keys())
