# Docker

Docker is a platform for developing, shipping, and running applications in containers. Containers package software with all its dependencies, ensuring consistent behavior across environments.

---

## Docker Basics

### Check Docker Version
```bash
docker --version
```
Displays the installed Docker version.

### Pull an Image
```bash
docker pull <image-name>
```
Downloads an image from a registry (e.g., Docker Hub).

**Example:**
```bash
docker pull hello-world
docker pull nginx:alpine
docker pull python:3.11-slim
```

### List Docker Images
```bash
docker images
docker image ls
```
Shows all images stored locally.

---

## Container Management

### List Running Containers
```bash
docker ps
docker container ls
```
Shows only currently running containers.

### List All Containers (Including Stopped)
```bash
docker ps -a
docker container ls -a
```
Shows all containers regardless of state.

### Run a Container
```bash
docker run -d -p 8000:8000 --name my-container <image-name>:<tag>
```

**Options explained:**
| Flag | Description |
|------|-------------|
| `-d` | Detached mode (runs in background) |
| `-p 8000:8000` | Port mapping: `<host-port>:<container-port>` |
| `--name my-container` | Assigns a name to the container |

**Examples:**
```bash
# Run in background with port mapping
docker run -d -p 8000:8000 my-dev-image

# Run interactively (opens terminal in container)
docker run -it -p 8000:8000 <image-name>:<tag> /bin/bash

# Run with automatic cleanup (removed on exit)
docker run --rm -it <image-name> /bin/bash
```

### Execute Command in Running Container
```bash
docker exec -it <container-name> /bin/bash
docker exec -it <container-name> /bin/sh
```
Opens an interactive shell session inside a running container.

### View Container Logs
```bash
docker logs <container-name>
```
Displays stdout/stderr logs from the container.

### Follow Logs (Real-time)
```bash
docker logs -f <container-name>
```
Streams logs in real-time (follow mode).

### Stop a Container
```bash
docker stop <container-name>
```
Gracefully stops a running container.

### Start a Stopped Container
```bash
docker start <container-name>
```
Starts a previously stopped container.

### Remove a Container
```bash
docker rm <container-name>
docker rm <container-id>
```
Deletes a stopped container.

### Remove a Running Container
```bash
docker rm -f <container-name>
```
Forcefully removes a running container.

---

## Image Management

### Build an Image
```bash
docker build -t <image-name>:<tag> .
```
Builds an image from a Dockerfile in the current directory.

**With custom Dockerfile path:**
```bash
docker build -f path/to/Dockerfile -t <image-name>:<tag> .
```

**Examples:**
```bash
docker build -t my-dev-image .
docker build -t myapp:v1.0 -f Dockerfile.prod .
```

### Inspect an Image
```bash
docker inspect <image-name>
```
Shows detailed metadata (layers, env vars, entrypoint, etc.).

### Inspect a Container
```bash
docker inspect <container-name>
```
Shows detailed container information (IP, mounts, state, etc.).

### Remove an Image
```bash
docker rmi <image-name>
docker image rm <image-name>
```
Deletes an image from local storage.

### Remove Unused Images
```bash
docker image prune -a
```
Removes all dangling and unused images.

### Build Image from Existing Container
```bash
docker commit <container-name-or-id> <new-image-name>
```
Creates a new image from a container's current state.

**Example:**
```bash
docker commit my-container my-snapshot:v1
```



---

## Testing & Debugging

### Run Tests Inside Container
```bash
docker run --rm <image-name> /bin/bash -c "poetry run pytest"
```
Runs tests in an ephemeral container (auto-removed after execution).

### Run Container with Custom Command
```bash
docker run --rm <image-name> <command>
```
Overrides the default CMD specified in Dockerfile.

**Example:**
```bash
docker run --rm my-dev-image poetry run pytest
docker run --rm nginx cat /etc/nginx/nginx.conf
```

---

## Dockerfile Syntax

### Example Dockerfile (FastAPI + Poetry)
```dockerfile
LABEL maintainer="ameen-alam"

# Set the working directory in the container
WORKDIR /code

# Install system dependencies required for potential Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy the current directory contents into the container at /code
COPY . /code/

# Configuration to avoid creating virtual environments inside the Docker container
RUN poetry config virtualenvs.create false

# Install dependencies including development ones
RUN poetry install

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app. CMD can be overridden when starting the container
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
```

### Dockerfile Instructions Reference

