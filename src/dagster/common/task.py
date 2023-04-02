"""Set of common, re-useable tasks.

"""
from typing import Dict, Optional, Text

from airflow.operators.empty import EmptyOperator
import airflow


def start(dag: airflow.DAG, default_args: Optional[Dict]) -> EmptyOperator:
    """Task `start` book-end definition."""
    return empty(dag, default_args, "start")


def end(dag: airflow.DAG, default_args: Optional[Dict]) -> EmptyOperator:
    """Task `end` book-end definition."""
    return empty(dag, default_args, "end")


def empty(dag: airflow.DAG, default_args: Optional[Dict], name: Text) -> EmptyOperator:
    """Task `name` book-end definition."""
    return EmptyOperator(task_id=name, default_args=default_args, dag=dag)
