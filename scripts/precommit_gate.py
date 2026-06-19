#!/usr/bin/env python3
"""Deterministic commit gate for the SDD plugin (Antigravity PreToolUse).

Antigravity hook contract (mirrors the working secops-iac-gate reference):
- input  : JSON on stdin -> {"toolCall": {"name": "...", "args": {"CommandLine": "...", "Cwd": "..."}}}
- block  : print {"decision": "deny", "reason": "..."} to STDOUT (exit 0). NOT via exit code.
- allow  : print {"decision": "allow", "reason": "..."} to STDOUT (exit 0).

This single PreToolUse/run_command hook intercepts `git commit` and enforces the
SDD invariants *before* the commit happens — consolidating what used to be
pre-commit + post-specify + post-implement. It reads the project's layout contract
(.agents/conventions/code-layout.env) so it carries NO project-specific path itself.

It fails OPEN (allows) on its own errors, so a bug here never blocks normal work.
"""
import sys
import os
import re
import json
import subprocess


def respond(decision, reason=""):
    print(json.dumps({"decision": decision, "reason": reason}))
    sys.exit(0)


def allow(reason=""):
    respond("allow", reason)


def deny(reason):
    respond("deny", reason)


def git(cwd, *args):
    """Run a git command in cwd, returning the CompletedProcess."""
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def is_git_commit(cmd):
    """True iff cmd runs `git commit` (commit as the subcommand), across && / | chains.

    Avoids false positives like `git log --grep=commit` by treating `commit` as a
    subcommand only when it is the first non-flag token after `git` (skipping `-C dir`
    and `-c key=val`).
    """
    for segment in re.split(r"&&|\|\||[|&;]", cmd):
        tokens = segment.split()
        for i, tok in enumerate(tokens):
            if tok != "git":
                continue
            j = i + 1
            while j < len(tokens):
                nxt = tokens[j]
                if nxt in ("-C", "-c"):
                    j += 2
                    continue
                if nxt.startswith("-"):
                    j += 1
                    continue
                if nxt == "commit":
                    return True
                break
    return False


def read_env(path):
    """Parse a shell-style KEY='value' file into a dict (no shell execution)."""
    env = {}
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"([A-Z_][A-Z0-9_]*)=(.*)", line)
            if not m:
                continue
            val = m.group(2).strip()
            if val and val[0] in "'\"" and val[-1] == val[0]:
                val = val[1:-1]
            env[m.group(1)] = val
    return env


def has_forbidden_import(base, pattern):
    """Return the first file under base matching pattern, else None."""
    try:
        rx = re.compile(pattern)
    except re.error:
        return None
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8", errors="ignore") as fh:
                    for ln in fh:
                        if rx.search(ln):
                            return fp
            except OSError:
                continue
    return None


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except (ValueError, TypeError) as exc:
        allow(f"gate parse error, allowing: {exc}")

    call = data.get("toolCall", {})
    if call.get("name") != "run_command":
        allow()

    args = call.get("args", {})
    cmd = args.get("CommandLine", "") or ""
    cwd = args.get("Cwd") or os.getcwd()

    # Only gate an actual git commit. Everything else passes untouched.
    if not is_git_commit(cmd):
        allow()

    top = git(cwd, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        allow("not a git repository")
    root = top.stdout.strip()

    def at(rel):
        return os.path.join(root, rel)

    problems = []

    # 1. Branch: workflow commits land on issue/<n>-<title>, never the default branch.
    branch = git(root, "branch", "--show-current").stdout.strip()
    if branch in ("main", "master"):
        problems.append(
            f"on '{branch}': SDD commits land on the issue/<n>-<title> branch /specify "
            "creates, not the default branch."
        )
    elif not re.match(r"^issue/[0-9]+-[a-z0-9-]+$", branch):
        problems.append(f"branch '{branch}' does not match issue/<number>-<short-kebab-title>.")

    # 2. The behavior contract must exist.
    if not os.path.isfile(at("SPEC.md")):
        problems.append("SPEC.md missing at the repo root — run /specify first.")

    # 3. The layout contract (prose + machine twin) must exist.
    layout_md = ".agents/conventions/code-layout.md"
    layout_env = ".agents/conventions/code-layout.env"
    if not os.path.isfile(at(layout_md)):
        problems.append(f"{layout_md} missing (the layout convention /implement obeys).")
    env = {}
    if os.path.isfile(at(layout_env)):
        env = read_env(at(layout_env))
    else:
        problems.append(f"{layout_env} missing (the machine layout contract the gate reads).")

    # 4. Layout conformance (working tree), driven entirely by code-layout.env.
    rules_dir = env.get("RULES_DIR")
    if rules_dir and os.path.isdir(at(rules_dir)):
        rule_pat = env.get("RULE_FILE_PATTERN", r"^r[0-9]+_[a-z0-9_]+\.py$")
        skip = set((env.get("RULES_SKIP_FILES") or "__init__.py base.py").split())
        tests_dir = env.get("TESTS_DIR", "tests")
        prefix = env.get("TEST_FILE_PREFIX", "test_")
        for fn in sorted(os.listdir(at(rules_dir))):
            if not fn.endswith(".py") or fn in skip:
                continue
            if not re.match(rule_pat, fn):
                problems.append(f"rule file '{rules_dir}/{fn}' must match {rule_pat}.")
                continue
            test_rel = os.path.join(tests_dir, prefix + fn)
            if not os.path.isfile(at(test_rel)):
                problems.append(
                    f"rule '{rules_dir}/{fn}' has no matching test '{test_rel}' (every rule is pinned by a test)."
                )

    pure_dir = env.get("PURE_DIR")
    forbidden = env.get("FORBIDDEN_IMPORT_REGEX")
    if pure_dir and forbidden and os.path.isdir(at(pure_dir)):
        hit = has_forbidden_import(at(pure_dir), forbidden)
        if hit:
            problems.append(
                f"the pure core ({pure_dir}) imports the I/O shell ({os.path.relpath(hit, root)}); "
                "the dependency points one way only: shell -> core."
            )

    if problems:
        deny(
            "Commit blocked by the SDD gate:\n  - "
            + "\n  - ".join(problems)
            + "\n\nFix these, then re-commit. See .agents/conventions/code-layout.md."
        )

    allow("SDD gate: branch, contract and layout OK.")


if __name__ == "__main__":
    main()
