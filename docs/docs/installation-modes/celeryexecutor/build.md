# Build

Containerisation of your workloads is a requirement for the [Celery Executor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/celery.html){target="blank"} installation type.

!!! note
    See [Makester's `docker` subsystem](https://loum.github.io/makester/makefiles/docker/){target="blank"} for more detailed container image operations.

The container image is based on a [customised variant](https://github.com/loum/airflow-base){target="blank"} of the [Apache Airflow project's Dockerfile](https://github.com/apache/airflow/blob/main/Dockerfile){target="blank"}. The main difference is that the `PYTHON_BASE_IMAGE` is overridden with [Ubuntu as the underlying OS](https://github.com/loum/python3-ubuntu){target="blank"}. This provides better currency to mitigate CVEs. The final Flowz Airflow image extends the customised base container image with the project's workflow capability (DAGs, operators and hooks).

## Container image validation in local environment

Local container image build and validation allows you to launch a running instance of Apache Airflow before pushing to the image repository.

!!! note
    Flowz embeds your workflow capability into the Flowz container image. As such, modifications to the workflow logic will require a fresh container image build.

### Build the container image for local testing
``` sh
make local-image-buildx
```

The conatiner image build process will created two tags:

- the SemVer taken from `src/flowz/VERSION`
- `latest`

!!! note
    See [Makester's versioning subsystem](https://loum.github.io/makester/makefiles/versioning/#generate-dynamic-version){target="blank"} on how Flowz maintains release versions.

### Search for built container image
``` sh
make image-search
```

Typical output based on SemVer value of `2.8.1-0.1.1` contained within `src/flowz/VERSION`:
``` sh title="Flowz container image tags."
REPOSITORY     TAG           IMAGE ID       CREATED         SIZE
loum/flowz   2.8.1-0.1.1   bcb2c5443e69   9 minutes ago   1.65GB
loum/flowz   latest        bcb2c5443e69   9 minutes ago   1.65GB
```

### Delete the container image
``` sh
make image-rm
```
