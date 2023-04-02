"""Bootstrap takes care of Airflow instance startup dependencies.

"""
from typing import Callable, Text, cast
import os
import pathlib

from airflow.operators.python import PythonOperator
import airflow

import dagster.common.task
import dagster.user
import dagster.variable
import dagster.connection
from dagster.primer import Primer


DAG_NAME: Text = os.path.basename(os.path.splitext(__file__)[0]).replace("_", "-")

DAG_PARAMS = {
    "tags": [DAG_NAME.upper()],
    "schedule_interval": "@once",
    "is_paused_upon_creation": False,
}
PRIMER = Primer(dag_name=DAG_NAME, department="ADMIN")
PRIMER.default_args.update({"description": "Once-off bootstrapper DAG"})
PRIMER.dag_properties.update(DAG_PARAMS)

DAG = airflow.DAG(
    PRIMER.dag_id, default_args=PRIMER.default_args, **(PRIMER.dag_properties)
)

TASK_START = dagster.common.task.start(DAG, PRIMER.default_args)

TASK_AUTH = PythonOperator(
    task_id="set-authentication",
    python_callable=dagster.user.set_authentication,
    dag=DAG,
)

CONFIG: Text = os.path.join(pathlib.Path(__file__).resolve().parents[1], "config")
CONFIG_CONTROL = [
    {
        "task_id": "load-connections",
        "callable": dagster.connection.set_connection,
        "path": os.path.join(CONFIG, "connections"),
    },
    {
        "task_id": "load-task-variables",
        "callable": dagster.variable.set_variables,
        "path": os.path.join(CONFIG, "tasks"),
    },
]
TASK_CONFIG = []
for config in CONFIG_CONTROL:
    path_to_configs: Text = cast(Text, config.get("path"))
    task = PythonOperator(
        task_id=config.get("task_id"),
        python_callable=cast(Callable, config.get("callable")),
        op_args=[path_to_configs],
        dag=DAG,
    )
    TASK_CONFIG.append(task)

TASK_END = dagster.common.task.end(DAG, PRIMER.default_args)

# pylint: disable=pointless-statement
TASK_START >> TASK_AUTH >> TASK_CONFIG >> TASK_END
