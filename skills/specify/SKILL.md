---
name: specify
description: Pull a user story from GitHub via the GitHub MCP server, extract its acceptance criteria, and translate them into proposed SPEC.md updates and test cases. The agent reads GitHub (intake) but obeys SPEC.md (source of truth). Use when starting work from an issue ("/specify #124", "pull the story", "what does this ticket need").
---

# /specify

Bring intent **in** from GitHub and turn it into the artifacts engineering actually works from. GitHub is intake; `SPEC.md` is the contract the agent obeys.

## When to use
- Starting a cycle or a task from a GitHub Issue.

## Tool
- **GitHub MCP server** — used to fetch the issue. The agent decides which ticket is relevant, so a connector (not a hard-coded call) is appropriate.

## Procedure
1. **Fetch** the story by number (e.g. `#124`) via the GitHub MCP server.
2. **Evaluate Quality**: Assess if the story has clear acceptance criteria and is actionable. If the story is vague, lacks criteria, or is otherwise unimplementable, **stop execution** and prompt the user (or comment on the issue) for clarification. Do not proceed to branching.
3. **Create a branch**: Create and checkout a new git branch for this issue enforcing the taxonomy `issue/<number>-<short-kebab-case-title>` (e.g., `git checkout -b issue/124-contractor-review`).
4. **Extract** the acceptance criteria and any constraints; restate them as a checklist in your own words.
5. **Update `SPEC.md`**: Make the precise edit(s) to the spec that capture this behavior. Do **not** treat the GitHub prose as canonical — the spec is.
6. **Request Review (Stop)**: Present the proposed changes to `SPEC.md` to the user. **Stop execution and wait for approval**. Do not commit or proceed to implementation until the user explicitly approves the spec changes.
7. **Commit `SPEC.md`**: Once approved, commit the specification update to the branch so the intent is version-controlled before implementation begins.
8. **Map to tests**: List the test cases the criteria imply, including edge/precedence cases and the expected `rule_ids`.
9. **Finish**: Notify the user that the setup is complete, the branch is active, the spec is committed, and they can invoke `/implement` whenever they are ready to begin coding.

## Guardrails
- The story is **intake only**. If the story and `SPEC.md` disagree, surface the conflict; `SPEC.md` (and its owners) decide.
- Never silently widen scope beyond the criteria.

## Verification
Before exiting this skill, you MUST verify:
- [ ] You fetched the issue using the `github` MCP server.
- [ ] You created and checked out a new feature branch adhering to the `issue/<number>-<title>` taxonomy.
- [ ] You explicitly updated and committed `SPEC.md` without treating the issue prose as canonical.
- [ ] You listed the implied test cases, including outcomes and expected `rule_ids`.
- [ ] You did not widen the scope beyond the explicit acceptance criteria.
- [ ] You used the `github` MCP server to add an 'in-progress' label or transition the issue state to indicate work has begun.

## Example
`/specify #124` → Checks out `issue/124-contractor-review`, proposes `SPEC.md` edit adding R4, waits for approval. Once approved, commits it and tells the user: "Spec committed on `issue/124-contractor-review`. Ready for `/implement`!"

> Note: connector name/endpoint and skill schema are platform-specific — confirm against the current Antigravity and GitHub MCP docs.
