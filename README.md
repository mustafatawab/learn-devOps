# 🚀 Learn DevOps

A hands-on DevOps learning journey - from Linux fundamentals to Kubernetes, CI/CD pipelines, and Cloud platforms. Every concept is learned by building real projects.


---

## 🗺️ Roadmap

```
01 → Linux Fundamentals   ✅ Complete
02 → Networking & NGINX   ✅ Complete
03 → Git & GitHub         ✅ Complete
04 → Containerization     ✅ Complete
05 → CI/CD Pipeline       ✅ Complete
06 → Kubernetes           🔄 In Progress
07 → Cloud Platform       ⬜ Upcoming
```

---

## 📂 Repository Structure

```
learn-devOps/
├── 01-linux/
│   └── Linux.md                     # Linux fundamentals, commands, permissions
├── 02-networking/
│   ├── reverse_proxy.md             # NGINX concepts, SSL, load balancing
│   └── nginx_setup.md               # Step-by-step NGINX setup guide
├── 03-git/
│   ├── README.md                    # Git learning path overview
│   ├── 3.1-git_basics.md            # What Git is, setup, daily workflow
│   ├── 3.2-git_branching.md         # Branches, merge, rebase, conflicts
│   ├── 3.3-github.md                # Remotes, PRs, Issues, team workflow
│   └── 3.4-git_advanced.md          # Undo/recover, stash, tags, pro habits
├── 04-containerization/
│   ├── docker_containerization.md   # Docker concepts, Dockerfile, multi-stage builds
│   └── docker_compose.md            # Docker Compose deep dive
├── 05-ci-cd/
│   ├── cicd_pipelines.md            # GitHub Actions CI/CD concepts
│   └── templates/                   # Ready-made pipeline templates
│       ├── nextjs/
│       ├── nextjs-node/
│       ├── nextjs-fastapi/
│       ├── fastapi/
│       └── laravel/
├── 06-kubernetes/                   # Kubernetes notes (in progress)
├── examples/                        # Practice applications
└── README.md
```

---

## 01 - Linux Fundamentals 🐧

> **Goal:** Get comfortable with Linux - the operating system every server runs on.

### What I Learned

- `apt` - Ubuntu's package manager (like `brew` on Mac)
- `sudo` - run commands as administrator
- Environment variables - `$USER`, `$HOME`, `$PATH`
- File permissions - `chmod`, `chown`
- `curl` + pipe (`|`) - download and execute scripts
- SSH setup - key pairs, `authorized_keys`, `~/.ssh/config`
- Process management - `ps`, `kill`, `systemctl`
- Disk usage - `df -h`, `du -sh`

### Notes

| File | Description |
|------|-------------|
| [Linux.md](./01-linux/Linux.md) | Essential Linux commands and concepts for DevOps |

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

# Download and execute
curl -LsSf https://example.com/install.sh | sh
```

---

## 02 - Networking & NGINX 🌐

> **Goal:** Understand how traffic flows from the internet to your app and set up NGINX as a reverse proxy.

### What I Learned

- **SSH** - connect to remote servers securely using key pairs
- **SSH config** - `~/.ssh/config` shortcuts for quick access
- **Multipass** - run Ubuntu VMs locally to simulate a real VPS
- **Reverse proxy** - what it is, why it exists, how it works
- **Forward proxy vs reverse proxy** - the key difference
- **NGINX** - install, configure, enable sites, test config, reload
- **`sites-available` vs `sites-enabled`** - symlink pattern
- **NGINX in Docker** - running NGINX as a container in Docker Compose
- **NGINX config** - `proxy_pass`, headers, domain-based vs path-based routing
- **Load balancing** - upstream blocks, round-robin
- **SSL/HTTPS** - Let's Encrypt + Certbot

### Notes

| File | Description |
|------|-------------|
| [reverse_proxy.md](./02-networking/reverse_proxy.md) | NGINX concepts, SSL, load balancing, troubleshooting |
| [nginx_setup.md](./02-networking/nginx_setup.md) | Step-by-step setup - bare metal and Docker Compose |

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

ssh devops-vm   # ← now just this!
```

**NGINX proxy_pass - bare metal vs Docker:**
```nginx
proxy_pass http://localhost:3000;   # ✅ bare metal NGINX
proxy_pass http://portfolio:3000;   # ✅ Docker Compose (service name!)
```

**Never build on the server - pull instead:**
```bash
docker compose pull
docker compose up -d
docker image prune -f
```

---

## 03 - Git & GitHub 🌿

> **Goal:** Master version control for safe collaboration and CI/CD that starts from Git events.

### What I Learned

