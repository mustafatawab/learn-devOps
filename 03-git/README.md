# 03 — Git & GitHub

Version control from zero to hero — for DevOps engineers who need clean history, safe collaboration, and CI/CD that starts from Git events.

---

## Learning path

Files are numbered **3.1 → 3.4** so beginners know the exact order (module **03** = Git).

| Step | File | Focus |
|------|------|--------|
| 3.1 | [3.1-git_basics.md](./3.1-git_basics.md) | What Git is, setup, daily commit workflow |
| 3.2 | [3.2-git_branching.md](./3.2-git_branching.md) | Branches, merge, rebase, conflicts |
| 3.3 | [3.3-github.md](./3.3-github.md) | Remotes, PRs, Issues, team workflow on GitHub |
| 3.4 | [3.4-git_advanced.md](./3.4-git_advanced.md) | Undo/recover, stash, tags, pro DevOps habits |

---

## Why this matters in DevOps

```
Code change → Git commit → Push → GitHub
                              ↓
                     CI/CD pipeline runs
                              ↓
                     Build → Test → Deploy
```

Without solid Git skills you cannot:

- Review and ship safely with Pull Requests
- Roll back bad deploys with confidence
- Trigger and debug CI/CD pipelines
- Collaborate without overwriting teammates’ work

---

## Quick mental model

| Concept | Simple meaning |
|---------|----------------|
| **Git** | Tool on your machine that tracks file history |
| **GitHub** | Website/host that stores remote copies and adds PRs, Issues, Actions |
| **Commit** | A saved snapshot of your project |
| **Branch** | A movable label pointing at a commit (parallel line of work) |
| **Remote** | A copy of the repo on another machine (usually GitHub) |
| **PR** | Ask to merge your branch into another (with review) |

---

## Prerequisites

- Terminal basics ([01-linux](../01-linux/))
- A [GitHub](https://github.com) account

---

## After this module

Go to **[05-ci-cd](../05-ci-cd/)** — GitHub Actions builds on push/PR events you learn here.
