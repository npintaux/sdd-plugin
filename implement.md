---
name: implement
description: Implement a unit of work from SPEC.md using TDD, object-oriented Python and docstrings — derive the tests from the acceptance criteria first, then write code until green. Use whenever turning a user story or a SPEC.md change into code (e.g. "/implement R4", "implement the contractor rule", "build the next cycle"). This is the single entry point for writing code in this repo.
---

# /implement

Turn an item of intent (an acceptance criterion in `SPEC.md`, itself derived from a Jira story) into tested, object-oriented Python — in one command. The method is non-negotiable; the gates enforce it.

## When to use
- A new or changed acceptance criterion exists in `SPEC.md`.
- You are starting a cycle, or adding/altering a rule in the approval engine.

## Preconditions
- The target behavior is written in `SPEC.md`. If it is missing or ambiguous, **stop and ask** — do not invent scope.
- `SPEC.md` is the source of truth. A Jira story is intake only.

## Procedure
1. **Read the acceptance criteria** for the target item from `SPEC.md`. Restate them as a short checklist.
2. **Write the tests first (red).** One test per criterion. Assert the `outcome` **and** the `rule_ids` where a rule is involved (e.g. `evaluate(amount=50, category="office", requester_tier="contractor")` → `REVIEW`, `["R4"]`).
3. **Implement object-oriented, Pythonic code:**
   - `dataclasses` for data (`Request`, `Decision`); make them frozen where natural.
   - a `Rule` interface via `typing.Protocol` (or ABC); **one rule class per file**.
   - **composition over inheritance** — the engine holds an ordered list of rules; precedence = list order.
   - full type hints; pure functions (no I/O, no network, deterministic).
4. **Docstrings** on every public module, class and function.
5. **Run to green** — implement until the derived tests pass; refactor while keeping green.
6. **Confirm the gates pass** (see below).

## Conventions (always)
- Python 3.13, one class per file, complete docstrings, explicit type hints.
- No deep inheritance trees; prefer dataclasses + Protocol + composition.
- Determinism: same input → same output; the only time-dependent value is the recorded `evaluated_at`.

## Gates (enforced by hooks — this skill only reminds)
- `pylint` — zero violations on the agreed ruleset (includes missing-docstring).
- `pytest` — all tests green.
- coverage ≥ 90 % (this pure engine naturally approaches 100 %).

## Definition of done
Tests derived from the acceptance criteria, all green; gates pass; code is OO and documented; no behavior exists that is not pinned by a test.

## Example invocation
`/implement APPR-124`  → implements the "contractor → REVIEW" rule (R4), tests first.

> Note: a skill **guides** the method; it cannot **guarantee** it. The guarantee is the hook layer. Confirm your platform's exact `SKILL.md` frontmatter and `.agents/` layout against the current Antigravity docs.
