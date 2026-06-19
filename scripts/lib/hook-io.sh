#!/bin/bash
# Shared helpers for Antigravity tool hooks.
#
# Antigravity's hook contract (confirmed against the working secops-iac-gate plugin):
#   • INPUT : the tool call arrives as a JSON object on STDIN.
#   • OUTPUT: the hook prints a JSON *decision* on STDOUT:
#               {"decision":"allow"|"deny","reason":"..."}
#   • A hook ALWAYS exits 0. Blocking is done by the "deny" decision — NOT by the
#     exit code (a non-zero exit is ignored).
#
# We use `jq` to BUILD that JSON so the reason is always correctly escaped, even when
# it contains quotes or newlines. Source this file, then call hook_allow / hook_deny.

# Emit "allow" and stop. The tool call proceeds untouched. $1 = optional reason.
hook_allow() {
  jq -cn --arg r "${1:-}" '{decision: "allow", reason: $r}'
  exit 0
}

# Emit "deny" and stop. Antigravity blocks the tool call and surfaces $1 to the agent.
hook_deny() {
  jq -cn --arg r "$1" '{decision: "deny", reason: $r}'
  exit 0
}
