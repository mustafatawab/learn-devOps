# 🐳 Docker & Containerization

A complete guide to understanding Docker from scratch - concepts, commands, and best practices.

---

## Table of Contents

1. [What is Docker?](#what-is-docker)
2. [Core Concepts](#core-concepts)
3. [Docker Architecture](#docker-architecture)
4. [Installation & Setup](#installation--setup)
5. [Images](#images)
6. [Containers](#containers)
7. [Dockerfile](#dockerfile)
8. [Multi-Stage Builds](#multi-stage-builds)
9. [Volumes](#volumes)
10. [Networks](#networks)
11. [Essential Commands](#essential-commands)
12. [Dev Containers](#dev-containers)

---

## What is Docker?

Docker is a platform for developing, shipping, and running applications inside **containers**. A container packages your application with all its dependencies - ensuring it runs the same way on every machine.

> Think of it like a shipping container - the content is always the same no matter which ship carries it.

### The Problem Docker Solves

Without Docker:
- "It works on my machine" - but breaks in production
- Setting up environments manually is error-prone
- Different OS, different dependency versions = chaos

With Docker:
- Same container runs on your Mac, your teammate's Windows, and production Linux
- One command to spin up the entire stack
- Isolated, reproducible environments every time

---

## Core Concepts

### Image vs Container

```
Image     = Blueprint / Class
Container = Running instance of that image / Object
```

Just like OOP - one class, many instances. One image, many containers.

### Docker Hub

Docker Hub (`hub.docker.com`) is the public registry where images are stored and shared - think of it like **npm registry but for Docker images**.

### Image Layers

Every image is made up of **layers** - each layer represents one instruction in the Dockerfile:

```
Layer 1 → Base OS (Alpine/Ubuntu)      ← rarely changes
Layer 2 → Install Node.js              ← rarely changes
Layer 3 → Install dependencies         ← changes sometimes
Layer 4 → Copy app code                ← changes most often
```

Docker **caches every layer**. When you rebuild:
- Unchanged layers → ✅ pulled from cache (fast)
- Changed layer + everything below it → ❌ rebuilt

> **Key insight:** Order your Dockerfile instructions from least-changing to most-changing for maximum cache efficiency.

---

## Docker Architecture

```
Your Machine (Host)
├── Docker Daemon (background process)
│     └── /var/run/docker.sock  ← the "door" to the daemon
├── Docker CLI  ← you talk to this
└── Containers  ← isolated processes
```

### Why `sudo` is needed by default

The Docker daemon socket (`/var/run/docker.sock`) is only accessible by `root` for security. Any user with Docker access can:
- Stop/delete any container
- Mount sensitive system files
- Escalate to root privileges

### Fix: Add user to Docker group

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group change without logging out
newgrp docker

# Verify
docker images  # should work without sudo now
```

---

## Installation & Setup

### On Ubuntu (Official Method)

Always install from Docker's **official source** https://docs.docker.com/engine/install/ubuntu/ - not `docker.io` or `podman-docker` from Ubuntu's repo (they're outdated).

```bash
# 1. Update and install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# 2. Add Docker's GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 3. Add Docker's repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 5. Remove need for sudo
sudo usermod -aG docker $USER
newgrp docker
```

---

## Images

### Pulling Images

```bash
# Docker checks local cache first, then Docker Hub
docker pull hello-world
docker pull node:22-alpine
docker pull postgres:16-alpine
```

### Image Tags

```
image-name:tag
     ↑       ↑
  hello-world  latest (default if not specified)
  node         22-alpine
  postgres     16-alpine
```

`alpine` = a minimal Linux distribution (~5MB vs Ubuntu's ~80MB). Same app, much lighter OS.

```
node:22          → ~900MB  (full Debian + Node)
node:22-alpine   → ~130MB  (tiny Alpine + Node)
```

### Listing & Managing Images

```bash
docker images                  # list all local images
docker image ls                # same as above
docker inspect <image-name>    # detailed metadata (layers, env vars, etc.)
docker rmi <image-name>        # remove an image
docker image prune -a          # remove all unused images
docker image tag frontend:test frontend:v2  # tag/rename an image

# Remove unused images
docker image prune -a -f
```

---

## Containers

### Running Containers

```bash
# Basic run
docker run <image-name>

# Run in background (detached)
docker run -d <image-name>

# Run with a custom name
docker run --name my-container -d <image-name>

# Run with port mapping (host:container)
docker run -d -p 9000:9000 <image-name>

# Run with environment file
docker run -d -p 4000:4000 --env-file ./backend/.env <image-name>:<tag>

# Run with inline environment variables
docker run -d -e DATABASE_URL=postgresql://... <image-name>

# Run with volume mount (dev mode - live code updates)
docker run -p 4000:4000 \
  -v $(pwd):/app \          # mount local folder into container
  -v /app/node_modules \    # protect container's node_modules
  --env-file .env \
  <image-name>:<tag>

# Run and connect to a network
docker run -d \
  --name my-postgres \
  --network my-network \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Run interactively (get a terminal)
docker run -it <image-name> /bin/sh

# Run and auto-remove on exit
docker run --rm <image-name>
```

> **`$(pwd)`** = present working directory. A Linux variable that expands to your current path.

> **`-v $(pwd):/app -v /app/node_modules`** - mounts your local code BUT protects the container's `node_modules`. Since `node_modules` built on macOS may differ from Linux (native packages like `bcrypt`), the container keeps its own.

### Managing Containers

```bash
docker ps                    # list running containers
docker ps -a                 # list ALL containers (including stopped)
docker stop <name>           # gracefully stop a container
docker start <name>          # start a stopped container
docker restart <name>        # restart a container
docker kill <name>           # force stop a container
docker rm <name>             # remove a stopped container
docker rm -f <name>          # force remove a running container
docker logs <name>           # view container logs
docker logs -f <name>        # follow logs in real-time
docker inspect <name>        # detailed container info (IP, mounts, state)

# Remove everything unused at once (nuclear option)
docker system prune -a -f

# Remove stopped containers
docker container prune -f
```

### Executing Commands Inside Containers

```bash
# Get interactive terminal inside container
docker exec -it <container-name> sh       # Alpine (sh)
docker exec -it <container-name> bash     # Ubuntu (bash)

# Get terminal as root
docker exec -it -u root <container-name> sh

# Run one-off commands
docker exec <container-name> npx prisma migrate deploy
docker exec <container-name> npx prisma db push --force-reset
docker exec <container-name> npx prisma db seed

# Run as root (useful for debugging)
docker exec -it -u root <container> sh
```

> `docker exec` is like SSH-ing into a server - but it's a container.

### Neworks & Volumes
```
# Networks

docker network create <name>
docker network ls
docker network inspect <name>
docker network rm <name>
docker network connect <network> <container>


# Volumes - dedicated, persistent storage space managed entirely by the Docker daemon

docker volume create <name>
docker volume ls
docker volume inspect <name>
docker volume rm <name>
docker volume prune        ← delete all unused volumes

```

---

## Dockerfile

A `Dockerfile` is a set of instructions to build a Docker image.

### Dockerfile Instructions

| Instruction | Description |
|-------------|-------------|
| `FROM <image>` | Base image to build upon |
| `LABEL <key>=<value>` | Metadata (maintainer, version, description) |
| `WORKDIR <path>` | Set working directory (like `mkdir -p /app && cd /app`) |
| `COPY <src> <dest>` | Copy files from host to container |
| `ADD <src> <dest>` | Like COPY, but also extracts tarballs and supports URLs |
| `RUN <command>` | Execute command during build (creates a new layer) |
| `EXPOSE <port>` | Document which port the app listens on (metadata only!) |
| `ENV <key>=<value>` | Set environment variables |
| `CMD [...]` | Default command when container starts (can be overridden) |
| `ENTRYPOINT [...]` | Main executable (CMD provides default args to this) |
| `VOLUME <path>` | Create a mount point |
| `ARG <name>` | Build-time variable |
| `USER <user>` | Switch to non-root user |

### Key Notes

**`EXPOSE` is just documentation** - it does NOT actually open ports. Ports are opened with the `-p` flag at runtime:
```bash
docker run -p 3000:3000 my-app  # host:container
```

**`CMD` vs `ENTRYPOINT`:**
```dockerfile
ENTRYPOINT ["node"]        # always runs node
CMD ["dist/server.js"]     # default arg - can be overridden
```

### Example: Node.js/Express Dockerfile (Single Stage)

```dockerfile
FROM node:22-alpine

LABEL maintainer="mustafatawab"
LABEL version="1.0"
LABEL description="Atlas Edu API"

WORKDIR /app

# Copy package files FIRST (layer caching optimization)
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

EXPOSE 3000

# node directly = faster startup + proper signal handling
CMD ["node", "dist/server.js"]
```

### Layer Caching Strategy

```dockerfile
# ✅ CORRECT - copy package.json first, then code
COPY package*.json ./   → layer 3 (changes rarely)
RUN npm install         → layer 4 (changes rarely, cached!)
COPY . .                → layer 5 (changes often)

# ❌ WRONG - copying everything forces npm install every time
COPY . .                → layer 3 (changes often - cache busted!)
RUN npm install         → layer 4 (forced to re-run every time)
```

**Why?** Docker invalidates a layer and all layers below it when any file involved changes. Since your app code changes often but `package.json` changes rarely - separate them!

---

## Multi-Stage Builds

### The Problem with Single-Stage Builds

A single-stage build puts everything in the final image:
- TypeScript compiler
- Dev dependencies (`nodemon`, `@types/*`, `ts-node`)
- `.ts` source files
- Everything in `node_modules` including dev deps

This results in a bloated, insecure image. You need dev tools to **build**, but not to **run**.

> Like cooking - you use pots, pans, and prep tools to make a dish, but you don't serve the meal with all the dirty dishes on the plate.

### The Solution: Multi-Stage Builds

```dockerfile
# ── Stage 1: Builder ──────────────────────────────────────
FROM node:22-alpine AS builder

LABEL maintainer="mustafatawab"
LABEL version="1.0"
LABEL description="Atlas Edu API"

WORKDIR /app

# Copy package files
COPY package*.json ./

# Copy prisma schema (needed for prisma generate)
COPY prisma ./prisma

# Install ALL dependencies (including dev deps for build)
RUN npm install

# Generate Prisma client (reads schema.prisma - no DB needed!)
RUN npx prisma generate

# Copy source code
COPY . .

# Compile TypeScript → dist/
RUN npm run build

# ── Stage 2: Production Runner ────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

# Copy only what's needed to RUN the app
COPY package*.json ./

# Install ONLY production dependencies
RUN npm install --omit=dev

# Copy compiled JavaScript from builder
COPY --from=builder /app/dist ./dist

# Copy prisma schema and generated client
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/src/generated ./src/generated

EXPOSE 4000

# Run node directly - no npm overhead, proper signal handling
CMD ["node", "dist/server.js"]
```

### Why Each Decision

| Decision | Reason |
|---|---|
| `AS builder` | Names the stage so we can reference it later |
| `npm install` in Stage 1 | Need TypeScript + all dev deps to compile |
| `npx prisma generate` before build | Generates TS types - needed for `tsc` to compile |
| `npm install --omit=dev` in Stage 2 | Production only - no TypeScript, no nodemon |
| `COPY --from=builder` | Cherry-pick only what we need from Stage 1 |
| `node dist/server.js` not `npm start` | Direct node = no extra process, proper signal handling |

### What Gets Left Behind (in Stage 1 only)

```
❌ TypeScript compiler
❌ nodemon, tsx, ts-node
❌ @types/* packages
❌ .ts source files
❌ tsconfig.json
❌ Dev node_modules
```

### Result

```
Single-stage image  → ~900MB
Multi-stage image   → ~180MB
```

---

## Volumes

Volumes provide **persistent storage** for containers. Without volumes, all data is lost when a container is removed.

### Types of Volumes

**Named Volume** - managed by Docker, stored in Docker's area:
```bash
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres
```

**Bind Mount** - maps a host path to a container path:
```bash
docker run -v $(pwd):/app my-app   # your local folder → /app in container
```

**Anonymous Volume** - no name, protects a specific path from being overwritten:
```bash
docker run -v /app/node_modules my-app   # protects node_modules
```

### Volume Commands

```bash
docker volume create <name>       # create a named volume
docker volume ls                  # list all volumes
docker volume inspect <name>      # detailed info
docker volume rm <name>           # remove a volume
docker volume prune               # delete all unused volumes
```

> ⚠️ `docker volume prune` and `docker compose down -v` delete data permanently - use with caution in production!

---

## Networks

By default, containers are **isolated** - they can't talk to each other. Docker Networks put containers in the same "room" so they can communicate.

### Why Networks Matter

```
Without network:
  backend → "postgres:5432" ❌ who?

With shared network:
  backend → "postgres:5432" ✅ found by container name!
```

Container names become **hostnames** on a shared network. So `DATABASE_URL` changes from:
```
postgresql://user:pass@localhost:5432/db     ← ❌ localhost = this container only
postgresql://user:pass@postgres:5432/db      ← ✅ postgres = container name on network
```

### Network Commands

```bash
docker network create <name>                   # create a network
docker network ls                              # list all networks
docker network inspect <name>                  # detailed info
docker network rm <name>                       # remove a network
docker network connect <network> <container>   # connect container to network
```

### Connecting Containers to a Network

```bash
# Create network
docker network create app-network

# Run postgres on the network
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  postgres:16-alpine

# Run backend on the same network
docker run -d \
  --name backend \
  --network app-network \
  -p 9000:9000 \
  taskflow-backend:latest
```

### Network Drivers

| Driver | Use case |
|---|---|
| `bridge` | Default. Isolated network on single host |
| `host` | Container shares host's network (no isolation) |
| `none` | No networking |

---

## Essential Commands

### Images

```bash
docker build -t <name>:<tag> .                    # build from Dockerfile in current dir
docker build -t <name>:<tag> -f <dockerfile> .    # build from specific Dockerfile
docker pull <image>:<tag>                          # download image
docker images                                      # list local images
docker image ls                                    # same
docker rmi <image>                                 # remove image
docker image prune -a                              # remove all unused images
docker inspect <image>                             # view metadata
docker image tag <old> <new>                       # tag/rename image
docker commit <container> <new-image>              # create image from container state
```

### Containers

```bash
docker run -d -p <host>:<container> --name <name> <image>   # run container
docker run -it <image> sh                                    # interactive terminal
docker run --rm <image>                                      # auto-remove on exit
docker ps                                                    # running containers
docker ps -a                                                 # all containers
docker stop <name>                                           # graceful stop
docker start <name>                                          # start stopped container
docker restart <name>                                        # restart
docker kill <name>                                           # force stop
docker rm <name>                                             # remove stopped container
docker rm -f <name>                                          # force remove running
docker logs <name>                                           # view logs
docker logs -f <name>                                        # follow logs live
docker inspect <name>                                        # container details
docker exec -it <name> sh                                    # shell into container
docker exec -it -u root <name> sh                           # shell as root
docker exec <name> <command>                                 # run one-off command
```

### Networks

```bash
docker network create <name>
docker network ls
docker network inspect <name>
docker network rm <name>
docker network connect <network> <container>
```

### Volumes

```bash
docker volume create <name>
docker volume ls
docker volume inspect <name>
docker volume rm <name>
docker volume prune
```

---

## Dev Containers

A **Dev Container** is a Docker container used as a full development environment - your code, tools, extensions, and runtime all inside a container.

### Why Dev Containers?

- Every team member has the **identical** development environment
- No "works on my machine" issues
- New developers onboard in minutes - just open the container
- Keeps your host machine clean - no global installs

### How It Works

VS Code and other editors can detect a `.devcontainer/devcontainer.json` file and open your project **inside a container**:

```
.devcontainer/
  ├── devcontainer.json    ← configuration
  └── Dockerfile           ← (optional) custom image
```

### Example `devcontainer.json`

```json
{
  "name": "mustafatawab's working space",
  "image": "node:22-alpine",
  "workspaceFolder": "/workspace",
  "forwardPorts": [3000, 9000],
  "postCreateCommand": "npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "prisma.prisma"
      ]
    }
  }
}
```

### Dev Container vs Production Container

| | Dev Container | Production Container |
|---|---|---|
| Purpose | Development environment | Running the app |
| Contains | All tools, extensions, source code | Only compiled output |
| Volume mount | Yes (live code editing) | No |
| Hot reload | Yes | No |
| Size | Larger | As small as possible |

---

## Quick Reference

### Common Port Mappings

| Service | Port |
|---------|------|
| Express/Node | `3000` or `4000` |
| FastAPI | `8000` |
| PostgreSQL | `5432` |
| Redis | `6379` |
| MongoDB | `27017` |
| Nginx | `80` / `443` |

### Image Size Comparison

| Base Image | Size |
|---|---|
| `ubuntu:latest` | ~80MB |
| `node:22` | ~900MB |
| `node:22-alpine` | ~130MB |
| `python:3.11` | ~900MB |
| `python:3.11-slim` | ~150MB |
| `alpine:latest` | ~5MB |

> Always prefer `-alpine` or `-slim` variants for production images.