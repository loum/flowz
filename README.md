# Dagster: Workflow Management Primer

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [(macOS Users only) upgrading GNU `make`](#macos-users-only-upgrading-gnu-make)
  - [Dagster development: creating the local environment](#dagster-development-creating-the-local-environment)
- [Help](#help)
- [Running the Test Harness](#running-the-test-harness)

## Overview
Workflow management code repository templater for [Apache Airflow](https://airflow.apache.org) targeting data engineering compute.

Fork Dagster into your preferred code repository and start building your workflows with minimal fuss.

The goals here are:
- Simple, basic entry point to Airflow DAG development and experimentation.
- A configurable [pyspark.sql.SparkSession](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.html) to develop Apache Spark compute workflows.
- Provide a localised, offline Airflow DAG development capability using the simple [Airflow Sequential Executor-based](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html) mode with pathways to production-ready containerised deployments.
- Containerisation tooling that can be used as part of your deployment model.

See [Dagster's documentation](https://loum.github.io/dagster/) for more information.

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3 Interpreter. [We recommend installing pyenv](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)
- To run local PySpark you will need [OpenJDK 11](https://openjdk.java.net/install/)

## Getting Started
[Makester](https://loum.github.io/makester/) is used as the Integrated Developer Platform.

### (macOS Users only) upgrading GNU `make`
Follow [these notes](https://loum.github.io/makester/macos/#upgrading-gnu-make-macos) to get [GNU make](https://www.gnu.org/software/make/manual/make.html).

### Dagster development: creating the local environment
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

## Help
There should be a `make` target to get most things done. Check the help for more information:
```
make help
```

## Running the Test Harness
We use [pytest](https://docs.pytest.org/en/latest/). To run the tests:
```
make tests
```

[top](#dagster-workflow-management-primer)
