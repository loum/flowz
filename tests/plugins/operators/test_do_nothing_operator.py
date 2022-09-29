""":class:`dagster.plugins.operators.do_nothing_operator.DoNothingOperator` unit test cases.
"""
import datetime
import unittest.mock
import random
import pytest
from airflow.models import Variable
from airflow.utils.state import State
import airflow
import airflow.utils
import airflow.exceptions

from dagster.utils.dagprimer import DagPrimer
from dagster.plugins.operators.do_nothing_operator import DoNothingOperator


@unittest.mock.patch.object(Variable, 'get')
def test_do_nothing_operator_init(mock_variable):
    """Initialise a DoNothingOperator object.
    """
    # Given a set of config parameters
    operator_kwargs = {
        'var_01': 'var_01_value',
        'var_02': 'var_02_value',
    }

    # when I initialise a DoNothingOperator
    mock_variable.side_effect = lambda *args, **kwargs: {'dry': False}
    do_nothing = DoNothingOperator(task_id='dummy', **operator_kwargs)

    # I should get a DoNothingOperator instance
    msg = 'Object is not a DoNothingOperator instance'
    assert isinstance(do_nothing, DoNothingOperator), msg


#@unittest.mock.patch.object(Variable, 'get')
#def test_do_nothing_operator_init_non_nullable(mock_variable):
#    """Initialise a DoNothingOperator object.
#    """
#    # Given a set of config parameters with undefined non-nullable
#    operator_kwargs = {
#        'var_01': 'var_01_value',
#    }
#
#    # when I initialise a DoNothingOperator
#    mock_variable.side_effect = lambda *args, **kwargs: {'dry': False}
#
#    # then I should get an airflow.exceptions.AirflowFailException
#    expected = 'Parameter "var_02" value None but set not-nullable'
#    with pytest.raises(airflow.exceptions.AirflowFailException, match=expected):
#        DoNothingOperator(task_id='dummy', **operator_kwargs)


DRY_RUNS = [
    {'dry': True, 'result': None},
    {'dry': False, 'result': 'do_nothing'},
]
@pytest.mark.parametrize('test_params', DRY_RUNS)
@unittest.mock.patch.object(Variable, 'get')
def test_do_nothing_operator_dry_run(mock_variable, test_params):
    """DoNothingOperator dry run.
    """
    # Given a DAG definition
    dag_name = 'do_nothing_dry_run'
    description = """DoNothingOperator dry run"""
    primer = DagPrimer(dag_name=dag_name, department='TEST', description=description)
    dag = airflow.DAG(primer.dag_id, default_args=primer.default_args, **(primer.dag_properties))

    # when I initialise a DoNothingOperator in "dry" mode
    def side_effect(*args, **kwargs): # pylint: disable=unused-argument
        return {'dry': test_params.get('dry')}
    mock_variable.side_effect = side_effect

    operator_kwargs = {
        'var_01': 'var_01_value',
        'var_02': 'var_02_value',
    }

    task_id = 'do_nothing'
    task = DoNothingOperator(dag=dag, task_id=task_id, **operator_kwargs)

    execution_date = primer.default_dag_properties.get('start_date')
    execution_date += datetime.timedelta(milliseconds=random.randint(0, 1e6))
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=airflow.utils.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=airflow.utils.types.DagRunType.MANUAL)


    # and run an operator task instance
    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.run(ignore_ti_state=True)

    # then I should receive SUCCESS state
    msg = 'DoNothingOperator task instance dry run error'
    assert _ti.state == State.SUCCESS, msg

    # and the task result should not be defined
    msg = 'Dry run mode should not produce a task result'
    assert _ti.xcom_pull(task_ids='do_nothing') == test_params.get('result'), msg


def test_do_nothing_operator_no_params():
    """DoNothingOperator: no airflow.model.Variable.
    """
    # Given a DAG definition
    dag_name = 'do_nothing_dry_run'
    description = """DoNothingOperator dry run"""
    primer = DagPrimer(dag_name=dag_name, department='TEST', description=description)
    dag = airflow.DAG(primer.dag_id, default_args=primer.default_args, **(primer.dag_properties))

    # when I initialise a DoNothingOperator without airflow.model.Variable coverage
    operator_kwargs = {
        'var_01': 'var_01_value',
        'var_02': 'var_02_value',
    }

    task_id = 'do_nothing'
    task = DoNothingOperator(dag=dag, task_id=task_id, **operator_kwargs)

    execution_date = primer.default_dag_properties.get('start_date')
    execution_date += datetime.timedelta(milliseconds=random.randint(0, 1e6))
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=airflow.utils.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=airflow.utils.types.DagRunType.MANUAL)

    # and run an operator task instance
    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task

    # then I should get an airflow.exceptions.AirflowFailException
    expected = 'Task ID "do_nothing" parameter definition not found in airflow.models.Variable'
    with pytest.raises(airflow.exceptions.AirflowFailException, match=expected):
        _ti.run(ignore_ti_state=True)

    msg = 'DoNothingOperator task instance skip error'
    assert _ti.state == State.FAILED, msg


@unittest.mock.patch.object(Variable, 'get')
def test_do_nothing_operator_skip_task(mock_variable):
    """DoNothingOperator skip task.
    """
    # Given a DAG definition
    dag_name = 'do_nothing_dry_run'
    description = """DoNothingOperator dry run"""
    primer = DagPrimer(dag_name=dag_name, department='TEST', description=description)
    dag = airflow.DAG(primer.dag_id, default_args=primer.default_args, **(primer.dag_properties))

    # when I initialise a DoNothingOperator to skip
    mock_variable.side_effect = lambda *args, **kwargs: {'dry': False, 'skip_task': True}

    operator_kwargs = {
        'var_01': 'var_01_value',
        'var_02': 'var_02_value',
    }

    task_id = 'do_nothing'
    task = DoNothingOperator(dag=dag, task_id=task_id, **operator_kwargs)

    execution_date = primer.default_dag_properties.get('start_date')
    execution_date += datetime.timedelta(milliseconds=random.randint(0, 1e6))
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=airflow.utils.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=airflow.utils.types.DagRunType.MANUAL)

    # and run an operator task instance
    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.run(ignore_ti_state=True)

    # then I should receive SKIPPED state
    msg = 'DoNothingOperator task instance skip error'
    assert _ti.state == State.SKIPPED, msg
