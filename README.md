# Dagster: Workflow Management Primer

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Upgrading GNU Make (macOS)](#macos-users-only-upgrading-gnu-make)
  - [Creating the local environment](#creating-the-local-environment)
  - [Local environment maintenance](#local-environment-maintenance)
- [Help](#help)
- [Running the Test Harness](#running-the-test-harness)
- [Container Image Management](#container-image-management)
  - [Running the compose stack locally](#running-the-compose-stack-locally)
- [Useful Commands](#useful-commands)

## Overview
Workflow management primer for Apache Airflow:
- [Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags)

The goals here are:
- Simple, basic entry point to Airflow DAG development and experimentation.
- Provide localised, offline Airflow DAG development capability using the simple [Airflow Sequential Executor-based](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode.

See [Dagster's documentation](https://loum.github.io/dagster/) for more information.

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
