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

When wired into a project, the engineering skills sit under `.agents/skills/`, with `AGENTS.md` acting as a thin **router** that points to them and to the always-on convention files. The companion `sdd-barista-agent` repo ships this: an `AGENTS.md` router at its root and a layout convention under `.agents/conventions/`. The layout convention is what makes the *structure* deterministic; the skill carries the method, the convention carries the layout, and a hook imposes the load-bearing parts.

### The harness contract (how the plugin stays project-independent)

The skills reference project files **by stable path, never by content** — that is an *interface*, not coupling (the same way every skill references `SPEC.md`). A consuming project agrees to provide a small, fixed set of files; the plugin depends only on those slots:

| File (project-provided) | Read by | Purpose |
|---|---|---|
| `SPEC.md` (repo root) | `/specify`, `/implement`, hooks | the behavior contract |
| `.agents/conventions/code-layout.md` | `/implement` (the agent) | where code goes — prose layout |
| `.agents/conventions/code-layout.env` | `post-implement` hook | the same invariants as `key=value`, so enforcement carries **no** project-specific path |

The plugin ships templates to scaffold conforming copies — `skills/specify/templates/SPEC.template.md`, `skills/implement/templates/code-layout.template.md`, `skills/implement/templates/code-layout.env.template` — exactly as `/specify` scaffolds `SPEC.md`. `code-layout.env` is the single source of truth for the machine-checkable layout: the prose (`code-layout.md`) is for the agent, `code-layout.env` is for the hook, and they declare the same paths/patterns. This is dependency inversion — the plugin depends on the *interface*, each project *implements* it.

This plugin ships its hook wiring in [`hooks.json`](hooks.json), registered via `"hooks": "./hooks.json"` in [`plugin.json`](plugin.json) (**required** — without that key Antigravity never loads the hooks).

Antigravity's hook model is **tool-centric**, not prompt-centric: a hook binds to `PreToolUse`/`PostToolUse` with a `matcher` that is an **internal tool name** (e.g. `run_command`) — there is no "fires when `/specify` is typed" event. A hook receives the tool call as JSON on **stdin** (`{"toolCall":{"name":...,"args":{"CommandLine":...,"Cwd":...}}}`) and **blocks by printing a JSON decision to stdout** (`{"decision":"deny","reason":...}`), *not* by a non-zero exit code.

A single `PreToolUse`/`run_command` hook is wired to an **entry script that dispatches to focused gates** — so the structure stays readable and extensible:

```
scripts/
├── pre-tool-use.sh      # entry (hooks.json → here): reads the tool call, routes by action
├── lib/hook-io.sh       # shared: hook_allow / hook_deny (build the JSON decision via jq)
└── gates/
    ├── commit-gate.sh   # the git-commit policy
    └── specify-gate.sh  # the /specify branch-cut policy
```

| Action detected | Gate | Imposes (deny) |
|---|---|---|
| `git commit` | `gates/commit-gate.sh` | the commit is on an `issue/<n>-<title>` branch; `SPEC.md` + the layout contract (`code-layout.md`/`code-layout.env`) exist; every rule file has a matching test; the pure core does not import the I/O shell |
| `git checkout -b issue/…` / `switch -c issue/…` / `branch issue/…` (the /specify "cut") | `gates/specify-gate.sh` | you are on `main`/`master`; the tree has no uncommitted **tracked** changes (the untracked `SPEC.md` draft is allowed); `main` is in sync with its upstream (a best-effort `git fetch` first; never blocks on network/auth) |

There is **no "fires when `/specify` is typed" event** in Antigravity, so the "start from a clean, up-to-date main" rule is enforced at the moment `/specify` *cuts the issue branch* — which is the load-bearing instant anyway (it guarantees the branch is based on the latest `main`). To add a new pre-hook behavior: detect the action in `pre-tool-use.sh` and `exec` a new `gates/<name>.sh`. Gates read the project's `code-layout.env`, so they carry no project-specific path; everything **fails open** (allows) on errors, so a hook bug never blocks normal work. The command path in `hooks.json` is **absolute** (Antigravity provides no plugin-root variable); the entry script then locates its own `lib/` and `gates/` relative to itself. Hooks are written in **bash + `jq`** for demo readability.

**Event names, matcher semantics, and the stdin/stdout contract are platform-specific — confirm them against `antigravity.google/docs/hooks` and a known-good reference plugin before relying on this wiring.**

> **On "no commit before human validation."** A hook cannot *read* your approval, so it is not the gate for it. Two layers cover it instead: (1) the `/implement` skill **stops** and presents the diff + test results, and never commits or advances on its own (`/commit` is a separate, user-initiated step); (2) the **harness's own tool-approval** for `git commit`/`git push` is the deterministic backstop that survives context compaction — keep those commands requiring confirmation rather than auto-approving them. The commit gate then imposes the *checkable* invariants (right branch, contract present, layout conforms, every rule has a test).

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
