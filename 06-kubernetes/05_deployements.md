# 05 — Deployments

A complete beginner-friendly guide to Kubernetes Deployments — the most important object in Kubernetes for running production applications.

---

## Table of Contents

1. [What is a Deployment?](#what-is-a-deployment)
2. [Why Use Deployments Instead of Pods](#why-use-deployments-instead-of-pods)
3. [How Deployments Work](#how-deployments-work)
4. [Your First Deployment YAML](#your-first-deployment-yaml)
5. [Deployment vs ReplicaSet vs Pod](#deployment-vs-replicaset-vs-pod)
6. [Scaling](#scaling)
7. [Rolling Updates](#rolling-updates)
8. [Rollback](#rollback)
9. [Deployment Strategies](#deployment-strategies)
10. [Environment Variables in Deployments](#environment-variables-in-deployments)
11. [Resource Limits in Deployments](#resource-limits-in-deployments)
12. [Health Checks — Liveness & Readiness Probes](#health-checks--liveness--readiness-probes)
13. [Real World Example](#real-world-example)
14. [Essential Deployment Commands](#essential-deployment-commands)
15. [Quick Reference](#quick-reference)

---

## What is a Deployment?

A **Deployment** is a Kubernetes object that manages your Pods for you — creating them, keeping them healthy, scaling them up and down, and updating them safely.

Think of a Deployment like a **staffing agency**:

```
You (manager) tell the staffing agency:
"I need 3 Node.js developers at all times"

Staffing agency (Deployment) handles:
✅ Hires 3 developers (creates 3 Pods)
✅ If a developer quits (Pod crashes) → immediately hires a replacement
✅ If workload grows → hires more developers (scales up)
✅ If workload drops → lets some go (scales down)
✅ When you update requirements → transitions developers one at a time
   so work never stops (rolling update)
✅ If new developers aren't working out → brings back the old ones (rollback)
```

---

## Why Use Deployments Instead of Pods

In the previous section we created Pods directly. But in production you should **never** create Pods directly. Here's why:

### Problem with raw Pods

```
You create a Pod manually
      ↓
Pod is running ✅
      ↓
Pod crashes for any reason ❌
      ↓
Pod stays dead — nobody restarts it 💀
      ↓
Your app is down until YOU manually intervene
```

### Solution with Deployment

```
You create a Deployment
      ↓
Deployment creates Pods ✅
      ↓
Pod crashes for any reason ❌
      ↓
Deployment detects it immediately
      ↓
Deployment creates a new Pod automatically ✅
      ↓
Your app is back up — you didn't do anything
```

### Side by side comparison

| Feature | Raw Pod | Deployment |
|---------|---------|------------|
| Self-healing | ❌ | ✅ Automatic |
| Scaling | ❌ Manual | ✅ One command |
| Rolling updates | ❌ | ✅ Zero downtime |
| Rollback | ❌ | ✅ One command |
| Multiple replicas | ❌ | ✅ Declarative |
| Update history | ❌ | ✅ Tracked |
| Production ready | ❌ Never | ✅ Always |

> Rule: In production, you NEVER create Pods directly. ALWAYS use a Deployment.

---

## How Deployments Work

A Deployment doesn't create Pods directly. There's an intermediate object called a **ReplicaSet**:

```
Deployment
    ↓ creates and manages
ReplicaSet
    ↓ creates and manages
Pods (your actual containers)
```

### The relationship

```
You → tell Deployment: "I want 3 replicas of my app"
Deployment → creates a ReplicaSet: "maintain 3 Pods"
ReplicaSet → creates 3 Pods and watches them
ReplicaSet → if a Pod dies, creates a new one immediately
Deployment → handles updates by creating new ReplicaSets
```

You almost never interact with ReplicaSets directly — the Deployment handles them automatically. But it's good to know they exist.

### The reconciliation loop

Kubernetes constantly runs a loop:

```
Every few seconds:
  Desired state:  "3 Pods should be running"
  Actual state:   "2 Pods are running"
  Action:         "Create 1 more Pod"
```

This is called the **reconciliation loop** — Kubernetes always tries to match actual state to desired state. This is why Kubernetes is called "self-healing".

---

## Your First Deployment YAML

Here is a simple Deployment for an nginx web server:

```yaml
apiVersion: apps/v1      # Deployments use apps/v1, not v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: my-app
  labels:
    app: nginx
spec:
  replicas: 3            # how many Pod copies to run
  selector:
    matchLabels:
      app: nginx         # which Pods this Deployment manages
  template:              # Pod template — defines what each Pod looks like
    metadata:
      labels:
        app: nginx       # must match selector.matchLabels above!
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
```

### Breaking it down section by section

**`apiVersion: apps/v1`**

Deployments are in the `apps` API group, not the core `v1` group:
```yaml
apiVersion: v1        # Pods, Services, ConfigMaps
apiVersion: apps/v1   # Deployments, StatefulSets, DaemonSets
```

**`spec.replicas: 3`**

How many Pod copies to run simultaneously:
```yaml
replicas: 1   # one Pod — single instance
replicas: 3   # three Pods — load balanced
replicas: 0   # zero Pods — app is "paused"
```

**`spec.selector.matchLabels`**

Which Pods this Deployment is responsible for managing. Must match the Pod template labels:
```yaml
selector:
  matchLabels:
    app: nginx       # Deployment manages all Pods with this label
```

**`spec.template`**

The blueprint for each Pod the Deployment creates. Everything inside `template` is exactly like writing a Pod YAML:
```yaml
template:
  metadata:
    labels:
      app: nginx     # MUST match selector.matchLabels
  spec:
    containers:      # same as Pod spec
      - name: nginx
        image: nginx:alpine
```

> The labels in `template.metadata.labels` MUST match `selector.matchLabels`. If they don't match, Kubernetes will reject the Deployment.

---

### Apply and verify

```bash
# Create the Deployment
kubectl apply -f deployment.yaml

# Check the Deployment
kubectl get deployments -n my-app
kubectl get deploy -n my-app          # shorthand

# Check the Pods it created
kubectl get pods -n my-app

# Check the ReplicaSet it created
kubectl get replicaset -n my-app
kubectl get rs -n my-app              # shorthand
```

Output of `kubectl get deployments`:
```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           30s
```

Columns explained:
```
READY        → 3/3 means 3 Pods running out of 3 desired ✅
UP-TO-DATE   → 3 Pods have the latest template applied
AVAILABLE    → 3 Pods are ready to serve traffic
```

---

## Deployment vs ReplicaSet vs Pod

Seeing all three after applying a Deployment can be confusing. Here's how they relate:

```bash
kubectl get all -n my-app
```

```
NAME                                    READY   STATUS    RESTARTS
pod/nginx-deployment-7d8f9b-abc12       1/1     Running   0
pod/nginx-deployment-7d8f9b-def34       1/1     Running   0
pod/nginx-deployment-7d8f9b-ghi56       1/1     Running   0

NAME                              DESIRED   CURRENT   READY
replicaset/nginx-deployment-7d8f9b   3         3         3

NAME                           READY   UP-TO-DATE   AVAILABLE
deployment/nginx-deployment    3/3     3            3
```

Notice the naming pattern:

```
Deployment name:   nginx-deployment
ReplicaSet name:   nginx-deployment-7d8f9b        (deployment + hash)
Pod names:         nginx-deployment-7d8f9b-abc12  (replicaset + random)
```

The hash (`7d8f9b`) changes every time the Pod template changes — this is how Kubernetes tracks different versions of your Deployment.

---

## Scaling

Scaling means changing the number of Pod replicas running.

### Scale up — more replicas

```bash
# Imperative (quick)
kubectl scale deployment nginx-deployment --replicas=5 -n my-app

# Declarative (recommended — update YAML and apply)
# Edit deployment.yaml: replicas: 5
kubectl apply -f deployment.yaml
```

What happens:
```
Before: 3 Pods running
Scale to 5
After:  5 Pods running (2 new Pods created automatically) ✅
```

### Scale down — fewer replicas

```bash
kubectl scale deployment nginx-deployment --replicas=2 -n my-app
```

What happens:
```
Before: 5 Pods running
Scale to 2
After:  2 Pods running (3 Pods gracefully terminated) ✅
```

### Scale to zero — pause the app

```bash
kubectl scale deployment nginx-deployment --replicas=0 -n my-app
```

All Pods are removed but the Deployment still exists. Useful for saving resources in staging environments overnight.

```
replicas: 0 → app is "paused" — no Pods, no traffic served
replicas: 3 → app is "running" — 3 Pods serving traffic
```

### Verify scaling

```bash
kubectl get pods -n my-app    # see all Pods
kubectl get deployment nginx-deployment -n my-app  # see READY count
```

---

## Rolling Updates

A rolling update replaces old Pods with new ones **gradually** — ensuring zero downtime.

### How rolling updates work

Imagine you have 3 Pods running v1 and you push v2:

```
Step 1:
  Pod-1 (v1) ✅     Pod-2 (v1) ✅     Pod-3 (v1) ✅
  Traffic split across all 3

Step 2: Update Pod-1
  Pod-1 (v2) 🔄     Pod-2 (v1) ✅     Pod-3 (v1) ✅
  Traffic goes to Pod-2 and Pod-3 while Pod-1 updates

Step 3: Pod-1 ready, update Pod-2
  Pod-1 (v2) ✅     Pod-2 (v2) 🔄     Pod-3 (v1) ✅
  Traffic goes to Pod-1 and Pod-3 while Pod-2 updates

Step 4: Pod-2 ready, update Pod-3
  Pod-1 (v2) ✅     Pod-2 (v2) ✅     Pod-3 (v2) 🔄
  Traffic goes to Pod-1 and Pod-2 while Pod-3 updates

Step 5: Done!
  Pod-1 (v2) ✅     Pod-2 (v2) ✅     Pod-3 (v2) ✅
  All traffic on v2 — zero downtime throughout 🎉
```

### Triggering a rolling update

A rolling update is triggered whenever the **Pod template** changes — most commonly when you update the image:

> ⚠️ **Common mistake:** The container name in `set image` must match exactly what's in your Deployment. Always check the exact name first:
> ```bash
> kubectl describe deployment <name> -n <namespace> | grep -A5 "Containers:"
> ```
> If you get `error: unable to find container named "nginx"` — the name in your YAML doesn't match what you typed.

```bash
# Update image version
kubectl set image deployment/nginx-deployment nginx=nginx:1.25 -n my-app

# Or update the YAML file and apply
# Edit: image: nginx:1.25
kubectl apply -f deployment.yaml
```

### Watch the rolling update in real time

```bash
# Watch Pods updating
kubectl get pods -n my-app -w

# Check rollout status
kubectl rollout status deployment/nginx-deployment -n my-app
```

Output:
```
Waiting for deployment "nginx-deployment" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 2 old replicas are pending termination...
deployment "nginx-deployment" successfully rolled out
```

### Controlling the rolling update

You can control how fast the update happens with `strategy`:

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1    # max Pods that can be unavailable during update
      maxSurge: 1          # max extra Pods that can be created during update
```

**`maxUnavailable: 1`** — at most 1 Pod can be down at any time:
```
3 Pods total, maxUnavailable: 1
→ At least 2 Pods always serving traffic ✅
```

**`maxSurge: 1`** — at most 1 extra Pod can be created during update:
```
3 Pods total, maxSurge: 1
→ Maximum 4 Pods exist at once during the update
```

---

## Rollback

If a new version has a bug, you can instantly go back to the previous version.

### View rollout history

```bash
kubectl rollout history deployment/nginx-deployment -n my-app
```

Output:
```
REVISION  CHANGE-CAUSE
1         Initial deployment
2         Update to nginx:1.25
3         Update to nginx:1.26 (broken!)
```

### Rollback to previous version

```bash
# Rollback to previous version (one step back)
kubectl rollout undo deployment/nginx-deployment -n my-app

# Rollback to a specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=1 -n my-app
```

> ⚠️ **Important:** Rollback does NOT go backwards in revision history. It creates a **new revision** with the old configuration. Revision numbers always increase — never decrease.
>
> ```
> Before rollback:  REVISION 1, 2, 3 (current)
> After rollback:   REVISION 1, 2, 3, 4 (new revision with config from rev 2)
> ```
>
> This means `kubectl rollout history` will always show you moving forward — even when rolling back.

### Adding change annotations

To make rollout history useful, annotate your changes:

```bash
kubectl annotate deployment/nginx-deployment \
  kubernetes.io/change-cause="Update to nginx:1.25" \
  -n my-app
```

Or in YAML:

```yaml
metadata:
  annotations:
    kubernetes.io/change-cause: "Update to nginx:1.25 for security patch"
```

### Verify rollback

```bash
kubectl rollout status deployment/nginx-deployment -n my-app
kubectl get pods -n my-app
```

---

## Deployment Strategies

Kubernetes supports two built-in update strategies:

### 1. RollingUpdate (default)

Replaces Pods gradually — zero downtime:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

```
Old Pods:  ✅ ✅ ✅
Update:    🔄 ✅ ✅ → ✅ 🔄 ✅ → ✅ ✅ 🔄 → ✅ ✅ ✅
```

Best for: Production apps where downtime is unacceptable.

### 2. Recreate

Kills ALL old Pods first, then creates new ones. Causes downtime:

```yaml
spec:
  strategy:
    type: Recreate
```

```
Old Pods:  ✅ ✅ ✅
Kill all:  ❌ ❌ ❌  ← DOWNTIME during this gap
New Pods:  ✅ ✅ ✅
```

Best for: Development environments, or apps where two versions running simultaneously causes problems (e.g. database migration).

### Comparison

| | RollingUpdate | Recreate |
|--|--------------|---------|
| Downtime | ❌ Zero | ✅ Yes |
| Two versions running at once | Yes (briefly) | No |
| Speed | Slower | Faster |
| Use case | Production | Dev / breaking changes |

---

## Environment Variables in Deployments

### Hardcoded values

```yaml
spec:
  template:
    spec:
      containers:
        - name: api
          image: my-api:latest
          env:
            - name: NODE_ENV
              value: "production"
            - name: PORT
              value: "3000"
            - name: LOG_LEVEL
              value: "info"
```

### From ConfigMap (non-sensitive config)

```yaml
# First create a ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: my-app
data:
  NODE_ENV: "production"
  PORT: "3000"
  LOG_LEVEL: "info"
```

```yaml
# Reference in Deployment
env:
  - name: NODE_ENV
    valueFrom:
      configMapKeyRef:
        name: api-config
        key: NODE_ENV
```

Or inject all ConfigMap values at once:

```yaml
envFrom:
  - configMapRef:
      name: api-config
```

### From Secret (sensitive config)

```yaml
# Reference a Secret value
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: DATABASE_URL
```

Or inject all Secret values at once:

```yaml
envFrom:
  - secretRef:
      name: db-secret
```

### Combined — ConfigMap + Secret

```yaml
envFrom:
  - configMapRef:
      name: api-config     # non-sensitive config
  - secretRef:
      name: db-secret      # sensitive config (passwords, tokens)
```

See `06_configmaps_secrets.md` for a full guide on ConfigMaps and Secrets.

---

## Resource Limits in Deployments

Always set resource requests and limits in production — prevents one Pod from starving others:

```yaml
spec:
  template:
    spec:
      containers:
        - name: api
          image: my-api:latest
          resources:
            requests:
              memory: "256Mi"    # guaranteed minimum RAM
              cpu: "250m"        # guaranteed minimum CPU (0.25 cores)
            limits:
              memory: "512Mi"    # maximum RAM allowed
              cpu: "500m"        # maximum CPU allowed (0.5 cores)
```

### CPU units

```
1000m = 1 CPU core
500m  = 0.5 CPU core
250m  = 0.25 CPU core (quarter core)
100m  = 0.1 CPU core
```

### Memory units

```
Ki = Kibibyte (1024 bytes)
Mi = Mebibyte (1024 Ki) — use this for RAM
Gi = Gibibyte (1024 Mi)

128Mi = 128 megabytes
256Mi = 256 megabytes
1Gi   = 1 gigabyte
```

### What happens without limits

```
No limits set:
  Pod A goes rogue → uses 100% CPU and RAM
  Pod B, C, D → starved of resources → crash
  Node → overwhelmed → all apps down ❌
```

```
Limits set:
  Pod A goes rogue → hits its limit → slowed down or OOMKilled
  Pod B, C, D → protected → still running ✅
```

---

## Health Checks — Liveness & Readiness Probes

Kubernetes needs to know if your app is actually working — not just running. Probes let you tell Kubernetes how to check.

### Liveness Probe — is the app alive?

Checks if your app is still alive. If the probe fails, Kubernetes **restarts the container**:

```yaml
livenessProbe:
  httpGet:
    path: /health      # your health check endpoint
    port: 3000
  initialDelaySeconds: 30   # wait 30s before first check (let app start)
  periodSeconds: 10          # check every 10 seconds
  failureThreshold: 3        # restart after 3 consecutive failures
```

What happens:

```
App starts → wait 30 seconds → check /health every 10s
/health returns 200 ✅ → all good, keep running
/health fails 3 times ❌ → container restarted automatically
```

### Readiness Probe — is the app ready for traffic?

Checks if your app is ready to receive traffic. If the probe fails, Kubernetes **stops sending traffic** to this Pod (but does NOT restart it):

```yaml
readinessProbe:
  httpGet:
    path: /ready       # your readiness endpoint
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

What happens:

```
New Pod starts
/ready returns 503 (still loading) → Service stops sending traffic to this Pod
/ready returns 200 (app fully loaded) ✅ → Service starts sending traffic
```

### Liveness vs Readiness

| | Liveness | Readiness |
|--|----------|-----------|
| Question | Is the app alive? | Is the app ready for traffic? |
| On failure | Container restarts | Pod removed from Service (no traffic) |
| Use case | Detect hung/stuck apps | Prevent traffic during startup |

### Startup Probe — slow starting apps

For apps that take a long time to start:

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 3000
  failureThreshold: 30      # 30 failures allowed
  periodSeconds: 10          # check every 10 seconds
  # Total: 30 * 10 = 300 seconds = 5 minutes to start
```

During startup, liveness/readiness probes are paused until startup probe succeeds.

### Simple probe types

```yaml
# HTTP probe — most common
livenessProbe:
  httpGet:
    path: /health
    port: 3000

# TCP probe — just checks if port is open
livenessProbe:
  tcpSocket:
    port: 3000

# Exec probe — runs a command inside container
livenessProbe:
  exec:
    command:
      - cat
      - /tmp/healthy
```

---

## Real World Example

Here is a complete production-ready Deployment for the **Atlas Edu API** — a Node.js/Express backend:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: atlas-edu-api
  namespace: atlas-edu-production
  labels:
    app: atlas-edu-api
    tier: backend
    env: production
  annotations:
    kubernetes.io/change-cause: "Initial production deployment"
spec:
  replicas: 3                    # 3 copies for high availability
  selector:
    matchLabels:
      app: atlas-edu-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1          # at least 2 Pods always running
      maxSurge: 1                # max 4 Pods during update
  template:
    metadata:
      labels:
        app: atlas-edu-api
        tier: backend
        env: production
    spec:
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
          imagePullPolicy: Always    # always pull latest from GHCR
          ports:
            - containerPort: 9000
              name: http

          # Environment variables
          envFrom:
            - configMapRef:
                name: api-config      # non-sensitive config
            - secretRef:
                name: api-secrets     # sensitive config (DB_URL, JWT_SECRET)

          # Resource limits
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"

          # Health checks
          startupProbe:
            httpGet:
              path: /health
              port: 9000
            failureThreshold: 30
            periodSeconds: 10

          livenessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /ready
              port: 9000
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
```

### Companion Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: atlas-edu-api-service
  namespace: atlas-edu-production
spec:
  type: ClusterIP
  selector:
    app: atlas-edu-api       # matches Deployment Pod labels
  ports:
    - port: 9000
      targetPort: 9000
      name: http
```

### Apply everything

```bash
# Create namespace first
kubectl apply -f namespace.yaml

# Create ConfigMap and Secrets
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Create Deployment and Service
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Verify everything is running
kubectl get all -n atlas-edu-production
```

---

## Essential Deployment Commands

```bash
# Create/update Deployment from YAML
kubectl apply -f deployment.yaml

# List deployments
kubectl get deployments -n <namespace>
kubectl get deploy -n <namespace>       # shorthand
kubectl get deploy -A                   # all namespaces

# Detailed info
kubectl describe deployment <name> -n <namespace>

# Get Deployment YAML
kubectl get deployment <name> -o yaml -n <namespace>

# Scale replicas
kubectl scale deployment <name> --replicas=5 -n <namespace>

# Update image
kubectl set image deployment/<name> <container>=<new-image>:<tag> -n <namespace>

# Watch rollout progress
kubectl rollout status deployment/<name> -n <namespace>

# Pause a rollout
kubectl rollout pause deployment/<name> -n <namespace>

# Resume a paused rollout
kubectl rollout resume deployment/<name> -n <namespace>

# View rollout history
kubectl rollout history deployment/<name> -n <namespace>

# Rollback to previous version
kubectl rollout undo deployment/<name> -n <namespace>

# Rollback to specific revision
kubectl rollout undo deployment/<name> --to-revision=2 -n <namespace>

# Restart all Pods (useful to pick up new Secrets/ConfigMaps)
kubectl rollout restart deployment/<name> -n <namespace>

# Delete deployment
kubectl delete deployment <name> -n <namespace>
kubectl delete -f deployment.yaml

# Watch Pods during update
kubectl get pods -n <namespace> -w

# Check ReplicaSets created by Deployment
kubectl get replicaset -n <namespace>
kubectl get rs -n <namespace>           # shorthand

# Generate Deployment YAML without creating
kubectl create deployment my-app --image=nginx --replicas=3 --dry-run=client -o yaml
```

---

## Quick Reference

### Minimal Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-container
          image: nginx:alpine
          ports:
            - containerPort: 80
```

### Full Deployment YAML with all common options

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
  namespace: my-namespace
  labels:
    app: my-app
  annotations:
    kubernetes.io/change-cause: "Update to v1.2.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-container
          image: my-image:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: my-config
            - secretRef:
                name: my-secrets
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Deployment Cheat Sheet

```bash
kubectl get deploy -n <ns>                             # list deployments
kubectl describe deploy <name> -n <ns>                 # describe
kubectl scale deploy <name> --replicas=5 -n <ns>       # scale
kubectl set image deploy/<name> <c>=<image> -n <ns>    # update image
kubectl rollout status deploy/<name> -n <ns>           # watch update
kubectl rollout undo deploy/<name> -n <ns>             # rollback
kubectl rollout history deploy/<name> -n <ns>          # view history
kubectl rollout restart deploy/<name> -n <ns>          # restart all pods
```

### Common Issues & Fixes

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Pods not starting | Image pull error | Check image name and registry access |
| READY shows 0/3 | App crashing on start | Check logs: kubectl logs |
| Rolling update stuck | New Pods not passing readiness | Check readiness probe and app logs |
| OOMKilled | Not enough memory | Increase memory limits |
| Deployment not updating | Wrong selector or label mismatch | Check selector matches template labels |
| Old version still running | Cached image | Set imagePullPolicy: Always |
| Rollback not working | No previous revision | Check rollout history |