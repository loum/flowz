.SILENT:
ifndef .DEFAULT_GOAL
.DEFAULT_GOAL := airflow-sequential-help
endif

# Prime the local Airflow LocalExecutor environment variables.
#
AIRFLOW_HOME := $(PWD)/airflow
AIRFLOW_CUSTOM_ENV ?= local
AIRFLOW_ENV := $(AIRFLOW_CUSTOM_ENV)

ifeq (, $(filter-out local-airflow-start local-list-dags _webserver _scheduler,$(MAKECMDGOALS)))
include resources/files/environment/local
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' $(PWD)/resources/files/environment/local)
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))
endif

# Silence SQLAlchemy 2.0 compatibility warnings.
export SQLALCHEMY_SILENCE_UBER_WARNING ?= 1

# Add target here if needed by "airflow" SequentialExecutor runtime.

# Flowz environment variables.
$(eval $(shell echo export AIRFLOW_HOME=$(AIRFLOW_HOME)))
$(eval $(shell echo export AIRFLOW_CUSTOM_ENV=$(AIRFLOW_CUSTOM_ENV)))

# Start Airflow in SequentialExecutor mode.
#
_local-reset-start:
	@$(shell which pkill) airflow || true

local-airflow-start: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
local-airflow-start: _local-reset-start
	@$(MAKE) _scheduler & $(MAKE) _webserver && kill $! 2>/dev/null || true

# Reset the SequentialExecutor environment.
#
_delete-airflow:
	$(info ### Deleting AIRFLOW_HOME at "$(AIRFLOW_HOME)")
	@$(shell which rm) -fr $(AIRFLOW_HOME)

_link-webserver-config:
	$(info ### Creating custom webserver-config at $(AIRFLOW_HOME)/webserver_config.py)
	@$(shell which mkdir) -p $(AIRFLOW_HOME)
	@flowz config dbauth --public-role admin > $(AIRFLOW_HOME)/webserver_config.py

_link-dags:
	@$(shell which ln) -s $(PWD)/src/flowz/dags/ $(AIRFLOW_HOME)
	@$(shell which ln) -s $(PWD)/src/flowz/plugins/ $(AIRFLOW_HOME)

_CMD ?= --help
_airflow:
	@venv/bin/airflow $(_CMD)

_local-migrate-db: _CMD = db migrate
_local-migrate-db: _airflow

local-airflow-reset: AIRFLOW_CUSTOM_ENV = $(AIRFLOW_ENV)
local-airflow-reset: _delete-airflow _link-webserver-config _link-dags
	$(MAKE) _local-migrate-db

# SequentialExecutor commands in local development mode.
#
local-db-shell: _CMD = db shell
local-db-shell: _airflow

local-airflow-version: _CMD = version
local-airflow-version: _airflow

_scheduler: _CMD = scheduler
_scheduler: _airflow

_webserver: _CMD = webserver
_webserver: _airflow

local-list-dags: AIRFLOW_CUSTOM_ENV := $(AIRFLOW_ENV)
local-list-dags: _CMD = dags list
local-list-dags: _airflow

# Run a DAG on the CLI.
#
_check-dag-to-run:
	$(call check-defined, DAG_TO_RUN)

local-run-dag: _check-dag-to-run
	$(shell which echo) "yes" |\
 $(MAKE) airflow\
 _CMD="dags backfill --subdir src/flowz/dags --reset-dagruns -s 2024-01-01 -e 2024-01-01 $(DAG_TO_RUN)"

# Force a re-run of the bootstrap DAG.
#
local-reset-bootstrap: AIRFLOW_CUSTOM_ENV := $(AIRFLOW_ENV)
local-reset-bootstrap:
	$(info ### Reset the BOOTSTRAP DAG)
	@venv/bin/flowz reset bootstrap

airflow-sequential-help:
	@echo "(makefiles/airflow-sequential.mk)\n\
  local-airflow-reset  Destroy Airflow environment at \"AIRFLOW_HOME\" and rebuild in LOCAL context\n\
  local-airflow-start  Start Airflow in Sequential Executor mode LOCAL context (Ctrl-C to stop)\n\
  local-airflow-version\n\
                       Airflow version currently installed in the development environment\n\
  local-reset-bootstrap\n\
                       Clear the BOOTSTRAP DAG to force a re-run\n\
  local-db-shell       Start shell to local Airflow database (set _CMD=\"shell\")\n\
  local-list-dags      List all the DAGs in LOCAL context\n\
  local-run-dag        Run DAG denoted by \"DAG_TO_RUN\" on the CLI\n"

.PHONY: airflow-sequential-help
