# 3.4 - Git Advanced

Recovery, cleanup, and pro workflows - the skills that separate “I use Git” from “I trust Git in production.”

---

## Table of Contents

1. [Stash](#stash)
2. [Undo & Recover (Decision Guide)](#undo--recover-decision-guide)
3. [Reset - Soft, Mixed, Hard](#reset--soft-mixed-hard)
4. [Revert (Safe for Shared History)](#revert-safe-for-shared-history)
5. [Reflog - Your Safety Net](#reflog--your-safety-net)
6. [Detached HEAD](#detached-head)
7. [Cherry-pick](#cherry-pick)
8. [Tags & Releases](#tags--releases)
9. [Interactive Rebase (Clean History)](#interactive-rebase-clean-history)
10. [Find Bugs: blame & bisect](#find-bugs-blame--bisect)
11. [Submodules (When & When Not)](#submodules-when--when-not)
12. [Signed Commits](#signed-commits)
13. [Hooks (Overview)](#hooks-overview)
14. [DevOps Habits & Danger Zone](#devops-habits--danger-zone)
15. [Disaster Cheatsheet](#disaster-cheatsheet)

---

## Stash

**Stash** temporarily shelves uncommitted work so you can switch branches cleanly.

```bash
git stash                  # stash tracked changes
git stash -u               # include untracked files
git stash list
git stash show -p          # see latest stash diff
git stash pop              # apply latest + remove from stash list
git stash apply            # apply but keep in stash list
git stash drop             # delete latest stash
git stash clear            # delete all stashes
```

Named stash:

```bash
git stash push -m "wip: nginx config"
```

> Stash is local only - it is **not** pushed to GitHub.

---

## Undo & Recover (Decision Guide)

Ask: **Has this commit been pushed / shared?**

| Situation | Prefer |
|-----------|--------|
| Unstaged edits, want to discard | `git restore file` |
| Staged, want to unstage | `git restore --staged file` |
| Last commit, not pushed, fix files/msg | `git commit --amend` |
| Remove commits from branch, **not pushed** | `git reset` |
| Undo a commit that **is on main / shared** | `git revert` |
| “I lost a commit somehow” | `git reflog` then recover |

```
Shared history (main, teammates)  →  revert (add new undo commit)
Only on your laptop / feature     →  reset / amend / rebase OK (with care)
```

---

## Reset - Soft, Mixed, Hard

**`git reset`** moves the current branch pointer (and optionally staging/working tree).

Assume history: `A ← B ← C` (HEAD = C)

```bash
git reset --soft HEAD~1     # back to B; keep changes staged
git reset --mixed HEAD~1    # back to B; keep changes unstaged (default)
git reset --hard HEAD~1     # back to B; DISCARD changes
```

| Mode | Branch moves | Staging | Working tree |
|------|--------------|---------|--------------|
| `--soft` | Yes | Keeps changes staged | Keeps files |
| `--mixed` | Yes | Unstages | Keeps files |
| `--hard` | Yes | Cleared | **Destroyed** to match commit |

Reset to a specific commit:

```bash
git reset --hard a1b2c3d
```

> **Danger:** `--hard` can delete uncommitted work permanently. Double-check `git status` first. Never hard-reset shared `main` unless the team agrees and you know the recovery plan.

---

## Revert (Safe for Shared History)

**`git revert`** creates a **new commit** that undoes an old commit’s changes. History stays intact.

```bash
git revert a1b2c3d
git revert HEAD              # undo last commit with a new commit
git revert -m 1 <merge_sha>  # revert a merge commit (pick parent)
```

Use this when the bad commit is already on `main` or deployed.

```
Bad commit C is on main:
A ← B ← C ← D
              ↓
A ← B ← C ← D ← R     (R undoes C)
```

---

## Reflog - Your Safety Net

**Reflog** records where HEAD pointed locally - even after reset/rebase “lost” commits.

```bash
git reflog
```

Example:

```
a1b2c3d HEAD@{0}: commit: Add auth
f9e8d7c HEAD@{1}: reset: moving to HEAD~1
b2c3d4e HEAD@{2}: commit: WIP nginx
```

Recover:

```bash
git switch -c recover-wip HEAD@{2}
# or
git reset --hard HEAD@{2}
```

> Reflog is **local** and expires eventually (default ~90 days). It won’t save what never committed and never stashed.

---

## Detached HEAD

You checked out a **commit** (or tag), not a branch name.

```bash
git checkout a1b2c3d
# or
git switch --detach a1b2c3d
```

You’re viewing history. New commits here can get “lost” if you switch away without a branch.

Fix - keep the work:

```bash
git switch -c hotfix-from-old-commit
```

Or just go back:

```bash
git switch main
```

---

## Cherry-pick

Copy **one commit** from another branch onto your current branch.

```bash
git switch main
git cherry-pick a1b2c3d
```

Useful for:

- Hotfix one commit without merging the whole feature branch  
- Moving a commit that landed on the wrong branch  

If conflicts happen: fix → `git add` → `git cherry-pick --continue`  
Or abort: `git cherry-pick --abort`

---

## Tags & Releases

**Tags** mark important points - usually versions.

```bash
git tag v1.0.0                        # lightweight
git tag -a v1.0.0 -m "Release 1.0.0"  # annotated (preferred)
git tag                               # list
git show v1.0.0
git push origin v1.0.0
git push origin --tags
```

Checkout a tag (detached HEAD):

```bash
git switch --detach v1.0.0
```

Delete:

```bash
git tag -d v1.0.0
git push origin --delete v1.0.0
```

On GitHub: **Releases** UI can create tags + release notes + binaries. Useful for deploy pins and changelogs.

Semantic versioning (common):

```
MAJOR.MINOR.PATCH   →  2.1.3
```

---

## Interactive Rebase (Clean History)

Rewrite recent local commits before sharing:

```bash
git rebase -i HEAD~3
```

Editor opens a todo list:

```
pick a111 aaa First
pick b222 bbb Second
pick c333 ccc Third
```

Common actions:

| Command | Meaning |
|---------|---------|
| `pick` | Keep commit |
| `reword` | Keep changes, edit message |
| `squash` | Combine into previous commit |
| `fixup` | Like squash, discard this message |
| `drop` | Remove commit |
| `edit` | Pause to amend |

> Only rewrite commits that exist on **your feature branch** and aren’t depended on by others. After a published rebase: `git push --force-with-lease`.

---

## Find Bugs: blame & bisect

**`git blame`** - Who last changed each line?

```bash
git blame path/to/file.py
git blame -L 20,40 path/to/file.py
```

**`git bisect`** - Binary search history to find the commit that introduced a bug.

```bash
git bisect start
git bisect bad                # current commit is bad
git bisect good v1.2.0        # known good tag/commit
# Git checks out a midpoint - test your app
git bisect good               # or: git bisect bad
# repeat until Git prints the first bad commit
git bisect reset
```

Huge time-saver on large histories.

---

## Submodules (When & When Not)

A **submodule** embeds another Git repo inside yours at a pinned commit.

```bash
git submodule add git@github.com:org/lib.git libs/lib
git submodule update --init --recursive
```

**Use when:** you truly need a separate repo pinned inside another (rare).

**Avoid when:** a package manager (npm, pip, Go modules) or monorepo is enough - submodules confuse clones and CI.

Prefer documenting “don’t use submodules unless you must.”

---

## Signed Commits

Prove commits came from you (some orgs require this).

```bash
# SSH signing (modern, simpler if you already use SSH keys)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Or GPG keys - add the public key in GitHub **SSH and GPG keys**. Verified badges appear on commits/PRs.

---

## Hooks (Overview)

Hooks are scripts Git runs on events (commit, push, etc.) in `.git/hooks/`.

Examples:

- `pre-commit` - lint / block secrets  
- `commit-msg` - enforce message format  
- `pre-push` - run tests  

Teams often use **Husky**, **pre-commit** (Python framework), or CI instead of relying only on local hooks (hooks aren’t committed by default unless you use a shared tool).

---

## DevOps Habits & Danger Zone

### Good habits

- Branch from latest `main`; open small PRs  
- Never commit secrets - use `.gitignore` + secret scanning  
- Prefer `revert` on shared branches  
- Use `--force-with-lease` instead of `--force`  
- Tag releases that get deployed  
- Read `git status` before every commit and push  

### Force push

```bash
git push --force-with-lease
```

Refuses to overwrite if remote has commits you don’t have (safer than `--force`).

**Never** force-push `main`/`master` on a team repo unless coordinated.

### Remove a tracked file but keep it locally

```bash
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Stop tracking .env"
```

If the secret was pushed: **rotate it** - history may still contain it until rewritten (advanced/filter tools) or treated as compromised.

### Large files

Don’t commit big binaries/videos. Use Git LFS if needed, or store artifacts in object storage / CI artifacts.

---

## Disaster Cheatsheet

| Problem | Fix |
|---------|-----|
| Committed to wrong branch | `cherry-pick` onto right branch; reset wrong branch if not shared |
| Need to undo last commit, keep edits | `git reset --soft HEAD~1` |
| Need to undo last commit, discard edits | `git reset --hard HEAD~1` (danger) |
| Bad commit already on main | `git revert <sha>` |
| Lost commit after reset | `git reflog` → `git reset --hard HEAD@{n}` |
| Merge gone wrong | `git merge --abort` |
| Rebase gone wrong | `git rebase --abort` |
| Detached HEAD with work | `git switch -c save-my-work` |
| Push rejected | `git pull --rebase` then `git push` |
| Accidentally committed `.env` | rotate secret + `git rm --cached` + `.gitignore` |
| Want clean PR history | `rebase -i` on feature branch, then force-with-lease |

---

## Quick Command Map

| Need | Command |
|------|---------|
| Shelf work | `git stash` / `git stash pop` |
| Soft undo commit | `git reset --soft HEAD~1` |
| Safe undo on main | `git revert <sha>` |
| Time machine | `git reflog` |
| Copy one commit | `git cherry-pick <sha>` |
| Version mark | `git tag -a v1.0.0 -m "msg"` |
| Clean last N commits | `git rebase -i HEAD~N` |
| Who wrote line | `git blame file` |
| Find breaking commit | `git bisect` |

---

## Module complete

You now have:

1. **Basics** - snapshots and daily workflow  
2. **Branching** - parallel work, merge/rebase, conflicts  
3. **GitHub** - remotes, PRs, protection, CI entry point  
4. **Advanced** - recover, clean history, ship safely  

Next learning step in the roadmap: **[04-containerization](../04-containerization/)** or jump to **[05-ci-cd](../05-ci-cd/)** to connect Git events to pipelines.
