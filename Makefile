.SILENT:
.DEFAULT_GOAL := help

MAKESTER__REPO_NAME := loum

include makester/makefiles/makester.mk
include makester/makefiles/docker.mk
include makester/makefiles/compose.mk
include makester/makefiles/python-venv.mk
include makester/makefiles/versioning.mk

GITVERSION_VERSION := 5.10.3-alpine.3.14-6.0
GITVERSION_CONFIG := makester/sample/GitVersion.yml

# Add current Python virtual environment to path.
export PATH := 3env/bin:$(PATH)
export PYTHONPATH := src

# APP_ENV is used in setup.py.
ifndef APP_ENV
export APP_ENV := local
else
export APP_ENV := $(APP_ENV)
endif

# Add target here if needed by "airflow" LocalExecutor runtime.
AIRFLOW_HOME ?= $(PWD)/airflow
AF_VARS_TARGETS = print-AIRFLOW__CORE__DAGS_FOLDER pristine start airflow init-db list-dags
ifeq ($(MAKECMDGOALS), $(filter $(MAKECMDGOALS), $(AF_VARS_TARGETS)))
$(info ### including envfile)
include envfile
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' $(PWD)/envfile)
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))
endif

AIRFLOW_CUSTOM_ENV ?= local
$(eval $(shell echo export AIRFLOW_HOME=$(AIRFLOW_HOME)))
$(eval $(shell echo export AIRFLOW_CUSTOM_ENV=$(AIRFLOW_CUSTOM_ENV)))

pristine: init reset-airflow

