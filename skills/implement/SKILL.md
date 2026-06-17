---
name: implement
description: Implement a unit of work from SPEC.md using TDD, object-oriented Python and docstrings — derive the tests from the acceptance criteria first, then write code until green. Query the GCP Developer Knowledge MCP server for context on GCP APIs and architectural best practices. Use whenever turning a user story or a SPEC.md change into code (e.g. "/implement R4", "implement the contractor rule", "build the next cycle"). This is the single entry point for writing code in this repo.
---

# /implement

Turn an item of intent (an acceptance criterion in `SPEC.md`, itself derived from a GitHub Issue) into tested, object-oriented Python — in one command. The method is non-negotiable; the gates enforce it.

## When to use
- A new or changed acceptance criterion exists in `SPEC.md`.
- You are starting a cycle, or adding/altering a rule in the approval engine.

## Preconditions
- The target behavior is written in `SPEC.md`. If it is missing or ambiguous, **stop and ask** — do not invent scope.
- `SPEC.md` is the source of truth. A GitHub Issue is intake only.

## Tools
- **GCP Developer Knowledge MCP server**: Use this resource to query best practices, reference architectures, and API documentation for Google Cloud when building infrastructure-as-code or integrating with GCP services.

## Procedure
1. **Read the acceptance criteria** for the target item from `SPEC.md`. Restate them as a short checklist.
2. **Consult GCP Documentation**: If the implementation involves Google Cloud resources or APIs, query the GCP Developer Knowledge MCP server to ensure best practices are followed.
3. **Write the tests first (red).** One test per criterion. Assert the `outcome` **and** the `rule_ids` where a rule is involved (e.g. `evaluate(amount=50, category="office", requester_tier="contractor")` → `REVIEW`, `["R4"]`).
4. **Implement object-oriented, Pythonic code:**
   - `dataclasses` for data (`Request`, `Decision`); make them frozen where natural.
   - a `Rule` interface via `typing.Protocol` (or ABC); **one rule class per file**.
   - **composition over inheritance** — the engine holds an ordered list of rules; precedence = list order.
   - full type hints; pure functions (no I/O, no network, deterministic).
5. **Docstrings** on every public module, class and function.
6. **Run to green** — implement until the derived tests pass; refactor while keeping green.
7. **Confirm the gates pass** (see below).

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
`/implement #124`  → implements the "contractor → REVIEW" rule (R4), tests first.

> Note: a skill **guides** the method; it cannot **guarantee** it. The guarantee is the hook layer. Confirm your platform's exact `SKILL.md` frontmatter and `.agents/` layout against the current Antigravity docs.
