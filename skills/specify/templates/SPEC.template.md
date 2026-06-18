# Specification

> **Source of truth.** GitHub Issues are intake; this file is the contract the
> agent obeys. When the two disagree, this file (and its owners) decide.

## Overview

<One paragraph: what this system decides and for whom. For the approval engine:
"Given a `Request`, the engine returns a `Decision` (an `outcome` plus the
`rule_ids` that fired), evaluating rules in precedence order.">

## Domain model

- **Request** — the input. Fields: `<field: type — meaning>` (e.g. `amount: int`,
  `category: str`, `requester_tier: str`).
- **Decision** — the output. Fields: `outcome` (one of `<APPROVE | REVIEW | DENY>`),
  `rule_ids: list[str]` (the rules that determined the outcome), `evaluated_at`.

## Global constraints

Invariants that hold across **all** rules and are not themselves rules. These are
spec-level guarantees the implementation must honor (distinct from the `/implement`
method conventions, which are about *how* code is written). Examples:

- `<unit/format invariant — e.g. "all monetary amounts are integer USD cents">`
- `<evaluation invariant — e.g. "evaluation is deterministic: same Request → same Decision">`
- `<totality — e.g. "every Request yields exactly one outcome; the last rule is a catch-all">`

## Rules

Each rule has a **stable ID** (`R1`, `R2`, …). IDs are assigned **sequentially**
and are **never reused or renumbered** — the first rule in a freshly scaffolded
spec is `R1`, and once `R4` ships it stays `R4` even if an earlier rule is removed.
Replace the `R<n>` placeholder below with the concrete ID when you add a rule. A rule's behavior must be stated in testable terms (a
concrete input → expected `outcome` and `rule_ids`).

### R<n>: <short title>

- **Behavior:** <precise, testable statement — e.g. "A `contractor` requester on
  any `amount` yields `REVIEW`.">
- **Example:** `evaluate(amount=50, category="office", requester_tier="contractor")`
  → `REVIEW`, `["R<n>"]`
- **Precedence:** <which rules this overrides or defers to, if relevant>
- **Source:** issue #<number>

<Repeat one `### R<n>` block per rule.>

## Precedence order

Rules are evaluated as an **ordered list**; earlier entries win on conflict
(this mirrors the engine, where precedence = list order). List the canonical
order, highest priority first:

1. R<n> — <title>
2. ...

## Glossary

- **<term>** — <definition of any domain word used above>
