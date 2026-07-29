# 🚀 Learn DevOps

A hands-on DevOps learning journey — from Docker fundamentals to Kubernetes, CI/CD pipelines, and Cloud platforms. Every concept is learned by building real projects.

---

## 🗺️ Roadmap

```
Phase 1 → Docker          ✅ Complete
Phase 2 → CI/CD Pipeline  ✅ Complete
Phase 3 → Networking      ✅ Complete
Phase 4 → Kubernetes      🔄 In Progress
Phase 5 → Cloud Platform  ⬜ Upcoming
```

---

## 📂 Repository Structure

```
learn-devOps/
├── 01-containerization/
│   ├── docker_containerization.md   # Docker concepts, Dockerfile, multi-stage builds
│   └── docker_compose.md            # Docker Compose deep dive
├── 02-networking/
│   └── reverse_proxy.md             # NGINX reverse proxy, SSL, load balancing
├── 03-ci-cd/
│   ├── cicd_pipelines.md            # GitHub Actions CI/CD concepts
│   ├── README.md            # GitHub Actions CI/CD concepts
│   └── templates/                   # Ready-made pipeline templates
│       ├── nextjs/
│       ├── nextjs-node/
│       ├── nextjs-fastapi/
│       ├── fastapi/
│       └── laravel/
├── 04-kubernetes/                   # Kubernetes notes (in progress)
├── 05-cloud/                        # Cloud platform notes (upcoming)
├── app/                             # Practice application
└── Linux.md                         # Linux fundamentals
```

---

## Phase 1 — Docker 🐳

> **Goal:** Understand containerization deeply and write production-ready Dockerfiles.

### What I Learned

- **Linux fundamentals** — `apt`, `sudo`, environment variables (`$USER`, `$HOME`, `$PATH`), `curl`, pipe (`|`)
- **Docker architecture** — daemon, socket, images, containers, layers, Docker Hub
- **Image layer caching** — order Dockerfile instructions from least-changing to most-changing
- **Multi-stage builds** — separate build stage from production stage to minimize image size
- **Docker networks** — containers communicate using service/container names as hostnames
- **Docker volumes** — named volumes for persistence, bind mounts for dev hot-reload
- **Docker Compose** — orchestrate multi-container apps with a single `compose.yaml`

### Notes

| File | Description |
|------|-------------|
| [docker_containerization.md](./01-containerization/docker_containerization.md) | Docker concepts, Dockerfile reference, multi-stage builds, volumes, networks, commands |
| [docker_compose.md](./01-containerization/docker_compose.md) | Compose services, networks, volumes, depends_on, healthchecks, restart policies |

### Key Concepts

**Single-stage vs Multi-stage builds:**
```dockerfile
# ❌ Single stage — dev tools end up in production image (~900MB)
FROM node:22-alpine
RUN npm install        # includes TypeScript, nodemon, @types/*
RUN npm run build
CMD ["node", "dist/server.js"]

# ✅ Multi-stage — only compiled output in production (~180MB)
FROM node:22-alpine AS builder
RUN npm install
RUN npm run build

FROM node:22-alpine AS runner
COPY --from=builder /app/dist ./dist
RUN npm install --omit=dev
CMD ["node", "dist/server.js"]
```

**Container networking:**
```
# Containers on the same network talk via service name
DATABASE_URL=postgresql://user:pass@db:5432/mydb
#                                    ↑
#                              service name = hostname
```

**Layer caching strategy:**
```dockerfile
COPY package*.json ./    # ← copy this first (changes rarely)
RUN npm install          # ← cached unless package.json changes
COPY . .                 # ← copy code last (changes often)
```

---

## Phase 2 — CI/CD Pipeline ⚙️

> **Goal:** Automate build → test → deploy on every push using GitHub Actions.

### What I Learned

- **GitHub Actions concepts** — workflows, jobs, steps, actions, triggers
- **`uses` vs `run`** — pre-built actions vs shell commands
- **`needs`** — job dependencies (sequential jobs)
- **`${{ }}`** — GitHub Actions expression syntax
- **Secrets** — store credentials safely, never hardcode
- **Caching** — `cache: "npm"` and Docker layer caching (`type=gha`)
- **Two-workflow pattern** — `ci.yml` for PRs, `cd.yml` for deployments
- **GHCR** — GitHub Container Registry for Docker images
- **Auto-formatting** — Prettier workflow that commits formatted code

### Notes

| File | Description |
|------|-------------|
| [cicd_pipelines.md](./03-ci-cd/cicd_pipelines.md) | Full CI/CD guide with concepts, triggers, secrets, caching |

