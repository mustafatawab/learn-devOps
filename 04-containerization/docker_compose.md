# 🐙 Docker Compose

A complete guide to Docker Compose - defining and running multi-container applications.

---

## Table of Contents

1. [What is Docker Compose?](#what-is-docker-compose)
2. [Why Docker Compose?](#why-docker-compose)
3. [compose.yaml Structure](#composeyaml-structure)
4. [Services](#services)
5. [Networks](#networks)
6. [Volumes](#volumes)
7. [Environment Variables](#environment-variables)
8. [depends_on & Health Checks](#depends_on--health-checks)
9. [Restart Policies](#restart-policies)
10. [Running Multiple Commands](#running-multiple-commands)
11. [Essential Commands](#essential-commands)
12. [Real-World Example](#real-world-example)

---

## What is Docker Compose?

Docker Compose is a tool for defining and running **multi-container** Docker applications using a single `compose.yaml` file.

Instead of running multiple `docker run` commands manually:

```bash
# Without Compose - painful 😩
docker network create app-network
docker run -d --name postgres --network app-network ...
docker run -d --name backend --network app-network ...
docker run -d --name frontend --network app-network ...
```

With Compose - one command does it all:

```bash
# With Compose - simple 🚀
docker compose up -d
```

---

## Why Docker Compose?

| Problem | Compose Solution |
|---|---|
| Managing multiple `docker run` commands | One `compose.yaml` file |
| Manually creating networks | Auto-creates shared network |
| Remembering all flags | Defined once in YAML |
| Container startup order | `depends_on` |
| Environment variables | `env_file` + `environment` |
| Persistent data | `volumes` |

---

## compose.yaml Structure

```yaml
name: my-app              # project name (prefixes container names)

services:                 # define your containers here
  service-name:
    # ... service config

networks:                 # define custom networks
  network-name:
    driver: bridge

volumes:                  # define named volumes
  volume-name:
```

---

## Services

Each service = one container. Here are all the key options:

### build

Build an image from a Dockerfile:

```yaml
services:
  backend:
    build:
      context: "./backend-nodejs"    # path to build context
      dockerfile: Dockerfile          # Dockerfile name (default: Dockerfile)
```

Or use a pre-built image:

```yaml
services:
  backend:
    image: taskflow-backend:latest
```

Or build AND name the image (so other services can reuse it):

```yaml
services:
  backend:
    build:
      context: "./backend-nodejs"
      dockerfile: Dockerfile
    image: taskflow-backend:latest   # tags the built image
```

### ports

Map host ports to container ports (`host:container`):

```yaml
ports:
  - "9000:9000"    # host 9000 → container 9000
  - "5433:5432"    # host 5433 → container 5432 (avoid conflicts)
```

### volumes

**Bind mount** - sync local files to container (dev mode):

```yaml
volumes:
  - ./backend-nodejs:/app          # mount local folder → /app
  - /app/node_modules              # protect container's node_modules
```

> The second line (`/app/node_modules`) is an **anonymous volume** that prevents your host's `node_modules` from overwriting the container's. This matters because packages with native bindings (like `bcrypt`) compile differently on macOS vs Linux.

**Named volume** - persistent storage managed by Docker:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

### networks

Connect a service to a network:

```yaml
networks:
  - app-network
```

### container_name

Give the container a custom name:

```yaml
container_name: taskflow_db
```

> If not set, Compose auto-names it as `<project>-<service>-<number>` e.g. `taskflow-backend-1`

---

## Networks

All services in a `compose.yaml` can talk to each other using their **service name as hostname** - as long as they're on the same network.

```yaml
# backend can reach db at "db:5432"
# frontend can reach backend at "backend:9000"

services:
  backend:
    networks:
      - app-network
    environment:
      - DATABASE_URL=postgresql://postgres:1234@db:5432/mydb
                                               ↑
                                          service name = hostname

  db:
    networks:
      - app-network

networks:
  app-network:
    driver: bridge    # default driver for single-host networking
```

### Network Drivers

| Driver | Use Case |
|---|---|
| `bridge` | Default. Isolated network on a single host |
| `host` | Container shares host's network stack |
| `none` | No networking |

---

## Volumes

### Named Volumes (Persistent Data)

Defined at the top level and referenced in services:

```yaml
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:    # Docker manages this volume
```

Data survives `docker compose down` but is deleted with `docker compose down -v`.

> ⚠️ **Never run `docker compose down -v` in production** - it permanently deletes all volume data (your database!).

---

## Environment Variables

There are two ways to pass env vars - and they can be used together:

### `env_file` - load from a file

```yaml
env_file:
  - ./backend-nodejs/.env
```

Loads all variables from the `.env` file.

### `environment` - inline hardcoded values

```yaml
environment:
  - DATABASE_URL=postgresql://postgres:1234@db:5432/mydb
  - DIRECT_URL=postgresql://postgres:1234@db:5432/mydb
```

### Which one wins?

**`environment` (inline) always overrides `env_file`.**

This is intentional - use `env_file` for most variables (like JWT secrets, email credentials) and `environment` to override specific ones (like `DATABASE_URL` to point to the local `db` container instead of NeonDB).

```yaml
env_file:
  - ./backend/.env                     # loads DATABASE_URL=neon-cloud-url
environment:
  - DATABASE_URL=postgresql://db:5432  # overrides with local container URL ✅
```

---

## depends_on & Health Checks

Control the **startup order** of services.

### Three Conditions

```yaml
depends_on:
  db:
    condition: service_started          # 1. container is running (don't care if ready)
    condition: service_healthy          # 2. container passed its healthcheck
    condition: service_completed_successfully  # 3. one-off task finished without error
```

### When to Use Each

| Condition | Use When |
|---|---|
| `service_started` | Service doesn't need the dependency to be fully ready at startup |
| `service_healthy` | Service connects to dependency immediately on startup (e.g. DB) |
| `service_completed_successfully` | Waiting for a one-time task like migrations |

**Real example:**

```yaml
db:
  image: postgres:16-alpine
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]  # checks if Postgres accepts connections
    interval: 10s       # check every 10 seconds
    timeout: 5s         # fail if no response in 5s
    retries: 5          # retry 5 times before marking unhealthy
    start_period: 10s   # grace period before first check

backend:
  depends_on:
    db:
      condition: service_healthy  # wait until Postgres is truly ready
  # Without this, backend starts before Postgres accepts connections → crash!

frontend:
  depends_on:
    backend:
      condition: service_started  # Next.js doesn't connect to backend at startup
  # Frontend only calls backend when a USER makes a request in the browser
```

### Migration Service Pattern

Run migrations before the backend starts:

```yaml
migrate:
  image: taskflow-backend:latest      # reuse the backend image
  command: npx prisma migrate deploy  # but run a different command
  depends_on:
    db:
      condition: service_healthy
  restart: on-failure:3               # retry up to 3 times

backend:
  image: taskflow-backend:latest
  depends_on:
    migrate:
      condition: service_completed_successfully  # wait for migrations ✅
    db:
      condition: service_healthy
```

---

## Restart Policies

Controls what happens when a container stops:

```yaml
restart: "no"              # never restart (default)
restart: always            # always restart - even if YOU stopped it manually
restart: unless-stopped    # restart on crash, but respect manual stops ✅
restart: on-failure        # only restart on error exit code
restart: on-failure:3      # retry max 3 times then give up
```

### Analogy

Think of it like an employee:
- `always` → comes back to work even when you told them to go home 😅
- `unless-stopped` → comes back if they fainted, but goes home when you tell them to ✅
- `on-failure` → only comes back if something went wrong, not if they chose to leave

### Recommended

```yaml
# For long-running services (API, frontend, DB)
restart: unless-stopped

# For one-off tasks (migrations, seeds)
restart: on-failure:3
```

---

## Running Multiple Commands

`command` only accepts **one** value. Use `sh -c` to chain multiple:

```bash
# && = run second ONLY if first succeeded
command: sh -c "npx prisma migrate deploy && node dist/server.js"

# ; = always run both (regardless of success/failure)
command: sh -c "cleanup.sh ; node dist/server.js"

# || = run second ONLY if first FAILED
command: sh -c "try-primary || fallback"
```

**Practical example** - migrate then start:

```yaml
backend:
  command: sh -c "npx prisma migrate deploy && node dist/server.js"
```

---

## Essential Commands

### Starting & Stopping

```bash
docker compose up                  # start all services (foreground)
docker compose up -d               # start in background (detached)
docker compose up -d --build       # rebuild images then start
docker compose down                # stop and remove containers + networks
docker compose down -v             # also delete volumes (⚠️ data loss!)
docker compose stop                # stop containers (don't remove)
docker compose start               # start stopped containers
docker compose restart <service>   # restart a specific service
```

### Building

```bash
docker compose build               # build all service images
docker compose build <service>     # rebuild a specific service
docker compose up -d --build       # rebuild + start in one command
```

### Inspecting

```bash
docker compose ps                  # list service status
docker compose logs                # view all service logs
docker compose logs -f             # follow all logs live
docker compose logs -f <service>   # follow specific service logs
docker compose config              # validate and view resolved compose file
```

### Executing

```bash
docker compose exec <service> sh              # shell into a running service
docker compose exec backend npx prisma studio # run a command in a service
```

### When to use `--build`

```bash
docker compose up -d           # use existing cached images (no rebuild)
docker compose up -d --build   # force rebuild - use when you changed code
```

---

## Real-World Example

Full `compose.yaml` for a Next.js + Express + PostgreSQL app:

```yaml
name: taskflow

services:

  # ── Database ──────────────────────────────────────
  db:
    image: postgres:16-alpine
    container_name: taskflow_db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=1234
      - POSTGRES_DB=taskflow
    ports:
      - "5433:5432"           # use 5433 on host to avoid conflicts
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app-network

  # ── Migrations (one-off task) ─────────────────────
  migrate:
    image: taskflow-backend:latest
    command: npx prisma migrate deploy
    depends_on:
      db:
        condition: service_healthy
    restart: on-failure:3
    networks:
      - app-network

  # ── Backend API ───────────────────────────────────
  backend:
    build:
      context: "./backend-nodejs"
      dockerfile: Dockerfile
    image: taskflow-backend:latest
    restart: unless-stopped
    ports:
      - "9000:9000"
    volumes:
      - ./backend-nodejs:/app
      - /app/node_modules
    env_file:
      - ./backend-nodejs/.env
    environment:
      # Override DATABASE_URL to point to local db container
      - DATABASE_URL=postgresql://postgres:1234@db:5432/taskflow
      - DIRECT_URL=postgresql://postgres:1234@db:5432/taskflow
    depends_on:
      migrate:
        condition: service_completed_successfully
      db:
        condition: service_healthy
    networks:
      - app-network

  # ── Frontend ──────────────────────────────────────
  frontend:
    build:
      context: "./frontend"
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    env_file:
      - ./frontend/.env
    environment:
      - API_URL=http://backend:9000   # reach backend by service name
    depends_on:
      backend:
        condition: service_started    # frontend doesn't connect at startup
    networks:
      - app-network

# ── Networks ─────────────────────────────────────────
networks:
  app-network:
    driver: bridge

# ── Volumes ──────────────────────────────────────────
volumes:
  postgres_data:    # persists DB data across container restarts
```

### Startup Order

```
db starts
  ↓ (healthcheck passes)
migrate runs → completes ✅
  ↓
backend starts
  ↓ (service_started)
frontend starts
```

---

## Quick Reference

### Commands Cheat Sheet

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start all services in background |
| `docker compose up -d --build` | Rebuild images and start |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | ⚠️ Also delete volumes |
| `docker compose ps` | List service status |
| `docker compose logs -f` | Follow all logs |
| `docker compose logs -f <svc>` | Follow specific service logs |
| `docker compose exec <svc> sh` | Shell into service |
| `docker compose build <svc>` | Rebuild specific service |
| `docker compose restart <svc>` | Restart specific service |
| `docker compose config` | Validate compose file |
| `docker compose stop` | Stop without removing |
| `docker compose start` | Start stopped services |

### Restart Policy Cheat Sheet

| Policy | Restarts on crash | Restarts if manually stopped | Restarts after reboot |
|---|---|---|---|
| `no` | ❌ | ❌ | ❌ |
| `always` | ✅ | ✅ | ✅ |
| `unless-stopped` | ✅ | ❌ | ✅ |
| `on-failure` | ✅ | ❌ | ❌ |

### depends_on Conditions Cheat Sheet

| Condition | Meaning | Use For |
|---|---|---|
| `service_started` | Container is running | Frontend waiting for backend |
| `service_healthy` | Healthcheck passes | Backend waiting for DB |
| `service_completed_successfully` | One-off task finished | App waiting for migrations |