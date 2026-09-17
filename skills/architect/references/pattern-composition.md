# Pattern Composition & Anti-Pattern Rules

## 4-Layer Architecture Stack
Every production agentic architecture organizes patterns into 4 orthogonal layers:

```
┌────────────────────────────────────────────────────────┐
│ 1. Operational & Governance Layer                      │
│    Memory (Ch 8), Monitoring (Ch 16), Audit (Ch 19)    │
├────────────────────────────────────────────────────────┤
│ 2. Safety & Control Layer                              │
│    Guardrails (Ch 18), HITL (Ch 13), Fallbacks (Ch 12) │
├────────────────────────────────────────────────────────┤
│ 3. Cognitive Routing & Planning Layer                  │
│    Routing (Ch 2), Planning (Ch 6), Reflection (Ch 4)  │
├────────────────────────────────────────────────────────┤
│ 4. Execution & Domain Engine Layer                     │
│    Tool Use (Ch 5), RAG (Ch 14), Domain Pattern Engine │
└────────────────────────────────────────────────────────┘
```

## Anti-Pattern Defense Catalog

1. **Unbounded Reflection Loop**:
   - *Smell*: Evaluator and generator looping indefinitely without guaranteed convergence.
   - *Mitigation*: Hard cap loop iterations ($\le 3$). If still failing, trigger HITL escalation (Ch 13).

2. **Multi-Agent Overkill**:
   - *Smell*: Spawning separate LLM subagents for deterministic calculations or simple lookups.
   - *Mitigation*: Use single-agent Tool Use (Ch 5) or deterministic Python code. Reserve Multi-Agent (Ch 7) for orthogonal persona conflicts or isolated context domains.

3. **Unchecked Mutations in Planning Loops**:
   - *Smell*: Autonomous planner executing write operations or deleting state without checkpoints.
   - *Mitigation*: Require Human-in-the-Loop (Ch 13) approval before any non-idempotent or destructive tool execution.

4. **Context Flooding (RAG Naivety)**:
   - *Smell*: Dumping large document corpora directly into prompts, exceeding budgets and causing needle-in-haystack attention loss.
   - *Mitigation*: Reranking, semantic chunking, and strict context budgeting (Ch 15).
