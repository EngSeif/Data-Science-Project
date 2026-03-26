# Git Flow Guide

A step-by-step guide for how we manage branches, commits, and keeping your work in sync with the team.

---

## 1. Start From a Clean Main

Before creating a new branch, make sure your local `main` is up to date:

```bash
git checkout main
git pull origin main
```

---

## 2. Create a New Branch

Branch off from the latest `main`:

```bash
git checkout -b <branch-name>
```

### Branch Naming Convention

| Type | Example |
|------|---------|
| New feature | `feature/added-nav-bar` |
| Bug fix | `fix/create-users-endpoint` |
| Cleanup / maintenance | `chore/removed-unnecessary-file` |

---

## 3. Do Your Work & Commit

As you finish portions of your work, stage and commit your changes:

```bash
git add .
git commit -m "feat(title): message"
```

### Commit Message Convention

```
feat(auth): add JWT token validation
fix(api): handle null response from users endpoint
chore(deps): remove unused lodash import
```

Use `feat` for new features, `fix` for bug fixes, and `chore` for non-functional changes like cleanup or config updates.

---

## 4. Stay in Sync With the Team

While you're working, teammates may merge PRs into `main`, making your branch's base outdated. Here's how to stay current:

**Fetch the latest changes from origin:**
```bash
git fetch origin
```

**Make sure you're on your feature branch, then rebase:**
```bash
git rebase origin/main
```

This moves the base of your branch to the latest commit on `main` — as if you had just created your branch right now. Your commits stay on top, cleanly applied.

---

## 5. Push Your Branch

Once you're done and your branch is rebased:

```bash
git push origin <branch-name>
```

If you've already pushed before rebasing, you may need to force push:
```bash
git push origin <branch-name> --force-with-lease
```

> `--force-with-lease` is safer than `--force` — it won't overwrite if someone else has pushed to the same branch.

---

## Quick Reference

```
main (up to date)
  │
  ├── git checkout -b feature/my-feature
  │       │
  │       ├── git add . && git commit -m "feat(...): ..."
  │       ├── git add . && git commit -m "feat(...): ..."
  │       │
  │       │   (teammate merges PR → main moves forward)
  │       │
  │       ├── git fetch origin
  │       ├── git rebase origin/main   ← rebases onto new tip
  │       │
  │       └── git push origin feature/my-feature
```

---

> 💡 **Tip:** All of this can be done through **VS Code's Source Control panel** — you don't need to use the terminal. The steps above are just to explain what's happening under the hood.
