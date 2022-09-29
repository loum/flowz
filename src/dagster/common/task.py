"""Set of common, re-useable tasks.

"""
from typing import Callable, Dict, Text
from operators.diffit_operator import DiffitOperator
from airflow.operators.dummy import DummyOperator
import airflow


def start(dag: airflow.DAG, default_args: Dict) -> DummyOperator:
    """Task ``start`` book-end definition.

    """
    return dummy(dag, default_args, 'start')


def end(dag: airflow.DAG, default_args: Dict) -> DummyOperator:
    """Task 'end' book-end definition.

    """
    return dummy(dag, default_args, 'end')


def dummy(dag: airflow.DAG, default_args: Dict, name: Text) -> DummyOperator:
    """Task *name* book-end definition.

    """
    return DummyOperator(task_id=name, default_args=default_args, dag=dag)


def diff(dag: airflow.DAG, name: Text, reader: Callable):
    """Convenience function to prime the Diffit Operator.

    """
    return DiffitOperator(dag=dag, task_id=name, reader=reader)
