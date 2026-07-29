# 🔧 NGINX Setup Guide

A step-by-step guide to setting up NGINX as a reverse proxy from scratch — covering bare metal installation and Docker Compose setup.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup A — Bare Metal NGINX](#setup-a--bare-metal-nginx)
3. [Setup B — NGINX in Docker Compose](#setup-b--nginx-in-docker-compose)
4. [Adding SSL with Let's Encrypt](#adding-ssl-with-lets-encrypt)
5. [Multiple Apps on One Server](#multiple-apps-on-one-server)
6. [Quick Reference](#quick-reference)

---

## Prerequisites

- Ubuntu server (VPS or local VM)
- Your app running on a port (e.g. `3000`)
- SSH access to the server

---

## Setup A — Bare Metal NGINX

Use this when your app runs directly on the server (not in Docker).

### Step 1 — Install NGINX

```bash
sudo apt update
sudo apt install -y nginx

# Start and enable on boot
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify
sudo systemctl status nginx
```

Visit `http://YOUR_SERVER_IP` — you should see the NGINX welcome page. ✅

---

### Step 2 — Create Site Config

```bash
sudo nano /etc/nginx/sites-available/myapp
```

Paste this config:

```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;   # or your domain e.g. portfolio.com

    location / {
        proxy_pass http://localhost:3000;   # your app port

        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;

        # Pass original request info to the app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save with `Ctrl+X → Y → Enter`.

---

### Step 3 — Enable the Site

```bash
# Create symlink to enable the site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/

# Optional: disable the default site to avoid conflicts
sudo rm /etc/nginx/sites-enabled/default
```

---

### Step 4 — Test Config

**Always test before reloading:**

```bash
sudo nginx -t
```

Expected output:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

If it fails — fix the config, do NOT reload.

---

### Step 5 — Reload NGINX

```bash
sudo systemctl reload nginx
```

> Use `reload` not `restart` — reload applies new config without dropping existing connections.

---

### Step 6 — Verify

Visit `http://YOUR_SERVER_IP` — you should see your app without any port number. ✅

```bash
# Quick check from terminal
curl -I http://localhost
curl -I http://YOUR_SERVER_IP
```

---

## Setup B — NGINX in Docker Compose

Use this when your app runs inside Docker containers.

> **Key difference:** In Docker Compose, `proxy_pass` uses the **service name** not `localhost`.
> `localhost` inside a container = that container itself, not your app.

---

### Project Structure

```
your-project/
├── compose.yaml
├── Dockerfile
├── nginx/
│   └── default.conf    ← NGINX config
├── app/
└── ...
```

---

### Step 1 — Create NGINX Config

```bash
mkdir nginx
nano nginx/default.conf
```

Paste this config:

```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;   # or your domain

    location / {
        proxy_pass http://app:3000;   # ← service name, NOT localhost!

        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;

        # Pass original request info to the app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> Replace `app` with your actual service name in `compose.yaml`.

---

### Step 2 — Write compose.yaml

```yaml
name: myapp

services:
  # Your application
  app:
    build:
      context: ./
      dockerfile: Dockerfile
    # ❌ Do NOT expose port 3000 — NGINX handles all traffic
    env_file:
      - ./.env
    restart: unless-stopped

  # NGINX reverse proxy
  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    ports:
      - "80:80"       # only NGINX is exposed to the world
    volumes:
      - ./nginx/default.conf:/etc/nginx/nginx.conf   # mount our config
    depends_on:
      app:
        condition: service_started
    restart: unless-stopped
```

---

### Step 3 — Start Everything

```bash
docker compose up -d --build
```

---

### Step 4 — Verify

```bash
# Check all containers are running
docker compose ps

# Check NGINX logs
docker compose logs nginx

# Check app logs
docker compose logs app
```

Visit `http://YOUR_SERVER_IP` — your app should load without any port number. ✅

---

### Step 5 — Redeploy After Code Changes

```bash
# Rebuild and restart
docker compose up -d --build

# Or if using pre-built images from GHCR
docker compose pull
docker compose up -d
docker image prune -f
```

---

## Adding SSL with Let's Encrypt

> **Note:** SSL requires a real domain name pointing to your server. It does NOT work with IP addresses.

### Bare Metal NGINX

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d portfolio.com -d www.portfolio.com

# Certbot auto-renews — verify renewal works
sudo certbot renew --dry-run
```

Certbot automatically updates your NGINX config to listen on port 443.

After SSL your traffic flow:
```
Browser --HTTPS:443--> NGINX --HTTP:3000--> App
```

### HTTPS NGINX Config (after Certbot)

```nginx
server {
    listen 80;
    server_name portfolio.com www.portfolio.com;
    return 301 https://$host$request_uri;   # redirect HTTP → HTTPS
}

server {
    listen 443 ssl;
    server_name portfolio.com www.portfolio.com;

    ssl_certificate /etc/letsencrypt/live/portfolio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/portfolio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Multiple Apps on One Server

Run multiple apps on the same server using different domains.

### Domain-Based Routing (different domains)

```nginx
# portfolio.com → app on :3000
server {
    listen 80;
    server_name portfolio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# api.mustafatawab.com → app on :9000
server {
    listen 80;
    server_name api.mustafatawab.com;

    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Create a separate file for each app:
```bash
sudo nano /etc/nginx/sites-available/portfolio
sudo nano /etc/nginx/sites-available/api
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Path-Based Routing (one domain, different paths)

```nginx
server {
    listen 80;
    server_name mustafatawab.com;

    # Frontend → :3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API → :9000 (note trailing slash on both sides)
    location /api/ {
        proxy_pass http://localhost:9000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```
http://mustafatawab.com/        → frontend on :3000
http://mustafatawab.com/api/    → backend on :9000
```

---

## Quick Reference

### File Locations

| Path | Purpose |
|------|---------|
| `/etc/nginx/nginx.conf` | Main NGINX config |
| `/etc/nginx/sites-available/` | Write your site configs here |
| `/etc/nginx/sites-enabled/` | Active sites (symlinks) |
| `/var/log/nginx/access.log` | All requests |
| `/var/log/nginx/error.log` | Errors |

### Essential Commands

```bash
# Install
sudo apt install -y nginx

# Service management
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx      # full restart
sudo systemctl reload nginx       # apply config, no downtime ✅
sudo systemctl enable nginx       # start on boot
sudo systemctl status nginx       # check if running

# Config management
sudo nginx -t                     # test syntax (always before reload!)
sudo nginx -T                     # print full effective config

# Enable a site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/

# Disable a site
sudo rm /etc/nginx/sites-enabled/myapp

# View logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# SSL
sudo certbot --nginx -d domain.com
sudo certbot renew --dry-run
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `502 Bad Gateway` | App not running — check `curl localhost:3000` |
| `404 Not Found` | Wrong `server_name` or `location` |
| Config error on reload | Run `sudo nginx -t` and fix errors first |
| Site not working | Check symlink exists in `sites-enabled` |
| Changes not applied | Run `sudo systemctl reload nginx` |
| Wrong IP in app logs | Add `X-Real-IP` and `X-Forwarded-For` headers |
| HTTPS redirect loop | Add `X-Forwarded-Proto $scheme` header |
| WebSockets not working | Add `Upgrade` and `Connection` headers |
| Port 80 already in use | Check `sudo lsof -i :80` |

### Bare Metal vs Docker Compose

| | Bare Metal | Docker Compose |
|--|------------|----------------|
| Install NGINX | `sudo apt install nginx` | Use `nginx:alpine` image |
| Config location | `/etc/nginx/sites-available/` | `./nginx/default.conf` mounted as volume |
| `proxy_pass` | `http://localhost:PORT` | `http://SERVICE_NAME:PORT` |
| Apply changes | `sudo systemctl reload nginx` | `docker compose restart nginx` |
| View logs | `sudo tail -f /var/log/nginx/error.log` | `docker compose logs nginx` |