# Getting started

Dagster can be used as a primer for your workflow management system.

## Running the Local Airflow Webserver UI
Launch the Airflow webserver UI in [SequentialExector](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode to visualise and interact with dashboard (`Ctrl-C` to stop):
```
make local-airflow-start
```
You can access your local Airflow webserver console via [http://localhost:8888](http://localhost:8888).

## Creating a workflow: the DAG file
Airflow DAGs are written in Python and are technically just a Python module (with `.py` extension). DAGs are interpreted by Airflow via the [DagBag facility](https://airflow.apache.org/docs/stable/_modules/airflow/models/dagbag.html#DagBag) and can then be scheduled to execute.

DAGs files are placed under the `AIRFLOW__CORE__DAGS_FOLDER`. The directory location can be identified as follows:
```
make print-AIRFLOW__CORE__DAGS_FOLDER
```

### Creating a DAG from the default template
The default DAG template can help you get started creating your new DAG. The template DAG at `src/dagster/dags/template.py` features a set of `start` and `end` "book-end" tasks that can be used to delimit your pipeline. You then add your own business related tasks in between.

The `start` and `end` tasks are instantiated via Airflow's [EmptyOperators](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/empty/index.html#module-airflow.operators.empty) and act as _safe_ landing zones for your pipeline.

!!! note
    More information around Airflow DAG creation and concepts is available at the [Airflow tutorial](https://airflow.apache.org/docs/stable/tutorial.html).

Copy `src/dagster/dags/template.py`  into a new Python file replacing `DAG_NAME` with something meaningful that best represents your new workflow:
```
cp src/dagster/dags/template.py src/dagster/dags/<DAG_NAME>.py
```
Provide a more detailed description about your new DAG by editing `src/dagster/dags/<DAG_NAME>.py` and replacing the `DESCRIPTION` variable value to suit. `DESCRIPTION` renders in the Airflow UI and helps visitors understand the intent behind your workflow.

A quick validation of your new DAG can be performed with:
```
make local-list-dags
```

#### Default DAG template code snippet
```
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
```

## Things to consider when creating your DAGs
Airflow as a workflow management tool can be utilised as shared infrastructure between different teams and entities within the organisation. Having more contributors to the platform introduces a communal aspect where everyone can create and leverage existing code and tooling. However, as the number of DAGs begins to increase the platform could also increase in complexity. The following guidelines should be considered when creating your DAGs.

### Naming standards
The DAG name (`DAG_NAME`) plays an integral part in the operation of Airflow. It is also the token that presents in the Airflow web UI.

The DAG names are made up of three components separated by underscores (`_`):

1. Department or team name (`department` parameter to `dagster.Primer`)
1. Short name to give DAG some operational context (`dag_name` parameter to `dagster.Primer`)
1. Environment is added automatically based on the setting of the environment variable `AIRFLOW_CUSTOM_ENV` (defaults to `local`)

For example, the DAG name generated from the `src/dagster/dags/template.py` becomes `ADMIN-TEMPLATE_LOCAL`

!!! note
    Ensure the `dag_name` and `department` combination is unique amongst all DAGS under ``AIRFLOW__CORE__DAGS_FOLDER`` as this could cause an implicit conflict that is difficult to troubleshoot.
