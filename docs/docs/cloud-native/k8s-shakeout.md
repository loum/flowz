# Getting ready to deploy to Kubernetes

!!! note
    The following steps will require [MicroK8s](https://microk8s.io/){target="blank"} to be installed on your local
    workstation. See [Makester's MicroK8s getting started reference](https://loum.github.io/makester/makefiles/k8s/microk8s/#getting-started){target="blank"}.

Dagster provides cloud native tooling to shakeout the container image before deploying to the Kubernetes cluster.

1. Start the local MicroK8s cluster.
``` sh
make microk8s-up
```
This will expose the local test Kubernetes dashboard. Authenticate with test credentials provided
in the output:
``` sh title="Test Kubernetes dashboard credentials."
2023-04-24 12:08:57 logga [INFO]: Checking host:port 192.168.1.211:19443 MicroK8s Kubernetes dashboard ...
2023-04-24 12:08:58 logga [INFO]: Port 19443 ready
### Login to the MicroK8s Kubernetes dashboard with following token:
eyJhbGciOiJ...
```

1. Start the local Argo CD service.
``` sh
make argocd-up
```
This will expose the local test Argo CD server UI. Authenticate with test credentials provided
in the output:
``` sh title="Test Argo CD server credentials."
2023-04-24 10:39:17 logga [INFO]: Checking host:port 192.168.1.211:20443 Argo CD API server ...
2023-04-24 10:39:18 logga [INFO]: Port 20443 ready
### Argo CD API Server address forwarded to: https://192.168.1.211:20443
### Argo CD API Server log output can be found at <$HOME>/.makester/argocd-dashboard.out
### Login to the Argo CD API Server as user "admin" with following password:
zRF2...
```

1. Inject the new `hapi` container image into the MicroK8s image cache.

    !!! note
        Repeat this step when a new image is created. You may need to delete any pre-existing
        container images:
        ``` sh
        make image-cache-del
        ```

    The `hapi` container image created is known to Docker, not Kubernetes. This is because your
    local Docker daemon is not part of the MicroK8s Kubernetes cluster. We need to export the built
    image from the local Docker daemon and inject it into the MicroK8s image cache:
    ``` sh
    make image-cache-add
    ```

1. Argo CD follows the GitOps pattern of using Git repositories as the source of truth for defining
the desired application state. `hapi` presents the Kubernetes manifests as a `kustomize` application.
During development and shakeout of the `kustomize` capability, it may be preferable to serve your
local repository with `git deamon` via the `local-serve-repo` recipe:
``` sh
make local-serve-repo
```
Make note of the URI that serves the current repository via `git daemon` as this will be used to
configure the Argo CD application's `--repo` switch:
``` sh title='Git daemon URI "git://192.168.1.211/hapi" example.'
### Serving Git repo as "git://192.168.1.211/hapi"
```

1. Create the Kubernetes namespace to deploy to:
``` sh
make microk8s-namespace-add K8S_NAMESPACE=<TARGET_KUBERNETES_NAMESPACE>
```
For example:
``` sh  title='Creating the example Kubernetes namespace "hapi-airflow-local"'
make microk8s-namespace-add K8S_NAMESPACE=hapi-airflow-local
```

1. Create the Argo CD application from the local Git repostiory. First, log into the Argo CD CLI:
``` sh
make argocd-cli-login
```
Next, create the Argo CD application with the Git daemon URI from the `local-serve-repo` recipe:
``` sh
argocd app create <ARGOCD_APP_NAME>\
 --repo <GIT_DAEMON_URI>\
 --path <LOCAL_PATH_TO_KUSTOMIZATION_YAML_FILE>\
 --dest-server https://kubernetes.default.svc\
 --dest-namespace <KUBERNETES_CLUSTER_NAMESPACE>
```
For example:
``` sh title="Argo CD application create example."
argocd app create hapi-airflow-local\
 --repo git://192.168.1.211/hirer-analytics-pipeline-integrations\
 --path resources/manifests/sample/celery-executor/local\
 --dest-server https://kubernetes.default.svc\
 --dest-namespace hapi-airflow-local
```

1. Simulate an application deployment by forcing a manual sync operations:
``` sh
argocd app sync <ARGOCD_APP_NAME> --local <LOCAL_PATH_TO_KUSTOMIZATION_YAML_FILE>
```
For example:
``` sh title="Argo CD application manual sync example."
argocd app sync hapi-airflow-local --local resources/manifests/sample/celery-executor/local
```

1. Establish a port-forward to connect to the Apache Airflow console. The follow example uses
port `28889`:
``` sh
microk8s kubectl port-forward svc/webserver -n default 28889:8889
```
Browse to [http://localhost:28889](http://localhost:28889) to access the Apache Airflow console login.
The default test account credentials are `airflow`:`airflow`.

1. Clean up.
``` sh
make image-cache-del
make argocd-down
make microk8s-down
```
