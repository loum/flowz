# syntax=docker/dockerfile:1.4

ARG PYTHON_MAJOR_MINOR_VERSION
ARG AIRFLOW_BASE_IMAGE

FROM $AIRFLOW_BASE_IMAGE as builder

USER root

ARG PYTHON_MAJOR_MINOR_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends\
 wget\
 ca-certificates\
 git\
 gcc\
 unzip\
 "python$PYTHON_MAJOR_MINOR_VERSION-dev" &&\
 apt-get autoremove -yqq --purge &&\
 rm -rf /var/lib/apt/lists/* &&\
 rm -rf /var/log/*

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048\
 -keyout /etc/ssl/private/airflow-selfsigned.key -out /etc/ssl/certs/airflow-selfsigned.crt\
 -subj "/C=AU/ST=VIC/L=Melbourne/O=Triple20/OU=GDM/CN=localhost"
# Note: need the explicit chown here for Buildkite runs as it appears
# https://docs.docker.com/engine/security/userns-remap/ is enabled.
RUN chown -R root:root /etc/ssl

# To resolve private repositories in GitHub.
RUN ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts

USER airflow
WORKDIR /home/airflow

# For local PyPI artifact builds.
ARG BUILT_DISTRIBUTION_NAME
COPY dist/$BUILT_DISTRIBUTION_NAME dist/

RUN --mount=type=ssh,uid=50000 python -m pip install\
 --no-compile\
 --no-cache-dir\
 --no-warn-script-location\
 dist/$BUILT_DISTRIBUTION_NAME &&\
 find .local/lib/python$PYTHON_MAJOR_MINOR_VERSION/site-packages/ -depth\
   \(\
     \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
     -o \
     \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
  \) -exec rm -rf '{}' +;

USER root
RUN chown -R root:root .local/lib

### builder stage end.

FROM $AIRFLOW_BASE_IMAGE AS main

USER root
RUN apt-get update && apt-get install -y --no-install-recommends\
 jq\
 libaio1\
 openjdk-11-jdk-headless &&\
 apt-get autoremove -yqq --purge &&\
 rm -rf /var/lib/apt/lists/* &&\
 rm -rf /var/log/*

ARG AIRFLOW_USER=airflow
ARG AIRFLOW_GROUP=root

ARG AIRFLOW_LOG_DIR=/var/log/airflow
WORKDIR $AIRFLOW_LOG_DIR
RUN chown -R $AIRFLOW_USER:$AIRFLOW_GROUP $AIRFLOW_LOG_DIR

# Create a "data" directory so that named volumes can be mounted to it
# while preserving ownership.
ARG AIRFLOW_DATA_DIR=/opt/airflow/data
WORKDIR $AIRFLOW_DATA_DIR
RUN chown -R $AIRFLOW_USER:$AIRFLOW_GROUP $AIRFLOW_DATA_DIR

# Note: need the explicit chown here for Buildkite runs as it appears
# https://docs.docker.com/engine/security/userns-remap/ is enabled.
COPY --from=builder --chown=root:root /etc/ssl/certs/airflow-selfsigned.crt /etc/ssl/certs/
WORKDIR /home/airflow/ssl/private
COPY --from=builder --chown=$AIRFLOW_USER:$AIRFLOW_GROUP /etc/ssl/private/airflow-selfsigned.key .

ENV TZ UTC
WORKDIR /home/airflow

ARG PYTHON_MAJOR_MINOR_VERSION
COPY --from=builder --chown=$AIRFLOW_USER:$AIRFLOW_GROUP\
 /home/airflow/.local/lib/python$PYTHON_MAJOR_MINOR_VERSION/site-packages\
 .local/lib/python$PYTHON_MAJOR_MINOR_VERSION/site-packages/

USER $AIRFLOW_USER
WORKDIR /opt/airflow
