#!/bin/bash
# Gate for `git commit`: ALLOW the commit only if the SDD invariants hold, else DENY
# with a precise reason. Invoked by pre-tool-use.sh with:
#   $1 = the directory the git command was about to run in.
#
# It reads the project's own layout contract (.agents/conventions/code-layout.env), so
# this gate carries NO project-specific path of its own. It fails OPEN on anything it
# can't evaluate (e.g. not a git repo), so it never blocks unrelated work.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../lib/hook-io.sh"

cwd="${1:-$PWD}"

# Resolve the repository root from where the command runs.
root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)" || hook_allow "not a git repository"
cd "$root" || hook_allow "cannot enter repo root"

layout_md=".agents/conventions/code-layout.md"
layout_env=".agents/conventions/code-layout.env"

# If this repo does not use SDD (no SPEC.md and no code-layout contract), fail open so
# plugin authoring and non-SDD repositories are not blocked.
if [[ ! -f "SPEC.md" && ! -f "$layout_md" && ! -f "$layout_env" ]]; then
  hook_allow "non-SDD repository (no SPEC.md or code-layout conventions found)"
fi

problems=()   # collect every violation, so the agent sees them all at once

# --- 1. Branch: SDD work lands on issue/<n>-<title>, never the default branch --
branch="$(git branch --show-current)"
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  problems+=("on '$branch': SDD commits land on the issue/<n>-<title> branch /specify creates, not the default branch.")
elif [[ ! "$branch" =~ ^issue/[0-9]+-[a-z0-9-]+$ ]]; then
  problems+=("branch '$branch' does not match issue/<number>-<short-kebab-title>.")
fi

# --- 2. The behavior contract must exist -------------------------------------
[[ -f "SPEC.md" ]] || problems+=("SPEC.md missing at the repo root — run /specify first.")

# --- 2b. SPEC.md conforms to the canonical structure (forced for reproducibility) --
# The required sections are the H2 headings of SPEC.template.md (single source of
# truth), so authors derive content into a FIXED shape rather than inventing layout.
template="$HERE/../../skills/specify/templates/SPEC.template.md"
if [[ -f "SPEC.md" && -f "$template" ]]; then
  while IFS= read -r heading; do
    grep -Fxq "$heading" SPEC.md \
      || problems+=("SPEC.md is missing the required section '$heading' (the canonical structure in SPEC.template.md is mandatory).")
  done < <(grep -E '^## ' "$template")
fi

# --- 3. The layout contract (prose + machine twin) must exist ----------------
layout_md=".agents/conventions/code-layout.md"
layout_env=".agents/conventions/code-layout.env"
[[ -f "$layout_md" ]] || problems+=("$layout_md missing (the layout convention /implement obeys).")
if [[ -f "$layout_env" ]]; then
  # The twin is trusted, plugin-provided-shape KEY='value' data; sourcing loads the
  # project's RULES_DIR / patterns / PURE_DIR so the checks below carry no hard-coded path.
  # shellcheck disable=SC1090
  source "$layout_env"
else
  problems+=("$layout_env missing (the machine layout contract the gate reads).")
fi

# --- 4. Layout conformance (working tree), driven entirely by code-layout.env -
if [[ -n "${RULES_DIR:-}" && -d "$RULES_DIR" ]]; then
  pattern="${RULE_FILE_PATTERN:-^r[0-9]+_[a-z0-9_]+\.py$}"
  tests_dir="${TESTS_DIR:-tests}"
  prefix="${TEST_FILE_PREFIX:-test_}"
  skip=" ${RULES_SKIP_FILES:-__init__.py base.py} "
  for path in "$RULES_DIR"/*.py; do
    [[ -e "$path" ]] || continue                       # no rule files yet
    file="$(basename "$path")"
    [[ "$skip" == *" $file "* ]] && continue            # __init__.py / base.py
    if [[ ! "$file" =~ $pattern ]]; then
      problems+=("rule file '$RULES_DIR/$file' must match $pattern.")
      continue
    fi
    test_file="$tests_dir/$prefix$file"
    [[ -f "$test_file" ]] || problems+=("rule '$RULES_DIR/$file' has no matching test '$test_file' (every rule is pinned by a test).")
  done
fi

# --- 5. The pure core must not import the I/O shell --------------------------
if [[ -n "${PURE_DIR:-}" && -d "$PURE_DIR" && -n "${FORBIDDEN_IMPORT_REGEX:-}" ]]; then
  hit="$(grep -REl "$FORBIDDEN_IMPORT_REGEX" "$PURE_DIR" 2>/dev/null | head -n1)"
  [[ -z "$hit" ]] || problems+=("the pure core ($PURE_DIR) imports the I/O shell ($hit); the dependency points one way only: shell -> core.")
fi

# --- 6. Python virtual environment activation --------------------------------
if [[ -f "venv/bin/activate" ]]; then
  source venv/bin/activate
elif [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
fi

# --- 7. Run pylint -----------------------------------------------------------
if command -v pylint >/dev/null 2>&1; then
  py_files=()
  while IFS= read -r f; do
    [[ -f "$f" ]] && py_files+=("$f")
  done < <(git ls-files '*.py')

  if ((${#py_files[@]} > 0)); then
    echo "Running pylint on ${#py_files[@]} file(s)..." >&2
    pylint_output="$(pylint "${py_files[@]}" 2>&1)"
    pylint_exit_code=$?
    if ((pylint_exit_code != 0)); then
      problems+=("pylint violations found:
$pylint_output")
    fi
  fi
else
  problems+=("pylint executable not found (is the virtual environment activated and pylint installed?)")
fi

# --- 8. Run pytest (runs unit tests + coverage) -------------------------------
if command -v pytest >/dev/null 2>&1; then
  echo "Running pytest..." >&2
  pytest_output="$(pytest 2>&1)"
  pytest_exit_code=$?
  if ((pytest_exit_code != 0)); then
    has_tests=0
    if [[ -n "${TESTS_DIR:-}" && -d "$TESTS_DIR" ]]; then
      if find "$TESTS_DIR" -name "*.py" -print -quit | grep -q .; then
        has_tests=1
      fi
    fi

    if ((pytest_exit_code == 5 && has_tests == 0)); then
      echo "No tests found to run, skipping pytest gate." >&2
    else
      problems+=("pytest failed (exit code $pytest_exit_code):
$pytest_output")
    fi
  fi
else
  problems+=("pytest executable not found (is the virtual environment activated and pytest installed?)")
fi

# --- 9. Run Trivy security scan -----------------------------------------------
if command -v trivy >/dev/null 2>&1; then
  echo "Running Trivy security scan..." >&2
  trivy_output="$(trivy fs --exit-code 1 --severity HIGH,CRITICAL --scanners vuln,secret,misconfig --skip-db-update --skip-java-db-update --skip-version-check . 2>&1)"
  trivy_exit_code=$?
  if ((trivy_exit_code != 0)); then
    problems+=("Trivy security scan failed:
$trivy_output")
  fi
fi

# --- Verdict -----------------------------------------------------------------
if ((${#problems[@]} > 0)); then
  reason="Commit blocked by the SDD gate:"
  for p in "${problems[@]}"; do reason+=$'\n  - '"$p"; done
  reason+=$'\n\nFix these, then re-commit. See .agents/conventions/code-layout.md.'
  hook_deny "$reason"
fi

hook_allow "SDD gate: branch, contract, layout, linter, tests, and security scans OK."
