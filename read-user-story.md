---
name: read-user-story
description: Pull a user story from Jira via the Atlassian MCP connector, extract its acceptance criteria, and translate them into proposed SPEC.md updates and test cases. The agent reads Jira (intake) but obeys SPEC.md (source of truth). Use when starting work from a ticket ("/read-user-story APPR-124", "pull the story", "what does this ticket need").
---

# /read-user-story

Bring intent **in** from Jira and turn it into the artifacts engineering actually works from. Jira is intake; `SPEC.md` is the contract the agent obeys.

## When to use
- Starting a cycle or a task from a Jira story.

## Tool
- **Atlassian MCP connector** — used to fetch the story. The agent decides which ticket is relevant, so a connector (not a hard-coded call) is appropriate.

## Procedure
1. **Fetch** the story by key (e.g. `APPR-124`) via the Atlassian MCP connector.
2. **Extract** the acceptance criteria and any constraints; restate them as a checklist in your own words.
3. **Map to `SPEC.md`**: propose the precise edit(s) to the spec that capture this behavior (a new rule, a precedence change, a contract change). Do **not** treat the Jira prose as canonical — the spec is.
4. **Map to tests**: list the test cases the criteria imply, including edge/precedence cases and the expected `rule_ids`.
5. Hand off to `/implement`.

## Guardrails
- The story is **intake only**. If the story and `SPEC.md` disagree, surface the conflict; `SPEC.md` (and its owners) decide.
- Never silently widen scope beyond the criteria.

## Output
A short brief: acceptance-criteria checklist, proposed `SPEC.md` edits, and the implied test list (with expected outcomes + `rule_ids`).

## Example
`/read-user-story APPR-124` → "Contractors always REVIEW. SPEC.md: add R4, set precedence R2 > R4 > R1 > R3. Tests: (50, office, contractor) → REVIEW, ["R4"]; …"

> Note: connector name/endpoint and skill schema are platform-specific — confirm against the current Antigravity and Atlassian MCP docs.
