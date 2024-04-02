.SILENT:
ifndef .DEFAULT_GOAL
.DEFAULT_GOAL := manifests-help
endif

KUSTOMIZE_VERSION := v5.2.1
KUSTOMIZE := registry.k8s.io/kustomize/kustomize:$(KUSTOMIZE_VERSION)

AIRFLOW_ENV := $(shell echo $(AIRFLOW_ENV) | tr A-Z a-z)

PROJECT_SHORTNAME := dagster

_check-env:
	$(call check-defined, PROJECT_SHORTNAME)
	$(call check-defined, AIRFLOW_ENV)

ifneq ($(AIRFLOW_ENV),$(filter $(AIRFLOW_ENV),local))
$(error K8s environment "$(AIRFLOW_ENV)" is not supported)
endif

map-kustomization: _check-env
	$(info ### Mapping "$(PROJECT_SHORTNAME)" in "$(AIRFLOW_ENV)" kustomization.yaml ...)
	RELEASE_VERSION=$(MAKESTER__VERSION) venv/bin/makester --quiet templater --write\
 $(MAKESTER__PROJECT_DIR)/resources/k8s/kustomize/manifests/$(AIRFLOW_ENV)/kustomization.yaml.j2

generate-manifest: _check-env
	$(MAKESTER__DOCKER) run --rm\
 -v "$(MAKESTER__PROJECT_DIR)/resources/k8s/:/mnt"\
 $(KUSTOMIZE) build /mnt/kustomize/manifests/$(AIRFLOW_ENV)

dagster-local-manifest:
	$(info ### Test kustomize build dagster-local)
	$(MAKE) generate-manifeset PROJECT_SHORTNAME=dagster AIRFLOW_CUSTOM_ENV=local > tests/out/celery-executor/dagster-local.yaml

dagster-local-manifest-out:
	$(info ### Test kustomize build dagster-local
	$(MAKE) generate-manifest PROJECT_SHORTNAME=dagster AIRFLOW_CUSTOM_ENV=local

test-manifest: dagster-local-manifest

manifests-help:
	@echo "(makefiles/manifest.mk)\n\
  generate-manifest\n\
                  \"kustomize build\" of supported K8s manifests\n\
  test-manifest   Build the k8s manifests\n"

.PHONY: manifests-help
