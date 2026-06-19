# Code layout convention — <project name>

> **Why this file exists.** `/implement` carries the *method* (TDD, OO, docstrings).
> This file carries the *layout* — where code goes — so the structure is
> **deterministic** rather than improvised on each run. `/implement` MUST read this
> before creating files. Its machine-readable twin, `code-layout.env` (same directory),
> declares the same paths/patterns as key=value so the hooks can enforce them. Keep
> the two in sync: this file is for the agent, `code-layout.env` is for the hooks.

## Repository layout

```
<repo-root>/
├── SPEC.md                  # the contract /implement obeys — ROOT, load-bearing (hooks expect it here)
├── pyproject.toml           # package metadata + semantic version
├── AGENTS.md                # thin router → SPEC.md, this convention, the skills
├── .agents/conventions/
│  ├── code-layout.md             # this file (prose, for the agent)
│  └── code-layout.env            # the same invariants as key=value (for the hooks)
├── docs/                    # reference material (e.g. the PRD) — not the dev's contract
└── <CODE_ROOT>/             # source root (e.g. src/)
   └── <package>/            # the importable package (= the built artifact)
      ├── <PURE_DIR slug>/   # pure decision core — deterministic, NO I/O
      │  └── <RULES_DIR slug>/   # one rule per file, named <RULE_FILE_PATTERN>
      └── <io shell>/        # optional: the I/O shell around the core
   <TESTS_DIR>/              # mirrors the rules; one test file per rule, <TEST_FILE_PREFIX><rule>
```

## The pure-core / shell seam (recommended)

Split the package in two so the deterministic logic stays portable and testable:

- **pure core** (`<PURE_DIR>`) — no I/O, no network, no model calls; same input →
  same output. This is what `/implement` builds and tests in TDD.
- **shell** — the I/O around the core (tools, model calls, side effects). All
  impurity lives here.

**The dependency points one way: shell → core.** The core must never import the
shell (`<FORBIDDEN_IMPORT_REGEX>` is what the hook forbids). A project with no I/O may
collapse the shell entirely.

## Rules — the unit of the engine

A *rule* is one declarative decision unit with a **stable ID** (`R1`, `R2`, …; never
reused or renumbered — see `SPEC.md`). Each rule answers: *given this input, do I
apply, and if so what `outcome` and `rule_ids` do I produce?*

- **One rule class per file**, named per `<RULE_FILE_PATTERN>` (e.g. `r2_<slug>.py`),
  under `<RULES_DIR>`.
- Each rule **subclasses the `Rule` ABC** (`abc.ABC` + an `@abstractmethod`, e.g.
  `evaluate(...) -> Decision | None`; `None` = "I don't apply"). The ABC — not a bare
  `Protocol` — is deliberate: it lets the **engine enforce the contract** (a rule that
  omits the method cannot be instantiated). Small single-method rule classes are
  intentional; configure `pylint` once to allow them, never per-file disables.
- The **engine** (`<engine module>`) is a **first-class artifact**: it holds the rule
  instances in an **ordered list at the SPEC's precedence**, exposes the **entry point**
  the SPEC names, and returns the first non-`None` decision; the last rule is the
  catch-all guaranteeing totality. Implementing a rule **includes registering it** in
  that list — **no orphan rules** — and the engine is a *walking skeleton* from the
  first rule so the system is callable end-to-end at all times.
- This ordered-list-of-rules design is what makes the engine auditable
  (`rule_ids` → file → commit `[Rn]` → issue) and declarative (add a policy = add a file).

## Tests

- Live in `<TESTS_DIR>`, **mirroring** the rule files: `<TEST_FILE_PREFIX><rule>.py`.
- One test file per rule; each test traces to an acceptance criterion in `SPEC.md`,
  not to the implementation. Assert the `outcome` **and** the `rule_ids`.
- Plus an **engine-level test** that drives each rule through the engine's entry point:
  the unit test pins the rule in isolation, the engine test pins its composition and
  precedence (and catches orphan rules / wrong ordering).

## What a hook enforces (deterministic, not just advised)

The values below live in `code-layout.env`; the `post-implement` hook reads them and blocks
a code commit that violates any of:

- `SPEC.md` stays at the repo **root**.
- New rule files live under `<RULES_DIR>` matching `<RULE_FILE_PATTERN>` and have a
  matching `<TESTS_DIR>/<TEST_FILE_PREFIX><rule>.py`.
- `<PURE_DIR>` imports nothing matching `<FORBIDDEN_IMPORT_REGEX>` (core stays pure).

Everything else here is convention the agent follows; the hook checks the parts that
must never drift.
