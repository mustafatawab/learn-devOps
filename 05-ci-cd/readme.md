# ⚙️ CI/CD Pipelines with GitHub Actions

A beginner-friendly guide to understanding and implementing CI/CD pipelines - from zero to production.

---

## Table of Contents

1. [What is CI/CD?](#what-is-cicd)
2. [What is GitHub Actions?](#what-is-github-actions)
3. [Core Concepts](#core-concepts)
4. [Anatomy of a Workflow File](#anatomy-of-a-workflow-file)
5. [Triggers](#triggers)
6. [Jobs & Dependencies](#jobs--dependencies)
7. [Secrets](#secrets)
8. [Caching](#caching)
9. [Templates](#templates)

---

## What is CI/CD?

Let's start with a simple story.

You built an app. It works perfectly. Your friend also starts working on the same app. He writes some new code and sends it to you saying *"add my code to the app."*

**What would you do before adding his code?**

Naturally - you'd run it first. Make sure it works. Make sure it doesn't break anything.

Now imagine instead of 1 friend, you have **10 friends** all sending you code every day. Would you manually run and test each person's code every single day?

That becomes impossible. **CI/CD automates exactly this.**

---

### CI - Continuous Integration

Every time someone pushes code, a robot automatically:

```
Developer pushes code
        ↓
✅ Installs dependencies
✅ Runs linting
✅ Runs tests
✅ Builds the app
        ↓
❌ Something broke → developer is notified, PR is blocked
✅ Everything passed → PR is safe to merge
```

No broken code ever reaches `main` - automatically, without anyone doing it manually.

---

### CD - Continuous Deployment

Once code is merged to `main`, a robot automatically:

```
Code merged to main
        ↓
✅ Tests run again (on merged code)
✅ Docker image is built
✅ Image is pushed to registry (GHCR)
✅ Server pulls new image
✅ App restarts with new version
        ↓
🚀 New version is live in production
```

No SSH-ing into servers. No forgetting to pull. No deploying broken code.

---

### CI vs CD - Summary

```
CI (Continuous Integration)   → verify code is safe to merge
CD (Continuous Deployment)    → ship verified code to production
```

Together:

```
Code Push → [CI] Test & Build → [CD] Deploy
   👨‍💻              🧪                  🚀
```

---

### Why Test Again in CD?

Your CI tested the PR branch. But between your PR being approved and reaching `main`, other developers may have merged their code too. The merged result could behave differently.

```
main:      A + B + C
your PR:         C + D
after merge: A + B + C + D  ← test THIS, not just D
```

Always test what's actually in `main` - not just the branch.

---

## What is GitHub Actions?

GitHub Actions is GitHub's built-in CI/CD platform. It's:

- **Free** for public repos
- **Built into GitHub** - no separate tool to set up
- **Triggered automatically** by events in your repo (push, PR, etc.)
- **Runs on GitHub's servers** - no server management needed

Every time you push code, GitHub spins up a **fresh virtual machine**, runs your pipeline, and destroys the machine when done.

---

## Core Concepts

GitHub Actions has four building blocks:

```
Workflow  →  A single automation process (one YAML file)
  └── Job  →  Runs on its own machine, in parallel by default
       └── Step  →  One task inside a job (runs sequentially)
            └── Action  →  A reusable pre-built step (like an npm package)
```

### Workflow

A YAML file inside `.github/workflows/`. GitHub scans all files in this folder automatically - the filename doesn't matter, only the content.

```
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml       ← runs on every PR
        └── cd.yml       ← runs on merge to main
```

### Jobs

One workflow can have multiple jobs. By default jobs run **in parallel**. Use `needs` to make them run in sequence.

### Steps

Steps inside a job run **sequentially**. If one step fails, all remaining steps are skipped and the job fails.

### Actions

Pre-built reusable steps from the GitHub Marketplace. Think of them like npm packages for your pipeline:

```yaml
uses: actions/checkout@v4       # pulls your repo code onto the VM
uses: actions/setup-node@v4     # installs Node.js
uses: docker/login-action@v3    # logs into a Docker registry
uses: appleboy/ssh-action@v1    # SSHs into your server
```

The `@v4` is the version - just like `npm install express@4`.

---

## Anatomy of a Workflow File

```yaml
name: CI Pipeline          # label shown in GitHub Actions UI

on:                        # when to run this workflow
  pull_request:
    branches: [main]

env:                       # global environment variables
  NODE_VERSION: 22

jobs:                      # what to run
  build:                   # job name (you choose this)
    runs-on: ubuntu-latest # which VM to use

    steps:
      - name: Checkout code          # step label (optional but recommended)
        uses: actions/checkout@v4    # uses a pre-built action

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:                        # parameters passed to the action
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci                  # run a shell command

      - name: Build
        run: npm run build
        env:                         # environment variables for this step only
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
```

### Key Syntax

| Syntax | Meaning |
|--------|---------|
| `uses:` | Use a pre-built action |
| `run:` | Run a shell command |
| `with:` | Pass parameters to an action |
| `env:` | Set environment variables |
| `needs:` | Wait for another job to finish |
| `${{ }}` | Expression syntax - reference variables, secrets, context |
| `${{ secrets.NAME }}` | Read a GitHub secret |
| `${{ github.actor }}` | GitHub username that triggered the workflow |
| `${{ github.repository }}` | `owner/repo-name` |

### `run` vs `uses`

```yaml
# run → execute a shell command
- run: npm install
- run: echo "Hello World"
- run: |
    npm install    # multi-line commands use | 
    npm run build

# uses → use a pre-built action
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
```

### `npm ci` vs `npm install`

```yaml
- run: npm ci       # ✅ recommended in CI
- run: npm install  # ⚠️ fine locally
```

`npm ci` is better in pipelines because:
- Faster - skips dependency resolution
- Deterministic - uses `package-lock.json` exactly
- Fails if `package-lock.json` is out of sync with `package.json`

---

## Triggers

The `on:` block defines when your workflow runs:

```yaml
on:
  # Run when code is pushed to a branch
  push:
    branches: [main, develop]

  # Run when a PR is opened or updated
  pull_request:
    branches: [main]

  # Run on a schedule (cron syntax)
  schedule:
    - cron: "0 6 * * 1"  # every Monday at 6 AM UTC

  # Run manually from GitHub UI
  workflow_dispatch:

  # Run only when specific files change
  push:
    paths:
      - "api/**"
      - "Dockerfile"
      - "compose.yaml"
```

### Common Patterns

| Scenario | Trigger |
|----------|---------|
| Test every PR | `pull_request: { branches: [main] }` |
| Deploy on merge | `push: { branches: [main] }` |
| Nightly builds | `schedule: [{ cron: "0 2 * * *" }]` |
| Manual deploy | `workflow_dispatch:` |
| Tagged releases | `push: { tags: ["v*"] }` |

---

## Jobs & Dependencies

### Parallel Jobs (default)

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test

# lint and test run at the same time ✅
```

### Sequential Jobs (needs)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  build:
    needs: [test]          # waits for test to pass
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  deploy:
    needs: [build]         # waits for build to pass
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying..."

# test → build → deploy (in sequence)
```

If `test` fails → `build` never runs → `deploy` never runs.

### Conditional Steps

```yaml
# Only run on push to main (not on PRs)
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: echo "deploying..."

# Only run on PRs
- name: Comment on PR
  if: github.event_name == 'pull_request'
  run: echo "commenting..."

# Continue even if this step fails
- name: Lint
  run: npm run lint
  continue-on-error: true   # informational only, doesn't fail the job
```

---

## Secrets

Never hardcode credentials in your workflow files. Store them as GitHub Secrets.

**Adding a secret:**
```
Your repo → Settings → Secrets and variables → Actions → New repository secret
```

**Using a secret:**
```yaml
- name: Deploy
  env:
    SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: echo "using secrets safely"
```

### Common Secrets

| Secret | Purpose |
|--------|---------|
| `SSH_PRIVATE_KEY` | SSH private key to connect to VPS |
| `SERVER_HOST` | VPS IP address or domain |
| `SERVER_USER` | VPS username (e.g. `ubuntu`) |
| `RESEND_API_KEY` | Email API key |
| `DATABASE_URL` | Database connection string |

> **Note:** `GITHUB_TOKEN` is provided automatically by GitHub - no setup needed. It's used for pushing to GHCR.

---

## Caching

Without caching, every pipeline run downloads all dependencies from scratch. With caching, repeated runs are much faster.

### Node.js (npm)

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: "npm"           # caches node_modules automatically
```

### Python (uv)

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"

- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}

- run: uv sync
```

### Docker Layer Caching

```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha      # restore layers from GitHub cache
    cache-to: type=gha,mode=max  # save layers to GitHub cache
```

### PHP (Composer)

```yaml
- uses: actions/cache@v4
  with:
    path: vendor
    key: ${{ runner.os }}-composer-${{ hashFiles('composer.lock') }}

- run: composer install --no-dev --optimize-autoloader
```

---

## Templates

Ready-made CI/CD pipeline templates for different project stacks. Each template includes:

- `ci.yml` - runs on every PR (test + build)
- `cd.yml` - runs on merge to main (build Docker image → push to GHCR → deploy to VPS via SSH)

All templates assume:
- Docker + Docker Compose on the VPS
- GHCR as the image registry
- SSH deployment

### Available Templates

| Stack | CI | CD |
|-------|----|----|
| [Next.js](./templates/nextjs/) | [ci.yml](./templates/nextjs/ci.yml) | [cd.yml](./templates/nextjs/cd.yml) |
| [Next.js + Node.js](./templates/nextjs-node/) | [ci.yml](./templates/nextjs-node/ci.yml) | [cd.yml](./templates/nextjs-node/cd.yml) |
| [Next.js + FastAPI](./templates/nextjs-fastapi/) | [ci.yml](./templates/nextjs-fastapi/ci.yml) | [cd.yml](./templates/nextjs-fastapi/cd.yml) |
| [FastAPI](./templates/fastapi/) | [ci.yml](./templates/fastapi/ci.yml) | [cd.yml](./templates/fastapi/cd.yml) |
| [Laravel](./templates/laravel/) | [ci.yml](./templates/laravel/ci.yml) | [cd.yml](./templates/laravel/cd.yml) |

### Required Secrets (all templates)

```
Settings → Secrets and variables → Actions

SERVER_HOST       → your VPS IP or domain
SERVER_USER       → your VPS username (e.g. ubuntu)
SSH_PRIVATE_KEY   → your SSH private key (cat ~/.ssh/id_rsa)
```

Stack-specific secrets are listed inside each template file.