---
name: code-review
description: Review a change for object-oriented design quality, conventions and test adequacy before it is committed. Advisory — it flags issues and suggests fixes, it does not block. Use when asked to "review", "check my code", "look over this change", or before opening a pull request.
---

# /code-review

A structured second pass over a change. Advisory by design: it raises issues and proposes fixes, but it is **not** a gate — the deterministic gates (pylint, pytest, coverage, Trivy) are what block.

## When to use
- Before `/commit`, or before opening a PR.
- When asked to review a diff, a file, or a cycle's output.

## Review checklist
**Design (OO)**
- Data modeled with `dataclasses`; behavior behind a `Rule` `Protocol`; composition, not inheritance.
- One class per file; clear single responsibility.
- No god-objects, no needless abstraction.

**Conventions**
- Complete docstrings on public modules/classes/functions.
- Explicit type hints; Python 3.13 idioms.
- Purity: no I/O, no network, no hidden state in the engine; deterministic.

**Tests**
- Each acceptance criterion has a test; tests **trace to the criteria**, not to the implementation.
- Tests assert `outcome` **and** `rule_ids` where a rule decides.
- Edge/precedence cases covered (e.g. contractor + small office → `R4`, not `R1`).

**Hygiene**
- No dead code, no commented-out blocks, no TODOs left silently.
- Names communicate intent; errors are explicit.

## Output
A short, prioritized list: blocking concerns first (even though this skill doesn't enforce), then improvements, then nits. Reference file and rule IDs. Suggest concrete edits.

## Definition of done
Reviewer has a clear, actionable list; nothing about correctness is left implicit.

> Note: advisory only. Real enforcement lives in the hooks. Confirm the exact Antigravity skill schema against the current docs.
