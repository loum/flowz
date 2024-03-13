# Airflow admin credentials

## Overriding Airflow's `webserver_config.py`

One of the key differences between the [Dagster development environment](../../installation-modes/sequentialexecutor/development-environment.md) and the [remote executor variant (Celery Executor)](../../installation-modes/celeryexecutor/instance-runtime.md) is that Airflow webserver authentication is disabled during DAG development. Dagster achieves this by overriding Airflow's [`webserver_config.py`](https://github.com/apache/airflow/blob/main/airflow/config_templates/default_webserver_config.py){target="blank"} during the initialisation of the development environment.

## Remote executor credentials management

Airflow remote executor installation types will enforce `admin` user authentication by default:

![Remote executor webserver login](../../assets/images/remote_executor_webserver_login.png)

The Dagster bootstrap DAG features an `admin` user credentials primer task. By default, the username and password fields are both `airflow`.

!!! warning
    Do not use the default primer credentials in a production environment.

It is possible to override the default primer credentials by setting the environment variables `DAGSTER_AIRFLOW_ADMIN_USER` and `DAGSTER_AIRFLOW_ADMIN_PASSWORD` during the Airflow instance start up with values of your choice. For example:

``` sh
DAGSTER_AIRFLOW_ADMIN_USER=user DAGSTER_AIRFLOW_ADMIN_PASSWORD=passwd make celery-stack-up
```
