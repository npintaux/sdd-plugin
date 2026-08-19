---
name: ship
description: Close out one GitHub Issue by opening a pull request from its issue branch, monitoring CI checks until green, squash-merging into main, deleting the remote/local branch, and pulling main up to date. Use once per issue when all acceptance criteria in SPEC.md are implemented, committed, and green ("/ship", "open PR and merge", "ship this issue", "close out ticket"). Do not use for per-rule commits (use commit) or while work is still in progress (use implement).
---

# /ship

Close out **one issue**. `/commit` runs many times per issue (once per reviewed rule); `/ship` runs **once**, at the end, when the whole issue is green: it opens a pull request from the issue branch, waits for the gates, merges, deletes the branch, and lets the merge close the issue.

**The human initiates; the machine then executes deterministically.** You run `/ship`; the skill opens the PR and — once CI is green — merges and cleans up, unattended. It does not invent scope, skip checks, or merge red.

## When to use
- Every acceptance criterion the issue owns is implemented, committed on the issue branch, and green.
- You are done with the issue and want it merged to `main` and closed.
- Closing out an issue via automated PR creation, CI check monitoring, squash-merging, and branch cleanup.

## When NOT to use
- Staging and committing a single reviewed rule implementation (use `/commit`).
- Actively writing unit tests or code for unfinished acceptance criteria (use `/implement`).
- Starting a new issue or drafting `SPEC.md` updates (use `/specify`).
- Running advisory reviews of code diffs (use `/code-review`).

## Preconditions
- You are on an issue branch (`issue/<n>-<title>`), **not** `main`/`master`.
- The branch's commits cover **all** of the issue's acceptance criteria in `SPEC.md` — every rule the issue owns is implemented and committed (`[Rn]`). If a criterion is unimplemented, **stop**: this issue is not ready to ship.
- The working tree is clean (nothing uncommitted). If not, **stop** — commit via `/commit` or discard first.
- Branch protection / CI on `main` is the real gate. `/ship` merges **only** when checks pass; it never bypasses them.

## Procedure
1. **Confirm readiness.** Identify the issue number `n` from the branch name. Verify the working tree is clean (`git status --porcelain` empty) and the branch is pushed (`git push -u origin HEAD`). Cross-check that every acceptance criterion the issue owns in `SPEC.md` has a corresponding committed rule — if any is missing, **stop and report**, do not open the PR.
2. **Open the PR.** From the issue branch into the default branch:
   ```bash
   gh pr create --base main --head "$(git branch --show-current)" \
     --title "<type>: <issue title> (#n)" \
     --body "Closes #n

   Implements the acceptance criteria for issue #n:
   - [Rn] <one line per rule/commit>
   ..."
   ```
   The body **must** contain `Closes #n` so the merge closes the issue. List the rules/commits so the PR is a readable summary of what the issue delivered.
3. **Wait for the gates.** Poll the PR's checks until they conclude:
   ```bash
   gh pr checks --watch
   ```
   If any check **fails**, **stop**: do not merge. Report which check failed and leave the PR open for a fix.
4. **Merge (only when green).** Squash-merge and delete the branch:
   ```bash
   gh pr merge --squash --delete-branch
   ```
   Use `--squash` so the issue lands as one clean commit on `main` (the per-rule history lives on the branch / in the PR). The merge closes issue #n automatically via `Closes #n`.
5. **Return to a clean base.** `git checkout main && git pull` so the next `/specify` starts from an up-to-date `main` (the `specify-gate` expects this).
6. **Report.** State the merged PR URL, the closed issue, and that `main` is now up to date.

## Guardrails
- **Never merge red.** If CI is not green, stop. `/ship` waits or aborts — it does not force-merge.
- **One issue per invocation.** `/ship` closes the issue it is on. It does not start the next story, branch, or spec.
- **No scope widening.** `/ship` does not write code or edit `SPEC.md`. If something is missing, that is an `/implement` step, not a ship step.
- **Human initiates.** `/ship` is never auto-triggered by `/commit` or `/implement`; it is an explicit, deliberate step.

## Common Rationalizations
| The excuse | The reality |
|---|---|
| "CI is failing on a flaky test, so I'll merge with admin override." | Never force-merge red CI. Fix or re-run the check before merging. |
| "I'll skip deleting the branch to keep it around." | Squash-merging preserves all history on GitHub; delete the branch to keep the workspace clean. |
| "I can run /ship while on the `main` branch." | Shipping merges an `issue/<n>-<title>` branch into `main`. Running on `main` is invalid. |
| "Some criteria are unfinished, but I will ship anyway." | All acceptance criteria for the issue must be committed and green before shipping. |

## Verification
Before completing the ship workflow, you MUST verify:
- [ ] You confirmed you are on branch `issue/<n>-<title>` with a clean working tree.
- [ ] You verified all acceptance criteria for issue #n in `SPEC.md` are implemented and committed.
- [ ] You opened the PR with `Closes #n` in the body and a summary of implemented rules.
- [ ] You watched CI checks (`gh pr checks --watch`) and confirmed all checks passed green.
- [ ] You squash-merged the PR and deleted the remote branch via `gh pr merge --squash --delete-branch`.
- [ ] You switched to `main` and pulled the latest changes (`git checkout main && git pull`).
- [ ] You reported the merged PR link, closed issue number, and updated `main` status to the user.

## Definition of done
The issue's PR is open with `Closes #n`, all gates green, squash-merged to `main`, the issue branch deleted, the issue closed, and the local `main` pulled up to date — the workflow is back to a clean base, ready for the next `/specify`.

## Example invocation
`/ship` on `issue/3-out-of-stock`, with R2 implemented, committed and green → opens PR "feat: out-of-stock handling (#3)" with `Closes #3` and the `[R2]` summary, watches CI to green, squash-merges, deletes the branch, pulls `main`. Issue #3 is closed.

> Note: the merge gate is the platform's branch protection / CI, not this skill. Confirm the exact Antigravity skill schema and your repo's branch-protection rules against the current docs.

