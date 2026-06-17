#!/bin/bash
set -e

echo "Running pre-read-user-story hooks..."

# 1. spec-exists check
if [[ ! -f "SPEC.md" ]]; then
  echo "❌ Error: SPEC.md not found in the root of the repository."
  echo "The Spec-Driven Development workflow requires a SPEC.md file."
  exit 1
fi

# 2. git-status-clean check
if [[ -n $(git status --porcelain) ]]; then
  echo "❌ Error: Working directory is not clean. Commit or stash changes first."
  exit 1
fi

# 3. main-branch-sync check
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
  echo "⚠️  Warning: Not on main or master branch. You are on '$current_branch'."
fi

echo "✅ Pre-hooks passed. Ready to read user story."
exit 0
