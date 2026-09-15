# 06 — ConfigMaps & Secrets

A complete beginner-friendly guide to ConfigMaps and Secrets — how to inject configuration and sensitive data into your Pods without hardcoding anything.

---

## Table of Contents

1. [The Problem — Hardcoded Config](#the-problem--hardcoded-config)
2. [What is a ConfigMap?](#what-is-a-configmap)
3. [What is a Secret?](#what-is-a-secret)
4. [ConfigMap vs Secret](#configmap-vs-secret)
5. [Creating ConfigMaps](#creating-configmaps)
6. [Creating Secrets](#creating-secrets)
7. [Using ConfigMaps in Pods](#using-configmaps-in-pods)
8. [Using Secrets in Pods](#using-secrets-in-pods)
9. [Common Mistakes When Injecting Config](#common-mistakes-when-injecting-config)
10. [Verifying Config Inside a Pod](#verifying-config-inside-a-pod)
11. [Mounting as Files](#mounting-as-files)
12. [Updating ConfigMaps and Secrets](#updating-configmaps-and-secrets)
13. [Secret Types](#secret-types)
14. [Real World Example](#real-world-example)
15. [Essential Commands](#essential-commands)
16. [Quick Reference](#quick-reference)

---

## The Problem — Hardcoded Config

Let's start with a real problem every developer faces.

You build a Node.js API. It needs a database URL, a JWT secret, and some config values. The easiest thing to do is hardcode them:

```javascript
// ❌ Hardcoded inside your code
const db = new Client({
  connectionString: "postgresql://admin:password123@prod-db:5432/atlas_edu"
})

const JWT_SECRET = "my-super-secret-jwt-key"
const PORT = 3000
```

Or you put them directly in your Deployment YAML:

```yaml
# ❌ Hardcoded in YAML
env:
  - name: DATABASE_URL
    value: "postgresql://admin:password123@prod-db:5432/atlas_edu"
  - name: JWT_SECRET
    value: "my-super-secret-jwt-key"
  - name: PORT
    value: "3000"
```

### Why this is a problem

```
Security      → passwords visible in Git history forever ❌
               anyone with repo access can see your database password

Flexibility   → staging and production need different values
               but you have one hardcoded value ❌

Rotation      → changing a password requires rebuilding Docker image ❌
               and redeploying — too risky and slow

Sharing       → multiple Deployments need same DB_URL
               you have to copy-paste everywhere ❌

Auditability  → no central place to see all config values ❌
```

### The solution

Kubernetes gives you two objects to solve this:

```
Non-sensitive config  → ConfigMap  (NODE_ENV, PORT, LOG_LEVEL)
Sensitive config      → Secret     (DATABASE_URL, JWT_SECRET, API_KEYS)
```

Your Deployment YAML stays clean — no hardcoded values. The Pod reads everything from ConfigMaps and Secrets at runtime.

---

## What is a ConfigMap?

A **ConfigMap** is a Kubernetes object that stores **non-sensitive** configuration data as key-value pairs.

Think of it like a **.env file** — but stored inside Kubernetes instead of on your local disk:

```
ConfigMap: api-config
  NODE_ENV = production
  PORT = 3000
  LOG_LEVEL = info
  ALLOWED_ORIGINS = https://app.com,https://api.com
  MAX_CONNECTIONS = 100
```

Your Pods read these values at startup as environment variables — no hardcoding needed.

### What to store in ConfigMap

```
✅ NODE_ENV       → development, staging, production
✅ PORT           → which port the app listens on
✅ LOG_LEVEL      → debug, info, warn, error
✅ Feature flags  → ENABLE_SIGNUP=true
✅ CORS origins   → ALLOWED_ORIGINS=https://app.com
✅ API base URLs  → non-sensitive URLs
✅ Timeout values → REQUEST_TIMEOUT=30s
✅ Config files   → nginx.conf, app.properties
```

### What NOT to store in ConfigMap

```
❌ Passwords
❌ Database connection strings (they contain passwords)
❌ JWT secrets
❌ API keys
❌ Tokens
❌ Certificates
```

These should go in a **Secret** instead.

---

## What is a Secret?

A **Secret** is a Kubernetes object that stores **sensitive** data — passwords, tokens, certificates, private keys.

Think of it like a **locked safe** — the data is encoded and access is controlled:

```
Secret: api-secrets
  DATABASE_URL = postgresql://admin:pass123@db:5432/mydb
  JWT_SECRET = eyJhbGciOiJIUzI1NiJ9...
  RESEND_API_KEY = re_abc123...
  SMTP_PASSWORD = myEmailPass456
```

### What to store in Secret

```
✅ Database connection strings (contain passwords)
✅ JWT secrets
✅ API keys (Resend, Stripe, OpenAI, etc.)
✅ OAuth client secrets
✅ SMTP credentials
✅ SSH private keys
✅ TLS certificates
✅ Docker registry credentials
```

### How Secrets are stored — Base64

Secrets are stored as **Base64 encoded** values in etcd (Kubernetes' internal database).

> ⚠️ IMPORTANT: Base64 is NOT encryption. It is just encoding — anyone can decode it:

```bash
# Encoding
echo -n "my-secret-password" | base64
# Output: bXktc2VjcmV0LXBhc3N3b3Jk

# Decoding — anyone can do this!
echo "bXktc2VjcmV0LXBhc3N3b3Jk" | base64 --decode
# Output: my-secret-password
```

Kubernetes Secrets are only as secure as your cluster access controls (RBAC). For production workloads, use external secret managers:
- AWS Secrets Manager
- HashiCorp Vault
- Sealed Secrets (encrypts the YAML so it's safe to commit to Git)

---

## ConfigMap vs Secret

| | ConfigMap | Secret |
|--|-----------|--------|
| Purpose | Non-sensitive config | Sensitive data |
| Storage in etcd | Plain text | Base64 encoded |
| Visible in kubectl describe | ✅ Shows values | ❌ Shows byte count only |
| Safe to commit to Git | ✅ Usually yes | ❌ Never |
| Use for | PORT, NODE_ENV, LOG_LEVEL | Passwords, tokens, keys |

### Real example

```
NODE_ENV = production       → ConfigMap ✅ (not sensitive)
PORT = 3000                 → ConfigMap ✅ (not sensitive)
LOG_LEVEL = info            → ConfigMap ✅ (not sensitive)
DATABASE_URL = postgresql://admin:pass@db:5432/mydb  → Secret 🔒
JWT_SECRET = my-secret-key  → Secret 🔒
RESEND_API_KEY = re_abc123  → Secret 🔒
```

---

## Creating ConfigMaps

### Method 1 — YAML file (recommended)

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: my-app
data:
  NODE_ENV: "production"
  PORT: "3000"
  LOG_LEVEL: "info"
  ALLOWED_ORIGINS: "https://app.com,https://admin.app.com"
  MAX_CONNECTIONS: "100"
```

> ⚠️ Always use quotes around values in ConfigMap data — even numbers:
> ```yaml
> PORT: "3000"    # ✅ string — correct
> PORT: 3000      # ❌ integer — can cause issues when app reads it as env var
> ```
> ConfigMap values must always be strings. Environment variables are always strings.

Apply it:
```bash
kubectl apply -f configmap.yaml
```

### Method 2 — From literal values (quick, no file needed)

```bash
kubectl create configmap api-config \
  --from-literal=NODE_ENV=production \
  --from-literal=PORT=3000 \
  --from-literal=LOG_LEVEL=info \
  -n my-app
```

Kubernetes handles quotes automatically. Good for quick testing.

### Method 3 — From an env file

Create a `.env` style file:
```bash
# app.env
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
```

Create ConfigMap from the file:
```bash
kubectl create configmap api-config \
  --from-env-file=app.env \
  -n my-app
```

### Method 4 — Multi-line file content

Use `|` to store entire file contents as a ConfigMap value:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: my-app
data:
  nginx.conf: |
    server {
      listen 80;
      server_name localhost;
      location / {
        proxy_pass http://api-service:3000;
      }
    }
```

The `|` means multi-line string — the entire nginx.conf content is stored as one value. Used when you want to mount config as a file inside the container.

### Verify ConfigMap was created

```bash
# List ConfigMaps
kubectl get configmap -n my-app
kubectl get cm -n my-app            # shorthand

# Show all values (plain text — not sensitive)
kubectl describe configmap api-config -n my-app

# Get full YAML
kubectl get configmap api-config -o yaml -n my-app
```

---

## Creating Secrets

### Method 1 — stringData YAML (recommended — no manual base64)

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: my-app
type: Opaque
stringData:                           # write plain text — K8s encodes automatically
  DATABASE_URL: "postgresql://admin:pass123@db:5432/mydb"
  JWT_SECRET: "my-jwt-secret-key-256-bits"
  RESEND_API_KEY: "re_abc123xyz"
```

`stringData` is much easier than `data` — you write plain text and Kubernetes automatically converts it to Base64 when saving.

Apply it:
```bash
kubectl apply -f secret.yaml
```

> ⚠️ Never commit `secret.yaml` with real values to Git. Add it to `.gitignore`:
> ```bash
> echo "secret.yaml" >> .gitignore
> echo "*.secret.yaml" >> .gitignore
> ```

### Method 2 — data YAML (manual base64)

If you must use `data` instead of `stringData`, you must base64 encode values first:

```bash
echo -n "postgresql://admin:pass123@db:5432/mydb" | base64
# Output: cG9zdGdyZXNxbDovL2FkbWluOnBhc3MxMjNAZGI6NTQzMi9teWRi

echo -n "my-jwt-secret" | base64
# Output: bXktand0LXNlY3JldA==
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: my-app
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL2FkbWluOnBhc3MxMjNAZGI6NTQzMi9teWRi
  JWT_SECRET: bXktand0LXNlY3JldA==
```

Use `stringData` instead — it's much cleaner and less error-prone.

### Method 3 — From literal values (quick)

```bash
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://admin:pass123@db:5432/mydb" \
  --from-literal=JWT_SECRET="my-jwt-secret-key-256-bits" \
  --from-literal=RESEND_API_KEY="re_abc123xyz" \
  -n my-app
```

Kubernetes handles base64 encoding automatically.

### Method 4 — From a .env file

```bash
# secrets.env — DO NOT commit to Git!
DATABASE_URL=postgresql://admin:pass123@db:5432/mydb
JWT_SECRET=my-jwt-secret-key-256-bits
RESEND_API_KEY=re_abc123xyz
```

```bash
kubectl create secret generic api-secrets \
  --from-env-file=secrets.env \
  -n my-app
```

### Verify Secret was created

```bash
# List secrets
kubectl get secrets -n my-app

# Describe — values are HIDDEN (shows byte count only)
kubectl describe secret api-secrets -n my-app
```

Output:
```
Name:         api-secrets
Namespace:    my-app
Type:         Opaque

Data
====
DATABASE_URL:  39 bytes    ← value hidden, shows size only 🔒
JWT_SECRET:    19 bytes    ← value hidden 🔒
RESEND_API_KEY: 12 bytes   ← value hidden 🔒
```

This is the key difference from ConfigMap — Secret values are always hidden in kubectl output.

### Decode a Secret value (when you need to check it)

```bash
kubectl get secret api-secrets -o jsonpath='{.data.DATABASE_URL}' -n my-app | base64 --decode
```

---

## Using ConfigMaps in Pods

### Way 1 — Inject all values at once (recommended)

```yaml
spec:
  containers:
    - name: api
      image: my-api:latest
      envFrom:
        - configMapRef:
            name: api-config    # ALL keys become environment variables
```

All keys in the ConfigMap automatically become environment variables in the container:
```
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
```

### Way 2 — Inject a single value

```yaml
spec:
  containers:
    - name: api
      image: my-api:latest
      env:
        - name: NODE_ENV          # env var name inside container
          valueFrom:
            configMapKeyRef:
              name: api-config    # ConfigMap name
              key: NODE_ENV       # key inside the ConfigMap
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: api-config
              key: PORT
```

Use this when you only need specific values — or when you want to rename a key.

### Reading values in your app

Once injected, your app reads them like any environment variable:

```javascript
// Node.js
const port = process.env.PORT          // "3000"
const env = process.env.NODE_ENV       // "production"
const logLevel = process.env.LOG_LEVEL // "info"
```

```python
# Python
import os
port = os.environ.get('PORT')          # "3000"
env = os.environ.get('NODE_ENV')       # "production"
```

```go
// Go
port := os.Getenv("PORT")             // "3000"
env := os.Getenv("NODE_ENV")          // "production"
```

---

## Using Secrets in Pods

Exactly the same pattern as ConfigMaps — just use `secretRef` and `secretKeyRef`:

### Inject all values at once (recommended)

```yaml
spec:
  containers:
    - name: api
      image: my-api:latest
      envFrom:
        - secretRef:
            name: api-secrets    # ALL secret keys become environment variables
```

### Inject a single value

```yaml
spec:
  containers:
    - name: api
      image: my-api:latest
      env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets    # Secret name
              key: DATABASE_URL    # key inside the Secret
```

### Combined ConfigMap + Secret (most common in production)

```yaml
spec:
  containers:
    - name: api
      image: my-api:latest
      envFrom:
        - configMapRef:
            name: api-config      # non-sensitive: NODE_ENV, PORT, LOG_LEVEL
        - secretRef:
            name: api-secrets     # sensitive: DATABASE_URL, JWT_SECRET
```

Your app receives ALL values as environment variables — it doesn't know or care which came from ConfigMap and which from Secret. It just reads `process.env.DATABASE_URL` and it works.

---

## Common Mistakes When Injecting Config

These are the mistakes beginners make most often:

### Mistake 1 — Number values without quotes

```yaml
# ❌ Wrong — PORT is an integer
data:
  PORT: 80

# ✅ Correct — PORT is a string
data:
  PORT: "80"
```

ConfigMap values must be strings. Without quotes, YAML treats `80` as an integer — which can cause issues when read as an environment variable.

### Mistake 2 — envFrom in wrong indentation level

This is the most common indentation mistake:

```yaml
# ❌ Wrong — envFrom is at container list level, not inside container
spec:
  containers:
    - name: nginx
      image: nginx:alpine
    envFrom:                  ← same level as "- name: nginx" — WRONG!
      - configMapRef:
          name: api-config

# ✅ Correct — envFrom is inside the container definition
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      envFrom:                ← indented under the container — CORRECT!
        - configMapRef:
            name: api-config
```

Rule to remember: `name`, `image`, and `envFrom` are all **properties of the same container** — they must be at the same indentation level:

```yaml
containers:
  - name: nginx          ← 10 spaces
    image: nginx:alpine  ← 10 spaces
    envFrom:             ← 10 spaces (same level!)
      - configMapRef:
          name: api-config
```

### Mistake 3 — Wrong ConfigMap or Secret name

```yaml
envFrom:
  - configMapRef:
      name: api-configs    # ❌ typo — should be "api-config"
```

If the name doesn't match exactly, the Pod will fail to start with:
```
Error: configmap "api-configs" not found
```

Always double-check the name with `kubectl get configmap -n <namespace>`.

### Mistake 4 — Forgetting to restart Pods after update

When you update a ConfigMap or Secret:

```
Environment variables → ❌ Pods do NOT update automatically
                          You must restart the Pods
```

```bash
kubectl rollout restart deployment/my-api -n my-app
```

---

## Verifying Config Inside a Pod

After injecting a ConfigMap or Secret, always verify the values are actually inside the Pod.

### Step 1 — Get the Pod name

```bash
kubectl get pods -n my-app
```

### Step 2 — Shell into the Pod

```bash
kubectl exec -it <pod-name> -n my-app -- sh
```

### Step 3 — Check environment variables

```bash
# Check all env vars
env

# Check specific ones (using grep)
env | grep -E "NODE_ENV|PORT|LOG_LEVEL"

# Check secrets
env | grep -E "DATABASE_URL|JWT_SECRET"
```

Expected output:
```
NODE_ENV=production
PORT=3000
LOG_LEVEL=info
DATABASE_URL=postgresql://admin:pass123@db:5432/mydb
JWT_SECRET=my-jwt-secret-key-256-bits
```

### Step 4 — Exit the Pod

```bash
exit
```

This is the most reliable way to confirm your config is working before deploying to production.

---

## Mounting as Files

Sometimes your app needs config as a **file** on disk rather than environment variables. Common examples:

- NGINX needs a `nginx.conf` file
- An app needs a `config.json` file
- TLS needs `.crt` and `.key` files

### Mount a ConfigMap as a file

First create the ConfigMap with file content:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: my-app
data:
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://api-service:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
      }
    }
```

Then mount it in the Deployment:

```yaml
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          volumeMounts:
            - name: nginx-config-volume
              mountPath: /etc/nginx/nginx.conf    # path inside container
              subPath: nginx.conf                 # which ConfigMap key to mount
      volumes:
        - name: nginx-config-volume
          configMap:
            name: nginx-config                    # which ConfigMap to use
```

Result: The `nginx.conf` content from ConfigMap appears at `/etc/nginx/nginx.conf` inside the container — as if it was a real file.

### Mount a Secret as a file (TLS certificates)

```bash
# Create secret from certificate files
kubectl create secret tls my-tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/key.key \
  -n my-app
```

```yaml
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          volumeMounts:
            - name: tls-certs
              mountPath: /etc/ssl/certs    # directory in container
              readOnly: true               # security — don't let app modify certs
      volumes:
        - name: tls-certs
          secret:
            secretName: my-tls-secret
```

Result: Certificate files appear at `/etc/ssl/certs/tls.crt` and `/etc/ssl/certs/tls.key`.

### Mount entire ConfigMap as a directory

```yaml
volumeMounts:
  - name: config-volume
    mountPath: /app/config    # all ConfigMap keys become files in this dir
volumes:
  - name: config-volume
    configMap:
      name: my-config
```

If ConfigMap has keys `app.json` and `db.json`, the container sees:
```
/app/config/app.json
/app/config/db.json
```

### envFrom vs volumeMount — when to use which

```
envFrom (env variables) → use when app reads config via process.env
                          most Node.js, Python, Go apps use this

volumeMount (files)     → use when app reads config from a file
                          NGINX, Java apps, certificate-based auth
```

---

## Updating ConfigMaps and Secrets

### Update a ConfigMap

```bash
# Edit directly in terminal
kubectl edit configmap api-config -n my-app

# Or update YAML file and apply
kubectl apply -f configmap.yaml
```

### Do Pods automatically get new values?

It depends on HOW you inject the config:

```
Mounted as files (volumeMount) → ✅ Pods update automatically (~60 seconds)
As env variables (envFrom)     → ❌ Pods do NOT update automatically
                                   Must restart Pods manually
```

### Restart Pods to pick up new env var values

```bash
kubectl rollout restart deployment/my-api -n my-app
```

This does a rolling restart — new Pods pick up latest ConfigMap/Secret values while old Pods are still serving traffic. Zero downtime.

### Update a Secret

```bash
# Method 1 — Patch a specific key
kubectl patch secret api-secrets \
  -p '{"stringData":{"JWT_SECRET":"new-secret-value"}}' \
  -n my-app

# Method 2 — Delete and recreate (most common)
kubectl delete secret api-secrets -n my-app
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="new-url" \
  --from-literal=JWT_SECRET="new-secret" \
  -n my-app

# Then restart Pods to pick up new values
kubectl rollout restart deployment/my-api -n my-app
```

---

## Secret Types

Kubernetes has built-in Secret types for specific use cases:

### Opaque (most common — use for everything generic)

```yaml
type: Opaque
```

```bash
kubectl create secret generic my-secret \
  --from-literal=KEY=value \
  -n my-app
```

Use for: passwords, API keys, JWT secrets, database URLs.

### docker-registry — Pull from private registry

When your Docker image is in a private registry (GHCR, Docker Hub private):

```bash
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=mustafatawab \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n my-app
```

Use it in Deployment to pull private images:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ghcr-credentials    # use this to authenticate with GHCR
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
```

Without this, Kubernetes can't pull your private image and Pods will fail with `ImagePullBackOff`.

### tls — SSL/TLS certificates

```bash
kubectl create secret tls my-tls \
  --cert=cert.crt \
  --key=key.key \
  -n my-app
```

Use for: NGINX HTTPS, Ingress TLS termination.

### service-account-token — Service account auth

Automatically created by Kubernetes for Service Accounts. You rarely create these manually.

### Summary table

| Type | Command | Use case |
|------|---------|---------|
| `Opaque` | `create secret generic` | Passwords, API keys, tokens |
| `docker-registry` | `create secret docker-registry` | Pull from private registry |
| `tls` | `create secret tls` | SSL/TLS certificates |
| `service-account-token` | Auto-created | Service account auth |

---

## Real World Example

Here is a complete production-ready setup for **Atlas Edu** — a school management SaaS:

### Project structure

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── deployment.yaml
└── service.yaml
# secrets are created via kubectl, not committed to Git!
```

### Step 1 — Create namespace

```bash
kubectl create namespace atlas-edu
```

### Step 2 — ConfigMap (non-sensitive config)

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: atlas-edu
data:
  NODE_ENV: "production"
  PORT: "9000"
  LOG_LEVEL: "info"
  FRONTEND_URL: "https://app.maktabone.org"
  MAX_LOGIN_ATTEMPTS: "5"
  TOKEN_EXPIRY: "15m"
  REFRESH_TOKEN_EXPIRY: "7d"
```

```bash
kubectl apply -f configmap.yaml
```

### Step 3 — Secrets (sensitive config — NOT in Git)

```bash
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://admin:securepass@db-service:5432/atlas_edu" \
  --from-literal=JWT_SECRET="your-256-bit-secret-key-here" \
  --from-literal=JWT_REFRESH_SECRET="your-refresh-secret-key-here" \
  --from-literal=RESEND_API_KEY="re_yourkeyhere" \
  --from-literal=BCRYPT_ROUNDS="12" \
  -n atlas-edu
```

### Step 4 — GHCR pull secret (to pull private image)

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=mustafatawab \
  --docker-password=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN \
  -n atlas-edu
```

### Step 5 — Deployment using both

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: atlas-edu-api
  namespace: atlas-edu
  labels:
    app: atlas-edu-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: atlas-edu-api
  template:
    metadata:
      labels:
        app: atlas-edu-api
    spec:
      imagePullSecrets:
        - name: ghcr-pull-secret       # authenticate with GHCR
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
          ports:
            - containerPort: 9000
          envFrom:
            - configMapRef:
                name: api-config       # NODE_ENV, PORT, LOG_LEVEL...
            - secretRef:
                name: api-secrets      # DATABASE_URL, JWT_SECRET...
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 10
            periodSeconds: 5
```

### Step 6 — Apply and verify

```bash
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml

# Verify everything is running
kubectl get all -n atlas-edu

# Verify config is injected
kubectl get pods -n atlas-edu
kubectl exec -it <pod-name> -n atlas-edu -- sh
env | grep -E "NODE_ENV|PORT|DATABASE_URL|JWT_SECRET"
exit
```

### Step 7 — Different config per environment

The same Deployment YAML works for staging and production. Only ConfigMaps and Secrets differ:

```bash
# Production
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://prod-db/atlas_edu" \
  -n atlas-edu-production

# Staging
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://staging-db/atlas_edu" \
  -n atlas-edu-staging
```

Same Secret name (`api-secrets`), different values, different namespaces. Your Deployment YAML never changes! ✅

---

## Essential Commands

### ConfigMap commands

```bash
# Create from YAML
kubectl apply -f configmap.yaml

# Create from literals
kubectl create configmap <name> --from-literal=KEY=VALUE -n <ns>

# Create from env file
kubectl create configmap <name> --from-env-file=app.env -n <ns>

# List ConfigMaps
kubectl get configmap -n <ns>
kubectl get cm -n <ns>                    # shorthand

# Show all values
kubectl describe configmap <name> -n <ns>

# Get full YAML
kubectl get configmap <name> -o yaml -n <ns>

# Edit directly
kubectl edit configmap <name> -n <ns>

# Delete
kubectl delete configmap <name> -n <ns>
kubectl delete -f configmap.yaml
```

### Secret commands

```bash
# Create from stringData YAML
kubectl apply -f secret.yaml

# Create from literals (no manual base64)
kubectl create secret generic <name> \
  --from-literal=KEY=VALUE \
  -n <ns>

# Create from env file
kubectl create secret generic <name> \
  --from-env-file=secrets.env \
  -n <ns>

# Create docker registry secret
kubectl create secret docker-registry <name> \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n <ns>

# Create TLS secret
kubectl create secret tls <name> \
  --cert=cert.crt \
  --key=key.key \
  -n <ns>

# List secrets
kubectl get secrets -n <ns>

# Describe (values hidden)
kubectl describe secret <name> -n <ns>

# Decode a specific value
kubectl get secret <name> -o jsonpath='{.data.KEY}' -n <ns> | base64 --decode

# Delete
kubectl delete secret <name> -n <ns>

# Restart Pods to pick up new values
kubectl rollout restart deployment/<name> -n <ns>
```

---

## Quick Reference

### ConfigMap vs Secret decision

```
Is the value sensitive? (password, token, key)
  YES → Secret 🔒
  NO  → ConfigMap ✅

Examples:
  NODE_ENV=production    → ConfigMap ✅
  PORT=3000              → ConfigMap ✅
  DATABASE_URL=...       → Secret 🔒 (contains password)
  JWT_SECRET=...         → Secret 🔒
  RESEND_API_KEY=...     → Secret 🔒
```

### Injection patterns

```yaml
# Pattern 1 — All ConfigMap values
envFrom:
  - configMapRef:
      name: api-config

# Pattern 2 — All Secret values
envFrom:
  - secretRef:
      name: api-secrets

# Pattern 3 — Combined (most common in production)
envFrom:
  - configMapRef:
      name: api-config
  - secretRef:
      name: api-secrets

# Pattern 4 — Single value from ConfigMap
env:
  - name: PORT
    valueFrom:
      configMapKeyRef:
        name: api-config
        key: PORT

# Pattern 5 — Single value from Secret
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: api-secrets
        key: DATABASE_URL
```

### Verify inside Pod

```bash
kubectl exec -it <pod-name> -n <ns> -- sh
env | grep -E "NODE_ENV|PORT|DATABASE_URL"
exit
```

### Decode a Secret value

```bash
kubectl get secret <name> -o jsonpath='{.data.KEY}' -n <ns> | base64 --decode
```

### Restart after update

```bash
kubectl rollout restart deployment/<name> -n <ns>
```

### Common mistakes table

| Mistake | Fix |
|---------|-----|
| Number values without quotes: `PORT: 80` | Always quote: `PORT: "80"` |
| `envFrom` at wrong indentation level | `envFrom` must be inside container, same level as `name` and `image` |
| Committing secrets to Git | Use `.gitignore` + `kubectl create secret` instead of YAML |
| ConfigMap name typo | Check exact name: `kubectl get cm -n <ns>` |
| Not restarting Pods after update | `kubectl rollout restart deployment/<name>` |
| Using `data` instead of `stringData` | Use `stringData` — no manual base64 needed |
| Same Secret values across environments | Create per-namespace Secrets with different values |
| Forgot to create imagePullSecret | `kubectl create secret docker-registry ghcr-credentials ...` |
