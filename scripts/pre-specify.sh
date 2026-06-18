#!/bin/bash
set -e

echo "Running pre-specify hooks..."

# 1. Git repository guard
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Error: Not inside a git repository. The SDD workflow requires a git repository."
  exit 1
fi

# 2. spec-exists check (non-fatal warning to allow first-story bootstrapping)
if [[ ! -f "SPEC.md" ]]; then
  echo "⚠️  Warning: SPEC.md not found in the root of the repository."
  echo "    Entering first-story bootstrap mode; the /specify skill will scaffold it."
fi

# 3. git-status-clean check (ignoring untracked files for true greenfield environments)
if [[ -n $(git status --porcelain --untracked-files=no) ]]; then
  echo "❌ Error: Working directory has uncommitted tracked changes. Commit or stash changes first."
  exit 1
fi

# 4. default-branch check (verifies branch name, not sync state)
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
  echo "⚠️  Warning: Not on main or master branch. You are on '$current_branch'."
fi

echo "✅ Pre-specify hooks passed. Ready to specify."
exit 0
