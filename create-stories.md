---
name: create-stories
description: (Product Owner skill — lives in the PO's own context, NOT the engineering repo.) From a PRD, draft user stories with acceptance criteria and create them as DRAFTS in Jira via the Atlassian MCP connector, tagged by cycle. The PO reviews and publishes. This skill never touches SPEC.md or code. Use when the PO wants to turn a PRD into a backlog ("/create-stories", "draft the stories from this PRD", "populate Jira").
---

# /create-stories  (Product Owner)

Turn product intent (the PRD) into a drafted backlog in Jira. This is an **intake / authoring** skill for the **Product Owner** — a different persona from the coding agent. It belongs to the PO's own Antigravity context, **not** the engineering repo's `.agents/`.

## When to use
- A PRD exists and the PO wants the corresponding user stories created in Jira.

## Tool
- **Atlassian MCP connector** — to create issues in the Jira project (e.g. `APPR`).

## Procedure
1. **Read the PRD.** Identify the distinct pieces of value.
2. **Draft user stories** at **product level** — "As a … I want … so that …" — each with **acceptance criteria** expressed as observable behavior (not implementation).
3. **Create them as drafts** in the Jira project via the connector; **tag each by cycle** (`cycle-1` / `cycle-2` / `cycle-3`) and link the PRD.
4. **Present for review.** The PO edits wording, criteria and priority.
5. **The PO publishes.** Publication is a human action.

## Guardrails (the responsibility line)
- **Drafts only.** The PO owns the content and is the one who publishes.
- This skill **never** writes `SPEC.md` or code. Intent is born in Jira (PO); its technical form is born in the repo (engineering) and owned there.
- Acceptance criteria stay at product altitude; the engineering team translates them into `SPEC.md`.

## Output
A set of draft Jira stories (with acceptance criteria, cycle tags, PRD link) ready for the PO to review and publish.

## Example
`/create-stories` on the Approval Engine PRD → drafts US1–US7 (US1–US3 `cycle-1`, US4–US5 `cycle-2`, US6–US7 `cycle-3`), each with acceptance criteria, as Jira drafts.

> Note: PO-side skill, deliberately separate from the engineering skills. Confirm the Atlassian MCP setup and the Antigravity skill schema against the current docs.
