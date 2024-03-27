# Sealed Secrets

Sealed secrets provides us with a mechanism to store secrets in Git. More details can be
found at ["Sealed Secrets" for Kubernetes](https://github.com/bitnami-labs/sealed-secrets/).

Install [kubeseal](https://github.com/bitnami-labs/sealed-secrets#kubeseal) to create a
Sealed Secret as a yaml file.

## Set up the environment

The creation of the Sealed Secrets is managed with a set of helper scripts. As the scripts are
dependent on sensitive resources that are stored offline, follow these preliminary set up steps

### Source the Kubernetes cluster certificates

Download the target K8s cluster certificate:

- `dev-primary`: <https://argocd.workflow-services.hirer-analytics.dev.outfra.xyz/v1/cert.pem>
- `prod-primary`: <https://argocd.workflow-services.seek-analytics.prod.outfra.xyz/v1/cert.pem>

Place the `cert.pem` under your local `~/.ssh` directory so that it identifiable. You will need
the patch to the `pem` file to create the Sealed Secrets. For example:

``` sh
mv cert.pm ~/.ssh/dev-primary.pem
```

### Source the application secrets

The application service secrets need to be securely stored in an offline location. When ready to
generate the Sealed Secrets, copy the secrets file to `resources/scripts/sealed-secrets-env.sh`.

!!! warning
    Application service secrets are sourced by the Sealed Secret scripts and need to be placed at
    `resources/scripts/sealed-secrets-env.sh`. Do not commit this file into the code repository.

## Creating the Sealed Secrets

Common settings used in the Sealed Secret scripts include:

- `AIRFLOW_NAMESPACE`: The Kubernetes namespace that the Airflow instance has been deployed to.
- `AIRFLOW_ENV`: The Airflow environment. This names the Sealed Secret accordingly and should
    align with the `AIRFLOW_CUSTOM_ENV` setting.
- `K8S_CERTIFICATE`: The Bitnami Sealed Secret public certificate that is associated with the
    target Kubernetes cluster.

The helper scripts should create the Sealed Secret as YAML and place the new file in the
appropriate `resources/kustomize/hapi/*` directory. You will need to manually adjust your Airflow
instances `kustomization.yaml.j2` file to pull in the new resource.

On completion, you will need to generate the new `kustomization.yaml`. For example:

``` sh
make map-kustomization PROJECT_SHORTNAME=hapi AIRFLOW_CUSTOM_ENV=dev-primary
```

The new Sealed Secret and Airflow instance `kustomization.yaml*` files can be commit into the
source code repository.

### Fernet key

``` sh
resources/scripts/airflow-fernet-sealed-secret.sh -h
```

``` sh title="airflow-fernet-sealed-secret.sh help."
K8s Sealed Secret generator.

Syntax: airflow-fernet-sealed-secret.sh -n <AIRFLOW_NAMESPACE> -e <AIRFLOW_ENV> -c <K8S_CERTIFICATE> [-h]
options:
-h     Print this Help
-n     K8s namespace that hosts Airflow
-e     Airflow env from <dev-primary|prod-primary>
-c     K8s certificate location
```

Example:

``` sh
resources/scripts/airflow-fernet-sealed-secret.sh -n dev-primary -e dev-primary -c $HOME/.ssh/dev-primary.pem
```

``` sh title="Sample output."
resources/scripts/airflow-fernet-sealed-secret.sh -n dev-primary -e dev-primary -c $HOME/.ssh/dev-primary.pem

### Sealed Secret airflow-fernet-sealed-secret.sh started ...
### Fernet sealed secret for Airflow instance dev-primary
### Fernet key: ***
### Kubernetes cert: $HOME/.ssh/dev-primary.pem
### Sealed Secret airflow-fernet-sealed-secret.sh finished.
###
```

New or updated Sealed Secret placed at
`resources/kustomize/hapi/celery-executor/dev-primary/resources/airflow-fernet-secrets-dev-primary-sealedsecret.yaml`.

### Airflow webserver secret

``` sh
resources/scripts/airflow-webserver-sealed-secret.sh -h
```

``` sh title="airflow-webserver-sealed-secret.sh help."
K8s Sealed Secret generator.

Syntax: airflow-webserver-sealed-secret.sh -n <AIRFLOW_NAMESPACE> -e <AIRFLOW_ENV> -c <K8S_CERTIFICATE> [-h]
options:
-h     Print this Help
-n     K8s namespace that hosts Airflow
-e     Airflow env from <dev-primary|prod-primary>
-c     K8s certificate location
```

Example:

``` sh
resources/scripts/airflow-webserver-sealed-secret.sh -n dev-primary -e dev-primary -c $HOME/.ssh/dev-primary.pem

### Sealed Secret airflow-webserver-sealed-secret.sh started ...
### Webserver secret sealed secret for Airflow instance dev-primary
### Webserver secret key: ***
### Kubernetes cert: $HOME/.ssh/dev-primary.pem
### Sealed Secret airflow-webserver-sealed-secret.sh finished.
###
```

New or updated Sealed Secret placed at
`resources/kustomize/hapi/celery-executor/dev-primary/resources/airflow-webserver-secrets-dev-primary-sealedsecret.yaml`.

### Airflow console UI login credentials

``` sh
K8s Sealed Secret generator.

Syntax: airflow-user-sealed-secret.sh -n <AIRFLOW_NAMESPACE> -e <AIRFLOW_ENV> -c <K8S_CERTIFICATE> [-h]
options:
-h     Print this Help
-n     K8s namespace that hosts Airflow
-e     Airflow env from <dev-primary|prod-primary>
-c     K8s certificate location
```

Example:

``` sh
resources/scripts/airflow-user-sealed-secret.sh -n dev-primary -e dev-primary -c $HOME/.ssh/dev-primary.pem

### Sealed Secret airflow-user-sealed-secret.sh started ...
### Airflow user for Airflow instance dev-primary: ***
### Airflow password for Airflow instance dev-primary: ***
### Kubernetes cert: $HOME/.ssh/dev-primary.pem
### Sealed Secret airflow-user-sealed-secret.sh finished.
###
```

New or updated Sealed Secret placed at
`resources/kustomize/hapi/celery-executor/dev-primary/resources/airflow-user-secrets-dev-primary-sealedsecret.yaml`.