init: WHEEL := .wheelhouse
init: clear-env makester-requirements .makester/env.mk
	$(info ### Installing "$(MAKESTER__PROJECT_NAME)" and dependencies ...)
	$(MAKE) pip-editable

AIRFLOW_ENV := $(AIRFLOW_CUSTOM_ENV)
reset-airflow: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
reset-airflow: delete-airflow link-webserver-config airflow-version link-dags
	$(MAKE) init-db

delete-airflow:
	$(info ### Deleting AIRFLOW_HOME at "$(AIRFLOW_HOME)")
	@$(shell which rm) -fr $(AIRFLOW_HOME)

link-webserver-config: release-version
link-webserver-config:
	$(info ### Creating custom webserver-config at $(AIRFLOW_HOME)/webserver_config.py)
	@$(shell which mkdir) -p $(AIRFLOW_HOME)
	@airflow-webserver config dbauth > $(AIRFLOW_HOME)/webserver_config.py

link-dags:
	@$(shell which ln) -s $(PWD)/src/dagster/dags/ $(AIRFLOW_HOME)
	@$(shell which ln) -s $(PWD)/src/dagster/plugins/ $(AIRFLOW_HOME)

start: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
start: reset-start
	@$(MAKE) scheduler & $(MAKE) webserver && kill $! 2>/dev/null

reset-start:
	@$(shell which pkill) airflow || true

CMD ?= --help
airflow:
	@airflow $(CMD)

db-shell: CMD = db shell
airflow-version: CMD = version
init-db: CMD = db init
scheduler: CMD = scheduler
webserver: CMD = webserver
list-dags: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
list-dags: CMD = dags list

check-dag-to-run:
	$(call check_defined, DAG_TO_RUN)

run-dag: check-dag-to-run
	$(shell which echo) "yes" |\
 $(MAKE) airflow\
 CMD="dags backfill --subdir src/dagster/dags --reset-dagruns -s 2020-01-01 -e 2020-01-01 $(DAG_TO_RUN)"

db-shell airflow-version init-db scheduler webserver list-dags: airflow

TESTS_TO_RUN := $(if $(TESTS),$(TESTS),tests)
PRIME_TEST_CONTEXT ?= true
quick-tests: PRIME_TEST_CONTEXT := false
quick-tests: fixture-tests

tests: fixture-tests

fixture-tests :
	PROJECT_SOURCE_DIR=src/dagster\
 AIRFLOW_PRIME_TEST_CONTEXT=$(PRIME_TEST_CONTEXT)\
 $(PYTHON) -m pytest\
 --override-ini log_cli=true\
 --override-ini junit_family=xunit2\
 --log-cli-level=INFO -vv\
 --exitfirst\
 --cov-config tests/.coveragerc\
 --pythonwarnings ignore\
 --cov src/dagster\
 --junitxml tests/junit.xml\
 $(TESTS_TO_RUN)

reset-bootstrap: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
reset-bootstrap:
	$(info ### Reset the BOOTSTRAP DAG)
	@airflow-webserver reset bootstrap

docs:
	@sphinx-build -b html docsource docs

docs-live:
	cd docs; $(PYTHON) -m http.server --bind 0.0.0.0 8999

package: WHEEL=.wheelhouse
package: APP_ENV=prod
package: release-version

git-tag-version: release-version
	$(GIT) fetch
	$(info ### Creating Git tag $(MAKESTER__RELEASE_VERSION))
	$(GIT) tag $(MAKESTER__RELEASE_VERSION)

git-tag-push: release-version
	$(info ### Pushing Git tag $(MAKESTER__RELEASE_VERSION))
	$(GIT) push origin $(MAKESTER__RELEASE_VERSION)

export PYTHON_MAJOR_MINOR_VERSION := 3.10
export DAGS_REPO ?= .wheelhouse/dagster-$(MAKESTER__RELEASE_VERSION)-py3-none-any.whl
export AIRFLOW_VERSION := 2.4.0
AIRFLOW_BASE_IMAGE ?= loum/airflow-base:jammy-$(AIRFLOW_VERSION)
OPENJDK_11_HEADLESS := 11.0.16+8-0ubuntu1~22.04
MAKESTER__BUILD_COMMAND = $(DOCKER) build\
 --no-cache\
 --build-arg DAGS_REPO=$(DAGS_REPO)\
 --build-arg PYTHON_MAJOR_MINOR_VERSION=$(PYTHON_MAJOR_MINOR_VERSION)\
 --build-arg OPENJDK_11_HEADLESS=$(OPENJDK_11_HEADLESS)\
 --build-arg AIRFLOW_BASE_IMAGE=$(AIRFLOW_BASE_IMAGE)\
 -t $(MAKESTER__IMAGE_TAG_ALIAS) -f docker/Dockerfile .
build-image: release-version

export SITE_PACKAGES_NAME ?= dagster

# Override MAKESTER__SERVICE_NAME to match the Airflow DAG deploy context.
MAKESTER__SERVICE_NAME ?= $(MAKESTER__REPO_NAME)/dagster

# Image versioning follows the format "<airflow-version>-<airflow-dags-tag>-<image-release-number>"
MAKESTER__VERSION = $(AIRFLOW_VERSION)-$(MAKESTER__RELEASE_VERSION)
MAKESTER__RELEASE_NUMBER ?= 1

export MAKESTER__IMAGE_TAG_ALIAS = $(MAKESTER__SERVICE_NAME):$(MAKESTER__VERSION)-$(MAKESTER__RELEASE_NUMBER)

.makester/env.mk: Makefile
	-@$(shell which mkdir) -p .makester
	-@$(PYTHON) makester/utils/templatester.py\
 --quiet\
 --write\
 --mapping docker/files/mapping/celery-executor.json\
 docker/files/celery-executor.j2 > $@

# Add target here if needed by "airflow" CeleryExecutor runtime.
COMPOSE_VARS_TARGETS = stack-config stack-up stack-down export-vars bump-worker
ifeq ($(MAKECMDGOALS), $(filter $(MAKECMDGOALS), $(COMPOSE_VARS_TARGETS)))
-include .makester/env.mk
COMPOSE_VARS = $(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' .makester/env.mk)
endif

export-vars:
	$(foreach v,$(COMPOSE_VARS),$(eval $(shell echo export $(v)="$($(v))")))

backoff:
	@$(PYTHON) makester/scripts/backoff -d "Airflow web UI" -p $(AIRFLOW__WEBSERVER__WEB_SERVER_PORT) localhost

compose-run: export-vars
	@MAKESTER__SERVICE_NAME=$(MAKESTER__SERVICE_NAME)\
 $(DOCKER_COMPOSE) --file $(MAKESTER__PROJECT_DIR)/docker/docker-compose.yml\
 -f docker/docker-compose.yml $(COMPOSE_CMD)

stack-config: COMPOSE_CMD = config
init-airflow-db: COMPOSE_CMD = up init-db
build-airflow: COMPOSE_CMD = up --scale init-db=0 -d
destroy-airflow: COMPOSE_CMD = down
bump-worker: COMPOSE_CMD = up -d --no-deps --build --force-recreate worker
stack-config init-airflow-db build-airflow destroy-airflow bump-worker: compose-run

stack-up: export-vars release-version
	$(MAKE) -s init-airflow-db
	$(MAKE) -s build-airflow
	$(MAKE) -s backoff
stack-down: export-vars
	$(MAKE) -s destroy-airflow

build-all: package build-image

deps:
	pipdeptree

lint:
	-@pylint $(MAKESTER__PROJECT_DIR)/src

pyspark:
	-@pyspark

help: release-version makester-help docker-help python-venv-help versioning-help
	@echo "(Makefile)\n\
  airflow              Run any \"airflow\" by setting CMD (defaults to \"CMD=--help\")\n\
  airflow-version      Run \"airflow version\" (set CMD=\"version\")\n\
  build-all            Special target to build the Python wheel and Docker image in one step\n\
  bump-worker          Docker compose recreate Airflow stack worker (refresh AWS creds)\n\
  db-shell             Run \"airflow shell\" (set CMD=\"shell\")\n\
  deps                 Display PyPI package dependency tree\n\
  docs                 Generate code based docs with Sphinx\n\
  docs-live            View docs via web browser\n\
  git-tag-push         Push Git tag $(MAKESTER__VERSION)\n\
  git-tag-version      Create Git tag $(MAKESTER__VERSION)\n\
  init                 Build the local Python-based virtual environment\n\
  init-db              Initialise the Airflow database\n\
  link-dags            Link project DAGs to Airflow environment at \"AIRFLOW_HOME\"\n\
  lint                 Lint the code base\n\
  list-dags            List all the DAGs in LOCAL context\n\
  pristine             Convenience target bundling clear-env, init and reset in LOCAL context\n\
  pypspark             Start the PyPI pyspark interpreter in virtual env context\n\
  reset-airflow        Destroy Airflow environment at \"AIRFLOW_HOME\" and rebuild in LOCAL context\n\
  reset-bootstrap      Clear the BOOTSTRAP DAG to force a re-run\n\
  run-dag              Run DAG denoted by \"DAG_TO_RUN\" on the CLI\n\
  stack-config         Docker compose config for Airflow stack in CeleryExecutor mode\n\
  stack-down           Docker compose stop for Airflow stack in CeleryExecutor mode\n\
  stack-up             Docker compose start for Airflow stack in CeleryExecutor mode\n\
  start                Start Airflow in Sequential Executor mode LOCAL context (Ctrl-C to stop)\n\
  tests                Run code test suite\n"

.PHONY: help airflow docs .makester/env.mk
