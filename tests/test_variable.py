"""Unit test cases for :mod:`dagster.variable`.
"""
import os
import pathlib
import pytest

import dagster.variable
from dagsesh.utils import lazy

AF_UTILS = lazy.Loader('airflow.utils', globals(), 'airflow.utils')
AF_MODELS = lazy.Loader('airflow.models', globals(), 'airflow.models')
VARIABLES_PATH = os.path.join(pathlib.Path(__file__).resolve().parents[0],
                              'files',
                              'config',
                              'tasks')
TASK_VARIABLE_COUNT = 10


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_delete_task_variables(task_variables): # pylint: disable=unused-argument
    """Test the pristine Airflow task Variables load.
    """
    # when I load in the configured Airflow task Variables

    # and attempt to delete a unknown key
    key = 'banana'
    received = dagster.variable.del_variable_key(key)

    # then I should receive a False status
    msg = 'Attempt to delete a unknown key should return False'
    assert not received, msg

    # and I should receive the original count of Airflow Variables
    msg = 'Variable list should not be empty (Airflow tasks)'
    assert task_variables == TASK_VARIABLE_COUNT, msg


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_pristine_load_of_task_variables(task_variables): # pylint: disable=unused-argument
    """Test the pristine Airflow task Variables load.
    """
    # when I load in the configured Airflow task Variables

    # then I should receive a list of Airflow Variables
    msg = 'Variable list should not be empty (Airflow tasks)'
    assert task_variables == TASK_VARIABLE_COUNT, msg


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_reload_of_task_variables(task_variables): # pylint: disable=unused-argument
    """Test the reload of Airflow task Variables load.
    """
    # when I load in the configured Airflow task Variables

    # and then reload the configured Airflow task Variables
    received = dagster.variable.set_variable(VARIABLES_PATH)

    # then the load count should be 0
    msg = 'Airflow task reload count should be 0'
    assert not received, msg

    # and the Airflow task Variable count should remain unchanged
    with AF_UTILS.session.create_session() as session:
        task_variable_count = session.query(AF_MODELS.Variable.id).\
                                  filter(~AF_MODELS.Variable.id.like('%_%_LOCAL')).count()

    msg = 'Variable list should not be empty (Airflow tasks)'
    assert task_variable_count == TASK_VARIABLE_COUNT, msg


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_reload_of_task_variables_missing_entry(task_variables): # pylint: disable=unused-argument
    """Test the reload of Airflow task Variables load: missing entry.
    """
    # when I load in the configured Airflow task Variables

    # and delete an existing Airflow task Variable entry
    key = 'task-01'
    dagster.variable.del_variable_key(key)

    # then the Airflow task Variable count should reduce by one
    with AF_UTILS.session.create_session() as session:
        task_variable_count = session.query(AF_MODELS.Variable.id).\
                                  filter(~AF_MODELS.Variable.id.like('%_%_LOCAL')).count()

    msg = 'Variable list should not be empty (Airflow tasks)'
    assert task_variable_count == TASK_VARIABLE_COUNT - 1, msg

    # and then when reload the configured Airflow task Variables
    received = dagster.variable.set_variable(VARIABLES_PATH)

    # then the load count should be 1
    msg = 'Airflow task reload count should be 0'
    assert received == 1, msg

    # and the original Airflow task Variable count should be restored
    with AF_UTILS.session.create_session() as session:
        task_variable_count = session.query(AF_MODELS.Variable.id).\
                                  filter(~AF_MODELS.Variable.id.like('%_%_LOCAL')).count()

    msg = 'Restored Variable list should be restored (Airflow tasks)'
    assert task_variable_count == TASK_VARIABLE_COUNT, msg


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_get_variables(task_variables): # pylint: disable=unused-argument
    """Test Airflow Variables get.
    """
    # when I load in the configured Airflow Variables

    # and I search for a known key
    key = 'task-01'

    # then I should receive a match
    received = dagster.variable.get_variable(key)
    msg = 'Known variable expected to match from Airflow Variables DB'
    assert received, msg


@pytest.mark.parametrize('config_path', [VARIABLES_PATH])
def test_get_variables_unmatched(task_variables): # pylint: disable=unused-argument
    """Test Airflow Variables get that is unmatched.
    """
    # when I load in the configured Airflow Variables

    # and I search for a unknown key
    key = 'banana'

    # then I should not receive a match
    received = dagster.variable.get_variable(key)
    msg = 'Unknown variable should not match against Airflow Variables DB'
    assert not received, msg
