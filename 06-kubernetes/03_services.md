# 03 - Services

A complete beginner-friendly guide to Kubernetes Services - how traffic reaches your Pods and why Services are essential for any real application.

---

## Table of Contents

1. [What is a Service?](#what-is-a-service)
2. [Why Services Exist](#why-services-exist)
3. [How Services Work](#how-services-work)
4. [Service Types](#service-types)
5. [ClusterIP - Internal Service](#clusterip--internal-service)
6. [NodePort - External via Port](#nodeport--external-via-port)
7. [LoadBalancer - External via Clean URL](#loadbalancer--external-via-clean-url)
8. [ExternalName - DNS Alias](#externalname--dns-alias)
9. [Labels & Selectors - The Glue](#labels--selectors--the-glue)
10. [Port Terminology](#port-terminology)
11. [DNS Inside the Cluster](#dns-inside-the-cluster)
12. [Port Forwarding](#port-forwarding)
13. [Real World Example](#real-world-example)
14. [Essential Service Commands](#essential-service-commands)
15. [Quick Reference](#quick-reference)

---

## What is a Service?

A **Service** is a stable, permanent entry point to reach your Pods.

Simple analogy - think of a Service like a **reception desk** at a company:

```
Visitors (traffic)
      ↓
Reception desk (Service) ← stable address, always there
      ↓
Routes to the right employee (Pod)
```

Employees (Pods) come and go - they get sick, resign, are replaced. But the reception desk is always there with the same phone number. Visitors never need to know which specific employee they're talking to.

---

## Why Services Exist

Every Pod in Kubernetes gets its own IP address. But there's a big problem:

**Pods are ephemeral** - they die and are replaced constantly:

```
Pod A crashes → new Pod B is created with a DIFFERENT IP

Before crash:  database IP = 10.1.1.50
After restart: database IP = 10.1.1.87   ← completely different!
```

If your backend hardcodes the Pod IP, it breaks every time the Pod restarts:

```
Backend: "connect to database at 10.1.1.50"
Database Pod restarts → new IP: 10.1.1.87
Backend: ❌ connection refused - IP no longer exists!
```

**Service solves this** by giving a **stable address** that never changes:

```
Backend: "connect to database-service"
Database Pod restarts → Service still points to the new Pod ✅
Backend: ✅ connected - Service found the new Pod automatically
```

---

## How Services Work

A Service uses **label selectors** to find the right Pods. It doesn't care about Pod names or IP addresses - only labels.

```
Service says: "Find me all Pods with label app=my-api"
Kubernetes:   "Found 3 Pods → 10.1.1.50, 10.1.1.51, 10.1.1.52"
Service:      "I'll load balance traffic across all three"
```

When a Pod with the matching label dies and a new one is created:

```
Old Pod (10.1.1.50) dies
New Pod (10.1.1.87) created with same label app=my-api
Service automatically discovers the new Pod ✅
```

The Service's own IP (`ClusterIP`) **never changes** - giving you a stable address forever.

---

## Service Types

Kubernetes has 4 Service types:

| Type | Accessible From | Use Case |
|------|----------------|----------|
| `ClusterIP` | Inside cluster only | Internal communication (default) |
| `NodePort` | Outside via port number | Development, testing |
| `LoadBalancer` | Outside via clean URL/IP | Production, public-facing apps |
| `ExternalName` | DNS alias to external service | Connect to external databases |

```
Internet
    ↓
LoadBalancer (public IP/URL)
    ↓
NodePort (high port 30000-32767)
    ↓
ClusterIP (internal IP)
    ↓
Pod
```

---

## ClusterIP - Internal Service

**ClusterIP** is the default Service type. It gives a stable internal IP address only reachable **inside the cluster**.

```
Internet → ❌ cannot reach ClusterIP
Pod A    → ✅ can reach ClusterIP
Pod B    → ✅ can reach ClusterIP
```

### When to use ClusterIP

```
✅ Database → backend only needs to reach it, not the internet
✅ Internal API → only other services need to reach it
✅ Cache (Redis) → only your app needs to reach it
```

### ClusterIP YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database-service
  namespace: my-app
spec:
  type: ClusterIP        # optional - ClusterIP is the default
  selector:
    app: postgres        # finds all Pods with this label
  ports:
    - port: 5432         # service port (what other Pods use to connect)
      targetPort: 5432   # pod port (what the container listens on)
```

### Access from another Pod

```bash
# From inside any Pod in the same namespace
psql -h database-service -p 5432 -U postgres

# Or in code
DATABASE_URL=postgresql://user:pass@database-service:5432/mydb
```

No IP needed - just the Service name. Kubernetes DNS handles the rest.

---

## NodePort - External via Port

**NodePort** exposes your Service on a specific port on **every Node** in the cluster. Anyone who knows the Node's IP and port can access it.

```
Browser → Node IP:30080 → Service → Pod
```

### NodePort range: 30000-32767

Kubernetes reserves this range to avoid conflicts with other applications:

```
0     - 1023   → Well-known ports (HTTP:80, SSH:22) - needs root
1024  - 29999  → Application ports - used by common apps
30000 - 32767  → Kubernetes NodePort range ✅ safe, no conflicts
```

### When to use NodePort

```
✅ Development and testing
✅ Quick demo access
✅ When you don't have a cloud load balancer
❌ Avoid in production - exposes high port numbers to users
```

### NodePort YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: my-app
spec:
  type: NodePort
  selector:
    app: frontend      # finds Pods with this label
  ports:
    - port: 80         # service port (internal)
      targetPort: 3000 # pod port (what Next.js listens on)
      nodePort: 30080  # external port (what you access from browser)
```

### Access from browser

```
http://localhost:30080      # Docker Desktop
http://NODE_IP:30080        # Real cluster
```

### NodePort without specifying the port

If you don't specify `nodePort`, Kubernetes picks a random port in the 30000-32767 range:

```yaml
ports:
  - port: 80
    targetPort: 3000
    # nodePort not specified → Kubernetes picks one automatically
```

Check which port was assigned:

```bash
kubectl get service frontend-service -n my-app
# Look at PORT(S) column: 80:31234/TCP
#                              ↑
#                         auto-assigned port
```

---

## LoadBalancer - External via Clean URL

**LoadBalancer** is the production-grade way to expose your app to the internet. It provisions a real load balancer from your cloud provider with a public IP.

```
Internet → Public IP (e.g. 34.123.45.67) → LoadBalancer → Pods
```

### When to use LoadBalancer

```
✅ Production public-facing apps
✅ APIs that external clients need to reach
✅ When you need a clean URL (no port numbers)
❌ Not for internal services - use ClusterIP instead
```

### LoadBalancer YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: my-app
spec:
  type: LoadBalancer
  selector:
    app: api           # finds Pods with this label
  ports:
    - port: 80         # external port (what users access)
      targetPort: 3000 # pod port (what your app listens on)
```

### What you see locally vs in cloud

**Docker Desktop (local):**
```
NAME          TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)
api-service   LoadBalancer   10.101.251.146   localhost     80:31234/TCP
```

`EXTERNAL-IP: localhost` - simulated. Access via `http://localhost`.

**Real cloud cluster (GKE/EKS):**
```
NAME          TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)
api-service   LoadBalancer   10.101.251.146   34.123.45.67     80:31234/TCP
```

`EXTERNAL-IP: 34.123.45.67` - real public IP. Access via `http://34.123.45.67`.

> **Cost warning:** LoadBalancer Services in the cloud provision a real load balancer that costs money. Don't create them unnecessarily.

---

## ExternalName - DNS Alias

**ExternalName** maps a Service to an external DNS name. Useful when your app inside the cluster needs to connect to an external service (like NeonDB or a managed Redis).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: neon-database
  namespace: my-app
spec:
  type: ExternalName
  externalName: ep-nameless-king.neon.tech   # external DNS
```

Now inside your cluster you can connect using:

```
DATABASE_URL=postgresql://user:pass@neon-database:5432/mydb
```

Instead of the long NeonDB URL. If you ever switch databases, just update the Service - your app code stays the same.

---

## Labels & Selectors - The Glue

The **selector** in a Service is what connects it to Pods. This is the most important concept to understand.

### How it works

```yaml
# Pod - has labels
metadata:
  labels:
    app: atlas-edu     ← Pod has this label
    tier: backend

# Service - selects by labels
spec:
  selector:
    app: atlas-edu     ← Service finds all Pods with this label
```

The Service continuously watches for Pods matching its selector. When a Pod is created, updated, or deleted - the Service automatically updates.

### Multiple Pods matched

If multiple Pods match the selector, the Service load balances traffic across all of them:

```
Service selector: app=atlas-edu

Matched Pods:
  Pod 1 (10.1.1.50) → gets ~33% of traffic
  Pod 2 (10.1.1.51) → gets ~33% of traffic
  Pod 3 (10.1.1.52) → gets ~33% of traffic
```

This is how Kubernetes scales - add more Pods with the same label, Service automatically distributes traffic.

### No matching Pods

If no Pods match the selector, the Service still exists but traffic goes nowhere:

```
Service: "looking for app=atlas-edu"
Kubernetes: "no Pods found"
Traffic: ❌ connection refused
```

This is why checking labels is important when debugging connection issues.

### Check which Pods a Service is routing to

```bash
kubectl get endpoints my-service -n my-namespace
```

Output:
```
NAME         ENDPOINTS
my-service   10.1.1.50:3000,10.1.1.51:3000,10.1.1.52:3000
```

If `ENDPOINTS` shows `<none>` - no Pods match the selector. Check your labels!

---

## Port Terminology

Services have three port-related fields that confuse many beginners:

```yaml
ports:
  - port: 80         # 1. Service port
    targetPort: 3000 # 2. Pod/container port
    nodePort: 30080  # 3. Node port (NodePort type only)
```

### Visual explanation

```
Browser/Client
      ↓
:30080  (nodePort)     ← what you type in the browser (NodePort only)
      ↓
Service
      ↓
:80     (port)         ← the Service's own port
      ↓
:3000   (targetPort)   ← what your container actually listens on
```

### Real example - Next.js frontend

```yaml
ports:
  - port: 80         # other services call this on port 80
    targetPort: 3000 # but Next.js listens on port 3000 inside the container
    nodePort: 30080  # accessible from browser at :30080
```

### Named ports

You can name ports for better readability:

```yaml
# In Pod
spec:
  containers:
    - name: api
      ports:
        - name: http
          containerPort: 3000

# In Service
spec:
  ports:
    - port: 80
      targetPort: http   # reference by name instead of number
```

---

## DNS Inside the Cluster

Kubernetes automatically creates DNS entries for every Service. This is how Pods find each other by name instead of IP address.

### DNS format

```
<service-name>.<namespace>.svc.cluster.local

Examples:
  database-service.my-app.svc.cluster.local
  api-service.production.svc.cluster.local
```

### Shorthand

Within the **same namespace**, you can use just the Service name:

```bash
# Same namespace - just use service name
curl http://api-service:3000

# Different namespace - use full DNS
curl http://api-service.production.svc.cluster.local:3000
```

### Why this matters

This is why your `DATABASE_URL` inside Kubernetes uses the Service name:

```bash
# ❌ Wrong - Pod IP changes on restart
DATABASE_URL=postgresql://user:pass@10.1.1.50:5432/mydb

# ✅ Correct - Service name never changes
DATABASE_URL=postgresql://user:pass@database-service:5432/mydb

# ✅ Also correct - full DNS format
DATABASE_URL=postgresql://user:pass@database-service.my-app.svc.cluster.local:5432/mydb
```

---

## Port Forwarding

Port forwarding is a development tool - not for production. It creates a **temporary tunnel** from your machine to a Service or Pod inside the cluster.

```bash
# Forward to a Service (recommended)
kubectl port-forward service/my-service 8080:80

# Forward to a Pod directly
kubectl port-forward pod/my-pod 8080:80

# Forward in specific namespace
kubectl port-forward service/my-service 8080:80 -n my-namespace
```

Then visit `http://localhost:8080` in your browser.

### Port-forward vs Service

| | Port-forward | Service |
|--|-------------|---------|
| Purpose | Development/debugging | Production access |
| Duration | Until Ctrl+C | Permanent |
| Who can access | Only you | Everyone |
| Survives Pod restart | ❌ | ✅ |
| Requires kubectl | ✅ | ❌ |

---

## Real World Example

Here's a complete real-world setup for **Atlas Edu** - a Next.js frontend + Node.js API + PostgreSQL database:

### Architecture

```
Internet
    ↓
LoadBalancer Service (port 80)
    ↓
Frontend Pods (Next.js :3000)
    ↓
ClusterIP Service (port 9000) ← internal only
    ↓
API Pods (Node.js :9000)
    ↓
ClusterIP Service (port 5432) ← internal only
    ↓
Database Pod (PostgreSQL :5432)
```

### Frontend Service (LoadBalancer)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: atlas-edu
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 3000
```

### API Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: atlas-edu
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - port: 9000
      targetPort: 9000
```

### Database Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database-service
  namespace: atlas-edu
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

### Environment variables using Service names

```bash
# In API Pod
DATABASE_URL=postgresql://user:pass@database-service:5432/atlas_edu

# In Frontend Pod
NEXT_PUBLIC_API_URL=http://api-service:9000
```

---

## Essential Service Commands

```bash
# Create Service from YAML
kubectl apply -f service.yaml

# List services
kubectl get services
kubectl get svc                            # shorthand
kubectl get svc -n <namespace>
kubectl get svc --all-namespaces

# Describe service (detailed info)
kubectl describe service <name>
kubectl describe svc <name> -n <namespace>

# Get service with extra details
kubectl get svc -o wide

# Full YAML of a service
kubectl get svc <name> -o yaml

# Check which Pods a Service is routing to
kubectl get endpoints <service-name>
kubectl get endpoints <service-name> -n <namespace>

# Port forward to service
kubectl port-forward service/<name> 8080:80
kubectl port-forward service/<name> 8080:80 -n <namespace>

# Delete service
kubectl delete service <name>
kubectl delete svc <name> -n <namespace>
kubectl delete -f service.yaml

# Generate Service YAML without creating (dry run)
kubectl create service clusterip my-service --tcp=80:3000 --dry-run=client -o yaml
```

---

## Quick Reference

### Service Type Cheat Sheet

```
ClusterIP    → internal only
               use for: databases, internal APIs, caches
               access: kubectl port-forward or from other Pods

NodePort     → external via high port (30000-32767)
               use for: development, testing
               access: localhost:30080

LoadBalancer → external via clean URL/IP
               use for: production, public-facing apps
               access: localhost (local) or public IP (cloud)

ExternalName → DNS alias to external service
               use for: connecting to external databases/APIs
```

### Minimal Service YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 3000
```

### Full Service YAML with all options

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: my-namespace
  labels:
    app: my-app
spec:
  type: ClusterIP           # ClusterIP | NodePort | LoadBalancer | ExternalName
  selector:
    app: my-app             # matches Pod labels
  ports:
    - name: http            # optional name
      protocol: TCP         # TCP (default) or UDP
      port: 80              # service port
      targetPort: 3000      # pod/container port
      nodePort: 30080       # NodePort only (30000-32767)
```

### Port Terminology Cheat Sheet

```
nodePort    → 30080  ← browser/external access (NodePort only)
port        → 80     ← service's own port
targetPort  → 3000   ← container's actual port
```

### DNS Cheat Sheet

```bash
# Same namespace
curl http://my-service:80

# Different namespace
curl http://my-service.my-namespace.svc.cluster.local:80

# Check endpoints (which Pods are being routed to)
kubectl get endpoints my-service
```

### Debugging Services Cheat Sheet

```bash
# Check if service exists
kubectl get svc -n <namespace>

# Check which pods are matched
kubectl get endpoints <service-name> -n <namespace>
# If ENDPOINTS shows <none> → no Pods match the selector → check labels!

# Check pod labels
kubectl get pods --show-labels -n <namespace>

# Describe service for detailed info
kubectl describe svc <name> -n <namespace>

# Test connection from inside cluster
kubectl run debug --rm -it --image=busybox -- sh
# Then inside: wget -qO- http://my-service:80
```