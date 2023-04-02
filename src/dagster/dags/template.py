"""The simplest DAG template.

"""
import os
import airflow

import dagster.common.task
from dagster.primer import Primer


DAG_NAME = os.path.basename(os.path.splitext(__file__)[0]).replace("_", "-")
DESCRIPTION = "Simple book-end DAG template to get you started"

PRIMER = Primer(dag_name=DAG_NAME, department="ADMIN")
PRIMER.dag_properties.update({"description": DESCRIPTION})

DAG = airflow.DAG(
    PRIMER.dag_id, default_args=PRIMER.default_args, **(PRIMER.dag_properties)
)

TASK_START = dagster.common.task.start(DAG, PRIMER.default_args)
#
# Add your content here.
#
TASK_END = dagster.common.task.end(DAG, PRIMER.default_args)

TASK_START >> TASK_END  # pylint: disable=pointless-statement
