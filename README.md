# Dagster: Workflow Management Primer

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Upgrading GNU Make (macOS)](#macos-users-only-upgrading-gnu-make)
  - [Creating the local environment](#creating-the-local-environment)
  - [Local environment maintenance](#local-environment-maintenance)
- [Help](#help)
- [Running the Test Harness](#running-the-test-harness)
- [Running the Local Airflow Webserver UI](#running-the-local-airflow-webserver-ui)
- [Creating a Workflow: the DAG File](#creating-a-workflow-the-dag-file)
  - [Creating a DAG from the default template](#creating-a-dag-from-the-default-template)
    - [Default DAG template code snippet](#default-dag-template-code-snippet)
- [Things to Consider when Creating Your DAGs](#things-to-consider-when-creating-your-dags)
  - [Naming standards](#naming-standards)
- [Container Image Management](#container-image-management)
  - [Running the compose stack locally](#running-the-compose-stack-locally)
- [Useful Commands](#useful-commands)

## Overview
Workflow management primer for Apache Airflow:
- [Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags)

The goals here are:
- Simple, basic entry point to Airflow DAG development and experimentation.
- Provide localised, offline Airflow DAG development capability using the simple [Airflow Sequential Executor-based](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode.

[top](#dagster-workflow-management-primer)

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3 Interpreter. [We recommend installing pyenv](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)
- To run local PySpark you will need [OpenJDK 11](https://openjdk.java.net/install/)

[top](#dagster-workflow-management-primer)

## Getting Started
[Makester](https://loum.github.io/makester/) is used as the Integrated Developer Platform.

### (macOS Users only) upgrading GNU `make`
Follow [these notes](https://loum.github.io/makester/macos/#upgrading-gnu-make-macos) to get [GNU make](https://www.gnu.org/software/make/manual/make.html).

### Creating the local environment
Get the code and change into the top level `git` project directory:
```
git clone https://github.com/loum/dagster.git && cd dagster
```

> **_NOTE:_** Run all commands from the top-level directory of the `git` repository.

For first-time setup, get the [Makester project](https://github.com/loum/makester.git):
```
git submodule update --init
```

Initialise the environment:
```
make pristine
```

### Local environment maintenance
Keep [Makester project](https://github.com/loum/makester.git) up-to-date with:
```
git submodule update --remote --merge
```

[top](#dagster-workflow-management-primer)

## Help
There should be a `make` target to get most things done. Check the help for more information:
```
make help
```

[top](#dagster-workflow-management-primer)

## Running the Test Harness
We use [pytest](https://docs.pytest.org/en/latest/). To run the tests:
```
make tests
```

[top](#dagster-workflow-management-primer)

## Running the Local Airflow Webserver UI
Launch the Airflow webserver UI in [SequentialExector](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode to visualise and interact with dashboard (`Ctrl-C` to stop):
```
make local-airflow-start
```
You can access your local Airflow webserver console via http://localhost:8888.

[top](#dagster-workflow-management-primer)

## Creating a Workflow: the DAG File
Airflow DAGs are written in Python and technically just a Python module (with `.py` extension). DAGs are interpreted by Airflow via the [DagBag facility](https://airflow.apache.org/docs/stable/_modules/airflow/models/dagbag.html#DagBag) and can then be scheduled to execute.

DAGs files are placed under the `AIRFLOW__CORE__DAGS_FOLDER`. The directory location can be identified as follows:
```
make print-AIRFLOW__CORE__DAGS_FOLDER
```

### Creating a DAG from the default template
The default DAG template can help you get started creating your new DAG. The template DAG at `src/dagster/dags/template.py` features a set of `start` and `end` "book-end" tasks that can be used to delimit your pipeline. You then add your own Business related tasks in between.

The `start` and `end` tasks are instantiated via Airflow's [DummyOperators](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/dummy/index.html#module-airflow.operators.dummy) and act as _safe_ landing zones for your pipeline.

> **_NOTE:_** More information around Airflow DAG creation and concepts is available at the [Airflow tutorial](https://airflow.apache.org/docs/stable/tutorial.html).

Copy `src/dagster/dags/template.py`  into a new Python file replacing `DAG_NAME` with something meaningful that best represents your new workflow:
```
cp src/dagster/dags/template.py src/dagster/dags/<DAG_NAME>.py
```
Provide a more detailed description about your new DAG by editing `src/dagster/dags/<DAG_NAME>.py` and replacing the `DESCRIPTION` variable value to suit. `DESCRIPTION` renders in the Airflow UI and helps visitors understand the intent behind your workflow.

A quick validation of your new DAG can be performed with:
```
make list-dags
```

#### Default DAG template code snippet
```python
"""The simplest DAG template.

"""
import os
import airflow

import dagster.common.task
from dagster.utils.dagprimer import DagPrimer


DAG_NAME = os.path.basename(os.path.splitext(__file__)[0]).replace('_', '-')
DESCRIPTION = """Simple book-end DAG template to get you started"""

PRIMER = DagPrimer(dag_name=DAG_NAME,
                   department='PG',
                   description=DESCRIPTION)

DAG = airflow.DAG(PRIMER.dag_id, default_args=PRIMER.default_args, **(PRIMER.dag_properties))

TASK_START = dagster.common.task.start(DAG, PRIMER.default_args)
#
# Add your content here.
#
TASK_END = dagster.common.task.end(DAG, PRIMER.default_args)

TASK_START >> TASK_END # pylint: disable=pointless-statement
```

[top](#dagster-workflow-management-primer)

## Things to Consider when Creating Your DAGs
Airflow as a workflow management tool can be utilised as shared infrastructure between different teams and entities within the organisation. Having more contributors to the platform introduces a communal aspect where everyone can create and leverage existing code and tooling. However, as the number of DAGs begins to increase the platform could also increase in complexity. The following guidelines should be considered when creating your DAGs.

### Naming standards
The DAG name (`DAG_NAME`) plays an integral part in the operation of Airflow. It is also the token that presents in the Airflow web UI.

The DAG names are made up of three components separated by underscores (`_`):
1. Department or team name (`department` parameter to `dagster.utils.dagprimer.DagPrimer`)
1. Short name to give DAG some operational context (`dag_name` parameter to `dagster.utils.dagprimer.DagPrimer`)
1. Environment is added automatically based on the setting of the environment variable `AIRFLOW_CUSTOM_ENV` (defaults to `local`)

For example, the DAG name generated from the `src/dagster/dags/template.py` becomes `ADMIN-TEMPLATE_LOCAL`

> **_NOTE:_** Ensure the `dag_name` and `department` combination is unique amongst all DAGS under ``AIRFLOW__CORE__DAGS_FOLDER`` as this could cause an implicit conflict that is difficult to troubleshoot.

[top](#dagster-workflow-management-primer)

## Container Image Management

> **_NOTE:_**  See [Makester's `docker` subsystem](https://loum.github.io/makester/makefiles/docker/) for more detailed container image operations.

Build the container image for local testing:
```
make multi-arch-build-test
```

Search for built container image:
```
make image-search
```

Delete the container image:
```
make image-rm
```

### Running the compose stack locally
The project supports the creation of a Docker image that can be used to deploy into a container orchestration system. A Docker compose recipe is provided that allows the creation of an Airflow stack that runs under CeleryExecutor mode. This can be invoked with:
```
make celery-stack-up
```
Navigate to [https://localhost:8443](http://localhost:8443/) and authenticate with dummy credentials `airflow`:`airflow`.

To destroy the stack:
```
make celery-stack-down
```

[top](#dagster-workflow-management-primer)

## Useful Commands

### `make pristine`
Rebuilds your local Python virtual environment and get the latest package dependencies. The Python virtual environment is disposable and will not affect your code. `make pristine` is also a good way to get the latest packages from PyPI to safeguard against version conflicts.

### `make reset-airflow`
Rebuilds your local Airflow operating environment. Gives you a fresh Airflow install without the overhead of rebuilding the Python virtual environment.

### `make pyspark`
Start the `pyspark` interpreter in a virtual environment context. Handy if you want quick access to the Spark context.

[top](#dagster-workflow-management-primer)
