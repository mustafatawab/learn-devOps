# 🚀 Learn DevOps

A hands-on DevOps learning journey — from Docker fundamentals to Kubernetes, CI/CD pipelines, and Cloud platforms. Every concept is learned by building real projects.


---

## 🗺️ Roadmap

```
Phase 1 → Docker          ✅ Complete
Phase 2 → CI/CD Pipeline  🔄 In Progress
Phase 3 → Kubernetes      ⬜ Upcoming
Phase 4 → Cloud Platform  ⬜ Upcoming
```

---

## 📂 Repository Structure

```
learn-devOps/
├── containerization/
│   ├── docker_containerization.md   # Docker concepts, Dockerfile, multi-stage builds
│   └── docker_compose.md            # Docker Compose deep dive
├── kubernetes/                      # Kubernetes notes (upcoming)
├── ci-cd/                           # GitHub Actions pipelines (upcoming)
├── cloud/                           # Cloud platform notes (upcoming)
├── app/                             # Practice application
├── fastapi-docker/                  # FastAPI + Docker example
└── Linux.md                         # Linux fundamentals
```

---

## Phase 1 — Docker 🐳

> **Goal:** Understand containerization deeply and write production-ready Dockerfiles.

### What I Learned

- **Linux fundamentals** for DevOps — `apt`, `sudo`, environment variables (`$USER`, `$HOME`, `$PATH`), `curl`, pipe (`|`)
- **Docker architecture** — daemon, socket, images, containers, layers, Docker Hub
- **Image layer caching** — order Dockerfile instructions from least-changing to most-changing
- **Multi-stage builds** — separate build stage from production stage to minimize image size
- **Docker networks** — containers communicate using service/container names as hostnames
- **Docker volumes** — named volumes for persistence, bind mounts for dev hot-reload
- **Docker Compose** — orchestrate multi-container apps with a single `compose.yaml`

### Notes

| File | Description |
|------|-------------|
| [docker_containerization.md](./containerization/docker_containerization.md) | Docker concepts, Dockerfile reference, multi-stage builds, volumes, networks, commands |
| [docker_compose.md](./containerization/docker_compose.md) | Compose services, networks, volumes, depends_on, healthchecks, restart policies |

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

### What I'll Learn

- [ ] GitHub Actions — workflows, jobs, steps, triggers
- [ ] Build & test stage — lint and unit tests on every PR
- [ ] Docker in CI — build and push images from the pipeline
- [ ] Environments & secrets — staging vs production gates
- [ ] End-to-end pipeline — push code → tests pass → image pushed to GHCR → deployed

### Planned Pipeline

```
Push to main
     ↓
Run tests (npm test)
     ↓
Build Docker image
     ↓
Push to GitHub Container Registry (GHCR)
     ↓
Deploy to staging
     ↓ (manual approval)
Deploy to production
```

---

## Phase 3 — Kubernetes ☸️

> **Goal:** Deploy and manage containerized apps at scale with self-healing and rolling updates.

### What I'll Learn

- [ ] Core objects — Pod, Deployment, Service, Namespace
- [ ] ConfigMaps & Secrets — inject config into pods
- [ ] Ingress & networking — route external traffic in
- [ ] Rolling deployments — zero-downtime updates + rollbacks
- [ ] Persistent storage — PersistentVolumes, PersistentVolumeClaims
- [ ] RBAC — role-based access control
- [ ] Observability — liveness/readiness probes, Prometheus, Grafana
- [ ] Helm — package manager for Kubernetes

### Learning Path

```
minikube (local) → kind → managed K8s (GKE/EKS)
```

---

## Phase 4 — Cloud Platform ☁️

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

# Environment variables
echo $USER    # current user
echo $HOME    # home directory
echo $PATH    # executable search paths

# Networking
curl -LsSf https://example.com/install.sh | sh   # download and execute script
```

---

## 🛠️ Tools & Stack

| Category | Tool |
|----------|------|
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Orchestration | Kubernetes (minikube → GKE) |
| IaC | Terraform |
| Cloud | GCP / AWS |
| Monitoring | Prometheus, Grafana |
| Package Manager | Helm |
| VM (local practice) | Multipass (Ubuntu VM on macOS) |

---

## 💡 Key Takeaways

> Things I wish I knew before starting.

**1. Install from official sources, not distro repos**
Ubuntu's `docker.io` and `podman-docker` are outdated. Always use the official Docker installation method from `docs.docker.com/engine/install/ubuntu`.

**2. Layer order matters more than you think**
Putting `COPY . .` before `npm install` forces a full reinstall on every code change. Always copy `package.json` first.

**3. `localhost` inside a container ≠ your machine**
Inside a Docker container, `localhost` refers to the container itself — not your host machine. Use container/service names for inter-container communication.

**4. `EXPOSE` doesn't actually expose anything**
It's documentation only. Real port mapping happens with `-p host:container` at runtime.

**5. `docker compose down -v` deletes your data**
Never run this in production. `-v` removes volumes — your database is gone.

**6. `node dist/server.js` over `npm start` in production**
Direct `node` means proper signal handling — Docker's `SIGTERM` reaches your app. With `npm start`, signals can get lost in the npm process.

---

## 📚 Resources

- [Docker Official Docs](https://docs.docker.com)
- [Docker Engine Install (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [Terraform Docs](https://developer.hashicorp.com/terraform/docs)

---

## 👤 Author

**Mustafa Tawab** — Full Stack Engineer & AI-first Software Agency (Farsight Systems)

- 🌐 Portfolio: [mustafatawab.vercel.app](https://mustafatawab.vercel.app)
- 📧 Contact: mustafa.tawab.dev@gmail.com
- 🐙 GitHub: [@mustafatawab](https://github.com/mustafatawab)