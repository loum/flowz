# Airflow instance runtime

Launch the Airflow webserver UI in [Celery Executor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/celery.html){target="blank"} mode to visualise and interact with dashboard:

## Start

/// tab | Makester
``` sh
make celery-stack-up
```
///

/// tab | Docker CLI
``` sh
docker compose --file docker/docker-compose.yml up -d
```
///

You can access your local Airflow webserver console via [https://localhost:8443](http://localhost:8443).

!!! note
    It is safe to ignore the certificate error exceptions raised by your browser as the stack is using a self-signed certificate.

!!! info
    Check the [credentials management](../../operations/bootstrap/auth.md#remote-executor-credentials-management) for instructions on Airflow webserver authentication.

## Stop

/// tab | Makester
``` sh
make celery-stack-down
```
///

/// tab | Docker CLI
``` sh
docker compose --file docker/docker-compose.yml down
```
///

## Docker files

Dagster Apache Airflow in CeleryExecutor mode is delivered as a containerised service. Use Docker `compose` to standup the services.

### Configuration

/// tab | Makester
``` sh
make celery-stack-config
```
///

/// tab | Docker CLI
``` sh
docker compose --file docker/docker-compose.yml config
```
///


The targeted [Apache Airflow configuration](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html){target="blank"} values are listed below:

``` sh title="Apache Airflow CeleryExecutor environment settings."
--8<-- "docker/files/celery-executor"
```

The environment variables are fed into the `docker-compose.yml`:
``` sh title="Apache Airflow CeleryExecutor Docker compose file."
--8<-- "docker/docker-compose.yml"
```

## Dagster default container image

Use the following `shell` snippet if you are only interested in sampling the [default Dagster container image](https://hub.docker.com/r/loum/dagster){target="blank"}:

``` sh
for i in $(curl -s https://raw.githubusercontent.com/loum/dagster/main/docker/files/celery-executor | grep -v "^#"); do export $i; done && curl -s https://raw.githubusercontent.com/loum/dagster/main/docker/docker-compose.yml |\
 docker compose -f - up -d
```

For this simple demo usecase, the default Airflow webserver login credentials are `airflow`:`airflow`.