| Instruction | Description |
|-------------|-------------|
| `FROM <image>` | Base image to build upon |
| `LABEL <key>=<value>` | Add metadata (e.g., maintainer) |
| `WORKDIR <path>` | Set working directory for subsequent instructions |
| `RUN <command>` | Execute command during build (creates a layer) |
| `COPY <src> <dest>` | Copy files from host to container |
| `ADD <src> <dest>` | Like COPY, but also extracts tarballs and supports URLs |
| `EXPOSE <port>` | Document which port the container listens on |
| `ENV <key>=<value>` | Set environment variables |
| `CMD [...]` | Default command when container starts (can be overridden) |
| `ENTRYPOINT [...]` | Main executable (CMD provides default args) |
| `VOLUME <path>` | Create mount point for volumes |
| `ARG <name>` | Build-time variable |
| `USER <user>` | Switch to non-root user |

---

## Docker Compose

Docker Compose defines and runs multi-container applications using a `compose.yaml` file.

### Example compose.yaml
```yaml
version: "3.8"
name: "fastapi"
services:
  api:
    build:
      context: ./
      dockerfile: Dockerfile
    container_name: fastapicontainer
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    container_name: postgres-db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Check Compose Version
```bash
docker compose version
```

### Validate Compose File
```bash
docker compose config
```
Parses and displays the resolved configuration (validates syntax).

### Start Services
```bash
docker compose up -d
```
Creates and starts all services in detached (background) mode.

### Build and Start
```bash
docker compose up -d --build
```
Rebuilds images before starting services.

### Stop Services
```bash
docker compose stop
```
Stops running containers without removing them.

### Start Stopped Services
```bash
docker compose start
```
Starts previously stopped containers.

### Stop and Remove Services
```bash
docker compose down
```
Stops containers and removes containers, networks created by compose.

### Remove Everything (Including Volumes)
```bash
docker compose down -v
```
Removes volumes as well (use with caution - deletes persistent data).

### List Services
```bash
docker compose ps
```
Shows status of all services defined in compose file.

### View Service Logs
```bash
docker compose logs
docker compose logs -f <service-name>
```
Displays aggregated logs from all services or a specific service.

### Execute Command in Service
```bash
docker compose exec <service-name> /bin/bash
```
Runs a command inside a running service container.

### Rebuild a Specific Service
```bash
docker compose build <service-name>
```
Rebuilds the image for a specific service.

### Restart a Service
```bash
docker compose restart <service-name>
```
Restarts a specific service.

---

## Quick Reference Table

### Images
| Command | Description |
|---------|-------------|
| `docker pull <image>` | Download an image |
| `docker images` | List local images |
| `docker build -t <name> .` | Build image from Dockerfile |
| `docker inspect <image>` | View image metadata |
| `docker rmi <image>` | Remove an image |
| `docker image prune -a` | Remove unused images |

### Containers
| Command | Description |
|---------|-------------|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker run -d -p 8000:8000 <image>` | Run container in background |
| `docker run -it <image> /bin/bash` | Run interactively |
| `docker exec -it <container> /bin/bash` | Shell into running container |
| `docker logs <container> [-f]` | View/follow container logs |
| `docker stop <container>` | Stop a container |
| `docker start <container>` | Start a stopped container |
| `docker rm <container>` | Remove a container |
| `docker rm -f <container>` | Force remove running container |
| `docker commit <container> <image>` | Create image from container |

### Docker Compose
| Command | Description |
|---------|-------------|
| `docker compose config` | Validate compose file |
| `docker compose up -d` | Start services (detached) |
| `docker compose up -d --build` | Rebuild and start |
| `docker compose down` | Stop and remove services |
| `docker compose down -v` | Stop, remove services and volumes |
| `docker compose ps` | List services |
| `docker compose stop` | Stop services |
| `docker compose start` | Start stopped services |
| `docker compose logs -f <svc>` | Follow service logs |
| `docker compose exec <svc> sh` | Shell into service |
| `docker compose build <svc>` | Rebuild specific service |
| `docker compose restart <svc>` | Restart specific service |

---

## Common Port Mappings

| Service | Host:Container |
|---------|---------------|
| FastAPI/Flask | `8000:8000` |
| Django | `8000:8000` or `8080:8000` |
| Nginx | `80:80` or `443:443` |
| PostgreSQL | `5432:5432` |
| MySQL | `3306:3306` |
| Redis | `6379:6379` |
| MongoDB | `27017:27017` |
