# 02 — Pods

A complete beginner-friendly guide to Pods — the smallest and most fundamental unit in Kubernetes.

---

## Table of Contents

1. [What is a Pod?](#what-is-a-pod)
2. [Pod vs Container](#pod-vs-container)
3. [Single Container vs Multi Container Pods](#single-container-vs-multi-container-pods)
4. [Your First Pod YAML](#your-first-pod-yaml)
5. [Pod Lifecycle](#pod-lifecycle)
6. [Pod Status Reference](#pod-status-reference)
7. [Labels & Selectors](#labels--selectors)
8. [Namespaces & Pods](#namespaces--pods)
9. [Accessing Pods](#accessing-pods)
10. [Debugging Pods](#debugging-pods)
11. [Why You Should Never Create Pods Directly](#why-you-should-never-create-pods-directly)
12. [Essential Pod Commands](#essential-pod-commands)
13. [Quick Reference](#quick-reference)

---

## What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes. Think of it as a wrapper around your container(s) that Kubernetes can manage.

Simple mental model:

```
Docker world  → you work with containers
K8s world     → you work with Pods
```

Just like in OOP:

```
Image     = Class / Blueprint
Container = Object / Instance
Pod       = Object + networking + storage + metadata that K8s needs
```

Kubernetes cannot manage raw containers directly — it needs the extra information a Pod provides (IP address, storage, health checks, etc.) to do its job properly.

---

## Pod vs Container

People often confuse Pods with containers. Here's the key difference:

| | Container | Pod |
|--|-----------|-----|
| What it is | Running instance of an image | Wrapper around container(s) |
| Managed by | Docker | Kubernetes |
| Has its own IP | ❌ | ✅ |
| Has storage volumes | ❌ | ✅ |
| Has health checks | ❌ (basic) | ✅ |
| Lifecycle managed | You manage | Kubernetes manages |

A Pod adds everything Kubernetes needs on top of a container:

```
Pod
├── Container (your app)
├── IP address (assigned by Kubernetes)
├── Storage volumes (shared between containers)
├── Health checks (liveness/readiness probes)
└── Metadata (labels, annotations, namespace)
```

---

## Single Container vs Multi Container Pods

### Single Container Pod (most common)

One Pod = One container. This is what you'll use 99% of the time:

```
Pod
└── Container (your Next.js app / Express API / FastAPI)
```

### Multi Container Pod (rare, specific use cases)

Sometimes two containers need to work **very closely together** — sharing the same network and storage. In that case, put them in the same Pod:

```
Pod
├── Main container (your app)
└── Sidecar container (helper — logging, proxy, sync)
```

**Common sidecar patterns:**

```
Pod
├── App container         → serves your API
└── Log collector         → ships logs to Elasticsearch

Pod
├── App container         → your service
└── Service mesh proxy    → handles encryption (Istio/Envoy)

Pod
├── App container         → reads local files
└── Git sync container    → keeps files up to date from Git repo
```

> **Rule of thumb:** Put containers in the same Pod only if they MUST share network/storage and can't work independently. Otherwise, use separate Pods.

---

## Your First Pod YAML

Every Kubernetes object is defined in YAML. Here's a simple Pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-first-pod
  namespace: default
  labels:
    app: nginx
    env: learning
spec:
  containers:
    - name: nginx-container
      image: nginx:alpine
      ports:
        - containerPort: 80
```

### Breaking it down line by line:

```yaml
apiVersion: v1
```
The Kubernetes API version for this resource. Pods use `v1` (core API group).

```yaml
kind: Pod
```
The type of Kubernetes object we're creating.

```yaml
metadata:
  name: my-first-pod
```
The unique name of this Pod inside its namespace. Two Pods in the same namespace cannot have the same name.

```yaml
  namespace: default
```
Which namespace this Pod belongs to. If omitted, goes to `default`.

```yaml
  labels:
    app: nginx
    env: learning
```
Key-value tags attached to the Pod. Used by Services to find this Pod, and by you to filter/organize.

```yaml
spec:
```
The desired state — what you want Kubernetes to create.

```yaml
  containers:
    - name: nginx-container
      image: nginx:alpine
```
A list of containers. The `-` makes it a list item. `name` is the container name, `image` is the Docker image.

```yaml
      ports:
        - containerPort: 80
```
Documents which port the container listens on. This is **metadata only** — it doesn't actually open the port. Opening happens through a Service.

---

### Pod with Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-api-pod
  namespace: default
  labels:
    app: api
spec:
  containers:
    - name: api-container
      image: node:22-alpine
      ports:
        - containerPort: 3000
      env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3000"
        - name: DATABASE_URL
          value: "postgresql://user:pass@db:5432/mydb"
```

### Pod with Resource Limits

Always set resource limits in production — prevents one Pod from consuming all server resources:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-api-pod
spec:
  containers:
    - name: api-container
      image: node:22-alpine
      resources:
        requests:              # minimum guaranteed resources
          memory: "128Mi"      # 128 megabytes RAM
          cpu: "250m"          # 250 millicores (0.25 CPU)
        limits:                # maximum allowed resources
          memory: "256Mi"      # 256 megabytes RAM
          cpu: "500m"          # 500 millicores (0.5 CPU)
```

**`requests` vs `limits`:**
```
requests → minimum Kubernetes guarantees to the Pod
limits   → maximum the Pod can ever use
```

Think of it like a hotel:
```
requests = the room you booked (guaranteed)
limits   = the maximum room service you can order
```

### Pod with Image Pull Policy

```yaml
spec:
  containers:
    - name: my-app
      image: my-local-image:latest
      imagePullPolicy: Never    # use local image only (never pull from registry)
```

**Image pull policies:**

| Policy | Behavior |
|--------|----------|
| `Always` | Always pull from registry (even if exists locally) |
| `IfNotPresent` | Pull only if not already on the Node |
| `Never` | Never pull — use local image only |

> Use `imagePullPolicy: Never` when practicing with local images in Docker Desktop.

---

## Pod Lifecycle

A Pod goes through several phases during its life:

```
Pod created
    ↓
Pending        → waiting to be scheduled on a Node
    ↓
Init (optional) → init containers run first (one-off setup tasks)
    ↓
Running        → all containers are running
    ↓
Succeeded      → all containers exited with code 0 (one-off tasks)
OR
Failed         → at least one container exited with non-zero code
    ↓
Terminating    → Pod is being deleted (graceful shutdown)
    ↓
Deleted
```

### What happens when a Pod starts:

```
1. Kubernetes scheduler picks a Node
2. kubelet on that Node pulls the Docker image
3. Container runtime (Docker) starts the container
4. Kubernetes assigns an IP to the Pod
5. Container starts running your app
6. Health checks begin (if configured)
```

### What happens when a Pod is deleted:

```
1. Pod enters Terminating state
2. Kubernetes stops sending new traffic to this Pod
3. App receives SIGTERM signal → starts graceful shutdown
4. After 30 seconds (default) → SIGKILL if still running
5. Pod is removed from the cluster
```

> **Important:** Pods are **ephemeral** — they're designed to be temporary. Don't store important data inside a Pod — use Volumes instead.

---

## Pod Status Reference

| Status | Meaning | What to do |
|--------|---------|------------|
| `Pending` | Waiting to be scheduled | Check node resources, check events |
| `Running` | All containers running ✅ | All good! |
| `Succeeded` | Completed successfully ✅ | Normal for one-off tasks |
| `Failed` | Exited with error | Check logs: `kubectl logs <pod>` |
| `CrashLoopBackOff` | Keeps crashing and restarting | Check logs, fix your app |
| `ImagePullBackOff` | Can't pull Docker image | Check image name, registry access |
| `ErrImagePull` | Image pull failed | Same as above |
| `Terminating` | Being deleted | Normal — wait for it |
| `OOMKilled` | Ran out of memory | Increase memory limits |
| `ContainerCreating` | Image pulling, starting | Wait a moment |

### READY column explained

```
kubectl get pods
NAME      READY   STATUS
my-pod    1/1     Running    ← 1 container running out of 1 total ✅
my-pod    0/1     Pending    ← 0 containers running out of 1 total
my-pod    2/3     Running    ← 2 out of 3 containers running (multi-container pod)
```

---

## Labels & Selectors

Labels are **key-value pairs** attached to Pods (and other objects). They are the most important organizational tool in Kubernetes.

### Adding Labels to a Pod

```yaml
metadata:
  labels:
    app: atlas-edu          # app name
    tier: backend           # frontend / backend / database
    env: production         # environment
    version: "1.0.0"        # version
```

### Why Labels Matter

**1. Services use labels to find Pods:**
```yaml
# Service selector
spec:
  selector:
    app: atlas-edu    # finds ALL pods with this label

# If a Pod crashes and restarts — new Pod still has the same label
# Service automatically finds it ✅
```

**2. You use labels to filter pods:**
```bash
kubectl get pods -l app=atlas-edu
kubectl get pods -l env=production
kubectl get pods -l app=atlas-edu,env=production   # multiple labels
```

**3. Deployments use labels to manage Pods:**
```yaml
# Deployment tracks Pods using labels
spec:
  selector:
    matchLabels:
      app: atlas-edu
```

### Labels vs Annotations

| | Labels | Annotations |
|--|--------|-------------|
| Purpose | Identifying/selecting objects | Non-identifying metadata |
| Used by K8s | ✅ (selectors, scheduling) | ❌ (ignored by K8s) |
| Examples | `app: nginx`, `env: prod` | `description: "main API"` |

```yaml
metadata:
  labels:
    app: nginx          # K8s uses this for routing
  annotations:
    description: "Main NGINX pod for portfolio site"   # just for humans
    contact: "mustafa.tawab.dev@gmail.com"
```

---

## Namespaces & Pods

Every Pod lives in a namespace. If you don't specify one — it goes to `default`.

### Create a Pod in a specific namespace

**Step 1 — Create the namespace:**
```bash
kubectl create namespace my-app
```

Or via YAML:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
```

**Step 2 — Add namespace to Pod YAML:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
  namespace: my-app      ← specify namespace here
  labels:
    app: api
spec:
  containers:
    - name: api
      image: node:22-alpine
```

**Step 3 — Apply:**
```bash
kubectl apply -f pod.yaml
```

**Step 4 — Check it:**
```bash
kubectl get pods -n my-app
```

---

## Accessing Pods

Pods have an internal IP (`10.x.x.x`) that's only reachable **inside the cluster**. To access from outside you have two options:

### Option 1 — Port Forward (dev/debugging only)

```bash
# Forward to the Pod directly
kubectl port-forward pod/my-pod 8080:80

# Forward to a Service (better — handles Pod restarts)
kubectl port-forward service/my-service 8080:80 -n my-namespace
```

Then visit `http://localhost:8080` in your browser.

**Port forward = temporary tunnel:**
```
Your Mac → kubectl tunnel → Pod inside cluster
```

Stops when you press `Ctrl+C`. Not for production.

### Option 2 — Create a Service (production way)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: my-namespace
spec:
  selector:
    app: nginx          # finds pods with this label
  ports:
    - port: 80          # service port
      targetPort: 80    # pod port
  type: ClusterIP       # internal only
```

See `03_services.md` for the full Service guide.

### Shell into a running Pod

```bash
kubectl exec -it my-pod -- sh          # Alpine (sh)
kubectl exec -it my-pod -- bash        # Ubuntu (bash)
kubectl exec -it my-pod -n my-ns -- sh # in specific namespace
```

Once inside:
```bash
ls              # browse files
env             # check environment variables
cat /app/.env   # read config files
curl localhost:3000  # test your app internally
```

---

## Debugging Pods

When something goes wrong — here's the debugging workflow:

### Step 1 — Check Pod status

```bash
kubectl get pods -n <namespace>
```

Look at `STATUS` and `RESTARTS` columns.

### Step 2 — Describe the Pod

```bash
kubectl describe pod <pod-name> -n <namespace>
```

Always scroll to the **Events** section at the bottom — this is where Kubernetes tells you exactly what went wrong:

```
Events:
  Warning  Failed   ImagePullBackOff: Failed to pull image "my-app:latest"
  Warning  Failed   CrashLoopBackOff: Back-off restarting failed container
```

### Step 3 — Check logs

```bash
kubectl logs <pod-name>                    # current logs
kubectl logs <pod-name> -f                 # follow logs live
kubectl logs <pod-name> --previous         # logs from crashed container
kubectl logs <pod-name> -c <container>     # specific container in multi-container pod
```

### Step 4 — Shell into the Pod

```bash
kubectl exec -it <pod-name> -- sh
```

Check env vars, files, network connectivity from inside.

### Step 5 — Run a temporary debug Pod

```bash
# Busybox — lightweight debug pod
kubectl run debug --rm -it --image=busybox -- sh

# Once inside, test connectivity to other pods
wget -qO- http://my-service:3000
nslookup my-service
```

`--rm` means the Pod is automatically deleted when you exit. Perfect for one-off debugging.

### Common Issues & Fixes

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `ImagePullBackOff` | Wrong image name or no registry access | Check image name, add imagePullSecret |
| `CrashLoopBackOff` | App keeps crashing | Check `kubectl logs --previous` |
| `Pending` forever | Not enough resources on Node | Check `kubectl describe pod` events |
| `OOMKilled` | Pod ran out of memory | Increase memory limits |
| Can't access Pod | No Service or wrong port | Create a Service or use port-forward |
| Wrong env vars | Misconfigured env section | Check `kubectl exec -- env` |

---

## Why You Should Never Create Pods Directly

This is critical to understand before moving on.

Pods created directly are **not managed**:

```
You create a Pod manually
      ↓
Pod runs ✅
      ↓
Pod crashes ❌
      ↓
Nobody restarts it — it stays dead 💀
```

A **Deployment** manages Pods for you:

```
You create a Deployment
      ↓
Deployment creates Pods ✅
      ↓
Pod crashes ❌
      ↓
Deployment detects it → creates a new Pod automatically ✅
```

**Other things Deployment does that raw Pods can't:**

```
❌ Raw Pod:   no scaling, no rolling updates, no self-healing, no rollback
✅ Deployment: scaling ✅, rolling updates ✅, self-healing ✅, rollback ✅
```

> Think of a raw Pod like a single employee with no manager — if they quit, the work stops. A Deployment is the manager that always ensures the right number of employees are working.

---

## Essential Pod Commands

```bash
# Create Pod from YAML
kubectl apply -f pod.yaml

# List pods (current namespace)
kubectl get pods

# List pods (specific namespace)
kubectl get pods -n <namespace>

# List pods (all namespaces)
kubectl get pods --all-namespaces

# List pods with extra details (IP, Node)
kubectl get pods -o wide

# List pods with full YAML output
kubectl get pods -o yaml

# Filter pods by label
kubectl get pods -l app=nginx
kubectl get pods -l app=nginx,env=production

# Describe pod (detailed info + events)
kubectl describe pod <name>
kubectl describe pod <name> -n <namespace>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> -f                  # follow live
kubectl logs <pod-name> --previous          # crashed container logs
kubectl logs <pod-name> -c <container>      # specific container

# Shell into pod
kubectl exec -it <pod-name> -- sh
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -n <ns> -- sh

# Run one-off command in pod
kubectl exec <pod-name> -- env              # list env vars
kubectl exec <pod-name> -- ls /app          # list files

# Port forward
kubectl port-forward pod/<name> 8080:80
kubectl port-forward pod/<name> 8080:80 -n <namespace>

# Delete pod
kubectl delete pod <name>
kubectl delete pod <name> -n <namespace>
kubectl delete -f pod.yaml                  # delete using YAML file

# Generate YAML without creating (dry run)
kubectl run my-pod --image=nginx --dry-run=client -o yaml > pod.yaml

# Run temporary debug pod (auto-removed on exit)
kubectl run debug --rm -it --image=busybox -- sh

# Get pod IP
kubectl get pod <name> -o jsonpath='{.status.podIP}'
```

---

## Quick Reference

### Minimal Pod YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: my-container
      image: nginx:alpine
```

### Full Pod YAML with all common options

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
  labels:
    app: my-app
    env: production
  annotations:
    description: "Main application pod"
spec:
  containers:
    - name: my-container
      image: nginx:alpine
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 80
      env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3000"
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
```

### Pod Status Cheat Sheet

```
Running          → ✅ healthy
Pending          → ⏳ waiting for scheduling
Completed        → ✅ one-off task finished
CrashLoopBackOff → ❌ app crashing — check logs
ImagePullBackOff → ❌ can't pull image — check name
OOMKilled        → ❌ out of memory — increase limits
Terminating      → 🔄 being deleted
```

### Debugging Cheat Sheet

```bash
kubectl get pods -n <ns>                   # check status
kubectl describe pod <name> -n <ns>        # check events
kubectl logs <name> -n <ns>               # check logs
kubectl logs <name> --previous -n <ns>    # check crashed logs
kubectl exec -it <name> -n <ns> -- sh     # shell inside
kubectl run debug --rm -it --image=busybox -- sh  # debug pod
```