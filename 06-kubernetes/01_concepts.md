# 01 - Kubernetes Concepts

A beginner-friendly guide to understanding Kubernetes from scratch - what it is, why it exists, and the core building blocks.

---

## Table of Contents

1. [What is Kubernetes?](#what-is-kubernetes)
2. [Why Kubernetes Exists](#why-kubernetes-exists)
3. [Docker Compose vs Kubernetes](#docker-compose-vs-kubernetes)
4. [Core Architecture](#core-architecture)
5. [Core Objects](#core-objects)
6. [Key Features](#key-features)
7. [Managed Kubernetes Services](#managed-kubernetes-services)
8. [kubectl - The CLI Tool](#kubectl--the-cli-tool)
9. [Declarative vs Imperative](#declarative-vs-imperative)
10. [YAML Manifest Structure](#yaml-manifest-structure)

---

## What is Kubernetes?

Kubernetes (K8s) is an open-source **container orchestration platform** that automates the deployment, scaling, and management of containerized applications. Originally developed by Google, it is now maintained by the Cloud Native Computing Foundation (CNCF).

> The name "Kubernetes" comes from Greek, meaning "helmsman" or "pilot" - the person who steers a ship. K8s is the helmsman of your containers.

In simple terms:

```
Docker     → runs one container
Kubernetes → manages thousands of containers across many servers
```

---

## Why Kubernetes Exists

Imagine your app goes viral - 10,000 users hit it at the same time. Your single server can't handle it.

```
Single server with Docker Compose:
  CPU hits 100% → requests queue up
  RAM fills up  → app crashes
  Users wait    → timeouts ❌
```

You need more servers. But managing containers across multiple servers manually is impossible:

```
❌ Which server should run which container?
❌ What if a server crashes - who restarts the containers?
❌ How do you update 100 containers without downtime?
❌ How do you add more servers when traffic grows?
```

**Kubernetes solves all of this automatically.**

Think of Kubernetes like a **smart restaurant manager**:
- Decides which chef (server) handles which order (container)
- If a chef faints (server crashes) → assigns their orders to others automatically
- Hires new chefs when it gets busy (auto-scaling)
- Fires chefs when it gets quiet (scale down)
- Updates the menu one chef at a time (rolling updates)

---

## Docker Compose vs Kubernetes

| | Docker Compose | Kubernetes |
|--|----------------|------------|
| Manages containers on | **1 server** | **Many servers** |
| Auto-scaling | ❌ Manual | ✅ Automatic |
| Self-healing | ❌ No | ✅ Yes |
| Rolling updates | ❌ No | ✅ Yes |
| Load balancing | ❌ Basic | ✅ Built-in |
| Production use | Small projects | Enterprise scale |
| Learning curve | Easy | Steeper |

```
Docker Compose → perfect for development and small deployments
Kubernetes     → production at scale, multiple servers
```

---

## Core Architecture

```
Kubernetes Cluster
├── Control Plane (the brain)
│   ├── kube-apiserver      → receives all kubectl commands
│   ├── etcd                → database storing ALL cluster state
│   ├── kube-scheduler      → decides which Node a Pod runs on
│   └── kube-controller     → watches cluster, makes corrections
│
└── Worker Nodes (the workers)
    ├── Node 1
    │   ├── kubelet         → talks to control plane, manages pods
    │   ├── kube-proxy      → handles networking between pods
    │   └── Pods            → your actual containers
    ├── Node 2
    └── Node 3
```

### Control Plane

The **brain** of Kubernetes - makes all decisions:

| Component | Role |
|-----------|------|
| `kube-apiserver` | Entry point for all kubectl commands |
| `etcd` | Key-value database storing all cluster state |
| `kube-scheduler` | Picks the best Node to run a Pod |
| `kube-controller-manager` | Watches cluster state, corrects drift |

### Worker Nodes

The **muscles** - where your apps actually run:

| Component | Role |
|-----------|------|
| `kubelet` | Agent on each Node, manages Pods |
| `kube-proxy` | Handles networking and Service routing |
| `Container Runtime` | Runs containers (Docker, containerd) |

> In Docker Desktop, your Mac acts as BOTH the control plane and worker node - a single-node cluster perfect for learning.

---

## Core Objects

### Cluster

A **Cluster** is the entire Kubernetes system - all nodes, all pods, all services working together.

```
Cluster = all nodes + control plane + all workloads
```

### Node

A **Node** is a single server (physical or virtual machine) inside the cluster. Pods run on Nodes.

```
kubectl get nodes
```

### Pod

A **Pod** is the smallest deployable unit in Kubernetes. It wraps one or more containers.

```
Pod = container(s) + networking + storage + metadata

Docker works with  → containers
Kubernetes works with → Pods
```

Why pods instead of raw containers?
- Kubernetes needs to add networking, storage, and metadata
- A Pod gives Kubernetes a manageable unit
- Containers inside a Pod share the same network and storage

```yaml
# Pod with one container (most common)
spec:
  containers:
    - name: my-app
      image: nginx:alpine

# Pod with two tightly coupled containers (rare)
spec:
  containers:
    - name: main-app
      image: my-app:latest
    - name: log-collector
      image: fluentd:latest
```

> In production - never create Pods directly. Use a **Deployment** instead.

### Deployment

A **Deployment** manages Pods for you:

```
You tell Deployment: "I want 3 copies of my app"
Deployment:
  ✅ Creates 3 Pods
  ✅ Restarts crashed Pods
  ✅ Updates Pods one at a time (rolling update)
  ✅ Rolls back if something goes wrong
```

### Service

A **Service** gives Pods a stable address. Pods come and go (crash, restart, scale) - their IPs change. A Service gives a **permanent entry point** that never changes.

```
Without Service:
  Pod IP changes every restart → other apps can't find it ❌

With Service:
  Service IP stays the same → always findable ✅
```

#### Three Service Types

**ClusterIP** - internal only:
```
Only reachable INSIDE the cluster
Use for: databases, internal APIs

Example:
  Backend → ClusterIP → Database ✅
  Internet → ClusterIP → ❌ not accessible
```

**NodePort** - external via port:
```
Exposes on a port on every Node (30000-32767)
Use for: development, testing

Example:
  Browser → localhost:30080 → your app ✅
```

**LoadBalancer** - external via clean URL:
```
Gets a public IP from cloud provider
Use for: production, public-facing apps

Local K8s → EXTERNAL-IP: localhost
Cloud K8s → EXTERNAL-IP: 34.123.45.67 (real public IP)
```

### Namespace

A **Namespace** is like a folder inside your cluster - it isolates and organizes resources.

```
Cluster
├── namespace: default      ← resources go here if not specified
├── namespace: kube-system  ← Kubernetes internal components (don't touch!)
├── namespace: production   ← your live apps
├── namespace: staging      ← testing environment
└── namespace: monitoring   ← Prometheus, Grafana
```

**Why namespaces?**
- **Isolation** - Team A can't accidentally touch Team B's resources
- **Organization** - staging vs production in same cluster
- **Permissions** - give access to only one namespace via RBAC
- **Resource limits** - limit CPU/RAM per namespace

> In production, NEVER use the `default` namespace. Always create custom namespaces.

---

## Key Features

### Horizontal Scaling

Add more Pod replicas when traffic grows:

```
Normal traffic:   3 Pods
Traffic spike:    Kubernetes adds 7 more → 10 Pods total
Traffic drops:    Kubernetes removes 7 → back to 3 Pods
```

### Auto-Scaling

Kubernetes can automatically scale based on CPU/memory usage - no manual intervention needed.

### Self-Healing

```
Pod crashes → Kubernetes detects it → restarts it automatically ✅
Node dies   → Kubernetes moves Pods to healthy nodes ✅
```

### Rolling Updates - Zero Downtime

Update your app without any downtime:

```
Pod 1 → update to v2 🔄 (Pod 2 & 3 still serving v1 ✅)
Pod 1 → v2 ready ✅
Pod 2 → update to v2 🔄 (Pod 1 & 3 serving ✅)
Pod 2 → v2 ready ✅
Pod 3 → update to v2 🔄 (Pod 1 & 2 serving ✅)
All done → zero downtime 🎉
```

### Rollback

If something goes wrong - revert instantly:

```bash
kubectl rollout undo deployment/my-app
```

---

## Managed Kubernetes Services

In production you don't manage the control plane yourself - cloud providers do it for you:

| Provider | Service | Description |
|----------|---------|-------------|
| Google | **GKE** - Google Kubernetes Engine | Best-in-class, easiest to start |
| AWS | **EKS** - Elastic Kubernetes Service | Most jobs require this |
| Azure | **AKS** - Azure Kubernetes Service | Best for Microsoft stack |
| DigitalOcean | **DOKS** - DigitalOcean Kubernetes | Simple, affordable |

**For learning locally:**

| Tool | Description |
|------|-------------|
| Docker Desktop | Built-in K8s - easiest to enable |
| minikube | Dedicated local K8s cluster |
| kind | Kubernetes in Docker |

---

## kubectl - The CLI Tool

`kubectl` is the command-line tool to talk to Kubernetes. Every command goes through `kube-apiserver`.

```
You type kubectl command
        ↓
kube-apiserver receives it
        ↓
Kubernetes does the work
        ↓
Result shown in terminal
```

### Essential Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl version

# Namespace commands
kubectl get namespaces
kubectl create namespace my-namespace
kubectl delete namespace my-namespace

# Pod commands
kubectl get pods
kubectl get pods -n <namespace>
kubectl get pods --all-namespaces
kubectl get pods -o wide          # extra details (IP, Node)
kubectl get pods -o yaml          # full YAML of the resource
kubectl describe pod <name>       # detailed info + events
kubectl delete pod <name>
kubectl logs <pod-name>
kubectl logs -f <pod-name>        # follow logs live
kubectl exec -it <pod-name> -- sh # shell into pod

# Apply/delete YAML manifests
kubectl apply -f <file.yaml>
kubectl delete -f <file.yaml>

# Port forwarding
kubectl port-forward pod/<name> 8080:80
kubectl port-forward service/<name> 8080:80

# Useful alias
alias k=kubectl
```

### Output Formats

```bash
kubectl get pods -o wide    # extra columns (IP, Node)
kubectl get pods -o yaml    # full YAML
kubectl get pods -o json    # full JSON
```

### Dry Run - Generate YAML without creating

```bash
kubectl run my-pod --image=nginx --dry-run=client -o yaml > pod.yaml
```

Generates YAML without actually creating anything - useful for version control.

---

## Declarative vs Imperative

**Imperative** - tell Kubernetes HOW to do something:
```bash
kubectl run my-pod --image=nginx
kubectl delete pod my-pod
```

**Declarative** - tell Kubernetes WHAT you want, it figures out HOW:
```bash
kubectl apply -f pod.yaml    # create or update
kubectl delete -f pod.yaml   # delete
```

> Always prefer **declarative** (YAML files) in production - it's version controlled, repeatable, and reviewable.

---

## YAML Manifest Structure

Every Kubernetes object follows the same YAML structure:

```yaml
apiVersion: v1          # API version (v1 for core, apps/v1 for Deployments)
kind: Pod               # type of object (Pod, Deployment, Service, etc.)
metadata:               # information about the object
  name: my-pod          # unique name in the namespace
  namespace: default    # which namespace (omit = default)
  labels:               # key-value tags for selecting/filtering
    app: my-app
    env: production
spec:                   # desired state - what you want
  containers:
    - name: my-container
      image: nginx:alpine
      ports:
        - containerPort: 80
```

### `apiVersion` Reference

| Object | apiVersion |
|--------|------------|
| Pod | `v1` |
| Service | `v1` |
| Namespace | `v1` |
| ConfigMap | `v1` |
| Secret | `v1` |
| Deployment | `apps/v1` |
| Ingress | `networking.k8s.io/v1` |

### Pod Status Reference

| Status | Meaning |
|--------|---------|
| `Running` | Container is running ✅ |
| `Pending` | Waiting to be scheduled on a Node |
| `Completed` | Container ran and exited successfully |
| `CrashLoopBackOff` | Container keeps crashing and restarting |
| `ImagePullBackOff` | Can't pull the Docker image (wrong name, no auth) |
| `Error` | Container exited with an error |
| `Terminating` | Pod is being deleted |

### Labels & Selectors

Labels are key-value pairs attached to objects. Selectors use labels to find objects:

```yaml
# Pod has label
metadata:
  labels:
    app: nginx       ← label

# Service uses selector to find that Pod
spec:
  selector:
    app: nginx       ← finds all pods with this label
```

This is the **glue** between Services and Pods. When a Pod restarts with a new IP - the Service finds it automatically because the label stays the same.