- **Git basics** - init, add, commit, status, log
- **Branching** - create, switch, merge, rebase
- **GitHub** - remotes, push, pull, PRs, Issues
- **Conflict resolution** - merge conflicts and how to fix them
- **Advanced Git** - stash, tags, cherry-pick, reset, revert
- **Git workflow** - feature branch → PR → review → merge to main
- **Why Git matters for DevOps** - every CI/CD pipeline starts from a Git event

### Notes

| File | Description |
|------|-------------|
| [3.1-git_basics.md](./03-git/3.1-git_basics.md) | What Git is, setup, daily commit workflow |
| [3.2-git_branching.md](./03-git/3.2-git_branching.md) | Branches, merge, rebase, conflicts |
| [3.3-github.md](./03-git/3.3-github.md) | Remotes, PRs, Issues, team workflow |
| [3.4-git_advanced.md](./03-git/3.4-git_advanced.md) | Undo/recover, stash, tags, pro DevOps habits |

### Key Concepts

**Why Git matters in DevOps:**
```
Code change → Git commit → Push → GitHub
                              ↓
                     CI/CD pipeline triggers
                              ↓
                     Build → Test → Deploy
```

**Git mental model:**
| Concept | Simple meaning |
|---------|----------------|
| Commit | A saved snapshot of your project |
| Branch | A parallel line of work |
| Remote | A copy of the repo on GitHub |
| PR | Ask to merge your branch (with review) |

---

## 04 - Containerization 🐳

> **Goal:** Understand containerization deeply and write production-ready Dockerfiles.

### What I Learned

- **Docker architecture** - daemon, socket, images, containers, layers, Docker Hub
- **Image layer caching** - order Dockerfile instructions from least-changing to most-changing
- **Multi-stage builds** - separate build stage from production stage to minimize image size
- **Docker networks** - containers communicate using service/container names as hostnames
- **Docker volumes** - named volumes for persistence, bind mounts for dev hot-reload
- **Docker Compose** - orchestrate multi-container apps with a single `compose.yaml`
- **depends_on** - `service_started`, `service_healthy`, `service_completed_successfully`
- **Restart policies** - `no`, `always`, `unless-stopped`, `on-failure`

### Notes

| File | Description |
|------|-------------|
| [docker_containerization.md](./04-containerization/docker_containerization.md) | Docker concepts, Dockerfile reference, multi-stage builds, volumes, networks, commands |
| [docker_compose.md](./04-containerization/docker_compose.md) | Compose services, networks, volumes, depends_on, healthchecks, restart policies |

### Key Concepts

**Single-stage vs Multi-stage builds:**
```dockerfile
# ❌ Single stage - dev tools end up in production image (~900MB)
FROM node:22-alpine
RUN npm install        # includes TypeScript, nodemon, @types/*
RUN npm run build
CMD ["node", "dist/server.js"]

# ✅ Multi-stage - only compiled output in production (~180MB)
FROM node:22-alpine AS builder
RUN npm install
RUN npm run build

FROM node:22-alpine AS runner
COPY --from=builder /app/dist ./dist
RUN npm install --omit=dev
CMD ["node", "dist/server.js"]
```

**Layer caching strategy:**
```dockerfile
COPY package*.json ./    # ← copy this first (changes rarely)
RUN npm install          # ← cached unless package.json changes
COPY . .                 # ← copy code last (changes often)
```

**Container networking:**
```
DATABASE_URL=postgresql://user:pass@db:5432/mydb
#                                    ↑
#                              service name = hostname
```

---

## 05 - CI/CD Pipeline ⚙️

> **Goal:** Automate build → test → deploy on every push using GitHub Actions.

### What I Learned

- **GitHub Actions concepts** - workflows, jobs, steps, actions, triggers
- **`uses` vs `run`** - pre-built actions vs shell commands
- **`needs`** - job dependencies (sequential jobs)
- **`${{ }}`** - GitHub Actions expression syntax
- **Secrets** - store credentials safely, never hardcode
- **Caching** - `cache: "npm"` and Docker layer caching (`type=gha`)
- **Two-workflow pattern** - `ci.yml` for PRs, `cd.yml` for deployments
- **GHCR** - GitHub Container Registry for Docker images
- **Auto-formatting** - Prettier workflow that commits formatted code

### Notes

| File | Description |
|------|-------------|
| [cicd_pipelines.md](./05-ci-cd/cicd_pipelines.md) | Full CI/CD guide with concepts, triggers, secrets, caching |

### Templates

