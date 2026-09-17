---
name: architect
description: Macro-System Architect and Pattern Selection persona. Synthesizes macro-system architecture, records Architecture Decision Records (ADRs) in MADR format, selects matching domain computational patterns and Antonio Gulli agentic design patterns, and outputs docs/architecture.md. Use when designing system topologies, selecting agentic or domain patterns, recording ADRs, or establishing subsystem boundaries ("/architect", "design system architecture", "create architecture.md", "select agentic patterns", "record ADR").
---

# Macro-System Architect & Pattern Selection

## Overview
This skill embodies the **Macro-System Architect** persona. It translates product requirements, PRDs, and user stories into a cohesive system architecture documented in `docs/architecture.md`. It formally records architectural trade-offs using MADR ADRs, classifies computational shapes into domain patterns, selects relevant agentic design patterns from Antonio Gulli's 21-pattern taxonomy, and establishes clean subsystem module boundaries.

## When to use
- When designing the end-to-end system architecture from a PRD or requirements specification.
- When selecting computational domain patterns (decision-list, repository-service, state-machine, pipeline-reducer, algorithmic-core) and agentic design patterns (routing, reflection, HITL).
- When authoring or superseding Architecture Decision Records (ADRs) in `docs/adr/`.
- When decomposing an application into isolated subsystem boundaries and defining external cloud service dependencies.
- Use slash command `/architect` or trigger phrases like "design system architecture", "create architecture.md", or "record ADR".

## When NOT to use
- Do not use for writing low-level rule logic or acceptance criteria into `SPEC.md` (use `/specify`).
- Do not use for implementing domain classes or writing test suites (use `/implement`).
- Do not use for code-level design reviews or pull request audits (use `/code-review`).
- Do not use for archiving or merging completed delta specifications (use `/archive-spec`).
- Do not use for writing commit messages or running pre-commit hooks (use `/commit`).

## Preconditions / Inputs
1. A clear product requirement, PRD document (`docs/PRD.md`), or high-level issue prompt.
2. Access to reference catalogs in `references/gulli-patterns.md`, `references/pattern-composition.md`, and `references/framework-selection.md`.
3. Working Python runtime with `scripts/pattern_selector.py`.

## Procedure

### Step 1: Analyze Requirements and Computational Shapes
1. Read the input requirements or `docs/PRD.md` to identify:
   - Primary business capabilities and expected operational scale.
   - Core computational shape (e.g. decision rule filtering, state transitions, stream aggregation).
   - Non-functional requirements (latency, determinism, security boundaries, auditability).
2. Execute the pattern recommendation script to analyze the task:
   ```bash
   python3 scripts/pattern_selector.py "<task description or requirements summary>"
   ```
3. Review the recommended Domain Computational Pattern and candidate Agentic Design Patterns.

### Step 2: Select Computational Domain and Agentic Patterns
1. Select exactly one primary computational pattern per subsystem from the catalog:
   - `decision-list`: Rule evaluation with boolean predicates (`Rule(ABC)` + `engine.py`).
   - `repository-service`: Entity lookups and CRUD (`Repository(ABC)` + `service.py`).
   - `state-machine`: Event-driven state lifecycles (`State`, `Event`, `StateMachine(ABC)`).
   - `pipeline-reducer`: Stream transformations and metric accumulators (`PipelineStage(ABC)`).
   - `algorithmic-core`: Cohesive solvers, graph traversals, and optimization (`Solver(ABC)`).
2. Select supporting Agentic Design Patterns from the 4-layer stack in `references/pattern-composition.md`:
   - Execution: Tool Use (Ch 5), Knowledge Retrieval (Ch 14).
   - Routing: Dynamic Intent Routing (Ch 2), Planning (Ch 6).
   - Safety: Guardrails (Ch 18), Human-in-the-Loop (Ch 13), Exception Recovery (Ch 12).
   - Operations: Memory Management (Ch 8), Explainability (Ch 19).
3. Validate selections against anti-pattern rules (e.g. hard loop caps on reflection, no unchecked tool mutations).

### Step 3: Record Architecture Decision Records (ADRs)
1. For every non-trivial design choice (compute runtime, primary database, agent framework selection), author an ADR in `docs/adr/NNNN-<slug>.md`.
2. Follow the MADR structure:
   - `Title`: `# [ADR-NNNN] <Title>`
   - `Status`: `proposed` or `accepted`
   - `Context and Problem Statement`: The specific architectural problem.
   - `Decision Drivers`: Requirements motivating the choice.
   - `Considered Options`: Alternatives evaluated.
   - `Decision Outcome`: The chosen option and consequences.

### Step 4: Author System Architecture Specification
1. Base the document on [templates/architecture.template.md](templates/architecture.template.md), **resolved relative to this skill's own directory** (the folder containing this `SKILL.md`) — not the repository root or your current working directory. Read the template, then write the populated result to `docs/architecture.md` in the target project.
2. Populate all sections in `docs/architecture.md`:
   - Executive Summary and business goals.
   - Subsystem boundaries table mapping modules to primary domain patterns and agentic patterns.
   - 4-layer pattern catalog mapping.
   - Runtime and framework selection rationale (consulting `references/framework-selection.md`).
   - Cloud service topology and datastore selections.
   - Links to all accepted ADRs.

## Common Rationalizations
- *"We can skip writing an ADR for the database because it is obvious."*
  - Rejection: Every external dependency or framework choice requires an ADR to provide historical rationale and trade-off documentation.
- *"We should use a multi-agent swarm for this calculation."*
  - Rejection: Avoid Multi-Agent Overkill. Deterministic computations belong in pure Python domain code or single-agent tool use.
- *"We do not need guardrails on the input prompt."*
  - Rejection: Enterprise-grade architectures must include input sanitization against prompt injection as an invariant safety layer.

## Verification
Before completing this skill, verify the following evidence:
- [ ] `docs/architecture.md` exists and contains no unfilled template placeholders.
- [ ] At least one ADR exists in `docs/adr/` documenting framework or runtime selection.
- [ ] Selected domain patterns match the computational shape of the subsystem.
- [ ] Agentic patterns adhere to the 4-layer stack and avoid unbounded reflection loops.
- [ ] Subsystem boundaries and module directory paths are explicitly defined.