### Templates

| Stack | CI | CD |
|-------|----|----|
| Next.js | [ci.yml](./03-ci-cd/templates/nextjs/ci.yml) | [cd.yml](./03-ci-cd/templates/nextjs/cd.yml) |
| Next.js + Node.js | [ci.yml](./03-ci-cd/templates/nextjs-node/ci.yml) | [cd.yml](./03-ci-cd/templates/nextjs-node/cd.yml) |
| Next.js + FastAPI | [ci.yml](./03-ci-cd/templates/nextjs-fastapi/ci.yml) | [cd.yml](./03-ci-cd/templates/nextjs-fastapi/cd.yml) |
| FastAPI | [ci.yml](./03-ci-cd/templates/fastapi/ci.yml) | [cd.yml](./03-ci-cd/templates/fastapi/cd.yml) |
| Laravel | [ci.yml](./03-ci-cd/templates/laravel/ci.yml) | [cd.yml](./03-ci-cd/templates/laravel/cd.yml) |

### Key Concepts

**Two-workflow pattern:**
```
PR opened       → ci.yml  → test + build only
PR merged       → cd.yml  → build image → push GHCR → deploy via SSH
```

**Job dependency chain:**
```
test → build-and-push → deploy
 ↑           ↑              ↑
fails?    never runs    never runs
```

**Never build on the server:**
```
❌ Wrong: server runs docker build (slow, wastes resources)
✅ Right: pipeline builds → pushes to GHCR → server pulls
```

---

## Phase 3 — Networking 🌐

> **Goal:** Understand how traffic flows from the internet to your app and set up NGINX as a reverse proxy.

### What I Learned

- **SSH** — how to connect to remote servers securely using key pairs
- **SSH key setup** — generating keys, `authorized_keys`, `~/.ssh/config` shortcuts
- **Multipass** — running Ubuntu VMs locally to simulate a real VPS
- **Manual deployment** — git clone → docker build → docker run on a server
- **Reverse proxy** — what it is, why it exists, how it works
- **NGINX** — install, configure, enable sites, test config, reload
- **`sites-available` vs `sites-enabled`** — symlink pattern
- **NGINX in Docker** — running NGINX as a container in Docker Compose
- **NGINX config** — `proxy_pass`, headers, domain-based routing, path-based routing
- **Load balancing** — upstream blocks, round-robin
- **SSL/HTTPS** — Let's Encrypt + Certbot

### Notes

| File | Description |
|------|-------------|
| [reverse_proxy.md](./02-networking/reverse_proxy.md) | Complete NGINX reverse proxy guide with configs, SSL, load balancing |

### Key Concepts

**SSH key pair:**
```
Private key → stays on YOUR machine (never share!)
Public key  → goes on the SERVER (~/.ssh/authorized_keys)
```

**SSH config shortcut:**
```
# ~/.ssh/config
Host devops-vm
    HostName 192.168.252.11
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519

# Now just type:
ssh devops-vm
```

**NGINX as reverse proxy:**
```
User visits http://your-server-ip
        ↓
NGINX listens on port 80
        ↓
Forwards to localhost:3000 (or portfolio:3000 in Docker)
        ↓
App responds → NGINX sends back to user
```

**NGINX in Docker Compose:**
```yaml
# proxy_pass uses SERVICE NAME not localhost!
proxy_pass http://portfolio:3000;  # ✅ Docker Compose
proxy_pass http://localhost:3000;  # ✅ Bare metal NGINX
```

**Never build on the server — pull instead:**
```bash
# ✅ Correct production deployment
docker compose pull
docker compose up -d
docker image prune -f
```

---

## Phase 4 — Kubernetes ☸️

> **Goal:** Deploy and manage containerized apps at scale with self-healing and rolling updates.

### What I Learned (Concepts)

- **Why Kubernetes** — Docker Compose manages 1 server, Kubernetes manages many
- **Cluster** — the whole Kubernetes system
- **Node** — a server inside the cluster
- **Pod** — the smallest unit, wraps your container
- **Service** — routes traffic to the right pods
  - `ClusterIP` → internal only (backend ↔ database)
  - `NodePort` → external via port
  - `LoadBalancer` → external via cloud load balancer
- **Horizontal scaling** — more pods when traffic grows
- **Auto-scaling** — Kubernetes adds/removes pods automatically
- **Rolling updates** — update one pod at a time, zero downtime
- **Rollback** — revert to previous version instantly

### Still to Cover

