"""Bootstrap takes care of Airflow dependency priming.

"""
import os
import pathlib
from airflow.operators.python_operator import PythonOperator
import airflow

import dagster.common.task
import dagster.user
import dagster.variable
import dagster.connection
from dagster.utils.dagprimer import DagPrimer


DAG_NAME = os.path.basename(os.path.splitext(__file__)[0]).replace('_', '-')
DESCRIPTION = """Once-off bootstrapper DAG"""

DAG_PARAMS = {
    'tags': [DAG_NAME.upper()],
    'schedule_interval': '@once',
    'is_paused_upon_creation': False,
}
PRIMER = DagPrimer(dag_name=DAG_NAME,
                   department='ADMIN',
                   description=DESCRIPTION,
                   **DAG_PARAMS)

DAG = airflow.DAG(PRIMER.dag_id, default_args=PRIMER.default_args, **(PRIMER.dag_properties))

TASK_START = dagster.common.task.start(DAG, PRIMER.default_args)

TASK_AUTH = PythonOperator(
    task_id='set-authentication',
    python_callable=dagster.user.set_authentication,
    dag=DAG)

CONFIG = os.path.join(pathlib.Path(__file__).resolve().parents[1], 'config')
CONFIG_CONTROL = [
    {
        'task_id': 'load-connections',
        'callable': dagster.connection.set_connection,
        'path': (CONFIG, 'connections')
    },
    {
        'task_id': 'load-task-variables',
        'callable': dagster.variable.set_variable,
        'path': (CONFIG, 'tasks')
    },
]
TASK_CONFIG = []
for config in CONFIG_CONTROL:
    task = PythonOperator(
        task_id=config.get('task_id'),
        python_callable=config.get('callable'),
        op_args=[os.path.join(*config.get('path'))],
        dag=DAG)
    TASK_CONFIG.append(task)

TASK_END = dagster.common.task.end(DAG, PRIMER.default_args)

TASK_START >> TASK_AUTH  >> TASK_CONFIG  >> TASK_END # pylint: disable=pointless-statement
