# Antigravity Skills — Spec-Driven Development harness

A small catalog of **CLI-invocable skills** that standardize *how* code is written, validated, tested, and shipped on an agent-first workflow with [Antigravity](https://antigravity.google). They are the **platform harness** behind a Spec-Driven Development (SDD) lab built around a sample application, the **Barista Agent**.

The guiding principle:

> **A skill asks; a hook imposes.**
> Skills carry the **method** (judgment, invoked from the CLI). Hooks carry the **enforcement** (deterministic, zero-token, blocking on a non-zero exit). A convention that is only stated in a skill is a suggestion — the non-negotiable part is what a hook can check.

---

## Skills catalog

Skills are grouped **by persona** to keep the responsibility line visible. The first four are engineering skills that live in the repo and are inherited from the platform; the last is a **Product Owner** skill that belongs to the PO's own context, **not** the engineering repo.

| Skill | What it does | Persona / location | Gate or tool |
|---|---|---|---|
| `/implement` | TDD (tests from the acceptance criteria) → OO code → docstrings, to green | Engineering · repo `.agents/` | gate: `pylint` · `pytest` · coverage ≥ 90% |
| `/code-review` | Checklist: OO design, one class/file, docstrings, no dead code | Engineering | advisory — no hard gate |
| `/commit` | Conventional message linked to the GitHub Issue + the rule (`[Rn]`) | Engineering | gate: pre-commit hook (`pylint` · `pytest` · `Trivy`) |
| `/specify` | Pull the GitHub Issue, extract acceptance criteria → `SPEC.md` + tests | Engineering | tool: GitHub MCP |
| `/prd-to-backlog` | From the PRD, draft stories + acceptance criteria as GitHub Issues drafts | **Product Owner** · own context (off-repo) | tool: GitHub MCP · PO publishes |

Each skill is a single `SKILL.md`-style markdown file with `name` / `description` frontmatter (the description drives triggering) and a body describing when to use it, the procedure, conventions, gates and examples.

---

## The two layers behind the catalog

**Method (skills).** `/implement` is the single entry point for writing code: read the acceptance criteria from `SPEC.md`, write the tests first, implement object-oriented Python (dataclasses + `typing.Protocol` + composition, one class per file), add docstrings, run to green.

**Enforcement (hooks).** The gates run outside the model loop and block on failure:

| Gate | Enforces | Note |
|---|---|---|
| `pylint` | quality, design smells, **docstrings** (`missing-docstring`) | "100%" = zero violations on the agreed ruleset |
| `pytest` | all unit tests pass (green) | derived from the acceptance criteria |
| coverage | floor ≥ 90% | the pure rules engine naturally approaches 100% |
| `Trivy` | security scan: dependencies, secrets, IaC | complementary to `pylint` — it is **not** a code linter |

> **Docstrings vs TDD — the asymmetry.** Docstrings are *fully* mechanically enforceable. TDD is a *process*, and a hook checks artifacts, not the order you typed them — so the enforceable proxy is: the tests exist, derive from the acceptance criteria, pass, and meet the coverage floor. Make the **outcome** non-negotiable; prescribe TDD as the method to reach it.

---

## Traceability — the `/commit` convention

`/commit` links every change to two anchors: the **GitHub Issue number** (e.g. `#124`) and the **rule** it implements (e.g. `[R4]`):

```
type(scope): summary [Rn] (#xxx)
```

```
feat(rules): allergen safety always triggers SUBSTITUTE or REFUSE [R4] (#124)
feat(schema): Decision carries price + policy_version + evaluated_at (#126)
```

This yields end-to-end traceability **story ↔ commit ↔ rule ↔ runtime**. Each `Decision` returned by the engine carries a `rule_ids` field, so an auditor can start from a production `REFUSE`, read `rule_ids=["R4"]`, find the `[R4]` commit, then the story and the PRD that motivated it.

| `take_order(request)` | action | `rule_ids` |
|---|---|---|
| `medium oat latte` | MAKE | `["R1"]` |
| `latte` (no size) | ASK | `["R2"]` |
| `hazelnut latte` (nut allergy) | REFUSE | `["R4"]` |
| `unicorn frappe` | REFUSE | `["R3"]` |

---

## Repository layout

The engineering skills are meant to live under the repo's agent config; the PO skill is kept separate on purpose. A recommended layout (adjust to your registry's conventions):

```
.
├── README.md
├── implement.md          # /implement
├── code-review.md        # /code-review
├── commit.md             # /commit
├── specify.md            # /specify
└── prd-to-backlog.md     # /prd-to-backlog   (Product Owner — off-repo in practice)
```

When wired into a project, the engineering skills sit under `.agents/skills/`, with `AGENTS.md` acting as a thin **router** that points to them and to the always-on convention files (`.agents/conventions/style.md`, `architecture.md`). *(Those convention/router files are not in this repo yet.)*

This plugin ships its hook wiring in [`hooks.json`](hooks.json) at the plugin root (plugin form — event map wrapped in `{"hooks": {…}}`). A consuming project may instead place an equivalent file at `.agents/hooks.json`. The `pre-specify` gate is wired to `UserPromptExpansion` (so it fires when `/specify` is typed) and `post-specify` to `PostToolUse`. **The exact event names, the tool-call matcher, and the plugin script-path base are platform-specific — confirm them against `antigravity.google/docs/hooks` before relying on this wiring.**

---

## Conventions enforced

- Python 3.13, **one class per file**, complete docstrings, explicit type hints.
- Object-oriented but Pythonic: dataclasses for data, `Protocol` for interfaces, **composition over inheritance** — no deep inheritance trees.
- Pure functions: no I/O, no network, deterministic (the only time-dependent value is the recorded `evaluated_at`).
- `SPEC.md` is the source of truth for behavior; a GitHub Issue is **intake** only. The agent reads GitHub but obeys `SPEC.md`.

---

## Using the skills

Invoke a skill by name from the Antigravity CLI, e.g.:

```
/specify #124
/implement #124
/commit
```

> ⚠️ **Version note.** Antigravity launched at Google I/O 2026. The exact `SKILL.md` frontmatter schema, the `.agents/` layout, the hook event names, and the GitHub MCP setup are platform-specific and may be newer than general references. **Confirm them against the current docs at `antigravity.google/docs` before relying on them.**

---

## Related materials

These skills are the harness for an SDD lab. The companion deliverables (separate from this repo) are:

- **"Getting the most from code assistants"** — the reference deck.
- **SDD Workshop Deck** and **SDD Workshop Guide** — the hands-on lab.
- **Barista Agent PRD** — the product definition of the sample app.
- **Lab Environment Setup Guide** — how to prepare an individual Google Cloud / GitHub / Artifact Registry environment.
