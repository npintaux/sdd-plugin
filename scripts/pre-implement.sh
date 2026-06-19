#!/bin/bash
set -e

# pre-implement hook
#
# Wired to UserPromptExpansion (matcher: implement), so it fires when /implement is
# typed — BEFORE any code is written. It enforces the harness's required-files
# contract: a project using /implement must provide the contract (SPEC.md) and the
# layout convention (its prose + machine forms). Symmetric to pre-specify.
#
# This is the "enforce a specific set of files present" gate: the plugin stays
# project-independent by depending only on these declared slots; this hook checks the
# project actually fills them.

echo "Running pre-implement hooks..."

# Git repository guard.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Error: Not inside a git repository. The SDD workflow requires a git repository."
  exit 1
fi

missing=0
require() {
  if [[ ! -f "$1" ]]; then
    echo "❌ Error: required file '$1' is missing. $2"
    missing=$((missing + 1))
  fi
}

# The contract /implement obeys.
require "SPEC.md" "Run /specify first — /implement reads only SPEC.md, never the issue."

# The layout convention: prose (for the agent) + machine twin (for the hooks).
require ".agents/conventions/code-layout.md" "Scaffold it from the plugin's code-layout.template.md — it tells /implement where code goes."
require ".agents/conventions/code-layout.env" "Scaffold it from the plugin's code-layout.env.template — the post-implement hook reads it to enforce the layout."

if [[ "$missing" -gt 0 ]]; then
  echo "pre-implement: $missing required file(s) missing — the project does not satisfy the harness contract."
  exit 1
fi

echo "✅ Pre-implement contract satisfied (SPEC.md + code-layout.md + code-layout.env present)."
exit 0
