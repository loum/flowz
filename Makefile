.SILENT:
.DEFAULT_GOAL := help

MAKESTER__INCLUDES := py docker compose versioning docs
MAKESTER__REPO_NAME := loum

include makester/makefiles/makester.mk
include makefiles/airflow-celery.mk
include makefiles/airflow-sequential.mk
include makefiles/container-images.mk

#
# Makester overrides.
#
MAKESTER__GITVERSION_CONFIG := GitVersion.yml
MAKESTER__VERSION_FILE := $(MAKESTER__PYTHON_PROJECT_ROOT)/VERSION

# Simulate Airflow, when running dynamically adds three directories to the sys.path.
export PYTHONPATH := "$(MAKESTER__PROJECT_DIR)/src:$(MAKESTER__PYTHON_PROJECT_ROOT)/dags:$(MAKESTER__PYTHON_PROJECT_ROOT)/plugins:$(MAKESTER__PYTHON_PROJECT_ROOT)/config"

# Container image build.
#
# Image versioning follows the format "<airflow-version>-<airflow-dags-tag>-<image-release-number>"
#
export AIRFLOW_VERSION := 2.8.3
MAKESTER__VERSION := $(AIRFLOW_VERSION)-$(MAKESTER__RELEASE_VERSION)
MAKESTER__RELEASE_NUMBER ?= 1

MAKESTER__IMAGE_TARGET_TAG := $(AIRFLOW_VERSION)-$(MAKESTER__RELEASE_VERSION)

# MAKESTER__IMAGE_TAG_ALIAS needs an explicit assignment to ensure correct
# MAKESTER__RELEASE_VERSION is picked up during the container image build.
#
MAKESTER__IMAGE_TAG_ALIAS := $(MAKESTER__SERVICE_NAME):$(MAKESTER__IMAGE_TARGET_TAG)
export PYTHON_MAJOR_MINOR_VERSION := 3.11
AIRFLOW_BASE_IMAGE ?= loum/airflow-base:jammy-$(AIRFLOW_VERSION)
BUILT_DISTRIBUTION_NAME := $(MAKESTER__PROJECT_NAME)-$(MAKESTER__RELEASE_VERSION)-py3-none-any.whl
MAKESTER__BUILD_COMMAND := --rm --no-cache\
 --build-arg BUILT_DISTRIBUTION_NAME=$(BUILT_DISTRIBUTION_NAME)\
 --build-arg PYTHON_MAJOR_MINOR_VERSION=$(PYTHON_MAJOR_MINOR_VERSION)\
 --build-arg AIRFLOW_BASE_IMAGE=$(AIRFLOW_BASE_IMAGE)\
 --tag $(MAKESTER__IMAGE_TAG_ALIAS)\
 --tag $(MAKESTER__SERVICE_NAME):latest\
 --file docker/Dockerfile .

#
# Local Makefile targets.
#
_venv-init: py-venv-clear py-venv-init

# Build the local development environment.
#
init-dev: _venv-init py-install-makester
	MAKESTER__PIP_INSTALL_EXTRAS=dev $(MAKE) py-install-extras

# Streamlined production packages.
#
init: _venv-init
	$(MAKE) py-install

# Prime Airflow in local development environment.
#
pristine: init-dev local-airflow-reset

# Dagster test harness.
#
TESTS_TO_RUN := $(if $(TESTS),$(TESTS),tests)
PRIME_TEST_CONTEXT ?= true
quick-tests: PRIME_TEST_CONTEXT := false
quick-tests: fixture-tests

ifeq ($(TESTS_TO_RUN),tests)
  _COVERAGE := --cov src --cov-config tests/.coveragerc
endif

tests: fixture-tests

fixture-tests:
	PROJECT_SOURCE_DIR=src/dagster\
 AIRFLOW__DAGSESH__PRIME_TEST_CONTEXT=$(PRIME_TEST_CONTEXT)\
 PYSPARK_PYTHON=$(MAKESTER__PYTHON) $(MAKESTER__PYTHON) -m pytest\
 --override-ini log_cli=true\
 --override-ini junit_family=xunit2\
 --log-cli-level=INFO -vv\
 --exitfirst\
 --pythonwarnings ignore\
 $(_COVERAGE)\
 --junitxml tests/junit.xml\
 -p tests.dagster.dataframes\
 $(TESTS_TO_RUN)

tests-pristine: py-vars vars init-dev tests

# Launch the PySpark CLI.
#
ifndef DRIVER_MEMORY
  DRIVER_MEMORY := 2g
endif
export DRIVER_MEMORY := $(DRIVER_MEMORY)

pyspark:
	@PYSPARK_PYTHON=$(MAKESTER__PYTHON) pyspark --driver-memory=$(DRIVER_MEMORY)

help: makester-help
	@echo "(Makefile)\n\
  airflow              Run any \"airflow\" by setting CMD (defaults to \"CMD=--help\")\n\
  pristine             Convenience target bundling clear-env, init and reset in LOCAL context\n\
  pyspark              Start the PyPI pyspark interpreter in virtual env context\n\
  tests                Run code test suite\n\
  tests-pristine       Convenience target to build pristine environment and run tests\n"
	$(MAKE) airflow-celery-help
	$(MAKE) airflow-sequential-help
	$(MAKE) container-images-help

.PHONY: help airflow
