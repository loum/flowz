# Getting started

Airflow provides different types of installations that are defined by the
[Executor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html){target="blank"}
type. Flowz supports [SequentialExecutor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/sequential.html){target="blank"} for development and [CeleryExecutor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/celery.html){target="blank"} for production workloads. The following section details how to setup the development environment and how to create your first DAG.

First, [prepare your local development environment](installation-modes/sequentialexecutor/development-environment.md) before creating a DAG from the default Flowz template.
