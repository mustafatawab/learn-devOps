# 3.2 - Git Branching

Branches let you build features, fix bugs, and experiment **without breaking `main`**. This is the core of real team and DevOps workflows.

---

## Table of Contents

1. [What is a Branch?](#what-is-a-branch)
2. [Create, Switch, List, Delete](#create-switch-list-delete)
3. [Feature Branch Workflow](#feature-branch-workflow)
4. [Merge](#merge)
5. [Fast-Forward vs Merge Commit](#fast-forward-vs-merge-commit)
6. [Rebase](#rebase)
7. [Merge vs Rebase](#merge-vs-rebase)
8. [Resolve Conflicts](#resolve-conflicts)
9. [Useful Branch Commands](#useful-branch-commands)
10. [Cheatsheet](#cheatsheet)

---

## What is a Branch?

A **branch** is a movable pointer (label) to a commit. It is **not** a full copy of all files.

```
main:     A ← B ← C
                   ↑
                 main, HEAD
```

Create a feature branch:

```
main:     A ← B ← C
                   ↑ main

feature:  A ← B ← C ← D ← E
                         ↑ feature, HEAD
```

You can switch branches anytime; Git updates your working files to match that branch’s tip.

> Analogy: `main` is the **official road**. A branch is a **side road** where you build something. When it’s ready, you join it back to the main road (merge/rebase).

Default branch name today is usually **`main`** (older repos used `master`).

---

## Create, Switch, List, Delete

### List branches

```bash
git branch            # local branches (* = current)
git branch -a         # local + remote-tracking
git branch -v         # with last commit
```

### Create a branch

```bash
git branch feature-login          # create only
git switch -c feature-login       # create AND switch (recommended)
git checkout -b feature-login     # older equivalent
```

**`git switch`** - Change branches (modern).  
**`git checkout -b`** - Older way; still common in docs.

### Switch branches

```bash
git switch main
git switch feature-login
```

If you have uncommitted changes that conflict with the other branch, Git will stop you - commit, stash, or discard first.

### Rename current branch

```bash
git branch -m new-name
```

### Delete a branch

```bash
git branch -d feature-login       # safe delete (merged only)
git branch -D feature-login       # force delete (even if not merged)
```

Delete remote branch:

```bash
git push origin --delete feature-login
```

---

## Feature Branch Workflow

The standard pattern for almost every team:

```bash
git switch main
git pull                        # get latest main
git switch -c feature/add-auth  # new branch from main

# ... edit files ...
git add .
git commit -m "Add JWT authentication"
git push -u origin feature/add-auth
```

Then open a **Pull Request** on GitHub (see [3.3-github.md](./3.3-github.md)) to merge into `main`.

Naming ideas:

```
feature/user-dashboard
fix/nginx-502
chore/bump-node-20
docs/git-basics
```

---

## Merge

**Merge** combines another branch into your current branch.

```bash
git switch main
git merge feature-login
```

Git finds a common ancestor and joins histories.

```
Before:
main:     A ← B ← C
feature:  A ← B ← C ← D ← E

After merge into main:
main:     A ← B ← C ← D ← E ← M
                              ↑ merge commit (sometimes)
```

---

## Fast-Forward vs Merge Commit

### Fast-forward

If `main` has no new commits since you branched, Git can just move the `main` pointer forward - **no merge commit**.

```
Before:  A ← B ← C          (main)
                   ← D ← E  (feature)

After:   A ← B ← C ← D ← E  (main, feature)
```

### Merge commit (no fast-forward)

If both sides moved, or you force a merge commit:

```bash
git merge --no-ff feature-login
```

Creates an explicit merge commit - useful to mark “this PR landed.”

Many teams use **PR merge on GitHub**, which creates merge commits (or squash/rebase options).

---

## Rebase

**Rebase** replays your commits **on top of** another branch, as if you started from the newer tip.

```bash
git switch feature-login
git fetch origin
git rebase origin/main
```

```
Before:
main:     A ← B ← C ← F
feature:  A ← B ← C ← D ← E

After rebase onto main:
main:     A ← B ← C ← F
feature:  A ← B ← C ← F ← D' ← E'
```

`D'` and `E'` are new commits with the same changes but new hashes.

### Why rebase?

- Cleaner, linear history
- Easier to read `git log --oneline --graph`

### Golden rule

> **Never rebase commits that are already shared** (pushed and used by others) unless the whole team agrees. Rebase rewrites history.

If you already pushed and then rebase:

```bash
git push --force-with-lease
```

Use `--force-with-lease` (safer) - **not** bare `--force` - and **never** on `main`/`master` unless you really know why.

---

## Merge vs Rebase

| | Merge | Rebase |
|--|-------|--------|
| History | Keeps true branch topology | Linear, “as if” one line |
| Safety on shared branches | Safer default | Dangerous if already pushed |
| Conflicts | Resolve once in merge | May resolve per replayed commit |
| Common use | Merge PR into `main` | Update feature branch onto latest `main` |

**Practical DevOps habit:**

1. On your **feature branch**: rebase (or merge) latest `main` often  
2. Into **`main`**: merge via Pull Request (don’t rewrite `main`)

---

## Resolve Conflicts

A **conflict** means Git can’t automatically combine both sides’ edits to the same lines.

When it happens:

```bash
git status
# shows unmerged paths
```

Open the file - you’ll see markers:

```text
<<<<<<< HEAD
your current branch version
=======
incoming branch version
>>>>>>> feature-login
```

### Fix steps

1. Edit the file - keep the correct final code  
2. Remove all `<<<<<<<`, `=======`, `>>>>>>>` markers  
3. Stage the fixed file  
4. Continue

**During merge:**

```bash
git add conflicted-file.js
git commit                 # completes the merge (message pre-filled)
```

**During rebase:**

```bash
git add conflicted-file.js
git rebase --continue
```

Abort if overwhelmed:

```bash
git merge --abort
git rebase --abort
```

Tips to reduce conflicts:

- Pull/rebase `main` into your feature branch often  
- Keep PRs small  
- Don’t format-whack huge files in the same PR as logic changes  

---

## Useful Branch Commands

```bash
# show branches that contain a commit
git branch --contains a1b2c3d

# compare two branches
git log main..feature-login --oneline    # commits on feature not in main
git diff main...feature-login            # changes introduced on feature

# set upstream when first pushing a branch
git push -u origin feature-login

# update local view of remotes
git fetch origin
git remote prune origin                  # clean deleted remote branches
```

---

## Cheatsheet

| Need | Command |
|------|---------|
| List branches | `git branch` |
| New + switch | `git switch -c name` |
| Switch | `git switch name` |
| Merge into current | `git merge other-branch` |
| Rebase onto main | `git rebase main` |
| Abort merge | `git merge --abort` |
| Abort rebase | `git rebase --abort` |
| Delete local | `git branch -d name` |
| Delete remote | `git push origin --delete name` |

---

## Next

Branches locally are not enough for teams - push them and review with Pull Requests → **[3.3-github.md](./3.3-github.md)**
