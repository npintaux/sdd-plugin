#!/bin/bash
# Gate for the /specify "cut" step (creating an issue/<n>-<title> branch).
# Guarantees the issue branch is cut from a clean, up-to-date default branch.
# Invoked by pre-tool-use.sh with $1 = the directory the git command runs in.
#
# Fails OPEN on anything it can't evaluate, so it never blocks unrelated work.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../lib/hook-io.sh"

cwd="${1:-$PWD}"
root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)" || hook_allow "not a git repository"
cd "$root" || hook_allow "cannot enter repo root"

problems=()

# 1. You must cut the issue branch from the default branch.
branch="$(git branch --show-current)"
if [[ "$branch" != "main" && "$branch" != "master" ]]; then
  problems+=("you are on '$branch'. /specify must cut the issue branch from 'main' — run 'git checkout main' first.")
fi

# 2. No uncommitted TRACKED changes. Untracked files (e.g. the drafted SPEC.md that
#    /specify carries onto the new branch) are fine and intentionally ignored.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  problems+=("'$branch' has uncommitted tracked changes — commit or stash them before starting /specify.")
fi

# 3. The default branch must be in sync with its upstream (origin). We do a
#    best-effort fetch so the comparison is honest; never blocks on network/auth.
GIT_TERMINAL_PROMPT=0 timeout 15 git fetch --quiet origin "$branch" 2>/dev/null || true
upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
if [[ -n "$upstream" ]]; then
  behind="$(git rev-list --count "HEAD..$upstream" 2>/dev/null || echo 0)"
  ahead="$(git rev-list --count "$upstream..HEAD" 2>/dev/null || echo 0)"
  if ((behind > 0)); then
    problems+=("'$branch' is $behind commit(s) behind $upstream — run 'git pull' so the issue branch starts from the latest.")
  fi
  if ((ahead > 0)); then
    problems+=("'$branch' is $ahead commit(s) ahead of $upstream — push '$branch' before starting so it is in sync.")
  fi
fi
# (No upstream configured -> we cannot verify sync, so we skip that check: fail open.)

if ((${#problems[@]} > 0)); then
  reason="/specify blocked by the SDD gate (start from a clean, up-to-date main):"
  for p in "${problems[@]}"; do reason+=$'\n  - '"$p"; done
  hook_deny "$reason"
fi

hook_allow "SDD gate: cutting the issue branch from an up-to-date '$branch'."
