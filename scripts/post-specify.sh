#!/bin/bash
set -e

# post-specify hook
#
# Wired to PostToolUse (run_command), so it fires after *every* shell command,
# not just /specify's commit. It therefore SELF-SKIPS (exit 0, silently) unless
# it detects the /specify commit context — defined as: the most recent commit
# modified SPEC.md. Only then does it enforce the invariant that spec changes
# land on a conforming issue/ branch. Success is silent; the hook speaks only
# when a SPEC.md commit landed somewhere it shouldn't have.

# --- Skip conditions (not our context) -------------------------------------

# Not inside a git repository — nothing to validate.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# No commits yet — `git show HEAD` would fail.
if ! git rev-parse HEAD >/dev/null 2>&1; then
  exit 0
fi

# Relevance gate: only act when the last commit modified SPEC.md (exact path,
# repo root). Any other command/commit is not the /specify context — skip.
last_commit_files=$(git show --name-only --format="" HEAD)
if ! echo "$last_commit_files" | grep -Fqx "SPEC.md"; then
  exit 0
fi

# --- Enforcement (a SPEC.md commit just happened) --------------------------

current_branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  echo "❌ Error: SPEC.md was committed on '$current_branch'. Spec changes must land on a feature branch created by /specify, not on the default branch."
  exit 1
fi

if [[ ! "$current_branch" =~ ^issue/[0-9]+-[a-z0-9-]+$ ]]; then
  echo "❌ Error: SPEC.md was committed on '$current_branch', which does not conform to the taxonomy 'issue/<number>-<short-kebab-case-title>' (e.g. issue/124-contractor-review)."
  exit 1
fi

# Conforming SPEC.md commit on a feature branch — pass silently.
exit 0
