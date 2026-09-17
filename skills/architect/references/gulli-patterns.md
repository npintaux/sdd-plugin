# Antonio Gulli's 21 Agentic Design Patterns Taxonomy

Reference catalog synthesizing the 21 agentic patterns across 4 maturity tiers.

## Tier 1: Core Patterns (Foundational Autonomy)
1. **Prompt Chaining (Ch 1)**: Linear decomposition of complex tasks into sequential prompt-response stages where each step's output conditions the next input.
2. **Routing (Ch 2)**: Dynamic request classification and dispatching to specialized persona subagents or deterministic handlers based on detected intent.
3. **Parallelization (Ch 3)**: Concurrent fan-out processing across independent subtasks:
   - *Sectioning*: Splitting a task into orthogonal components executed concurrently.
   - *Voting*: Running multiple prompts/models on the same task to achieve consensus or reduce variance.
4. **Reflection (Ch 4)**: Iterative self-critique loop where an evaluator persona audits the generator's output against explicit rubrics, producing feedback-driven revisions.
5. **Tool Use (Ch 5)**: Augmenting LLMs with external tools (APIs, computational engines, shell commands, databases) using typed schemas (e.g. MCP).
6. **Planning (Ch 6)**: Multi-step goal decomposition, dependency graphing, execution tracking, and dynamic replanning when encountering failures.
7. **Multi-Agent Collaboration (Ch 7)**: Distributed problem-solving among autonomous agent personas collaborating via hierarchical dispatch or peer messaging.

## Tier 2: Advanced Patterns (Cognitive Extension)
8. **Memory Management (Ch 8)**: Maintaining context across turns:
   - *Working Memory*: Scratchpad within the active context window.
   - *Episodic Memory*: Temporal history of prior interactions and user decisions.
   - *Semantic Memory*: Long-term vector-indexed factual knowledge.
9. **Goal Setting & Monitoring (Ch 9)**: Tracking high-level objective completion metrics, state checkpoints, and progress thresholds.
10. **Model Context Protocol (MCP) (Ch 10)**: Standardizing client-server tool, resource, and prompt integrations over JSON-RPC.
11. **Orchestration & Flow Control (Ch 11)**: Deterministic DAG execution, state machines, and lifecycle management governing multi-agent interactions.

## Tier 3: Production Patterns (Reliability & Scale)
12. **Exception Handling & Recovery (Ch 12)**: Fault tolerance mechanisms including circuit breakers, graceful degradation, fallback models, and bounded retries.
13. **Human-in-the-Loop (HITL) (Ch 13)**: Explicit human gating checkpoints before irreversible state mutations, financial transfers, or permission escalations.
14. **Knowledge Retrieval (RAG) (Ch 14)**: Grounding generation in authoritative external vector databases, hybrid search indices, and structured corpora.
15. **Resource Optimization (Ch 15)**: Context window budgeting, prompt compression, model tiering (flash vs pro), and caching.
16. **Evaluation & Monitoring (Ch 16)**: Continuous LLM-as-a-judge scoring, trajectory evaluation, and OpenTelemetry instrumentation.

## Tier 4: Enterprise Patterns (Governance & Trust)
17. **Security & Access Control (Ch 17)**: Token-based authorization, identity propagation, sandbox isolation, and principle of least privilege.
18. **Guardrails & Safety (Ch 18)**: Pre-generation input sanitization against prompt injection and post-generation filtering for safety and PII.
19. **Explainability & Auditability (Ch 19)**: End-to-end traceability linking outputs to source inputs, rules, and model decisions (e.g. `rule_ids`).
20. **Continuous Learning (Ch 20)**: Feedback capture, prompt fine-tuning, and heuristic updating based on operational telemetry.
21. **Federated & Cross-Organization Agents (Ch 21)**: Inter-organization agent communication protocols with cryptographic verification and trust boundaries.
