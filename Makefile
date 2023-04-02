.SILENT:
.DEFAULT_GOAL := help

MAKESTER__INCLUDES := py docker compose versioning docs
MAKESTER__REPO_NAME := loum

include makester/makefiles/makester.mk

#
# Makester overrides.
#
MAKESTER__VERSION_FILE := $(MAKESTER__PYTHON_PROJECT_ROOT)/VERSION

# Simulate Airflow, when running dynamically adds three directories to the sys.path.
export PYTHONPATH := "$(MAKESTER__PROJECT_DIR)/src:$(MAKESTER__PYTHON_PROJECT_ROOT)/dags:$(MAKESTER__PYTHON_PROJECT_ROOT)/plugins:$(MAKESTER__PYTHON_PROJECT_ROOT)/config"

# Image versioning follows the format "<airflow-version>-<airflow-dags-tag>-<image-release-number>"
export AIRFLOW_VERSION := 2.4.3
MAKESTER__VERSION := $(AIRFLOW_VERSION)-$(MAKESTER__RELEASE_VERSION)
MAKESTER__RELEASE_NUMBER ?= 1

MAKESTER__IMAGE_TARGET_TAG := $(AIRFLOW_VERSION)-$(MAKESTER__RELEASE_VERSION)

# MAKESTER__IMAGE_TAG_ALIAS needs an explicit assignment to ensure correct
# MAKESTER__RELEASE_VERSION is picked up during the container image build.
export MAKESTER__IMAGE_TAG_ALIAS := $(MAKESTER__SERVICE_NAME):$(MAKESTER__IMAGE_TARGET_TAG)

# Container image build.
export PYTHON_MAJOR_MINOR_VERSION := 3.10
AIRFLOW_BASE_IMAGE ?= loum/airflow-base:jammy-$(AIRFLOW_VERSION)
OPENJDK_11_HEADLESS ?= 11.0.18+10-0ubuntu1~22.04
BUILT_DISTRIBUTION_NAME := $(MAKESTER__PROJECT_NAME)-$(MAKESTER__RELEASE_VERSION)-py3-none-any.whl
MAKESTER__BUILD_COMMAND := --rm --no-cache\
 --build-arg BUILT_DISTRIBUTION_NAME=$(BUILT_DISTRIBUTION_NAME)\
 --build-arg PYTHON_MAJOR_MINOR_VERSION=$(PYTHON_MAJOR_MINOR_VERSION)\
 --build-arg OPENJDK_11_HEADLESS=$(OPENJDK_11_HEADLESS)\
 --build-arg AIRFLOW_BASE_IMAGE=$(AIRFLOW_BASE_IMAGE)\
 --tag $(MAKESTER__IMAGE_TAG_ALIAS)\
 --file docker/Dockerfile .

#
# Local Makefile targets.
#
# Silence SQLAlchemy 2.0 compatibility warnings.
export SQLALCHEMY_SILENCE_UBER_WARNING ?= 1

# Add target here if needed by "airflow" LocalExecutor runtime.
AIRFLOW_HOME ?= $(PWD)/airflow

# Prime the local Airflow LocalExecutor environment variables.
include resources/files/environment/local
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' $(PWD)/resources/files/environment/local)
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))

# Dagster environment variables.
AIRFLOW_CUSTOM_ENV ?= local
$(eval $(shell echo export AIRFLOW_HOME=$(AIRFLOW_HOME)))
$(eval $(shell echo export AIRFLOW_CUSTOM_ENV=$(AIRFLOW_CUSTOM_ENV)))

_venv-init: py-venv-clear py-venv-init

# Build the local development environment.
init-dev: _venv-init py-install-makester
	MAKESTER__PIP_INSTALL_EXTRAS=dev $(MAKE) py-install-extras

# Streamlined production packages.
init: _venv-init
	$(MAKE) py-install

# Prime Airflow in local development environment.
pristine: init-dev local-airflow-reset

AIRFLOW_ENV := $(AIRFLOW_CUSTOM_ENV)
local-airflow-reset: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
local-airflow-reset: _delete-airflow _link-webserver-config _local-airflow-version _link-dags
	$(MAKE) _local-init-db

