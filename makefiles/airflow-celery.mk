.SILENT:
ifndef .DEFAULT_GOAL
.DEFAULT_GOAL := airflow-celery-help
endif

#
# CeleryExecutor commands in local development mode.
#
_compose-run:
	@MAKESTER__SERVICE_NAME=$(MAKESTER__SERVICE_NAME) $(MAKESTER__DOCKER_COMPOSE) \
 --file $(MAKESTER__PROJECT_DIR)/docker/docker-compose.yml $(COMPOSE_CMD)

_backoff:
	@venv/bin/makester backoff $(MAKESTER__LOCAL_IP) 8443 --detail "Airflow web UI"

# Display the docker compose configuration for the Airflow stack.
#
celery-stack-config: COMPOSE_CMD = config
celery-stack-config: _compose-run

# Create the Airflow stack.
#
celery-stack-up csu: COMPOSE_CMD = up -d
celery-stack-up csu: _compose-run
celery-stack-up csu:
	$(MAKE) _backoff

# Restart the Airflow worker in isolation.
#
celery-bump-worker: COMPOSE_CMD = up -d --no-deps --build --force-recreate worker
celery-bump-worker: _compose-run

# Destroy the Airflow stack.
#
celery-stack-down csd: COMPOSE_CMD = down --volumes
celery-stack-down csd: _compose-run

airflow-celery-help:
	@echo "(makefiles/airflow-celery.mk)\n\
  celery-bump-worker   Docker compose recreate Airflow stack worker\n\
  celery-stack-config  Docker compose config for Airflow stack in CeleryExecutor mode\n\
  celery-stack-down    Docker compose stop for Airflow stack in CeleryExecutor mode\n\
  celery-stack-up      Docker compose start for Airflow stack in CeleryExecutor mode\n"

.PHONY: airflow-celery-help
