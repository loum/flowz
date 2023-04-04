"""`dagster.plugins.operators.do_nothing_operator.DoNothingOperator` unit test cases.

"""
from datetime import datetime, timedelta
from typing import Union, cast
import random
import unittest.mock

import pytest

from airflow.models import Variable
from airflow.utils.state import State
import airflow
import airflow.utils
import airflow.exceptions

from dagster.primer import Primer  # type: ignore[import]
from dagster.plugins.operators.do_nothing_operator import (  # type: ignore[import]
    DoNothingOperator,
)


@unittest.mock.patch.object(Variable, "get")
def test_do_nothing_operator_init(mock_variable: unittest.mock.MagicMock) -> None:
    """Initialise a DoNothingOperator object."""
    # Given an initialised a DoNothingOperator
    mock_variable.side_effect = lambda *args, **kwargs: {
        "dry": False,
        "var_01": "var_01_value",
        "var_02": "var_02_value",
    }
    do_nothing = DoNothingOperator(task_id="dummy")

    # I should get a DoNothingOperator instance
    msg = "Object is not a DoNothingOperator instance"
    assert isinstance(do_nothing, DoNothingOperator), msg


DRY_RUNS = [
    {"dry": True, "result": None},
    {"dry": False, "result": "do_nothing"},
]


@pytest.mark.parametrize("test_params", DRY_RUNS)
@unittest.mock.patch.object(Variable, "get")
def test_do_nothing_operator_dry_run(
    mock_variable: unittest.mock.MagicMock,
    test_params: dict[str, bool],
) -> None:
    """DoNothingOperator dry run."""
    # Given a DAG definition
    dag_name = "do_nothing_dry_run"
    description = "DoNothingOperator dry run"
    primer = Primer(dag_name=dag_name, department="TEST")
    primer.dag_properties.update({"description": description})
    dag = airflow.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    # when I initialise a DoNothingOperator in "dry" mode
    def side_effect(  # type: ignore[no-untyped-def]  # pylint: disable=unused-argument
        *args, **kwargs
    ) -> dict[str, Union[bool, str]]:
        return {
            "dry": test_params.get("dry", False),
            "var_01": "var_01_value",
            "var_02": "var_02_value",
        }

    mock_variable.side_effect = side_effect

    task_id = "do_nothing"
    task = DoNothingOperator(dag=dag, task_id=task_id)

    execution_date = cast(datetime, primer.dag_properties.get("start_date"))
    execution_date += timedelta(milliseconds=random.randint(0, int(1e6)))
    execution_date_end = execution_date + timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=airflow.utils.state.DagRunState.RUNNING,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=airflow.utils.types.DagRunType.MANUAL,
    )

    # and run an operator task instance
    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.run(ignore_ti_state=True)

    # then I should receive SUCCESS state
    msg = "DoNothingOperator task instance dry run error"
    assert _ti.state == State.SUCCESS, msg

    # and the task result should not be defined
    msg = "Dry run mode should not produce a task result"
    assert _ti.xcom_pull(task_ids="do_nothing") == test_params.get("result"), msg


@unittest.mock.patch.object(Variable, "get")
def test_do_nothing_operator_no_params(mock_variable: unittest.mock.MagicMock) -> None:
    """DoNothingOperator: no airflow.model.Variable."""
    # Given a DAG definition
    dag_name = "do_nothing_dry_run"
    description = "DoNothingOperator dry run"
    primer = Primer(dag_name=dag_name, department="TEST")
    primer.dag_properties.update({"description": description})
    dag = airflow.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    # when I initialise a DoNothingOperator without airflow.model.Variable coverage
    def side_effect(  # type: ignore[no-untyped-def]  # pylint: disable=unused-argument
        *args, **kwargs
    ) -> dict[str, str]:
        return {"var_01": "var_01_value"}

    mock_variable.side_effect = side_effect

    task_id = "do_nothing"
    expected = 'Parameter "var_02" value None but set not-nullable'
    with pytest.raises(airflow.exceptions.AirflowFailException, match=expected):
        DoNothingOperator(dag=dag, task_id=task_id)


@unittest.mock.patch.object(Variable, "get")
def test_do_nothing_operator_skip_task(mock_variable: unittest.mock.MagicMock) -> None:
    """DoNothingOperator skip task."""
    # Given a DAG definition
    dag_name = "do_nothing_dry_run"
    description = "DoNothingOperator dry run"
    primer = Primer(dag_name=dag_name, department="TEST")
    primer.dag_properties.update({"description": description})
    dag = airflow.DAG(
        primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
    )

    # when I initialise a DoNothingOperator to skip
    mock_variable.side_effect = lambda *args, **kwargs: {
        "dry": False,
        "skip_task": True,
        "var_01": "var_01_value",
        "var_02": "var_02_value",
    }

    task_id = "do_nothing"
    task = DoNothingOperator(dag=dag, task_id=task_id)

    execution_date = cast(datetime, primer.dag_properties.get("start_date"))
    execution_date += timedelta(milliseconds=random.randint(0, int(1e6)))
    execution_date_end = execution_date + timedelta(days=1)
    dagrun = dag.create_dagrun(
        state=airflow.utils.state.DagRunState.RUNNING,
        execution_date=execution_date,
        data_interval=(execution_date, execution_date_end),
        start_date=execution_date_end,
        run_type=airflow.utils.types.DagRunType.MANUAL,
    )

    # and run an operator task instance
    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.run(ignore_ti_state=True)

    # then I should receive SKIPPED state
    msg = "DoNothingOperator task instance skip error"
    assert _ti.state == State.SKIPPED, msg
