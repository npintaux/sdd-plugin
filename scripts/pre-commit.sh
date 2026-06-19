#!/bin/bash
set -e

# pre-commit hook
#
# Wired to UserPromptExpansion (matcher: commit), so it fires when /commit is
# typed — BEFORE any commit is produced. It is the precondition gate symmetric to
# pre-specify: it refuses to let a commit be prepared in the wrong place.
#
# It is NOT the quality gate. The deterministic quality gates (pylint, pytest,
# coverage, Trivy) and the human-approval backstop (the harness's tool-approval on
# `git commit`) are separate layers. This hook only checks the cheap, structural
# preconditions that must hold before /commit makes sense.

echo "Running pre-commit hooks..."

# 1. Git repository guard.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Error: Not inside a git repository."
  exit 1
fi

# 2. Branch taxonomy: a /commit lands work on the issue/<n>-<title> branch that
#    /specify created — never on the default branch.
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  echo "❌ Error: You are on '$current_branch'. Work (spec + code) lands on the issue/<n>-<title> branch /specify created, not the default branch. Run /specify first, or check out the issue branch."
  exit 1
fi
if [[ ! "$current_branch" =~ ^issue/[0-9]+-[a-z0-9-]+$ ]]; then
  echo "❌ Error: Branch '$current_branch' does not match 'issue/<number>-<short-kebab-case-title>' (e.g. issue/1-take-an-order)."
  exit 1
fi

# 3. There must be something to commit.
if [[ -z $(git status --porcelain) ]]; then
  echo "❌ Error: Working tree is clean — nothing to commit."
  exit 1
fi

# 4. A code/spec commit needs a contract. Warn (don't block) if SPEC.md is absent;
#    /specify is what creates it, and a first /commit may predate code.
if [[ ! -f "SPEC.md" ]]; then
  echo "⚠️  Warning: SPEC.md not found at the repo root. Code should implement a contract — confirm this commit is intended."
fi

echo "✅ Pre-commit preconditions passed on '$current_branch'."
echo "   Reminder: this is not approval. Commit only what the user reviewed; the gates (pylint/pytest/coverage/Trivy) and the harness commit-approval still apply."
exit 0
