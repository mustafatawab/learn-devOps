# 06 - ConfigMaps & Secrets

A complete beginner-friendly guide to ConfigMaps and Secrets - how to inject configuration and sensitive data into your Pods without hardcoding anything.

---

## Table of Contents

1. [The Problem - Hardcoded Config](#the-problem--hardcoded-config)
2. [What is a ConfigMap?](#what-is-a-configmap)
3. [What is a Secret?](#what-is-a-secret)
4. [ConfigMap vs Secret](#configmap-vs-secret)
5. [Creating ConfigMaps](#creating-configmaps)
6. [Creating Secrets](#creating-secrets)
7. [Using ConfigMaps in Pods](#using-configmaps-in-pods)
8. [Using Secrets in Pods](#using-secrets-in-pods)
9. [Mounting as Files](#mounting-as-files)
10. [Updating ConfigMaps and Secrets](#updating-configmaps-and-secrets)
11. [Secret Types](#secret-types)
12. [Real World Example](#real-world-example)
13. [Essential Commands](#essential-commands)
14. [Quick Reference](#quick-reference)

---

## The Problem - Hardcoded Config

Imagine you Dockerize your Node.js API and hardcode the database URL inside:

```javascript
// ❌ Hardcoded inside your code
const db = new Client({
  connectionString: "postgresql://admin:password123@prod-db:5432/atlas_edu"
})
```

Or worse, hardcoded inside your Deployment YAML:

```yaml
# ❌ Hardcoded in YAML
env:
  - name: DATABASE_URL
    value: "postgresql://admin:password123@prod-db:5432/atlas_edu"
  - name: JWT_SECRET
    value: "my-super-secret-jwt-key"
```

**Problems with this approach:**

```
Security    → passwords visible in Git history forever ❌
Flexibility → different values for staging vs production requires different YAML files ❌
Rotation    → changing a password requires rebuilding the Docker image ❌
Sharing     → can't share the same config across multiple Deployments ❌
Auditability → no central place to see all config values ❌
```

**The solution: ConfigMaps and Secrets**

```
Non-sensitive config  → ConfigMap  (NODE_ENV, PORT, LOG_LEVEL)
Sensitive config      → Secret     (DATABASE_URL, JWT_SECRET, API_KEYS)
```

---

## What is a ConfigMap?

A **ConfigMap** is a Kubernetes object that stores **non-sensitive** configuration data as key-value pairs.

Think of a ConfigMap like a **settings file** for your app - but stored in Kubernetes instead of on disk:

```
ConfigMap: api-config
  NODE_ENV = production
  PORT = 3000
  LOG_LEVEL = info
  ALLOWED_ORIGINS = https://app.com,https://api.com
```

Your Pods read these values at runtime - no hardcoding needed.

### What to store in ConfigMap

```
✅ NODE_ENV (development, staging, production)
✅ PORT numbers
✅ Log levels
✅ Feature flags
✅ CORS allowed origins
✅ API base URLs (non-sensitive)
✅ Timeout values
✅ Pagination limits
✅ Config files (nginx.conf, app.properties)
```

---

## What is a Secret?

A **Secret** is a Kubernetes object that stores **sensitive** data - passwords, tokens, certificates, private keys.

Think of a Secret like a **locked safe** - the data is encoded and access is controlled:

```
Secret: api-secrets
  DATABASE_URL = postgresql://admin:pass123@db:5432/mydb
  JWT_SECRET = eyJhbGciOiJIUzI1NiJ9...
  RESEND_API_KEY = re_abc123...
  SMTP_PASSWORD = myEmailPass456
```

### What to store in Secret

```
✅ Database connection strings (with passwords)
✅ JWT secrets
✅ API keys (Resend, Stripe, OpenAI, etc.)
✅ OAuth client secrets
✅ SMTP credentials
✅ SSH private keys
✅ TLS certificates
✅ Docker registry credentials
```

### How Secrets are stored

Secrets are stored as **Base64 encoded** values in etcd (Kubernetes database). Base64 is NOT encryption - it is just encoding:

```
"my-secret-password"
    ↓ base64 encode
"bXktc2VjcmV0LXBhc3N3b3Jk"
    ↓ base64 decode (anyone can do this!)
"my-secret-password"
```

> Important: Base64 is NOT security. Kubernetes Secrets are only as secure as your cluster access controls (RBAC). For production, use external secret managers like AWS Secrets Manager, HashiCorp Vault, or Sealed Secrets.

---

## ConfigMap vs Secret

| | ConfigMap | Secret |
|--|-----------|--------|
| Purpose | Non-sensitive config | Sensitive data |
| Storage | Plain text in etcd | Base64 encoded in etcd |
| Visible in kubectl | ✅ Yes | ❌ Values hidden by default |
| Use for | PORT, NODE_ENV, LOG_LEVEL | Passwords, tokens, keys |
| Git safe | ✅ Usually yes | ❌ Never commit secrets to Git |

---

## Creating ConfigMaps

### Method 1 - From a YAML file (recommended)

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

Apply it:

```bash
kubectl apply -f configmap.yaml
```

### Method 2 - From literal values (quick)

```bash
kubectl create configmap api-config \
  --from-literal=NODE_ENV=production \
  --from-literal=PORT=3000 \
  --from-literal=LOG_LEVEL=info \
  -n my-app
```

### Method 3 - From a file

Create a config file:

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

### Method 4 - From a whole file (as a mounted file later)

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

The `|` means multi-line string - the entire nginx.conf content is stored as one value.

### Verify ConfigMap was created

```bash
kubectl get configmap -n my-app
kubectl get cm -n my-app              # shorthand

kubectl describe configmap api-config -n my-app

# View the full YAML
kubectl get configmap api-config -o yaml -n my-app
```

---

## Creating Secrets

### Method 1 - From a YAML file

Secrets in YAML require **base64 encoded values**:

```bash
# First encode your values
echo -n "postgresql://admin:pass123@db:5432/mydb" | base64
# Output: cG9zdGdyZXNxbDovL2FkbWluOnBhc3MxMjNAZGI6NTQzMi9teWRi

echo -n "my-jwt-secret-key-256-bits" | base64
# Output: bXktand0LXNlY3JldC1rZXktMjU2LWJpdHM=
```

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: my-app
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL2FkbWluOnBhc3MxMjNAZGI6NTQzMi9teWRi
  JWT_SECRET: bXktand0LXNlY3JldC1rZXktMjU2LWJpdHM=
```

> Never commit this YAML to Git with real secret values. Use .gitignore or external secret management.

### Method 2 - From literal values (recommended - no manual base64)

```bash
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://admin:pass123@db:5432/mydb" \
  --from-literal=JWT_SECRET="my-jwt-secret-key-256-bits" \
  --from-literal=RESEND_API_KEY="re_abc123xyz" \
  -n my-app
```

Kubernetes handles the base64 encoding automatically. Much easier!

### Method 3 - From a .env file

```bash
# secrets.env (DO NOT commit this to Git!)
DATABASE_URL=postgresql://admin:pass123@db:5432/mydb
JWT_SECRET=my-jwt-secret-key-256-bits
RESEND_API_KEY=re_abc123xyz
```

```bash
kubectl create secret generic api-secrets \
  --from-env-file=secrets.env \
  -n my-app
```

### Method 4 - Using stringData (human readable YAML)

```yaml
# Kubernetes auto-encodes stringData to base64
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: my-app
type: Opaque
stringData:                           # plain text - Kubernetes encodes it
  DATABASE_URL: "postgresql://admin:pass123@db:5432/mydb"
  JWT_SECRET: "my-jwt-secret-key-256-bits"
  RESEND_API_KEY: "re_abc123xyz"
```

`stringData` lets you write plain text - Kubernetes converts it to base64 automatically. Much easier than `data`.

### Verify Secret was created

```bash
kubectl get secrets -n my-app

# Describe (values are hidden by default)
kubectl describe secret api-secrets -n my-app

# View base64 encoded values
kubectl get secret api-secrets -o yaml -n my-app

# Decode a specific value
kubectl get secret api-secrets -o jsonpath='{.data.DATABASE_URL}' -n my-app | base64 --decode
```

---

## Using ConfigMaps in Pods

There are two ways to use a ConfigMap in a Pod:

### Way 1 - As environment variables

**Single value:**

```yaml
env:
  - name: NODE_ENV
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

**All values at once (recommended):**

```yaml
envFrom:
  - configMapRef:
      name: api-config      # inject ALL keys as environment variables
```

This is cleaner - all ConfigMap keys become environment variables automatically.

### Way 2 - As mounted files

See the [Mounting as Files](#mounting-as-files) section below.

### Full Deployment example with ConfigMap

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
  namespace: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-api
  template:
    metadata:
      labels:
        app: my-api
    spec:
      containers:
        - name: api
          image: my-api:latest
          envFrom:
            - configMapRef:
                name: api-config     # all ConfigMap values as env vars
```

Inside the container, your app can read them normally:

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

---

## Using Secrets in Pods

Exactly the same as ConfigMaps - just use `secretRef` and `secretKeyRef` instead.

### Single value

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: api-secrets    # Secret name
        key: DATABASE_URL    # key inside the Secret
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: api-secrets
        key: JWT_SECRET
```

### All values at once (recommended)

```yaml
envFrom:
  - secretRef:
      name: api-secrets      # inject ALL secret keys as environment variables
```

### Combined - ConfigMap + Secret

The most common production pattern:

```yaml
envFrom:
  - configMapRef:
      name: api-config       # non-sensitive config
  - secretRef:
      name: api-secrets      # sensitive config
```

Your app gets ALL values as environment variables - it doesn't know or care which came from ConfigMap and which from Secret.

### Full Deployment example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: atlas-edu-api
  namespace: atlas-edu
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
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
          ports:
            - containerPort: 9000
          envFrom:
            - configMapRef:
                name: api-config      # NODE_ENV, PORT, LOG_LEVEL
            - secretRef:
                name: api-secrets     # DATABASE_URL, JWT_SECRET
```

---

## Mounting as Files

Sometimes your app needs config as a **file** rather than environment variables. For example:

- NGINX needs an `nginx.conf` file
- A TLS certificate needs a `.crt` file
- An app config needs a `config.json` file

### Mount a ConfigMap as a file

```yaml
# ConfigMap with file content
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
      }
    }
```

```yaml
# Mount in Deployment
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          volumeMounts:
            - name: nginx-config-volume
              mountPath: /etc/nginx/nginx.conf    # where to mount in container
              subPath: nginx.conf                 # which key to mount as file
      volumes:
        - name: nginx-config-volume
          configMap:
            name: nginx-config                    # which ConfigMap to use
```

Result: The `nginx.conf` content from the ConfigMap appears at `/etc/nginx/nginx.conf` inside the container.

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
              mountPath: /etc/ssl/certs
              readOnly: true
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
    mountPath: /app/config    # all ConfigMap keys become files here
volumes:
  - name: config-volume
    configMap:
      name: my-config
```

If ConfigMap has keys `app.json` and `db.json`, the container will see:
```
/app/config/app.json
/app/config/db.json
```

---

## Updating ConfigMaps and Secrets

### Updating a ConfigMap

```bash
# Edit directly
kubectl edit configmap api-config -n my-app

# Or update YAML and apply
kubectl apply -f configmap.yaml
```

### Do Pods automatically get updates?

It depends on HOW you use the ConfigMap:

```
Mounted as files    → ✅ Pods get updates automatically (within ~1 minute)
As env variables    → ❌ Pods do NOT get updates automatically
                        You must restart the Pods
```

### Restart Pods to pick up new env var values

```bash
# Restart all Pods in a Deployment to pick up new config
kubectl rollout restart deployment/my-api -n my-app
```

This does a rolling restart - new Pods pick up the latest ConfigMap/Secret values while old Pods are still running.

### Update a Secret

```bash
# Update a single key in a Secret
kubectl patch secret api-secrets \
  -p '{"stringData":{"JWT_SECRET":"new-secret-value"}}' \
  -n my-app

# Or delete and recreate (most common approach)
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

Kubernetes has several built-in Secret types for specific use cases:

### Opaque (most common)

Generic key-value secrets - use for everything that doesn't fit other types:

```yaml
type: Opaque
```

```bash
kubectl create secret generic my-secret --from-literal=key=value
```

### kubernetes.io/dockerconfigjson - Docker registry credentials

Used to pull images from private registries (GHCR, Docker Hub private repos):

```bash
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=mustafatawab \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n my-app
```

Use it in a Deployment to pull private images:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ghcr-credentials    # use this secret to pull images
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
```

### kubernetes.io/tls - TLS certificates

For storing SSL/TLS certificates:

```bash
kubectl create secret tls my-tls \
  --cert=cert.crt \
  --key=key.key \
  -n my-app
```

### kubernetes.io/service-account-token

Automatically created for Service Accounts - you rarely create these manually.

### Summary table

| Type | Use case |
|------|---------|
| `Opaque` | Generic secrets (passwords, API keys, tokens) |
| `docker-registry` | Pull images from private Docker registries |
| `tls` | TLS/SSL certificates |
| `service-account-token` | Service account authentication (auto-created) |

---

## Real World Example

Here is a complete setup for **Atlas Edu** with proper ConfigMaps and Secrets:

### 1. Create Namespace

```bash
kubectl create namespace atlas-edu
```

### 2. ConfigMap - non-sensitive config

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

### 3. Secret - sensitive config

```bash
# Create secret (never put real values in YAML committed to Git)
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL="postgresql://admin:securepass@db-service:5432/atlas_edu" \
  --from-literal=JWT_SECRET="your-256-bit-secret-key-here" \
  --from-literal=JWT_REFRESH_SECRET="your-refresh-secret-key-here" \
  --from-literal=RESEND_API_KEY="re_yourkeyhere" \
  --from-literal=BCRYPT_ROUNDS="12" \
  -n atlas-edu
```

### 4. GHCR pull secret (for private image)

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=mustafatawab \
  --docker-password=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN \
  -n atlas-edu
```

### 5. Deployment using both

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: atlas-edu-api
  namespace: atlas-edu
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
        - name: ghcr-pull-secret       # pull private image from GHCR
      containers:
        - name: api
          image: ghcr.io/mustafatawab/atlas-edu-api:latest
          ports:
            - containerPort: 9000
          envFrom:
            - configMapRef:
                name: api-config        # NODE_ENV, PORT, LOG_LEVEL...
            - secretRef:
                name: api-secrets       # DATABASE_URL, JWT_SECRET...
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

### 6. Apply everything in order

```bash
# Apply ConfigMap first
kubectl apply -f configmap.yaml

# Apply Deployment (Secret already created via kubectl create)
kubectl apply -f deployment.yaml

# Verify
kubectl get all -n atlas-edu
kubectl describe deployment atlas-edu-api -n atlas-edu
```

### 7. Different values per environment

Same Deployment YAML works for staging and production - only the ConfigMaps and Secrets differ:

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

Same Deployment YAML, same Secret name - different values per namespace!

---

## Essential Commands

### ConfigMap commands

```bash
# Create ConfigMap from YAML
kubectl apply -f configmap.yaml

# Create ConfigMap from literals
kubectl create configmap <name> --from-literal=KEY=VALUE -n <ns>

# Create ConfigMap from env file
kubectl create configmap <name> --from-env-file=app.env -n <ns>

# List ConfigMaps
kubectl get configmap -n <ns>
kubectl get cm -n <ns>

# Describe ConfigMap (shows all values)
kubectl describe configmap <name> -n <ns>

# Get full YAML
kubectl get configmap <name> -o yaml -n <ns>

# Edit ConfigMap directly
kubectl edit configmap <name> -n <ns>

# Delete ConfigMap
kubectl delete configmap <name> -n <ns>
```

### Secret commands

```bash
# Create Secret from literals
kubectl create secret generic <name> \
  --from-literal=KEY=VALUE \
  -n <ns>

# Create Secret from env file
kubectl create secret generic <name> \
  --from-env-file=secrets.env \
  -n <ns>

# Create Docker registry secret
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

# List Secrets
kubectl get secrets -n <ns>

# Describe Secret (values hidden)
kubectl describe secret <name> -n <ns>

# View encoded values
kubectl get secret <name> -o yaml -n <ns>

# Decode a specific value
kubectl get secret <name> -o jsonpath='{.data.KEY}' -n <ns> | base64 --decode

# Delete Secret
kubectl delete secret <name> -n <ns>

# Restart Pods to pick up new values
kubectl rollout restart deployment/<name> -n <ns>
```

---

## Quick Reference

### When to use what

```
ConfigMap  → NODE_ENV, PORT, LOG_LEVEL, feature flags, CORS origins
Secret     → DATABASE_URL, JWT_SECRET, API_KEYS, passwords, certificates
```

### Three ways to inject config

```yaml
# 1. Single value from ConfigMap
env:
  - name: PORT
    valueFrom:
      configMapKeyRef:
        name: api-config
        key: PORT

# 2. All values from ConfigMap
envFrom:
  - configMapRef:
      name: api-config

# 3. All values from Secret
envFrom:
  - secretRef:
      name: api-secrets

# 4. Combined (most common in production)
envFrom:
  - configMapRef:
      name: api-config
  - secretRef:
      name: api-secrets
```

### Decode a secret value

```bash
kubectl get secret <name> -o jsonpath='{.data.KEY}' -n <ns> | base64 --decode
```

### Restart Pods to pick up new config

```bash
kubectl rollout restart deployment/<name> -n <ns>
```

### Common mistakes

| Mistake | Fix |
|---------|-----|
| Committing secrets to Git | Use .gitignore + external secret manager |
| Using ConfigMap for passwords | Move sensitive data to Secret |
| Not restarting Pods after update | kubectl rollout restart deployment |
| Forgetting namespace | Always add -n namespace to commands |
| Wrong key name in valueFrom | Check exact key name with kubectl describe configmap |
| base64 encoding manually | Use stringData in YAML or kubectl create secret |
| Same Secret across all environments | Create per-namespace Secrets with environment-specific values |