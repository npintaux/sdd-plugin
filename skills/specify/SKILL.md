---
name: specify
description: Pull a user story from GitHub via the GitHub MCP server, extract its acceptance criteria, and translate them into proposed SPEC.md updates and test cases. The agent reads GitHub (intake) but obeys SPEC.md (source of truth). Use when starting work from an issue ("/specify #124", "pull the story", "what does this ticket need").
---

# /specify

Bring intent **in** from GitHub and turn it into the artifacts engineering actually works from. GitHub is intake; `SPEC.md` is the contract the agent obeys. No git branch, commit, or issue state changes until the user approves the spec.

## When to use
- Starting a cycle or a task from a GitHub Issue.

## Tool
- **GitHub MCP server** (`github`) — used to fetch the issue and, after approval, update its state/labels. The agent decides which ticket is relevant, so a connector (not a hard-coded call) is appropriate.

## Spec structure
`SPEC.md` follows the canonical format in `templates/SPEC.template.md`, **resolved relative to this skill's own directory** (the folder containing this `SKILL.md`) — not relative to the repository root or your current working directory. The template defines: an overview, a domain model, global constraints, a list of **rules** with stable sequential IDs (`R1`, `R2`, …), a precedence order, and a glossary. Rule IDs are never reused or renumbered. Read the template before editing so your changes conform to it.

## Procedure
1. **Fetch** the story by number (e.g. `#124`) via the `github` MCP server.
2. **Evaluate quality**: The story must have (a) an explicit acceptance-criteria section, and (b) at least one outcome stated in testable terms (a concrete input → expected result). If either is missing, or the story is otherwise unimplementable, **stop**: comment on the issue requesting clarification and tell the user. Do **not** scaffold, edit, branch, or label. Resume from step 1 once the story is updated.
3. **Extract** the acceptance criteria and any constraints; restate them as a checklist in your own words.
4. **Draft the `SPEC.md` change** (no commit yet):
   - **If `SPEC.md` does not exist** (first story), scaffold it from [templates/SPEC.template.md](templates/SPEC.template.md), then add the first rule(s).
   - **If it exists**, edit in place.
   - Assign each new rule the **next sequential `rule_id`** (`R1`, `R2`, …); never reuse or renumber existing IDs. Do **not** treat the GitHub prose as canonical — the spec is.
   - **Keep the spec self-sufficient.** `/implement` reads only `SPEC.md`, never the issue. So if a rule introduces a new `Request` field, a new `outcome` value, a new global invariant, or a new term, update the **Domain model**, **Global constraints**, **Precedence order**, and **Glossary** in the *same* edit. A reader must be able to implement the rule from `SPEC.md` alone; the `Source: issue #` link is for traceability (the *why*), not a required input.
5. **Map to tests**: List the test cases the criteria imply, including edge/precedence cases and the expected `outcome` and `rule_ids`. These are presented at review and carried forward to `/implement`; this skill does not persist them.
6. **Request review (STOP)**: Present the proposed `SPEC.md` diff **and** the implied test list to the user. **Stop execution and wait for explicit approval.** If the user requests changes, return to step 4. Do not branch, commit, or touch issue state until approved.
7. **Commit on a branch** (only after approval): Create and check out `issue/<number>-<short-kebab-case-title>` (e.g. `git checkout -b issue/124-contractor-review`), then commit the `SPEC.md` change to it so intent is version-controlled before implementation.
8. **Mark the issue in progress**: Via the `github` MCP server, add an `in-progress` label or transition the issue state to indicate work has begun.
9. **Finish**: Tell the user what actually happened — branch name, that the spec is committed, and that they can invoke `/implement` when ready.

## Guardrails
- The story is **intake only**. If the story and `SPEC.md` disagree, surface the conflict by commenting on the issue and stopping; `SPEC.md` (and its owners) decide.
- Never silently widen scope beyond the criteria.
- No git or issue-state mutation before the user approves the spec (step 6).

## Verification
Before exiting this skill, you MUST verify:
- [ ] You fetched the issue using the `github` MCP server.
- [ ] The story passed the quality check (explicit criteria + at least one testable outcome), or you stopped and requested clarification.
- [ ] `SPEC.md` conforms to [templates/SPEC.template.md](templates/SPEC.template.md) (scaffolded it if absent), with new rules assigned the next sequential `rule_id` and no existing IDs renumbered.
- [ ] The spec is **self-sufficient**: any new `Request` field, `outcome` value, global constraint, or term introduced by a rule is also reflected in the Domain model / Global constraints / Precedence order / Glossary, so `/implement` needs nothing but `SPEC.md`.
- [ ] You did not treat the issue prose as canonical.
- [ ] You presented the spec diff and implied test list and **waited for explicit approval** before any git or issue-state change.
- [ ] After approval, you created/checked out the `issue/<number>-<title>` branch and committed `SPEC.md`.
- [ ] You listed the implied test cases, including outcomes and expected `rule_ids`.
- [ ] You used the `github` MCP server to add an `in-progress` label or transition the issue state.
- [ ] You did not widen the scope beyond the explicit acceptance criteria.

## Example
`/specify #124` → fetches the story, checks it's actionable, proposes a `SPEC.md` edit adding R4 ("contractor → REVIEW") plus the implied tests, and **waits**. Once approved: checks out `issue/124-contractor-review`, commits the spec, labels the issue `in-progress`, and tells the user: "Spec committed on `issue/124-contractor-review`. Ready for `/implement`!"

> Note: connector name/endpoint and skill schema are platform-specific — confirm against the current Antigravity and GitHub MCP docs.
