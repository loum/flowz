# Dagster: Workflow Management Primer
- [Overview](#Overview)
- [Prerequisites](#Prerequisites)
  - [Upgrading GNU Make (macOS)](#Upgrading-GNU-Make-macOS)
- [Getting Started](#Getting-Started)
  - [Help](#Help)
  - [Building the Local Environment](#Building-the-Local-Environment)
    - [Local Environment Maintenance](#Local-Environment-Maintenance)
  - [Running the Test Harness](#Running-the-Test-Harness)
  - [Running the Airflow Webserver UI](#Running-the-Airflow-Webserver-UI)
- [Creating a Workflow: the DAG File](#Creating-a-Workflow-the-DAG-File)
  - [Creating a DAG from the Default Template](#Creating-a-DAG-from-the-Default-Template)
    - [The Default DAG Template Code Snippet](#The-Default-DAG-Template-Code-Snippet)
- [Things to Consider when Creating Your DAGs](#Things-to-Consider-when-Creating-Your-DAGs)
  - [Naming Standards](#Naming-Standards)
- [Docker Image Development and Management](#Docker-Image-Development-and-Management)
  - [Building the PyPI Package Artefact](#Building-the-PyPI-Package-Artefact)
  - [Building the Docker Image](#Building-the-Docker-Image)
  - [Searching Images](#Searching-Images)
  - [All-in-one Helper](#All-in-one-Helper)
- [Preparing for Deployment](#Preparing-for-Deployment)
 - [Useful Commands](#Useful-Commands)
 - [FAQs](#FAQs)

## Overview
Workflow management primer for Apache Airflow:
- [Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags)

The goals here are:
- simple, basic entry point to Airflow DAG development and experimentation
- provide localised, offline Airflow DAG development capability using the simple [Airflow Sequential Executor-based](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3.10 Interpreter [(we recommend installing pyenv)](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)
- To run local PySpark you will need [OpenJDK 11](https://openjdk.java.net/install/)

### Upgrading GNU Make (macOS)
Although the macOS machines provide a working GNU `make` it is too old to support the capabilities within the DevOps utilities package, [makester](https://github.com/loum/makester). Instead, it is recommended to upgrade to the GNU `make` version provided by Homebrew. Detailed instructions can be found at https://formulae.brew.sh/formula/make . In short, to upgrade GNU make run:
```
brew install make
```
The `make` utility installed by Homebrew can be accessed by `gmake`. The https://formulae.brew.sh/formula/make notes suggest how you can update your local `PATH` to use `gmake` as `make`. Alternatively, alias `make`:
```
alias make=gmake
```
## Getting Started
### Building the Local Environment
Get the code and change into the top level `git` project directory:
```
git clone https://github.com/loum/dagster.git && cd dagster
```
> **_NOTE:_** Run all commands from the top-level directory of the `git` repository.

For first-time setup, prime the [Makester project](https://github.com/loum/makester.git):
```
git submodule update --init
```
Initialise the environment:
```
make pristine
```
#### Local Environment Maintenance
Keep [Makester project](https://github.com/loum/makester.git) up-to-date with:
```
git submodule update --remote --merge
```
### Help
There should be a `make` target to get most things done. Check the help for more information:
```
make help
```
### Running the Test Harness
Tests are good. We use [pytest](https://docs.pytest.org/en/6.2.x/). To run the tests:
```
make tests
```
### Running the Airflow Webserver UI
Launch the Airflow webserver UI in [SequentialExector](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode to visualise and interact with dashboard (`Ctrl-C` to stop):
```
make start
```
You can access your local Airflow webserver console via http://localhost:8888.

## Creating a Workflow: the DAG File
Airflow DAGs are written in Python and technically just a Python module (with `.py` extension). DAGs are interpreted by Airflow via the [DagBag facility](https://airflow.apache.org/docs/stable/_modules/airflow/models/dagbag.html#DagBag) and can then be scheduled to execute.

DAGs files are placed under the `AIRFLOW__CORE__DAGS_FOLDER`. The directory location can be identified as follows:
```
make print-AIRFLOW__CORE__DAGS_FOLDER
```
### Creating a DAG from the Default Template
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
#### The Default DAG Template Code Snippet
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
## Things to Consider when Creating Your DAGs
Airflow as a workflow management tool can be utilised as shared infrastructure between different teams and entities within the organisation. Having more contributors to the platform introduces a communal aspect where everyone can create and leverage existing code and tooling. However, as the number of DAGs begins to increase the platform could also increase in complexity. The following guidelines should be considered when creating your DAGs.

### Naming Standards
The DAG name (`DAG_NAME`) plays an integral part in the operation of Airflow. It is also the token that presents in the Airflow web UI.

The DAG names are made up of three components separated by underscores (`_`):
 1. Department or team name (`department` parameter to `dagster.utils.dagprimer.DagPrimer`)
 2. Short name to give DAG some operational context (`dag_name` parameter to `dagster.utils.dagprimer.DagPrimer`)
 3. Environment is added automatically based on the setting of the environment variable `AIRFLOW_CUSTOM_ENV` (defaults to `local`)

For example, the DAG name generated from the `src/dagster/dags/template.py` becomes `ADMIN-TEMPLATE_LOCAL`

> **_NOTE:_** Ensure the `dag_name` and `department` combination is unique amongst all DAGS under ``AIRFLOW__CORE__DAGS_FOLDER`` as this could cause an implicit conflict that is difficult to troubleshoot.

## Docker Image Development and Management
### Building the PyPI Package Artefact
Here's a great [PyPI package build](https://packaging.python.org/tutorials/packaging-projects/) reference. Fortunately, most of the work has been done for you with the `package` target:
```
make package
```
This will create a Python wheel under the `.wheelhouse` directory.

### Building the Docker Image
> **_NOTE:_** Airflow base image is taken from [https://hub.docker.com/repository/docker/loum/airflow-base](https://hub.docker.com/repository/docker/loum/airflow-base)

Build the image with:
```
make build-image
```
### Searching Images
To list the available Docker images::
```
make search-image
```
### All-in-one Helper
PyPI Package Artefact and immutable Airflow Docker image can be built with the following convenience target:
```
make build-all
```
## Preparing for Deployment
The project supports the creation of a Docker image that can be used to deploy into a container orchestration system. A Docker compose recipe is provided that allows the creation of an Airflow stack that runs under CeleryExecutor mode. This can be invoked with:
```
make stack-up
```
Navigate to [https://localhost:8443](http://localhost:8443/) and authenticate with dummy credentials `airflow`:`airflow`.

To destroy the stack:
```
make stack-down
```
## Useful Commands
### `make pristine`
Rebuilds your local Python virtual environment and get the latest package dependencies. The Python virtual environment is disposable and will not affect your code. `make pristine` is also a good way to get the latest packages from PyPI to safeguard against version conflicts.

### `make reset-airflow`
Rebuilds your local Airflow operating environment. Gives you a fresh Airflow install without the overhead of rebuilding the Python virtual environment.

### `make py`
Start the `python` interpreter in a virtual environment context. This will give you access to all of your PyPI package dependencies.

### `make lint`
Lint the code base with `pylint`.

### `make deps`
Display PyPI package dependency tree.

### `make pyspark`
Start the `pyspark` interpreter in a virtual environment context. Handy if you want quick access to the Spark context.

## FAQs
***Q. Why is the default make on macOS so old?***
Apple seems to have an issue with licensing around GNU products: more specifically to the terms of the GPLv3 licence agreement. It is unlikely that Apple will provide current versions of utilities that are bound by the GPLv3 licensing constraints.
***Q. Can I change the default Airflow webserver port?***
Yes. All Airflow settings can be managed via environment variables. The default port of `8888` has been set within the `envfile`:
```
AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8888
```

---
[top](#Dagster-Workflow-Management-Primer)
