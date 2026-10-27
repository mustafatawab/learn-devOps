# Ingress

Ingress is how you expose multiple applications running inside a Kubernetes cluster to the outside world — through a single entry point, using domain names instead of ports.

---

## Table of Contents

1. [The Problem Ingress Solves](#the-problem-ingress-solves)
2. [Two Parts of Ingress](#two-parts-of-ingress)
3. [How a Request Travels](#how-a-request-travels)
4. [Installing the Ingress Controller](#installing-the-ingress-controller)
5. [Writing an Ingress Resource](#writing-an-ingress-resource)
6. [Local Testing with /etc/hosts](#local-testing-with-etchosts)
7. [Domain-Based vs Path-Based Routing](#domain-based-vs-path-based-routing)
8. [Debugging Checklist](#debugging-checklist)
9. [Docker Desktop vs Minikube](#docker-desktop-vs-minikube)
10. [Quick Reference](#quick-reference)

---

## The Problem Ingress Solves

Without Ingress, every app you want to expose outside the cluster needs its own `LoadBalancer` Service:

```
❌ Without Ingress:
  Frontend app  → needs its own LoadBalancer  ($$$)
  API app       → needs its own LoadBalancer  ($$$)
  Admin app     → needs its own LoadBalancer  ($$$)
```

On a cloud provider, every `LoadBalancer` Service spins up a **real, billed load balancer**. Three apps = three bills.

```
✅ With Ingress:
  ONE LoadBalancer → Ingress Controller
                        ├── routes to Frontend (ClusterIP)
                        ├── routes to API      (ClusterIP)
                        └── routes to Admin    (ClusterIP)
```

One entry point, one bill, and your backend Services can all stay `ClusterIP` (internal-only, not reachable from outside the cluster on their own).

---

## Two Parts of Ingress

This trips up a lot of beginners — "Ingress" is actually two separate things working together:

| Part | What it is |
|------|------------|
| **Ingress Resource** | A YAML file — just *rules*. "Route `fastapi.local` to `fastapi-service`." It does nothing by itself. |
| **Ingress Controller** | The actual running software (usually NGINX) that reads those rules and enforces them. Without a Controller installed, an Ingress Resource is just inert YAML. |

```
Ingress Resource   = the instructions ("if host is X, send to Y")
Ingress Controller = the worker that reads the instructions and does the routing
```

You must install a Controller yourself — Kubernetes doesn't ship with one by default.

---

## How a Request Travels

This is the mental model to keep in your head every time something breaks:

```
Browser → http://fastapi.local
    ↓
/etc/hosts → resolves "fastapi.local" to an IP (e.g. 127.0.0.1)
    ↓
Ingress Controller (NGINX) — listening on port 80
    ↓ reads the Ingress Resource rules
    ↓ "host: fastapi.local → send to fastapi-service"
    ↓
ClusterIP Service (fastapi-service:80)
    ↓ selector matches Pod labels
    ↓
FastAPI Pod (e.g. 10.1.2.90:80)
```

Every step in this chain can break independently. When Ingress "doesn't work," you debug by checking each link, starting from the Pod and working outward — not by staring at the browser error.

---

## Installing the Ingress Controller

For Minikube (recommended for local Ingress practice on a Mac):

```bash
minikube addons enable ingress
```

For a generic cluster, you'd install the NGINX Ingress Controller manually via a YAML manifest from the [ingress-nginx project](https://github.com/kubernetes/ingress-nginx). Minikube's addon does this for you automatically, with networking already wired up correctly for local use.

Verify it's running:

```bash
kubectl get pods -n ingress-nginx
```

You want to see the controller Pod as `1/1 Running`.

---

## Writing an Ingress Resource

**Step 1 — Deployment** (the app itself):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
        - name: fastapi-app
          image: tiangolo/uvicorn-gunicorn-fastapi:python3.11
          ports:
            - containerPort: 80
```

**Step 2 — Service** (ClusterIP — internal only):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
  namespace: default
spec:
  type: ClusterIP
  selector:
    app: fastapi-app      # must EXACTLY match Deployment's Pod labels
  ports:
    - port: 80
      targetPort: 80
```

> ⚠️ **The #1 beginner mistake:** the Service `selector` must match the Pod's `labels` *exactly*. If the Service was created separately from the Deployment (copy-pasted from an old example, etc.), the selector can silently point at the wrong label and the Service will have **zero endpoints** — meaning it has nowhere to send traffic, even though it "exists."

**Step 3 — Ingress** (the routing rule):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: fastapi.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-service
                port:
                  number: 80
```

A common YAML mistake here: `paths` is a **list**, so every path needs a `-` to mark it as a list item, with `pathType` and `backend` indented underneath that same `-`:

```yaml
# ❌ Wrong — missing the dash, not a list item
paths:
  path: /
  pathType: Prefix

# ✅ Correct
paths:
  - path: /
    pathType: Prefix
```

Apply all three in order:

```bash
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
kubectl apply -f fastapi-ingress.yaml
```

---

## Local Testing with /etc/hosts

A real domain like `fastapi.local` doesn't exist on the public internet — nobody registered it. So your Mac has no idea where to send that request.

`/etc/hosts` is the oldest form of DNS: a plain text file your OS checks **before** asking any DNS server. If it finds a match, it uses that IP immediately.

```bash
sudo nano /etc/hosts
```

```
127.0.0.1       fastapi.local
```

Now:

```
Browser types: fastapi.local
      ↓
OS checks /etc/hosts FIRST → match found → 127.0.0.1
      ↓
Request goes to whatever is listening on 127.0.0.1:80
```

> Note: with **Minikube**, the Ingress Controller doesn't always live at `127.0.0.1`. Check the ADDRESS column with `kubectl get ingress` and point `/etc/hosts` at that IP instead — and, for Minikube specifically, you generally need `minikube tunnel` running in its own terminal to expose it to your Mac at all.

---

## Domain-Based vs Path-Based Routing

Ingress supports two ways to route multiple apps through one entry point:

**Domain-based** — different hostnames, same Ingress:

```yaml
rules:
  - host: api.myapp.local
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service: { name: api-service, port: { number: 80 } }
  - host: app.myapp.local
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service: { name: frontend-service, port: { number: 80 } }
```

**Path-based** — one hostname, different paths:

```yaml
rules:
  - host: myapp.local
    http:
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service: { name: api-service, port: { number: 80 } }
        - path: /
          pathType: Prefix
          backend:
            service: { name: frontend-service, port: { number: 80 } }
```

```
myapp.local/      → frontend-service
myapp.local/api   → api-service
```

---

## Debugging Checklist

This is the order we actually used to debug a real broken Ingress setup. Work through it top to bottom — each step rules something out:

**1. Are the Pods actually running?**
```bash
kubectl get pods -n default
```
`ImagePullBackOff` here means Kubernetes can't pull the image — often because it's a local-only image (`fastapi-app:dev`) that only exists on your machine, not in any registry Kubernetes can reach.

**2. Does the Service have endpoints?**
```bash
kubectl get endpoints fastapi-service -n default
```
`<none>` means the Service's `selector` doesn't match any Pod's `labels`. This was our actual bug — the Service had `selector: run=fastapi-pod` while the Deployment's Pods had `labels: app=fastapi-app`. Fix with:
```bash
kubectl edit service fastapi-service -n default
```

**3. Does the app work if you bypass Ingress entirely?**
```bash
kubectl port-forward service/fastapi-service 8080:80 -n default
curl http://localhost:8080
```
If this returns real data, the app and Service are fine — the problem is specifically in the Ingress layer.

**4. What do the Ingress Controller logs say?**
```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller | tail -20
```
Look for lines like:
```
Service "default/fastapi-service" does not have any active Endpoint.
```
That's the Controller telling you, in plain language, exactly what step 2 already showed.

**5. Does the Ingress have an ADDRESS yet?**
```bash
kubectl get ingress -n default
```
Give it 30-60 seconds after creation. An empty ADDRESS column means it's still provisioning.

**6. Is /etc/hosts pointing at the right IP?**
```bash
cat /etc/hosts | grep fastapi.local
```
Compare it against the ADDRESS from step 5.

**7. Curl with verbose output:**
```bash
curl -v http://fastapi.local
```
`Empty reply from server` (curl error 52) means the connection reached *something* listening on that port, but got no response back — this points at a Controller-level networking issue, not a DNS or app issue.

---

## Docker Desktop vs Minikube

We hit a real, known limitation: on Docker Desktop's built-in Kubernetes (on a Mac), the Ingress Controller can accept connections but return **empty responses** — a networking quirk in how Docker Desktop maps the Controller's port to the host. Every layer checked out (Pods running, Service had endpoints, Controller logs showed no errors) — yet `curl` consistently returned `Empty reply from server`.

**Minikube** avoids this because it runs Kubernetes inside its own dedicated VM with its own clean networking stack, instead of sharing Docker Desktop's.

```
Docker Desktop K8s → Kubernetes shares Docker's existing VM/networking
                      → Ingress port-mapping can be unreliable

Minikube           → its own dedicated VM, built-in ingress addon
                      → `minikube tunnel` exposes it cleanly to your Mac
```

```bash
brew install minikube
minikube start
minikube addons enable ingress
minikube tunnel     # run in a separate terminal, keep it open
```

**Takeaway:** this was a local-environment quirk, not a conceptual gap. In a real cloud cluster (GKE, EKS, AKS), the Ingress Controller's LoadBalancer gets a real, routable external IP and this entire class of problem doesn't come up.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `kubectl get ingress -n <ns>` | Check Ingress status and ADDRESS |
| `kubectl describe ingress <name> -n <ns>` | Full details + events |
| `kubectl get endpoints <service> -n <ns>` | Confirm Service → Pod wiring |
| `kubectl logs -n ingress-nginx deployment/ingress-nginx-controller` | Controller-level errors |
| `kubectl port-forward service/<svc> <local>:<port>` | Bypass Ingress to test the app directly |
| `curl -v http://<host>` | See exactly where a request stalls |
| `minikube tunnel` | Expose Minikube's Ingress to your host machine |

---

## Summary

```
Ingress Resource   → the rules (YAML)
Ingress Controller → the engine that enforces them (NGINX)
ClusterIP Service  → internal-only, reached only via the Controller
Pod labels         → must match the Service selector exactly, or there are no endpoints
/etc/hosts         → fakes local DNS so a browser can reach a fake domain
```

The concept is the same everywhere. What changes between Docker Desktop, Minikube, and a real cloud cluster is just how reliably the local networking plumbing behaves — not how Ingress itself works.
