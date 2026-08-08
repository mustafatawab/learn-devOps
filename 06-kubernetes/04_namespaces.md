# 04 - Namespaces

A complete beginner-friendly guide to Kubernetes Namespaces - how to organize, isolate, and manage resources inside your cluster.

---

## Table of Contents

1. [What is a Namespace?](#what-is-a-namespace)
2. [Why Namespaces Exist](#why-namespaces-exist)
3. [Default Namespaces](#default-namespaces)
4. [kube-system Namespace](#kube-system-namespace)
5. [Creating Namespaces](#creating-namespaces)
6. [Working with Namespaces](#working-with-namespaces)
7. [Resource Isolation](#resource-isolation)
8. [Resource Quotas](#resource-quotas)
9. [Cross-Namespace Communication](#cross-namespace-communication)
10. [Namespace Best Practices](#namespace-best-practices)
11. [Real World Example](#real-world-example)
12. [Essential Namespace Commands](#essential-namespace-commands)
13. [Quick Reference](#quick-reference)

---

## What is a Namespace?

A **Namespace** is a virtual cluster inside your physical Kubernetes cluster. Think of it as a **folder** that groups and isolates related resources.

Simple analogy - think of a Namespace like **floors in a building**:

```
🏢 Building (Kubernetes Cluster)
├── Floor 1 - default        ← resources with no specific floor
├── Floor 2 - kube-system    ← building management (don't touch!)
├── Floor 3 - production     ← live apps
├── Floor 4 - staging        ← testing before going live
└── Floor 5 - monitoring     ← dashboards and alerts
```

Each floor is completely separate:
- Resources on Floor 3 don't interfere with Floor 4
- Teams working on Floor 3 don't accidentally touch Floor 4
- You can set different rules for each floor

---

## Why Namespaces Exist

Without namespaces - everything in one big pile:

```
❌ Without namespaces:
Cluster
├── frontend-pod
├── backend-pod
├── database-pod
├── frontend-pod      ← ❌ name conflict! (team B also made one)
├── redis-pod
└── monitoring-pod    ← which app does this belong to?
```

Problems:
- **Name conflicts** - two teams can't both create a resource called `backend`
- **No isolation** - Team A can accidentally delete Team B's resources
- **No permissions** - can't give Team A access to only their resources
- **No organization** - 100 resources with no grouping = chaos

With namespaces - everything organized:

```
✅ With namespaces:
Cluster
├── namespace: team-a
│   ├── frontend-pod
│   └── backend-pod
├── namespace: team-b
│   ├── frontend-pod   ← ✅ same name is fine! different namespace
│   └── backend-pod
└── namespace: monitoring
    └── prometheus-pod
```

---

## Default Namespaces

When you install Kubernetes, it creates **4 namespaces automatically**:

```bash
kubectl get namespaces
```

```
NAME              STATUS
default           Active   ← your resources go here if not specified
kube-system       Active   ← Kubernetes internal components
kube-public       Active   ← publicly readable resources
kube-node-lease   Active   ← node heartbeat tracking
```

### default

Where your resources go when you don't specify a namespace:

```bash
kubectl run my-pod --image=nginx   # goes to default namespace
```

> In production - NEVER use default. Always create dedicated namespaces. default is fine for quick learning and experiments.

### kube-system

Where Kubernetes runs itself. Contains all the internal components that make the cluster work:

```bash
kubectl get pods -n kube-system
```

```
NAME                              READY   STATUS
coredns-668d6bf9bc-fpwjs          1/1     Running  ← DNS for the cluster
etcd-docker-desktop               1/1     Running  ← cluster database
kube-apiserver-docker-desktop     1/1     Running  ← API server
kube-controller-manager           1/1     Running  ← controller
kube-scheduler-docker-desktop     1/1     Running  ← scheduler
kube-proxy-m5cnx                  1/1     Running  ← networking
```

> Never deploy your apps to kube-system. Never delete or modify resources here. This is the engine room - breaking it breaks the entire cluster.

### kube-public

Readable by everyone, including unauthenticated users. Rarely used in practice. Contains basic cluster info.

### kube-node-lease

Used internally by Kubernetes for node heartbeats - checking if nodes are alive. You will never need to touch this.

---

## kube-system Namespace

Let's understand what's running inside kube-system in detail:

| Pod | What it does |
|-----|-------------|
| kube-apiserver | The brain - all kubectl commands go here first |
| etcd | The database - stores ALL cluster state (pods, services, configs) |
| kube-scheduler | Decides which Node a new Pod should run on |
| kube-controller-manager | Watches cluster state, fixes drift (e.g. restarts crashed pods) |
| coredns | DNS server - how Pods find each other by name |
| kube-proxy | Handles networking between Pods across nodes |
| storage-provisioner | Manages storage volumes |

Think of kube-system like the **IT department of a company**:
- They keep the building's infrastructure running
- You don't go into their server room and unplug things
- You just use the services they provide

---

## Creating Namespaces

### Method 1 - Command line (quick)

```bash
kubectl create namespace my-namespace
```

### Method 2 - YAML file (recommended for production)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
  labels:
    team: backend
    env: production
```

Apply it:

```bash
kubectl apply -f namespace.yaml
```

Why YAML is better:
- Version controlled in Git
- Reviewable in pull requests
- Reproducible across environments
- Can include labels and annotations

### Verify it was created

```bash
kubectl get namespaces
# or shorthand
kubectl get ns
```

---

## Working with Namespaces

### Adding a Pod to a namespace

Option A - Specify in YAML (recommended):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
spec:
  containers:
    - name: my-container
      image: nginx:alpine
```

Option B - Specify with kubectl flag:

```bash
kubectl run my-pod --image=nginx -n my-namespace
```

### Viewing resources in a namespace

```bash
# Pods in a specific namespace
kubectl get pods -n my-namespace

# Services in a specific namespace
kubectl get services -n my-namespace

# ALL resources in a namespace
kubectl get all -n my-namespace

# Resources across ALL namespaces
kubectl get pods --all-namespaces
kubectl get pods -A              # shorthand for --all-namespaces
```

### Setting a default namespace

Tired of typing -n my-namespace every time? Set a default:

```bash
kubectl config set-context --current --namespace=my-namespace
```

Now all commands use my-namespace by default:

```bash
kubectl get pods   # automatically uses my-namespace
```

Reset back to default:

```bash
kubectl config set-context --current --namespace=default
```

Check current context and namespace:

```bash
kubectl config current-context
kubectl config view --minify | grep namespace
```

---

## Resource Isolation

Namespaces provide **soft isolation** - they separate resources logically but don't provide network isolation by default.

### What IS isolated per namespace

```
Names        → two namespaces can have resources with the same name
RBAC         → permissions can be scoped to a namespace
Resource Quotas → CPU/RAM limits per namespace
ConfigMaps and Secrets → not shared between namespaces
```

### What is NOT isolated (by default)

```
Network      → Pods in different namespaces CAN talk to each other
               (you need NetworkPolicy to restrict this)
Nodes        → Pods from any namespace run on any node
StorageClasses → available cluster-wide
```

### Network isolation with NetworkPolicy

To truly isolate namespaces from each other, you need a NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: production
spec:
  podSelector: {}
  ingress:
    - from:
      - podSelector: {}
```

This blocks all incoming traffic from other namespaces - only Pods within production can talk to each other.

---

## Resource Quotas

You can limit how much CPU, memory, and how many objects a namespace can use. This prevents one team or app from consuming all cluster resources.

### Setting a ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: my-namespace-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "4Gi"
    limits.cpu: "4"
    limits.memory: "8Gi"
    pods: "20"
    services: "10"
    configmaps: "20"
    secrets: "20"
    persistentvolumeclaims: "5"
```

Apply it:

```bash
kubectl apply -f quota.yaml
```

Check quota usage:

```bash
kubectl describe resourcequota -n my-namespace
```

Output:

```
Name:            my-namespace-quota
Namespace:       my-namespace
Resource         Used   Hard
--------         ----   ----
limits.cpu       500m   4
limits.memory    256Mi  8Gi
pods             3      20
requests.cpu     250m   2
requests.memory  128Mi  4Gi
```

### LimitRange - default limits per Pod

ResourceQuota limits the whole namespace. LimitRange sets default limits for each Pod:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: my-limits
  namespace: my-namespace
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "256Mi"
      defaultRequest:
        cpu: "250m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "1Gi"
      min:
        cpu: "100m"
        memory: "64Mi"
```

---

## Cross-Namespace Communication

Pods in different namespaces **can** communicate with each other using the full DNS name:

```
<service-name>.<namespace>.svc.cluster.local
```

### Example

```
namespace: frontend
  Pod needs to call API in namespace: backend
```

In the frontend Pod environment variables:

```bash
# Wrong - only works within same namespace
API_URL=http://api-service:9000

# Correct - full DNS name for cross-namespace
API_URL=http://api-service.backend.svc.cluster.local:9000
```

### Test cross-namespace connectivity

```bash
# Run debug pod in frontend namespace
kubectl run debug --rm -it --image=busybox -n frontend -- sh

# From inside, try to reach API in backend namespace
wget -qO- http://api-service.backend.svc.cluster.local:9000
```

---

## Namespace Best Practices

### 1. Never use default in production

```bash
# Bad - everything in default
kubectl apply -f deployment.yaml

# Good - always specify namespace
kubectl apply -f deployment.yaml -n production
```

### 2. Use meaningful names

```bash
# Bad - vague names
kubectl create namespace ns1
kubectl create namespace test

# Good - descriptive names
kubectl create namespace production
kubectl create namespace staging
kubectl create namespace monitoring
kubectl create namespace team-backend
```

### 3. Common namespace patterns

By environment:
```
production   → live user traffic
staging      → final testing before production
development  → active development
```

By team:
```
team-frontend
team-backend
team-data
team-devops
```

By application:
```
atlas-edu
pharmacy-pos
monitoring
```

Combined (enterprise):
```
atlas-edu-production
atlas-edu-staging
atlas-edu-development
```

### 4. Always define namespaces in YAML

```yaml
metadata:
  name: my-pod
  namespace: production
```

### 5. Set resource quotas for every namespace

Prevents runaway processes from consuming all cluster resources:

```bash
kubectl apply -f quota.yaml -n production
kubectl apply -f quota.yaml -n staging
```

### 6. Label your namespaces

```yaml
metadata:
  name: production
  labels:
    env: production
    team: platform
    cost-center: "12345"
```

Labels help with filtering, monitoring, and cost tracking.

---

## Real World Example

Here is how to structure namespaces for **Atlas Edu** - a school management SaaS:

### Namespace structure

```
Cluster
├── namespace: atlas-edu-production    ← live users
├── namespace: atlas-edu-staging       ← pre-production testing
├── namespace: atlas-edu-development   ← active development
├── namespace: monitoring              ← Prometheus, Grafana
└── namespace: kube-system            ← Kubernetes internals
```

### Create all namespaces

```yaml
# namespaces.yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: atlas-edu-production
  labels:
    app: atlas-edu
    env: production

---
apiVersion: v1
kind: Namespace
metadata:
  name: atlas-edu-staging
  labels:
    app: atlas-edu
    env: staging

---
apiVersion: v1
kind: Namespace
metadata:
  name: atlas-edu-development
  labels:
    app: atlas-edu
    env: development

---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    purpose: observability
```

Apply all at once:

```bash
kubectl apply -f namespaces.yaml
```

### Resource quota for production

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: atlas-edu-production
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "50"
    services: "20"
```

### Deploy to specific namespace

```bash
# Deploy to production
kubectl apply -f deployment.yaml -n atlas-edu-production

# Deploy to staging
kubectl apply -f deployment.yaml -n atlas-edu-staging

# Check what's running in production
kubectl get all -n atlas-edu-production
```

### Different configs per namespace

Each namespace can have its own ConfigMaps and Secrets with different values:

```bash
# Production database
kubectl create secret generic db-secret \
  --from-literal=DATABASE_URL="postgresql://prod-server/atlas_edu" \
  -n atlas-edu-production

# Staging database
kubectl create secret generic db-secret \
  --from-literal=DATABASE_URL="postgresql://staging-server/atlas_edu" \
  -n atlas-edu-staging
```

Same Secret name, different values per namespace. Your Deployment YAML stays identical across environments.

---

## Essential Namespace Commands

```bash
# List namespaces
kubectl get namespaces
kubectl get ns

# Create namespace
kubectl create namespace my-namespace
kubectl create ns my-namespace

# Delete namespace (deletes EVERYTHING inside!)
kubectl delete namespace my-namespace
kubectl delete ns my-namespace

# Describe namespace
kubectl describe namespace my-namespace
kubectl describe ns my-namespace

# Create namespace from YAML
kubectl apply -f namespace.yaml

# Set default namespace for current session
kubectl config set-context --current --namespace=my-namespace

# Check current default namespace
kubectl config view --minify | grep namespace

# Reset to default namespace
kubectl config set-context --current --namespace=default

# Get resources in a namespace
kubectl get all -n my-namespace
kubectl get pods -n my-namespace
kubectl get services -n my-namespace
kubectl get deployments -n my-namespace
kubectl get configmaps -n my-namespace
kubectl get secrets -n my-namespace

# Get resources across ALL namespaces
kubectl get pods --all-namespaces
kubectl get pods -A
kubectl get all -A

# Apply resource to specific namespace
kubectl apply -f deployment.yaml -n my-namespace

# Check resource quotas
kubectl get resourcequota -n my-namespace
kubectl describe resourcequota -n my-namespace

# Check limit ranges
kubectl get limitrange -n my-namespace
```

---

## Quick Reference

### Namespace Cheat Sheet

```bash
kubectl get ns                          # list all namespaces
kubectl create ns <name>                # create namespace
kubectl delete ns <name>                # delete namespace + everything inside!
kubectl get all -n <name>              # all resources in namespace
kubectl get pods -A                     # pods in ALL namespaces
kubectl config set-context --current --namespace=<name>  # set default namespace
```

### DNS Naming

```
Same namespace:
  http://my-service:80

Different namespace:
  http://my-service.other-namespace.svc.cluster.local:80
```

### Production Namespace Pattern

```
production    → live users, strict quotas, limited access
staging       → pre-production testing, similar to production
development   → active development, relaxed quotas
monitoring    → Prometheus, Grafana, alerting
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using default in production | Always create dedicated namespaces |
| Forgetting -n namespace in commands | Set default namespace with kubectl config set-context |
| Deleting a namespace by accident | kubectl delete ns deletes EVERYTHING inside - be careful! |
| Pods can not find each other | Cross-namespace needs full DNS: service.namespace.svc.cluster.local |
| No resource limits | Always add ResourceQuota to prevent runaway resource usage |
| Vague namespace names | Use descriptive names: atlas-edu-production not prod |