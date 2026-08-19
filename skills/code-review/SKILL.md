---
name: code-review
description: Review a change for object-oriented design quality, Rule ABC inheritance, engine composition, conventions, and test adequacy before it is committed. Advisory — flags issues and suggests concrete fixes with prioritized severity. Use when asked to review changes, check code quality, look over a diff, or audit design before committing or opening a PR ("/code-review", "review this diff", "check my code", "audit our engine implementation"). Do not use for automated commit gating or executing implementation changes.
---

# /code-review

A structured second pass over a change. Advisory by design: it raises issues and proposes concrete fixes, but it is **not** a gate — the deterministic gates (pylint, pytest, coverage, Trivy) are what block.

## When to use
- Before `/commit`, or before opening a PR.
- When asked to review a diff, a file, a rule, or an iteration's output.
- Auditing object-oriented design, Rule ABC compliance, engine composition, and test adequacy.

## When NOT to use
- Enforcing deterministic pre-commit gates in hooks (automated gate's responsibility).
- Writing or refactoring implementation code directly (use `/implement`).
- Creating or editing the specification in `SPEC.md` (use `/specify`).
- Staging and committing changes to git (use `/commit`).

## Procedure
1. **Inspect the changes**: Examine the diff or target files, comparing against `SPEC.md` and `.agents/conventions/code-layout.md`.
2. **Evaluate OO design & contracts**:
   - Check that domain models use `dataclasses` (frozen where appropriate).
   - Confirm each rule subclasses the `Rule` ABC and implements `@abstractmethod`.
   - Verify single-responsibility (one rule class per file).
   - Verify engine composition: rule instance is registered in the `engine.py` ordered list at SPEC precedence (no orphan rules).
   - Check for clean architecture: pure core, no I/O or side-effects in decision logic.
3. **Evaluate conventions & linting**:
   - Verify complete docstrings on public modules, classes, and functions.
   - Verify explicit type hints and Python idioms.
   - Ensure no per-file `# pylint: disable=too-few-public-methods` exists (must be centrally configured in `pyproject.toml`).
4. **Evaluate test adequacy**:
   - Verify tests pin acceptance criteria, asserting both `outcome` and `rule_ids`.
   - Verify both unit tests and engine-level entry-point tests exist.
   - Check coverage of precedence and edge cases.
5. **Format prioritized review output**:
   - Group findings by severity: Critical/Blocking concerns, Recommended Improvements, and Nits.
   - Quote relevant file paths and line ranges, and provide drop-in code suggestions.

## Review checklist
**Design (OO)**
- Data modeled with `dataclasses`; each rule is a class **subclassing the `Rule` ABC** (`@abstractmethod`); composition (the engine's ordered list), not inheritance.
- One rule class per file; clear single responsibility. **No orphan rules** — every rule is registered in the engine's ordered list at the SPEC's precedence, and an engine-level test drives it through the entry point.
- No god-objects, no needless abstraction. Small single-method rule classes are intentional — they must not carry per-file `# pylint: disable=too-few-public-methods` (the project configures it once).

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

## Common Rationalizations
| The excuse | The reality |
|---|---|
| "The tests are green, so no review is needed." | Passing tests do not guarantee OO design, docstring quality, or lack of orphan rules. |
| "A Protocol is fine instead of Rule ABC." | `Rule` must subclass `abc.ABC` to guarantee contract enforcement at instantiation time. |
| "I'll fix the code directly during review." | `/code-review` is advisory analysis; code edits belong to `/implement`. |
| "It's fine to disable pylint in this one rule file." | Single-method rule classes are intentional; disable `too-few-public-methods` once centrally in `pyproject.toml`. |

## Verification
Before delivering the review, you MUST verify:
- [ ] You checked OO design: dataclasses for data, Rule ABC subclassing with `@abstractmethod`.
- [ ] You confirmed engine registration: rule instance is wired into `engine.py` at SPEC precedence (no orphan rules).
- [ ] You checked tests: verified criteria traceability, unit tests, and engine-level entry point tests.
- [ ] You checked docstrings, type hints, and cleanliness of public APIs.
- [ ] You confirmed no per-file pylint disables were introduced.
- [ ] You formatted the output as a prioritized list (blocking, improvements, nits) with actionable code suggestions.

## Examples
`/code-review` on `r4_contractor.py` and `test_r4_contractor.py`:
- Checks `ContractorRule` subclasses `Rule` ABC.
- Checks `engine.py` lists `ContractorRule()` ahead of default catch-all.
- Checks `test_evaluate_contractor_returns_review` asserts `outcome == Outcome.REVIEW` and `rule_ids == ["R4"]`.
- Outputs structured advisory report with line-specific recommendations.

> Note: advisory only. Real enforcement lives in the hooks. Confirm the exact Antigravity skill schema against the current docs.

