#!/bin/bash
# PreToolUse entry point — the single hook wired in hooks.json.
#
# Its only job is to READ the tool call and ROUTE it to the right gate. It contains
# no policy itself: each gate is a small, independently-testable script under gates/.
# To add a new pre-hook behavior: detect the action below and `exec` its gate.
set -u

# Resolve our own directory so sub-scripts are found no matter the caller's CWD.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/lib/hook-io.sh"

# --- 1. Read the JSON tool call from STDIN -----------------------------------
# jq extracts the three fields we route on. On any parse error jq prints nothing,
# the variables stay empty, and we fall through to "allow" — i.e. we FAIL OPEN:
# a bug in the hook must never block the user's normal work.
payload="$(cat)"
tool="$(jq -r '.toolCall.name // ""'            <<<"$payload" 2>/dev/null)"
cmd="$( jq -r '.toolCall.args.CommandLine // ""' <<<"$payload" 2>/dev/null)"
cwd="$( jq -r '.toolCall.args.Cwd // ""'         <<<"$payload" 2>/dev/null)"

# --- 2. We only ever gate shell commands; everything else passes -------------
[[ "$tool" == "run_command" ]] || hook_allow ""

# --- 3. Is this command a `git commit`? --------------------------------------
# True only when `commit` is the git SUBCOMMAND (first non-flag token after `git`,
# skipping `-C dir` / `-c key=val`), scanned across &&, ||, |, ; chains. This avoids
# false positives such as `git log --grep=commit`.
is_git_commit() {
  local segment; local -a toks; local n i j
  while IFS= read -r segment; do
    read -ra toks <<<"$segment"          # split on whitespace, no globbing
    n=${#toks[@]}
    for ((i = 0; i < n; i++)); do
      [[ "${toks[i]}" == "git" ]] || continue
      j=$((i + 1))
      while ((j < n)); do
        case "${toks[j]}" in
          -C|-c) j=$((j + 2)) ;;         # flag that takes a value
          -*)    j=$((j + 1)) ;;         # any other flag
          commit) return 0 ;;            # first real subcommand is `commit`
          *)     break ;;                # first real subcommand is something else
        esac
      done
    done
  done < <(printf '%s\n' "$1" | sed -E 's/&&|\|\||[|&;]/\n/g')
  return 1
}

# --- 4. Dispatch -------------------------------------------------------------
# `exec` hands over the process so the gate's STDOUT becomes the hook's STDOUT.
if is_git_commit "$cmd"; then
  exec bash "$HERE/gates/commit-gate.sh" "$cwd"
fi

# Not an action we gate.
hook_allow ""