| Stack | CI | CD |
|-------|----|----|
| Next.js | [ci.yml](./05-ci-cd/templates/nextjs/ci.yml) | [cd.yml](./05-ci-cd/templates/nextjs/cd.yml) |
| Next.js + Node.js | [ci.yml](./05-ci-cd/templates/nextjs-node/ci.yml) | [cd.yml](./05-ci-cd/templates/nextjs-node/cd.yml) |
| Next.js + FastAPI | [ci.yml](./05-ci-cd/templates/nextjs-fastapi/ci.yml) | [cd.yml](./05-ci-cd/templates/nextjs-fastapi/cd.yml) |
| FastAPI | [ci.yml](./05-ci-cd/templates/fastapi/ci.yml) | [cd.yml](./05-ci-cd/templates/fastapi/cd.yml) |
| Laravel | [ci.yml](./05-ci-cd/templates/laravel/ci.yml) | [cd.yml](./05-ci-cd/templates/laravel/cd.yml) |

### Key Concepts

**Two-workflow pattern:**
```
PR opened  → ci.yml → test + build only
PR merged  → cd.yml → build image → push GHCR → deploy via SSH
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

## 06 - Kubernetes ☸️

> **Goal:** Deploy and manage containerized apps at scale with self-healing and rolling updates.

### What I Learned (Concepts)

- **Why Kubernetes** - Docker Compose manages 1 server, Kubernetes manages many
- **Cluster** - the whole Kubernetes system
- **Node** - a server inside the cluster
- **Pod** - the smallest unit, wraps your container
- **Service** - routes traffic to the right pods
  - `ClusterIP` → internal only (backend ↔ database)
  - `NodePort` → external via port
  - `LoadBalancer` → external via cloud load balancer
- **Horizontal scaling** - more pods when traffic grows
- **Auto-scaling** - Kubernetes adds/removes pods automatically
- **Rolling updates** - update one pod at a time, zero downtime
- **Rollback** - revert to previous version instantly

### Still to Cover

- [ ] Deployment - manages pods, rolling updates, rollbacks
- [ ] `kubectl` - the CLI tool to talk to Kubernetes
- [ ] ConfigMaps & Secrets - inject config into pods
- [ ] Ingress - route external HTTP traffic
- [ ] Volumes - persistent storage
- [ ] Namespaces - isolate environments
- [ ] RBAC - role-based access control
- [ ] Deploy Atlas Edu to local cluster (Docker Desktop)
- [ ] Deploy to real cloud cluster (GKE/EKS)

### Learning Path

```
Docker Desktop K8s (local) → minikube → managed K8s (GKE/EKS)
```

---

## 07 - Cloud Platform ☁️

> **Goal:** Deploy the full stack to a real cloud provider with IaC and observability.

### What I'll Learn

- [ ] Cloud provider fundamentals (GCP / AWS)
- [ ] Managed Kubernetes - GKE or EKS
- [ ] Infrastructure as Code - Terraform
- [ ] Observability - CloudWatch / Cloud Logging, Prometheus, Grafana, Sentry
- [ ] Full end-to-end: CI/CD pipeline → Docker image → Kubernetes on cloud

---

## 🛠️ Tools & Stack

| Category | Tool |
|----------|------|
| OS / Server | Linux (Ubuntu) |
| Version Control | Git, GitHub |
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
Never run this in production. `-v` removes volumes - your database is gone.

**6. Never build images on the server**
CI/CD pipeline builds and pushes to GHCR. Server only pulls and runs.

**7. NGINX `proxy_pass` changes in Docker**
Bare metal: `proxy_pass http://localhost:3000` → Docker Compose: `proxy_pass http://service-name:3000`

**8. SSH vs HTTP are completely independent**
No SSH key = can't control the server. But users can still access your app via HTTP. They're separate doors.

**9. Port 3000 should never be public in production**
NGINX listens on 80/443. App port (3000) stays internal - only NGINX talks to it directly.

**10. `node dist/server.js` over `npm start` in production**
Direct `node` = proper signal handling. With `npm start`, Docker's `SIGTERM` can get lost.

**11. Every CI/CD pipeline starts from a Git event**
`push`, `pull_request`, `tag` - mastering Git branching directly affects your deployment workflow.

**12. Test twice - once on PR, once after merge**
PR branch passes CI ≠ merged code passes CI. Always test the merged result too.

---

## 📚 Resources

- [Docker Official Docs](https://docs.docker.com)
- [Docker Engine Install (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [NGINX Docs](https://nginx.org/en/docs/)
- [Certbot (Let's Encrypt)](https://certbot.eff.org/)
- [Git Official Docs](https://git-scm.com/doc)
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [Terraform Docs](https://developer.hashicorp.com/terraform/docs)
- [Multipass Docs](https://multipass.run/docs)

---

## 👤 Author

**Mustafa Tawab** - Full Stack Engineer & AI-first Software Agency (Farsight Systems)

- 🌐 Portfolio: [mustafatawab.vercel.app](https://mustafatawab.vercel.app)
- 📧 Contact: mustafa.tawab.dev@gmail.com
- 🐙 GitHub: [@mustafatawab](https://github.com/mustafatawab)