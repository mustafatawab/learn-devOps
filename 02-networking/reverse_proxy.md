# Nginx Reverse Proxy

A beginner-friendly guide to understanding reverse proxies and configuring Nginx to sit in front of your apps.

---

## Table of Contents

1. [What is a Reverse Proxy?](#what-is-a-reverse-proxy)
2. [Without vs With Reverse Proxy](#without-vs-with-reverse-proxy)
3. [Forward Proxy vs Reverse Proxy](#forward-proxy-vs-reverse-proxy)
4. [Why Use a Reverse Proxy?](#why-use-a-reverse-proxy)
5. [Install Nginx](#install-nginx)
6. [Nginx Config Layout](#nginx-config-layout)
7. [Basic Reverse Proxy Config](#basic-reverse-proxy-config)
8. [Enable the Site](#enable-the-site)
9. [Understanding the Headers](#understanding-the-headers)
10. [Domain-Based vs Path-Based Routing](#domain-based-vs-path-based-routing)
11. [Load Balancing with Upstream](#load-balancing-with-upstream)
12. [HTTPS / SSL (Let's Encrypt)](#https--ssl-lets-encrypt)
13. [Useful Commands](#useful-commands)
14. [Troubleshooting](#troubleshooting)

---

## What is a Reverse Proxy?

Imagine you call a big company's customer service number. You don't know which specific employee will answer - you just call one number and the company decides internally who handles your call.

```
You (customer)
      ↓
📞 One phone number (company's main line)
      ↓
Company decides internally → routes to the right employee
      ↓
Employee handles your request
      ↓
Response comes back to you
```

You never knew which employee handled it. You just called one number. ✅

That's exactly what a reverse proxy does:

```
User (customer)
      ↓
🌐 One IP/domain (reverse proxy)
      ↓
Proxy decides internally → routes to the right app/port
      ↓
App handles the request
      ↓
Response comes back to user
```

**Nginx** is a popular web server that is often used as a reverse proxy.

---

## Without vs With Reverse Proxy

### Without reverse proxy

```
Portfolio app  → port 3000
Blog app       → port 4000
API            → port 5000

User must know:
  http://192.168.252.11:3000  → portfolio
  http://192.168.252.11:4000  → blog
  http://192.168.252.11:5000  → API
```

Problems:
- Users see ugly ports
- Apps are exposed directly to the internet
- Hard to add HTTPS, logging, or rate limits in one place

### With reverse proxy

```
Portfolio app  → port 3000  (hidden)
Blog app       → port 4000  (hidden)
API            → port 5000  (hidden)

NGINX sits in front on port 80:
  http://portfolio.com    → forwards to :3000
  http://blog.com         → forwards to :4000
  http://api.com          → forwards to :5000
```

Users only talk to Nginx on port **80** (HTTP) or **443** (HTTPS). Backend ports stay private.

---

## Forward Proxy vs Reverse Proxy

| | Forward Proxy | Reverse Proxy |
|--|---------------|---------------|
| Sits in front of | **Clients** | **Servers** |
| Flow | Clients → Forward Proxy → Internet | Internet → Reverse Proxy → Your servers |
| Hides | Client identity | Server / app details |
| Common uses | Content filtering, company blocks websites, anonymity | Hide ports, load balancing, SSL termination |

```
Forward proxy:   Client → Proxy → Internet
Reverse proxy:   Internet → Proxy → Your Apps
```

---

## Why Use a Reverse Proxy?

- **Hide backend servers** - users never see `:3000`, `:4000`, etc.
- **One public entry point** - port 80/443 only
- **SSL / HTTPS termination** - Nginx handles certificates; apps can stay on HTTP internally
- **Load balancing** - spread traffic across multiple app instances
- **Routing** - by domain (`api.com`) or by path (`/api`)
- **Extra features** - caching, compression, rate limiting, access logs

---

## Install Nginx

On Ubuntu / Debian:

```bash
sudo apt update
sudo apt install nginx

sudo systemctl status nginx
sudo systemctl enable nginx     # start on boot
```

Default page should open at `http://YOUR_SERVER_IP`.

---

## Nginx Config Layout

| Path | Purpose |
|------|---------|
| `/etc/nginx/nginx.conf` | Main Nginx config |
| `/etc/nginx/sites-available/` | Site configs you write (not always active) |
| `/etc/nginx/sites-enabled/` | Symlinks to configs that are **active** |
| `/var/log/nginx/access.log` | Request log |
| `/var/log/nginx/error.log` | Error log |

> Pattern: create file in `sites-available` → symlink into `sites-enabled` → test → reload.

---

## Basic Reverse Proxy Config

Create a config file:

```bash
sudo nano /etc/nginx/sites-available/portfolio
```

```nginx
server {
    listen 80;
    server_name 192.168.252.11;   # or portfolio.com

    location / {
        proxy_pass http://localhost:3000;

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

**What this does:** any request to this server on port 80 is forwarded to the app running on `localhost:3000`.

> Tip: also add `X-Forwarded-For` and `X-Forwarded-Proto` so the app knows the real client IP and whether the original request was HTTP or HTTPS.

---

## Enable the Site

```bash
# 1. Create symlink (activate the site)
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/

# Optional: remove default site if it conflicts
sudo rm /etc/nginx/sites-enabled/default

# 2. Test config for syntax errors (always do this)
sudo nginx -t

# 3. Reload Nginx to apply changes (no downtime)
sudo systemctl reload nginx
```

If `nginx -t` fails, **do not reload** - fix the config first.

---

## Understanding the Headers

| Directive | Meaning |
|-----------|---------|
| `proxy_pass` | Where Nginx forwards the request (your app URL) |
| `proxy_http_version 1.1` | Needed for keep-alive and WebSockets |
| `Upgrade` / `Connection` | Lets WebSocket connections work through the proxy |
| `Host` | Sends the original hostname to the app |
| `X-Real-IP` | Client’s real IP address |
| `X-Forwarded-For` | Chain of client IPs (important behind multiple proxies) |
| `X-Forwarded-Proto` | Original scheme: `http` or `https` |
| `proxy_cache_bypass` | Don’t cache WebSocket upgrade requests |

Without these headers, apps may generate wrong URLs, log `127.0.0.1` as the user, or break cookies / HTTPS redirects.

---

## Domain-Based vs Path-Based Routing

### Domain-based (different hostnames)

```nginx
# portfolio.com → :3000
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

# api.com → :5000
server {
    listen 80;
    server_name api.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

DNS for each domain must point to your server’s IP.

### Path-based (one domain, different paths)

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;   # frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:5000/;  # trailing slash matters
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```
http://example.com/        → app on :3000
http://example.com/api/    → app on :5000
```

---

## Load Balancing with Upstream

One reverse proxy can distribute traffic across several app instances:

```nginx
upstream api_backends {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name api.com;

    location / {
        proxy_pass http://api_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

By default Nginx uses **round-robin** (request 1 → server A, request 2 → server B, …).

---

## HTTPS / SSL (Let's Encrypt)

Reverse proxies commonly terminate SSL: browsers talk HTTPS to Nginx; Nginx talks HTTP to your local apps.

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d portfolio.com -d www.portfolio.com
```

Certbot can edit your Nginx config to listen on **443** and renew certificates automatically.

After SSL:

```
Browser --HTTPS:443--> Nginx --HTTP:3000--> App
```

Always keep `X-Forwarded-Proto $scheme` so the app knows the user used HTTPS.

---

## Useful Commands

```bash
sudo systemctl status nginx       # is Nginx running?
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx      # full restart
sudo systemctl reload nginx       # apply config without dropping connections

sudo nginx -t                     # test config syntax
sudo nginx -T                     # print full effective config

sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| `502 Bad Gateway` | Is the app running on the `proxy_pass` port? (`curl localhost:3000`) |
| `404 Not Found` | Wrong `server_name` or `location` path |
| Config won’t load | Run `sudo nginx -t` and read the error |
| Site not active | Missing symlink in `sites-enabled` |
| Changes not applied | Forgot `sudo systemctl reload nginx` |
| Wrong client IP in app logs | Missing `X-Real-IP` / `X-Forwarded-For` |
| HTTPS redirect loop | Missing or wrong `X-Forwarded-Proto` |
| WebSockets fail | Missing `Upgrade` and `Connection` headers |
| Permission / bind error | Port 80 needs root/capabilities; check `error.log` |

Quick backend check:

```bash
curl -I http://localhost:3000
curl -I http://YOUR_SERVER_IP
```

---

## Quick Cheatsheet

| Need | Do this |
|------|---------|
| Install | `sudo apt install nginx` |
| New site config | `/etc/nginx/sites-available/myapp` |
| Enable site | `ln -s ... sites-enabled/` |
| Test | `sudo nginx -t` |
| Apply | `sudo systemctl reload nginx` |
| Proxy to app | `proxy_pass http://localhost:PORT;` |
| HTTPS | `sudo certbot --nginx -d domain.com` |
| Logs | `/var/log/nginx/error.log` |
