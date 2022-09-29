""":mod:`dagster.plugins.operators.diffit_operator` unit test cases.
"""
import unittest.mock
from airflow.models import Variable

from dagster.plugins.operators.diffit_operator import DiffitOperator


@unittest.mock.patch.object(Variable, 'get')
def test_diffit_operator_init(mock_variable):
    """Initialise a DiffitOperator object.
    """
    # Given a set of Diffit config parameters
    operator_kwargs = {'reader': None}

    # when I initialise a DiffitOperator
    airflow_variable = {
        'left': 'data/differ/left',
        'right': 'data/differ/right',
        'outpath': 'data/differ/out',
        'skip_task': False,
        'dry': False,
    }
    mock_variable.side_effect = lambda *args, **kwargs: airflow_variable
    diffit = DiffitOperator(task_id='dummy', **operator_kwargs)

    # I should get a DiffitOperator instance
    msg = 'Object is not a DiffitOperator instance'
    assert isinstance(diffit, DiffitOperator), msg
