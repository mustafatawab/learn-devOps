# 3.1 - Git Basics

Learn Git from scratch - what it is, how to set it up, and the everyday commands you’ll use forever.

---

## Table of Contents

1. [What is Git?](#what-is-git)
2. [Git vs GitHub](#git-vs-github)
3. [Core Concepts](#core-concepts)
4. [Install & First-Time Setup](#install--first-time-setup)
5. [Create or Clone a Repository](#create-or-clone-a-repository)
6. [The Daily Workflow](#the-daily-workflow)
7. [See What Changed](#see-what-changed)
8. [Undo Safe Basics](#undo-safe-basics)
9. [Ignore Files (.gitignore)](#ignore-files-gitignore)
10. [Good Commit Messages](#good-commit-messages)
11. [Quick Cheatsheet](#quick-cheatsheet)

---

## What is Git?

**Git** is a version control system. It saves snapshots of your project over time so you can:

- Go back to any previous version
- See who changed what and when
- Work on features without breaking the main code
- Collaborate without emailing zip files

> Think of Git like **save points in a game**. Each commit is a save. You can reload an old save without losing the whole game.

Without Git:

```
project/
project-backup/
project-final/
project-final-v2/
project-REALLY-final/
```

With Git: one folder + a full history of every meaningful change.

---

## Git vs GitHub

| | Git | GitHub |
|--|-----|--------|
| What | Software on your computer | Website / cloud service |
| Job | Track history locally | Host remotes, PRs, Issues, Actions |
| Need internet? | No (for local work) | Yes (to push/pull/collaborate) |

```
Your laptop (Git)  ←→  GitHub (remote copy + collaboration tools)
```

You can use Git without GitHub. You cannot get GitHub’s full value without Git.

Other hosts exist (GitLab, Bitbucket) - same Git commands, different websites.

---

## Core Concepts

### Repository (repo)

A project folder tracked by Git. Contains your files **plus** a hidden `.git/` directory (the database of history).

### The three areas

```
Working Directory     Staging Area (Index)     Repository (.git)
─────────────────     ────────────────────     ─────────────────
Files you edit   →    Files marked "ready"  →  Saved commits
                      with git add             with git commit
```

| Area | Meaning |
|------|---------|
| **Working directory** | Files as you see them in the folder |
| **Staging area** | The next commit “shopping cart” - what will be saved |
| **Repository** | Permanent history of commits |

### Commit

A snapshot with:

- Unique ID (hash), e.g. `a1b2c3d`
- Author, date, message
- Pointer to the previous commit (forms a chain)

```
(A) ← (B) ← (C) ← (D)   ← newest commit (usually where you are)
```

### HEAD

A pointer to “where you are now” - usually the tip of the current branch.

---

## Install & First-Time Setup

### Install

```bash
# macOS (Homebrew)
brew install git

# Ubuntu / Debian
sudo apt update
sudo apt install git

git --version
```

### Tell Git who you are

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the **same email** as your GitHub account (or a GitHub noreply email) so commits link to your profile.

### Useful defaults

```bash
git config --global init.defaultBranch main
git config --global color.ui auto
git config --global pull.rebase false    # merge on pull (simple default)
```

### See your config

```bash
git config --list
git config --global --list
```

| Scope | Flag | Where it applies |
|-------|------|------------------|
| System | `--system` | Whole machine |
| Global | `--global` | Your user account |
| Local | (default in a repo) | One repository only |

---

## Create or Clone a Repository

### Start a new repo in an existing folder

```bash
mkdir my-app && cd my-app
git init
```

Creates `.git/` and starts tracking history from here.

### Clone an existing repo (from GitHub)

```bash
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git        # SSH
cd repo
```

**`git clone`** - Downloads the project **and** its full Git history, then sets `origin` as the remote.

---

## The Daily Workflow

This is 90% of what you’ll do every day:

```bash
git status                  # what’s changed?
git add file.txt            # stage one file
git add .                   # stage everything (careful)
git commit -m "message"     # save a snapshot
```

### Step by step

**1. `git status`** - Shows modified, staged, and untracked files. Run this often.

**2. `git add`** - Moves changes into the staging area.

```bash
git add index.html
git add src/                # stage a folder
git add -p                  # stage hunks interactively (advanced but useful)
```

**3. `git commit`** - Saves the staged snapshot permanently in history.

```bash
git commit -m "Add login form validation"
```

### First commit tip

```bash
git add .
git commit -m "Initial commit"
```

### Amend the last commit (only if not pushed yet, or you’re sure)

```bash
git add forgotten-file.txt
git commit --amend --no-edit     # keep same message
git commit --amend -m "New msg"  # change message
```

> **Rule:** Don’t amend commits that others already pulled - it rewrites history.

---

## See What Changed

**`git status`** - High-level: which files changed / staged.

**`git diff`** - Line-by-line changes **not yet staged**.

```bash
git diff
```

**`git diff --staged`** (or `--cached`) - Changes that **are** staged, ready to commit.

```bash
git diff --staged
```

**`git log`** - Commit history.

```bash
git log
git log --oneline              # short one line per commit
git log --oneline --graph      # ASCII branch graph
git log -5                     # last 5 commits
git log --author="Yasir"
```

**`git show`** - Details of one commit (message + diff).

```bash
git show
git show a1b2c3d
```

---

## Undo Safe Basics

These are the safe “oops” tools for beginners. Deeper recovery is in [3.4-git_advanced.md](./3.4-git_advanced.md).

| Goal | Command |
|------|---------|
| Unstage a file (keep edits) | `git restore --staged file.txt` |
| Discard unstaged edits in a file | `git restore file.txt` |
| Unstage everything | `git restore --staged .` |

Older docs may show:

```bash
git reset HEAD file.txt      # unstage (older style)
git checkout -- file.txt     # discard changes (older style)
```

Prefer `git restore` on modern Git.

> **Warning:** `git restore file.txt` throws away uncommitted work in that file. There is no recycle bin.

---

## Ignore Files (.gitignore)

Some files should **never** be committed:

- Secrets (`.env`, keys)
- Dependencies (`node_modules/`, `.venv/`)
- Build output (`dist/`, `build/`)
- OS junk (`.DS_Store`)

Create `.gitignore` in the repo root:

```gitignore
# dependencies
node_modules/
.venv/

# env / secrets
.env
.env.local
*.pem

# build
dist/
build/
__pycache__/

# OS / editor
.DS_Store
.idea/
.vscode/
```

**`git check-ignore -v file`** - Explains why a file is ignored.

If you already committed a secret by mistake:

1. Rotate the secret (treat it as leaked)
2. Remove from Git tracking (see advanced notes)
3. Add it to `.gitignore`

---

## Good Commit Messages

Bad:

```
fix
updates
asdf
final
```

Good:

```
Add rate limiting to login API
Fix nginx 502 when upstream is down
Remove unused docker-compose volume
```

**Simple formula:**

```
<verb in imperative> <what changed and why it matters>
```

Like an order: “Add…”, “Fix…”, “Update…”, “Remove…”

Optional Conventional Commits style (nice for teams):

```
feat: add user invite endpoint
fix: correct CORS origin for staging
docs: explain reverse proxy headers
chore: bump node to 20 in Dockerfile
```

---

## Quick Cheatsheet

| Need | Command |
|------|---------|
| Who am I? | `git config user.name` |
| New repo | `git init` |
| Copy remote repo | `git clone <url>` |
| What’s going on? | `git status` |
| Stage file | `git add <file>` |
| Commit | `git commit -m "msg"` |
| Unstaged diff | `git diff` |
| Staged diff | `git diff --staged` |
| History | `git log --oneline` |
| Unstage | `git restore --staged <file>` |
| Discard edits | `git restore <file>` |

---

## Next

You can save snapshots alone. Next: work on features safely with branches → **[3.2-git_branching.md](./3.2-git_branching.md)**
