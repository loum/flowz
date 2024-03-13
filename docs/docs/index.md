# Dagster workflow management primer

Dagster is a code repository templater that provides a development environment for integrating your DAGs into the [Apache Airflow](https://airflow.apache.org/) workflow management system with minimal fuss. Dagster also provides default tooling for the full software development lifecycle and deployment into a containerised environment.

## Wait, what is a DAG?

As per the [Apache Airflow DAG documentation](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html){target="blank"}:

> A DAG (Directed Acyclic Graph) is the core concept of Airflow, collecting [Tasks](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html){target="blank"} together, organized with dependencies and relationships to say how they should run.

Programmatically, a DAG is nothing more than a [Python module](https://docs.python.org/3/tutorial/modules.html){target="blank"}. As such, consider your workflows as a Python logic whereby software development principles can be applied. Mainly code linting, formatting and tests. Dagster provides a default set of tooling for the SDLC. These are interchangeable to suit your team and projects requirements.

!!! note
    Dagster does not intend to tell you **_how_** you should do things. It's here to help you work common tasks.

## Where do I start?

### Creating DAGs
As Dagster is an Apache Airflow DAG code repository templater, begin by forking a copy into your preferred code repository in the first instance. Next, follow the instructions under the Dagster [getting started](getting-started.md) section.

### Getting ready for production: building the container image
Dagster provides the tooling to support a cloud-native deployment model. Follow the: guide under [container image management](installation-modes/celeryexecutor/build.md) to containerise your workflows so that they are ready for deployment.
