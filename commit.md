---
name: commit
description: Write a conventional commit message linked to the Jira story key and the rule(s) implemented, for end-to-end traceability (story ↔ commit ↔ rule). Use when staging a completed, green change ("commit this", "/commit", "write a commit message"). The pre-commit hook (pylint, pytest, Trivy) is what blocks; this skill produces the message.
---

# /commit

Produce a traceable commit message. The discipline: every commit links to the **Jira story** it advances and the **rule** it implements, so an auditor can walk story → commit → rule → runtime `rule_ids`.

## When to use
- A change is complete and green and ready to stage.

## Preconditions
- Gates will run on commit (pre-commit hook: `pylint`, `pytest`, `Trivy`). If they fail, the commit is blocked — fix first; this skill does not bypass them.

## Message format
```
type(scope): summary [Rn] (APPR-xxx)

<optional body: what & why, not how>
```
- **type**: conventional commits — `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
- **scope**: the area, e.g. `rules`, `engine`, `schema`.
- **summary**: imperative, ≤ 50 characters.
- **[Rn]**: the rule(s) implemented or changed, e.g. `[R4]`. Omit if no rule applies.
- **(APPR-xxx)**: the Jira story key, for automatic linking.

## Procedure
1. Confirm the change is green (gates).
2. Identify the Jira story key and the rule(s) touched.
3. Write the subject line in the format above; add a one-line body if the *why* isn't obvious.

## Examples
```
feat(rules): contractor requests always REVIEW [R4] (APPR-124)
feat(schema): Decision carries policy_version + evaluated_at (APPR-126)
fix(rules): raise office auto-approve ceiling to 250 [R1] (APPR-125)
```

## Definition of done
A conventional message that names the rule and the story; gates green; history is auditable.

> Note: traceability convention tuned to a rules engine. Confirm the exact Antigravity skill/hook schema against the current docs.
