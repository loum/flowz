"""Project level fixtures.
"""
from typing import Iterable, List, Text
import pytest


DAG_TASK_IDS = {
    'PG_BOOTSTRAP_LOCAL': [
        'end',
        'load-connections',
        'load-task-variables',
        'set-authentication',
        'start',
    ],
}


@pytest.fixture()
def dag_id_cntrl(request) -> List[Text]: # pylint: disable=unused-argument
    """Return each DAG ID from the "DAG_TASK_IDS" control list.
    """
    return DAG_TASK_IDS.keys()


@pytest.fixture(params=list(DAG_TASK_IDS.items()))
def dag_id_cntrl_iterator(request) -> Iterable[str]:
    """Iterate over each DAG ID from the "DAG_TASK_IDS" control list.
    """
    return request.param


@pytest.fixture()
def dag_names(dagbag) -> Iterable[str]:
    """Get a list of DAG names: dagbag context.
    """
    return list(dagbag.dags.keys())
