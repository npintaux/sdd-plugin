#!/bin/bash
set -e

echo "Running post-read-user-story hooks..."

# 1. branch-check
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  echo "❌ Error: Still on $current_branch branch. A new feature branch should have been created."
  exit 1
fi

# 2. spec-modified check
# Checks if SPEC.md was modified in the most recent commit
last_commit_files=$(git show --name-only --format="" HEAD)
if ! echo "$last_commit_files" | grep -q "SPEC.md"; then
  echo "❌ Error: SPEC.md was not modified in the last commit."
  echo "The agent must commit the proposed specification changes to SPEC.md."
  exit 1
fi

echo "✅ Post-hooks passed. SPEC.md updated on feature branch '$current_branch'."
exit 0
