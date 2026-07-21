# Kubernetes

Kubernetes (K8s) is an open-source platform that automates the deployment, scaling, and management of containerized applications. Originally developed by [Google](https://google.com), it functions as a container orchestrator, managing groups of containers (pods) across clusters of machines to ensure high availability, self-healing, and efficient resource utilization.

It does reconciliation of the cluster state to ensure that the cluster is in the desired state.

## Key Features and Capabilities

- **Automation**: Automates container deployment and replication.
- **Self-Healing**: Automatically restarts failed containers, replaces them, and reschedules them when nodes die.
- **Scaling**: Scales applications up or down automatically based on demand.
- **Load Balancing**: Distributes network traffic to maintain stable performance.
- **Storage Orchestration**: Mounts storage systems (local, public cloud) automatically.

## Core Components

| Component | Description |
|-----------|-------------|
| **Cluster** | A set of machines (nodes) that run containerized applications. |
| **Control Plane** | The "brain" of Kubernetes that makes global decisions about the cluster. |
| **Nodes** | Machines (virtual or physical) that run the application containers. |
| **Pods** | The smallest deployable units, containing one or more containers. |

## Managed Kubernetes Services (Cloud Providers)

| Provider | Service |
|----------|---------|
| Google | **GKE** - Google Kubernetes Engine |
| AWS | **EKS** - Amazon Elastic Kubernetes Service |
| Azure | **AKS** - Azure Kubernetes Service |
| DigitalOcean | **DOKS** - DigitalOcean Kubernetes |

> **Note**: `kubectl` is the CLI client tool to interact with a Kubernetes cluster.

---

## Cluster Information & Configuration

### View Cluster Information
```bash
kubectl cluster-info
```
Displays the Kubernetes control plane URL and other core services running in the cluster.

### View Kubernetes Configuration
```bash
kubectl config view
```
Shows the kubeconfig file contents (clusters, contexts, users).

### View Raw Configuration
```bash
kubectl config view --raw
```
Shows the complete merged kubeconfig including environment overrides.

### List All Contexts
```bash
kubectl config get-contexts
```
Displays all configured contexts (cluster + user + namespace combinations).

### Show Current Context
```bash
kubectl config current-context
```
Shows which context is currently active.

### Switch Context
```bash
kubectl config use-context <context-name>
```
Switches to a different context (e.g., `kubectl config use-context docker-desktop`).

### List Nodes in Cluster
```bash
kubectl get nodes
```
Shows all worker nodes registered in the cluster with their status.

### List Nodes (Wide Output)
```bash
kubectl get nodes -o wide
```
Shows nodes with additional details like internal IP and OS version.

### Check Kubectl and Cluster Version
```bash
kubectl version
```
Displays client and server version information.

---

## Namespaces

Namespaces provide logical isolation within a cluster.

### Why Use Namespaces?
1. **Scope Isolation** - Separate teams, environments, or microservices
2. **Policy Attachment** - Apply RBAC, quotas, and network policies per namespace
3. **Resource Accounting** - Track resource usage per team/project

### List Namespaces
```bash
kubectl get ns
```
Shows all namespaces in the cluster.

### Create Namespace
```bash
kubectl create ns <namespace-name>
```
Creates a new namespace (e.g., `kubectl create ns fundtransfer`).

### Delete Namespace
```bash
kubectl delete ns <namespace-name>
```
Deletes a namespace and all resources within it.

### View Events in Namespace
```bash
kubectl get events -n <namespace>
```
Shows recent events (scheduling, failures, scaling) in a namespace.

### View Pods in Namespace
```bash
kubectl get pods -n <namespace>
```
Lists all pods in a specific namespace.

---

## API Resources

### List API Resources
```bash
kubectl api-resources
```
Shows all resource types available in the cluster (pods, deployments, services, etc.).

### List API Versions
```bash
kubectl api-versions
```
Displays all API groups and versions supported by the cluster.

---

## Working with Pods

### Create a Pod
```bash
kubectl run <pod-name> --image=<image-name> --restart=Never -n <namespace>
```
Creates a single-container pod (imperative way).

**Example:**
```bash
kubectl run nginx --image=nginx:alpine --restart=Never -n nginx
```

### Create Pod with Labels
```bash
kubectl run <pod-name> --image=<image-name> --labels="key1=value1,key2=value2"
```
**Example:**
```bash
kubectl run fastapi-dev --image=ameenalam/cloud-native-fastapi:dev --labels="app=backend,stack=fastapi"
```

### List Pods
```bash
kubectl get pods
```
Shows all pods in the current namespace.

### List Pods with Label Selector
```bash
kubectl get pods -l app=backend
kubectl get pods -l stack=fastapi
kubectl get pods -l app=backend,stack=fastapi
```
Filters pods by label(s).

### View Pod Logs
```bash
kubectl logs <pod-name> -n <namespace>
```
Streams container logs (useful for debugging).

### Describe Pod (Detailed View)
```bash
kubectl describe pod <pod-name> -n <namespace>
```
Shows detailed pod information including events, conditions, and container state.

### Port Forward to Pod
```bash
kubectl port-forward pod/<pod-name> <local-port>:<pod-port>
```
Forwards a local port to a pod port (e.g., `kubectl port-forward pod/nginx 8000:80`).

### Run Temporary Debug Pod
```bash
kubectl run debug --image=busybox -it --rm --restart=Never -- /bin/sh
```
Creates an ephemeral pod for debugging, removed on exit.

### Run Pod and Show Environment Variables
```bash
kubectl run test --image=busybox -it --rm --restart=Never -- env
```

---

## RBAC (Role-Based Access Control)

RBAC controls who can do what in Kubernetes.

### RBAC Resources

| Resource | Scope | Description |
|----------|-------|-------------|
| **Role** | Namespace | Defines permissions within a namespace |
| **ClusterRole** | Cluster-wide | Defines permissions across the entire cluster |
| **RoleBinding** | Namespace | Binds a Role to users/service accounts |
| **ClusterRoleBinding** | Cluster-wide | Binds a ClusterRole to users/service accounts |

> **Principle**: Minimize blast radius - grant only the permissions needed.

### Create Service Account
```bash
kubectl create serviceaccount <name> -n <namespace>
```
**Example:**
```bash
kubectl create serviceaccount deployer -n fundtransfer
```

### Service Account (Dry Run - Generate YAML)
```bash
kubectl create serviceaccount deployer -n fundtransfer --dry-run=client -o yaml
```
Generates YAML without creating the resource (useful for version control).

### List Service Accounts
```bash
kubectl get serviceaccount -n <namespace>
kubectl get sa -n <namespace>
```

### Create Role (Declarative)
Create `role.yaml`:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: fundtransfer-deployer
  namespace: fundtransfer
rules:
  - apiGroups: ["apps"]
    resources: ["deployment", "replicaset"]
    verbs: ["get", "list", "create", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list"]
```

### Apply Role
```bash
kubectl apply -f role.yaml
```

### List Roles in Namespace
```bash
kubectl get role -n fundtransfer
```

### Create RoleBinding (Declarative)
Create `rolebinding.yaml`:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deployer-binding
  namespace: fundtransfer
subjects:
  - kind: ServiceAccount
    name: deployer
    namespace: fundtransfer
roleRef:
  kind: Role
  name: fundtransfer-deployer
  apiGroup: rbac.authorization.k8s.io
```

### Apply RoleBinding
```bash
kubectl apply -f rolebinding.yaml
```

### Check Permissions
```bash
kubectl auth can-i create deployments -n fundtransfer --as system:serviceaccount:fundtransfer:deployer
```
Verifies if a service account has specific permissions.

### Create Token for Service Account
```bash
kubectl create token <service-account-name> -n <namespace>
```
Generates a JWT token for service account authentication.

### Configure kubectl with Service Account Token
```bash
# Set credentials
kubectl config set-credentials deployer --token=<token>

# Create context
kubectl config set-context dev-context --user=deployer --namespace=fundtransfer --cluster=docker-desktop

# Switch to context
kubectl config use-context dev-context
```

### Rename Context
```bash
kubectl config rename-context <old-name> <new-name>
```
**Example:**
```bash
kubectl config rename-context docker-desktop admin@docker-desktop
```

---

## Kubectl Explain (Built-in Documentation)

Use `kubectl explain` to explore resource schemas:

```bash
kubectl explain Role
kubectl explain RoleBinding
kubectl explain RoleBinding.subjects
kubectl explain RoleBinding.subjects.kind
kubectl explain RoleBinding.subjects.name
kubectl explain RoleBinding.roleRef
```

---

## Useful Tips

### Create kubectl Alias
```bash
alias k=kubectl
```
Add to your shell config (`~/.zshrc` or `~/.bashrc`) for convenience.

### Pod Creation (Dry Run - Generate YAML)
```bash
kubectl run fastapi-dev --image=ameenalam/cloud-native-fastapi:dev \
  --labels="app=backend,stack=fastapi" \
  --dry-run=client -o yaml > fastapi-dev.yaml
```
Generates pod YAML for version control and reuse.

---

## Advanced Pod Operations

### Create Pod with Specific Port and Image Pull Policy
```bash
kubectl run fastapi-pod --image=hello_fastapi --image-pull-policy=Never --port=8000
```
Creates a pod with a specified container port and sets image pull policy to `Never` (uses only local images).

### Port Forward to Pod
```bash
kubectl port-forward <pod-name> <external-port>:<container-port>
kubectl port-forward <pod-name> 9000:8000
```
Forwards local port 9000 to container port 8000. Access the pod via `localhost:9000`.

### Execute Command in Pod (Interactive Shell)
```bash
kubectl exec -it <pod-name> -- /bin/sh
kubectl exec -it <pod-name> -- sh
```
Opens an interactive shell session inside a running container.

### Run Debug Pod (Ephemeral)
```bash
kubectl run debug --rm -it --image=busybox -- sh
```
Creates a temporary busybox pod for debugging, automatically removed when exited.

### Run Pod with Inline Command
```bash
kubectl run bb --image=busybox --restart=Never -- /bin/sh -c "echo hello"
```
Runs a pod that executes a single command and exits.

### Run Pod with Delayed Command
```bash
kubectl run bb2 --image=busybox --restart=Never -- /bin/sh -c "echo start && sleep 15 && echo hello"
```
Runs a pod that prints, waits 15 seconds, then prints again.

### Run Pod Interactively with Cleanup
```bash
kubectl run bb2 --image=busybox -it --rm --restart=Never -- /bin/sh -c "echo start && sleep 15 && echo hello"
```
Same as above but with interactive terminal and auto-removal.

### Follow Pod Logs (Streaming)
```bash
kubectl logs bb2 -f
```
Streams logs in real-time (follow mode).

### Get Pod IP Address
```bash
FASTAPI_IP=$(kubectl get pod fastapi-dev -o jsonpath='{.status.podIP}')
```
Stores the pod's IP address in a shell variable for use in subsequent commands.

### Test Pod Connectivity with wget
```bash
kubectl run bb2 --image=busybox -it --rm --restart=Never -- /bin/sh -c "wget -qO- $FASTAPI_IP:8000"
```
Runs a busybox pod to test HTTP connectivity to another pod's IP.

### List Pods by Label
```bash
kubectl get pod -l run=fastapi-dev
kubectl get pod -l app=backend
```
Filters pods by label key-value pairs.

### Create Pod with Multiple Labels
```bash
kubectl run fastapi-dev2 --image=ameenalam/cloud-native-fastapi:dev --labels="app=backend,stack=fastapi"
```
Creates a pod with multiple labels for better organization and filtering.

---

## ConfigMaps

ConfigMaps store non-sensitive configuration data as key-value pairs.

### Create ConfigMap from Literal
```bash
kubectl create configmap <configmap-name> --from-literal=API_URL=http://backend:8000
```
Creates a ConfigMap with a single key-value pair.

### Create ConfigMap (Dry Run - Generate YAML)
```bash
kubectl create configmap <configmap-name> --from-literal=API_URL=http://backend:8000 --dry-run=client -o yaml > configmap.yaml
```
Generates ConfigMap YAML for version control.

### Get ConfigMap
```bash
kubectl get configmap <configmap-name>
kubectl get cm <configmap-name>
```
Retrieves ConfigMap details.

---

## Deployments & Scaling

### Scale Deployment
```bash
kubectl scale deployment <deployment-name> --replicas=5
```
Scales a deployment to 5 replicas.

**Example:**
```bash
kubectl scale deployment progress-app --replicas=5
```

---

## Services & Networking

### List Services
```bash
kubectl get svc
```
Shows all services in the current namespace.

### List Endpoint Slices
```bash
kubectl get endpointslices
```
Shows endpoint slices (used by kube-proxy for service routing).

---

## RBAC - Imperative Commands

### Create Service Account (Dry Run)
```bash
kubectl create serviceaccount -n fundtransfer --dry-run=client -o yaml
```
Generates ServiceAccount YAML without creating it.

### Apply ServiceAccount Manifest
```bash
kubectl apply -f serviceaccount.yaml
```

### Create Role Imperatively
```bash
kubectl create role devuser-role --resources=pods --verb=get,list,update,create -n devteam --dry-run=client -o yaml
```
Generates a Role manifest imperatively.

### List Permissions for Current User
```bash
kubectl auth can-i --list
```
Shows all permissions the current user has.

### Check Permissions for Specific Action
```bash
kubectl auth can-i create deployments -n <namespace> --as system:serviceaccount:<namespace>:<serviceaccount-name>
```
Tests if a service account can perform a specific action.

### Delete RoleBinding
```bash
kubectl delete -f rolebinding.yaml
```
Removes a RoleBinding defined in a manifest.

---

## Context & User Management

### Create Service Account
```bash
kubectl create serviceaccount devuser -n devteam
```
Creates a new service account for a user/team.

### Create Token for Service Account
```bash
kubectl create token devuser -n devteam
```
Generates a JWT token for authentication.

### Configure kubectl with Token
```bash
kubectl config set-credentials devuser --token="<your-token-here>"
```
Sets up kubectl credentials using a service account token.

### List Namespaces with Specific User
```bash
kubectl get ns --user=devuser
```
Lists namespaces using alternate user credentials.

---

## Editing Resources

### Edit Pod (Interactive)
```bash
kubectl edit pod fastapi-dev
```
Opens the pod manifest in your default editor for live modifications.

> **Note**: Some fields cannot be edited after pod creation (e.g., container image for non-init containers).

---

## Quick Reference Table

### Cluster & Configuration
| Command | Description |
|---------|-------------|
| `kubectl cluster-info` | View cluster information |
| `kubectl config view` | View kubeconfig |
| `kubectl config get-contexts` | List all contexts |
| `kubectl config current-context` | Show active context |
| `kubectl config use-context <name>` | Switch context |
| `kubectl get nodes` | List cluster nodes |
| `kubectl get ns` | List namespaces |
| `kubectl create ns <name>` | Create namespace |
| `kubectl api-resources` | List all API resources |
| `kubectl api-versions` | List API versions |

### Pods
| Command | Description |
|---------|-------------|
| `kubectl run <name> --image=<img>` | Create a pod |
| `kubectl run <name> --image=<img> --port=<port>` | Create pod with port |
| `kubectl run <name> --image=<img> --labels="key=val"` | Create pod with labels |
| `kubectl get pods` | List pods |
| `kubectl get pods -l <label>` | Filter pods by label |
| `kubectl logs <pod> [-f]` | View/follow pod logs |
| `kubectl describe pod <name>` | Detailed pod info |
| `kubectl port-forward pod/<name> 9000:8000` | Forward port to pod |
| `kubectl exec -it <pod> -- /bin/sh` | Shell into pod |
| `kubectl delete pod <name>` | Delete pod |

### Debugging
| Command | Description |
|---------|-------------|
| `kubectl run debug --rm -it --image=busybox -- sh` | Temporary debug pod |
| `kubectl run bb --image=busybox -- env` | Show environment variables |
| `kubectl run bb --image=busybox -- /bin/sh -c "cmd"` | Run inline command |
| `kubectl get pod <name> -o jsonpath='{.status.podIP}'` | Get pod IP address |

### ConfigMaps
| Command | Description |
|---------|-------------|
| `kubectl create configmap <name> --from-literal=KEY=value` | Create ConfigMap |
| `kubectl create configmap <name> ... --dry-run=client -o yaml` | Generate ConfigMap YAML |
| `kubectl get configmap <name>` | Get ConfigMap |

### Deployments & Scaling
| Command | Description |
|---------|-------------|
| `kubectl scale deployment <name> --replicas=5` | Scale deployment |
| `kubectl get deployments` | List deployments |
| `kubectl edit pod <name>` | Edit resource interactively |

### Services & Networking
| Command | Description |
|---------|-------------|
| `kubectl get svc` | List services |
| `kubectl get endpointslices` | List endpoint slices |

### RBAC
| Command | Description |
|---------|-------------|
| `kubectl create sa <name> -n <ns>` | Create service account |
| `kubectl get sa -n <ns>` | List service accounts |
| `kubectl create token <sa> -n <ns>` | Generate SA token |
| `kubectl auth can-i <verb> <resource>` | Check permissions |
| `kubectl auth can-i --list` | List all permissions |
| `kubectl apply -f role.yaml` | Apply Role manifest |
| `kubectl apply -f rolebinding.yaml` | Apply RoleBinding manifest |
| `kubectl delete -f rolebinding.yaml` | Delete RoleBinding |

### Context & Users
| Command | Description |
|---------|-------------|
| `kubectl config set-credentials <name> --token=<token>` | Set user credentials |
| `kubectl config set-context <name> --user=<user>` | Create context |
| `kubectl get ns --user=<name>` | Use alternate credentials |
| `kubectl config rename-context <old> <new>` | Rename context |

### General
| Command | Description |
|---------|-------------|
| `kubectl apply -f <file.yaml>` | Apply manifest |
| `kubectl delete -f <file.yaml>` | Delete from manifest |
| `kubectl explain <resource>` | API documentation |
| `kubectl edit <resource> <name>` | Edit resource |
| `alias k=kubectl` | Create shorthand alias |
