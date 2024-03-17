"""The simplest DAG template.

"""

from pathlib import PurePath

import airflow

import dagster.task
from dagster.primer import Primer


primer = Primer(dag_name=PurePath(__file__).stem.replace("_", "-"), department="ADMIN")
primer.dag_properties.update(
    {"description": "Simple book-end DAG template to get you started"}
)

dag = airflow.DAG(
    primer.dag_id, default_args=primer.default_args, **(primer.dag_properties)
)

task_start = dagster.task.start(dag, default_args=primer.default_args)
#
# Add your content here.
#
task_end = dagster.task.end(dag, default_args=primer.default_args)

task_start >> task_end  # pylint: disable=pointless-statement