_delete-airflow:
	$(info ### Deleting AIRFLOW_HOME at "$(AIRFLOW_HOME)")
	@$(shell which rm) -fr $(AIRFLOW_HOME)

_link-webserver-config:
	$(info ### Creating custom webserver-config at $(AIRFLOW_HOME)/webserver_config.py)
	@$(shell which mkdir) -p $(AIRFLOW_HOME)
	@dagster config dbauth > $(AIRFLOW_HOME)/webserver_config.py

_link-dags:
	@$(shell which ln) -s $(PWD)/src/dagster/dags/ $(AIRFLOW_HOME)
	@$(shell which ln) -s $(PWD)/src/dagster/plugins/ $(AIRFLOW_HOME)

local-airflow-start: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
local-airflow-start: _local-reset-start
	@$(MAKE) scheduler & $(MAKE) webserver && kill $! 2>/dev/null || true

_local-reset-start:
	@$(shell which pkill) airflow || true

CMD ?= --help
airflow:
	@airflow $(CMD)

local-db-shell: CMD = db shell
_local-airflow-version: CMD = version
_local-init-db: CMD = db init
scheduler: CMD = scheduler
webserver: CMD = webserver

local-list-dags: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
local-list-dags: CMD = dags list

check-dag-to-run:
	$(call check-defined, DAG_TO_RUN)

local-run-dag: check-dag-to-run
	$(shell which echo) "yes" |\
 $(MAKE) airflow\
 CMD="dags backfill --subdir src/dagster/dags --reset-dagruns -s 2023-01-01 -e 2023-01-01 $(DAG_TO_RUN)"

local-db-shell _local-airflow-version _local-init-db scheduler webserver local-list-dags: airflow

TESTS_TO_RUN := $(if $(TESTS),$(TESTS),tests)
PRIME_TEST_CONTEXT ?= true
quick-tests: PRIME_TEST_CONTEXT := false
quick-tests: fixture-tests

tests: fixture-tests

fixture-tests :
	PROJECT_SOURCE_DIR=src/dagster\
 AIRFLOW__DAGSESH__PRIME_TEST_CONTEXT=$(PRIME_TEST_CONTEXT)\
 $(MAKESTER__PYTHON) -m pytest\
 --override-ini log_cli=true\
 --override-ini junit_family=xunit2\
 --log-cli-level=INFO -vv\
 --exitfirst\
 --cov-config tests/.coveragerc\
 --pythonwarnings ignore\
 --cov src/dagster\
 --junitxml tests/junit.xml\
 -p tests.dagster.dataframes\
 $(TESTS_TO_RUN)

reset-bootstrap: AIRFLOW_CUSTOM_ENV := $(AIRFLOW_ENV)
reset-bootstrap:
	$(info ### Reset the BOOTSTRAP DAG)
	@dagster reset bootstrap

_backoff:
	@venv/bin/makester backoff $(MAKESTER__LOCAL_IP) 8443 --detail "Airflow web UI"

image-pull-into-docker:
	$(info ### Pulling local registry image $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION) into docker)
	$(MAKESTER__DOCKER) pull $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION)

image-tag-in-docker: image-pull-into-docker
	$(info ### Tagging local registry image $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION) => $(MAKESTER__STATIC_SERVICE_NAME):$(MAKESTER__VERSION))
	$(MAKESTER__DOCKER) tag $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION) $(MAKESTER__STATIC_SERVICE_NAME):$(MAKESTER__VERSION)

image-transfer: image-tag-in-docker
	$(info ### Deleting pulled image $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION))
	$(MAKESTER__DOCKER) rmi $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION)

multi-arch-build-test: image-registry-start image-buildx-builder
	$(MAKE) multi-arch-build
	$(MAKE) image-transfer
	$(MAKE) image-registry-stop

multi-arch-build:
	$(MAKE) gitversion-release
	$(MAKE) py-distribution
	$(MAKE) MAKESTER__DOCKER_DRIVER_OUTPUT=push MAKESTER__DOCKER_PLATFORM=linux/arm64,linux/amd64 image-buildx

_compose-run:
	@MAKESTER__SERVICE_NAME=$(MAKESTER__SERVICE_NAME) $(MAKESTER__DOCKER_COMPOSE) \
 --file $(MAKESTER__PROJECT_DIR)/docker/docker-compose.yml $(COMPOSE_CMD)

_celery-airflow-down: COMPOSE_CMD = down --volumes
_celery-airflow-up: COMPOSE_CMD = up --scale init-db=0 -d
_celery-init-db: COMPOSE_CMD = up init-db
celery-bump-worker: COMPOSE_CMD = up -d --no-deps --build --force-recreate worker
celery-stack-config: COMPOSE_CMD = config

_celery-airflow-down _celery-airflow-up _celery-init-db celery-bump-worker celery-stack-config: _compose-run

celery-stack-up csu:
	$(MAKE) _celery-init-db
	$(MAKE) _celery-airflow-up
	$(MAKE) _backoff

celery-stack-down csd:
	$(MAKE) _celery-airflow-down

pyspark:
	-@pyspark

help: makester-help
	@echo "(Makefile)\n\
  airflow              Run any \"airflow\" by setting CMD (defaults to \"CMD=--help\")\n\
  celery-bump-worker   Docker compose recreate Airflow stack worker (refresh AWS creds)\n\
  celery-stack-config  Docker compose config for Airflow stack in CeleryExecutor mode\n\
  celery-stack-down    Docker compose stop for Airflow stack in CeleryExecutor mode\n\
  celery-stack-up      Docker compose start for Airflow stack in CeleryExecutor mode\n\
  local-airflow-reset  Destroy Airflow environment at \"AIRFLOW_HOME\" and rebuild in LOCAL context\n\
  local-airflow-start  Start Airflow in Sequential Executor mode LOCAL context (Ctrl-C to stop)\n\
  local-db-shell       Start shell to local Airflow database (set CMD=\"shell\")\n\
  local-list-dags      List all the DAGs in LOCAL context\n\
  local-run-dag        Run DAG denoted by \"DAG_TO_RUN\" on the CLI\n\
  multi-arch-build     Multi-platform container image build for \n\
  multi-arch-build-test\n\
					   Shake-out multi-platform container image build locally\n\
  pristine             Convenience target bundling clear-env, init and reset in LOCAL context\n\
  pyspark              Start the PyPI pyspark interpreter in virtual env context\n\
  reset-bootstrap      Clear the BOOTSTRAP DAG to force a re-run\n\
  tests                Run code test suite\n"

.PHONY: help airflow
