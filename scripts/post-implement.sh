#!/bin/bash
set -e

# post-implement hook
#
# Wired to PostToolUse (run_command), so it fires after *every* shell command.
# It SELF-SKIPS (exit 0, silently) unless it detects a *code commit* — defined per
# the project's own layout contract (.agents/conventions/code-layout.env). Only then does
# it enforce the load-bearing layout invariants. Success is silent; the hook speaks
# only when something is wrong.
#
# The plugin knows NO project-specific path: every value comes from code-layout.env, which
# each consuming project provides. The skill ASKS for this layout (code-layout.md); this
# hook IMPOSES the parts that must hold.

# --- Skip conditions (not our context) -------------------------------------

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi
if ! git rev-parse HEAD >/dev/null 2>&1; then
  exit 0
fi

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

layout_env=".agents/conventions/code-layout.env"
last_commit_files=$(git show --name-only --format="" HEAD)

# Load the project's layout contract if present. Use a conservative default relevance
# gate (^src/) only to decide whether this is a code commit worth complaining about.
if [[ -f "$layout_env" ]]; then
  # shellcheck disable=SC1090
  source "$layout_env"
  # Relevance gate: act only when the last commit touched code, per the project's regex.
  code_path_regex="${CODE_PATH_REGEX:-^src/}"
  if ! echo "$last_commit_files" | grep -Eq "$code_path_regex"; then
    exit 0
  fi
else
  # No layout contract: we cannot know the project's code root, so any committed .py
  # file is treated as a code commit — and demands the missing contract.
  if ! echo "$last_commit_files" | grep -Eq '\.py$'; then
    exit 0
  fi
  echo "❌ Code was committed but $layout_env is missing. A project using this harness must declare its layout contract (scaffold it from the plugin's code-layout.env.template)."
  exit 1
fi

errors=0
fail() { echo "❌ $1"; errors=$((errors + 1)); }

# --- 1. Contract present ----------------------------------------------------
if [[ ! -f "SPEC.md" ]]; then
  fail "Code was committed but SPEC.md is missing at the repo root. Code must implement a contract — run /specify first."
fi

# --- 2. Code lands on an issue/ branch, not the default branch --------------
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  fail "Code was committed on '$current_branch'. Implementation must land on the issue/<n>-<title> branch created by /specify, not the default branch."
elif [[ ! "$current_branch" =~ ^issue/[0-9]+-[a-z0-9-]+$ ]]; then
  fail "Code was committed on '$current_branch', which does not match 'issue/<number>-<short-kebab-case-title>'."
fi

# --- 3 & 4. Rule files are well-named and each has a matching test ----------
if [[ -n "${RULES_DIR:-}" && -d "$RULES_DIR" ]]; then
  test_prefix="${TEST_FILE_PREFIX:-test_}"
  tests_dir="${TESTS_DIR:-tests}"
  rule_pattern="${RULE_FILE_PATTERN:-^r[0-9]+_[a-z0-9_]+\.py$}"
  skip_files=" ${RULES_SKIP_FILES:-__init__.py base.py} "
  while IFS= read -r rule_path; do
    rule_file=$(basename "$rule_path")
    [[ "$skip_files" == *" $rule_file "* ]] && continue
    if [[ ! "$rule_file" =~ $rule_pattern ]]; then
      fail "Rule file '$rule_path' must match $rule_pattern (see code-layout.md)."
      continue
    fi
    test_file="${tests_dir}/${test_prefix}${rule_file}"
    if [[ ! -f "$test_file" ]]; then
      fail "Rule '$rule_path' has no matching test '$test_file'. Every rule is pinned by a test (TDD)."
    fi
  done < <(find "$RULES_DIR" -maxdepth 1 -name '*.py')
fi

# --- 5. The pure core must not import the I/O shell -------------------------
if [[ -n "${PURE_DIR:-}" && -d "$PURE_DIR" && -n "${FORBIDDEN_IMPORT_REGEX:-}" ]]; then
  if grep -REn "$FORBIDDEN_IMPORT_REGEX" "$PURE_DIR" >/dev/null 2>&1; then
    fail "The pure core ($PURE_DIR) imports the I/O shell. The dependency points one way only: shell -> core. Keep the core pure and I/O-free."
  fi
fi

# --- Verdict ----------------------------------------------------------------
if [[ "$errors" -gt 0 ]]; then
  echo "post-implement: $errors layout violation(s). See .agents/conventions/code-layout.md."
  exit 1
fi

exit 0
