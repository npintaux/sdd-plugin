# Framework Selection Guide & Decision Matrix

This guide provides technical decision criteria for choosing an execution harness when designing agentic and computational systems.

---

## 1. Technical Trade-Off Matrix

| Dimension | Native Clean Architecture | Google GenAI SDK / ADK | LangGraph | CrewAI / AutoGen |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Model** | Deterministic OOP (`Rule(ABC)`, `Engine`, `State`) | ReAct / Tool-calling function loop | Cyclic StateGraph DAG with conditional branching | Conversational multi-agent role-playing |
| **Latency & Overhead** | Sub-millisecond, zero token overhead | Model latency only (~200ms–1.5s) | Model latency + graph transition overhead (~50ms) | Multi-turn latency (several seconds to minutes) |
| **State Persistence** | Project DB / Repository pattern | Ephemeral turn context (or manual session store) | Built-in checkpointers (Memory, Postgres, Redis, time-travel) | Conversation memory scratchpads |
| **Observability** | Standard logs, OpenTelemetry spans | Google Cloud Trace, Vertex AI Telemetry | LangSmith, OpenTelemetry, custom event listeners | Agentops, custom callback handlers |
| **Tool Integration** | Direct method invocation | Function calling declarations, MCP client | `@tool` decorators, LangChain tools, MCP | Tool wrappers, custom agent tools |
| **Testability** | 100% unit-testable without mocks or API keys | Mock model responses / Recorded replay fixtures | Unit-test individual node functions in isolation | Non-deterministic integration tests |
| **Governance & Safety** | Absolute mathematical determinism | System instructions, SafetySettings, JSON schemas | Guardrail nodes, human approval interrupts (`interrupt_before`) | Prompt-based instructions (soft constraints) |

---

## 2. Decision Tree for Architecture Selection

```
Is the core requirement deterministic business rules, scoring, pricing, or compliance?
  ├── YES ──► Use NATIVE CLEAN ARCHITECTURE (Rule ABCs + Engine Composition)
  │           (100% predictable, 0 token cost, microsecond execution)
  │
  └── NO ──► Does it require LLM reasoning, external search, or natural language generation?
               │
               ├── Needs cyclical reflection, rollbacks, or state-machine graph checkpoints?
               │     └──► Choose LANGGRAPH (StateGraph with persistence)
               │
               ├── Cloud Run / Vertex AI / Gemini enterprise deployment?
               │     └──► Choose GOOGLE GENAI SDK / ADK (First-class Vertex AI support)
               │
               └── Exploratory persona role-playing / brainstorming?
                     └──► Choose CREWAI / AUTOGEN (Prototyping only — not for compliance)
```

---

## 3. Recommended Hybrid Composition Pattern

In enterprise systems, **never replace deterministic rules with prompt engineering**.
Instead, compose them using the **Tool Use (Ch 5)** pattern:

```
┌────────────────────────────────────────────────────────┐
│ Outer Agent Harness (Google ADK or LangGraph)          │
│ - Natural language understanding & goal decomposition   │
│ - HITL Checkpoint Gating (Ch 13)                       │
└──────────────────────────┬─────────────────────────────┘
                           │ Dispatches typed call
                           ▼
┌────────────────────────────────────────────────────────┐
│ Inner Deterministic Engine (Clean Architecture Python) │
│ - Rule(ABC) Decision List Engine / State Machine       │
│ - 100% deterministic validation, pricing, or policy    │
│ - Returns structured Decision(outcome, rule_ids)       │
└────────────────────────────────────────────────────────┘
```

This composition ensures that:
1. The agent cannot hallucinate business decisions, pricing discounts, or security allowances.
2. Every business decision is pinned to concrete rule IDs for complete auditability (Ch 19).
3. The outer agent handles reasoning, user communication, and error recovery (Ch 12).
