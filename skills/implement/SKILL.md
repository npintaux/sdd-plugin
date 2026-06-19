---
name: implement
description: Implement one unit of work from SPEC.md using TDD, object-oriented Python and docstrings — derive the tests from the acceptance criteria first, then write code until green, following the project's layout convention. Stops for human review before any commit. Use whenever turning a single acceptance criterion or rule from SPEC.md into code (e.g. "/implement R2", "implement the next rule", "build US1's engine"). This is the single entry point for writing code in this repo.
---

# /implement

Turn **one** item of intent (an acceptance criterion in `SPEC.md`, itself derived from a GitHub Issue) into tested, object-oriented Python. The method is non-negotiable; the gates enforce it. **This skill writes and tests code — it does not commit, and it never advances to the next story on its own.**

## When to use
- A new or changed acceptance criterion exists in `SPEC.md`.
- You are starting a cycle, or adding/altering a single rule in the decision engine.

## Preconditions
- The target behavior is written in `SPEC.md`. If it is missing or ambiguous, **stop and ask** — do not invent scope.
- `SPEC.md` is the source of truth. A GitHub Issue is intake only.
- **Harness contract (required files).** This skill is project-independent: it depends only on a declared set of files every consuming project must provide, never on any specific project's paths. Those files are:
  - `SPEC.md` (repo root) — the behavior contract.
  - `.agents/conventions/code-layout.md` — the project's **layout convention** (where code goes: package, module split, one-rule-per-file, test location), read by you before creating files.
  - `.agents/conventions/code-layout.env` — the same invariants in machine form, read by the hooks.

  Read `code-layout.md` before creating any file so the structure is deterministic, not improvised. If these files are missing, **stop**: scaffold them from the plugin's templates (`templates/code-layout.template.md`, `templates/code-layout.env.template`) — do not invent an arrangement. The commit gate (`precommit_gate.py`) will **deny the eventual commit** if the contract is unmet, so provision it now.

## Scope discipline (one unit at a time)
- **One acceptance criterion / rule per invocation.** Do not batch the whole story, and do not pull in behavior from a *different* user story (e.g. do not add allergy fields while implementing "take an order" — that is a separate story).
- **Never auto-advance.** When the unit is green, you are done. Do not start the next criterion, the next rule, or the next story without a fresh, explicit instruction.

## Tools
- **GCP Developer Knowledge MCP server** *(only when relevant)*: when the work touches Google Cloud APIs or the ADK agent shell, query it for best practices and reference architectures. The pure decision core needs no I/O and no GCP — skip it there.

## Procedure
1. **Read the acceptance criteria** for the target item from `SPEC.md`. Restate them as a short checklist. Confirm the unit's scope — exactly which rule / criterion, nothing adjacent.
2. **Locate the files** per `.agents/conventions/code-layout.md` (which package, which module, which test file). Do not improvise paths.
3. **Write the tests first (red).** One test per criterion. Assert the `outcome` **and** the `rule_ids` where a rule decides (e.g. `take_order(order="latte")` → `ASK`, `["R2"]`). Trace each test to the criterion it pins, not to the implementation.
4. **Implement object-oriented, Pythonic code:**
   - `dataclasses` for data (`Request`/`Order`, `Decision`); make them frozen where natural.
   - a `Rule` interface via `typing.Protocol` (or ABC); **one rule class per file**, in the location the convention dictates.
   - **composition over inheritance** — the engine holds an ordered list of rules; precedence = list order.
   - full type hints; pure functions in the core (no I/O, no network, deterministic).
5. **Docstrings** on every public module, class and function.
6. **Run to green** — implement until the derived tests pass; refactor while keeping green.
7. **Confirm the gates pass** (see below).
8. **Request review (STOP).** Present: the diff (files added/changed), the test results (all green + coverage), and a one-line-per-rule summary of the behavior. **Stop execution and wait for explicit human approval.** Do **not** run `/commit`, stage, push, or touch issue state. If changes are requested, return to step 3.

## Conventions (always)
- Python 3.13, one class per file, complete docstrings, explicit type hints.
- No deep inheritance trees; prefer dataclasses + Protocol + composition.
- Determinism: same input → same output; the only time-dependent value is any recorded `evaluated_at`.
- File placement follows `.agents/conventions/code-layout.md` — the skill carries the *method*, the convention carries the *layout* (and `code-layout.env` lets the hooks enforce it).

## Gates (enforced by hooks — this skill only reminds)
- `pylint` — zero violations on the agreed ruleset (includes missing-docstring).
- `pytest` — all tests green.
- coverage ≥ 90 % (this pure engine naturally approaches 100 %).

## Definition of done
Tests derived from the acceptance criteria, all green; gates pass; code is OO and documented; placed per the layout convention; no behavior exists that is not pinned by a test — **and the change has been presented for review and is awaiting the user's decision to `/commit`.** Implementation is *not* "done" the moment tests go green; it is done when the human has seen it.

## Guardrails
- **No commit, ever, from this skill.** Committing is a separate, user-initiated `/commit` step that follows explicit approval.
- **One unit per invocation; never auto-advance** to another rule or story.
- **Never widen scope** beyond the single acceptance criterion in play.

## Example invocation
`/implement R2` → writes the failing test for the "missing size → ASK" rule, implements `r2_ask.py` in the location the convention dictates, runs to green, then **stops and presents the diff and test results for review** — it does not commit.

> Note: a skill **guides** the method; it cannot **guarantee** it. The guarantees are the hook layer (gates, branch/commit checks) and the harness permission on `git commit`. Confirm your platform's exact `SKILL.md` frontmatter and `.agents/` layout against the current docs.
