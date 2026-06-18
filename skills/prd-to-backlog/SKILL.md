---
name: prd-to-backlog
description: (Product Owner skill — lives in the PO's own context, NOT the engineering repo.) From any PRD, draft user stories with acceptance criteria and create them as issues in GitHub via the GitHub MCP connector, checking for existing issues to prevent duplicates and handle incremental updates. The PO reviews and publishes. This skill never touches SPEC.md or code. Use when the PO wants to turn a PRD into a backlog ("/prd-to-backlog", "draft the stories from this PRD", "populate GitHub").
---

# /prd-to-backlog  (Product Owner)

Turn product intent (the PRD) into a drafted backlog in GitHub. This is an **intake / authoring** skill for the **Product Owner** — a different persona from the coding agent. It belongs to the PO's own Antigravity context, **not** the engineering repo's `.agents/`.

## When to use
- A PRD exists and the PO wants the corresponding user stories created as GitHub Issues.

## Tool
- **GitHub MCP server** — to list, create, and update issues and labels in the repository.

## Story structure & the ingestion contract

This skill drafts issues using the canonical format in `templates/STORY.template.md`, **resolved relative to this skill's own directory** (the folder containing this `SKILL.md`). The template defines: standard description structure (As a / I want / So that), concrete testable acceptance criteria, a repo-relative PRD source link, and a hidden `prd-sync` reconciliation marker (see below).

**Be strict about what you emit, liberal about what you accept.** The PRD is the PO's product narrative — do **not** impose a tooling syntax on it. Require only the lightest anchors a good PRD has anyway, and parse them **tolerantly**:

- **Story identity** — each story is a discrete heading carrying a durable key. Accept any of `US1`, `[US1]`, `US-1`, `US 1` (case-insensitive) and normalize to `us<n>`. This key is the **only** load-bearing convention; everything else is recoverable on each run.
- **Acceptance criteria** — a recognizable per-story criteria section (match "acceptance criteria" case-insensitively).
- **Priority** — *derive, don't demand.* Map the PRD's prioritisation (e.g. MoSCoW) to a label, tolerating synonyms (`could-have` ≈ "stretch" ≈ "nice to have"). If a story's priority is absent or ambiguous, ask the PO rather than guessing.
- Do **not** require Given/When/Then, exact label keywords, cycles, front-matter, or story ordering in the PRD. Transform prose into the issue template's shape on the way **in**.

**Reconciliation is keyed on the issue, not the PRD.** Each issue the skill creates carries a hidden marker stamped into its body:

`<!-- prd-sync: key=us<n> src-sha=<short hash of the story's PRD section> -->`

Match existing issues on `key`; treat a story as **Changed** only when the **`src-sha` differs** from the hash of the current PRD section — never by re-drafting the body and fuzzy-diffing it against itself (the draft wording varies run to run; the source hash does not). The PO maintains none of this.

## Procedure
1. **Read the PRD.** Identify the distinct pieces of value and their durable story keys, parsing tolerantly (`US1` / `[US1]` / `US-1`, case-insensitive) and normalizing to `us<n>`. For each story, compute `src-sha` = a short hash of that story's PRD section (the exact text the issue is derived from).
2. **Fetch existing backlog:** Use the `github` MCP server to list all existing issues in the repository. Read each issue's `prd-sync` marker (falling back to the `[USn]` title key for issues created before markers existed) to recover its `key` and stored `src-sha`.
3. **Draft and Reconcile:**
   - Draft user stories from the PRD using the structure in [templates/STORY.template.md](templates/STORY.template.md), transforming the PRD's prose acceptance criteria into the template's Given/When/Then shape.
   - Reconcile each PRD story against the existing issues from Step 2, **keyed on `key`** (not the title text, which may change):
     * **New Story:** No issue with this `key` exists → Queue for creation, stamping the `prd-sync` marker with the story's `src-sha`, plus a `status:draft` (or `needs-review`) label and the derived priority label (e.g., `must-have`).
     * **Changed Story:** An issue with this `key` exists but its stored `src-sha` ≠ the current PRD section's hash → Queue for update (re-draft the body, refresh `src-sha`, re-derive the priority label).
     * **Unchanged Story:** An issue with this `key` exists and its `src-sha` matches → Skip (no API write).
   - **Removed Stories:** Any existing issue whose `key` is *no longer* present in the PRD is left untouched on GitHub, but flagged to the PO in the output to prevent silent drift.
4. **Handle missing details:** If any key story detail, persona, or acceptance criterion is missing or ambiguous in the PRD, stop and ask the PO for clarification on those specific sections before proceeding.
5. **Create and Update Issues on GitHub:**
   - Create new stories as issues with the standard template layout, including the hidden `prd-sync` marker (`key` + `src-sha`).
   - Update changed stories by modifying the issue body and refreshing the marker's `src-sha`.
   - Apply real GitHub metadata labels for priority (e.g. `must-have`, `should-have`) and draft state (`status:draft`) via the MCP server.
   - *Operational Draft State:* Since GitHub does not have a native draft state for regular issues, "drafts" are represented by adding a `status:draft` or `needs-review` label. This label is manually removed by the PO when they publish the story.
6. **Present for review.** Show a summary of new creations, updates, skips, and any removed-story warnings to the PO.

## Guardrails (the responsibility line)
- **Drafts only.** The PO owns the content and is the one who publishes (by removing the `status:draft` label).
- This skill **never** writes `SPEC.md` or code. Intent is born in GitHub (PO); its technical form is born in the repo (engineering) and owned there.
- Acceptance criteria stay at product altitude; the engineering team translates them into `SPEC.md`.

## Verification
Before exiting this skill, you MUST verify the following:
- [ ] You fetched existing GitHub Issues first and read their `prd-sync` markers to prevent duplicate creations and detect changed requirements.
- [ ] You parsed PRD story keys tolerantly (`US1` / `[US1]` / `US-1`) and reconciled on the normalized `key`, not on title text.
- [ ] You categorized each story by comparing the PRD section's `src-sha` to the stored marker — Unchanged stories triggered no API write.
- [ ] Each created or updated issue carries the hidden `prd-sync` marker with the correct `key` and `src-sha`.
- [ ] You derived priority from the PRD (asking the PO when absent/ambiguous) and applied it — with the `status:draft` label — as real GitHub label metadata via the MCP.
- [ ] You handled removed stories by leaving them intact and flagging them to the PO.
- [ ] Each drafted or updated issue body conforms to [templates/STORY.template.md](templates/STORY.template.md), including a repo-relative PRD link (e.g. `PRD.md#us1`).
- [ ] You did not create, modify, or delete any code files or `SPEC.md` during execution.

## Example
`/prd-to-backlog` on an updated PRD → fetches the backlog and reads each issue's `prd-sync` marker. `us1` and `us2` match on `key` with an unchanged `src-sha` → skipped (no writes); `us3`'s `src-sha` differs → its body and `src-sha` are refreshed; `us4` is new → drafted with the `prd-sync` marker, a `status:draft` label, and a `could-have` label derived from the PRD; `us5` still has an issue but is gone from the PRD → left intact and flagged. The plan is presented to the PO.

> Note: PO-side skill, deliberately separate from the engineering skills. Confirm the GitHub MCP setup and the Antigravity skill schema against the current docs.