- [ ] Deployment — manages pods, rolling updates, rollbacks
- [ ] `kubectl` — the CLI tool to talk to Kubernetes
- [ ] ConfigMaps & Secrets — inject config into pods
- [ ] Ingress — route external HTTP traffic
- [ ] Volumes — persistent storage
- [ ] Namespaces — isolate environments
- [ ] RBAC — role-based access control
- [ ] Deploy Atlas Edu to local cluster (Docker Desktop)
- [ ] Deploy to real cloud cluster (GKE/EKS)

### Learning Path

```
Docker Desktop K8s (local) → minikube → managed K8s (GKE/EKS)
```

---

## Phase 5 — Cloud Platform ☁️

> **Goal:** Deploy the full stack to a real cloud provider with IaC and observability.

### What I'll Learn

- [ ] Cloud provider fundamentals (GCP / AWS)
- [ ] Managed Kubernetes — GKE or EKS
- [ ] Infrastructure as Code — Terraform
- [ ] Observability — CloudWatch / Cloud Logging, Prometheus, Grafana
- [ ] Full end-to-end: CI/CD pipeline → Docker image → Kubernetes on cloud

---

## 🐧 Linux Fundamentals

> Linux knowledge required for DevOps work.

| File | Description |
|------|-------------|
| [Linux.md](./Linux.md) | Essential Linux commands and concepts for DevOps |

### Key Commands

```bash
# Package management
sudo apt update && sudo apt install <package>

# User & permissions
sudo usermod -aG docker $USER    # add user to group
newgrp docker                    # apply group change
chmod 700 ~/.ssh                 # secure SSH folder
chmod 600 ~/.ssh/authorized_keys # secure authorized keys

# Disk usage
df -h                            # check disk space
docker system prune -a -f        # free Docker space

# Networking
curl -LsSf https://example.com/install.sh | sh   # download and execute
curl -I http://localhost:3000                      # check if app is running
```

---

## 🛠️ Tools & Stack

| Category | Tool |
|----------|------|
| Containerization | Docker, Docker Compose |
| Reverse Proxy | NGINX |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Orchestration | Kubernetes (Docker Desktop → GKE) |
| IaC | Terraform |
| Cloud | GCP / AWS |
| Monitoring | Prometheus, Grafana, Sentry |
| Package Manager | Helm |
| VM (local practice) | Multipass (Ubuntu VM on macOS) |

---

## 💡 Key Takeaways

> Things I wish I knew before starting.

**1. Install from official sources, not distro repos**
Ubuntu's `docker.io` is outdated. Always use the official Docker installation from `docs.docker.com/engine/install/ubuntu`.

**2. Layer order matters more than you think**
Putting `COPY . .` before `npm install` forces a full reinstall on every code change. Always copy `package.json` first.

**3. `localhost` inside a container ≠ your machine**
Inside Docker, `localhost` = the container itself. Use container/service names for inter-container communication.

**4. `EXPOSE` doesn't actually expose anything**
It's documentation only. Real port mapping happens with `-p host:container` at runtime.

**5. `docker compose down -v` deletes your data**
Never run this in production. `-v` removes volumes — your database is gone.

**6. Never build images on the server**
CI/CD pipeline builds and pushes to GHCR. Server only pulls and runs.

**7. NGINX `proxy_pass` changes in Docker**
Bare metal: `proxy_pass http://localhost:3000` → Docker Compose: `proxy_pass http://service-name:3000`

**8. SSH vs HTTP are completely independent**
No SSH key = can't control the server. But users can still access your app via HTTP. They're separate doors.

**9. Port 3000 should never be public in production**
NGINX listens on 80/443. App port (3000) stays internal — only NGINX talks to it directly.

**10. `node dist/server.js` over `npm start` in production**
Direct `node` = proper signal handling. With `npm start`, Docker's `SIGTERM` can get lost.

---

## 📚 Resources

- [Docker Official Docs](https://docs.docker.com)
- [Docker Engine Install (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [NGINX Docs](https://nginx.org/en/docs/)
- [Certbot (Let's Encrypt)](https://certbot.eff.org/)
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [Terraform Docs](https://developer.hashicorp.com/terraform/docs)
- [Multipass Docs](https://multipass.run/docs)

---

## 👤 Author

**Mustafa Tawab** — Full Stack Engineer & AI-first Software Agency (Farsight Systems)

- 🌐 Portfolio: [mustafatawab.vercel.app](https://mustafatawab.vercel.app)
- 📧 Contact: mustafa.tawab.dev@gmail.com
- 🐙 GitHub: [@mustafatawab](https://github.com/mustafatawab)