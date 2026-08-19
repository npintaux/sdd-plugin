---
name: commit
description: Write and stage a conventional commit message linked to the GitHub Issue and rule(s) implemented for end-to-end traceability (issue ↔ commit ↔ rule). Use when staging a completed, green, reviewed change ("commit this", "/commit", "write a commit message", "commit rule R3"). Pre-commit hooks enforce gates; this skill produces the traceable message. Do not use for opening PRs or closing entire issues (use ship) or during active coding before review (use implement).
---

# /commit

Produce a traceable commit message and commit the change. The discipline: every commit links to the **GitHub Issue** it advances and the **rule** it implements, so an auditor can walk issue → commit → rule → runtime `rule_ids`.

## When to use
- A single rule implementation or unit of work is complete, reviewed, green, and ready to stage.
- Writing conventional commit messages with explicit issue and rule ID tags.
- Invoking the traceable commit step after `/implement` review approval.

## When NOT to use
- Actively implementing or debugging rules before human review (use `/implement`).
- Opening a pull request, watching CI, or merging the whole issue (use `/ship`).
- Translating issues into specifications before coding begins (use `/specify`).
- Advisory review of code architecture and design (use `/code-review`).

## Preconditions
- Gates will run on commit (pre-commit hook: `pylint`, `pytest`, `Trivy`). If they fail, the commit is blocked — fix first; this skill does not bypass them.
- You are on the dedicated `issue/<n>-<title>` branch, never on `main`.
- The human has explicitly reviewed and approved the change.

## Message format
```
type(scope): summary [Rn] (#xxx)

<optional body: what & why, not how>
```
- **type**: conventional commits — `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
- **scope**: the area, e.g. `rules`, `engine`, `schema`.
- **summary**: imperative, ≤ 50 characters.
- **[Rn]**: the rule(s) implemented or changed, e.g. `[R4]`. Omit if no rule applies.
- **(#xxx)**: the GitHub Issue number, for automatic linking.

## Procedure
1. **Confirm readiness and branch**: Ensure current branch is `issue/<n>-<title>` and human approval has been given.
2. **Verify gates pass**: Confirm pylint, pytest (coverage >= 90%), and security scans pass.
3. **Identify traceability tags**: Identify the GitHub Issue number `n` and the rule(s) `[Rn]` touched.
4. **Draft and format the commit message**: Compose the subject line matching `type(scope): summary [Rn] (#n)`; add a short body if the rationale requires explanation.
5. **Stage and commit**: Stage the relevant changed files and execute `git commit -m "..."`.

## Examples
```
feat(rules): contractor requests always REVIEW [R4] (#124)
feat(schema): Decision carries policy_version + evaluated_at (#126)
fix(rules): raise office auto-approve ceiling to 250 [R1] (#125)
test(engine): add edge-case test for concurrent requests [R2] (#120)
```

## Guardrails
- **Never commit unreviewed or red code.** All tests and linter gates must be green.
- **Never commit directly to `main` or `master`.** SDD commits must land on an issue branch.
- **Always tag rule ID and issue number.** Preserving end-to-end traceability is mandatory.

## Common Rationalizations
| The excuse | The reality |
|---|---|
| "I'll commit directly on main since it's a small fix." | SDD commit-gate denies commits on main; always work on an `issue/<n>-<title>` branch. |
| "I'll omit `[Rn]` because it's obvious from the diff." | Rule IDs in commit subjects are required for auditability (issue ↔ commit ↔ rule). |
| "I'll bypass failing linter or test checks with `--no-verify`." | Gates exist to guarantee codebase health; fix violations before committing. |
| "I'll combine committing and merging into one step." | `/commit` runs per-rule on the issue branch; `/ship` runs once at the end to open PR and merge. |

## Verification
Before completing the commit, you MUST verify:
- [ ] You confirmed the current branch matches `issue/<n>-<title>` (not `main` or `master`).
- [ ] All pre-commit checks (pylint, pytest, Trivy) pass green.
- [ ] The commit message format follows `type(scope): summary [Rn] (#xxx)` (<= 50 char subject).
- [ ] The rule ID `[Rn]` matches the actual rule in `SPEC.md` and the issue number `(#n)` matches the branch issue.
- [ ] Only files belonging to the approved unit of work are staged and committed.
- [ ] You did not push, open a PR, or merge (those belong to `/ship`).

## Definition of done
A conventional message that names the rule and the issue; gates green; history is auditable.

> Note: traceability convention tuned to a rules engine. Confirm the exact Antigravity skill/hook schema against the current docs.
